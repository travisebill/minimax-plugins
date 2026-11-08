---
name: afpds-expert
description: |
  Build, parse, and validate AFP / AFPDS (Advanced Function Presentation) data streams.
  Use this skill whenever the task touches IPDS transport framing, MO:DCA document
  structure, the OCA content architectures (IOCA image, GOCA graphics, PTOCA text,
  BCOCA barcode, FOCA font), presentation objects, object containers, Active
  Environment Groups, structured fields, AFP fonts, code pages, character data, or
  .afp files. Trigger phrases include "AFP", "AFPDS", "MO:DCA", "IPDS", "presentation
  object", "structured field", "BOC", "AEG", "generate an AFP job", "parse this .afp
  file", "AFP 資料流", "AFP 檔", "呈現物件". Do NOT use for generic PDF/PostScript
  work, printer drivers, or any document-generation library that has nothing to do
  with the AFP architecture.
---

# AFPDS Expert

Read [Codex runtime guidance](../../CODEX.md) before using this skill. Resolve bundled skills and resources relative to this installed package.


Working knowledge of the AFP Consortium's AFP/AFPDS architecture, backed by a local
copy of the complete AFPC publication corpus (32 documents, 5,490 pages) that every
non-obvious constant can be traced back to.

## The one rule that makes this skill trustworthy

**Never state a byte value, structure ID, or ordering rule from memory.** The corpus
is authoritative; your own recollection of "I think BOC is 0xD3A892" is not, and a
single wrong byte produces a stream that silently renders wrong on a printer.

Every claim in the output carries its source page: `[mo-dca-reference-mixed-object-document-content-architecture-reference p.187]`.

## Bundled scripts

| Script | What it does |
|---|---|
| `scripts/spec-search.mjs` | Search the corpus by phrase, by regex, or by page number; `docs` lists all 32 documents. |
| `scripts/verify-stream.mjs` | Walk an AFP file's structured-field chain and check it is well formed (`--tree` prints the object tree; `--layer modca\|ipds` selects the ruleset). |
| `scripts/test-verify-stream.mjs` | Self-test for the validator: builds valid and corrupted streams — with and without the platform `X'5A'` prefix — and asserts the validator accepts the good ones and rejects every broken one. Run it after touching `verify-stream.mjs`. |
| `scripts/mo-dca-structures.mjs` | The 98 MO:DCA structured fields as data: `{ acronym, hex, name, aliases }`. Import it instead of re-typing structure identifiers, and use `hex` for the identifier bytes and `name` for the caption. It is generated from the MO:DCA Reference table of contents, so every entry has a corpus page behind it. |

**The `X'5A'` prefix.** MO:DCA defines a structured field as an SFI plus data, and
`SFLength` counts the structured field itself. Real platforms store the field with
one extra `X'5A'` byte in front of it, and that byte is *not* counted in the length:
"Some platforms include structured fields in a larger platform-specific record by
surrounding the structured field with additional bytes (such as the X'5A' prefix)"
[mo-dca-reference-mixed-object-document-content-architecture-reference p.53].
`verify-stream.mjs` therefore reads the SFI after the prefix when it sees one, and
accepts a prefix-stripped stream as well. IPDS commands have no such prefix —
their length runs `Length(2B) | Command(2B) | Flag(1B) | [CID(2B)] | Data`
[ipds-reference-intelligent-printer-data-stream-reference p.106].

```js
import { MO_DCA_STRUCTURES as structures } from "./scripts/mo-dca-structures.mjs";
const boc = structures.find((s) => s.acronym === "BOC");   // hex: "D3A892"
```

## Inputs to collect

- **Which layer** the task lives in: transport (IPDS), document (MO:DCA), content
  (OCA), resources (fonts/characters), or tooling.
- **Direction**: generating a stream, parsing one, or explaining/validating one.
- **Target output**: a library, a command, a sample file, or an explanation.
- If the user asks to "fix" an AFP file, ask for the file or the bytes — guessing at
  an AFP stream's structure from its size is not workable.

## Procedure

1. **Classify the layer, then read exactly one reference.** See the layer table
   below. Reason: the corpus is 5,490 pages across six architectures; mixing
   IPDS framing rules with MO:DCA document rules produces confidently wrong output.

