"""GOCA (Graphics Object Content Architecture) decoding and rendering.

Drawing orders come in four formats [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.97]:

  * fixed 1-byte: the order code alone (only GNOP1, X'00')
  * fixed 2-byte: code + one operand byte (code bit 0 = 0 and bit 4 = 1)
  * long:         code + length(1) + length operand bytes
  * extended:     X'FE' + qualifier(1) + length(2) + operand

A GOCA graphic object starts with a Begin Segment command (X'70'):
byte 0 code, byte 1 length of the following 12 parameter bytes, bytes 2-5 name,
byte 6 flag 1, byte 7 flag 2, bytes 8-9 segment data length, bytes 10-13
predecessor/successor name, then the segment data.

Rendering rules implemented here
-------------------------------
* Order codes are taken from the Summary List of Orders
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.100]
  and [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.101].
* Colours come from the standard colour table, Table 5
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.35].
* An area (GBAR .. GEAR) is filled with the pattern symbol that was current
  when the Begin Area order was executed
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.102]
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.57].
  Pattern symbol X'0F' is "no fill" and X'40' is "blank"
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.179].
* The BOUNDARY bit (bit 1, X'40') of the Begin Area order decides whether the
  boundary lines are drawn; inside an area the Move Type orders only define
  the boundary, they do not draw the lines themselves
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.102]
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.58].
  The bit numbering is MSB first: "Bits in a single byte are numbered from
  left to right beginning with bit zero, the most significant bit"
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.51],
  so bit 0 is X'80' and bit 2 is X'20'.
* Inside an area every "at given position" order (a *Move Type* order, Table 9
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.50])
  starts a new closed figure; the figures jointly define the area boundary and
  the interior is determined with the alternate (even/odd) rule unless the
  INSIDE bit (bit 2, X'20') selects nonzero winding
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.56]
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.57].
* A GCFLT/GFLT order draws a curve fitted to the straight lines whose end
  points it carries; with only two points the result is a straight line
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.126]
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.46].  An "at current position" fillet takes the current position as
  its first point, so a fillet with two operand points joins three points and
  rounds the corner between them.
* The normal line width is *device dependent* unless the Graphics Data
  Descriptor carries a Set Current Defaults instruction with an absolute
  value; the specification only *recommends* the algorithm
  "Line width (in inches) = MH.MFR x 1/120 inches" for generators
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.52].
  This renderer follows that recommendation, which is what the document's
  rounded-rectangle outlines are sized against.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw

from afp_render.colors import goca_color

# Order names, Summary List of Orders (printed pages 80 and 81).
ORDER_NAMES = {
    0x00: "GNOP1", 0x01: "GCOMT", 0x04: "GSGCH", 0x08: "GSPS", 0x0A: "GSCOL",
    0x0C: "GSMX", 0x0D: "GSBMX", 0x11: "GSFLW", 0x18: "GSLT", 0x19: "GSLW",
    0x1A: "GSLE", 0x1B: "GSLJ", 0x20: "GSCLT", 0x21: "GSCP", 0x22: "GSAP",
    0x26: "GSECOL", 0x28: "GSPT", 0x29: "GSMT", 0x33: "GSCC", 0x34: "GSCA",
    0x35: "GSCH", 0x37: "GSMC", 0x38: "GSCS", 0x39: "GSCR", 0x3A: "GSCD",
    0x3B: "GSMP", 0x3C: "GSMS", 0x3E: "GEPROL", 0x5E: "GECP",
    0x60: "GEAR", 0x68: "GBAR", 0x80: "GCBOX", 0x81: "GCLINE", 0x82: "GCMRK",
    0x83: "GCCHST", 0x85: "GCFLT", 0x87: "GCFARC", 0x91: "GCBIMG", 0x92: "GIMD",
    0x93: "GEIMG", 0xA0: "GSPRP", 0xA1: "GCRLINE", 0xA3: "GCPARC", 0xA5: "GCCBEZ",
    0xB2: "GSPCOL", 0xC0: "GBOX", 0xC1: "GLINE", 0xC2: "GMRK", 0xC3: "GCHST",
    0xC5: "GFLT", 0xC7: "GFARC", 0xD1: "GBIMG", 0xDE: "GBCP", 0xDF: "GDPT",
    0xE1: "GRLINE", 0xE3: "GPARC", 0xE5: "GCBEZ",
}

# Orders that specify the starting point of a line ("at given position").
# Table 9 of the GOCA Reference (printed page 30) lists them as Move Type
# orders; inside an area each of them starts a new closed figure.
MOVE_TYPE_ORDERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC7, 0xD1, 0xE1, 0xE3, 0xE5}

# Standard line types, printed page 30.  The sequence gives the dash and move
# lengths in units of line width; a dash length of zero is a dot.
LINE_TYPE_SEQUENCES = {
    0x01: (0, 2),
    0x02: (3, 3),
    0x03: (6, 4, 0, 4),
    0x04: (0, 3, 0, 7),
    0x05: (8, 3),
    0x06: (6, 3, 0, 3, 0, 3),
}

# Pattern symbols of the default pattern set.  The Set Pattern Symbol order
# defines their meaning
# [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.179]:
#
#   X'00'       drawing default (solid fill when the GDD names no default)
#   X'01'-X'08' dotted patterns of decreasing density
#   X'09'       vertical lines
#   X'0A'       horizontal lines
#   X'0B'-X'0E' diagonal lines
#   X'0F'       no fill
#   X'10'       solid fill
#   X'40'       blank, processed the same as X'0F'
#
# Figure 19 on printed page 40 shows representative pictures of the set.
PATTERN_SOLID = 0x10
PATTERN_NONE = 0x0F
PATTERN_BLANK = 0x40
PATTERN_DOTS = range(0x01, 0x09)
PATTERN_VERTICAL = 0x09
PATTERN_HORIZONTAL = 0x0A
PATTERN_DIAGONAL = {0x0B, 0x0C, 0x0D, 0x0E}

# Nominal size of one pattern cell in presentation-space units.  The dot size
# and spacing of the default pattern set are presentation-device dependent
# [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.60],
# so a nominal cell is used here.
PATTERN_CELL_UNITS = 8.0


@dataclass
class Order:
    code: int
    operands: bytes
    offset: int

    @property
    def name(self) -> str:
        return ORDER_NAMES.get(self.code, f"X'{self.code:02X}'")


def parse_orders(data: bytes) -> list[Order]:
    """Split a GOCA segment data stream into drawing orders."""
    orders: list[Order] = []
    i = 0
    n = len(data)
    while i < n:
        code = data[i]
        start = i
        if code == 0x00:
            orders.append(Order(code, b"", start))
            i += 1
        elif code == 0xFE:
            length = int.from_bytes(data[i + 2:i + 4], "big")
            orders.append(Order(code, data[i + 4:i + 4 + length], start))
            i += 4 + length
        elif code < 0x80 and (code & 0x0F) >= 0x08:
            # fixed 2-byte: "the first digit of the order code is less than 8,
            # and the second digit is greater than, or equal to, 8"
            orders.append(Order(code, data[i + 1:i + 2], start))
            i += 2
        else:
            length = data[i + 1]
            orders.append(Order(code, data[i + 2:i + 2 + length], start))
            i += 2 + length
    return orders


@dataclass
class BeginSegment:
    name: bytes
    flags: int
    segment_length: int
    data: bytes


def parse_begin_segment(data: bytes) -> BeginSegment:
    """Parse a GOCA Begin Segment command (X'70')."""
    if data[0] != 0x70:
        raise ValueError(f"not a Begin Segment command: {data[0]:#04x}")
    length = data[1]
    flags2 = data[7]
    seg_len = int.from_bytes(data[8:10], "big")
    return BeginSegment(
        name=data[2:6],
        flags=flags2,
        segment_length=seg_len,
        data=data[14:14 + seg_len],
    )


def s16(data: bytes) -> int:
    return int.from_bytes(data, "big", signed=True)


@dataclass
class Segment:
    """One boundary segment together with the line attributes in force for it."""

    x0: float
    y0: float
    x1: float
    y1: float
    line_type: int
    width_mult: int
    color_index: int


@dataclass
class Area:
    """An area under construction (GBAR .. GEAR).

    The pattern attributes are those that were current when the Begin Area
    order was executed
    [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.102]
    [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.57].
    """
    flags: int
    color_index: int
    pattern_symbol: int
    figures: list[list[tuple[float, float]]] = field(default_factory=list)
    current: list[tuple[float, float]] = field(default_factory=list)
    segments: list[Segment] = field(default_factory=list)


class GocaRenderer:
    """Draws a GOCA graphics object into a PIL image.

    The graphics presentation space is mapped one-to-one onto the page
    presentation space: the Object Area Descriptor of this document gives an
    object area of 2041 x 2882 units at 240 units/inch, which is exactly the
    page size [mo-dca-reference-mixed-object-document-content-architecture-reference p.345]
    [mo-dca-reference-mixed-object-document-content-architecture-reference p.436].
    """

    def __init__(self, image: Image.Image, px_per_unit: float,
                 units_per_inch: float = 240.0, offset=(0.0, 0.0)):
        self.image = image
        self.draw = ImageDraw.Draw(image)
        self.px_per_unit = px_per_unit
        self.units_per_inch = units_per_inch
        self.offset = offset

        self.color_index = 0xFF00      # drawing default
        self.pattern_symbol = PATTERN_SOLID
        self.line_type = 0x00          # drawing default
        self.line_width_mult = 1
        self.pos = (0.0, 0.0)          # current position
        self.area: Area | None = None
        self.warnings: list[str] = []

    # -- helpers ---------------------------------------------------------
    @property
    def normal_line_width_units(self) -> float:
        """Normal line width in presentation-space units (1/120 inch)."""
        return self.units_per_inch / 120.0

    def _px(self, x: float, y: float) -> tuple[float, float]:
        ox, oy = self.offset
        return (ox + x * self.px_per_unit, oy + y * self.px_per_unit)

    def _points(self, data: bytes) -> list[tuple[float, float]]:
        return [(s16(data[i:i + 2]), s16(data[i + 2:i + 4]))
                for i in range(0, len(data) - 3, 4)]

    # -- main loop -------------------------------------------------------
    def render(self, data: bytes) -> None:
        for order in parse_orders(data):
            self._dispatch(order)

    def _dispatch(self, order: Order) -> None:
        code, ops = order.code, order.operands
        if code == 0x0A:                       # GSCOL - set colour
            self.color_index = 0xFF00 | ops[0]
        elif code == 0x28:                     # GSPT - set pattern symbol
            self.pattern_symbol = ops[0]
        elif code == 0x18:                     # GSLT - set line type
            self.line_type = ops[0]
        elif code == 0x19:                     # GSLW - set line width
            self.line_width_mult = ops[0]
        elif code == 0x68:                     # GBAR - begin area
            self._begin_area(ops[0] if ops else 0)
        elif code == 0x60:                     # GEAR - end area
            self._end_area()
        elif code == 0xC1:                     # GLINE - line at given position
            pts = self._points(ops)
            if len(pts) >= 2:
                self._move_type(pts[0])
                self._polyline([pts[0], pts[1]])
                self.pos = pts[1]
        elif code == 0x81:                     # GCLINE - line at current position
            pts = self._points(ops)
            if pts:
                self._polyline([self.pos, pts[0]])
                self.pos = pts[0]
        elif code in (0x85, 0xC5):             # GCFLT / GFLT - fillet
            pts = self._points(ops)
            if code == 0xC5:                 # at given position (Move Type)
                if len(pts) >= 2:
                    self._move_type(pts[0])
                    self._polyline(self._fillet_polyline(pts))
                    self.pos = pts[-1]
                elif len(pts) == 1:
                    # "only an initial position ... serves only to move the
                    # current position"
                    self.pos = pts[0]
            else:                             # at current position
                if len(pts) >= 2:
                    self._polyline(self._fillet_polyline([self.pos] + pts))
                    self.pos = pts[-1]
                # with only an initial position the order is a No-Op
        elif code in (0xC0, 0x80):             # GBOX / GCBOX
            pts = self._points(ops)
            if len(pts) >= 2:
                self._move_type(pts[0])
                self._polyline([pts[0], pts[1], (pts[1][0], pts[0][1]),
                                (pts[0][0], pts[1][1]), pts[0]])
                self.pos = pts[0]
        elif code == 0x21:                     # GSCP - set current position
            pts = self._points(ops)
            if pts:
                self._move_type(pts[0])
                self.pos = pts[0]
        elif code == 0x00:                     # GNOP1
            pass
        else:
            self.warnings.append(f"unsupported GOCA order {order.name}")

    # -- area handling ---------------------------------------------------
    def _fillet_polyline(self, pts: list[tuple[float, float]],
                         steps: int = 16) -> list[tuple[float, float]]:
        """Approximate a fillet by a polyline.

        "The points specified in the order are joined by conceptual straight
        lines, to which a curve is fitted.  The curve is tangential to the
        first line at its start point, and to the last line at its end point.
        If there are more than two lines, the curve is tangential to the
        intermediate lines at their center points.  If only two points are
        supplied, a straight line is drawn between the points."
        [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.46]

        A circular arc is used.  It is tangent to the two lines that meet at
        the corner, and the tangent length is the shorter of the two adjacent
        segments.  When the two adjacent segments have the same length — which
        is the case for every rounded rectangle in this document — the tangent
        points fall exactly on the first and the last point of the order, so
        the arc is exactly the quarter circle the specification describes.

        Limitation: the general case (more than two lines, or adjacent
        segments of different lengths) is not implemented; the specification
        defines it through a sharpness parameter, which the AFP GOCA
        architecture does not support
        [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.46].
        """
        if len(pts) < 3:
            return list(pts)
        out: list[tuple[float, float]] = [pts[0]]
        for i in range(1, len(pts) - 1):
            p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
            d1 = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            d2 = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            if d1 == 0 or d2 == 0:
                out.append(p1)
                continue
            u1 = ((p0[0] - p1[0]) / d1, (p0[1] - p1[1]) / d1)
            u2 = ((p2[0] - p1[0]) / d2, (p2[1] - p1[1]) / d2)
            bx, by = u1[0] + u2[0], u1[1] + u2[1]
            blen = math.hypot(bx, by)
            if blen == 0:                       # 180 degree turn
                out.append(p1)
                continue
            bx, by = bx / blen, by / blen
            cos_half = blen / 2.0
            cos_half = max(-1.0, min(1.0, cos_half))
            sin_half = math.sqrt(max(0.0, 1.0 - cos_half * cos_half))
            tangent = min(d1, d2)
            radius = tangent * sin_half / cos_half if cos_half else tangent
            centre_dist = tangent / cos_half if cos_half else tangent
            cx = p1[0] + bx * centre_dist
            cy = p1[1] + by * centre_dist
            t1 = (p1[0] + u1[0] * tangent, p1[1] + u1[1] * tangent)
            t2 = (p1[0] + u2[0] * tangent, p1[1] + u2[1] * tangent)
            out.append(t1)
            a1 = math.atan2(t1[1] - cy, t1[0] - cx)
            a2 = math.atan2(t2[1] - cy, t2[0] - cx)
            delta = a2 - a1
            while delta > math.pi:
                delta -= 2 * math.pi
            while delta < -math.pi:
                delta += 2 * math.pi
            for k in range(1, steps + 1):
                a = a1 + delta * k / steps
                out.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
            out.append(t2)
        out.append(pts[-1])
        return out

    def _begin_area(self, flags: int) -> None:
        # The pattern and colour attributes that are current now are the ones
        # used to fill the area.
        self.area = Area(flags=flags, color_index=self.color_index,
                         pattern_symbol=self.pattern_symbol)

    def _move_type(self, start: tuple[float, float]) -> None:
        """A Move Type order starts a new closed figure inside an area.

        "The first constructed figure in an area is defined as starting at the
        Begin Area order.  It is delimited either by an End Area order, or by
        any Move Type order that is valid in an area definition, which implies
        the start of a new closed figure."
        [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.56]
        """
        if self.area is None:
            return
        if self.area.current:
            self.area.figures.append(self.area.current)
        self.area.current = [start]

    def _polyline(self, pts: list[tuple[float, float]]) -> None:
        """Record a polyline in the current figure.

        Inside an area the lines are *not* drawn here: they are only drawn if
        the Begin Area order asked for the boundary to be drawn, and then with
        the line attributes that were current when each order was executed
        [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.58].
        """
        if self.area is not None:
            if not self.area.current:
                self.area.current = [pts[0]]
            self.area.current.extend(pts[1:])
            for a, b in zip(pts, pts[1:]):
                self.area.segments.append(Segment(
                    a[0], a[1], b[0], b[1], self.line_type,
                    self.line_width_mult, self.color_index))
            return
        for a, b in zip(pts, pts[1:]):
            self._draw_line(a[0], a[1], b[0], b[1])

    def _end_area(self) -> None:
        if self.area is None:
            return
        area = self.area
        self.area = None
        if area.current:
            area.figures.append(area.current)
        if not area.figures:
            return

        edges: list[tuple[float, float, float, float]] = []
        for fig in area.figures:
            if len(fig) < 2:
                continue
            for i in range(len(fig)):
                x0, y0 = fig[i]
                x1, y1 = fig[(i + 1) % len(fig)]
                edges.append((x0, y0, x1, y1))

        color = goca_color(area.color_index)
        mask = self._area_mask(edges, area.flags & 0x20)
        if mask is not None:
            self._paint(mask, color, area.pattern_symbol)

        if area.flags & 0x40:                  # BOUNDARY: draw the boundary
            for seg in area.segments:
                self._draw_line(seg.x0, seg.y0, seg.x1, seg.y1,
                                line_type=seg.line_type,
                                width_mult=seg.width_mult,
                                color=goca_color(seg.color_index))

    # -- rasterising ------------------------------------------------------
    def _area_mask(self, edges, nonzero: bool):
        """Even/odd (alternate) or nonzero winding fill of the area edges."""
        if not edges:
            return None
        pu = self.px_per_unit
        ox, oy = self.offset
        pe = [(ox + x0 * pu, oy + y0 * pu, ox + x1 * pu, oy + y1 * pu)
              for (x0, y0, x1, y1) in edges]
        xs = [v for e in pe for v in (e[0], e[2])]
        ys = [v for e in pe for v in (e[1], e[3])]
        width, height = self.image.size
        x0 = max(0, int(math.floor(min(xs))))
        x1 = min(width, int(math.ceil(max(xs))) + 1)
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(height, int(math.ceil(max(ys))) + 1)
        if x1 <= x0 or y1 <= y0:
            return None

        mask = np.zeros((y1 - y0, x1 - x0), dtype=bool)
        crossings: dict[int, list[float]] = {}
        for (ax, ay, bx, by) in pe:
            if ay == by:
                continue
            for y in range(max(y0, int(math.floor(min(ay, by)))),
                           min(y1, int(math.ceil(max(ay, by))))):
                crossings.setdefault(y, []).append((ax, ay, bx, by))
        for y, segs in crossings.items():
            yc = y + 0.5
            xs_hit = []
            for (ax, ay, bx, by) in segs:
                if (ay <= yc < by) or (by <= yc < ay):
                    t = (yc - ay) / (by - ay)
                    xs_hit.append((ax + t * (bx - ax),
                                   1 if by > ay else -1))
            if nonzero:
                xs_hit.sort()
                wind = 0
                start = None
                for x, direction in xs_hit:
                    if wind == 0:
                        start = x
                    wind += direction
                    if wind == 0 and start is not None:
                        a = max(x0, int(math.ceil(start - 0.5)))
                        b = min(x1 - 1, int(math.floor(x - 0.5)))
                        if b >= a:
                            mask[y - y0, a - x0:b - x0 + 1] = True
                        start = None
            else:
                xs_hit.sort()
                for i in range(0, len(xs_hit) - 1, 2):
                    a = max(x0, int(math.ceil(xs_hit[i][0] - 0.5)))
                    b = min(x1 - 1, int(math.floor(xs_hit[i + 1][0] - 0.5)))
                    if b >= a:
                        mask[y - y0, a - x0:b - x0 + 1] = True
        return (mask, x0, y0)

    def _paint(self, mask, color, pattern_symbol=PATTERN_SOLID) -> None:
        region, x0, y0 = mask
        if not region.any():
            return
        region = self._apply_pattern(region, x0, y0, pattern_symbol)
        if region is None or not region.any():
            return
        height, width = region.shape
        patch = Image.new("RGB", (width, height), color)
        alpha = Image.fromarray((region * 255).astype("uint8"), mode="L")
        self.image.paste(patch, (x0, y0), alpha)
        self.draw = ImageDraw.Draw(self.image)

    def _apply_pattern(self, region, x0: int, y0: int, symbol: int):
        """Mask *region* with the default pattern set symbol *symbol*.

        The pattern set and symbol that were current when the Begin Area order
        was executed select the fill
        [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.57].
        """
        if symbol in (0x00, PATTERN_SOLID):
            return region
        if symbol in (PATTERN_NONE, PATTERN_BLANK):
            # "No fill" and "blank" - the area interior is left untouched.
            return None
        pu = self.px_per_unit
        ox, oy = self.offset
        xs = (np.arange(x0, x0 + region.shape[1]) - ox) / pu
        ys = (np.arange(y0, y0 + region.shape[0]) - oy) / pu
        cell = PATTERN_CELL_UNITS
        if symbol in PATTERN_DIAGONAL:
            # X'0B'/X'0C' run bottom-left to top-right, X'0D'/X'0E' the other
            # way; the second of each pair is the thin variant.
            if symbol in (0x0B, 0x0D):
                thickness = cell / 3.0
            else:
                thickness = cell / 10.0
            if symbol in (0x0B, 0x0C):
                grid = (xs[None, :] + ys[:, None]) % cell
            else:
                grid = (xs[None, :] - ys[:, None]) % cell
            pattern = grid < thickness
        elif symbol == PATTERN_VERTICAL:
            pattern = (xs[None, :] % cell) < (cell / 3.0)
        elif symbol == PATTERN_HORIZONTAL:
            pattern = (ys[:, None] % cell) < (cell / 3.0)
        elif symbol in PATTERN_DOTS:
            # "Dotted patterns of decreasing density": X'01' is nearly solid,
            # X'08' is a sparse grid of dots.
            level = symbol - 0x01
            period = cell * (level + 1)
            radius = max(0.6, cell * (0.45 - 0.05 * level))
            gx = np.mod(xs[None, :], period)
            gy = np.mod(ys[:, None], period)
            pattern = ((gx - period / 2) ** 2 + (gy - period / 2) ** 2
                       ) <= radius ** 2
        else:
            # Undefined pattern symbol: the standard action is to use the
            # standard default pattern symbol, which is solid fill.
            return region
        return region & pattern

    # -- lines -----------------------------------------------------------
    def _draw_line(self, x0: float, y0: float, x1: float, y1: float,
                   line_type: int | None = None, width_mult: int | None = None,
                   color=None) -> None:
        if line_type is None:
            line_type = self.line_type
        if width_mult is None:
            width_mult = self.line_width_mult
        if color is None:
            color = goca_color(self.color_index)
        if line_type == 0x08:            # invisible line
            return
        width_units = width_mult * self.normal_line_width_units
        width_px = max(1, int(round(width_units * self.px_per_unit)))
        sequence = LINE_TYPE_SEQUENCES.get(line_type)
        if sequence is None:                 # solid / drawing default
            self._segment(x0, y0, x1, y1, color, width_px)
            return
        dash_units = width_units * sequence
        total = math.hypot(x1 - x0, y1 - y0)
        if total <= 0 or dash_units <= 0:
            self._segment(x0, y0, x1, y1, color, width_px)
            return
        dx, dy = (x1 - x0) / total, (y1 - y0) / total
        pos = 0.0
        index = 0
        draw = True
        while pos < total:
            length = dash_units[index % len(sequence)]
            end = min(total, pos + length) if length > 0 else min(total, pos + width_units)
            if draw and end > pos:
                self._segment(x0 + dx * pos, y0 + dy * pos,
                              x0 + dx * end, y0 + dy * end, color, width_px)
            elif draw and length == 0:
                self._segment(x0 + dx * pos, y0 + dy * pos,
                              x0 + dx * pos + dx * width_units,
                              y0 + dy * pos + dy * width_units, color, width_px)
            pos = end
            index += 1
            draw = not draw

    def _segment(self, x0, y0, x1, y1, color, width_px) -> None:
        a = self._px(x0, y0)
        b = self._px(x1, y1)
        self.draw.line([a[0], a[1], b[0], b[1]], fill=color, width=width_px)
