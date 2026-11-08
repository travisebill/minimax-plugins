# Line data, metadata, and colour (distilled reference)

Sources: Line Data Programming Guide and Reference (260p), MOCA Reference, Metadata
Guide for AFP, CMOCA Reference (160p), ACMA (AFP Color Management Architecture,
G550-1046-00), and the AFPC IPDS encryption recommendation.

Citation slugs used below:
- `line-data-reference-programming-guide-and-line-data-reference`
- `moca-reference-metadata-object-content-architecture-reference`
- `metadata-guide-for-afp`
- `cmoca-reference-color-management-object-content-architecture-reference`
- `afp-color-management-architecture-acma`
- `recommended-method-to-encrypt-ipds-communications`

## 1. Line data — the "outboard formatting" path

An application emits **plain line data** (records, no positioning information); a
**Page Definition resource** tells the presentation services program how to compose
those records into physical pages. The application never changes; only the Page
Definition changes.

> "One of the major enhancements provided by AFP to existing line-data applications is
> the ability to print application-generated output in different formats without making
> any application changes. This function is called outboard formatting, and is provided
> by the Page Definition resource object."
> `[line-data-reference-programming-guide-and-line-data-reference p.33]`

Consequences:

- **A Page Definition is mandatory** for any print file containing line data, "whether
  alone or in combination with MO:DCA structured fields".
  `[line-data-reference-programming-guide-and-line-data-reference p.32]`
- **The Page Definition name comes from job control, not from the data.**
  `[line-data-reference-programming-guide-and-line-data-reference p.33]`
- **One Page Definition per print file, many copies.** "only one Page Definition can be
  used to map the output format of that file. However, multiple copies of the file can be
  printed, each one using a different Page Definition, if the appropriate job control
  statements are used."
  `[line-data-reference-programming-guide-and-line-data-reference p.33]`

### How a line-data stream becomes pages

The Page Definition is a MO:DCA-conformant structured field resource object holding one
or more **Data Maps**. Each Data Map holds a **Data Map Transmission Subcase** (DMTS)
whose descriptors (LND / RCD / XMD) map each incoming record onto the page:

```
Page Definition (resource object)
  BPM → [CCP]×n → [IOB]×n → REG → Data Map{ DMTS{ BDX, DXD, LNC, LND×n,
         [FDS/FDX], EDX } }×n → EPM   (EPM name must match BPM name)
```

`[line-data-reference-programming-guide-and-line-data-reference p.34, p.35, p.44, p.46]`

### Line data structured field IDs

Each row's page is the page that defines **that** structured field (the
`ACR (X'HEX') Syntax` line for it), so a claim about one identifier does not rest on a
page that only happens to mention it.

| SF | ID | Name | PDF p. |
|---|---|---|---|
| BDM | `X'D3A8CA'` | Begin Data Map | p.87 |
| BDX | `X'D3A8E3'` | Begin Data Map Transmission Subcase | p.94 |
| BPM | `X'D3A8CB'` | Begin Page Map | p.95 |
| CCP | `X'D3A7CA'` | Conditional Processing Control | p.96 |
| DXD | `X'D3A6E3'` | Data Map Transmission Subcase Descriptor | p.100 |
| EDM | `X'D3A9CA'` | End Data Map | p.101 |
| EDX | `X'D3A9E3'` | End Data Map Transmission Subcase | p.102 |
| EPM | `X'D3A9CB'` | End Page Map | p.103 |
| FDS | `X'D3AAEC'` | Fixed Data Size | p.104 |
| FDX | `X'D3EEEC'` | Fixed Data Text | p.105 |
| IDM | `X'D3ABCA'` | Invoke Data Map | p.106 |
| IOB | `X'D3AFC3'` | Include Object | p.107 |
| IPO | `X'D3AFD8'` | Include Page Overlay | p.111 |
| IPS | `X'D3AF5F'` | Include Page Segment | p.113 |
| LNC | `X'D3AAE7'` | Line Descriptor Count | p.115 |
| LND | `X'D3A6E7'` | Line Descriptor | p.116 |
| RCD | `X'D3A68D'` | Record Descriptor | p.142 |
| XMD | `X'D3A68E'` | XML Descriptor | p.169 |

