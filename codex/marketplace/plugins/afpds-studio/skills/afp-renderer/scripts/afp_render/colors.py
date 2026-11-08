"""Colour resolution for the AFP object architectures.

Two tables exist and they are *not* identical:

* GOCA standard colour table — Table 5 of the GOCA Reference, printed page 15
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.35].
  X'0000'/X'FF00' is the "Drawing default", X'FF07' the "Presentation-process
  default", X'FF08' the "Color of medium".
* PTOCA colour-value table — Table 13 of the PTOCA Reference, printed page 103
  [ptoca-reference-presentation-text-object-content-architecture-reference p.121].
  Here X'0000'/X'FF00' is the "Presentation-process default", X'FF07' the
  device default and X'FF08' explicitly requests the *erase* function, i.e.
  the receiver's background colour is used as the foreground colour
  [ptoca-reference-presentation-text-object-content-architecture-reference p.122].

Both tables are resolved for a bilevel (black on white) presentation device,
which is what the statement this renderer was written for targets.
"""

from __future__ import annotations

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# GOCA Table 5 (printed page 15).
GOCA_COLORS = {
    0x0001: (0, 0, 255),        # Blue
    0x0002: (255, 0, 0),        # Red
    0x0003: (255, 0, 255),      # Pink/magenta
    0x0004: (0, 255, 0),        # Green
    0x0005: (0, 255, 255),      # Turquoise/cyan
    0x0006: (255, 255, 0),      # Yellow
    0x0007: (255, 255, 255),    # White
    0x0008: (0, 0, 0),          # Black
    0x0009: (0, 0, 170),        # Dark blue
    0x000A: (255, 128, 0),      # Orange
    0x000B: (170, 0, 170),      # Purple
    0x000C: (0, 146, 0),        # Dark green
    0x000D: (0, 146, 170),      # Dark turquoise
    0x000E: (196, 160, 32),     # Mustard
    0x000F: (131, 131, 131),    # Gray
    0x0010: (144, 48, 0),       # Brown
}

# PTOCA Table 13 (printed page 103).
PTOCA_COLORS = dict(GOCA_COLORS)


def goca_color(index: int) -> tuple[int, int, int]:
    """Resolve a two-byte GOCA colour-table index to RGB."""
    if index in (0xFF00,):
        # Drawing default: the colour used to draw, i.e. the ink colour.
        # "The standard default in AFP environments is the presentation device
        # default color."  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.162]
        return BLACK
    if index == 0xFF07:
        # "The presentation-process default specified by X'FF07' is resolved as
        # the presentation device default.  This color value is also known in
        # GOCA as neutral white for compatibility with display devices."
        # [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.35]
        # On a bilevel device the presentation device default is the ink
        # colour, so this renders black.
        return BLACK
    if index == 0xFF08:
        # Color of medium: the colour of the medium (paper), i.e. white.
        # [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.35]
        return WHITE
    return GOCA_COLORS.get(index, BLACK)


def oca_color(value: int) -> tuple[int, int, int]:
    """Resolve a Standard OCA colour value to RGB for a bilevel device.

    Standard OCA Color Value Table, Table 43
    [mo-dca-reference-mixed-object-document-content-architecture-reference p.581]:
    X'FF08' is the Color of medium and X'0007' is White.
    Note 1 on [mo-dca-reference-mixed-object-document-content-architecture-reference p.582]
    resolves X'0000'/X'FF00' (presentation-process default) to the presentation
    device default for IM image data, i.e. black, and Note 3 resolves X'FF07'
    the same way.  Note 2 is *not* about X'FF08': it is the note attached to
    the White entry and says how white is rendered on presentation devices
    that do not support white.  Note 4 on
    [mo-dca-reference-mixed-object-document-content-architecture-reference p.582]
    covers X'FFFF': that value is not in the table but is used by some objects
    as a default indicator, which is why this function resolves it like the
    presentation-process default.
    """
    if value in (0x0000, 0xFF00, 0xFF07, 0xFFFF):
        return BLACK
    if value == 0xFF08:
        # Colour of medium: the colour of the paper.
        return WHITE
    return GOCA_COLORS.get(value, BLACK)


def ptoca_color(value: int) -> tuple[int, int, int]:
    """Resolve a two-byte PTOCA FRGCOLOR value to RGB."""
    if value == 0xFF08:
        # "the receiver's default background color should be used for the
        # foreground color.  This provides an erase function."
        return WHITE
    if value == 0xFFFF:
        # Presentation-process default (FRGCOLOR = X'FFFF').
        return BLACK
    if value == 0xFF07:
        # Device default: black on a device that supports only black.
        return BLACK
    if 0xFF00 <= value <= 0xFF06:
        # "The color attribute values X'FF00' to X'FF06' are translated to
        # X'0000' to X'0006' and treated exactly like those colors."
        value -= 0xFF00
    if value == 0x0000:
        # Presentation-process default.
        return BLACK
    return PTOCA_COLORS.get(value, BLACK)
