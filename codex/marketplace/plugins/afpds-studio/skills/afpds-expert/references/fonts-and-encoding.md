# Fonts, characters, and encoding (distilled reference)

Sources: FOCA Reference (AFPC-0007-06, 270p), Character Data Representation
Architecture (SC09-2190-00, 320p), Technical Reference for Code Pages (S544-3802-02,
490p), AFPC Font Typeface Registry (FGID), Font Summary for AFP Font Collection, and
the OpenType redbook (`using-opentype-fonts-in-an-afp-system`).

Citation slugs used below:
- `foca-reference-font-object-content-architecture-reference`
- `character-data-representation-architecture-and-reference-and-registry`
- `technical-reference-for-code-pages`
- `fgid-registry-afpc-font-typeface-registry`
- `font-summary-for-afp-font-collection`
- `using-opentype-fonts-in-an-afp-system`

## 1. The one chain to remember

> **character code (code point) → code page (CPGID) → graphic character identifier
> (GCGID) → font resource → presentation object**

"A code page is a table that associates graphic character identifiers with code
points." `[foca-reference-font-object-content-architecture-reference p.30]`

The code page is *not* the font, and the font is *not* the code page — they are two
independent resources joined only by the code page's table. A code page holds
**256 code points** `[technical-reference-for-code-pages p.79]`.

Resolution direction: characters encoded as code points are associated with a
font's character information **through the code page**
`[foca-reference-font-object-content-architecture-reference p.30]`.

### Vocabulary

| Term | Meaning |
|---|---|
| **Code point** | unique code of a graphic character in the document data stream; usually 1 or 2 bytes |
| **GCGID** | unique name of a graphic character in a font. EBCDIC, uppercase A–Z and 0–9, length 4 or 8 bytes (even; default 8) |
| **CPGID** | code page global id; 1–65,279 reserved for IBM assignment |
| **GCSGID** | graphic character set global id — the list of GCGIDs a code page covers |
| **CGCSGID / GCID** | composite = GCSGID (5 digits) + CPGID (5 digits) = 10 digits. "GCID" is the legacy synonym |
| **ESID** | encoding scheme identifier (2 bytes) |
| **CCSID** | coded character set identifier |
| **ACRI** | additional coding-related required information |

`[character-data-representation-architecture-and-reference-and-registry p.38, p.45]`,
`[foca-reference-font-object-content-architecture-reference p.117, p.125, p.127, p.128]`

GCSGID reserved ranges: `X'FE00'`–`X'FEFF'` IBM RPQ use; `X'FF00'`–`X'FFFE'` customer
use `[character-data-representation-architecture-and-reference-and-registry p.45]`.

## 2. Font resource vs font reference

| | Definition | Normal residence |
|---|---|---|
| **Font resource** | the stored collection of code pages and FOCA font parameters for a particular font; the aggregate of stored font information is the **font library** | system storage / font library |
| **Font reference** | "information that identifies a particular font resource. A font reference is embedded either in a document data stream or in an application program" | — |

`[foca-reference-font-object-content-architecture-reference p.30, p.31]`

Two levels `[foca-reference-font-object-content-architecture-reference p.31]`:

| Level | Definition | Residence |
|---|---|---|
| **System-level** | resolution-independent formatting information + device-specific presentation information | font library |
| **Device-level** | device-specific font information for presentation | ROM cartridge, loadable file on disk/tape, or loadable file from a host system |

**Hard interoperability constraint**: "all receiving sites, that is, processing
applications and presentation devices, must have access to the same or equivalent font
resources" `[foca-reference-font-object-content-architecture-reference p.31]`.

### The four parameter groups of a font resource

`[foca-reference-font-object-content-architecture-reference p.32]`

| Group | Provides | Occurrence |
|---|---|---|
| Font-description | referencing / identifying / describing fonts | once per font resource |
| Font-metric | measurements for positioning the font and each character | once per supported rotation |
| Character-shape | forming images of character shapes on a presentation surface | once per shape representation technology |
| **Character-mapping** | associating character identifiers with code points on code pages | **once per code page** |