All pages are in
`[line-data-reference-programming-guide-and-line-data-reference]`.

### Line Descriptor (LND) byte layout

`[line-data-reference-programming-guide-and-line-data-reference p.116, p.117]`

| Offset | Type | Name | Range | Meaning | M/O |
|---|---|---|---|---|---|
| 0–1 | BITS | `LNDFlgs` | see bit table | LND flags | M |
| 2–3 | UBIN | `IPos` | 0 to page extent minus 1 | Inline Position | M |
| 4–5 | UBIN | `BPos` | 0 to page extent minus 1 | Absolute baseline position | M |
| 4–5 | SBIN | `BPos` | `X'8000'`–`X'7FFF'` | Relative baseline position | |
| 6–9 | CODE | `TxtOrent` | `X'0000 2D00'` · `X'2D00 5A00'` · `X'5A00 8700'` · `X'8700 0000'` | Text (I,B) Orientation: 0,90 degrees · 90,180 degrees · 180,270 degrees · 270,360 degrees | M |
| 10 | CODE | `FntLID` | `X'01'`–`X'7F'` | Primary font local ID | M |
| 10 | CODE | `FntLID` | `X'FF'` | Presentation system default font | |
| 11 | CODE | `ChnlCde` | `X'00'`–`X'0C'` | Channel code | M |
| 12–13 | UBIN | `NLNDskp` | `X'0001'`–`X'FFFF'` | Next LND if skipping | M |
| 14–15 | UBIN | `NLNDsp` | `X'0001'`–`X'FFFF'` | Next LND if spacing | M |
| 16–17 | UBIN | `NLNDreu` | `X'0001'`–`X'FFFF'` | Next LND if reusing data | M |
| 18–25 | CHAR | `SupName` | a null value `X'FF...FF'` is not valid | Suppression token name | M |
| 26 | CODE | `SOLid` | `X'01'`–`X'7F'` | Shift-out font local ID | M |
| 26 | CODE | `SOLid` | `X'00'` | Not specified | |
| 27–30 | UBIN | `DataStrt` | `X'00000000'`–`X'00007FFF'` | Data start position | M |
| 31–32 | UBIN | `DataLgth` | `X'0000'`–`X'FFFE'` | Data length | M |
| 31–32 | UBIN | `DataLgth` | `X'FFFF'` | Place remaining bytes | |
| 33–34 | CODE | `TxtColor` | See LND Semantics. | Text color value | M |
| 35–36 | UBIN | `NLNDccp` | `X'0000'`–`X'FFFF'` | Next LND if conditional processing | M |
| 37 | CODE | `SubpgID` | `X'00'`–`X'FF'` | Subpage ID | M |
| 38–39 | CODE | `CCPID` | `X'0000'`–`X'FFFF'` | CCP Identifier | M |
| 40–n | — | Triplets | — | See LND Semantics for triplet applicability. | O |

> This table was transcribed from the **rendered page images** of PDF p.116–117 (printed
> p.98–99). The field names are `TxtOrent` and `ChnlCde` — note that the *prose* of the
> same specification spells the orientation parameter `TxtOrent` as well, but other
> AFP documents (RCD, XMD) use the same spelling, so do not "correct" it to
> `TxtOrient`.

**The optional tail is confirmed by the corpus**: "Prior to the addition of color and
conditional processing to the page definition, bytes 33 through 39 were not defined as
part of the LND structured field. … **The valid length of the LND without the color and
conditional processing fields was 33 bytes.** Processors of page definitions may safely
assume the value of each missing field is zero. LND triplets are not allowed on the
shorter version of the LND."
`[line-data-reference-programming-guide-and-line-data-reference p.117]` — i.e. `TxtColor`,
`NLNDccp`, `SubpgID` and `CCPID` are the optional tail and default when absent.

**LNDFlgs bits** `[line-data-reference-programming-guide-and-line-data-reference p.116]`:
bit 0 end page if skipping · bit 1 end page if spacing · bit 2 generate inline position ·
bit 3 generate baseline position · bit 4 generate font change · bit 5 generate suppression ·
bit 6 reuse record · bit 7 use fixed data · bit 8 reserved (should be zero) ·
bit 9 use compatibility TRC · bit 10 set text color · bit 11 conditional processing ·
bit 12 resource object include · bit 13 relative baseline position ·
bits 14–15 reserved (should be zero).

