# MO:DCA — document architecture (distilled reference)

Source: MO:DCA Reference, AFPC-0004-11 (772 pages). All page numbers are **PDF page**
numbers (the corpus `<<<PAGE n>>>` marker), not the printed page in the footer — for
this document PDF page = printed page + 32.

Citation slug used below: `mo-dca-reference-mixed-object-document-content-architecture-reference`.

Page pointers marked **✔** were read directly during research. Unmarked pages in the
identifier table are derived from the specification's own table of contents
(`p.13–p.28`) plus the +32 offset — the identifiers themselves are directly read;
the page pointer is computed. Re-verify with the search tool before citing.

## 1. What MO:DCA owns

The **document-architecture** layer: the component hierarchy, the environment each
component renders in, the mapping of resources to local IDs, print control, and the
container mechanism that carries non-AFP payloads.

It does **not** own the bytes inside a presentation object — that is the OCAs'
job. MO:DCA supplies the envelope (begin/end structured fields, OEG, data
structured field); the OCA supplies the content. `[mo-dca-reference-mixed-object-document-content-architecture-reference p.533]`

Transport is deliberately decoupled: "The MO:DCA architecture does not dictate the
physical format of the data stream or how it is transported." A stream may be one
continuous byte string or broken into fixed/variable-length records; "The receiver
must be capable of receiving the data stream and parsing or processing it
sequentially from start to finish." `[mo-dca-reference-mixed-object-document-content-architecture-reference p.57]`

## 2. Layer stack

```
Print File            BPF … EPF                    X'D3A8A5' / X'D3A9A5'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.114]
  └─ Resource Group   BRG … ERG                    X'D3A8C6' / X'D3A9C6'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.126]
  └─ Document         BDT … EDT                    X'D3A8A8' / X'D3A9A8'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.115, p.170]
       ├─ REG          BSG … ESG                    X'D3A8D9' / X'D3A9D9'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.117]
       ├─ Medium Map   BMM … EMM                    X'D3A8CC' / X'D3A9CC'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.134]
       ├─ Page Group   BNG … ENG                    X'D3A8AD' / X'D3A9AD'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.120]
       └─ Page         BPG … EPG                    X'D3A8AF' / X'D3A9AF'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.118, p.196]
            ├─ AEG      BAG … EAG                  X'D3A8C9' / X'D3A9C9'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.118, p.162]
            └─ Data Object  BGR/EGR, BIM/EIM, BPT/EPT, BBC/EBC
                            each optionally wrapped in its own OEG
                            BOG … EOG                  X'D3A8C7' / X'D3A9C7'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.155]
                            + Data-class SF: GAD X'D3EEBB', IPD X'D3EEFB',
                              PTX X'D3EE9B', BDA X'D3EEEB', OCD X'D3EE92'
            └─ Object Container  BOC … EOC          X'D3A892' / X'D3A992'   [mo-dca-reference-mixed-object-document-content-architecture-reference p.155, p.187, p.230]
```

**State** is the formalisation of this stack: a domain bounded by a begin-end pair
within which only certain structured fields are permitted. A processor must check
that every structured field belongs to the permitted set of its enclosing envelope,
and "is required to raise an exception condition" otherwise.
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.58]`

## 3. The Structured Field Introducer (SFI)

Every MO:DCA structured field starts with the same 5-byte introducer.

| Offset | Type | Name | Range | Meaning |
|---|---|---|---|---|
| 0–1 | UBIN | SFLength | 8–32,767 | Total length of the structured field **including the length of the introducer** |
| 2–4 | CODE | SFTypeID | — | Three-byte code `D3TTCC` (class / type / category) |
| 5 | BITS | FlagByte | — | Bit 0 ExtFlag, bit 2 SegFlag, bit 4 PadFlag; bits 1, 3, 5–7 reserved (zero) |

`[mo-dca-reference-mixed-object-document-content-architecture-reference p.52]`

Flag semantics `[mo-dca-reference-mixed-object-document-content-architecture-reference p.53]`:

| Bit | Name | B'1' means |
|---|---|---|
| 0 | ExtFlag | SFI extension present (adds `ExtLength` 1–255 + up to 254 bytes `ExtData`; introducer becomes 8–263 bytes) |
| 2 | SegFlag | data segmented into consecutive SFs forming one uninterrupted parameter string; the **last** fragment must have SegFlag = B'0' |
| 4 | PadFlag | padding appended; length in the last byte (1–2 bytes) or last three bytes (256–32,759 bytes, last byte X'00') |

Bytes 6–7 are reserved; "some applications use bytes 6–7 … to specify a sequence
number… This is an unarchitected use of these bytes and should be avoided."
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.54]`

