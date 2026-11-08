# IPDS transport layer (distilled reference)

Source: IPDS Reference, AFPC-0001-13 (1152 pages), plus UP3i v1.20 and the IPDS
encryption recommendation.

Citation slug used below: `ipds-reference-intelligent-printer-data-stream-reference`
(the UP3i and encryption documents are cited by their own slugs where used).

## 1. The correction that matters most

**IPDS and MO:DCA are sibling data streams, not layers of each other.**

The AFP architecture is split into "two major categories: data streams and objects",
and the two strategic data-stream architectures are MO:DCA and IPDS
`[ipds-reference-intelligent-printer-data-stream-reference p.38]`.

- **MO:DCA** "defines the data stream used by applications to describe documents and
  object envelopes for interchange with other applications and application services…
  Presentation fidelity is accommodated by including resource objects in the documents
  that reference them."
- **IPDS** "defines the data stream used by print server programs and device drivers to
  manage all-points-addressable page printing on a full spectrum of devices… The same
  object content architectures carried in a MO:DCA data stream **can be carried in an
  IPDS data stream**… The IPDS architecture defines **bidirectional command protocols**
  for query, resource management, and error recovery."

> **Consequence:** you cannot "wrap MO:DCA data into an IPDS stream". You re-encode the
> same content as IPDS commands.

IPDS is transport-independent: "IPDS data streams are independent of the carrying
communications protocol." There is **no IPDS stream header, magic number, or trailer**
— the stream is a concatenation of length-prefixed commands.
`[ipds-reference-intelligent-printer-data-stream-reference p.43]`

## 2. The IPDS command frame (the only universal structure)

`[ipds-reference-intelligent-printer-data-stream-reference p.106]`

```
+------+---------+-----+------+------------------+
| Length (2)   | Code (2) | Flg | CID (2, opt.) | Data ...        |
+------+---------+-----+------+------------------+
  off 0–1      off 2–3    4    off 5–6          off 7 .. end
```

| Offset | Type | Name | Range | Meaning |
|---|---|---|---|---|
| 0–1 | UBIN | Length | `X'0005'`–`X'7FFF'` | "Length of the command… The length includes the length field itself, the command code field, the flag byte, and the optional correlation ID (CID) and data fields." |
| 2–3 | CODE | Command code | `X'D600'`–`X'D6FF'` | a two-byte General Data Stream (GDS) registered structured field ID |
| 4 | BITS | IPDS command flags | — | see below |
| 5–6 | UBIN | CID (optional) | `X'0000'`–`X'FFFF'` | present only if flag bit 1 = B'1'; echoed by the printer in a NACK |
| 7 → end | — | Data | — | 0–32,760 bytes with CID; 0–32,762 without |

**Flag byte** `[ipds-reference-intelligent-printer-data-stream-reference p.106]`:
bit 0 ARQ (Acknowledgment Required) · bit 1 CID present · bit 2 ACK continuation ·
bit 3 long ACK accepted (up to 65,535 bytes vs 256) · bits 4–7 reserved.

The printer replies with an **Acknowledge Reply, reply code `X'D6FF'`**
`[ipds-reference-intelligent-printer-data-stream-reference p.1055]`.

## 3. Self-defining field and triplet

**SDF** `[ipds-reference-intelligent-printer-data-stream-reference p.643, p.644]`:
"Each self-defining field contains a two-byte length field, a two-byte self-defining
field ID, and a data field." The length includes itself.

**Triplet** `[ipds-reference-intelligent-printer-data-stream-reference p.751]`:
"a three-part self-defining variable-length parameter consisting of a length byte, an
identifier byte, and parameter-value bytes."

**Length-range trap**: the MO:DCA triplet format restricts the length to 3–254, but
four IPDS-only triplets allow 2–255 — Group ID `X'00'`, Group Information `X'6E'`,
Linked Font `X'8D'`, Invoke Tertiary Resource `X'A2'`
`[ipds-reference-intelligent-printer-data-stream-reference p.752]`.

