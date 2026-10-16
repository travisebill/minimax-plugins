# Styles — the token contract and the catalog

The page shell is style-agnostic. **All visual personality lives in one `:root` block.**
Swap that block and the entire page re-skins — components never change.

This file has three parts: the token contract (what you may and may not write in CSS),
the catalog (ten ready `:root` blocks), and the selection gate (how the user picks).

---

## 1. Why style is a decision, not a default

A dark navy page with mint accents and glowing 3D renders reads as *technical and
cinematic*. That is a strong choice, and it is **wrong for most topics**:

| Topic | What the default style does to it |
|---|---|
| A medical mechanism | Adds spectacle to something the reader must *trust* |
| A statistical / economic explainer | Wastes the page on atmosphere; the data is the content |
| A political result | Imparts a "cool tech startup" tone to contested ground |
| A historical event | Anachronistic — glowing volumetric light reads as sci-fi |
| A how-to / practical guide | Decorative 3D actively competes with the instruction |

Matching the register to the subject is not decoration. It is the difference between
"this looks nice" and "this is the right kind of page for this thing."

**The corollary that costs the most:** the style also drives the *image prompt*. You
cannot restyle after generation without regenerating every image. So the gate has to
happen **before** step 3, not after.

---

## 2. The token contract

Two layers, and **the split matters**. A style author edits only layer 1.

**Layer 1 — base tokens, per style.** This is the only thing a catalog style defines.

```css
:root{
  /* surfaces, light → dark */
  --bg:      /* page background            */
  --bg2:     /* inset / secondary fill     */
  --card:    /* panel surface              */
  --line:    /* hairline border            */
  --line2:   /* emphasised border          */

  /* text, strong → weak */
  --txt:     /* primary                    */
  --txt2:    /* body secondary             */
  --txt3:    /* captions, axis labels      */

  /* five semantic accents — always exactly five, in this order.
     They are ROLES, not colours. Components must not care which hue
     is which, so a style may re-map them freely. */
  --mint:    /* primary interactive, "hot" state      */
  --coral:   /* alert, negative, the other party     */
  --amber:   /* caution, third series                */
  --peri:    /* fourth series                         */
  --sky:     /* fifth series                          */

  --on-accent:/* text on top of a --mint fill         */

  /* non-colour personality */
  --radius:      /* card / image corner radius */
  --font-display:/* headings                  */
  --font-body:   /* body                      */
  --font-mono:   /* numerals, tables, codes   */
}
```

**Layer 2 — derived tokens, shared, written once in `components.md` §0.** They are a pure
function of layer 1, so a style must **never** redefine them:

```
--mint-a12 --mint-a30 --coral-a30 --amber-a10
--shade --shade-deep --veil --txt-a05 --txt-a12
```

This split is not tidiness. An early draft had each style define its own derived tokens,
and **9 of 10 styles silently dropped 6 of them** — the topbar, tooltip, lightbox and
table hover all fell back to `transparent` and vanished, with no console error and no
failing assertion. Anything a style cannot express is added to layer 2, not to layer 1.

### Rules

1. **Five accents, always.** A component hardcoded to `var(--mint)` still works if the
   style paints `--mint` red. Never add `--mint2` or drop `--sky` — a missing token is
   an unstyled element that no assertion will catch.
2. **Semantic data colour is your call, not the catalog's.** When a topic has parties,
   species, or teams, override `--mint`/`--coral` to the *conventional* colours for that
   domain (blue/green for Taiwan politics, say) so the page reads correctly to someone
   who already knows the subject. Note the override in the final message.
3. **Never hardcode a hue in a component.** `rgba(72,224,189,.06)` is a bug — it is one
   page's mint, invisible to the style system. Use `--mint-a12` / `--shade`.
4. **`--txt` must clear 7:1 against `--bg`; `--txt3` at least 4.5:1.** Light styles fail
   this most often. Check, do not eyeball.
5. **`--on-accent` is a separate token** because inverting is not automatic: a pale
   yellow accent needs dark text, a deep blue one needs light.
6. `color-mix()` needs Chrome 111 / Safari 16.2 / Firefox 113. If you must support older
   browsers, write the resolved rgba values into the style block instead — do not revert
   to hardcoding per component.