The character-mapping group is the bridge to the encoding family: "primarily used by
applications to associate code points in a document to the graphic character
information in a font resource"
`[foca-reference-font-object-content-architecture-reference p.125]`.

## 3. Structure identifiers (FOCA Table 14)

`[foca-reference-font-object-content-architecture-reference p.144, p.145]`

| Abbrev | Assigned Number | Full Field Name |
|---|---|---|
| BCF | X'D3A88A' | Begin Coded Font |
| BCP | X'D3A887' | Begin Code Page |
| BFN | X'D3A889' | Begin Font |
| CFC | X'D3A78A' | Coded Font Control |
| **CFI** | **X'D38C8A'** | **Coded Font Index** |
| CPC | X'D3A787' | Code Page Control |
| CPD | X'D3A687' | Code Page Descriptor |
| CPI | X'D38C87' | Code Page Index |
| ECF | X'D3A98A' | End Coded Font |
| ECP | X'D3A987' | End Code Page |
| EFN | X'D3A989' | End Font |
| FNC | X'D3A789' | Font Control |
| FND | X'D3A689' | Font Descriptor |
| FNG | X'D3EE89' | Font Patterns |
| FNI | X'D38C89' | Font Index |
| FNM | X'D3A289' | Font Patterns Map |
| FNN | X'D3AB89' | Font Names (Outline Fonts Only) |
| FNO | X'D3AE89' | Font Orientation |
| FNP | X'D3AC89' | Font Position |
| NOP | X'D3EEEE' | No Operation |

## 4. CFI — Coded Font Index (X'D38C8A')

Binds a **font character set** to a **code page**. The structured field data is
"25*[number of sections] bytes" — one 25-byte repeating group per section
`[foca-reference-font-object-content-architecture-reference p.153]`.

| Offset | Type | Name | Range | Meaning | M/O |
|---|---|---|---|---|---|
| 0–7 | CHAR | FCSName | — | Font Character Set Name | M |
| 8–15 | CHAR | CPName | — | Code Page Name | M |
| 16–17 | UBIN | SVSize | 0–65,535 | Specified Vertical Font Size, in 20ths of a point (1440ths of an inch) | M |
| 18–19 | UBIN | SHScale | 0–65,535 | Specified Horizontal Scale Factor, in 20ths of a point (1440ths of an inch) | M |
| 20–23 | UNDF | — | `X'00000000'` | Reserved | M |
| 24 | UBIN | Section | `X'00'` single-byte · `X'41'`–`X'FE'` double-byte raster · `X'FF'` reserved | Section Number | M |

> This table was transcribed from the **rendered page image** of PDF p.153 (printed
> p.131). The narrative pages are p.154 (names) and p.155 (sizes and section number).

**Name constraints** `[foca-reference-font-object-content-architecture-reference p.154]`:
the font character set name "can be any value except null (any name that contains
`X'FFFF'` in the first two bytes) or eight blanks (`X'4040 4040 4040 4040'`)"; the same
constraints apply to the code page name.

**Section Number (byte 24)** `[foca-reference-font-object-content-architecture-reference p.155]`:

| Case | Required value |
|---|---|
| Single-Byte | must be `X'00'` to identify a single-byte section |
| Double-Byte Raster Coded Fonts | must be `X'41'`–`X'FE'` to identify a double-byte section |
| Double-Byte Outline Coded Fonts | must be `X'00'` to identify all double-byte sections |

> The p.153 table lists `X'00'` / `X'41'`–`X'FE'` / `X'FF'` (reserved) while p.155 adds
> the Double-Byte Outline case as `X'00'`. The two pages disagree — **the specification
> is inconsistent here**; follow p.155 for outline fonts.

"This section number is the first byte of the two-byte code that identifies the
character in a coded font and in text." ("ward" is a synonym.)
`[foca-reference-font-object-content-architecture-reference p.155]`

