# OCA presentation objects — IOCA / GOCA / PTOCA / BCOCA (distilled reference)

Sources: IOCA Reference (250p), GOCA for AFP Reference (248p), PTOCA Reference (244p),
BCOCA Reference (266p) + BCOCA FAQ.

Citation slugs used below:
- `ioca-reference-image-object-content-architecture-reference`
- `afp-goca-reference-graphics-object-content-architecture-for-afp-reference`
- `ptoca-reference-presentation-text-object-content-architecture-reference`
- `bcoca-reference-bar-code-object-content-architecture-reference`
- `bcoca-faq-bar-code-object-content-architecture-frequently-asked-questions`

## 1. The shared problem

All four OCAs solve the same structural problem in different media: **given a piece of
content, describe it so a printer can rasterize it, and describe how it maps into a
rectangular presentation space.** Each defines:

1. a **content model** — self-defining fields (IOCA), drawing orders (GOCA), control
   sequences (PTOCA), or two flat structures (BCOCA);
2. a **presentation space** with its own coordinate system and units;
3. an optional-to-mandatory **descriptor** carrying space size, resolution and units,
   plus a **data** payload carrying the content.

The MO:DCA wrapper puts a rectangle (the *object area*) on the page; the OCA
descriptor tells the receiver how to map the OCA's presentation space into it.

| | **IOCA** | **GOCA (for AFP)** | **PTOCA** | **BCOCA** |
|---|---|---|---|---|
| **Content kind** | raster / bilevel images | vector graphics | text (code points, glyph runs) | bar code symbols |
| **Framing** | self-defining fields (long, extended) | drawing orders in a segment (4 formats) | control sequences (+ raw code points) | two flat structures: BSD + BSA |
| **Content space** | Image Presentation Space (IPS) | Graphics Presentation Space (GPS) | text object space (Xp/Yp) | bar code presentation space (Xbc/Ybc) |
| **Coordinate type** | image points, integer | Xg/Yg, **16-bit two's-complement signed** | I-axis (inline) / B-axis (baseline) | Xbc/Ybc, **UBIN** |
| **Descriptor (MO:DCA SF)** | **IDD** `X'D3A6FB'` | **GDD** `X'D3A6BB'` | **PTD** `X'D3B19B'` | **BDD** `X'D3A6EB'` |
| **Data (MO:DCA SF)** | **IPD** `X'D3EEFB'` | **GAD** `X'D3EEBB'` | **PTX** `X'D3EE9B'` | **BDA** `X'D3EEEB'` |
| **Descriptor lives in** | separate SF | **OEG (mandatory)** | OEG *or* AEG | **OEG** |

`[ioca-reference-image-object-content-architecture-reference p.174]`,
`[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.200]`,
`[ptoca-reference-presentation-text-object-content-architecture-reference p.182]`,
`[bcoca-reference-bar-code-object-content-architecture-reference p.200]`

## 2. The spatial model (three levels)

```
  controlling environment
        │
        ├── Usable Area (UA)   ← GOCA only: the environment-defined presentation space
        │        └── GPS window on the GPS maps into the UA
        │
        ├── OCA presentation space  (IPS / GPS / text object space / bar code space)
        │        └── size + resolution declared by the OCA descriptor
        │
        └── MO:DCA object area   (the rectangle placed on the page)
```

