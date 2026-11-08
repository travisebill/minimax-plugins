"""MO:DCA (AFP) data stream reader.

Structure framing is the one described in MO:DCA Reference p.52 and FOCA
Reference p.144 (Table 13, Structured Field Introducer):

    X'5A' | Length(2) | Identifier(3) | Flags(1) | SequenceNumber(2) | Data

``Length`` counts the Length field itself through the end of Data; it does
**not** count the X'5A' control character.  A record therefore occupies
``1 + Length`` bytes.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Iterator

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STRUCTURE_TABLE = os.path.join(REPO_ROOT, "research", "modca-structure-table.json")


def _load_structure_table() -> dict[str, str]:
    with open(STRUCTURE_TABLE, encoding="utf-8") as fh:
        data = json.load(fh)
    return {row["hex"].upper(): row["acronym"] for row in data["structures"]}


MO_STRUCTURES = _load_structure_table()


@dataclass
class Structure:
    offset: int
    length: int
    identifier: str          # hex, e.g. "d3a088"
    flags: int
    sequence_number: int
    data: bytes

    @property
    def acronym(self) -> str:
        return MO_STRUCTURES.get(self.identifier.upper(), self.identifier.upper())

    @property
    def name(self) -> str:
        return MO_STRUCTURES.get(self.identifier.upper(), "?")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<{self.acronym} {self.identifier} len={self.length}>"


def iter_structures(buf: bytes) -> Iterator[Structure]:
    """Yield every structured field in *buf*.

    Raises ValueError on a malformed stream rather than silently truncating.
    """
    off = 0
    n = len(buf)
    while off < n:
        if buf[off] != 0x5A:
            raise ValueError(f"expected X'5A' at offset {off}, got {buf[off]:#04x}")
        if off + 3 > n:
            raise ValueError(f"truncated length field at offset {off}")
        length = int.from_bytes(buf[off + 1:off + 3], "big")
        if length < 8:
            raise ValueError(f"structured field length {length} at offset {off} below minimum 8")
        end = off + 1 + length
        if end > n:
            raise ValueError(f"structured field at offset {off} overruns buffer")
        yield Structure(
            offset=off,
            length=length,
            identifier=buf[off + 3:off + 6].hex(),
            flags=buf[off + 6],
            sequence_number=int.from_bytes(buf[off + 7:off + 9], "big"),
            data=buf[off + 9:end],
        )
        off = end


def read_structures(buf: bytes) -> list[Structure]:
    return list(iter_structures(buf))


@dataclass
class Page:
    """One page: the structures between a Begin Page and its End Page."""
    index: int
    structures: list[Structure] = field(default_factory=list)

    def by_acronym(self, acronym: str) -> list[Structure]:
        return [s for s in self.structures if s.acronym == acronym]

    def first(self, acronym: str) -> Structure | None:
        for s in self.structures:
            if s.acronym == acronym:
                return s
        return None


def split_pages(structures: list[Structure]) -> list[Page]:
    """Group a document's structures into pages (BDT..EDT, BPG..EPG)."""
    pages: list[Page] = []
    current = Page(index=len(pages))
    for st in structures:
        current.structures.append(st)
        if st.acronym == "EDT":
            pages.append(current)
            current = Page(index=len(pages))
    if current.structures:
        pages.append(current)
    return pages


def load_document(path: str) -> tuple[list[Structure], list[Page]]:
    with open(path, "rb") as fh:
        buf = fh.read()
    structures = read_structures(buf)
    return structures, split_pages(structures)
