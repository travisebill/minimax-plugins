---
name: afp-renderer
description: |
  Rasterise an AFP / MO:DCA document page into a PNG image.
  Use this skill whenever the task asks to render, rasterise, preview, screenshot
  or "see what it looks like" for an AFP file — for example "把這份 AFP 轉成圖片",
  "render this .afp to PNG", "預覽這個 AFP 頁面", "this AFP looks blank, show me
  what the page contains". It decodes the MO:DCA data stream, the FOCA fonts,
  PTOCA text, GOCA graphics and IOCA images and composites them into a
  black-on-white page image, with every drawing rule traced to a specification
  page. Do NOT use it for PDF/PostScript conversion, for editing the AFP bytes
  themselves (use the afpds-expert skill), or for a document that has no
  external resource file available.
---

# AFP renderer

Turn an AFP data stream into a picture of the page.  The renderer is a Python
package under `scripts/afp_render/` in this skill; it was written because no
mature open-source AFP renderer exists (see the sibling `afpds-expert` skill's
`references/ecosystem.md`).

The package loads the 98 MO:DCA structure identifiers from
`research/modca-structure-table.json` next to it — the same machine-built table
the `afpds-expert` skill ships as `scripts/mo-dca-structures.mjs`, with each
row's corpus page behind it.  **Do not remove that file**: the parser reads it
at import time, so the renderer fails to start without it.

Every rule that is not obvious carries a specification page citation in the
docstring of the module that implements it, and `references/renderer.md` repeats
the ones that are easy to get wrong.  **Read the citation before you trust a
behaviour** — several of them (the even/odd fill rule, the overlay mixing
rule, the unit bases) look wrong at first glance and are not.

## Inputs to collect

- **The AFP file.**  Ask for it; do not guess its structure from its size.
- **The resource directory.**  This is the part people forget.  The renderer
  needs
  - the FOCA font resources (`.FON`, `.CHS`, `.CDP`, …), and
  - the MO:DCA external resource file(s) (`*.res`) that hold the page overlays
    and page segments.

  Without the `.res` file the page renders with its text and its own graphics
  but **no overlay and no barcode** — that is the usual reason a render looks
  half-empty.
- **Which page**, and the resolution.  300 dpi is the default; below 300 dpi a
  stroke thinner than a device pixel survives only as partial coverage.
- The page geometry is read from the AFP's own Page Descriptor, so nothing has
  to be supplied for it.

## Procedure

1. **Check the runtime.**  The renderer needs Python 3.11+, `Pillow` and
   `numpy`.  If an import fails, install them into the user's environment
   (`python3 -m pip install --user Pillow numpy`) rather than rewriting the
   renderer to avoid them.

2. **Render the page.**

   ```bash
   python3 scripts/afp_render/render.py <file.afp> \
       --resources <dir> --page 1 --dpi 300 --out page1.png
   ```

   The script prints the page geometry, the output pixel size and any
   warnings.  A `note:` line about `.res` provenance is informational; a
   `warning:` line means something in the stream is not implemented the way the
   document expects.

3. **Look at the output before claiming success.**  Read the PNG back and
   check the things a wrong renderer produces quietly: text upside down or
   mirrored, tofu boxes instead of glyphs, a stretched or distorted image,
   rules in the wrong place, content missing, content drawn twice.  A render
   that produces a file is not the same as a render that produced the right
   picture.

4. **Decide whether what you see is a bug.**  Some oddities are the
   document's own layout, not the renderer's fault — overlapping labels, a
   logo printed over a heading, rules that run off the page edge.  Check the
   AFP structure order before calling a position wrong: the page's own
   objects are merged onto the presentation space in the order they appear
   [mo-dca-reference-mixed-object-document-content-architecture-reference p.78],
   and an overlay is merged before the page's own objects if it is included
   first.  A white band that erases the overlay text underneath it is the
   document's own erase, not a compositing bug.

5. **Report honestly.**  State the resolution, the pixel size, and anything
   the renderer warned about.  If the render is missing content because a
   resource was absent, say that instead of delivering the picture as if it
   were the document.

## Composition order (the rule that breaks overlays)

An overlay is composited as a **transparent layer**, never as an opaque white
sheet: MO:DCA defines the foreground of a presentation space as "the part of
the presentation space that is occupied with object data"
[mo-dca-reference-mixed-object-document-content-architecture-reference p.77],
and the default mixing rule makes the background *underpaint* the page while
the foreground overpaints it
[mo-dca-reference-mixed-object-document-content-architecture-reference p.80].
MO:DCA says it directly for object areas: "An empty object area is
transparent" [mo-dca-reference-mixed-object-document-content-architecture-reference p.82].

If a second overlay is pasted as an opaque white rectangle it erases
everything the first overlay drew.  That single mistake removes an entire
label row and every table frame in the test document.

## Failure handling

- **The page renders but the overlays are missing** — the resource directory
  has no matching `.res` file, or has one for a different print job.  The
  `note:` line names the files that were used; ask the user for the `.res`
  that belongs to *this* AFP if the names do not match.
- **A coded font cannot be found** — the renderer maps `X1FNT007` to
  `X0FNT007.FON` by substituting the first two characters.  If the resource
  set uses other names, map them with `--font-map`.
- **An unsupported GOCA order** — the renderer reports it as a warning rather
  than ignoring it.  That order is drawn incorrectly or not at all; say so.
- **The output is blank or nearly blank** — check that the page number is
  right and that the resource directory is the one for this document.  Do not
  conclude that the AFP is empty before checking both.
- **Text renders as boxes** — the character set or code page in the resource
  set does not match the coded font the AFP asks for.
- **The requested resolution is below 300 dpi** — expect thin strokes to be
  grey rather than black.  Render at 300 dpi and downscale the image instead
  if publication quality matters.

## Output contract

- The PNG, with the resolution it was rendered at stated.
- The pixel size and the physical size it corresponds to.
- Every warning the renderer printed, quoted.
- Any part of the page that could not be rendered faithfully, and why.

Do not claim the render is "identical to what the printer produces" — this
renderer has been checked against the specifications and for internal
consistency, not against a physical print.
