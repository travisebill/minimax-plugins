"""Render a MO:DCA (AFP) page to a PNG.

Usage:
    python3 tools/afp_render/render.py <file.afp> --resources <dir> --page 1 --out page1.png

Coordinate spaces
-----------------
* The **presentation space** unit is defined by the Page Descriptor
  (MO:DCA Reference p.355): XpgUnits page units per unit base.  With
  XpgBase = X'00' the base is 10 inches, so 2400 units means 240 units
  per inch.
* The **text space** unit is defined by the Presentation Text Descriptor:
  XptUnits text presentation space units per unit base, with its own
  XptBase/YptBase unit bases, and XptSize/YptSize extents that must equal
  the extent of the including page or overlay presentation space
  (MO:DCA Reference p.661).  The Presentation Text object supplies the
  measurement units used by the generator when it formats the data
  (PTOCA Reference, printed page 12).
* A FOCA font measures its characters in its own *pels*; the font control
  (FOCA Reference p.170) declares XftUnits = 3000 pels per 10 inches, i.e.
  300 pels per inch.  A font therefore has to be scaled by
  ``page units per inch / font pels per inch`` to land on the page.

Object composition
------------------
A page may pull in content that lives in an external resource file:

* **IPO** (Include Page Overlay) names a page overlay; the overlay's
  coordinate-system origin is placed at the offset given by the IPO
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.267].
* **IPS** (Include Page Segment) names a page segment and gives the position
  of its reference point on the including page or overlay
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.269].
  The page segment holds IM image objects whose origin is measured from that
  reference point.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from afp_render.afpstream import load_document  # noqa: E402
from afp_render.colors import ptoca_color  # noqa: E402
from afp_render.goca import GocaRenderer, parse_begin_segment  # noqa: E402
from afp_render.imimage import collect_im_images, render_im_image  # noqa: E402
from afp_render.ptoca import parse_control_sequences  # noqa: E402
from afp_render.resfile import parse_resource_file  # noqa: E402
from afp_render.resources import ResourceLibrary  # noqa: E402
from afp_render.units import inch_base, page_base_inches  # noqa: E402

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def s16(data: bytes) -> int:
    return int.from_bytes(data, "big", signed=True)


def s24(data: bytes) -> int:
    return int.from_bytes(data, "big", signed=True)


def u16(data: bytes) -> int:
    return int.from_bytes(data, "big")


class FontResolver:
    """Maps an AFP coded font name to the FOCA resources that back it.

    The resource archive that ships with this AFP names its coded fonts
    ``X0FNTnnn`` / ``X0FDBnnn`` while the AFP asks for ``X1FNTnnn`` /
    ``X1FDBnnn``; the mapping is a pure name substitution and lives here so
    that a differently named resource set only needs this one change.
    """

    def __init__(self, library: ResourceLibrary, name_map=None):
        self.library = library
        self.name_map = name_map or (lambda n: n.replace("X1", "X0", 1))
        self._fonts: dict[str, object] = {}

    def coded_font(self, afp_name: str):
        key = self.name_map(afp_name)
        if key not in self._fonts:
            self._fonts[key] = self.library.coded_font(key)
        return self._fonts[key]

    def decode(self, afp_name: str, data: bytes):
        """Decode text data into [(code_point, gcgid, glyph)] triples."""
        font = self.coded_font(afp_name)
        out = []
        if len(font.sections) == 1 and font.sections[0].section == 0:
            section = font.sections[0]
            cp = self.library.code_page(section.codepage_name)
            cs = self.library.character_set(section.charset_name)
            for byte in data:
                gcgid = cp.gcgid(byte)
                out.append((byte, gcgid, cs.glyph(gcgid) if gcgid else None))
        else:
            i = 0
            while i + 1 < len(data):
                section = font.section(data[i])
                if section is None:
                    i += 2
                    continue
                cp = self.library.code_page(section.codepage_name)
                cs = self.library.character_set(section.charset_name)
                gcgid = cp.gcgid(data[i + 1])
                out.append(((data[i] << 8) | data[i + 1], gcgid,
                            cs.glyph(gcgid) if gcgid else None))
                i += 2
        return out


class PageGeometry:
    """MO:DCA page descriptor geometry (MO:DCA Reference p.355).

    Offset 0 XpgBase, 1 YpgBase, 2-3 XpgUnits, 4-5 YpgUnits,
    6-8 XpgSize, 9-11 YpgSize, 12-14 reserved.

    XpgBase selects the unit base: X'00' is a 10 inch base and X'01' is a
    10 centimetre base (MO:DCA Reference p.355), so page units per inch is
    XpgUnits divided by that base and not always by ten.
    """

    def __init__(self, pgd: bytes):
        self.x_base = pgd[0]
        self.y_base = pgd[1]
        self.x_units = int.from_bytes(pgd[2:4], "big")
        self.y_units = int.from_bytes(pgd[4:6], "big")
        self.x_size = int.from_bytes(pgd[6:9], "big")
        self.y_size = int.from_bytes(pgd[9:12], "big")
        if self.x_base != self.y_base:
            # "A X'01' exception condition exists if the XpgBase and YpgBase
            # values are not identical." (MO:DCA Reference p.355)
            raise ValueError(
                f"page descriptor has different X and Y unit bases "
                f"(X'{self.x_base:02X}' / X'{self.y_base:02X}')")
        # Page units per inch: XpgUnits per unit base.
        self.units_per_inch = self.x_units / page_base_inches(self.x_base)


class TextGeometry:
    """MO:DCA presentation text descriptor geometry (MO:DCA Reference p.661).

    Offset 0 XptBase, 1 YptBase, 2-3 XptUnits, 4-5 YptUnits,
    6-8 XptSize, 9-11 YptSize, 12-13 reserved.

    The summary table on printed page 629 labels XptSize/YptSize as UBIN, but
    the sizes in the stream are three bytes wide: in every container of this
    document the three-byte XptSize/YptSize reproduce the page descriptor's
    XpgSize/YpgSize exactly (page 2041 x 2882, overlay 1984 x 2806), which the
    two-byte reading does not.
    """

    def __init__(self, ptd: bytes):
        self.x_base = ptd[0]
        self.y_base = ptd[1]
        self.x_units = int.from_bytes(ptd[2:4], "big")
        self.y_units = int.from_bytes(ptd[4:6], "big")
        self.x_size = int.from_bytes(ptd[6:9], "big")
        self.y_size = int.from_bytes(ptd[9:12], "big")
        # Text presentation space units per unit base.  The Presentation Text
        # Descriptor restricts the unit base to X'00', i.e. 10 inches
        # (MO:DCA Reference p.660).
        self.units_per_inch = self.x_units / inch_base(
            self.x_base, "text presentation space unit base")


class Renderer:
    def __init__(self, resolver: FontResolver, dpi: float, units_per_inch: float):
        self.resolver = resolver
        self.dpi = dpi
        self.units_per_inch = units_per_inch
        self.px_per_unit = dpi / units_per_inch
        self.font_scale_cache: dict[str, float] = {}
        self.goca_warnings: list[str] = []

    # -- text -------------------------------------------------------------
    def font_scale(self, charset) -> float:
        """Page units per font pel for one character set."""
        key = charset.name
        if key not in self.font_scale_cache:
            pels_per_inch = charset.units_per_inch / 10.0
            self.font_scale_cache[key] = self.units_per_inch / pels_per_inch
        return self.font_scale_cache[key]

    def draw_text_object(self, data: bytes, mcf_fonts: dict[int, str],
                         draw: ImageDraw.ImageDraw, offset=(0, 0)):
        inline = 0
        baseline = 0
        font_lid = None
        color = BLACK
        for cs in parse_control_sequences(data):
            p = cs.params
            if cs.function == 0xC6:            # AMI - Absolute Move Inline
                inline = s16(p)
            elif cs.function == 0xD2:          # AMB - Absolute Move Baseline
                baseline = s16(p)
            elif cs.function == 0xF0:          # SCFL - Set Coded Font Local
                font_lid = p[0]
            elif cs.function == 0x74:          # STC - Set Text Color
                color = ptoca_color(int.from_bytes(p[0:2], "big"))
            elif cs.function == 0xDA:          # TRN - Transparent Data
                name = mcf_fonts.get(font_lid)
                if name is None:
                    continue
                for _, gcgid, glyph in self.resolver.decode(name, p):
                    if glyph is None:
                        continue
                    scale = self.font_scale(self._charset_of(name, gcgid))
                    self._draw_glyph(draw, glyph, inline, baseline, scale,
                                     offset, color)
                    inline += int(round(glyph.char_increment * scale))
            elif cs.function == 0xE6:          # DBR - Draw B-axis Rule
                self._draw_rule(draw, inline, baseline, p, offset, axis="B",
                                color=color)
            elif cs.function == 0xE4:          # DIR - Draw I-axis Rule
                self._draw_rule(draw, inline, baseline, p, offset, axis="I",
                                color=color)
        return inline, baseline

    def _charset_of(self, afp_name: str, gcgid: str):
        font = self.resolver.coded_font(afp_name)
        for section in font.sections:
            if section.section == 0:
                cs = self.resolver.library.character_set(section.charset_name)
                if gcgid in cs.index:
                    return cs
        for section in font.sections:
            cs = self.resolver.library.character_set(section.charset_name)
            if gcgid in cs.index:
                return cs
        return self.resolver.library.character_set(font.sections[0].charset_name)

    def _draw_glyph(self, draw, glyph, inline: int, baseline: int,
                    scale: float, offset, color=BLACK):
        """Stamp one raster glyph; its reference point is the presentation position.

        The glyph box starts at (inline + a-space, baseline - baseline offset)
        and is measured in the font's pels, which are scaled onto the page by
        ``scale`` (page units per pel).
        """
        ox, oy = offset
        px_per_unit = self.px_per_unit
        left = ox + (inline + glyph.a_space * scale) * px_per_unit
        top = oy + (baseline - glyph.baseline_offset * scale) * px_per_unit
        pel_px = px_per_unit * scale
        rows = glyph.bits()
        if pel_px >= 1.0:
            for y, row in enumerate(rows):
                py = top + y * pel_px
                for x, bit in enumerate(row):
                    if not bit:
                        continue
                    pxx = left + x * pel_px
                    draw.rectangle([pxx, py, pxx + pel_px - 1, py + pel_px - 1],
                                   fill=color)
            return
        # Below one device pixel per font pel a single pel is smaller than a
        # pixel, so the glyph has to be scaled down as a bitmap instead of
        # stamped pel by pel.
        self._draw_glyph_scaled(draw, glyph, left, top, pel_px, color)

    def _draw_glyph_scaled(self, draw, glyph, left: float, top: float,
                           pel_px: float, color) -> None:
        """Draw a glyph that is smaller than one device pixel per font pel.

        One font pel is then smaller than a device pixel and the 1-bit glyph
        bitmap has to be reduced.  The reduction is an **area average**: every
        destination pixel takes the fraction of its source pels that carry
        ink.  A stroke thinner than a device pixel therefore survives as
        partial coverage instead of disappearing — sampling one source pel per
        destination pixel would drop every other column of the glyph and
        turn, say, 日 into a single vertical stroke.
        """
        rows = glyph.bits()
        height = len(rows)
        width = len(rows[0]) if rows else 0
        if not width or not height:
            return
        x0 = int(math.floor(left))
        y0 = int(math.floor(top))
        x1 = int(math.ceil(left + width * pel_px))
        y1 = int(math.ceil(top + height * pel_px))
        if x1 <= x0 or y1 <= y0:
            return
        bitmap = np.array(rows, dtype=bool)
        mask = Image.fromarray((bitmap * 255).astype("uint8"), mode="L")
        mask = mask.resize((x1 - x0, y1 - y0), Image.BOX)
        patch = Image.new("RGB", (x1 - x0, y1 - y0), color)
        draw._image.paste(patch, (x0, y0), mask)

    def _draw_rule(self, draw, inline: int, baseline: int, params: bytes,
                   offset, axis: str, color=BLACK):
        """PTOCA rule: DBR runs along the B axis, DIR along the I axis."""
        length = s16(params[0:2])
        width = 1.0
        if len(params) >= 5:
            width = s16(params[2:4])
            if params[4] & 0x80:
                width += 0.5
        ox, oy = offset
        pu = self.px_per_unit
        if axis == "B":
            x0, y0 = inline, baseline
            x1, y1 = inline, baseline + length
            wpx = max(1, int(round(width * pu)))
            draw.rectangle([ox + x0 * pu, oy + y0 * pu,
                            ox + x1 * pu + wpx - 1, oy + y1 * pu], fill=color)
        else:
            x0, y0 = inline, baseline
            x1, y1 = inline + length, baseline
            hpx = max(1, int(round(width * pu)))
            draw.rectangle([ox + x0 * pu, oy + y0 * pu,
                            ox + x1 * pu, oy + y1 * pu + hpx - 1], fill=color)

    # -- graphics ---------------------------------------------------------
    def draw_graphic_object(self, data: bytes, image: Image.Image,
                            offset=(0, 0)):
        """Render one GOCA graphics object into ``image``."""
        seg = parse_begin_segment(data)
        renderer = GocaRenderer(image, self.px_per_unit, self.units_per_inch,
                                offset)
        renderer.render(seg.data)
        self.goca_warnings.extend(renderer.warnings)
        return renderer


def parse_mcf(data: bytes) -> dict[int, str]:
    """Map coded font local IDs to coded font names (MO:DCA Reference p.284)."""
    out: dict[int, str] = {}
    i = 0
    while i < len(data):
        rg_len = int.from_bytes(data[i:i + 2], "big")
        group = data[i:i + rg_len]
        i += rg_len
        j = 2
        local = None
        name = None
        while j < len(group):
            tlen = group[j]
            ttype = group[j + 1]
            tdata = group[j + 2:j + tlen]
            j += tlen
            if ttype == 0x02 and tdata and tdata[0] == 0x8E:
                name = tdata[2:10].decode("cp037")
            elif ttype == 0x24 and len(tdata) >= 2:
                local = tdata[1]
        if local is not None and name:
            out[local] = name
    return out


class Composer:
    """Draws the objects of a page, an overlay or a page segment.

    Every container (page, overlay) has its own presentation space, defined by
    its Page Descriptor, and its own Map Coded Font.  A page segment is not a
    container of its own: it is drawn into the including page or overlay at the
    reference point given by the IPS structured field.
    """

    def __init__(self, resolver: FontResolver, dpi: float, resources=None):
        self.resolver = resolver
        self.dpi = dpi
        self.resources = resources or {}
        self.warnings: list[str] = []
        self.renderers: list[Renderer] = []

    # -- helpers ----------------------------------------------------------
    def _renderer(self, units_per_inch: float) -> Renderer:
        r = Renderer(self.resolver, self.dpi, units_per_inch)
        self.renderers.append(r)
        return r

    @staticmethod
    def _first(structures, acronym: str):
        for st in structures:
            if st.acronym == acronym:
                return st
        return None

    # -- containers -------------------------------------------------------
    def render_container(self, structures, target: Image.Image,
                         origin_px=(0, 0), units_per_inch: float = 240.0):
        """Draw a page or overlay into ``target``.

        ``origin_px`` is the pixel position of the container's coordinate
        system origin inside ``target``.
        """
        pgd = self._first(structures, "PGD")
        if pgd is not None:
            geom = PageGeometry(pgd.data)
            units_per_inch = geom.units_per_inch
        renderer = self._renderer(units_per_inch)
        px_per_unit = renderer.px_per_unit
        draw = ImageDraw.Draw(target)

        # The text presentation space has its own unit base and unit count
        # (MO:DCA Reference p.661); its extent must equal the extent of the
        # including page or overlay presentation space.
        text_renderer = renderer
        ptd = self._first(structures, "PTD")
        if ptd is not None:
            tgeom = TextGeometry(ptd.data)
            if pgd is not None and (tgeom.x_size != geom.x_size
                                    or tgeom.y_size != geom.y_size):
                self.warnings.append(
                    f"text presentation space extent {tgeom.x_size} x "
                    f"{tgeom.y_size} differs from the page extent "
                    f"{geom.x_size} x {geom.y_size}")
            if tgeom.units_per_inch != units_per_inch:
                text_renderer = self._renderer(tgeom.units_per_inch)

        mcf = self._first(structures, "MCF")
        mcf_fonts = parse_mcf(mcf.data) if mcf else {}

        for st in structures:
            if st.acronym == "PTX":
                text_renderer.draw_text_object(st.data, mcf_fonts, draw,
                                               origin_px)
            elif st.acronym == "GAD":
                renderer.draw_graphic_object(st.data, target, origin_px)
            elif st.acronym == "IPO":
                self._include_overlay(st, target, origin_px, units_per_inch)
            elif st.acronym == "IPS":
                self._include_page_segment(st, target, origin_px,
                                           units_per_inch)
        self.warnings.extend(renderer.goca_warnings)
        return renderer

    # -- includes ---------------------------------------------------------
    def _include_overlay(self, st, target: Image.Image, origin_px,
                         units_per_inch: float):
        """IPO - include a page overlay resource."""
        data = st.data
        name = data[0:8].decode("cp037")
        x_off = s24(data[8:11])
        y_off = s24(data[11:14])
        orient = int.from_bytes(data[14:16], "big")
        if orient != 0:
            self.warnings.append(
                f"overlay {name!r} has orientation {orient:#06x}; only 0 "
                f"degrees is implemented")
        resource = self.resources.get(name)
        if resource is None:
            self.warnings.append(f"overlay resource {name!r} not found")
            return
        # The overlay has its own presentation space, defined by its own Page
        # Descriptor; it is rendered on its own canvas and then placed on the
        # including page at the offset given by the IPO.
        pgd = self._first(resource.structures, "PGD")
        if pgd is None:
            self.warnings.append(f"overlay {name!r} has no Page Descriptor")
            return
        geom = PageGeometry(pgd.data)
        pu = self.dpi / geom.units_per_inch
        width = int(round(geom.x_size * pu))
        height = int(round(geom.y_size * pu))
        # The overlay canvas starts out transparent.  MO:DCA defines the
        # foreground of a presentation space as "the part of the presentation
        # space that is occupied with object data" and the background as the
        # rest of it, which is implicitly the colour of the medium
        # [mo-dca-reference-mixed-object-document-content-architecture-reference p.77];
        # the default mixing rule makes that background underpaint the page
        # while the foreground overpaints it
        # [mo-dca-reference-mixed-object-document-content-architecture-reference p.80],
        # so only the pixels the overlay actually draws may be opaque.
        # Without this, the white background of the second overlay would
        # erase the frames the first overlay drew.
        canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        self.render_container(resource.structures, canvas, (0, 0),
                              geom.units_per_inch)
        # The offset is expressed in the units of the *including* page.
        px = self.dpi / units_per_inch
        target.paste(canvas.convert("RGB"),
                     (int(round((origin_px[0] + x_off * px))),
                      int(round((origin_px[1] + y_off * px)))),
                     canvas.getchannel("A"))

    def _include_page_segment(self, st, target: Image.Image, origin_px,
                               units_per_inch: float):
        """IPS - include a page segment resource."""
        data = st.data
        name = data[0:8].decode("cp037")
        x_off = s24(data[8:11])
        y_off = s24(data[11:14])
        resource = self.resources.get(name)
        if resource is None:
            self.warnings.append(f"page segment resource {name!r} not found")
            return
        pu = self.dpi / units_per_inch
        base_x = origin_px[0] + x_off * pu
        base_y = origin_px[1] + y_off * pu
        for image in collect_im_images(resource.structures):
            upt_x = units_per_inch / image.points_per_inch_x
            upt_y = units_per_inch / image.points_per_inch_y
            origin = (base_x / pu + image.ioc.x_oa_oset * upt_x,
                      base_y / pu + image.ioc.y_oa_oset * upt_y)
            render_im_image(image, target, origin, pu, units_per_inch)


RES_FILE_RE = re.compile(r"^(?P<docname>.+)\.afp(?:\.\d+)?\.res$", re.I)


def load_resources(directory: str, prefer_stem: str | None = None):
    """Load every external resource file found in ``directory``.

    A resource archive can hold one ``.res`` per print job, and two of those
    files may offer the same resource name with different content.  Each
    ``.res`` is named after the document it belongs to
    (``<document name>.afp.<group>.res``); the file whose document name is a
    suffix of ``prefer_stem`` — the name of the AFP being rendered — wins.
    Otherwise the first file in sorted order is used, which keeps the choice
    deterministic.

    Returns the resource table and a mapping from resource name to the
    ``.res`` file it came from, so the caller can report the provenance.
    """
    resources: dict = {}
    source: dict[str, str] = {}
    files = sorted(n for n in os.listdir(directory) if n.lower().endswith(".res"))

    def matches(name: str) -> bool:
        if not prefer_stem:
            return False
        m = RES_FILE_RE.match(name)
        return bool(m) and prefer_stem.endswith(m.group("docname"))

    ordered = ([n for n in files if matches(n)]
               + [n for n in files if not matches(n)])
    for name in ordered:
        for key, value in parse_resource_file(
                os.path.join(directory, name)).items():
            if key not in resources:
                resources[key] = value
                source[key] = name
    return resources, source


def render_page(page, resolver: FontResolver, dpi: float, out_path: str,
                resources=None):
    pgd = page.first("PGD")
    geom = PageGeometry(pgd.data)
    px_per_unit = dpi / geom.units_per_inch
    width = int(round(geom.x_size * px_per_unit))
    height = int(round(geom.y_size * px_per_unit))
    img = Image.new("RGB", (width, height), WHITE)

    composer = Composer(resolver, dpi, resources)
    composer.render_container(page.structures, img, (0, 0), geom.units_per_inch)
    # Store the resolution so that a viewer or print driver uses the real
    # physical size (2041 x 2882 units at 240 units/inch = 8.50 x 12.01 in)
    # instead of assuming 72 dpi.
    img.save(out_path, dpi=(dpi, dpi))
    for warning in composer.warnings:
        print(f"warning: {warning}")
    return img, geom, composer


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render an AFP page to PNG")
    ap.add_argument("afp")
    ap.add_argument("--resources", required=True,
                    help="directory holding the FOCA resources and the .res file")
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--dpi", type=float, default=300.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--font-map", default=None,
                    help="JSON object mapping AFP font names to resource names")
    args = ap.parse_args(argv)

    if os.path.isdir(args.out):
        ap.error(f"--out must be a file path, not a directory: {args.out}")
    if not os.path.splitext(args.out)[1]:
        ap.error(f"--out must name a file with an extension: {args.out}")

    _, pages = load_document(args.afp)
    page = pages[args.page - 1]
    name_map = None
    if args.font_map:
        mapping = json.load(open(args.font_map, encoding="utf-8"))
        name_map = lambda n: mapping.get(n, n)  # noqa: E731
    resolver = FontResolver(ResourceLibrary(args.resources), name_map)
    stem = os.path.splitext(os.path.basename(args.afp))[0]
    resources, sources = load_resources(args.resources, prefer_stem=stem)
    used = sorted(set(sources.values()))
    if used and not any(RES_FILE_RE.match(n) and
                        stem.endswith(RES_FILE_RE.match(n).group("docname"))
                        for n in used):
        print(f"note: no .res file in the resource directory is named after "
              f"this document; the resources come from {', '.join(used)}")
    img, geom, composer = render_page(page, resolver, args.dpi, args.out,
                                      resources)
    print(f"page {args.page}: {geom.x_size} x {geom.y_size} units "
          f"({geom.x_size / geom.units_per_inch:.2f} x "
          f"{geom.y_size / geom.units_per_inch:.2f} in), "
          f"{img.width} x {img.height} px at {args.dpi} dpi -> {args.out}")


if __name__ == "__main__":
    main()