- GOCA names two spaces — "Drawing Order Coordinate Space (DOCS)" and "Graphics
  Presentation Space (GPS)" — but **in AFP GOCA they collapse**: "there is a one-to-one
  mapping … Therefore in AFP GOCA, DOCS and GPS are equivalent coordinate systems."
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.33]`
- The Usable Area is "a presentation space and coordinate system defined by the
  controlling environment… In the AFP environment, the usable area is a MO:DCA or
  IPDS object area" `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.34]`
- IOCA is point-based: "Each image point in IOCA Image Content is mapped to one image
  point in the Image Presentation Space", always written from the IPS origin
  `[ioca-reference-image-object-content-architecture-reference p.183, p.175]`
- BCOCA: the symbol origin is the top-left corner of an imaginary rectangle of minimum
  size bounding the bar-space patterns; height is measured in +Ybc, width in +Xbc
  `[bcoca-reference-bar-code-object-content-architecture-reference p.47]`

## 3. The four OCAs are NOT structurally parallel

Parallel in *intent*, different in *framing* — this trips people up.

| | Framing byte layout | Terminator |
|---|---|---|
| IOCA | code + length + params (long) or 2-byte code + 2-byte length + params (extended) | yes — End Segment `X'71'`, End Image Content `X'93'` |
| GOCA | 1-byte order code + optional operand/length (1-byte / 2-byte / long / extended) | **no formal End Segment** — `X'71'` is a reserved order treated as No-Op |
| PTOCA | 4-byte unchained (`X'2BD3'` + len + type) or 2-byte chained (len + type) | no — bounded by MO:DCA Begin/End Presentation Text |
| BCOCA | two flat structures (BSD, BSA), no framing bytes | no — bounded by MO:DCA Begin/End Bar Code Object |

`[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.95]`

## 4. IOCA

### 4.1 Self-defining field formats

`[ioca-reference-image-object-content-architecture-reference p.39]`

- **Long**: `C` (1-byte code) + `L` (1-byte length) + parameters. "L is the length of
  the following parameters, excluding L itself."
- **Extended**: `CC` (2-byte code, **first byte always `X'FE'`**) + `LL` (2-byte
  length) + parameters. "LL is the length of the parameters, excluding LL itself."
- Extended is used by: Image Data `X'FE92'`, Band Image Data `X'FE9C'`, nColor Names
  `X'FEB3'`, Include Tile `X'FEB8'`, Tile TOC `X'FEBB'`, Image Subsampling `X'FECE'`
  (all six are listed in Table 3 on p.40; the prose on p.39 names only five, so the
  table is authoritative). "Other values for the second byte of CC are reserved."

### 4.2 IOCA code points (Table 3)

`[ioca-reference-image-object-content-architecture-reference p.40]`

| Code | Name | Format |
|---|---|---|
| `X'70'` | Begin Segment | Long |
| `X'71'` | End Segment | Long |
| `X'8C'` | Begin Tile | Long |
| `X'8D'` | End Tile | Long |
| `X'8E'` | Begin Transparency Mask | Long |
| `X'8F'` | End Transparency Mask | Long |
| `X'91'` | Begin Image Content | Long |
| `X'93'` | End Image Content | Long |
| `X'94'` | Image Size | Long |
| `X'95'` | Image Encoding | Long |
| `X'96'` | IDE Size | Long |
| `X'97'` | Image LUT-ID (Retired) | Long |
| `X'98'` | Band Image | Long |
| `X'9B'` | IDE Structure | Long |
| `X'9F'` | External Algorithm Specification | Long |
| `X'B5'` | Tile Position | Long |
| `X'B6'` | Tile Size | Long |
| `X'B7'` | Tile Set Color | Long |
| `X'F4'` | Set Extended Bilevel Image Color | Long |
| `X'F6'` | Set Bilevel Image Color | Long |
| `X'F7'` | IOCA Function Set Identification | Long |
| `X'FE92'` | Image Data | Extended |
| `X'FE9C'` | Band Image Data | Extended |
| `X'FEB3'` | nColor Names | Extended |
| `X'FEB8'` | Include Tile | Extended |
| `X'FEBB'` | Tile TOC | Extended |
| `X'FECE'` | Image Subsampling | Extended |

### 4.3 Framing structures

`[ioca-reference-image-object-content-architecture-reference p.43, p.44, p.46, p.48]`

| Structure | ID | Offset | Type | Name | Range | Meaning | M/O |
|---|---|---|---|---|---|---|---|
| Begin Segment | `X'70'` | 0 | CODE | ID | `X'70'` | Begin Segment | M |
| | | 1 | UBIN | LENGTH | `X'00'`–`X'04'` | Length of the parameters to follow | M |
| | | 2 | UBIN | NAME | `X'00000000'`–`X'FFFFFFFF'` | Name of the Image Segment | O |
| End Segment | `X'71'` | 0 | CODE | ID | `X'71'` | End Segment | M |
| | | 1 | UBIN | LENGTH | `X'00'` | Length of the parameters to follow | M |
| Begin Image Content | `X'91'` | 0 | CODE | ID | `X'91'` | Begin Image Content | M |
| | | 1 | UBIN | LENGTH | `X'01'` | Length of the parameters to follow | M |
| | | 2 | CODE | OBJTYPE | `X'FF'` | Object type: `X'FF'` = IOCA image object; all other values are reserved | M |
| End Image Content | `X'93'` | 0 | CODE | ID | `X'93'` | End Image Content | M |
| | | 1 | UBIN | LENGTH | `X'00'` | Length of the parameters to follow | M |

### 4.4 Image Size `X'94'` (mandatory in untiled content)

The section lead-in is on p.49; **the parameter table itself is on p.50**
`[ioca-reference-image-object-content-architecture-reference p.49, p.50]`.

| Offset | Type | Name | Range | Meaning | M/O |
|---|---|---|---|---|---|
| 0 | CODE | ID | `X'94'` | Image Size parameter | M |
| 1 | UBIN | LENGTH | `X'09'` | Length of the parameters to follow | M |
| 2 | CODE | UNITBASE | `X'00'`–`X'02'` | Unit base: `X'00'` 10 inches · `X'01'` 10 centimeters · `X'02'` Logical (resolution ratio). All other values are reserved. | M |
| 3–4 | UBIN | HRESOL | `X'0000'`–`X'7FFF'` | Horizontal resolution | M |
| 5–6 | UBIN | VRESOL | `X'0000'`–`X'7FFF'` | Vertical resolution | M |
| 7–8 | UBIN | HSIZE | `X'0000'`–`X'7FFF'` | Horizontal size in image points (excluding any padding bit in each scan line) | M |
| 9–10 | UBIN | VSIZE | `X'0000'`–`X'7FFF'` | Vertical size in image points (excluding any padding scan line) | M |

> This table was transcribed from the **rendered page image** of PDF p.50 (printed p.32).

**UNITBASE semantics** `[ioca-reference-image-object-content-architecture-reference p.50]`:
- `X'00'`/`X'01'` — "Nonzero HRESOL or VRESOL values, divided by 10, yield the number of
  image points per inch or per centimeter in the corresponding direction." Example:
  `X'0007D007D0'` = 2000 image points per 10 inches in both directions.
- `X'02'` — "Dividing a nonzero HRESOL value by a nonzero VRESOL value yields the ratio of
  the horizontal and vertical resolutions."
- If HRESOL or VRESOL is zero (with UNITBASE `X'00'`/`X'01'`), the resolution in that
  direction is undefined and each image point maps onto one point in the IPS.

### 4.5 IOCA hard requirements

- Image Size **mandatory** in untiled contents, **forbidden** in tiled ones.
  `[ioca-reference-image-object-content-architecture-reference p.49]`
- "The same Image Data parameter cannot appear more than once within a single Image
  Content." `[ioca-reference-image-object-content-architecture-reference p.45]`
- HSIZE/VSIZE = `X'0000'` only legal where the receiver can derive the size; otherwise
  EC-9411. "IOCA generators should set HSIZE and VSIZE to the image's actual width and
  height regardless of the compression algorithm used… Setting either HSIZE or VSIZE to
  zero might cause some IOCA receivers to abort prematurely."
  `[ioca-reference-image-object-content-architecture-reference p.51]`
- If the size detected in the data differs from HSIZE/VSIZE → EC-9401, and the
  **system action** is "The size detected from the image data is used."
  `[ioca-reference-image-object-content-architecture-reference p.51, p.100]`
- If COMPRID or RECID is `X'FE'`, the External Algorithm Specification parameter must
  also be present in the same Image Content, else EC-9F01.
  `[ioca-reference-image-object-content-architecture-reference p.53]`
- Solid Fill Rectangle compression (`X'20'`) "can be used only within tiled images, for
  bilevel tiles. Otherwise, exception condition EC-9510 occurs."
  `[ioca-reference-image-object-content-architecture-reference p.53]`
- "Data beyond the End Segment self-defining field is ignored by receivers."
  `[ioca-reference-image-object-content-architecture-reference p.183]`

## 5. GOCA

### 5.1 Drawing order formats

`[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.97, p.98]`

| Format | Layout | Operand capacity |
|---|---|---|
| Fixed 1-byte | order code only | — |
| Fixed 2-byte | order code + 1 operand byte | 1 byte |
| Long | order code + 1-byte length + operand data | 255 |
| Extended | order code `X'FE'` + 1-byte qualifier + 2-byte length + operand data | 65,535 |

"The value of the length field is the length of the operand data in bytes; that is, the
length does not include the order code or length fields."

**Format selection is computable**: the one fixed 1-byte order has code `X'00'` (the
No-Operation); "For fixed 2-byte orders, bit 0 is set to 0, and bit 4 is set to 1, that
is, the first digit of the order code is less than 8, and the second digit is greater
than, or equal to, 8"; everything else is long format; `X'FE'` introduces extended.

### 5.2 Coordinates

- Coordinate data: "each point being specified by a set of two parameters, Xg and Yg. The
  sequence of parameters in coordinate data is (Xg, Yg); the format of the parameters is
  16-bit twos-complement signed binary integers (SBIN)."
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.99]`
- Offset data: "the format of the parameters is 8-bit twos-complement signed binary
  integers (SBIN)." `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.99]`