2. **Pull the exact syntax from the corpus before writing it.** Use the search tool:

   ```bash
   node scripts/spec-search.mjs search "Begin Object Container" --doc modca -n 5 -C 2
   node scripts/spec-search.mjs search "X'D3A892'" --regex --doc modca
   node scripts/spec-search.mjs page modca 187 188
   ```

   `docs` lists all 32 documents with page counts and AFPC document numbers.
   Reason: the references in `references/` are distilled for speed and can drift
   from a specification revision; the corpus is the text of record.

3. **Build the stream as a structure tree, not raw bytes.** Model each structured
   field as (ID bytes, length, flags, data) and let one encoder serialise it.
   Reason: AFP is length-prefixed and nested; hand-assembled byte arrays get the
   length field wrong, and the failure appears only on the printer.

4. **Validate the bytes with the checker before you hand them over.** An AFP stream is
   self-describing — every structured field carries its own Length — so structural
   well-formedness is mechanically decidable:

   ```bash
   node scripts/verify-stream.mjs output.afp --tree
   ```

   It walks the structured-field chain, checks every Length lands exactly on the next
   field boundary, checks Flags/Reserved are `X'0000'`, checks begin/end nesting, and
   prints the object tree with structure names. Exit code 0 means the chain is
   consistent; 1 means it is not, with the offending offset.
   **This checks structure, not semantics** — a stream can pass here and still be
   semantically wrong. It is the cheapest possible test, and it catches the single
   most common defect (a miscomputed length).
   Reason: the alternative is shipping bytes that fail only on a printer.

5. **Work outward through the layers.** Within MO:DCA the nesting is
   print file → document → page group → page → object container → presentation object
   → content. Each layer constrains the one below it, so a valid inner object inside an
   invalid envelope is still an invalid file.

   **IPDS is NOT a layer above MO:DCA — it is a sibling.** MO:DCA and IPDS are the two
   strategic *data stream* architectures; the same OCA content can be carried in
   either. IPDS is a bidirectional command protocol with its own framing, not a
   wrapper around a MO:DCA stream. "You cannot wrap MO:DCA data into an IPDS stream —
   you re-encode the same content as IPDS commands." See `references/ipds.md` §1.

6. **Check the traps section for the layer you are in.** Ordering rules, mandatory
   versus optional structures, and exception conditions are where most generated
   AFP fails.

7. **State what you could not confirm.** If the corpus does not settle a question,
   say so explicitly and say what you did find, rather than filling the gap with a
   plausible-looking value.

## Layer map

| Layer | Reference | Primary corpus documents |
|---|---|---|
| Transport / framing | `references/ipds.md` | IPDS Reference (AFPC-0001-13, 1152p), UP3i v1.20 |
| Document architecture | `references/modca.md` | MO:DCA Reference (AFPC-0004-11, 772p), Presentation Object Subsets |
| Content objects | `references/oca.md` | IOCA 250p, GOCA 248p, PTOCA 244p, BCOCA 266p |
| Fonts & characters | `references/fonts-and-encoding.md` | FOCA 270p, FGID registry, Character Data 320p, Code Pages 490p |
| Line data, metadata, colour | `references/line-data-metadata-color.md` | Line Data 260p, MOCA, CMOCA 160p, ACMA |
| Tooling & ecosystem | `references/ecosystem.md` | external (GitHub/PyPI verification, not spec facts) |

## Corpus access

The search tool resolves the corpus in this order:

1. `$AFPDS_CORPUS`
2. `<skill-dir>/corpus` — the copy bundled with this skill (32 `.txt` files plus
   `index.json`). This is where it resolves in a normal install.

If neither exists, restore the bundled `corpus/` directory next to `scripts/`, or
point `$AFPDS_CORPUS` at a corpus directory you built yourself.

**Rebuilding a corpus** from the AFPC publication PDFs means extracting their text
with `pdfminer.six` (`pip install --user pdfminer.six`). Do **not** substitute
`pypdf`: it drops inter-word spaces on several AFPC PDFs, which breaks phrase
search without any visible error.