### SFTypeID = `D3TTCC`

- **D3** — structured field class code assigned to the MO:DCA architecture
- **TT** — type code (function: begin, end, descriptor, data…)
- **CC** — category code (lowest-level component constructible; the same code is
  used on that component's begin **and** end structured field)

`[mo-dca-reference-mixed-object-document-content-architecture-reference p.53]`

**Type codes** — all 15 defined codes `[mo-dca-reference-mixed-object-document-content-architecture-reference p.54, p.55]`:
X'A0' Attribute · X'A2' Copy Count · X'A6' Descriptor · X'A7' Control ·
X'A8' Begin · X'A9' End · X'AB' Map · X'AC' Position · X'AD' Process ·
X'AF' Include · X'B0' Reserved · X'B1' Migration · X'B2' Variable ·
X'B4' Link · X'EE' Data.

> **X'A8' = Begin, X'A9' = End** — these two are the type byte of *every* begin/end
> structured field. For example BOC `X'D3A892'` = `D3` (class) + `A8` (Begin) +
> `92` (Object Container category). A decoder that recognises only a subset of the
> type codes above will reject legal MO:DCA structures.

**Category codes** `[mo-dca-reference-mixed-object-document-content-architecture-reference p.55]`:
X'5F' Page Segment · X'6B' Object Area · X'77' Reserved (see MO:DCA-L) ·
X'7B' IM Image · X'88' Medium · X'8A' Coded Font · X'90' Process Element ·
X'92' Object Container · X'9B' Presentation Text · X'A5' Print File ·
X'A7' Document Index · X'A8' Document · X'AD' Page Group · X'AF' Page ·
X'BB' Graphics · X'C3' Data Resource · X'C4' Document Environment Group ·
X'C6' Resource Group · X'C7' Object Environment Group · X'C9' Active Environment Group ·
X'CC' Medium Map · X'CD' Form Map · X'CE' Name Resource · X'D8' Page Overlay ·
X'D9' Resource Environment Group · X'DC' Preprinted Form Overlay · X'DF' Overlay ·
X'EA' Data Suppression · X'EB' Bar Code · X'EE' No Operation · X'FB' Image.

"The following type codes have been defined. All other type codes are reserved."
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.54]` ·
"The following category codes have been defined. All other category codes are
reserved." `[mo-dca-reference-mixed-object-document-content-architecture-reference p.55]`

## 3.1 OBP — Object Area Position (X'D3AC6B')

**Verified against the page image** (the syntax pages PDF p.347–348 are rotated
landscape pages; the text layer scrambles the columns, so this table was read from the
rendered page). Printed page 315–316.

| Offset | Type | Name | Range | Meaning | M/O | Exc |
|---|---|---|---|---|---|---|
| 0 | CODE | `OAPosID` | X'01'–X'7F' | the object area position identifier; used to associate this OBP with the Object Area Descriptor | M | X'06' |
| 1 | UBIN | `RGLength` | 23 | total length of the repeating group, **including the length of the RGLength parameter itself** | M | X'06' |
| 2–4 | SBIN | `XoaOset` | -32,768–32,767 | X-axis origin of the object area | M | X'06' |
| 5–7 | SBIN | `YoaOset` | -32,768–32,767 | Y-axis origin of the object area | M | X'06' |
| 8–9 | CODE | `XoaOrent` | — | object area's X-axis rotation from the X axis of the reference coordinate system | M | X'06' |
| 10–11 | CODE | `YoaOrent` | — | object area's Y-axis rotation from the X axis of the reference coordinate system | M | X'06' |
| 12 | — | — | — | Reserved; should be zero | M | X'06' |
| 13–15 | SBIN | `XocaOset` | -32,768–32,767 | X-axis origin for object content | M | X'06' |
| 16–18 | SBIN | `YocaOset` | -32,768–32,767 | Y-axis origin for object content | M | X'06' |
| 19–20 | CODE | `XocaOrent` | X'0000' | object content's X-axis rotation from the X axis of the object area coordinate system | M | X'06' |
| 21–22 | CODE | `YocaOrent` | X'2D00' | object content's Y-axis rotation from the X axis of the object area coordinate system | M | X'06' |
| 23 | CODE | `RefCSys` | X'00', X'01', X'05' | reference coordinate system (see below) | M | X'06' |

`[mo-dca-reference-mixed-object-document-content-architecture-reference p.347, p.348]`

> **Decode the orientation fields like this** — the bit labels in the specification's
> sub-table are printed as "Bits 0–8 Degrees, Bits 9–14 Minutes, Bit 15 Reserved", but
> that numbering only works if you count from the **most** significant end. Copying the
> labels literally and decoding LSB-first silently produces the wrong angle:
>
> ```python
> def decode_orient(value: int) -> tuple[int, int]:
>     """OBP XoaOrent / YoaOrent / XocaOrent / YcaOrent -> (degrees, minutes)."""
>     degrees = (value >> 7) & 0x1FF        # bits 0-8, counted from the MSB
>     minutes = (value >> 1) & 0x3F         # bits 9-14, counted from the MSB
>     return degrees, minutes               # bit 15 is reserved (0)
>
> decode_orient(0x0000)  # -> (0, 0)
> decode_orient(0x2D00)  # -> (90, 0)
> decode_orient(0x5A00)  # -> (180, 0)
> decode_orient(0x8700)  # -> (270, 0)
> ```
>
> The four "frequently used values" the specification prints next to the field
> (`X'0000'` = 0°, `X'2D00'` = 90°, `X'5A00'` = 180°, `X'8700'` = 270°) only reproduce
> with the MSB reading — use them as your regression test.

### Two traps in this structure

**Trap 1 — the specification's own table is internally inconsistent about `RGLength`.**
The Type column says `UBIN` (2 bytes) but the Offset column puts the next field at
offset 2, so `RGLength` occupies **one** byte there. Every other field's declared type
matches its offset span exactly (SBIN = 3 bytes at 2–4, 5–7, 13–15, 16–18; CODE =
2 bytes at 8–9, 10–11, 19–20, 21–22; CODE = 1 byte at 23; offset 12 is a 1-byte
reserved field) — `RGLength` is the **only** mismatch.
The offsets 2–23 are contiguous and occupy **22 bytes**, so the whole repeating group
(offset 1–23) is **23 bytes** with `RGLength` taking 1 of them — exactly the value the
table gives for `RGLength`, and exactly what p.348 means by "Specifies the total length
of the repeating group, including the length of the RGLength parameter itself".
General MO:DCA says the RGLength value "always includes the length of the RGLength
parameter itself, which is **usually two bytes**"
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.61]` — "usually",
not "always", and here the offsets say one byte.
**Practical consequence: follow the offset column** — emit `RGLength` as a **1-byte**
value of **23**, and the group as 23 bytes. The alternative reading (2-byte UBIN, 24-byte
group) contradicts the table's own `23` and its offset column; if you have to support a
receiver that reads it that way, validate against a working implementation before
shipping.
This is the one place in the OBP where the reference cannot be resolved from the
document alone; there is no second source in the corpus.
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.347, p.348]`

**Trap 2 — the orientation bit table counts bits from the MSB.**
The sub-table reads "Bits 0–8 Degrees, Bits 9–14 Minutes, Bit 15 Reserved"
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.347, p.348]` (read from
the rendered page image — those pages are rotated landscape and the text layer
scrambles them). Read from the **LSB** those offsets do not reproduce the four
"frequently used values" the same table prints. Read from the **MSB** they do:

| Value | Degrees | Minutes | Check |
|---|---|---|---|
| X'0000' | 0 | 0 | 0 degrees |
| X'2D00' | 90 | 0 | 0b001011010 = 90 |
| X'5A00' | 180 | 0 | 0b010110100 = 180 |
| X'8700' | 270 | 0 | 0b100001011 = 270 |

Arithmetic that reproduces all four:

```
degrees = (value >> 7) & 0x1FF     # 9 bits, 0-359
minutes = (value >> 1) & 0x3F      # 6 bits, 0-59
bit 0 (LSB) reserved = 0
```

Note this is the **opposite** of the usual IBM convention in which bit 1 is the least
significant. Do not decode these fields with an LSB-first helper.

### Reference coordinate system (`RefCSys`, offset 23)

`[mo-dca-reference-mixed-object-document-content-architecture-reference p.348]`

| Value | Meaning |
|---|---|
| X'00' | Page or overlay coordinate system; origin is defined by the IPS structured field |
| X'01' | Page or overlay coordinate system; standard origin |
| X'05' | Retired value |

### Semantics worth knowing

- `XoaOset` / `YoaOset` are the offset along the X/Y axis of the **referenced**
  coordinate system (`X_pg` or `X_ol`) to the origin of the object area coordinate
  system, in the referenced system's measurement units.
- `YoaOrent` **must be 90 degrees greater** than `XoaOrent`, or exception condition
  **X'01'** exists.
- If the object area origin offset plus the object area extent exceeds the including
  presentation space in X or Y, the object area does not fit: data falling outside is
  **not presented**, and exception condition **X'01'** exists.