**Name encoding** `[foca-reference-font-object-content-architecture-reference p.154]`:
names are encoded using **CPGID 500, GCSGID 103**; for interchange
**CPGID 500, GCSGID 961** is recommended — that code page permits only A–Z, 0–9,
`$`, `#`, `@`.

IBM naming conventions (**not** part of the FOCA architecture) `[foca-reference-font-object-content-architecture-reference p.154]`:
raster fonts use a two-character prefix **C0**, outline fonts **CZ**, followed by one
to six non-null characters.

## 5. CPC — Code Page Control (X'D3A787')

Header: Length (2) / SFID (3) `X'D3A787'` / Flags (1) `X'0000'` / data (13 or 17 bytes)
`[foca-reference-font-object-content-architecture-reference p.156]`.

| Offset | Type | Name | Range | Meaning | M/O |
|---|---|---|---|---|---|
| 0–7 | CHAR | DefCharID | — | Default Graphic Character Global ID | M |
| 8 | BITS | PrtFlags | See Below | Default Character Use Flags | M |
| 9 | CODE | CPIRGLen | `X'0A'` · `X'0B'` · `X'FE'` · `X'FF'` | CPI Repeating Group Length (see below) | M |
| 10 | UBIN | VSCharSN | `X'00'`–`X'FF'` | Space Character Section Number | M |
| 11 | UBIN | VSChar | `X'00'`–`X'FF'` | Space Character Code Point | M |
| 12 | BITS | VSFlags | See Below | Code Page Use Flags | M |
| +0–3 (bytes 13–16) | UBIN | Unicode scalar value | `X'00000000'`–`X'FFFFFFFF'` (excluding surrogates) | Unicode scalar value to be mapped to the default character GCGID in bytes 0–7 | O |

> **Zero or one Unicode scalar value for the default character ID** (only present when
> byte 9 contains either `X'FE'` or `X'FF'`) in the following format.
> `[foca-reference-font-object-content-architecture-reference p.156, p.158, p.159]`

> This table was transcribed from the **rendered page image** of PDF p.156 (printed
> p.134); the flag details are on p.157 and p.158.

**Default Character Use Flags (byte 8)** `[foca-reference-font-object-content-architecture-reference p.157]`:
bit 0 = invalid coded character · bit 1 = no presentation · bit 2 = no increment ·
bits 3–7 reserved. Printing a character whose invalid flag is on causes a **printer
data check** unless suppressed by print-server software.

**CPI Repeating Group Length (byte 9)** `[foca-reference-font-object-content-architecture-reference p.156, p.157]`:

| Value | Meaning |
|---|---|
| `X'0A'` | single-byte code point, repeating group length is `X'0A'` bytes |
| `X'0B'` | double-byte code point, repeating group length is `X'0B'` bytes |
| `X'FE'` | single-byte code point, group length varies per code point depending on how many Unicode scalar values are listed |
| `X'FF'` | double-byte code point, group length varies per code point depending on how many Unicode scalar values are listed |

**"Some FOCA products do not support the values X'FE' or X'FF'."**
`[foca-reference-font-object-content-architecture-reference p.157]`

**Space character (bytes 10–11)** `[foca-reference-font-object-content-architecture-reference p.158]`:
single-byte encoding → the code point in byte 10, **repeated** in byte 11;
double-byte → section number in byte 10, code point in byte 11. Typical values:

| Basic Encoding Structure | Single Byte | Double Byte |
|---|---|---|
| IBM-PC Data | `X'2020'` | Not used |
| EBCDIC Presentation | `X'4040'` | `X'4040'` |
| UCS Presentation (latin) | Not applicable | `X'0020'` |
| UCS Presentation (ideographic, full-width space) | Not applicable | `X'3000'` |

"The character shape assigned to this code point is not printed."

**Code Page Use Flags (byte 12)** `[foca-reference-font-object-content-architecture-reference p.158]`:
bit 0 = sort order (`B'1'` ⇒ CPI groups sorted in ascending **code point** order;
`B'0'` ⇒ ascending **character ID** order) · bit 4 = variable space enable
(`B'1'` ⇒ PTOCA variable space increment used; `B'0'` ⇒ all PTOCA SVI control
sequences ignored). Some products that justify text (DCF is named) require bit 4 set.