**Page numbers.** Citations use the PDF page number — the `<<<PAGE n>>>` marker in
the corpus text. This is *not* the printed page number shown in the document
footer, and the two differ (for example MO:DCA's BOC syntax is PDF page 187 but
printed page 155). Always cite the PDF page, because that is what the search tool
reproduces.

**Rotated pages — when a table reads as scrambled columns.** Several MO:DCA syntax
tables are landscape pages whose text layer is emitted one character per line, so a
normal read interleaves the columns. Two ways out:

1. Re-join the single-character lines of that page into one string and read the
   columns in order. This recovered the full OBP field order and offsets.
2. If that is still ambiguous, read the page image. On macOS, no extra tooling is
   needed:
   ```bash
   qlmanage -t -s 1700 -o /tmp/ql page.pdf   # -> page.pdf.png
   ```

**The text layer and the page image have different authority — know which one to
trust.**

- The **text layer** is authoritative for *what words the page contains*. It is
  machine-extracted from the PDF, so it cannot invent a token.
- The **page image** is authoritative for *which column a value belongs to*, and is the
  only way to read a rotated landscape page.

A short token read off an image can easily be misread — a field named `TxtOrent` in
the specification was read as `TxtOrient` off an image and "corrected" in a draft. So:
**confirm every short token against the text layer before you change it.** If the two
disagree, the text layer wins on wording; only the column association needs the image.

Do not guess a value that the text layer cannot settle. Say which field is
unresolved and how to resolve it (which page image to read) — a wrong byte is worse
than an admitted gap.

## Output contract

For implementation work, the deliverable is code plus its provenance:

- The code itself — an encoder/parser/validator, not a prose description.
- Each non-obvious constant annotated with its source page, e.g.
  `# BOC = X'D3A892'  [mo-dca-reference-... p.187]`.
- A short **Unconfirmed / not found** list, when anything could not be settled from
  the corpus.
- When producing AFP bytes, say how they were validated (structure walk, parser
  round-trip, or external tool) — and say plainly when they were not. The bundled
  validator is the quickest of these:
  ```bash
  node scripts/verify-stream.mjs output.afp --tree
  ```
  Quote its verdict (PASS / FAIL) in the delivery.

For explanation work, the deliverable is the explanation with page citations, and
the same **Unconfirmed** list.

## Failure handling

- **Corpus missing or the search tool errors** — rebuild the corpus with the two
  commands above, then retry. Do not fall back to answering from memory.
- **The corpus does not contain what is needed** — say so. If the question is about
  the historical IBM AFP-1 publication, note that AFP Consortium does not publish
  it and it is outside this corpus (see `references/ecosystem.md`).
- **Two plausible readings of a structure** — present both with their pages and
  explain which the specification makes mandatory; do not silently pick one.
- **The request is about printing pipeline, driver, or PostScript/PDF conversion
  rather than the AFP architecture** — answer directly without this skill's
  machinery.

## Windows (win32) platform notes

Both tools are Node.js and run unchanged on Windows:

```powershell
node scripts\spec-search.mjs search "Begin Object Container" --doc modca
node scripts\spec-search.mjs page modca 187 188
node scripts\verify-stream.mjs output.afp --tree
```

Corpus rebuild needs Python. On Windows use `py` instead of `python3`, and install
the dependency with `py -m pip install --user pdfminer.six`.

## Examples

**Input**: "Write a Python function that emits the MO:DCA structure tree for a page
containing one image."

**Output**: a `structures.py` with a `StructuredField` dataclass (id bytes, length,
flags, payload) and the page's begin/end structures in order, every ID annotated
with its corpus page, plus the ordering constraints it depends on. The image
content itself is delegated to IOCA per `references/oca.md` rather than guessed at.
The emitted bytes are then run through `scripts/verify-stream.mjs` and its verdict
is quoted.

**Input**: "Our generated AFP prints blank on the printer."

**Output**: first run `scripts/verify-stream.mjs` on the file — a broken Length
is the single most common cause and it is decided mechanically. Then checks the
layer the failure is in — is the stream even reaching the printer (IPDS), is the
document envelope well-formed (MO:DCA), or is the page empty (OCA) — by walking
the structure tree against the ordering rules, before suggesting any fix.
