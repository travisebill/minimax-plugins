"""PTOCA (Presentation Text Object Content Architecture) decoding.

Control sequence framing follows PTOCA Reference p.54:

    unchained:  X'2B' prefix | X'D3' class | length(1) | function type(1) | params
    chained:                            length(1) | function type(1) | params

``length`` counts from the length byte itself, so the parameter portion is
``length - 2`` bytes.  Chaining is signalled by an odd function type — "the
low-order bit is B'1'" — and the chain ends at a control sequence with an even
function type [ptoca-reference-presentation-text-object-content-architecture-reference p.54]
[p.55].

The function type table is PTOCA Reference Table 4, printed page 25
[ptoca-reference-presentation-text-object-content-architecture-reference p.43].
"""

from __future__ import annotations

from dataclasses import dataclass

# Function type table (PTOCA Reference Table 4; even = unchained, +1 = chained).
FUNCTIONS = {
    0xC0: "SIM", 0xC2: "SIA", 0xC4: "SVI", 0xC6: "AMI", 0xC8: "RMI",
    0xD0: "SBI", 0xD2: "AMB", 0xD4: "RMB", 0xD8: "BLN",
    0xF6: "STO", 0x6A: "UCT",
    0x98: "ENC", 0x9C: "SEA", 0xDA: "TRN", 0xEE: "RPS", 0xF8: "NOP",
    0xE4: "DIR", 0xE6: "DBR",
    0x74: "STC", 0x80: "SEC",
    0x9A: "SKI", 0xF0: "SCFL", 0xF2: "BSU", 0xF4: "ESU",
    0x72: "OVS", 0x76: "USC", 0x78: "TBM",
    0x6D: "GLC", 0x8B: "GIR", 0x8C: "GAR", 0x8E: "GOR",
}

# (inline, baseline) orientation: 9-bit degrees + 6-bit minutes, MSB first.
def decode_orientation(value: int) -> tuple[int, int]:
    degrees = (value >> 7) & 0x1FF
    minutes = (value >> 1) & 0x3F
    return degrees, minutes


@dataclass
class ControlSequence:
    function: int          # even base type
    params: bytes
    chained: bool

    @property
    def name(self) -> str:
        return FUNCTIONS.get(self.function, f"X'{self.function:02X}'")


def parse_control_sequences(data: bytes) -> list[ControlSequence]:
    """Parse a PTOCA presentation text data stream into control sequences."""
    out: list[ControlSequence] = []
    i = 0
    chained = False
    n = len(data)
    while i < n:
        if not chained:
            if data[i] != 0x2B:
                raise ValueError(f"expected control sequence prefix X'2B' at {i}")
            if data[i + 1] != 0xD3:
                raise ValueError(f"unsupported control sequence class at {i}")
            i += 2
        length = data[i]
        if length < 2:
            raise ValueError(f"control sequence length {length} at {i} is below 2")
        ftype = data[i + 1]
        end = i + length
        if end > n:
            raise ValueError(f"control sequence at {i} overruns data")
        out.append(ControlSequence(ftype & 0xFE, data[i + 2:end], bool(ftype & 1)))
        i = end
        chained = bool(ftype & 1)
    return out


@dataclass
class TextState:
    """Modal PTOCA text state."""
    inline: int = 0
    baseline: int = 0
    font_lid: int = 0xFF
    inline_margin: int = 0
    baseline_increment: int = 0
    i_orientation: tuple[int, int] = (0, 0)
    b_orientation: tuple[int, int] = (90, 0)
    text_color: int = 0xFFFF


def s16(data: bytes) -> int:
    return int.from_bytes(data, "big", signed=True)


def u16(data: bytes) -> int:
    return int.from_bytes(data, "big")


def s24(data: bytes) -> int:
    return int.from_bytes(data, "big", signed=True)