- "AFP GOCA uses 16-bit signed integers to specify GPS coordinates. A point outside GPS
  is characterized by a 2-byte arithmetic overflow."
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.34]`
- Geometric format is declared in the GDD: `CFORMAT` = `X'00'` means "16-bit
  high-byte-first signed integer".
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.202, p.217]`

### 5.3 Begin Segment command `X'70'`

`[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.95, p.96]`

| Offset | Type | Name | Meaning |
|---|---|---|---|
| 0 | CODE | code | `X'70'` |
| 1 | UBIN | LENGTH | `X'0C'` (fixed) |
| 2–5 | UBIN | NAME | ignored |
| 6 | BITS | FLAG1 | ignored |
| 7 | BITS | FLAG2 | CHAIN (bit 0) / CHPOS (bits 1–2, ignored) / PROLOG (**bit 3**) / ignored (bit 4) / APP (bits 5–6) / DATAFL (bit 7, ignored) |
| 8–9 | UBIN | SEGL | segment data length |
| 10–13 | CHAR | P/SNAME | ignored |

- CHAIN: `B'0'` = chained, `B'1'` = unchained.
- PROLOG: `B'0'` = no prolog, `B'1'` = prolog. **PROLOG is bit 3, not bit 1** — bit 1
  belongs to CHPOS, and CHPOS is ignored. CHPOS occupies bits 1–2, bit 4 and bit 7
  (DATAFL) are ignored.
- APP: `B'00'` = new segment; `B'01'`/`B'10'` reserved (command rejected); `B'11'` =
  append data to the existing segment.
- "Bytes 0–13 of this command are often referred to as the Begin Segment Introducer (BSI)."
- Exceptions: CPC-0001 invalid command code; CPC-7001 APP=`B'10'`; CPC-7082 APP=`B'01'`;
  CPC-70C1 invalid parameter length; CPC-70C5 insufficient data.

### 5.4 GOCA hard requirements

- **GDD is mandatory** in the OEG; the Window Specification `X'F6'` is **mandatory**
  within the GDD.
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.200, p.202]`
- The Drawing Order Subset parameter is **retired** — do not generate it for GRS2.
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.201]`
- In MO:DCA, **all segments must be chained** or they are ignored: "Unchained segments
  are ignored in AFP GOCA." `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.37, p.81, p.96, p.208]`
- "All receiving products that claim to support the MO:DCA environment must support at
  least all the orders in GOCA subset DR/2V0."
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.208]`
- "The drawing defaults apply during the whole of the drawing process. They cannot be
  changed by a control instruction while the drawing process is being executed."
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.99]`

## 6. PTOCA

### 6.1 Control Sequence Introducer

`[ptoca-reference-presentation-text-object-content-architecture-reference p.56, p.57]`

**Unchained (4 bytes)** — PREFIX `X'2B'` · CLASS `X'D3'` · LENGTH (2–255) · TYPE
(`X'00'`–`X'FE'`)

**Chained (2 bytes)** — LENGTH (2–255) · TYPE (`X'00'`–`X'FE'`)

- Class: "`X'D3'` has been assigned for PTOCA. If any other class is encountered,
  exception condition EC-1C01 exists. The standard action is to ignore the control
  sequence."
- Length: "specifies the length of the control sequence beginning with and including
  itself. **The prefix and class are not included in the length.**" → a classic
  off-by-two.
- Type: "These are the only valid function types. If any other function type is
  encountered, exception condition EC-0001 exists."