7. **Never animate anything that changes glyph width.** Changing `font-weight` on a CJK
   label reflows it (bug class #2 in SKILL.md). State changes are colour only.

---

## 3. The selection gate

The user decides. This is a **blocking** step — unlike the angle set, which is not.
The reason is asymmetry of cost: a weak angle set is fixed by editing text, but the
wrong style means regenerating every image and rewriting the look. Ask once, early.

**Skip the gate** if the user already signalled a preference ("dark and serious",
"like a newspaper", "不要再用那種 3D"), or said "你決定" / "you pick".

### How to ask

Present **2–3 candidates**, never the whole catalog, and always include a recommendation.
Each candidate carries:

- name + one line of character
- **four actual hex swatches** — this is a visual decision; make it answerable in one glance
- one sentence on why *this topic* suits it
- your recommendation, marked

Then stop. One question. A one-word answer, a name, or "你決定" unblocks you.

### Worked shape

> 三個方向，你挑一個（或直接說「你決定」我就用推薦的）：
>
> **A. Ledger 帳本** — 米白紙底、墨黑字、等寬數字、單一紅色警示
>  `#F7F4ED` `#1A1A1A` `#B4462F` `#6B7A8F`
> 適合：這題的重量在數字本身，觀眾要能逐格查證，不是要被氣氛帶走。
>
> **B. Broadsheet 報紙** — 高對比、粗規則線、襯線標題、雙方色碼
>  `#FCFCFA` `#111111` `#2B5FC7` `#0E8A5F`
> 適合：選舉題材，紙本新聞的公信力與中立感。
>
> **C. Telemetry 儀表** — 深底、霓虹數據、等寬字、大量運動感
>  `#0A0E14` `#E6EDF5` `#FFC44D` `#48E0BD`
> 適合：像賽車／即時戰況那種速度感。
>
> **我的推薦是 B**，因為這題的核心是「兩份民調打架」，需要的是讀者信任你的中立，而不是覺得這很酷。

### The gate is cheap; skipping it is not

Ask **before** step 3 (generation). After step 3 the images already exist in one look.

---

## 4. The catalog

Each block is a **complete `:root` override**. Paste over the defaults wholesale.

> Fonts: `Noto Sans TC` / `Noto Serif TC` / `Noto Serif` / `Space Grotesk` /
> `IBM Plex Mono` / `JetBrains Mono` are all on Google Fonts. A display face that lacks
> CJK coverage will silently fall back for Chinese text — check the actual render.

---
### A. Clinical — biology, medicine, mechanisms

Calm authority. The reader is being asked to trust you with their body.

```css
:root{
  --bg:#F4F7F8; --bg2:#E8EFF1; --card:#FFFFFF; --line:#D3DFE3; --line2:#AFC3C9;
  --txt:#16262B; --txt2:#4A6169; --txt3:#5F7187;
  --mint:#0E7C86; --coral:#C0433A; --amber:#B7791F; --peri:#5B5BD6; --sky:#2E7D5B;
  --on-accent:#FFFFFF;
  --radius:8px;
  --font-display:"Noto Serif TC",Georgia,serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `clean scientific diagram, white background, restrained teal
and slate linework, flat vector anatomy, even clinical lighting, high detail, no glow`
**Avoid:** volumetric haze, neon glow, dark backgrounds, anything that looks like a movie poster.

---
### B. Ledger — statistics, economics, data-heavy explainers

Paper and ink. The chart *is* the design; decoration is a tax on the reader.

```css
:root{
  --bg:#F7F4ED; --bg2:#EFEADC; --card:#FFFDF7; --line:#DCD6C4; --line2:#B9B09A;
  --txt:#1A1A1A; --txt2:#4C4A44; --txt3:#6F6E6B;
  --mint:#1F6F5C; --coral:#B4462F; --amber:#8A6D1F; --peri:#4A4E8C; --sky:#2B6E8F;
  --on-accent:#FFFFFF;
  --radius:4px;
  --font-display:"Noto Serif TC",Georgia,serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `flat editorial data illustration, warm off-white background,
muted ink linework, no gradients, screenprint texture, high detail`
**Avoid:** 3D render, glow, photoreal, anything with perspective drama.

---
### C. Broadsheet — politics, elections, contested ground

Print lineage. High contrast, heavy rules, and **no visual allegiance**.

```css
:root{
  --bg:#FCFCFA; --bg2:#F0F0EC; --card:#FFFFFF; --line:#D8D8D2; --line2:#9A9A92;
  --txt:#111111; --txt2:#3D3D3A; --txt3:#6E6E68;
  --mint:#1F3D8F; --coral:#0E6B4F; --amber:#8A5A00; --peri:#6A2D7A; --sky:#1F6F8F;
  --on-accent:#FFFFFF;
  --radius:2px;
  --font-display:"Noto Serif TC",Georgia,serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `newspaper-infographic aesthetic, flat vector, off-white
background, two-colour duotone, bold geometric shapes, screenprint grain`
**Avoid:** candidate portraits, party logos, flags, anything implying endorsement.
For a contested topic **default to the neutral accent set** unless the user asks
otherwise; use `--mint`/`--coral` only for the two sides, and only if the mapping is
conventional in that domain.

---
### D. Telemetry — sport, races, live competition, speed

Motion and precision. Numerals do the talking.

```css
:root{
  --bg:#0A0E14; --bg2:#10161F; --card:#141B26; --line:#1E2836; --line2:#2E3D4F;
  --txt:#E6EDF5; --txt2:#93A5B8; --txt3:#7B7D80;
  --mint:#FFC44D; --coral:#FF5C5C; --amber:#48E0BD; --peri:#8B7BFF; --sky:#4DD0E1;
  --on-accent:#0A0E14;
  --radius:6px;
  --font-display:"Space Grotesk","Noto Sans TC",sans-serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"JetBrains Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `dark telemetry dashboard aesthetic, high-contrast neon data
on near-black, motion trails, precision grid, high detail`
**Avoid:** soft pastel anything. This style's whole identity is contrast.

---
### E. Archive — history, conflict, long timescales

Distance and gravity. The material age of the page is the point.

```css
:root{
  --bg:#F2EDE3; --bg2:#E7E0D2; --card:#FBF7EE; --line:#D6CCB6; --line2:#B3A689;
  --txt:#2B241A; --txt2:#5A4F3E; --txt3:#746956;
  --mint:#7A5C2E; --coral:#8C3B2E; --amber:#A08040; --peri:#4A4A6B; --sky:#4A6B6B;
  --on-accent:#FBF7EE;
  --radius:3px;
  --font-display:"Noto Serif TC",Georgia,serif;
  --font-body:"Noto Serif TC",Georgia,serif;
  --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `aged archival illustration, sepia and muted ochre, paper
texture, engraved linework, documentary plate, high detail`
**Avoid:** neon, sci-fi volumetrics, saturated primaries.

---
### F. Blueprint — engineering, systems, architecture, infrastructure

Schematic lineage. Everything is a drawing on a technical sheet.

```css
:root{
  --bg:#0B1B33; --bg2:#0F2444; --card:#102A50; --line:#1C3D6E; --line2:#2B5490;
  --txt:#DCE9F7; --txt2:#94B2D4; --txt3:#6A87AC;
  --mint:#4DD0E1; --coral:#FF8A5B; --amber:#FFD166; --peri:#9B8CFF; --sky:#48E0BD;
  --on-accent:#04121F;
  --radius:4px;
  --font-display:"Space Grotesk","Noto Sans TC",sans-serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"JetBrains Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `technical blueprint schematic, white linework on deep blue,
orthographic projection, dimension lines, drafting style, high detail`
**Avoid:** photographic, organic, soft-focus. Keep it drawn, not shot.

---
### G. Field guide — nature, geology, climate, ecology

Naturalist tradition. Illustrated-plate, not cinematic.

```css
:root{
  --bg:#FAF7F0; --bg2:#F0EADC; --card:#FFFFFF; --line:#DED5C2; --line2:#BCAF95;
  --txt:#26332A; --txt2:#51604F; --txt3:#687463;
  --mint:#3D6B4A; --coral:#A8562F; --amber:#96762A; --peri:#5B5A8A; --sky:#2F6A7A;
  --on-accent:#FFFFFF;
  --radius:6px;
  --font-display:"Noto Serif TC",Georgia,serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `natural history plate illustration, muted botanical greens,
hand-drawn lithograph texture, soft natural light, high detail`
**Avoid:** neon, dark voids, hard sci-fi geometry.

---
### H. Gallery — art, music, film, culture, design

The work gets the room. Whitespace is the composition.

```css
:root{
  --bg:#FDFDFC; --bg2:#F2F1EE; --card:#FFFFFF; --line:#E6E4E0; --line2:#C9C6C0;
  --txt:#141414; --txt2:#55534F; --txt3:#75726D;
  --mint:#141414; --coral:#C2452D; --amber:#B07D2B; --peri:#5A4FCF; --sky:#2A6F7F;
  --on-accent:#FDFDFC;
  --radius:0px;
  --font-display:"Noto Serif TC",Georgia,serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `gallery print aesthetic, generous negative space, soft even
light, muted tonal range, high detail`
**Avoid:** dense dashboards, chart junk, multiple competing accent hues. If the page
needs five charts, **this is the wrong style** — use Ledger.

---
### I. Workbench — practical how-to, process, setup, DIY

Utilitarian and warm. Instruction first, everything else gets out of the way.

```css
:root{
  --bg:#FAF9F6; --bg2:#F0EEE7; --card:#FFFFFF; --line:#E0DDD3; --line2:#BFBBAE;
  --txt:#23231F; --txt2:#51504A; --txt3:#737068;
  --mint:#1F6F5C; --coral:#B4462F; --amber:#A0781E; --peri:#4C4E93; --sky:#2A6C8A;
  --on-accent:#FFFFFF;
  --radius:10px;
  --font-display:"Noto Sans TC",system-ui,sans-serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `clear instructional illustration, flat vector, bright even
lighting, neutral background, diagram clarity, high detail`
**Avoid:** cinematic lighting, dark backgrounds, mood. Mood is a distraction from a step.

---
### J. Plate — abstract theory, mathematics, philosophy

Typeset like a paper. Hairlines and margins do the work.

```css
:root{
  --bg:#FBFBF9; --bg2:#F0F0EC; --card:#FFFFFF; --line:#E2E2DC; --line2:#B8B8B0;
  --txt:#17171A; --txt2:#4A4A52; --txt3:#72727C;
  --mint:#2A2A2E; --coral:#C0392B; --amber:#9A7B18; --peri:#4B3F9E; --sky:#206A80;
  --on-accent:#FBFBF9;
  --radius:2px;
  --font-display:"Noto Serif TC",Georgia,serif;
  --font-body:"Noto Serif TC",Georgia,serif;
  --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}
```

**Image prompt fragment:** `minimal geometric diagram, monochrome line work on white,
single accent hue, generous margins, precise construction lines`
**Avoid:** illustration-for-its-own-sake. An abstract topic rarely needs a literal
picture; a construction diagram beats a stock "concept" image.

---

## 5. Topic → style, fast

| If the topic is… | Reach for | Notes |
|---|---|---|
| biology, medicine, physiology | **Clinical** | |
| statistics, economics, data | **Ledger** | |
| elections, politics, policy | **Broadsheet** | override accents to the conventional party colours |
| sport, race, live result | **Telemetry** | |
| history, war, long arc | **Archive** | |
| engineering, systems, infra | **Blueprint** | |
| nature, geology, climate | **Field guide** | |
| art, music, film, design | **Gallery** | pick a different style if it needs many charts |
| how-to, setup, process | **Workbench** | |
| maths, theory, philosophy | **Plate** | |

When the mapping is not clean, **ask** — that is what the gate is for. A page that is
two topics at once (「量子力學的經濟學」) usually wants the *reader-facing* one.

## 6. Hybrid and overrides

Two legitimate moves:

- **Accent override** — take a catalog style, remap `--mint`/`--coral` to domain
  conventions. This is the recommended fix for party/team/species colour.
- **Full custom** — write a new `:root` from scratch, keeping the token names and all
  five accents. Then **append it to this catalog** so it is reusable next time.

Never introduce a token that is not in the contract. If you need a sixth data series,
that is a signal the visualisation is over-specified — split the view.

## 7. Anti-patterns

- **Re-skinning after generation.** Style must be settled before step 3. The images
  carry the style; you cannot recolour them with CSS.
- **A dark style for a topic about trust, health, or money.** Darkness reads as
  "brochure", not "authoritative".
- **Five accents all at full saturation.** If `--mint`, `--coral`, `--amber`, `--peri`
  and `--sky` are all fighting, the page has no focal point. Most of them should be
  near-idle.
- **Changing only the palette and calling it a style.** Type, radius and density are
  what separate Ledger from Clinical at a glance.
- **A style that fights the interaction budget.** Gallery's zero radius and huge type
  space look wrong on a scrubber with a dense readout; pick a style that the
  *controls* can live in.