### Rendering Intent triplet `X'95'`

`[line-data-reference-programming-guide-and-line-data-reference p.167]`

| Offset | Type | Name | Values |
|---|---|---|---|
| 0 | UBIN | `Tlength` | length of the triplet including `Tlength` |
| 1 | CODE | `Tid` | `X'95'` |
| 2–3 | — | — | `X'FFFFFF'` not used |
| 4–6 | — | — | reserved, should be zero |
| 7 | CODE | `GOCARI` | `X'00'` perceptual · `X'01'` media-relative colorimetric · `X'02'` saturation · `X'03'` ICC-absolute colorimetric · `X'FF'` not specified |
| 8–9 | — | — | reserved, should be zero |

- Perceptual: "Gamut mapping is vendor-specific and colors are adjusted to give a pleasing
  appearance. This intent is typically used to render continuous-tone images."
- Media-relative colorimetric: "In-gamut colors are rendered accurately and out-of-gamut
  colors are mapped to the nearest value within the gamut… typically used for vector
  graphics."

Placement: "Rendering intent is specified with the Rendering Intent (`X'95'`) triplet on
the Presentation Environment Control (PEC) structured field. For document hierarchy levels
other than the object level, rendering intents can be specified independently for each
major AFP color object type category." `[afp-color-management-architecture-acma p.18]`

## 2. Metadata (MOCA)

### Metadata Object (MO) header

`[moca-reference-metadata-object-content-architecture-reference p.26]`

| Offset | Len | Type | Name | Value |
|---|---|---|---|---|
| 0–3 | 4 | UBIN | `MOLength` | `X'00000032'`–`X'FFFFFFFF'` — MO length **including this**; minimum 50 bytes |
| 4–5 | 2 | UBIN | `HeaderLength` | `X'002E'`–end of header |
| 6–11 | 6 | UTF16 | `MOType` | `DES` = `X'0044 0045 0053'` (Descriptive) |
| 12–19 | 8 | UTF16 | `MOFormat` | `AFPT` = `X'0041 0046 0050 0054'` (AFP Tagging) |
| 20–39 | 20 | UTF16 | `MOCompression` | `XMP` / `NONE` / `GZIP` / `EXI` + 8 reserved bytes |
| 40–47 | 8 | UBIN | `MONameLength` | `X'0000'`–`X'00FA'`, **even only**; length in **bytes** of the `MOName` that follows |
| 48–49 | 2 | UNDF | — | reserved; accept but ignore, do not specify |
| 50–end | var | UTF16 | `MOName` | any valid UTF-16BE characters (even byte count) |
| — | — | — | `MOData` | the metadata payload |

> **Alignment caveat (honest).** The corpus table prints the fixed fields at offsets
> 0–49 with `MOName` starting at 50, while `HeaderLength` has a stated minimum of 46
> (`X'002E'`). Those two do not obviously reconcile, and the extracted table merges the
> "Length in Bytes" and "Offset" columns. **Trust `HeaderLength` and `MOLength` from the
> stream rather than a hard-coded name offset.**

### AFP Tagging (metadata guide) essentials

- **Metadata is invisible by design.** "In AFP environments, the MOs have no presentation
  semantic and may be ignored by products not interested in the metadata."
  `[metadata-guide-for-afp p.15]`
- **Pointer origin is *after* the MO**, not the start of the file: "The pointer position
  starts at zero in the AFP following the Metadata Object (MO) containing this metadata
  tagging information." `[metadata-guide-for-afp p.17]`
- **Pairing violations**: `BeginIndex`/`EndIndex` must pair; `IndexElement`/`Offset` must
  pair; the two pairs "cannot be used individually and are not meant to be intermixed".
  `[metadata-guide-for-afp p.23]`
- **Tag order matters**: "If a specific tag is used, it must appear exactly in the order
  shown in this chapter." `[metadata-guide-for-afp p.19]`
- **Untagged content is ignored**: "Any content not explicitly tagged is to be considered
  as ignored by default." `[metadata-guide-for-afp p.18]`