### 6.2 Chaining rule

`[ptoca-reference-presentation-text-object-content-architecture-reference p.183]`

> the first control sequence … starts with the `X'2BD3'` prefix and class code and
> indicates chaining with an **odd** function type (low-order bit `B'1'`) if other
> control sequences follow. All control sequences that follow, except for the last, are
> chained control sequences that start with their length byte (not with `X'2BD3'`) and
> have an odd function type. The last control sequence in the chain starts with the
> length byte but indicates termination of the chain with an **even** function type.

"it is recommended that generators always terminate chains with a control sequence
whose low-order bit is `B'0'`." `[ptoca-reference-presentation-text-object-content-architecture-reference p.55]`

### 6.3 All 31 control sequences

Each function type was read from that control sequence's own syntax table.

| Mnemonic | Name | Type | | Mnemonic | Name | Type |
|---|---|---|---|---|---|---|
| AMB | Absolute Move Baseline | `X'D2'`–`X'D3'` | | OVS | Overstrike | `X'72'`–`X'73'` |
| AMI | Absolute Move Inline | `X'C6'`–`X'C7'` | | RMB | Relative Move Baseline | `X'D4'`–`X'D5'` |
| BLN | Begin Line | `X'D8'`–`X'D9'` | | RMI | Relative Move Inline | `X'C8'`–`X'C9'` |
| BSU | Begin Suppression | `X'F2'`–`X'F3'` | | RPS | Repeat String | `X'EE'`–`X'EF'` |
| DBR | Draw B-axis Rule | `X'E6'`–`X'E7'` | | SBI | Set Baseline Increment | `X'D0'`–`X'D1'` |
| DIR | Draw I-axis Rule | `X'E4'`–`X'E5'` | | SCFL | Set Coded Font Local | `X'F0'`–`X'F1'` |
| ENC | Encrypted Data | `X'98'`–`X'99'` | | SEC | Set Extended Text Color | `X'80'`–`X'81'` |
| ESU | End Suppression | `X'F4'`–`X'F5'` | | SEA | Set Encrypted Alternate | `X'9C'`–`X'9D'` |
| GAR | Glyph Advance Run | `X'8C'`, `X'8D'` | | SIM | Set Inline Margin | `X'C0'`–`X'C1'` |
| GIR | Glyph ID Run | `X'8B'` (single) | | SIA | Set Intercharacter Adjustment | `X'C2'`–`X'C3'` |
| GLC | Glyph Layout Control | `X'6D'` (single) | | SKI | Set Key Information | `X'9A'`–`X'9B'` |
| GOR | Glyph Offset Run | `X'8E'`, `X'8F'` | | STC | Set Text Color | `X'74'`–`X'75'` |
| NOP | No Operation | `X'F8'`–`X'F9'` | | STO | Set Text Orientation | `X'F6'`–`X'F7'` |
| TBM | Temporary Baseline Move | `X'78'`–`X'79'` | | SVI | Set Variable Space Char Incr | `X'C4'`–`X'C5'` |
| TRN | Transparent Data | `X'DA'`–`X'DB'` | | UCT | Unicode Complex Text | `X'6A'` (single, even) |
| USC | Underscore | `X'76'`–`X'77'` | | | | |

**Classes** `[ptoca-reference-presentation-text-object-content-architecture-reference p.45, p.46, p.47]`:
- *Directive* — AMB, AMI, BLN, BSU, DBR, DIR, ENC, ESU, GAR, GIR, GLC, GOR, NOP, RMB,
  RMI, RPS, TRN, UCT
- *Modal* — SBI, SCFL, SEA, SEC, SIA, SIM, SKI, STC, STO, SVI
- *Field* — OVS, TBM, USC

Modal means the value "remains in effect until a subsequent control sequence for that
function is encountered or until the end of the current Presentation Text object."

### 6.4 PTOCA hard requirements

- Prefix/Class/Length/Type all mandatory. Class must be `X'D3'` (else EC-1C01).
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.56, p.57, p.63]`
- Function type must be defined (else EC-0001 → ignore and continue).
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.57, p.63]`
- `X'2BD3'` prefix + class must start an unchained control sequence.
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.56, p.57]`
- GLC: FFNLGTH must be `X'00'` when OIDLGTH is `X'00'`, else EC-9C0B; FFONTNME must
  not be specified when FONTOID is not specified, else EC-9C0B.
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.85, p.88]`
- GIR/GAR/GOR outside a GLC chain → EC-9C06; GIR without a preceding GLC/GAR/GOR →
  EC-9C03; unknown glyph ID → EC-9C02.
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.82, p.83]`
- **The font must be defined at the start of a text object** (SCFL + GLC with FONTOID).
- A character not in the active coded font → EC-2100, standard action = present the
  font's default character.
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.63]`
- Text may be split across PTX structured fields **on any byte boundary**, including in
  the middle of a control sequence.
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.184]`
- The UCT payload is "processed as code points without a scan for embedded control
  sequences".
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.140]`
- The PTD's **format 1** (`X'D3A69B'`) is migration-only and forbidden in a text
  object OEG.
  `[ptoca-reference-presentation-text-object-content-architecture-reference p.184]`

## 7. BCOCA

### 7.1 Bar Code Symbol Descriptor (BSD)

`[bcoca-reference-bar-code-object-content-architecture-reference p.55, p.56]`

> Transcribed from the **rendered page images** of PDF p.55–56 (printed p.31–32).
> The BCD1/BCD2 columns are the subset-restriction columns; they are unreadable in the
> PDF text layer because the text extractor interleaves them with the Range column.

15 rows, bytes 0–22 = **23 bytes** of BSD data. (The specification never states the
total in words; 23 bytes is derived from the last row, offsets 21–22.)