- `OAPosID` must be **unique within the environment group**.

`[mo-dca-reference-mixed-object-document-content-architecture-reference p.349]`

## 4. Structure identifier table

All 98 MO:DCA structured fields, rebuilt mechanically from the MO:DCA Reference
table of contents and cross-checked against Appendix E "Cross-References", whose
tables include "Table 53 Structured Fields Sorted by ID"
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.695, p.696]`,
by `tools/build_modca_table.py`. Every row was verified: the cited PDF page
contains that structure's own `ACR (X'HEX') Syntax` line. PDF page = printed page + 32
for this document.

| Identifier | Acronym | Structured Field Name | Printed p. | PDF p. |
|---|---|---|---|---|
| X'D3A088' | MFC | Medium Finishing Control | 279 | 311 |
| X'D3A090' | TLE | Tag Logical Element | 356 | 388 |
| X'D3A288' | MCC | Medium Copy Count | 246 | 278 |
| X'D3A66B' | OBD | Object Area Descriptor | 313 | 345 |
| X'D3A67B' | IID | IM Image Input Descriptor | 631 | 663 |
| X'D3A688' | MDD | Medium Descriptor | 257 | 289 |
| X'D3A692' | CDD | Container Data Descriptor | 183 | 215 |
| X'D3A69B' | PTD-1 | Presentation Text Data Descriptor Format 1 | 628 | 660 |
| X'D3A6AF' | PGD | Page Descriptor | 323 | 355 |
| X'D3A6BB' | GDD | Graphics Data Descriptor | 208 | 240 |
| X'D3A6C5' | FGD | Form Environment Group Descriptor | 583 | 615 |
| X'D3A6EB' | BDD | Bar Code Data Descriptor | 134 | 166 |
| X'D3A6FB' | IDD | Image Data Descriptor | 209 | 241 |
| X'D3A77B' | IOC | IM Image Output Control | 633 | 665 |
| X'D3A788' | MMC | Medium Modification Control | 289 | 321 |
| X'D3A79B' | CTC | Composed Text Control | 582 | 614 |
| X'D3A7A8' | PEC | Presentation Environment Control | 319 | 351 |
| X'D3A7AF' | PMC | Page Modification Control | 341 | 373 |
| X'D3A85F' | BPS | Begin Page Segment | 167 | 199 |
| X'D3A87B' | BII | Begin IM Image Object | 629 | 661 |
| X'D3A892' | BOC | Begin Object Container | 155 | 187 |
| X'D3A89B' | BPT | Begin Presentation Text Object | 169 | 201 |
| X'D3A8A5' | BPF | Begin Print File | 161 | 193 |
| X'D3A8A7' | BDI | Begin Document Index | 136 | 168 |
| X'D3A8A8' | BDT | Begin Document | 138 | 170 |
| X'D3A8AD' | BNG | Begin Named Page Group | 151 | 183 |
| X'D3A8AF' | BPG | Begin Page | 164 | 196 |
| X'D3A8BB' | BGR | Begin Graphics Object | 143 | 175 |
| X'D3A8C4' | BDG | Begin Document Environment Group | 135 | 167 |
| X'D3A8C5' | BFG | Begin Form Environment Group | 582 | 614 |
| X'D3A8C6' | BRG | Begin Resource Group | 172 | 204 |
| X'D3A8C7' | BOG | Begin Object Environment Group | 160 | 192 |
| X'D3A8C9' | BAG | Begin Active Environment Group | 130 | 162 |
| X'D3A8CC' | BMM | Begin Medium Map | 147 | 179 |
| X'D3A8CD' | BFM | Begin Form Map | 141 | 173 |
| X'D3A8CE' | BRS | Begin Resource | 174 | 206 |
| X'D3A8D9' | BSG | Begin Resource Environment Group | 182 | 214 |
| X'D3A8DF' | BMO | Begin Overlay | 149 | 181 |
| X'D3A8EB' | BBC | Begin Bar Code Object | 131 | 163 |
| X'D3A8FB' | BIM | Begin Image Object | 145 | 177 |
| X'D3A95F' | EPS | End Page Segment | 202 | 234 |
| X'D3A97B' | EII | End IM Image Object | 630 | 662 |
| X'D3A992' | EOC | End Object Container | 198 | 230 |
| X'D3A99B' | EPT | End Presentation Text Object | 203 | 235 |
| X'D3A9A5' | EPF | End Print File | 200 | 232 |
| X'D3A9A7' | EDI | End Document Index | 189 | 221 |
| X'D3A9A8' | EDT | End Document | 190 | 222 |
| X'D3A9AD' | ENG | End Named Page Group | 196 | 228 |
| X'D3A9AF' | EPG | End Page | 201 | 233 |
| X'D3A9BB' | EGR | End Graphics Object | 192 | 224 |
| X'D3A9C4' | EDG | End Document Environment Group | 188 | 220 |
| X'D3A9C5' | EFG | End Form Environment Group | 583 | 615 |
| X'D3A9C6' | ERG | End Resource Group | 204 | 236 |
| X'D3A9C7' | EOG | End Object Environment Group | 199 | 231 |
| X'D3A9C9' | EAG | End Active Environment Group | 186 | 218 |
| X'D3A9CC' | EMM | End Medium Map | 194 | 226 |
| X'D3A9CD' | EFM | End Form Map | 191 | 223 |
| X'D3A9CE' | ERS | End Resource | 205 | 237 |
| X'D3A9D9' | ESG | End Resource Environment Group | 206 | 238 |
| X'D3A9DF' | EMO | End Overlay | 195 | 227 |
| X'D3A9EB' | EBC | End Bar Code Object | 187 | 219 |
| X'D3A9FB' | EIM | End Image Object | 193 | 225 |
| X'D3AB88' | MMT | Map Media Type | 302 | 334 |
| X'D3AB8A' | MCF | Map Coded Font Format 2 | 250 | 282 |
| X'D3AB92' | MCD | Map Container Data | 248 | 280 |
| X'D3AB9B' | MPT | Map Presentation Text | 310 | 342 |
| X'D3ABAF' | MPG | Map Page | 305 | 337 |
| X'D3ABBB' | MGO | Map Graphics Object | 286 | 318 |
| X'D3ABC3' | MDR | Map Data Resource | 259 | 291 |
| X'D3ABCC' | IMM | Invoke Medium Map | 212 | 244 |
| X'D3ABCD' | MMD | Map Media Destination | 299 | 331 |
| X'D3ABD8' | MPO | Map Page Overlay | 307 | 339 |
| X'D3ABEA' | MSU | Map Suppression | 311 | 343 |
| X'D3ABEB' | MBC | Map Bar Code Object | 245 | 277 |
| X'D3ABFB' | MIO | Map Image Object | 287 | 319 |
| X'D3AC6B' | OBP | Object Area Position | 315 | 347 |
| X'D3AC7B' | ICP | IM Image Cell Position | 630 | 662 |
| X'D3ACAF' | PGP-1 | Page Position Format 1 | 628 | 660 |
| X'D3ADC3' | PPO | Preprocess Presentation Object | 343 | 375 |
| X'D3AF5F' | IPS | Include Page Segment | 237 | 269 |
| X'D3AFAF' | IPG | Include Page | 232 | 264 |
| X'D3AFC3' | IOB | Include Object | 214 | 246 |
| X'D3AFD8' | IPO | Include Page Overlay | 235 | 267 |
| X'D3B15F' | MPS | Map Page Segment | 309 | 341 |
| X'D3B18A' | MCF-1 | Map Coded Font Format 1 | 626 | 658 |
| X'D3B19B' | PTD | Presentation Text Data Descriptor Format 2 | 354 | 386 |
| X'D3B1AF' | PGP | Page Position Format 2 | 326 | 358 |
| X'D3B1DF' | MMO | Map Medium Overlay | 301 | 333 |
| X'D3B288' | PFC | Presentation Fidelity Control | 321 | 353 |
| X'D3B2A7' | IEL | Index Element | 210 | 242 |
| X'D3B490' | LLE | Link Logical Element | 239 | 271 |
| X'D3EE7B' | IRD | IM Image Raster Data | 635 | 667 |
| X'D3EE92' | OCD | Object Container Data | 318 | 350 |
| X'D3EE9B' | PTX | Presentation Text Data | 355 | 387 |
| X'D3EEBB' | GAD | Graphics Data | 207 | 239 |
| X'D3EEEB' | BDA | Bar Code Data | 133 | 165 |
| X'D3EEEE' | NOP | No Operation | 312 | 344 |
| X'D3EEFB' | IPD | Image Picture Data | 231 | 263 |

**Obsolete / alternate names** — Appendix C lists the pre-rename names of the *same*
identifiers. These are aliases, not conflicts: MO:DCA p.616 states "This structured
field has been renamed Presentation Text Data (PTX)."

| Identifier | Current name | Obsolete name |
|---|---|---|
| X'D3A69B' | Presentation Text Data Descriptor Format 1 | Composed Text Descriptor |
| X'D3A89B' | Begin Presentation Text Object | Begin Composed Text |
| X'D3A99B' | End Presentation Text Object | End Composed Text |
| X'D3EE9B' | Presentation Text Data | Composed Text Data |

> Appendix C lists **exactly four** renames (CTX, CTD, BCT, ECT).
> `[mo-dca-reference-mixed-object-document-content-architecture-reference p.616]`
> `End Print File` (`X'D3A9A5'`) is **not** a rename — an earlier version of this file
> listed an obsolete name "File" for it, which is an artefact of the PDF text layer
> breaking `End Print File (EPF) X'D3A9A5'` across two lines on p.551, not a name in
> the specification.
> Appendix C writes the new names without the word "Object" ("Begin Presentation
> Text", "End Presentation Text"); the corpus uses "Begin Presentation Text Object"
> / "End Presentation Text Object" everywhere else (e.g. p.15, p.24, p.27).

## 5. Exception conditions

The backbone of every validity rule, at every nesting level.
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.113]`

