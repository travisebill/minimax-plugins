"""IM image (MO:DCA) decoding and rendering.

An IM image object is the MO:DCA presentation object that carries a raster
image.  It is described by four structures, all of them defined in the MO:DCA
Reference:

* **IOC** — IM Image Output Control
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.665].
  Bytes 0-2 XoaOset, 3-5 YoaOset (offsets of the object area origin, in *image
  points*), 6-7 XoaOrent, 8-9 YoaOrent (rotation), 10-17 constant, 18-19 XMap,
  20-21 YMap, 22-23 constant.  XMap/YMap X'03E8' means "image point-to-pel".
* **IID** — IM Image Input Descriptor
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.664].
  Bytes 0-11 constant, 12 XBase, 13 YBase, 14-15 XUnits, 16-17 YUnits
  (image points per unit base; X'00' = 10 inches), 18-19 XSize, 20-21 YSize
  (extent of a *non-celled* image, in image points), 22-27 constant, 28-29
  XCSizeD, 30-31 YCSizeD (default cell extent), 32-33 constant, 34-35 Color.
* **ICP** — IM Image Cell Position
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.662, p.663].
  Bytes 0-1 XCOset, 2-3 YCOset (cell offset from the object area origin, in
  image points), 4-5 XCSize, 6-7 YCSize (cell extent in image points), 8-9
  XFilSize, 10-11 YFilSize (fill rectangle extent in image points; X'FFFF'
  means "use the cell extent").  The cell is *repeated* in X and Y to fill the
  fill rectangle, and may be truncated to fit.
* **IRD** — IM Image Raster Data
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.667].
  One bit per image point, "grouped into bytes and ordered from left to right
  within each byte", recorded left to right in scan lines, scan lines from top
  to bottom.  Only the *last* byte of the whole image data is padded to a byte
  boundary — the rows are not individually aligned.

The raster therefore holds XCSize x YCSize image points as one continuous bit
stream; this is what makes a 261-point-wide image occupy exactly 1305 bytes
(261 x 40 / 8) rather than 1320 (33 bytes per aligned row).

A bit with value B'1' indicates a significant image point and is painted with
the colour given by the IID Color field; a bit with value B'0' indicates an
insignificant image point, which is left untoned
[mo-dca-reference-mixed-object-document-content-architecture-reference p.667].
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from PIL import Image

from afp_render.colors import oca_color
from afp_render.units import inch_base


@dataclass
class Ioc:
    """IM Image Output Control."""

    x_oa_oset: int = 0
    y_oa_oset: int = 0
    x_oa_orent: int = 0
    y_oa_orent: int = 0
    x_map: int = 0
    y_map: int = 0


@dataclass
class Iid:
    """IM Image Input Descriptor."""

    x_base: int = 0
    y_base: int = 0
    x_units: int = 0
    y_units: int = 0
    x_size: int = 0
    y_size: int = 0
    xc_size_d: int = 0
    yc_size_d: int = 0
    color: int = 0


@dataclass
class Icp:
    """IM Image Cell Position."""

    xc_offset: int = 0
    yc_offset: int = 0
    xc_size: int = 0
    yc_size: int = 0
    x_fil_size: int = 0
    y_fil_size: int = 0


@dataclass
class ImImage:
    """One IM image data object."""

    name: str = ""
    ioc: Ioc = field(default_factory=Ioc)
    iid: Iid = field(default_factory=Iid)
    icp: Icp = field(default_factory=Icp)
    raster: bytes = b""

    # -- geometry ---------------------------------------------------------
    @property
    def points_per_inch_x(self) -> float:
        """Image points per inch along X (IID XUnits per unit base)."""
        return self.iid.x_units / self._base_inches()

    @property
    def points_per_inch_y(self) -> float:
        return self.iid.y_units / self._base_inches()

    def _base_inches(self) -> float:
        """Length in inches of the IM image unit base.

        The IM Image Input Descriptor restricts the unit base to X'00', i.e.
        10 inches
        [mo-dca-reference-mixed-object-document-content-architecture-reference p.664];
        any other value is rejected rather than assumed, because guessing ten
        inches would scale the image by the wrong factor.
        """
        return inch_base(self.iid.x_base, "IM image unit base")

    @property
    def cell_size(self) -> tuple[int, int]:
        return (self.icp.xc_size, self.icp.yc_size)

    @property
    def fill_size(self) -> tuple[int, int]:
        x = self.icp.x_fil_size
        y = self.icp.y_fil_size
        if x == 0xFFFF:
            x = self.icp.xc_size
        if y == 0xFFFF:
            y = self.icp.yc_size
        return (x, y)


def parse_ioc(data: bytes) -> Ioc:
    return Ioc(
        x_oa_oset=int.from_bytes(data[0:3], "big"),
        y_oa_oset=int.from_bytes(data[3:6], "big"),
        x_oa_orent=int.from_bytes(data[6:8], "big"),
        y_oa_orent=int.from_bytes(data[8:10], "big"),
        x_map=int.from_bytes(data[18:20], "big"),
        y_map=int.from_bytes(data[20:22], "big"),
    )


def parse_iid(data: bytes) -> Iid:
    return Iid(
        x_base=data[12],
        y_base=data[13],
        x_units=int.from_bytes(data[14:16], "big"),
        y_units=int.from_bytes(data[16:18], "big"),
        x_size=int.from_bytes(data[18:20], "big"),
        y_size=int.from_bytes(data[20:22], "big"),
        xc_size_d=int.from_bytes(data[28:30], "big"),
        yc_size_d=int.from_bytes(data[30:32], "big"),
        color=int.from_bytes(data[34:36], "big"),
    )


def parse_icp(data: bytes) -> Icp:
    return Icp(
        xc_offset=int.from_bytes(data[0:2], "big"),
        yc_offset=int.from_bytes(data[2:4], "big"),
        xc_size=int.from_bytes(data[4:6], "big"),
        yc_size=int.from_bytes(data[6:8], "big"),
        x_fil_size=int.from_bytes(data[8:10], "big"),
        y_fil_size=int.from_bytes(data[10:12], "big"),
    )


def collect_im_images(structures) -> list[ImImage]:
    """Collect the IM image objects of a page segment or page."""
    images: list[ImImage] = []
    for st in structures:
        if st.acronym == "BII":
            images.append(ImImage(name=st.data[:8].decode("cp037")))
        elif images and st.acronym == "IOC":
            images[-1].ioc = parse_ioc(st.data)
        elif images and st.acronym == "IID":
            images[-1].iid = parse_iid(st.data)
        elif images and st.acronym == "ICP":
            images[-1].icp = parse_icp(st.data)
        elif images and st.acronym == "IRD":
            images[-1].raster += st.data
    return images


def cell_bits(image: ImImage) -> np.ndarray:
    """Return the image cell as a boolean array (significant = True).

    The raster is one continuous bit stream: MSB first inside every byte,
    left to right along a scan line, scan lines from top to bottom.
    """
    w, h = image.cell_size
    if w <= 0 or h <= 0:
        return np.zeros((0, 0), dtype=bool)
    data = np.frombuffer(image.raster, dtype=np.uint8)
    if data.size == 0:
        return np.zeros((h, w), dtype=bool)
    bits = np.unpackbits(data, bitorder="big")
    needed = w * h
    if bits.size < needed:
        bits = np.concatenate([bits, np.zeros(needed - bits.size, dtype=np.uint8)])
    return bits[:needed].reshape(h, w).astype(bool)


def render_im_image(image: ImImage, target: Image.Image,
                    origin: tuple[float, float], px_per_unit: float,
                    units_per_inch: float) -> None:
    """Draw one IM image object onto *target*.

    ``origin`` is the position of the IM image object area origin in
    presentation-space units; ``px_per_unit`` converts presentation units to
    device pixels.
    """
    cell = cell_bits(image)
    if cell.size == 0:
        return
    fill_w, fill_h = image.fill_size
    if fill_w <= 0 or fill_h <= 0:
        return

    # The cell is repeated to fill the fill rectangle.
    reps_y = -(-fill_h // cell.shape[0])
    reps_x = -(-fill_w // cell.shape[1])
    tiled = np.tile(cell, (reps_y, reps_x))[:fill_h, :fill_w]

    color = oca_color(image.iid.color)

    # Image points -> presentation units.
    upt_x = units_per_inch / image.points_per_inch_x
    upt_y = units_per_inch / image.points_per_inch_y

    left = origin[0] + image.icp.xc_offset * upt_x
    top = origin[1] + image.icp.yc_offset * upt_y
    x0 = int(round(left * px_per_unit))
    y0 = int(round(top * px_per_unit))
    w_px = int(round(fill_w * upt_x * px_per_unit))
    h_px = int(round(fill_h * upt_y * px_per_unit))
    if w_px <= 0 or h_px <= 0:
        return

    # Scale the 1-bit cell up to the device resolution.
    sx = max(1, int(round(w_px / fill_w)))
    sy = max(1, int(round(h_px / fill_h)))
    mask = np.repeat(np.repeat(tiled, sy, axis=0), sx, axis=1)
    if mask.shape[0] < h_px:
        mask = np.pad(mask, ((0, h_px - mask.shape[0]), (0, 0)))
    if mask.shape[1] < w_px:
        mask = np.pad(mask, ((0, 0), (0, w_px - mask.shape[1])))
    mask = mask[:h_px, :w_px]

    patch = Image.new("RGB", (w_px, h_px), color)
    alpha = Image.fromarray((mask * 255).astype("uint8"), mode="L")
    target.paste(patch, (x0, y0), alpha)
