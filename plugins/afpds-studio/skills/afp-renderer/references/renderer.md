# AFPDS renderer — reference

A self-contained AFP → PNG renderer for MO:DCA documents, implemented as a
Python package under `scripts/afp_render/`.  There is no mature open-source
AFP renderer (see the sibling skill's `references/ecosystem.md`), so this
decodes the stream, the FOCA fonts, PTOCA text, GOCA graphics and IOCA images
directly against the AFPC corpus.

Everything here is **derived from the corpus**, and every rule that is not
obvious carries a page citation in the docstring of the module that implements
it.  Read the citation before trusting the behaviour.

All page numbers are **PDF page numbers** — the `<<<PAGE n>>>` marker in the
corpus text, not the printed page number in the document footer.

## Usage

```bash
python3 scripts/afp_render/render.py <file.afp> \
    --resources <dir-with-fonts-and-.res> \
    --page 1 --dpi 300 --out page1.png
```

`--resources` must contain

* the FOCA font resources (`.FON`, `.CHS`, `.CDP`, …), and
* the MO:DCA external resource file(s) (`*.res`) that hold the page overlays
  and page segments.

  A resource archive can hold one `.res` per print job, and two of them may
  offer the same resource name with different content.  Each `.res` is named
  after its document (`<document name>.afp.<group>.res`); the renderer prefers
  the file whose document name ends the name of the AFP being rendered and
  otherwise takes the first file in sorted order, so the choice is
  deterministic; when no file matches it prints a `note:` line naming the
  files it used.

`--font-map` takes a JSON object that overrides the coded-font name mapping.
The default substitutes the first two characters, so a coded font the AFP asks
for as `X1FNT007` resolves to a shipped resource file named `X0FNT007.FON`.  A
differently named resource set only needs this one mapping changed.

The renderer is not limited to the first page — the 96-page test document
renders end to end with no errors and no warnings.  Only pages 1 to 3 have
been inspected in detail.

### Requirements

Python 3.11 or later, `Pillow` and `numpy`:

```bash
python3 -m pip install --user Pillow numpy
```

## Modules

| Module | Responsibility |
| --- | --- |
| `afpstream.py` | AFP data-stream framing and object model (5A / Len / ID / Flags / Seq / Data). |
| `resources.py` | FOCA resource library: code pages, character sets, `.FON`/`.CHS`/`.CDP` chains, bitmaps. |
| `resfile.py` | MO:DCA external resource file (`.res`): BRG/ERS wrapped overlays and page segments. |
| `ptoca.py` | PTOCA control-sequence framing (unchained `2B D3 LEN TYPE params`, chained `LEN TYPE params`). |
| `goca.py` | GOCA drawing orders, areas, patterns, fillets. |
| `imimage.py` | IOCA IM images (IOC / IID / ICP / IRD) and their rasterisation. |
| `colors.py` | GOCA / PTOCA / Standard OCA colour tables. |
| `units.py` | Unit bases of the Page / Presentation Text / IM Image descriptors. |
| `render.py` | Composition: page → overlays → page segments → PNG. |

## Coordinate spaces

* The **presentation space** unit comes from the Page Descriptor: `XpgUnits`
  page units per unit base.  With `XpgBase = X'00'` the base is 10 inches, so
  2400 units = 240 units/inch
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.355].
  The base is not always inches: `XpgBase` may also be X'01', which is a
  10 centimetre base
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.355],
  and a page whose X and Y unit bases differ is an X'01' exception condition.
  The Presentation Text Descriptor and the IM Image Input Descriptor both
  restrict their unit base to X'00', i.e. 10 inches
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.660]
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.664];
  `units.py` rejects any other value instead of guessing a length.
* The **text presentation space** has its own unit base and unit count in the
  Presentation Text Descriptor (`XptBase`/`YptBase`, `XptUnits`/`YptUnits`),
  and its extent must equal the extent of the including page or overlay
  presentation space
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.661].
  The renderer reads the PTD, uses its units for text, and warns if the text
  extent does not match the page extent.  Because the PTD extent in the test
  document is stored in three bytes (not two, as the summary table's "UBIN"
  label suggests) the three-byte reading is the one that reproduces the page
  descriptor's extent exactly.
* A FOCA font measures in its own pels; the font control declares
  `XftUnits` [foca-reference-font-object-content-architecture-reference p.168]
  as 3000 pels per 10 inches, i.e. 300 pels/inch, so the scale factor onto
  the page is `page units per inch / font pels per inch`
  [foca-reference-font-object-content-architecture-reference p.170].
* An **overlay** has its own Page Descriptor and its own presentation space.
  The IPO offset places the overlay's origin on the including page
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.267];
  the overlay is rendered on its own canvas and pasted, unscaled.