| Code | Meaning |
|---|---|
| **X'40'** | "If a structured field that is not identified as being part of the object appears anywhere within the object, a X'40' exception condition exists." |
| **X'20'** | "If a structured field appears out of the stated order or more than the permitted number of times, a X'20' exception condition exists." |
| **X'08'** | "If a structured field that is identified as required does not appear within the object, a X'08' exception condition exists." |

Other confirmed codes:

| Code | Meaning | Source |
|---|---|---|
| X'01' | Present data outside the presentation space / object area; OBP `YoaOrent` not 90° greater than `XoaOrent` | p.349 |
| X'02' | Invalid parameter value (e.g. `AEGName` present when not permitted) | p.162, p.157 |
| X'06' | Parameter outside its permitted range | p.289, p.187 |
| X'08' | Required structured field missing / unmatched begin | p.162, p.187 |
| X'10' | Invalid triplet, or required triplet missing | p.161 |
| X'14' | Invalid triplet | p.161, p.282 |
| X'20' | Out-of-order or over-repetition | p.113 |
| X'40' | Unrecognised structured field in this object | p.113 |
| X'00' | (OCD) — no other detail given | p.350 |

## 6. Ordering notation

`[mo-dca-reference-mixed-object-document-content-architecture-reference p.113]`

- `( )` — the structured field acronym and identifier
- `D3..C9` — dots mean the item is not a structured field but a **structure**. MO:DCA
  wording: "The presence of dots or periods in the identifier indicates that the item is
  not a structured field, but instead is a structure, for example a medium map. The
  structure is composed of an assortment of structured fields, and is defined
  separately." `[mo-dca-reference-mixed-object-document-content-architecture-reference p.113]`