**Optional Unicode mapping entry** `[foca-reference-font-object-content-architecture-reference p.158, p.159]`:
allows user-defined characters (no registered GCGID) to work with TrueType/OpenType by
mapping the **default** character id to a Unicode scalar value. Valid range excludes
surrogates: X'00000000'–X'0000D7FF' and X'0000E000'–X'0010FFFF'. "The Unicode scalar
value and the GCGID should identify the same character and should be in all
TrueType/OpenType fonts used with this code page."

**IPDS-specific default-character behaviour** `[foca-reference-font-object-content-architecture-reference p.157]`:
in an IPDS outline font the code page need not be fully populated and may not carry a
default GCGID. Code points without an entry take the default GCGID if present; if not,
they get undefined / non-printing / incrementing flags, and on an error-continuation
action the **space character code point** is used instead. Recommended practice: set
the default GCGID to the same GCGID as the space character, so the page works with
both raster and outline character sets.

## 6. CPD — Code Page Descriptor (X'D3A687')

Data is **42 or 44 bytes** `[foca-reference-font-object-content-architecture-reference p.160]`.

| Offset | Type | Name | Range |
|---|---|---|---|
| 0–31 | CHAR | CPDesc | code page description |
| 32–33 | UBIN | GCGIDLen | 8 — graphic character GID length |
| 34–37 | UBIN | NumCdPts | 1–65,535 — number of coded graphic characters assigned |
| 38–39 | UBIN | GCSGID | `X'0000'` (no GCSGID) · `X'0001'`–`X'FFFE'` · `X'FFFF'` |
| 40–41 | UBIN | CPGID | `X'0000'` (no CPGID) · `X'0001'`–`X'FFFE'` · `X'FFFF'` |
| 42–43 | UBIN | EncScheme | encoding scheme — **optional**, so the record is 42 or 44 bytes |

`[foca-reference-font-object-content-architecture-reference p.160]`

## 7. FNC — Font Control (X'D3A789')

Header: Length (2 bytes) / SFID (3 bytes) `X'D3A789'` / Flags (1 byte) `X'0000'` /
Structured Field Data (22, 28, 32, 35, 42, or 46 bytes)
`[foca-reference-font-object-content-architecture-reference p.168, p.169]`.

> **This table was transcribed from the rendered page images** (PDF p.168–169, printed
> p.146–147). The PDF text layer interleaves the columns of this table, which is how an
> earlier draft ended up with `PatAlign` at offset 14 and the wrong values there.