- **`<Private>` is a dead end for accessibility**: private extensions "are ignored by
  conformant metadata processors", and "any information relevant to assistive technology
  should not be included in the private section." `[metadata-guide-for-afp p.17]`
- **`tid` is unique to the AFP page being tagged**, not globally.
  `[metadata-guide-for-afp p.23]`

## 3. Colour management (CMOCA / ACMA)

### CMR header

`[cmoca-reference-color-management-object-content-architecture-reference p.28, p.29, p.30]`

> "Bytes 0–163 represent the CMR Header. Each field in the CMR header has a fixed
> length. The fields from byte 10–155 are character data encoded as UTF-16BE. Data in
> these fields are left aligned. If the number of the characters in these fields is
> smaller than the field length, the remaining bytes will be padded with `@` (`X'0040'`).
> Any field from byte 44–139 is 'unspecified' if it is filled with `@` characters."

> "The CMR name is the concatenated fields in bytes 10–155, exactly in the order
> specified in the CMR header. The CMR name is 73 characters (146 bytes) long. It should
> be unique, since it is the name that will be used in the MO:DCA data stream to
> reference the resource."

| Offset | Len | Type | Name | Value / range |
|---|---|---|---|---|
| 0–3 | 4 | UBIN | length | `X'000000A4'`–`X'FFFFFFFF'`; CMR length **including** the length field |
| 4–7 | 4 | CODE | `CMRSig` | `X'434D5239'` ("CMR" + `X'39'`) |
| 8–9 | 2 | — | — | reserved, set to zero |
| 10–25 | 16 | UTF16 | `CMRAlias` | 8-character user-defined alias |
| 26–29 | 4 | UTF16 | `CMRType` | `CC` · `DL` · `HT` · `IX` · `LK` · `TC` |
| 30–43 | 14 | UTF16 | `CMRVersion` | `ddd.ddd` · `AFP.ddd` · `generic` · `pasthru` |
| 44–53 | 10 | UTF16 | `ManufacturerName` | `@@@@@` = unspecified |
| 54–65 | 12 | UTF16 | `DeviceType` | `@@@@@@` = unspecified |
| 66–71 | 6 | UTF16 | `DeviceModel` | `@@@` = unspecified |
| 72–77 | 6 | UTF16 | `MediaBrightness` | `0`–`100` for print media; `Zxy` for screens |
| 78–83 | 6 | UTF16 | `MediaColor` | 3-char code, see below |
| 84–87 | 4 | UTF16 | `MediaFinish` | 2-char code, see below |
| 88–93 | 6 | UTF16 | `MediaWeight` | 1–999, grams/m² |
| 94–103 | 10 | UTF16 | `Prop1` | CMR-type-specific |
| 104–115 | 12 | UTF16 | `Prop2` | CMR-type-specific |
| 116–123 | 8 | UTF16 | `Prop3` | CMR-type-specific |
| 124–131 | 8 | UTF16 | `Prop4` | CMR-type-specific |
| 132–139 | 8 | UTF16 | `Prop5` | CMR-type-specific |

`MediaColor` values: `blu` blue · `buf` buff · `gdr` goldenrod · `grn` green · `gry` gray ·
`ivy` ivory · `noc` no-colour (transparency) · `org` orange · `pnk` pink · `red` red ·
`wht` white · `ylw` yellow · `custom` · `@@@` not specified.

`MediaFinish` values: `cm` commodity · `ct` coated · `gl` glossy · `hg` high-gloss ·
`mt` matte · `no` none · `np` newsprint · `sg` semi-gloss · `st` satin · `tr` treated ·
`custom` · `@@` not specified.

**The CMR name is the reference key** and is error-prone to build by hand. The corpus
gives a worked example: `Alias=JohnMay4, CMRType=HT, CMRVersion=1.2,
ManufacturerName=IBM, DeviceType=4100, DeviceModel=PD1, MediaBrightness=94,
MediaColor=wht, MediaFinish=gl, MediaWeight=90, number of device levels=2, Halftone
type=rnd, line screen frequency=141, resolution=600, rotation=proc` produces
`JohnMay4HT001.200IBM@@4100@@PD194@whtgl90@2@@@@rnd@@@141@600@proc@@@@@@@@`.
`[cmoca-reference-color-management-object-content-architecture-reference p.28]`

