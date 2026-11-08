# Codex runtime guidance

## Package routing

Use the installed files below, even when an older global skill has the same name. A sibling skill handoff means reading its file with the available file tool. It does not require MiniMax's `skill` tool or a separate agent.

| Request | Bundled skill |
| --- | --- |
| AFP structure, MO:DCA / IPDS / OCA spec facts, generating or validating a data stream | [afpds-expert](skills/afpds-expert/SKILL.md) |
| Turning an AFP page into a PNG picture | [afp-renderer](skills/afp-renderer/SKILL.md) |

Resolve each skill's `references/`, `scripts/` and `corpus/` relative to that skill directory. Keep generated output in the user's workspace, outside the installed plugin.

## The corpus is the authority

`skills/afpds-expert/corpus/` ships with this package: 32 plain-text files (one per AFP Consortium publication) plus `index.json`, with pages delimited by `<<<PAGE n>>>` markers. It is the text of record for every byte value, structure identifier and ordering rule.

Never state a hex value, a structure ID or an ordering constraint from memory — read the page and cite it as `[<doc-slug> p.N]`, where `N` is the **PDF** page number (the `<<<PAGE n>>>` marker), not the printed page number in the document footer. If the corpus does not settle a question, say so explicitly and report what you did find instead of substituting a plausible-looking value.

```bash
node skills/afpds-expert/scripts/spec-search.mjs docs
node skills/afpds-expert/scripts/spec-search.mjs search "Begin Object Container" --doc modca -n 5 -C 2
node skills/afpds-expert/scripts/spec-search.mjs page modca 187 188
```

The tool resolves `$AFPDS_CORPUS` first, then the bundled `corpus/` directory. If neither is present, restore the bundled directory rather than answering from memory.

Two cautions the skills already document: the extracted text layer is authoritative for *which words a page contains* but interleaves multi-column tables, so a value's column association may need the page image; and a verifier's finding — or its confirmation — is a hypothesis to re-derive from the corpus before anything is changed.

## Runtime dependencies

- **Node.js** for the three bundled `.mjs` scripts (corpus search, stream-structure validator, the MO:DCA structure table). No install step, no dependencies.
- **Python 3.11+** with `Pillow` and `numpy` for the renderer under `skills/afp-renderer/scripts/afp_render/`. Check the import first and install into the user's environment (`python3 -m pip install --user Pillow numpy`) instead of rewriting the renderer to avoid them.

Render with an explicit script path and an output path in the user's workspace:

```bash
python3 skills/afp-renderer/scripts/afp_render/render.py <file.afp> \
    --resources <dir> --page 1 --dpi 300 --out page1.png
```

The renderer needs the resource directory — FOCA font files plus the MO:DCA external resource file (`*.res`) that carries the page overlays and segments. Without the `.res` the page renders with its own text and graphics but no overlay and no barcode; say that plainly instead of delivering a half-empty picture as if it were the document.

## Evidence and honesty

Quote the validator's verdict rather than implying success: `node skills/afpds-expert/scripts/verify-stream.mjs output.afp --tree` exits 0 when the structured-field chain is consistent and 1 otherwise. It checks **structure, not semantics** — a stream can pass and still be semantically wrong.

Do not claim a render is "identical to what the printer produces". The renderer was checked against the specifications and for internal consistency, not against a physical print. Read the produced PNG back before claiming success: text upside down or mirrored, tofu boxes instead of glyphs, a stretched image, missing content and content drawn twice are all failures that a file on disk does not reveal.

This is a skills package. It supplies no MCP server, printer driver, print-queue access or credentials. If the task needs to reach a real device or a print system, finish the local artifacts and give an exact handoff instead of claiming the job was sent.

## Scope

This package covers the AFP architecture itself — IPDS transport framing, MO:DCA document structure, the OCA content architectures, AFP fonts, code pages and character data. It is not a PDF or PostScript converter, not a printer driver, and it contains no document-generation library. Requests about generic print pipelines are answered directly without this machinery.

The historical IBM AFP-1 publication is outside the corpus: the AFP Consortium does not publish it. If a question genuinely needs AFP-1 history, source it separately and label it as an external source with its own citation — do not fold it into a corpus citation.