**Triplet tolerance**: "Printers ignore any triplet that is not supported and no
exception is reported. If byte 16 or the first byte after a valid triplet is `X'00'` or
`X'01'` (an invalid triplet length), the printer ignores the remaining data within the
optional triplets field."
`[ipds-reference-intelligent-printer-data-stream-reference p.649, p.658]`

### The IPDS triplet registry (Table 57)

`[ipds-reference-intelligent-printer-data-stream-reference p.751, p.752]`

| TID | Name | | TID | Name |
|---|---|---|---|---|
| `X'00'` | Group ID | | `X'8B'` | Data Object Font Descriptor |
| `X'01'` | Coded Graphic Character Set Global ID | | `X'8D'` | Linked Font |
| `X'02'` | Fully Qualified Name | | `X'8E'` | UP3I Finishing Operation |
| `X'4E'` | Color Specification | | `X'91'` | Color Management Resource Descriptor |
| `X'50'` | Encoding Scheme ID | | `X'92'` | Invoke CMR |
| `X'5A'` | Object Offset | | `X'95'` | Rendering Intent |
| `X'62'` | Local Date and Time Stamp | | `X'96'` | CMR Tag Fidelity |
| `X'6E'` | Group Information | | `X'97'` | Device Appearance |
| `X'70'` | Presentation Space Reset Mixing | | `X'9A'` | Image Resolution |
| `X'74'` | Toner Saver | | `X'9C'` | Object Container Presentation Space Size |
| `X'75'` | Color Fidelity | | `X'9E'` | Setup Name |
| `X'79'` | Metric Adjustment | | `X'A2'` | Invoke Tertiary Resource |
| `X'84'` | Font Resolution and Metric Technology | | `X'E0'` | Encrypted Object |
| `X'85'` | Finishing Operation | | `X'EA'` | Encrypted Alternate |
| `X'86'` | Text Fidelity | | `X'FF'` | Triplet Extender |
| `X'88'` | Finishing Fidelity | | | |

*(The corpus's "carrying commands" column interleaves with another column in the text
layer; re-verify per-triplet carrying commands against the source PDF before relying
on them.)*

## 4. IPDS operating states

"The printer must be in the initial state shown for each command to be valid. The
ending state is the state the printer enters after a valid command has been processed."
`[ipds-reference-intelligent-printer-data-stream-reference p.119]`

- **Presentation-object states cannot be entered from home state** — you must already
  be in page, page-segment, or overlay state.
  `[ipds-reference-intelligent-printer-data-stream-reference p.109]`
- **Page / page-segment / overlay / font / code-page / IO-Image-resource /
  object-container-resource states are entered only from home state.**
  `[ipds-reference-intelligent-printer-data-stream-reference p.122]`
- **Metadata must come first inside a state**: "It is invalid to specify a Write
  Metadata Control command sequence after the first non-metadata command within the
  containing state." `[ipds-reference-intelligent-printer-data-stream-reference p.117, p.123]`
- **END is state-conditional**: in IM-Image state only after ≥1 WI; in font state only
  after ≥1 LF; in code page state only after ≥1 LCP; in text / IO-Image / graphics /
  bar code / object-container presentation-object states and in IO-Image-resource /
  object-container-resource / metadata states, END is valid at any time.
  `[ipds-reference-intelligent-printer-data-stream-reference p.122]`
- **LPD is home-state only.** `[ipds-reference-intelligent-printer-data-stream-reference p.242]`

## 5. IPDS "environment" — IPDS's answer to MO:DCA's AEG

"Active Environment Group" is a **MO:DCA** construct; the IPDS Reference uses it only
when contrasting with MO:DCA. In IPDS the environment is an explicit, stateful triple:

> **IPDS environment = LPD values + LFE values + LE values**, scoped to the current
> page/overlay, snapshotted at BO time.