| Offset | Type | Name | Range | Meaning | M/O |
|---|---|---|---|---|---|
| 0 | UBIN | Retired | `X'01'` | Retired Parameter | M |
| 1 | CODE | PatTech | `X'05'` · `X'1E'` · `X'1F'` | Pattern Technology Identifier: Laser Matrix N-bit Wide · Composite Adobe Type 0 · Type 1 Font Printer File Binary (PFB) | M |
| 2 | UNDF | Reserved | `X'00'` | Reserved for future use | M |
| 3 | BITS | FntFlags | See below | Font Use Flags | M |
| 4 | CODE | XUnitBase | `X'00'` · `X'02'` | Fixed metrics, 10 inches · Relative metrics | M |
| 5 | CODE | YUnitBase | `X'00'` · `X'02'` | Fixed metrics, 10 inches · Relative metrics | M |
| 6–7 | UBIN | XftUnits | `X'0960'` · `X'0BB8'` · `X'03E8'` | 240 pels per inch · 300 pels per inch · 1000 units per em | M |
| 8–9 | UBIN | YftUnits | `X'0960'` · `X'0BB8'` · `X'03E8'` | 240 pels per inch · 300 pels per inch · 1000 units per em | M |
| 10–11 | UBIN | MaxBoxWd | 0–32,767 | Maximum Character Box Width | M |
| 12–13 | UBIN | MaxBoxHt | 0–32,767 | Maximum Character Box Height | M |
| 14 | UBIN | FNORGLen | `X'1A'` | FNO Repeating Group Length | M |
| 15 | UBIN | FNIRGLen | `X'0A'` · `X'1C'` | FNI Repeating Group Length | M |
| 16 | CODE | PatAlign | `X'00'` · `X'02'` · `X'03'` | Pattern Data Alignment Code: 1-Byte Alignment · 4-Byte Alignment · 8-Byte Alignment | M |
| 17–19 | UBIN | RPatDCnt | `X'0'` to `X'7FFFFF'` | Raster Pattern Data Count | M |
| 20 | UBIN | FNPRGLen | `X'16'` | FNP Repeating Group Length | M |
| 21 | UBIN | FNMRGLen | `X'00'` · `X'08'` | FNM Repeating Group Length: No Raster Data · Raster Data | M |
| 22 | CODE | ResXUBase | `X'00'` | Shape resolution, 10 inches | O |
| 23 | CODE | ResYUBase | `X'00'` | Shape resolution, 10 inches | O |
| 24–25 | UBIN | XfrUnits | `X'0000'` · `X'0960'` · `X'0BB8'` | No shape resolution provided · 240 pels per inch · 300 pels per inch | O |
| 26–27 | UBIN | YfrUnits | `X'0000'` · `X'0960'` · `X'0BB8'` | No shape resolution provided · 240 pels per inch · 300 pels per inch | O |
| 28–31 | UBIN | OPatDCnt | `X'0A'` to `X'FFFFFFFF'` | Outline Pattern Data Count | O |
| 32–34 | UNDF | Reserved | `X'000000'` | Reserved for future use | O |
| 35 | UBIN | FNNRGLen | `X'0C'` | FNN Repeating Group Length | O |
| 36–39 | UBIN | FNNDCnt | `X'02'` to `X'FFFFFFFF'` | FNN Data Count | O |
| 40–41 | UBIN | FNNMapCnt | 0–65,535 | FNN Name Count | O |
| 42–nn | — | Triplets | See Below | Self-Defining Triplets | O |

**Font Use Flags (byte 3)** `[foca-reference-font-object-content-architecture-reference p.169]`:
- **Bit 0** — MICR printing: `B'0'` Normal printing · `B'1'` MICR printing
- **Bit 1** — font resource extent: `B'0'` Complete Font · `B'1'` Extension Font
- **Bits 2–3** — `B'00'`, reserved
- **Bit 4** — retired. It was used by some implementations to decide whether the
  baseline offset should be shifted by one pel. If it is 0 (default) and the baseline
  offset is negative, most implementations shift the baseline offset up by one pel.
  This processing does not apply to fonts using relative units of measure.
- **Bit 5** — `B'0'`, reserved

> **PatAlign:** byte 16 is the *base-2 exponent* of the byte alignment — `X'00'` = 1 byte,
> `X'02'` = 4 bytes, `X'03'` = 8 bytes. This is the same encoding as the FOCA
> "Pattern Data Alignment Code" glyph property, whose valid choices are 0/1/2/3 =
> One/Two/Four/Eight-byte Alignment
> `[foca-reference-font-object-content-architecture-reference p.120]`. (`X'01'` = 2-byte
> alignment is a valid glyph-property value but is **not** in the FNC byte-16 list.)

## 8. ESID — Encoding Scheme Identifier

Two bytes `[character-data-representation-architecture-and-reference-and-registry p.41]`:
byte 1 nibble 1 = **Basic Encoding Structure**, nibble 2 = **Number of Bytes per Code
Point**; byte 2 = **Code Extension Method (zz)**.

FOCA's restricted valid set `[foca-reference-font-object-content-architecture-reference p.126]`:
Basic Encoding Structure `0` none / `2` IBM-PC Data / `6` EBCDIC Presentation / `8` UCS
Presentation · Bytes per Code Point `1` fixed single-byte / `2` fixed double-byte ·
Code Extension Method `00` no extension.

