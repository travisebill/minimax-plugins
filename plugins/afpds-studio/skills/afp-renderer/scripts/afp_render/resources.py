"""FOCA (FOCA Reference) resource loading.

Implements the resource chain documented in FOCA Reference:

    code point --(CPI)--> GCGID --(FNI)--> FNM index --(FNM)--> pattern box
    and pattern raster bytes --(FNG)--> glyph bitmap

Structured-field framing is the one in FOCA Reference Table 13
[foca-reference-font-object-content-architecture-reference p.144]:

    X'5A' | Length(2) | Identifier(3) | Flags(1) | SequenceNumber(2) | Data

``Length`` counts the Length field itself through the end of Data; the X'5A'
control character is not counted
[foca-reference-font-object-content-architecture-reference p.144].
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# FOCA structured-field identifiers (FOCA Reference Table 14,
# [foca-reference-font-object-content-architecture-reference p.144] and
# [foca-reference-font-object-content-architecture-reference p.145]).
SF_BCP = "d3a887"   # Begin Code Page
SF_CPD = "d3a687"   # Code Page Descriptor
SF_CPC = "d3a787"   # Code Page Control
SF_CPI = "d38c87"   # Code Page Index
SF_ECP = "d3a987"   # End Code Page

SF_BFN = "d3a889"   # Begin Font (Font Character Set)
SF_FND = "d3a689"   # Font Descriptor
SF_FNC = "d3a789"   # Font Control
SF_FNM = "d3a289"   # Font Patterns Map
SF_FNO = "d3ae89"   # Font Orientation
SF_FNP = "d3ac89"   # Font Position
SF_FNI = "d38c89"   # Font Index
SF_FNN = "d3ab89"   # Font Name Map
SF_FNG = "d3ee89"   # Font Patterns
SF_EFN = "d3a989"   # End Font

SF_BCF = "d3a88a"   # Begin Coded Font
SF_CFC = "d3a78a"   # Coded Font Control
SF_CFI = "d38c8a"   # Coded Font Index
SF_ECF = "d3a98a"   # End Coded Font


class ResourceError(Exception):
    pass


def iter_sf(buf: bytes):
    """Yield (identifier_hex, data_bytes) for each structured field in *buf*."""
    off = 0
    n = len(buf)
    while off < n:
        if buf[off] != 0x5A:
            raise ResourceError(f"expected X'5A' at offset {off}, got {buf[off]:#04x}")
        length = int.from_bytes(buf[off + 1:off + 3], "big")
        if length < 8 or off + 1 + length > n:
            raise ResourceError(f"bad structured field length {length} at offset {off}")
        yield buf[off + 3:off + 6].hex(), buf[off + 9:off + 1 + length]
        off += 1 + length


def ebcdic(data: bytes) -> str:
    return data.decode("cp037")


@dataclass
class Glyph:
    """One raster glyph."""
    gcgid: str
    char_increment: int
    ascender: int
    descender: int
    a_space: int
    b_space: int
    c_space: int
    baseline_offset: int
    box_width: int          # pels
    box_height: int         # pels
    pattern: bytes          # 1 bit per pel, rows padded to byte boundary

    def bits(self) -> list[list[int]]:
        """Return the glyph as a list of rows of 0/1 values (top row first)."""
        row_bytes = (self.box_width + 7) // 8
        rows = []
        for y in range(self.box_height):
            row = []
            base = y * row_bytes
            for x in range(self.box_width):
                byte = self.pattern[base + (x >> 3)]
                row.append((byte >> (7 - (x & 7))) & 1)
            rows.append(row)
        return rows


@dataclass
class CharacterSet:
    """A FOCA Font Character Set (.CHS)."""
    name: str
    descriptor: bytes = b""
    control: bytes = b""
    # FNM repeating groups: (box_width_minus_1, box_height_minus_1, pattern_offset)
    patterns_map: list[tuple[int, int, int]] = field(default_factory=list)
    # FNI repeating groups keyed by GCGID
    index: dict[str, dict] = field(default_factory=dict)
    # concatenated FNG pattern data
    patterns: bytes = b""
    # FNC fields
    units_per_inch: int = 0
    pattern_alignment: int = 1
    max_box_width: int = 0
    max_box_height: int = 0
    font_index_count: int = 1

    def glyph(self, gcgid: str) -> Glyph | None:
        entry = self.index.get(gcgid)
        if entry is None:
            return None
        fnm = self.patterns_map[entry["fnm_index"]]
        box_w = fnm[0] + 1
        box_h = fnm[1] + 1
        offset = fnm[2] * self.pattern_alignment
        nxt = self.patterns_map[entry["fnm_index"] + 1][2] * self.pattern_alignment \
            if entry["fnm_index"] + 1 < len(self.patterns_map) else len(self.patterns)
        return Glyph(
            gcgid=gcgid,
            char_increment=entry["char_increment"],
            ascender=entry["ascender"],
            descender=entry["descender"],
            a_space=entry["a_space"],
            b_space=entry["b_space"],
            c_space=entry["c_space"],
            baseline_offset=entry["baseline_offset"],
            box_width=box_w,
            box_height=box_h,
            pattern=self.patterns[offset:nxt],
        )


@dataclass
class CodePage:
    """A FOCA Code Page (.CDP)."""
    name: str
    descriptor: bytes = b""
    control: bytes = b""
    # code point -> (gcgid, print flags)
    index: dict[int, tuple[str, int]] = field(default_factory=dict)
    default_char: str = ""
    cpgid: int = 0

    def gcgid(self, code_point: int) -> str | None:
        hit = self.index.get(code_point)
        return hit[0] if hit else None


@dataclass
class CodedFontSection:
    charset_name: str
    codepage_name: str
    section: int


@dataclass
class CodedFont:
    """A FOCA Coded Font (.FON)."""
    name: str
    sections: list[CodedFontSection] = field(default_factory=list)

    def section(self, number: int) -> CodedFontSection | None:
        for s in self.sections:
            if s.section == number:
                return s
        return None


def load_character_set(path: str) -> CharacterSet:
    with open(path, "rb") as fh:
        buf = fh.read()
    cs = CharacterSet(name="")
    fnc = b""
    fnm_rg_len = 8
    fni_rg_len = 28
    for ident, data in iter_sf(buf):
        if ident == SF_BFN:
            cs.name = ebcdic(data[:8])
        elif ident == SF_FND:
            cs.descriptor = data
        elif ident == SF_FNC:
            fnc = data
            cs.units_per_inch = int.from_bytes(data[6:8], "big")
            cs.max_box_width = int.from_bytes(data[10:12], "big") + 1
            cs.max_box_height = int.from_bytes(data[12:14], "big") + 1
            fni_rg_len = data[15]
            cs.pattern_alignment = {0: 1, 2: 4, 3: 8}.get(data[16], 1)
            if len(data) > 21:
                fnm_rg_len = data[21]
        elif ident == SF_FNM:
            for i in range(0, len(data) - fnm_rg_len + 1, fnm_rg_len):
                grp = data[i:i + fnm_rg_len]
                w = int.from_bytes(grp[0:2], "big")
                h = int.from_bytes(grp[2:4], "big")
                off = int.from_bytes(grp[4:8], "big")
                cs.patterns_map.append((w, h, off))
        elif ident == SF_FNI:
            # only the first FNI is used (0 degree rotation)
            if cs.index:
                continue
            for i in range(0, len(data) - fni_rg_len + 1, fni_rg_len):
                grp = data[i:i + fni_rg_len]
                gcgid = ebcdic(grp[0:8])
                cs.index[gcgid] = {
                    "char_increment": int.from_bytes(grp[8:10], "big"),
                    "ascender": int.from_bytes(grp[10:12], "big"),
                    "descender": int.from_bytes(grp[12:14], "big"),
                    "fnm_index": int.from_bytes(grp[16:18], "big"),
                    "a_space": int.from_bytes(grp[18:20], "big"),
                    "b_space": int.from_bytes(grp[20:22], "big"),
                    "c_space": int.from_bytes(grp[22:24], "big"),
                    "baseline_offset": int.from_bytes(grp[26:28], "big"),
                }
        elif ident == SF_FNG:
            cs.patterns += data
    return cs


def load_code_page(path: str) -> CodePage:
    with open(path, "rb") as fh:
        buf = fh.read()
    cp = CodePage(name="")
    cpc = b""
    cpi_rg_len = 10
    for ident, data in iter_sf(buf):
        if ident == SF_BCP:
            cp.name = ebcdic(data[:8])
        elif ident == SF_CPD:
            cp.descriptor = data
            if len(data) >= 42:
                cp.cpgid = int.from_bytes(data[40:42], "big")
        elif ident == SF_CPC:
            cpc = data
            cpi_rg_len = data[9]
            cp.default_char = ebcdic(data[0:8])
        elif ident == SF_CPI:
            if cpi_rg_len == 10:
                for i in range(0, len(data) - 9, 10):
                    grp = data[i:i + 10]
                    cp.index[grp[9]] = (ebcdic(grp[0:8]), grp[8])
            else:
                for i in range(0, len(data) - 10, 11):
                    grp = data[i:i + 11]
                    cp.index[grp[10]] = (ebcdic(grp[0:8]), grp[8])
    return cp


def load_coded_font(path: str) -> CodedFont:
    with open(path, "rb") as fh:
        buf = fh.read()
    font = CodedFont(name="")
    cfi_rg_len = 25
    for ident, data in iter_sf(buf):
        if ident == SF_BCF:
            font.name = ebcdic(data[:8])
        elif ident == SF_CFC:
            if data:
                cfi_rg_len = data[0]
        elif ident == SF_CFI:
            for i in range(0, len(data) - cfi_rg_len + 1, cfi_rg_len):
                grp = data[i:i + cfi_rg_len]
                font.sections.append(CodedFontSection(
                    charset_name=ebcdic(grp[0:8]),
                    codepage_name=ebcdic(grp[8:16]),
                    section=grp[24],
                ))
    return font


class ResourceLibrary:
    """Loads and caches FOCA resources from a directory."""

    def __init__(self, directory: str):
        self.directory = directory
        self._chs: dict[str, CharacterSet] = {}
        self._cdp: dict[str, CodePage] = {}
        self._fon: dict[str, CodedFont] = {}

    def character_set(self, name: str) -> CharacterSet:
        key = name.strip()
        if key not in self._chs:
            path = os.path.join(self.directory, key + ".CHS")
            if not os.path.exists(path):
                raise ResourceError(f"character set not found: {path}")
            self._chs[key] = load_character_set(path)
        return self._chs[key]

    def code_page(self, name: str) -> CodePage:
        key = name.strip()
        if key not in self._cdp:
            path = os.path.join(self.directory, key + ".CDP")
            if not os.path.exists(path):
                raise ResourceError(f"code page not found: {path}")
            self._cdp[key] = load_code_page(path)
        return self._cdp[key]

    def coded_font(self, name: str) -> CodedFont:
        key = name.strip()
        if key not in self._fon:
            path = os.path.join(self.directory, key + ".FON")
            if not os.path.exists(path):
                raise ResourceError(f"coded font not found: {path}")
            self._fon[key] = load_coded_font(path)
        return self._fon[key]