- The **LPD** (Logical Page Descriptor) "establishes the characteristics of the current
  logical page for a subsequently sent page or overlay" — units of measure, logical
  page size, and the initial text-major text conditions. "These values remain in effect
  until the next LPD command is received, unless superseded for a given logical page by
  explicit controls in other commands."
  `[ipds-reference-intelligent-printer-data-stream-reference p.242]`
- At Begin Overlay time "the current environment, that consists of the Logical Page
  Descriptor values, the Load Font Equivalence values, and the Load Equivalence values,
  is saved as a part of the stored overlay definition."
  `[ipds-reference-intelligent-printer-data-stream-reference p.111]`
- "The LPD that is current when a Begin Overlay command is received becomes part of the
  overlay. When this overlay is included on a page, the LPD values stored with the
  overlay redefine the current logical page for the extent of the overlay."
  `[ipds-reference-intelligent-printer-data-stream-reference p.242]`
- Page segments, by contrast, "assume the active environment at the time they are
  included" and "are not independent of the logical page environment"
  `[ipds-reference-intelligent-printer-data-stream-reference p.112, p.60]`

The corpus states the IPDS/MO:DCA correspondence explicitly: "In MO:DCA, the PTD is in
the Active Environment Group (AEG) for the page; in IPDS, the PTD is specified as
initial text-major conditions in the Logical Page Descriptor"
`[ipds-reference-intelligent-printer-data-stream-reference p.1128]`.

## 6. Object containers in IPDS

The IPDS Object Container command set contains nine commands: DORE, DORE2, DDOFC,
DDOR, IDO, RRR, RRRL, WOCC, WOC
`[ipds-reference-intelligent-printer-data-stream-reference p.611]`.

**It is a two-command sequence, not an envelope:**

- `WOCC` (Write Object Container Control) carries the *control* data — object type
  OID, area position, output control — and **causes the printer to enter**
  object-container-resource, page-object-container, or overlay-object-container state.
  `[ipds-reference-intelligent-printer-data-stream-reference p.643]`
- `WOC` (Write Object Container) carries the payload bytes: "Zero or more WOC commands
  follow the WOCC command."
  `[ipds-reference-intelligent-printer-data-stream-reference p.662]`
- The object ends with an `END` command: "Object container data processing ends when
  the printer receives an End command in the object container state."
  `[ipds-reference-intelligent-printer-data-stream-reference p.643]`

**Presentation vs non-presentation**: "The object-type OIDs also indicate whether an
object container is a presentation object or a non-presentation object."
Non-presentation containers are downloaded in home state; presentation containers can
be part of a page/overlay or downloaded in home state and later included by `IDO`.
`[ipds-reference-intelligent-printer-data-stream-reference p.404]`

**Multi-page resource objects**: the reference selects a single paginated object within
the file, using the **Object Offset (`X'5A'`) triplet**; "If there are no Object Offset
(`X'5A'`) triplets specified in a page-state or overlay-state WOCC command, the first
paginated object within the file is selected."
`[ipds-reference-intelligent-printer-data-stream-reference p.660]`

## 7. Complete IPDS command code table

Appendix A Table 70, cross-validated against Table 11
`[ipds-reference-intelligent-printer-data-stream-reference p.1053, p.119]`