- `[ ]` — optional; without brackets the field **must** appear between the begin and end
- `+` — fields may appear in any order relative to those marked `+`; unmarked
  neighbours keep the listed order
- `(S)` — may be repeated; if `(S)` is on a required field, at least one occurrence
  is required
- `F2` — format-two structured field

**No Operation may appear anywhere**: "The No Operation structured field may appear
within any begin-end domain. Therefore, it is not listed in the structured field
groupings." `[mo-dca-reference-mixed-object-document-content-architecture-reference p.113]`

**Processing order**: "Unless otherwise specified … all structured fields are
processed in the order in which they appear in the data stream." A page with text
object, IPO, graphic, second IPO, image presents them in exactly that order.
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.59]`

## 7. Length rules (high trap area)

- SFLength "Defines the length of the structured field, **including itself**."
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.53]`
- Max SF length 32,767; max data payload 32,759 (32,767 − 8).
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.52, p.56]`
- Strongly recommended max **X'7FF0' = 32,752** — some platforms wrap a structured
  field in a larger record (e.g. an X'5A' prefix), and a length of X'7FFF' makes the
  record look negative if read as SBIN.
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.53]`
- **IS/3: max SF length X'7FF0' = 32,752.**
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.550]`
- **IS/1 and IS/2: max SF length X'2000' = 8,192.**
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.53]`
- RGLength "always includes the length of the RGLength parameter itself."
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.61]`
- With an SFI extension, data can occupy 32,759 bytes **less** the extension length.
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.56]`

## 8. Environment hierarchy

The contents of an AEG or OEG are **not** one fixed list — they differ by interchange
set and by the type of object the group belongs to. The three rows below are the actual
permitted contents; do not treat any of them as "the" list.