### Full CDRA ESID value table

`[character-data-representation-architecture-and-reference-and-registry p.44]`

| ESID | Interpretation | States |
|---|---|---|
| 1100 | EBCDIC, SBCS, no code extension allowed | 1 |
| 2100 | IBM-PC Data, SBCS | 1 |
| 3100 | IBM-PC Display, SBCS | 1 |
| 4100 | ISO 8, SBCS | 1 |
| 4105 | ISO 8 (ASCII), SBCS, graphics in C1 area X'80'–X'9F' | 1 |
| 5100 | ISO 7 (ASCII), SBCS | 1 |
| 6100 | EBCDIC Presentation, SBCS | 1 |
| 1200 | EBCDIC, DBCS | 1 |
| 2200 | IBM-PC Data, DBCS | 1 |
| 3200 | IBM-PC Display, DBCS | 1 |
| 1301 | EBCDIC, mixed SBCS/DBCS, SO/SI code extension | 2 |
| 2300 | IBM-PC Data, mixed SBCS/DBCS, implicit code extension | 2 |
| 3300 | IBM-PC Display, mixed SBCS/DBCS, implicit code extension | 2 |
| 4403 | IBM EUC | 2–4 |
| 5404 | ISO 2022 TCP/IP | 2–4 |
| 5700 | ISO 7 triple-byte code set | 1 |
| 7200 | UCS-2 | 1 |
| 7807 | UTF-8 | 1 |
| Fxxx / xFxx / xxFE | private use, user-defined encoding scheme | — |

### Code Extension Method (zz)

`[character-data-representation-architecture-and-reference-and-registry p.43]`

| Hex | Method |
|---|---|
| 00 | no extensions specified |
| 01 | Locking Shifts (SO/SI, or LSI/LSO) |
| 02 | reserved |
| 03 | IBM EUC (ISO-2022-based) |
| 04 | TCP/IP (ISO-2022-based) |
| 05 | ISO-8 with possible graphics in C1 area |
| 06 | reserved |
| 07 | UTF-8 |
| 08–FD | reserved |
| FE | reserved for private use |
| FF | code extension consideration does not apply |

"The code extension method … indicates that a code point from an extended coded
character set **may** appear in the data; it does not mean that the extension method
has actually been used in a specific character string."

**"When the first two nibbles of the ESID are zeros, the code extension byte value
must be zero."**

### Code extension states

`[character-data-representation-architecture-and-reference-and-registry p.43]`
Numbering begins at 1. In mixed single/double-byte encodings there are 2 states:
**the single-byte coded character set is state 1, the double-byte set is state 2.**
The second nibble plus the last byte together give the number of switching states.

## 9. Code page map structure

`[technical-reference-for-code-pages p.79]`

| Field | Definition |
|---|---|
| Code Page | the code page's own name/id |
| Descriptive Name | "describes the most common use of the code page" |
| Code Page ID | "The AFP identifier by which the code page is referenced" |
| **CPGID** | unique value identifying a set of code points assigned to a list of GCGIDs |
| **GCSGID** | unique value identifying the list of GCGIDs included in the code page |
| Encoding | EBCDIC or ASCII |
| Default Character | character printed for undefined code points |
| Code Point | 1-byte code per character; hex 50 = decimal 80 |
| Character Graphic | the glyph shape shown in the matrix |
| Character ID | standard identifier regardless of type family, e.g. `LA020000` for all uppercase A |
| Baseline | where the character is aligned in a line of text |

## 10. FGID registry and font summary

**FGID registry** `[fgid-registry-afpc-font-typeface-registry p.6, p.9]`:
columns `Dec. ID | Hex. ID | Font Typeface Description`; the description carries
Family / Style / Class / Subclass. "The only item registered is the FGID and the
associated Font Typeface Name(s)."