| Code | Mnemonic | Name | | Code | Mnemonic | Name |
|---|---|---|---|---|---|---|
| `X'D601'` | MID | Manage IPDS Dialog | | `X'D65A'` | RRR | Remove Resident Resource |
| `X'D602'` | AFO | Apply Finishing Operations | | `X'D65B'` | DDOFC | Deactivate Data-Object-Font Component |
| `X'D603'` | NOP | No Operation | | `X'D65C'` | DDOR | Deactivate Data Object Resource |
| `X'D608'` | SPE | Set Presentation Environment | | `X'D65D'` | END | End |
| `X'D60A'` | ASN | Activate Setup Name | | `X'D65F'` | BPS | Begin Page Segment |
| `X'D60F'` | LFI | Load Font Index | | `X'D66B'` | ICMR | Invoke CMR |
| `X'D619'` | LFCSC | Load Font Character Set Control | | `X'D66C'` | DORE | Data Object Resource Equivalence |
| `X'D61A'` | LCPC | Load Code Page Control | | `X'D66D'` | LPP | Logical Page Position |
| `X'D61B'` | LCP | Load Code Page | | `X'D66E'` | DORE2 | Data Object Resource Equivalence 2 |
| `X'D61C'` | — | Retired item 134 | | `X'D66F'` | DPS | Deactivate Page Segment |
| `X'D61D'` | LE | Load Equivalence | | `X'D67B'` | RPO | Rasterize Presentation Object |
| `X'D61E'` | LSS | Load Symbol Set | | `X'D67C'` | IDO | Include Data Object |
| `X'D61F'` | LFC | Load Font Control | | `X'D67D'` | IO | Include Overlay |
| `X'D62D'` | WT | Write Text | | `X'D67E'` | ISP | Include Saved Page |
| `X'D62E'` | AR | Activate Resource | | `X'D67F'` | IPS | Include Page Segment |
| `X'D62F'` | LF | Load Font | | `X'D680'` | WBCC | Write Bar Code Control |
| `X'D633'` | XOA | Execute Order Anystate | | `X'D681'` | WBC | Write Bar Code |
| `X'D634'` | PFC | Presentation Fidelity Control | | `X'D684'` | WGC | Write Graphics Control |
| `X'D63C'` | WOCC | Write Object Container Control | | `X'D685'` | WG | Write Graphics |
| `X'D63D'` | WIC | Write Image Control | | `X'D688'` | WTC | Write Text Control |
| `X'D63E'` | WIC2 | Write Image Control 2 | | `X'D68A'` | WMC | Write Metadata Control |
| `X'D63F'` | LFE | Load Font Equivalence | | `X'D68B'` | WM | Write Metadata |
| `X'D64C'` | WOC | Write Object Container | | `X'D68F'` | XOH | Execute Order Home State |
| `X'D64D'` | WI | Write Image | | `X'D697'` | SHS | Set Home State |
| `X'D64E'` | WI2 | Write Image 2 | | `X'D69F'` | LCC | Load Copy Control |
| `X'D64F'` | DF | Deactivate Font | | `X'D6AF'` | BP | Begin Page |
| `X'D658'` | DHM | Delete Home-State Metadata | | `X'D6BF'` | EP | End Page |
| `X'D659'` | RRRL | Request Resident Resource List | | `X'D6CE'` | DUA | Define User Area |
| `X'D6CF'` | LPD | Logical Page Descriptor | | `X'D6DF'` | BO | Begin Overlay |
| `X'D6E4'` | STM | Sense Type and Model | | `X'D6EF'` | DO | Deactivate Overlay |
| `X'D6FF'` | ACK | Acknowledge Reply (reply code) | | | | |

Retired command codes: `X'D600'`, `X'D604'`, `X'D60D'`, `X'D614'`, `X'D61C'`, `X'D624'`
`[ipds-reference-intelligent-printer-data-stream-reference p.122]`.

**OC1 subset membership** (Table 50) `[ipds-reference-intelligent-printer-data-stream-reference p.611]`:
of the nine object-container commands, only **WOCC** and **WOC** are in the OC1 subset —
DORE, DORE2, DDOFC, DDOR, IDO, RRR and RRRL are not.

**Metadata command set** (Table 52): DHM (`X'D658'`), WMC (`X'D68A'`), WM (`X'D68B'`) —
all three are in the MO1 subset `[ipds-reference-intelligent-printer-data-stream-reference p.663]`.

## 8. Length rules and the failure taxonomy

| Rule | Value |
|---|---|
| Minimum command length | `X'0005'` without CID, `X'0007'` with CID |
| Maximum command length | `X'7FFF'` |
| Length includes | length field + command code + flag byte + optional CID + data |
| Data field size | 0–32,760 with CID; 0–32,762 without |
| SDF length | 2 bytes, includes itself |
| Triplet length | 1 byte; 3–254 (MO:DCA-defined) or 2–255 (the four IPDS-only triplets) |
| Minimum LPD data field | 43 bytes mandatory; 24/28/32/34/36/38/40/41 optional |