| Mechanism | Scope | Permitted contents | Source |
|---|---|---|---|
| **AEG** — page/overlay, IS/1 | one page or overlay | MCF, MPO, PGD, OBD, OBP, PTD | `[mo-dca-reference-mixed-object-document-content-architecture-reference p.534]` |
| **AEG** — page/overlay, IS/3 | one page or overlay | PEC, MDR, MPO, MPS, PGD, OBD, OBP, PTD — **no MCF** | `[mo-dca-reference-mixed-object-document-content-architecture-reference p.553]` |
| **OEG** — object container | one data object | PEC, OBD, OBP, MCD, MDR, CDD | `[mo-dca-reference-mixed-object-document-content-architecture-reference p.155]` |
| **OEG** — graphics object | one data object | PEC, OBD, OBP, MGO, MCF, GDD | `[mo-dca-reference-mixed-object-document-content-architecture-reference p.141]` |
| **OEG** — image object | one data object | PEC, OBD, OBP, MIO, IDD | `[mo-dca-reference-mixed-object-document-content-architecture-reference p.146]` |
| **REG** | pages after it, up to the next REG or end of document | pre-declares resources to download **before** the following pages | p.116, p.117 |

> For an object included directly in a page or overlay, the container "must, at a
> minimum, have the following structure: BOC/EOC with the Object Classification (X'10')
> triplet on the BOC …; OEG with OBD, OBP, and CDD; All object data partitioned into
> OCDs."
> `[mo-dca-reference-mixed-object-document-content-architecture-reference p.155]`

- "Parameters specified in the OEG override like parameters specified in the AEG,
  while like parameters specified within the same environment … replace the previous
  specification." `[mo-dca-reference-mixed-object-document-content-architecture-reference p.58]`
- "Resource Environment Groups (REGs) are optional and do not affect AEGs and OEGs.
  Identifying a resource in a REG does not remove the need to map that resource in the
  environment groups of the pages and objects that use the resource."
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.59]`
- REG scope: "from the point where it occurs up to the next REG … or the end of the
  document, whichever occurs first."
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.116]`
- REG exists for device download latency: it "is used to identify complex resources,
  such as high-resolution color images, that need to be downloaded to the presentation
  device before the pages that follow are processed."
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.117]`

**Resource search order** (MO:DCA resources): 1. internal (page-level) resource
groups — retired IS/2 only; 2. external print-file-level resource groups;
3. external resource libraries.
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.59]`

## 9. Recipes

### A — minimal valid document (IS/3)

Mandatory envelope `[mo-dca-reference-mixed-object-document-content-architecture-reference p.550, p.551]`:
BPF and EPF required; BDT and EDT required; **all** BDT structured fields must carry
the Interchange Set (X'18') triplet with ISid = X'0D00'; the BPF must carry the same
triplet; max SF length limited to X'7FF0'; the SFI Flag byte must be X'00' — IS/3 has
no support for SFI extension, segmentation, or padding.

```
BPF (D3A8A5)                          ; + X'18' triplet ISid=X'0D00'
  [ Resource Group ]
  [ Index + Document ] (S)
    BDT (D3A8A8)                      ; + X'18' triplet ISid=X'0D00'
      IMM (D3ABCC) (S)                ; invoke a medium map from the form map
      Page (D3..AF) (S)
    EDT (D3A9A8)
EPF (D3A9A5)
```

> The print file "must specify the MO:DCA Interchange Set X'18' triplet on the BPF
> and must indicate ISid = X'0D00' = MO:DCA IS/3"
> `[mo-dca-reference-mixed-object-document-content-architecture-reference p.551]`

Page structure — **IS/3 Table 27**
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.553]`

```
BPG (D3A8AF)
  AEG:
    BAG (D3A8C9)
      [ PEC (D3A7A8) ]               ; Presentation Environment Control
      [ MDR (D3ABC3) ] (S)           ; Map Data Resource
      [ MPO (D3ABD8) ] (S)           ; Map Page Overlay
      [ MPS (D3B15F) ] (S)           ; Map Page Segment
      (PGD, D3A6AF)                  ; Page Descriptor
      [ OBD (D3A66B) ]               ; Object Area Descriptor
      [ OBP (D3AC6B) ]               ; Object Area Position
      (PTD, D3B19B) F2               ; Presentation Text Data Descriptor Format 2
    EAG (D3A9C9)
  [ IOB (D3AFC3) ] (S)               ; Include Object
  [ IPO (D3AFD8) ] (S)               ; Include Page Overlay
  [ IPS (D3AF5F) ] (S)               ; Include Page Segment
  [ LLE (D3B490) ] (S)               ; Link Logical Element
  [ TLE (D3A090) ] (S)               ; Tag Logical Element
  [ BCOCA ] (S)
  [ GOCA ] (S)
  [ IOCA ] (S)
  [ PTOCA ] (S)
  [ Object Cont ] (S)