* An **overlay is a layer, not an opaque sheet.**  An overlay is a page-like
  resource object with its own environment parameters, positioned on the
  including page
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.43];
  when its presentation space is merged onto the page's, the default MO:DCA
  mixing rule applies: "the background of Pn underpaints the background and
  foreground of Pe" and "the foreground of Pn overpaints the background and
  foreground of Pe"
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.80].
  Underpainting means "the intersection keeps the color attribute of Pe",
  which the specification calls "transparent mixing or leave alone mixing"
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.80].
  So only the pixels the overlay actually draws are opaque, and the second
  overlay does not erase the frames the first one drew.  This matters in the
  test document: the two overlays both draw tables, and one of them draws the
  field labels for a table whose frame the other one draws.  A fill in the
  color of medium is a foreground fill, so it overpaints like any other
  fill — the overlay only leaves the *undrawn* parts of its presentation
  space transparent.

  **Why the background is transparent.**  MO:DCA defines the foreground of a
  presentation space as "the part of the presentation space that is occupied
  with object data" and the background as the rest of it, which is
  "implicitly assigned the color of the medium"
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.77];
  the default mixing rule then makes that background underpaint the page
  while the foreground overpaints it, and MO:DCA states the same conclusion
  for object areas directly: "An empty object area is transparent"
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.82].
  Table 11 says the same thing in its own words: an *Empty* object area, page
  or overlay presentation space has no foreground and the complete
  presentation space as its background
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.78],
  and that background is the colour of the medium, which the default mixing
  rule leaves alone.

  **The one place the specification does not line up.**  Table 11 gives a
  *Colored* object area, page, or overlay presentation space a foreground of
  "Complete presentation space" and no background
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.78],
  which read literally would make every overlay an opaque sheet.  That row
  describes a presentation space that has been given a colour attribute for
  the whole space — "If a Color Specification (X'4E') triplet is specified on
  the OBD, it can color the object area"
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.82]
  — and neither overlay of the test document does that: each only draws
  objects into its presentation space, so each is merged with the default rule
  above.
* A **page segment** has no presentation space of its own.  It is drawn into
  the including page or overlay at the reference point given by the IPS
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.269];
  the IM image origin inside the segment is then offset by the IOC offsets.

## Drawing rules that are easy to get wrong

* **GOCA area fill.** `GBAR` bit 1 = BOUNDARY, bit 2 = INSIDE
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.102];
  the bits of a byte are numbered from the most significant one, so bit 0 is
  X'80' and bit 2 is X'20'
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.51].
  INSIDE = 0 is *alternate* (even/odd) mode, so
  a figure nested inside another figure is a **hole**
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.57].  A *rounded rectangle outline* is therefore drawn as two nested
  figures filled with the even/odd rule.
* **Pattern symbols.** X'0F' = no fill, X'40' = blank (same as X'0F'),
  X'10' = solid fill
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.179]
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.59].
  Figure 19 on printed page 40 (PDF page 60
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.60])
  illustrates the same set and **agrees** with the table: cells 1 to 8 are the
  dotted patterns of decreasing density, 9 and 10 the vertical and the
  horizontal lines, 11 to 14 the four diagonal-line patterns, the 15th
  (X'0F') is drawn blank and the 16th (X'10') is solid.  The figure has no
  text layer, so this can only be checked against the page image.
* **Area attributes are captured at GBAR time** — pattern set, pattern symbol
  and pattern colour are the ones current when the Begin Area order executes
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.102].
* **Boundary lines** are drawn only when the BOUNDARY bit is set, and use the
  line attributes that were current when each defining order executed
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.58].
* **Move Type orders inside an area** start a new closed figure; they do not
  draw lines themselves
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.56].
* **GSCOL** operand X'00'–X'08' is prefixed with X'FF' to form the colour
  index; X'07' = device default, X'08' = colour of medium (white paper)
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.162].
* **PTOCA STC X'FF08'** is the *erase* function — the receiver's background
  colour is used as the foreground colour
  [ptoca-reference-presentation-text-object-content-architecture-reference p.122].
* **IM image** data is one continuous MSB-first bit stream for the whole
  image; scan lines are **not** individually byte aligned
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.667].

## Known limitations

* Only orientation 0 (no rotation) is implemented for overlays; a non-zero
  orientation produces a warning.
* **Fillet geometry is implemented for the two-line case only.**  A fillet order
  that supplies three or more points (more than two conceptual lines), or whose
  adjacent segments have different lengths, is approximated with a circular arc
  whose tangent length is the shorter adjacent segment.  The specification
  defines those cases through a sharpness parameter that AFP GOCA does not
  support [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.46].
  Every fillet in the test document supplies two points, so the current position
  plus two operand points, and its adjacent segments are equal — the arc then
  coincides exactly with the quarter circle the specification describes.
* The default pattern set's dot size, dot spacing, line thickness and line
  spacing are implementation differences between presentation devices
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.60];
  a nominal 8-unit cell is used.
* A GOCA drawing order that the renderer does not implement is reported as an
  unsupported order rather than silently ignored.  GOCA mentions one order
  that is *not* in the Summary List of Orders but that some printers accept
  as a no-op — Set Pick Identifier (GSPIK, X'43')
  [afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.101].
* Character glyph rasterisation is unfiltered at the font's native resolution;
  no hinting or smoothing.  At 300 dpi one font pel is at least one device
  pixel and every pel is stamped on its own, so the output stays bilevel.
  Below 300 dpi one pel is smaller than a device pixel (the fonts here are
  300 pel/inch, so one pel is `dpi / 300` pixels) and the glyph has to be
  reduced; the reduction is an area average, so a stroke that is thinner than
  a device pixel survives as partial coverage (grey) instead of being
  dropped.
* The renderer targets a bilevel (black on white) presentation device.  The
  one exception is a glyph drawn below the font's native resolution, whose
  strokes are rendered as partial coverage rather than dropped.
* The renderer has been checked against an internal consistency test only.
  There is no side-by-side comparison against a real printer or a commercial
  RIP, so "correct" here means "consistent with the specifications and
  internally consistent", not "pixel-identical to a physical print".