`[ipds-reference-intelligent-printer-data-stream-reference p.106, p.643, p.752, p.242]`

**What makes a stream invalid** `[ipds-reference-intelligent-printer-data-stream-reference p.870, p.920, p.107, p.612, p.658, p.616, p.662, p.644, p.643, p.657]`:

| Situation | Exception ID |
|---|---|
| Bad command code | `X'8001..00'` — "An invalid length on a previous command might have caused the current data to be mistaken for a command." |
| Bad command length | `X'0202..02'` (alternates `X'0203..02'`, `X'80E0..00'`) |
| Command out of sequence / wrong printer state | `X'8002..00'` — "The printer state is invalid or is unsupported for the received command." |
| Data after ARQ | `X'8004..00'` |
| Bad ARQ / ACK-continuation flag use | `X'0204..02'` |
| Unsupported object-type OID in WOCC | `X'020D..02'`, or `X'8002..00'` in the wrong state |
| Duplicate / in-use HAID | `X'020D..16'`; invalid HAID value `X'020D..11'` |
| Missing or inactive secondary resource | `X'020D..10'`; resource unsupported with that data object `X'020D..17'` |
| Object payload invalid | `X'020D..01'` (non-presentation), `X'020D..05'` (presentation), `X'025D..ee'` (CMR) |
| WOCC SDF structural error | `X'020B..05'` |
| WOCC missing required data | `X'0205..01'` |
| SDF length ≠ sum of the SDF lengths within an IDO/WBCC/WGC/WIC2/WMC/WOCC/WTC | `X'0202..02'` |
| Invalid UP³I Print Data Format ID | `X'027E..00'` |

Each exception carries an **action code** plus an Alternate Exception Action and a Page
Continuation Action. After a NACK: "the printer and the communications network … ensure
that the next IPDS command processed subsequent to a given NACK, is the beginning of
the host's response to that NACK."
`[ipds-reference-intelligent-printer-data-stream-reference p.107]`

## 9. Trap checklist

1. **WOCC's self-defining field order is fixed: OCAP → OCOC → OCDD.** OCDD is required.
   Violation → `X'020B..05'`.
2. **Only Anystate commands may appear between concatenated WOC commands.**
3. **Never enter a presentation-object state from home state.**
4. **Metadata must come first inside a state.**
5. **END is state-conditional** (see §4).
6. **DORE/DORE2 must precede the object that uses the secondary resource**, and the
   secondary resource "must be activated before they are used".
   `[ipds-reference-intelligent-printer-data-stream-reference p.658]`
7. **Only one WBC per encrypted bar code object** → `X'8007..00'`.
8. **Presentation object containers cannot span pages.**
9. **Multi-page resource activation is whole-file**: "an activation of single pages or
   single images within the file is not possible."
   `[ipds-reference-intelligent-printer-data-stream-reference p.172]`
10. **An empty object container** is a WOCC followed by an End with no WOC between — it
    can be used to colour or shade a rectangle without presenting data. But if it
    contains only empty WOCs and the type needs data, `X'020D..01'`/`X'020D..05'`.
11. **Overlay capture**: omit OCAP/OCOC from a home-state WOCC so the object is captured
    with known defaults, and always override on the later IDO.
12. **Encrypted object containers**: the *entirety* of the data is encrypted first, then
    split across WOC commands; on receipt the WOC data is concatenated and then
    decrypted as a whole.