EPG (D3A9AF)
```

IS/3 notes on that page AEG
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.553]`:
1. "The OBD is only used for PTOCA objects without an OEG, and if specified: the
   measurement units must match the PGD units; the extents must match the PGD
   extents." Omitting it is the architected default — the text object area then has the
   same units and extents as the page.
2. "The OBP is only used for PTOCA objects without an OEG, and if specified: the object
   area origin must be set to zero; the object content origin must be set to zero; the
   object area orientation must be set to (0°,90°)." Omitting it is the architected
   default — the text object area is then positioned coincident with the page.
3. "The PTD is only mandatory if the page contains one or more PTOCA objects without an
   OEG."

> **Do not use the IS/1 page AEG for an IS/3 file.** The general-architecture page AEG
> (Figure 80, p.534) contains **MCF** (Map Coded Font); IS/3 Table 27 (p.553) does
> **not** allow MCF in the page AEG — it lists PEC, MDR, MPO, MPS, PGD, OBD, OBP, PTD.
> "The page contains only the following structured fields and objects, as defined in the
> general architecture subject to all applicable IS/3 restrictions."
> `[mo-dca-reference-mixed-object-document-content-architecture-reference p.553]`

Data-object envelopes — the **general** MO:DCA architecture, which IS/3 reuses subject
to its own restrictions
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.535, p.536]`:

```
BGR (D3A8BB) [ OEG: BOG(D3A8C7) { OBD, OBP, [MGO], [MCF], GDD } ] GAD(D3EEBB) (S) EGR (D3A9BB)
BIM (D3A8FB) [ OEG: BOG(D3A8C7) { OBD, OBP, [MIO], IDD } ]              IPD(D3EEFB) (S) EIM (D3A9FB)
BPT (D3A89B) PTX(D3EE9B) (S) EPT (D3A99B)
```

### B–E

Recipes B (place a presentation object at a position), C (carry a resource for later
use), D (attach metadata to a page), and E (embed a non-AFP object) are in
`research/02-modca-document-architecture.md` §4.2–4.5 in the working repo, with full
citations. Copy them into the application rather than re-deriving them.

## 10. Trap checklist

Run this before shipping a generated stream:

1. Is the SFI Flag byte X'00'? (IS/3 forbids extension / segmentation / padding.)
2. Is every SF length ≤ X'7FF0' and does it **include** the introducer?
3. Does every begin have a matching end, in the right state?
4. Is the BPF present, with the X'18' ISid = X'0D00' triplet?
5. Does every BDT carry the X'18' triplet?
6. Are resources mapped in the AEG/OEG that uses them — a REG does not substitute for
   mapping?
7. Is the Object Classification (X'10') triplet on the BOC, with a registered
   object-type OID? In IS/3 it is mandatory, occurrence 1.
   `[mo-dca-reference-mixed-object-document-content-architecture-reference p.563]`
8. For metadata: the MO Type object container must directly follow the BDT (or the
   TLEs in page-group state) and the ObjClass must be X'50' — otherwise the container
   is ignored. `[mo-dca-reference-mixed-object-document-content-architecture-reference p.116, p.121]`
9. Are reserved fields zero? SFI bytes 6–7, BDT offsets 8–9, MDDFlgs, OBP reserved
   bits.

Sources for items 1–9: items 1, 2, 4 and 5 are the IS/3 compliance conditions
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.550, p.551]`;
item 3 is the begin/end pairing rule
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.113]`;
item 6 is the resource-mapping rule
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.59]`;
item 9 is the reserved-field rule
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.113]`.

## 11. Not confirmed

- **OBP byte offsets.** The field order and most offsets were recovered from the
  (rotated) syntax pages, but **the printed offset column disagrees with the declared
  data-type widths at exactly one position** — `RGLength` — see §3.1. There is no second
  source in the corpus to cross-check it, and the third-party metamodel carries only a
  placeholder. **Read the page image (PDF p.347-348) before emitting an OBP.**
  `[mo-dca-reference-mixed-object-document-content-architecture-reference p.347, p.348]`
- Not read: OBD full parameter layout (p.345), IOB/IPG/IPO/IPS/IMM/BRS parameter
  tables, Appendix D object-type OID registry (p.669), Chapter 6 full triplet syntax.

## 12. Framing correction worth remembering

The AFPC document titled **"Presentation Object Subsets for AFP"** is *not* about
IOCA/GOCA/PTOCA/BCOCA subsets. It defines the **non-AFP formats** (TIFF, JPEG, PNG,
SVG) that may be carried inside a MO:DCA object container, with their registered
object-type OIDs. The confirmed OIDs are listed in
`research/02-modca-document-architecture.md` §5.11.
