# AFPDS ecosystem and tooling — research findings

> Scope: **external** sources only. Everything here is tooling/ecosystem knowledge
> verified against live sources on 2026-10-29, with one deliberate exception noted
> inline: §4 reproduces MO:DCA structure type-IDs taken from a third-party EBNF file,
> and those byte values are independently corroborated against the corpus.
> For spec facts (byte values, structure semantics) see the corpus-cited
> findings documents `01`–`05`.
>
> Verification method: GitHub REST API (`api.github.com/repos/...`) and PyPI JSON API
> queried on 2026-10-29. Every row below reflects the API response, not memory.

## 1. Headline finding

**There is no mature, actively maintained AFP library for Python, JavaScript, or
Go.** The ecosystem is thin, mostly Java, mostly stale, and GPL-heavy. Practical
consequence for anyone building an AFPDS application today:

> Plan to **write your own parser/serializer**, using the AFPC corpus as the
> authoritative source of truth, and use the existing libraries mainly as
> *cross-reference material* for structure tables — not as runtime dependencies.

This is the single most important thing to know before starting, because the
instinct ("find an AFP library and use it") does not have a good answer.

## 2. Open-source AFP implementations

Verified via GitHub API on 2026-10-29.

| Repo | Language | Stars | Last push | License | What it is |
|---|---|---|---|---|---|
| [`yan74/afplib`](https://github.com/yan74/afplib) | Java | 45 | 2025-07-13 | Apache-2.0 | Library for **reading AND writing** AFP files. Eclipse/OSGi project. **Most complete option.** |
| [`afpdev/alpheusafpparser`](https://github.com/afpdev/alpheusafpparser) | Java | 22 | 2026-05-28 | GPL-3.0 | Library & parser for the AFP document/print stream format. **Most recently updated.** Parser-focused. |
| [`mdneale/afp`](https://github.com/mdneale/afp) | Python | 7 | 2018-10-24 | Apache-2.0 | Python package for **reading** AFP files. Only Python option. Unmaintained since 2018. |
| [`jpeeters-arch/AFP_pdf_to_afp`](https://github.com/jpeeters-arch/AFP_pdf_to_afp) | Java | 1 | 2025-01-31 | GPL-3.0 | PDF → AFP conversion scripts. Narrow scope. |
| [`Cenz/org.qxsched.doc.afp`](https://github.com/Cenz/org.qxsched.doc.afp) | Java | 3 | 2016-02-09 | GPL-3.0 | Library to read/write AFP data streams. Stale. |
| [`audreyt/parse-afp`](https://github.com/audreyt/parse-afp) | **Perl** | 5 | 2015-12-05 | none | AFP format parser. |
| [`afpdev/herculesafpeditor`](https://github.com/afpdev/herculesafpeditor) | Java | 5 | 2015-11-13 | GPL-3.0 | GUI editor for AFP files. Stale. |

**Correction worth recording:** `audreyt/parse-afp` is **Perl**, not Python. It is
easy to assume otherwise from the name. Verified: GitHub API reports
`language: Perl`.

## 3. Language coverage — the gap

| Language | Reading | Writing | Maintenance status |
|---|---|---|---|
| Java | yes (afplib, alpheus) | yes (afplib) | afplib 2025-07, alpheus 2026-05 |
| Python | yes (`mdneale/afp`, 2018) | **no** | unmaintained |
| Perl | yes (2015) | no | unmaintained |
| JavaScript / TypeScript | **no** | **no** | none found |
| Go / Rust | **no** | **no** | none found |

GitHub repository search for `afp advanced function presentation parser` (sorted by
updated) returned only `bone1966/readAFP` (an HTML/JS web app for inspecting AFP
files, ★1) and `afpdev/alpheusafpparser` — no meaningful JS/TS library exists.

PyPI check on 2026-10-29: `afp` exists (version 0.1, "Python package and utilities
for reading AFP files") — it is the `mdneale/afp` distribution. `pyafp`,
`afp-tools`, and `advanced-function-presentation` all return HTTP 404.

## 4. Machine-readable structure models (cross-reference material)

These are third-party, so they are **not** authoritative — but they are excellent
for cross-checking a table derived from the corpus, and for seeing how an
independent implementer modelled the same bytes.

Fetched into `research/external/`:

| File | Source | Size | Why it matters |
|---|---|---|---|
| `alpheus-structure.ebnf` | `afpdev/alpheusafpparser` → `ebnf_docs/structure.ebnf` | 6.8 KB | EBNF grammar of MO:DCA document structure, **including the 3-byte structure type IDs** |
| `alpheus-AFP_META_STRUCTURE.md` | `afpdev/alpheusafpparser` → `specifications/AFP_META_STRUCTURE.md` | 6.4 KB | Meta-structure of the AFP stream |
| `alpheus-GLOSSARY.md` | `afpdev/alpheusafpparser` → `GLOSSARY.md` | 23 KB | Terminology glossary |
| `afplib-afpStructure.ecore` | `yan74/afplib` → `org.afplib.generator/src/metamodel/afpStructure.ecore` | 11.5 KB | **Eclipse Ecore metamodel** of AFP structures — machine-readable, 26 EClasses |
| `afplib-README.md` | `yan74/afplib` → `README.md` | 5.4 KB | Library usage |

Note: `afplib` also ships a 482 KB `afplib.ecore` (the full AFP metamodel, as
opposed to the 11.5 KB structural subset). It was not fetched here due to size;
pull it on demand.

### The MO:DCA 3-byte type-ID pattern (from `alpheus-structure.ebnf`)

The EBNF encodes MO:DCA structure type IDs as three bytes. The observed pattern
is `X'D3'`, then `X'A8'` for **Begin**-type structures and `X'A9'` for **End**-type
structures, then a family byte. Example values present in that file:

```
BPF_ID = X'D3', X'A8', X'A5'      BRG_ID = X'D3', X'A8', X'C6'
EPF_ID = X'D3', X'A9', X'A5'      ERG_ID = X'D3', X'A9', X'C6'
BDI_ID = X'D3', X'A8', X'A7'      BNG_ID = X'D3', X'A8', X'AD'
EDI_ID = X'D3', X'A9', X'A7'      ENG_ID = X'D3', X'A9', X'AD'
BDT_ID = X'D3', X'A8', X'A8'      BPG_ID = X'D3', X'A8', X'AF'
EDT_ID = X'D3', X'A9', X'A8'      EPG_ID = X'D3', X'A9', X'AF'
BAG_ID = X'D3', X'A8', X'C9'      BSG_ID = X'D3', X'A8', X'D9'
EAG_ID = X'D3', X'A9', X'C9'      ESG_ID = X'D3', X'A9', X'D9'
BOG_ID = X'D3', X'A8', X'C7'      BIM_ID = X'D3', X'A8', X'FB'
EOG_ID = X'D3', X'A9', X'C7'      EIM_ID = X'D3', X'A9', X'FB'
BMM_ID = X'D3', X'A8', X'CC'      BOC_ID = X'D3', X'A8', X'92'
EMM_ID = X'D3', X'A9', X'CC'      EOC_ID = X'D3', X'A9', X'92'
```

**These are third-party values.** Every one of them must be re-verified against the
corpus (MO:DCA Reference) before being used as fact in the Skill. The corpus is the
authority; this file is the cross-check.

## 5. Commercial / free tools listed by AFPC

Source: https://www.afpconsortium.org/freeafptools.html (retrieved 2026-10-29).

| Tool | URL | Notes |
|---|---|---|
| AFP Viewer | https://www.isis-papyrus.com/e15/pages/software/afp-viewer.html | ISIS Papyrus (Kyocera). Viewing + validation. |
| AFP Explorer | https://www.compulsivecode.com/Project_AFPexplorer.aspx | Structure-level AFP viewer (Compulsive Code). |
| PrintBuilder | https://www.compulsivecode.com/Project_PrintBuilder.aspx | AFP construction/authoring tool. |
| M-View for AFP | https://kwsoft.com/series-m/omnichannel-output-management-with-m-oms/m-view-for-afp/ | Konica Minolta. |
| FOP Designer | https://www.java4less.com/fopdesigner/fodesigner.php | |
| Apache FOP | https://xmlgraphics.apache.org/fop/ | Listed under output formats; Java rendering engine. |
| Ricoh AFPC drivers | https://dl.ricohsoftware.com/no_charge_request | Printer drivers from AFPC. |

## 6. Community / human sources

- **AFP Forum** — moderated community platform sponsored by the AFP Consortium, for
  technical questions about AFP with answers from knowledgeable users. Linked from
  https://www.afpconsortium.org/faq.html (the FAQ's "How do I get answers to
  technical questions about AFP?" entry).
  Note the AFPC disclaimer that ideas and information exchanged there are
  independent of the AFPC.
- **AFPC meeting recaps** (`https://www.afpconsortium.org/in-the-news.html`) publish
  what the consortium is actively working on — e.g. IPDS security (TLS 1.3
  recommendation), a new page-placement option, and non-ASCII job names. Useful as a
  signal of where the specs are heading, but not normative.

## 7. Practical guidance derived from this research

1. **Do not plan around a library dependency.** Write the parser/serializer against
   the corpus. Java `afplib` is the only library that both reads and writes and is
   maintained enough to consider; if the target language is not Java, budget for
   writing it.
2. **Cross-check every byte value against the corpus**, using the third-party
   EBNF/Ecore models only to catch mistakes — never as the source of truth.
3. **Validate output with a real tool** (AFP Explorer / AFP Viewer) before
   believing it. These are the practical oracle for "is my stream actually valid".
4. **Watch licence contamination.** `alpheusafpparser`, `herculesafpeditor`,
   `Cenz/org.qxsched.doc.afp`, and `AFP_pdf_to_afp` are **GPL-3.0**. `afplib` and
   `mdneale/afp` are **Apache-2.0**. If the deliverable is closed-source, GPL
   libraries can only be used as a reference, not linked.
5. **Use the AFPC forum** when the corpus is silent on an implementation question —
   but treat forum answers as informal, and record them as such.

## 8. Not found / open questions

- No AFP library exists for JavaScript/TypeScript, Go, or Rust (searched GitHub +
  PyPI on 2026-10-29). If the target stack is JS, a from-scratch implementation is
  implied.
- No maintained Python *writer* was found. Writing AFP from Python means writing
  the serializer yourself.
- The corpus does not contain **AFP-1** (the historical IBM "Print Stream Format"
  publication) — AFPC does not publish it. Modern development works from the AFPC
  standards, which are fully covered here.
- The exact upstream URL for the AFPC Forum could not be extracted from the FAQ page
  (it is rendered as a link whose target was not captured in the text extraction).
  It is linked from the FAQ page directly.

## 9. Citation index

All accessed 2026-10-29:

- https://www.afpconsortium.org/publications.html
- https://www.afpconsortium.org/freeafptools.html
- https://www.afpconsortium.org/faq.html
- https://api.github.com/repos/yan74/afplib
- https://api.github.com/repos/afpdev/alpheusafpparser
- https://api.github.com/repos/mdneale/afp
- https://api.github.com/repos/jpeeters-arch/AFP_pdf_to_afp
- https://api.github.com/repos/Cenz/org.qxsched.doc.afp
- https://api.github.com/repos/audreyt/parse-afp
- https://api.github.com/repos/afpdev/herculesafpeditor
- https://api.github.com/search/repositories?q=afp+advanced+function+presentation+parser
- https://pypi.org/pypi/afp/json
- https://raw.githubusercontent.com/afpdev/alpheusafpparser/master/ebnf_docs/structure.ebnf
- https://raw.githubusercontent.com/afpdev/alpheusafpparser/master/specifications/AFP_META_STRUCTURE.md
- https://raw.githubusercontent.com/afpdev/alpheusafpparser/master/GLOSSARY.md
- https://raw.githubusercontent.com/yan74/afplib/master/org.afplib.generator/src/metamodel/afpStructure.ecore
- https://raw.githubusercontent.com/yan74/afplib/master/README.md