## 4. Security — encrypting IPDS

`[recommended-method-to-encrypt-ipds-communications p.3, p.4]`

- **TLS 1.3 or later.**
- **TLS does not change IPDS**: "neither the protocol that defines how the TCP/IP IPDS
  communication is accomplished, nor the IPDS architecture itself, is changing due to this
  recommendation." Enabling TLS is a transport-layer change only — no AFP-level changes,
  no new structured fields, no renegotiation of the IPDS command set.
- **Port separation is required by the recommendation**: encrypted IPDS should use a
  different port from unencrypted IPDS (8801 vs the traditional 5001); dual-simplex pairs
  get 8802/8803.
- **The recommendation is optional** — it "does not require all IPDS implementations to
  implement support for TLS", but two endpoints only interoperate securely if they share
  a method.
- **Performance is a real constraint**: IPDS printers print while receiving; encryption
  overhead "could cause printers to be unable to print at rated speed."
  `[recommended-method-to-encrypt-ipds-communications p.3]` Enable TLS only
  when needed and size buffers accordingly.

## 5. Trap checklist

**Line data**

1. **Choosing line data when you should have used MO:DCA.** If the application already
   knows where everything goes, MO:DCA is strictly simpler. Use line data when the *same*
   application output must be re-presented in different layouts without touching the
   application.
2. **Forgetting the Page Definition entirely.**
3. **Assuming the first Data Map in the file is the one in use**: "When a Page Definition
   containing more than one Data Map … is used, the one that appears physically first in
   the resource object is selected as the default."
   `[line-data-reference-programming-guide-and-line-data-reference p.34]`
4. **Mixing descriptor kinds**: "A Data Map Transmission Subcase can contain LNDs, RCDs,
   or XMDs, **but not a mixture**."
   `[line-data-reference-programming-guide-and-line-data-reference p.44]`
5. **Mixing MO:DCA structured fields with XML data** — explicitly disallowed.
6. **Mismatched carriage control conventions** between ANSI and machine-code forms.

**Metadata**

1. **Metadata is invisible by design** — never depend on an MO being consumed.
2. **Pointer origin is after the MO**, not the start of the file.
3. **Pairing violations** (BeginIndex/EndIndex; IndexElement/Offset).
4. **Tag order matters.**
5. **Untagged content is ignored.**
6. **`<Private>` is a dead end for accessibility.**
7. **`tid` is unique per page, not globally.**

**Colour**

1. **The CMR name is the reference key** — build it with a library, not by hand.
2. **`@` padding means "unspecified", and unspecified device fields auto-match.**
3. **Padding-format mismatch**: the XOH-OPC device type is EBCDIC (`004100`) while the CMR
   header is UTF-16BE right-padded with `@` (`4100@@`); comparison tools "must be prepared
   to indicate a match taking into account the differences in padding practices."
   `[cmoca-reference-color-management-object-content-architecture-reference p.32]`
4. **Brightness scales are not interchangeable** (TAPPI GE vs ISO differ by ~2 units);
   "the scale that is used to specify each value must be the same" on both sides.
   `[cmoca-reference-color-management-object-content-architecture-reference p.33]`
5. **Media must match the device's loaded media**, otherwise the CMR does not apply.
6. **Only HT and TTC may be `generic`; only CC may be `passthru`.**
7. **Generic and passthrough CMR data is ignored** — do not expect the payload to act.

**Security**

1. TLS does not change IPDS — no AFP-level changes.
2. Use a separate port for encrypted IPDS.
3. The recommendation is optional; both ends must agree.
4. TLS 1.3 or later.
5. Encryption overhead can stop printers printing at rated speed.

## 6. Not confirmed / open questions

- **MOCA header offsets** do not reconcile with the stated `HeaderLength` minimum — trust
  the stream's own length fields (see §2).
- **CMOCA colour spaces** (CIELAB / RGB / CMYK definitions as the corpus defines them),
  the CMR data tagged format and the rendering-intent tags are in
  `research/05-line-data-metadata-color.md` §3.7–3.8 with full citations.
- **ACMA's association of CMRs with document components** is in the research file §3.10.
- **The Metadata Guide's full AFP Tagging XML structure** is in the research file §3.5.
- The task recipes are in the research file §4.