| Offset | Type | Name | Range | Meaning | BCD1 | BCD2 |
|---|---|---|---|---|---|---|
| 0 | CODE | Unit base | `X'00'`, `X'01'` | Ten inches; Ten centimeters | `X'00'` | `X'00'` |
| 1 | — | — | `X'00'` | Reserved | `X'00'` | `X'00'` |
| 2–3 | UBIN | XUPUB | `X'0001'`–`X'7FFF'` | Units per unit base in the Xbc direction | **`X'3840'`** | `X'0001'`–`X'7FFF'` |
| 4–5 | UBIN | YUPUB | `X'0001'`–`X'7FFF'` | Units per unit base in the Ybc direction; **must be the same as XUPUB** | **`X'3840'`** | `X'0001'`–`X'7FFF'` |
| 6–7 | UBIN | X extent | `X'0001'`–`X'7FFF'`, `X'FFFF'` | Width of bar code presentation space in L-units; Default | `X'0001'`–`X'7FFF'`, `X'FFFF'` | `X'0001'`–`X'7FFF'`, `X'FFFF'` |
| 8–9 | UBIN | Y extent | `X'0001'`–`X'7FFF'`, `X'FFFF'` | Length of bar code presentation space in L-units; Default | `X'0001'`–`X'7FFF'`, `X'FFFF'` | `X'0001'`–`X'7FFF'`, `X'FFFF'` |
| 10–11 | UBIN | Symbol width | `X'0000'`, `X'0001'`–`X'7FFF'` | Desired symbol width: Not specified (use module width); Desired width of symbol in L-units — Not supported by all BCOCA receivers | `X'0000'` | `X'0000'` |
| 12 | CODE | Type | `X'01'`–`X'03'`, `X'05'`–`X'0D'`, `X'11'`, `X'16'`–`X'18'`, `X'1A'`–`X'27'` | Bar code type (Table 9, printed p.34) | see Table 9 | see Table 9 |
| 13 | CODE | Modifier | See field description | Bar code modifier (Table 10, printed p.36) | see Table 10 | see Table 10 |
| 14 | CODE | Local ID | `X'00'`–`X'FE'`, `X'FF'` | Font Local ID for HRI; Default | `X'01'`–`X'7F'`, `X'FF'` | `X'00'`–`X'FE'`, `X'FF'` |
| 15–16 | CODE | Color | `X'0000'`–`X'0010'`, `X'FF00'`–`X'FF08'`, `X'FFFF'` | Color | `X'FF07'` | `X'FF07'` |
| 17 | UBIN | Module width | `X'01'`–`X'FE'`, `X'FF'` | Module width in mils; Default | Device specific `X'FF'` | Device specific `X'FF'` |
| 18–19 | UBIN | Element height | `X'0001'`–`X'7FFF'`, `X'FFFF'` | Element height in L-units; Default | `X'0001'`–`X'7FFF'`, `X'FFFF'` | `X'0001'`–`X'7FFF'`, `X'FFFF'` |
| 20 | UBIN | Multiplier | `X'01'`–`X'FF'` | Height multiplier | `X'01'`–`X'FF'` | `X'01'`–`X'FF'` |
| 21–22 | UBIN | WE:NE | `X'0000'`, `X'0001'`–`X'7FFF'`, `X'FFFF'` | Bar code (see byte 12) does not use ratio; Wide-to-narrow ratio; Default | `X'0000'`, at least one value, `X'FFFF'` | `X'0000'`, at least one value, `X'FFFF'` |

Note (printed p.32): "The BCD1 and BCD2 range for these fields has been specified
assuming a unit of measure of 1/1440 of an inch."

Exceptions: unit base → EC-0505 · units per unit base → EC-0605 · extents → EC-0705 ·
invalid type → EC-0300 · symbol beyond the presentation space → EC-1100 · invalid
modifier → EC-0B00. "the standard action to be taken for all exception conditions is to
report the exception condition, terminate the bar code object processing, and continue
processing with the next object."

### 7.2 Bar Code Symbol Data (BSA)

`[bcoca-reference-bar-code-object-content-architecture-reference p.118, p.119]`

> Transcribed from the **rendered page image** of PDF p.118 (printed p.94).

| Offset | Type | Name | Range | Meaning | BCD1 | BCD2 |
|---|---|---|---|---|---|---|
| 0 | BITS | Flags | — | see bit table below | | |
| 1–2 | UBIN | X offset | `X'0001'`–`X'7FFF'` | Xbc-coordinate of the symbol origin in the bar code presentation space | `X'0001'`–`X'7FFF'` | `X'0001'`–`X'7FFF'` |
| 3–4 | UBIN | Y offset | `X'0001'`–`X'7FFF'` | Ybc-coordinate of the symbol origin in the bar code presentation space | `X'0001'`–`X'7FFF'` | `X'0001'`–`X'7FFF'` |
| 5–n | — | Special functions | See field description | Special-function information specific to the bar code type. **Only used with:** Aztec Code, Data Matrix, Han Xin Code, Intelligent Mail Package Barcode, MaxiCode, PDF417, QR Code, QR Code with Image | Not supported in BCD1 | see field description |
| n+1→end | UNDF | Data | any | Data to be encoded, according to the type selected by the BSD | any value defined for the bar code type | same |

**Flags byte 0**

