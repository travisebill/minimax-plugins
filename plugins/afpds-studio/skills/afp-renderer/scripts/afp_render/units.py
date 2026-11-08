"""Measurement unit bases used by the MO:DCA descriptors.

Three descriptors carry a unit base per axis, and they do **not** all allow
the same values.

* The **Page Descriptor** allows X'00'–X'01': X'00' is a 10 inch base and
  X'01' is a 10 centimetre base
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.355].
  The same page also carries an exception condition: a X'01' exception
  condition exists if the XpgBase and YpgBase values are not identical.
* The **Presentation Text Descriptor** restricts the unit base to X'00', i.e.
  10 inches
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.660].
* The **IM Image Input Descriptor** restricts the unit base to X'00' as well,
  i.e. 10 inches
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.664].

Anything outside the permitted set is a specification violation.  These
helpers raise instead of guessing a length, because silently assuming ten
inches would scale a page or an image by the wrong factor and still produce
a plausible-looking picture.
"""

from __future__ import annotations

CM_PER_INCH = 2.54

# Page Descriptor unit bases (MO:DCA Reference p.355).
PAGE_BASE_INCHES = {
    0x00: 10.0,
    0x01: 10.0 / CM_PER_INCH,
}

# The only unit base the Presentation Text Descriptor (p.660) and the IM Image
# Input Descriptor (p.664) allow.
INCH_BASE_CODE = 0x00
INCH_BASE = 10.0


def page_base_inches(code: int) -> float:
    """Length in inches of a Page Descriptor unit base code."""
    try:
        return PAGE_BASE_INCHES[code]
    except KeyError:
        allowed = ", ".join(f"X'{c:02X}'" for c in sorted(PAGE_BASE_INCHES))
        raise ValueError(
            f"unsupported page unit base X'{code:02X}': MO:DCA defines "
            f"{allowed}"
        ) from None


def inch_base(code: int, what: str) -> float:
    """Length in inches of a unit base that may only be X'00'."""
    if code != INCH_BASE_CODE:
        raise ValueError(
            f"unsupported {what} X'{code:02X}': only X'00' (10 inches) is "
            f"defined for this descriptor"
        )
    return INCH_BASE