13. **Only the last triplet of a given type wins** — the specification states this
    per command, not as one global sentence:
    - `X'4E'` (RPO): "If multiple Color Specification (X'4E') triplets are specified, the
      last one is used and the others are ignored."
      `[ipds-reference-intelligent-printer-data-stream-reference p.268]`
    - `X'9A'` and `X'9C'` (RPO): "If more than one … triplet is specified, the last one is
      used and the others are ignored."
      `[ipds-reference-intelligent-printer-data-stream-reference p.270]`
    - `X'91'` and `X'02'` (WOCC): "the last is used and the others are ignored."
      `[ipds-reference-intelligent-printer-data-stream-reference p.658]`
    - `X'E0'` and `X'EA'` (WTC): "only the last specified triplet of each type will be
      used and additional X'E0' or X'EA' triplets are ignored."
      `[ipds-reference-intelligent-printer-data-stream-reference p.512]`
    - and **Triplet Extender `X'FF'` triplets must immediately follow the `X'E0'` triplet
      they extend**, and only those following the *last* `X'E0'` are used
      `[ipds-reference-intelligent-printer-data-stream-reference p.512]`
14. **Invoke CMR (`X'92'`) on WOCC is not used with data object resources included via
    IDO** — "Because Invoke CMR (X'92') triplets contain a HAID, these triplets should not
    be stored with a captured resource."
    `[ipds-reference-intelligent-printer-data-stream-reference p.650]`
15. **PreRIP constraint**: "A preRIPped presentation object will be printed only if the
    CMRs and rendering intent used during preRIP match those selected while processing
    the IDO command."
    `[ipds-reference-intelligent-printer-data-stream-reference p.557]`
16. **Units of measure**: "The IPDS architecture requires all printers to support 1440ths
    in all commands that specify units of measure… Using 1440ths, however, limits
    addressability to slightly more than 22 3/4 inches." Printers supporting larger
    presentation spaces must also support 240ths.
    `[ipds-reference-intelligent-printer-data-stream-reference p.105]`
17. **LPD bytes 4–5 (YUPUB) must equal bytes 2–3 (XUPUB)**; otherwise exception ID
    `X'0206..05'` exists.
    `[ipds-reference-intelligent-printer-data-stream-reference p.243, p.514]`
18. **`X'FFFF'` means different things in different extent fields — check which one
    you are writing.**
    - **OCOC** (WOCC), bytes 7–8 *Xoa extent* / 9–10 *Yoa extent*: `X'FFFF'` = "Use the
      LPD value" — "A value of `X'FFFF'` causes the printer to use the Xp extent and the
      Xp unit base and units per unit base of the LPD command that is current when this
      object is printed in a page or overlay."
      `[ipds-reference-intelligent-printer-data-stream-reference p.647, p.648]`
      The same wording is used for the text (`p.509`), IO-Image (`p.549`), graphics
      (`p.578`) and bar code (`p.602`) object-area extent fields.
    - **DOOC** (IDO), bytes 7–8 *Xoa extent* / 9–10 *Yoa extent*: the **opposite** — "X'FFFF'
      is a special value that specifies that the Xoa extent and the unit base and units
      per unit base **from the OCOC or IOC in the object** are used for this parameter."
      `[ipds-reference-intelligent-printer-data-stream-reference p.628, p.629, p.630]`
    - **RPO** override fields, bytes 10–11 / 12–13: `X'FFFF'` = "this parameter has not
      been specified" — a third meaning again.
      `[ipds-reference-intelligent-printer-data-stream-reference p.267]`
    - If the OCOC is omitted altogether the default is "Xoa extent = Xp extent, Yoa
      extent = Yp extent"
      `[ipds-reference-intelligent-printer-data-stream-reference p.647]`

## 10. Not confirmed / open questions

- The **per-command legal length lists**, the **XOH-OPC self-defining field negotiation
  surface**, and the **complete command-set/state table (Table 11)** are in
  `research/01-ipds-transport.md` §3.8, §3.9, §3.10 with full citations.
- The four task recipes (wrap MO:DCA data → re-encode as IPDS commands; declare a
  resource; build a minimal end-to-end job; negotiate IPDS/object-container versions)
  are in the research file §4.1–4.4.
- **UP3i (third-party IPDS extensions)** — the extension mechanism and its triplets
  (`X'8E'` UP3I Finishing Operation, `X'AF'` etc.) — is in the research file §2.4 and
  the UP3i document itself.