| Bit | Name | `B'0'` | `B'1'` |
|---|---|---|---|
| 0 | HRI | HRI **is** presented | HRI **not** presented |
| 1–2 | Position | `B'00'` device default; `B'01'` HRI below the symbol; `B'10'` HRI above the symbol | `B'11'` → **EC-1000** |
| 3 | **SSCAST** | Asterisk is not presented | Asterisk is presented |
| 4 | — | Retired item 21 (named "CPtype" in the Retired Items appendix, printed p.187) | — |
| 5 | Suppress bar code symbol | Present the symbol | Suppress the symbol |
| 6 | Suppress blanks | Don't suppress | Suppress and adjust |
| 7 | — | Retired item 3 | — |

- "If the bar-code-symbol-suppression flag (bit 5) is `B'1'`, the HRI position flags are
  ignored and should be set to `B'00'`."
  `[bcoca-reference-bar-code-object-content-architecture-reference p.51, p.119]`
- The HRI and Position flags are ignored for symbologies that do not allow HRI.

### 7.3 MO:DCA bar code object structure

`[bcoca-reference-bar-code-object-content-architecture-reference p.199]`

> Begin Bar Code Object / Object Environment Group (contains the BCOCA BSD structure
> and other information) / Zero or more Bar Code Data structured fields (contains the
> BCOCA BSA structure; there is one Bar Code Data structured field per bar code
> symbol) / End Bar Code Object

One BDA per symbol; the BDD precedes the BDAs and lives in the OEG. The colour in the
BDD's Color Specification triplet overrides BSD bytes 15–16.

### 7.4 Bar code type → modifier (the table you actually need)

`[bcoca-reference-bar-code-object-content-architecture-reference p.58, p.59, p.60, p.61]`

BSD byte 12 = **type**, byte 13 = **modifier**. The type alone is usually not enough —
several symbologies share one type and are separated only by the modifier. The
combination (type, modifier) is what the receiver validates.

| Type | Symbology | Modifier (byte 13) | BCD1 | BCD2 |
|---|---|---|---|---|
| `X'01'` | Code 39, AIM USS-39 | `X'01'` and `X'02'` | Yes | Yes |
| `X'02'` | MSI | `X'01'` through `X'09'` | Yes | Yes |
| `X'03'` | UPC/CGPC Version A | `X'00'` | Yes | Yes |
| `X'05'` | UPC/CGPC Version E | `X'00'` | Yes | Yes |
| `X'06'` | UPC Two-Digit Supplemental | `X'00'` | Yes | Yes |
| | | `X'01'` and `X'02'` | No | No |
| `X'07'` | UPC Five-Digit Supplemental | `X'00'` | Yes | Yes |
| | | `X'01'` and `X'02'` | No | No |
| `X'08'` | EAN-8 | `X'00'` | Yes | Yes |
| `X'09'` | EAN-13 | `X'00'` | Yes | Yes |
| `X'0A'` | Industrial 2-of-5 | `X'01'` and `X'02'` | No | No |
| `X'0B'` | Matrix 2-of-5 | `X'01'` and `X'02'` | No | No |
| `X'0C'` | Interleaved 2-of-5, ITF-14, AIM USS-I 2/5 | `X'01'` through `X'02'` | Yes | Yes |
| | | `X'03'` through `X'04'` | No | No |
| `X'0D'` | Codabar, 2-of-7 | `X'01'` and `X'02'` | No | Yes |
| `X'11'` | Code 128, UCC/EAN 128, AIM USS-128 | `X'02'` through `X'03'` | No | Yes |
| | GS1-128, UCC/EAN 128 | `X'04'` | No | No |
| | Intelligent Mail Container Barcode | `X'05'` | No | No |
| | Intelligent Mail Package Barcode | `X'06'` | No | No |
| `X'16'` | EAN Two-Digit Supplemental | `X'00'` | Yes | Yes |
| | | `X'01'` | No | No |
| `X'17'` | EAN Five-Digit Supplemental | `X'00'` | Yes | Yes |
| | | `X'01'` | No | No |
| `X'18'` | POSTNET (deprecated), PLANET (deprecated) | `X'00'` through `X'04'` | No | No |
| `X'1A'` | RM4SCC, Dutch KIX | `X'00'` and `X'01'` | No | Yes |
| `X'1B'` | Japan Postal Bar Code | `X'00'` and `X'01'` | No | Yes |
| `X'1C'` | Data Matrix, GS1 DataMatrix | `X'00'` | No | Yes |
| | Data Matrix, GS1 DataMatrix, including DMRE symbols | `X'01'` | No | No |
| `X'1D'` | MaxiCode | `X'00'` | No | Yes |
| `X'1E'` | PDF417 | `X'00'` and `X'01'` | No | Yes |
| `X'1F'` | Australia Post Bar Code | `X'01'` through `X'08'` | No | Yes |
| `X'20'` | QR Code | `X'02'` | No | Yes |
| | QR Code with Image | `X'12'` | No | No |
| `X'21'` | Code 93 | `X'00'` | No | Yes |
| `X'22'` | Intelligent Mail Barcode | `X'00'` through `X'03'` | No | Yes |
| `X'23'` | Royal Mail RED TAG (deprecated) | `X'00'` | No | No |
| `X'24'` | GS1 DataBar | `X'00'` through `X'04'`, `X'11'` through `X'1B'` | No | No |
| `X'25'` | Royal Mail Mailmark | `X'00'` and `X'01'` | No | No |
| `X'26'` | Aztec Code | `X'00'` through `X'03'` | No | No |
| `X'27'` | Han Xin Code | `X'00'` | No | No |

> **Do not collapse the sub-rows.** A type can have several modifier values with
> *different* subset membership — `X'06'`, `X'07'`, `X'0C'`, `X'16'`, `X'17'` and
> `X'1C'` each split that way. Only the first modifier of each of those types is in
> BCD1 (and, for `X'06'`/`X'07'`/`X'16'`/`X'17'`, in BCD2 as well); the extra
> modifiers are in **neither** subset. Writing "modifier `X'00'` (also `X'01'`,
> `X'02'`) — Yes/Yes" would tell an implementer that a supplemental barcode with a
> non-default modifier is BCD1-supported, which is false.