> **Corpus extraction limitation:** the FGID pages extract as two parallel column
> streams with no reliable row-wise interleaving, so **FGID → Family mappings cannot
> be safely reconstructed from this text**. The alternate-FGID cross references that
> *are* inline: OCR-B → 306; Orator (alias Rhetoric) → 434; Light Italic (APL) → 58;
> Scribe (alias Symbol) → 30; Prestige → 432; OCR-A → 305
> `[fgid-registry-afpc-font-typeface-registry p.9]`. Class 12 = Symbolic also appears
> there, i.e. the taxonomy extends past the classes 1–8 printed on p.7.

**FontSummary conventions** `[font-summary-for-afp-font-collection p.51]`:

| Column | Meaning |
|---|---|
| AFP Typeface Name | IBM's name for the typeface |
| Type 1 Typeface Name | the Type 1 outline font name |
| Style and Weight | `RB` Roman Bold, `RM` Roman Medium, `IM` Italic Medium, `IB` Italic Bold |
| Code Page | alphabetic/symbol fonts use **only single-byte** code pages; DBCS Core Fonts use **both** |
| Character Set Identifier | 6- or 8 chars; **the second character identifies raster vs outline** (`0` = 240/300-pel raster, `Z` = AFP outline) |
| Type 1 File Name | .AFM, .INF, .PFB |
| CID-Keyed File Name | .CID, .CMP |
| Coded Font Identifier | the n in the second position has the same values as the character set identifier |
| Alternate Coded Font Identifier | for environments limiting names to 6 chars (JES); only 4 asked for, `X0` and `XZ` supplied |
| Size in Pitch or Points | pitch = characters per inch (uniformly-spaced); points = 1/72 inch (typographic/mixed) |

## 11. Inline (OpenType/TrueType) resource group

The **print-file-level** container for an embedded TrueType/OpenType font
`[using-opentype-fonts-in-an-afp-system p.45]`:

```
BRG
   ......
   BRS
      BOC
         OCD
         ......
         OCD
      EOC
   ERS
   ......
ERG
```

> The nesting is a staircase: the `OCD` structured fields sit **inside** `BOC`/`EOC`,
> which sit inside `BRS`/`ERS`, which sit inside `BRG`/`ERG`. Reading the flat string
> "BRG ... BRS BOC EOC ERS ... ERG OCD ... OCD" would wrongly make the `OCD`s siblings
> of `ERG`.

The OpenType redbook says (read from the rendered page image — the text layer of p.45
is scrambled): "Like other AFP resources, TrueType and OpenType fonts **may be** carried
in a print-file-level resource group… This resource group is optional, and if present,
must precede the first document in a print file. **Only a single resource group is
permitted in a given print file.**"
`[using-opentype-fonts-in-an-afp-system p.45]`

MO:DCA states the same rule independently: "Only a single resource group is permitted
at the print file level. If multiple resource groups appear before the first document,
or if one or more resource groups follow the first document, the treatment of these
resource groups is presentation-system-dependent."
`[mo-dca-reference-mixed-object-document-content-architecture-reference p.115]`

Inline resource group is **always searched first**: "the inline resource group (if
present) is always searched first, that is, it is *always* searched ahead of any
resource library." `[using-opentype-fonts-in-an-afp-system p.45]`

Printer-resident fonts captured via the OpenType Font Installer are **deleted** when
the Font capture function is next performed, unless RAT permission flags forbid it
`[using-opentype-fonts-in-an-afp-system p.29]`.

## 12. Trap checklist

Run before shipping anything that emits text:

1. **Do not derive the encoding scheme from the CPGID.** "It has been assumed that the
   encoding scheme information can always be reliably derived from the code page
   identifier alone, but this assumption is not true for many registered PC code pages,"
   and it breaks entirely for mixed SBCS/DBCS Far East schemes. Carry the ESID
   explicitly.
   `[character-data-representation-architecture-and-reference-and-registry p.45]`
2. **Compare both CPGID and GCSGID.** Two code pages can look identical and differ.
   `[technical-reference-for-code-pages p.81]`