**Retired types** (never emit): `X'04'`, `X'0E'`, `X'0F'`, `X'10'`, `X'12'`–`X'15'`,
`X'19'`, `X'EC'`–`X'EF'` (Retired items 7, 10–16, 19, 22–25).

**Retired modifier**: type `X'11'` + modifier `X'01'` = Retired item 20 (1993), whose
meaning was "present the bar code symbol without a generated check digit"
`[bcoca-reference-bar-code-object-content-architecture-reference p.211]`.
The specification lists **16** retired modifier values in total (Retired items 7, 10–20,
22–25) — the complete list is in `research/03-oca-presentation-objects.md` §3.5.4.

> The PDF text layer flattens Table 10's multi-line symbology cells, so the
> type↔modifier pairing **cannot** be read from the text mirror — it was read from the
> rendered page image and cross-checked against Figure 10 (printed p.30) and Table 7
> (printed p.26).

## 8. Coordinates, units, chaining — comparison tables

### 8.1 Coordinate / origin conventions

| OCA | Convention | PDF p. |
|---|---|---|
| IOCA | X-Y Cartesian, fourth quadrant only, **origin top-left**; "Units along the X and Y axes correspond directly to image points that are represented by IDEs in the Image Content." The image is then placed in the Image Presentation Space (IPS) by a mapping — image points are **not** the same thing as IPS points; the scale comes from HRESOL/VRESOL (image) and the IDD (IPS) | p.34, p.35, p.50 |
| GOCA | absolute = Xg/Yg, 16-bit two's-complement SBIN; **relative** offsets = 8-bit two's-complement SBIN; DOCS ≡ GPS in AFP GOCA | p.33, p.99 |
| PTOCA | Inline (I) / Baseline (B) axes in a *rotatable* frame; `Io`/`Bo` are the frame origin, `Ic`/`Bc` the current position. AMB/AMI are absolute to the frame origin; RMB/RMI relative to the current position | p.58 |
| BCOCA | Xbc/Ybc; origin = top-left of the bounding rectangle of the bar-space patterns | p.86 |

Sources — IOCA: `[ioca-reference-image-object-content-architecture-reference p.34, p.35, p.50]`;
GOCA: `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.33, p.99]`;
PTOCA: `[ptoca-reference-presentation-text-object-content-architecture-reference p.58]`;
BCOCA: `[bcoca-reference-bar-code-object-content-architecture-reference p.86]`.

Extra PTOCA: STO sets the angle of the I-axis and B-axis w.r.t. the Xp-axis; the
default B-axis orientation is `X'2D00'` = 90°. Character advance comes from the
**active coded font**, not from a PTOCA parameter; SIA adjusts on top.

### 8.2 Resolution / measurement units

| OCA | Unit concept | Declared in |
|---|---|---|
| IOCA | image points; resolution in points per unit base; UNITBASE ten inches / ten cm / logical ratio | Image Size `X'94'` + IDD |
| GOCA | GPS units per unit base (UBASE); coordinates are integer L-units (1/1440 in nominal) | GDD Window Spec `X'F6'` |
| PTOCA | Xp-units per unit base (XPUNITVL/YPUNITVL), extent in Xp units | PTD |
| BCOCA | L-units (1/1440 in nominal) for extents/height; **mils** for module width | BSD |

- **"L-units" are not exactly 1/1440 inch.** All BCD1/BCD2 range values are
  *specified* assuming 1/1440 inch, and receivers supporting other units must support
  an equivalent relative range.
- GOCA: "The complete range is valid, and assumes a measurement unit of 1/1440 inch.
  That is, the measurement base is ten inches, and the Xg, Yg units per unit base are
  14,400."
  `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.202]`
- PTOCA's PTD ranges likewise assume 1/1440 inch with 14,400 Xp/Yp units per unit base.
- **IOCA has two independent resolutions** and they are *not* interchangeable: the
  Image Size parameter describes the image at creation; the IDD describes the IPS. The
  **IDD wins at render time**.
- **BCOCA's module width is in mils, not L-units** — a common unit bug.

### 8.3 Chaining

| OCA | Chaining concept | PDF p. |
|---|---|---|
| IOCA | none at the OCA level — the Image Segment is one self-contained segment (Begin Segment … End Segment); how that content is fragmented across IPDS commands is an IPDS question, not an IOCA one | p.39, p.42 |
| GOCA | a **segment** property (FLAG2 bit 0 CHAIN). Chained segments are executed then discarded; **unchained segments are ignored** | p.95, p.96, p.208 |
| PTOCA | a **control-sequence** property, encoded in the **low-order bit of the function type** — odd = continues, even = terminates. Chained sequences use the 2-byte introducer | p.183 |
| BCOCA | none; "there is one Bar Code Data structured field per bar code symbol" | p.199 |

Sources — IOCA: `[ioca-reference-image-object-content-architecture-reference p.39, p.42]`;
GOCA: `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.95, p.96, p.208]`;
PTOCA: `[ptoca-reference-presentation-text-object-content-architecture-reference p.183]`;
BCOCA: `[bcoca-reference-bar-code-object-content-architecture-reference p.199]`.

## 9. Trap checklist

1. **IOCA: `X'93'` is End Image Content, `X'71'` is End Segment** — both are 2 bytes
   total (ID + LENGTH `X'00'`).
   `[ioca-reference-image-object-content-architecture-reference p.40, p.44, p.48]`
2. **IOCA: `X'FE92'` is the only "image payload" code**; `X'FE9C'` is Band Image Data.
   `[ioca-reference-image-object-content-architecture-reference p.39, p.40]`
3. **GOCA: `X'70'` is the Begin Segment *command* code — it is NOT a drawing-order
   identifier.** Table 20 "Drawing Orders Sorted by ID" does not list `X'70'` at all;
   the table runs `X'68'` → `X'71'`. Do not confuse the 14-byte Begin Segment command
   (BSI) with an order.
   `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.220, p.221]`
4. **GOCA: `X'21'` is Set Current Position as a drawing order, but `X'21'` is also the
   Set Current Defaults *instruction* inside the GDD.** Same byte, different namespaces.
   `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.163, p.86]`
5. **GOCA: `X'71'` looks like an End Segment but is a reserved No-Op** — and it is
   *fixed 2-byte*, not long format.
   `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.95, p.101]`
6. **GOCA: unchained segments are silently ignored** (not an error). A whole graphic can
   vanish with no diagnostic.
   `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.95, p.96, p.208]`
7. **PTOCA: most mnemonics pair `TYPE` and `TYPE+1`** — unchained = even, chained = odd.
   **But three are single-valued**: GLC `X'6D'`, GIR `X'8B'`, UCT `X'6A'`
   `[ptoca-reference-presentation-text-object-content-architecture-reference p.83, p.84, p.141]`
   — and GAR (`X'8C'`/`X'8D'`) and GOR (`X'8E'`/`X'8F'`) are paired but *not* adjacent
   to their mnemonic neighbours. Get the parity wrong and the receiver ignores the
   sequence (EC-0001). See §6.3 for the authoritative per-mnemonic table.
8. **PTOCA: LENGTH counts the introducer bytes too** (but not the prefix/class) —
   "The control sequence length specifies the length of the control sequence beginning
   with and including itself. The prefix and class are not included in the length."
   `[ptoca-reference-presentation-text-object-content-architecture-reference p.57]`
9. **PTOCA: `X'D3'` is the class byte, `X'2B'` is the prefix.** Chained sequences have
   *neither*.
   `[ptoca-reference-presentation-text-object-content-architecture-reference p.56, p.57]`
10. **PTOCA: a PTX can be split on any byte boundary**, including mid-control-sequence.
    `[ptoca-reference-presentation-text-object-content-architecture-reference p.184]`
11. **BCOCA: bar code type `X'11'` is a *family*, not one symbology** — Code 128,
    AIM USS-128, GS1-128, UCC/EAN 128 and both Intelligent Mail variants share it and
    are distinguished by the **modifier**.
    `[bcoca-reference-bar-code-object-content-architecture-reference p.58, p.60, p.61]`
12. **BCOCA: `X'00'` is a valid modifier for many types but the *default* modifier is
    type-dependent** (e.g. UPC-A = type `X'03'` + modifier `X'00'`; Code 39 = type
    `X'01'` + modifier `X'01'`/`X'02'` — Code 39 has **no** `X'00'` modifier).
    `[bcoca-reference-bar-code-object-content-architecture-reference p.60, p.61, p.72]`
12b. **BCOCA: modifier `X'01'` for bar code type `X'11'` (Code 128) is RETIRED**
    (Retired item 20, 1993) — its meaning was "present the bar code symbol without a
    generated check digit". Code 128's live modifiers are `X'02'`–`X'03'` (Code 128,
    UCC/EAN 128, AIM USS-128), `X'04'` (UCC/EAN 128 and GS1-128), `X'05'` (Intelligent
    Mail Container Barcode), `X'06'` (Intelligent Mail Package Barcode). Only
    `X'02'`–`X'03'` are in the BCD2 subset; `X'04'`–`X'06'` are in neither subset.
    `[bcoca-reference-bar-code-object-content-architecture-reference p.60, p.61, p.211]`
13. **BCOCA: the desired-symbol-width parameter is not supported by all receivers** — if
    you set it, also set a module width.
    `[bcoca-reference-bar-code-object-content-architecture-reference p.58]`
14. **BCOCA: module-width rounding is applied to the module width, not to each bar.**
    Applying the multiple first yields non-integer bar widths and breaks symbology
    compliance. `[bcoca-faq-bar-code-object-content-architecture-frequently-asked-questions p.15]`
15. **BCOCA: HRI flags are ignored for 12 symbologies** (2D codes, Japan Postal,
    RM4SCC, Royal Mail variants) — setting them is harmless but misleading.
    `[bcoca-reference-bar-code-object-content-architecture-reference p.62, p.119]`
16. **GOCA: drawing defaults are frozen for the whole drawing process** — "The drawing
    defaults apply during the whole of the drawing process. They cannot be changed by a
    control instruction while the drawing process is being executed."
    `[afp-goca-reference-graphics-object-content-architecture-for-afp-reference p.99]`
17. **PTOCA: the font must be defined at the start of a text object** — "The AFP
    generator must therefore always define an active font at the start of the text object
    by generating a SCFL control sequence that specifies the font LID and a GLC that
    specifies the font OID."
    `[ptoca-reference-presentation-text-object-content-architecture-reference p.85]`

## 10. Not confirmed / open questions

- **PTOCA control sequence parameter layouts** were read in full only for GIR; the
  remaining 30 are in `research/03-oca-presentation-objects.md` §3.4.4 — copy from
  there rather than re-deriving.
- **The complete GOCA drawing-order code table** (with the computable length column)
  is in the research file §3.3.5.
- **The complete BCOCA bar code type and modifier tables** (Table 9 / Table 10) are in
  the research file §3.5.3–3.5.4.
- The task recipes (embed an image / draw a graphic / render text / render a barcode)
  are in the research file §4.1–4.4 with full citations.