3. **The font's character set and the code page's character list need not match.**
   Intended invariant: the font's graphic character set must be equal to or greater
   than the code page's. `[foca-reference-font-object-content-architecture-reference p.31, p.44]`
4. **ASCII code pages cannot be processed by DCF** (Document Composition Facility).
   `[technical-reference-for-code-pages p.80]`
5. **Do not assume a code page is 8-bit.** If "Number of Code Points Available" > 256,
   the code point must be used together with the section number.
   `[foca-reference-font-object-content-architecture-reference p.125]`
6. **Do not derive encoding from the font's GCSGID alone** — "By itself, the GCSGID
   does not specify either the inclusion or the exclusion of the SPACE
   (GCGID = SP010000) character."
   `[character-data-representation-architecture-and-reference-and-registry p.45]`
7. **Font substitution is defined behaviour, not an error** — a missing font is
   expected to be substituted. `[foca-reference-font-object-content-architecture-reference p.42, p.43]`
8. **Font references are many-to-many** with font resources; do not assume a
   name → file bijection. `[foca-reference-font-object-content-architecture-reference p.44]`
9. **Residency ≠ availability.** Availability is a query answer, not a file-existence
   test. Device-resident fonts are a separate namespace from the system font library.
   `[foca-reference-font-object-content-architecture-reference p.41, p.43]`
10. **DATA CHECK = YES is expensive** — some printers do extensive recovery even when
    data checks are blocked. **DATA CHECK = NO hides undefined code points
    entirely.** `[technical-reference-for-code-pages p.80]`
11. **Undefined code points print the default character** (a blank, `SW10000`, in
    IBM's code pages) when the data check is blocked.
    `[technical-reference-for-code-pages p.80]`
12. **Code page maps are editable** via the Type Transformer code page editor, so a
    code page you fetched from IBM is not necessarily the one the printer uses.
    `[technical-reference-for-code-pages p.80]`
13. **CPI ordering is a flag, not a guarantee** — a parser must not assume code-point
    ordering. `[foca-reference-font-object-content-architecture-reference p.158]`
14. **Section numbers are hard values, not ranges to clamp.**
15. **Structured field length includes the length field and introducer but not the
    `X'5A'` control character**; cap at X'7FF0' = 32,752 for portability.
    `[foca-reference-font-object-content-architecture-reference p.144]`
16. **Flags byte**: bits 1 and 3 are B'0'; bits 5–7 are B'000'.
    `[foca-reference-font-object-content-architecture-reference p.145]`
17. **Padding must include the padding length value.**
    `[foca-reference-font-object-content-architecture-reference p.146]`
18. **Sequence numbers are not validated** by presentation services.
    `[foca-reference-font-object-content-architecture-reference p.145]`
19. **GCGIDs are uppercase EBCDIC**; font-specific ASCII character names are
    **lowercase ASCII** — that is a style rule, not case folding.
    `[foca-reference-font-object-content-architecture-reference p.127]`

## 13. Not confirmed / open questions

- **FGID → typeface family mappings** — corpus text does not interleave the table
  columns; use the PDF page image or the registry PDF directly.
- **CDRA special-purpose GCSGID/CPGID values** (including `X'0000'` and `X'FFFF'`) are
  in the corpus at CDRA printed page 29 = **PDF p.46**
  `[character-data-representation-architecture-and-reference-and-registry p.46]`:
  "IBM standards reserve the values X'0000' and X'FFFF' for future assignments. However,
  in practice, some of these identifier values have been used for different special
  purposes." The CS value `X'0000'` is used in FD:OCA, MO:DCA and DIA profiles to
  migrate from a CGCSGID (CS/CP pair) to a CCSID identifier — when the CS portion is
  `X'0001'`, the CP portion is interpreted as a CCSID.
- **The font reference end-to-end flow** (§2.6 of the findings) and the four task
  recipes (§4.1–4.4) are in
  `research/04-fonts-characters-encoding.md` in the working repo with full citations —
  copy them into the application rather than re-deriving them.
