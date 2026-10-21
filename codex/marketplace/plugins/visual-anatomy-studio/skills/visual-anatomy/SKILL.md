---
name: visual-anatomy
description: |
  Build a single-file, multi-perspective interactive HTML explainer on any topic and
  deploy it to a public URL. Chooses a visual style that matches the subject with the
  user (10 catalogued styles, from clinical to broadcast), researches current data, and uses tools available in the current host to produce
  illustrations, video, music and narration. It wires clickable hotspots,
  drag comparators, scrubber timelines and a scale map of the "lenses" (viewpoints).
  Trigger phrases: "視覺解剖", "像新冠那個網站", "多視角互動網站", "用互動的方式解釋",
  "做成可互動的網頁來解釋", "visual anatomy of", "interactive explainer for",
  or a bare topic noun when the user has just praised a previously built one of
  these sites. Do NOT use for: a single chart or diagram request, a slide deck,
  a written report with no interactive requirement, or a plain factual question
  that one paragraph answers.
---

# Visual Anatomy

Read [Codex runtime guidance](../../CODEX.md) before using this skill. Resolve bundled skills and resources relative to this installed package.

Build one deliverable: a **single self-contained HTML file**, deployed, that explains one
topic from several distinct viewpoints — where the reader *drags, clicks, scrubs and
switches* rather than reads.

The reader's stated principle: **visual + interactive beats text**. When choosing between
adding a paragraph and adding an interactive element, add the interactive element. Text
is still written — it is just collapsed by default and one click away.

## Inputs to collect

Required — take from the request, do not re-ask:
- **Topic**. If the user gave a bare noun, that is the topic.

Optional — infer, and state the inference in the final message rather than asking:
- Language of the page (mirror the user's language; default to Traditional Chinese)
- Whether to deploy (if they said 給我網址 / 上線 / make it a website, that is consent;
  otherwise build locally, show it, and offer deployment)
- **Style** — never inferred silently. Propose 2–3 and ask (see step 2). If the request
  already carries a visual direction ("dark and serious", "像報紙"), take it and skip
  the gate.

If the topic is ambiguous enough that different readings produce *materially different
angle sets* (e.g. "Apple" — company vs product vs fruit), pick the most likely reading,
state it in one line, and build. They can redirect after seeing it.

## Procedure

### 1. Fix the angle set before researching (2 minutes, do it in your head)

The angle set is the whole product. A weak set cannot be rescued by good visuals. Write
5–7 viewpoints that are **genuinely different in kind**, not the same topic at different
zoom levels. Useful shapes:

- **spatial/scale ladder** — the same object from room → molecule
- **mechanism** — how it actually happens, step by step
- **actor's-eye** — what one participant experiences, in order
- **comparison** — vs the alternative / vs baseline / vs itself over time
- **outcome** — what it costs, who it affects
- **state of play** — where things stand *today*, with a date

Publish this list in the page itself (see the scale map below) and repeat it in the final
message. Do not stop and ask for approval — a visible, editable angle list is faster
feedback than a blocking question.

### 2. Choose the style — and let the user choose it

**A dark navy page with mint accents and glowing 3D renders is not a neutral default. It
is a strong choice that is wrong for most topics** — it adds spectacle to things the reader
is supposed to *trust*, buries data under atmosphere, and gives politics a "cool tech
startup" tone. Register has to match the subject.

This step is **blocking**, unlike step 1, and the asymmetry is the reason: a weak angle set
is repaired by editing text, but the wrong style means regenerating every image and
rewriting the look. Ask once, early, before anything is generated.

1. Classify the topic → pick **2–3 styles** from the catalog in `references/styles.md`
   (the `Topic → style` table in §5 is the fast path).
2. Show each candidate with **four actual hex swatches** — this is a visual decision, so
   make it answerable at a glance, and one sentence on why *this topic* suits it.
3. Mark your recommendation and explain the reasoning in one clause.
4. **Stop and ask.** One question; the answer is a name or 「你決定」.

Skip the gate if the user already signalled a preference ("dark and serious", "像報紙",
"不要再用那種 3D") or said "you pick". Then record the choice in the final message, along
with any **accent override** — for a political page, remap `--mint`/`--coral` to the
conventional party colours rather than shipping the catalog default.

### 3. Research, and pin the data to a date

Search for current figures. Every number that appears on the page must be traceable to a
source you actually retrieved — put a `## Sources` section at the bottom with the URLs.

Record an **as-of date** and surface it in the page header. This is what separates a page
that will be trusted next month from one that will silently rot. When sources disagree,
say so on the page rather than picking whichever is convenient.

Where a number is an estimate, model output, or a schematic, **label it on the page**
("示意模型 · 非實測"). Fabricated precision is worse than an honest range.

### 4. Route generation to tools available here

Before generating media, inspect the current tool catalog and load the relevant installed
provider skill. `mcode-tools` is one possible provider, not a required dependency. Choose a
provider whose live tools support the requested asset and the selected visual style. Batch
images according to that provider's current request limits.

When MiniMax Design MCP is available and the user has not selected another provider:

1. Call `list_projects` first. Select a suitable project with `open: true` and call
   `open_project` with its returned `projectId` before other project operations. If no
   suitable MiniMax project is open, use another compatible provider when available unless
   the user specifically requires MiniMax; otherwise ask the user to open a project.
2. Call `capability_list` for the required media operations and `capability_get` for each
   selected capability. Treat the live parameter schema and model rules as authoritative.
3. Submit through `execute` only when prompts and references are ready. Wait on the same
   `taskId` with `task_wait` until completion; a timeout is not a reason to submit duplicate
   work.
4. If a task requests cost approval, show the quoted amount and wait for the user's
   explicit approval before calling `confirm_cost`.
5. Retrieve finished outputs with `get_output` and the returned `versionId`, then copy
   assets into the page's local folders. Do not construct download URLs from resource IDs.

For other providers, follow their live generation, cost, wait and retrieval contracts. Do
not assume model names, formats, duration limits or latency from a different computer.
Every image and video prompt must still carry the user's chosen style fragment; style is
baked into the pixels and cannot be repaired with CSS.

### 5. Build the page

Single file: inline `<style>` and `<script>`, with assets in sibling `img/`, `video/` and, when generated, `audio/` folders next to `index.html`. No frameworks, no CDN JS. Google Fonts is fine (it is a stylesheet, and the page degrades to system fonts offline).

Audio players must have visible controls and must not autoplay. Include a transcript for narration. Retrieve generated media locally before embedding it; do not rely on temporary provider URLs.

Copy component code from `references/components.md` rather than rewriting it. It is
already free of the six bugs listed below.

**Style application is one block.** Paste the chosen style's `:root` from `styles.md` over
the default in `components.md` §0 and change nothing else. Components reference tokens
only — that is the contract that makes the swap total. If you find yourself hardcoding a
hue, you are about to break the next style anyone picks.

Standard shell: sticky top bar with lens tabs → scale map showing where each lens sits →
one panel per lens → a compact Q&A / sources section → footer.

Interaction budget — a page feels thin if it has fewer than these:
- lens switcher that also **scrolls to** the panel
- at least one **draggable or scrubbable** control
- at least one **generated illustration** with 3+ clickable hotspots
- one **comparison** the reader manipulates (slider, or A/B toggle)
- long text collapsed to ~2 lines behind a click

**Check the style can actually host the controls.** Gallery's zero radius and huge type
space look wrong on a dense scrubber readout; if a style fights the interaction budget,
pick a different style — not different components.

### 6. Verify visually before deploying

Non-negotiable, and it is where every real bug has been found. Run
`references/verify.md` — it is a ready Playwright harness. It must assert on **element
position inside the viewport** and on **pixels changing**, not on class names or text
content.

> **The lesson that cost the most:** asserting "element has class `.on` and contains text"
> passes while the element sits 3000px above the viewport, invisible to the user. DOM state
> correct ≠ user can see it. Every overlay, tooltip, modal and tooltip must be screenshot-
> verified or boundary-asserted at least once.

Eight bug classes this exact architecture has actually produced — check each explicitly:

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | Rotating 3D object drifts off-canvas | CSS `transform: rotate()` on a 2D projection of a 3D point set | Project properly per frame with a rotation matrix; recompute depth, length, opacity; hide back-facing points |
| 2 | Labels "jump" when selected | CSS `font-weight` change alters CJK glyph width | Hold weight constant, change colour only; never animate a dimension that affects layout |
| 3 | A control has zero effect on the readout | Normalisation constant built from the same variable it should be independent of (`score = D/DL` where `DL` also contains `D`'s input) | The reference constant must be a **fixed literal**; verify by moving each control and checking the number actually moves |
| 4 | Drag handle moves, image does not | Both layers of a comparator are the same image — the composite never changes | A before/after comparator needs **two different source images** |
| 5 | Click on a hotspot appears to do nothing | Hover already opened it, and click toggles "already open" → closes it | Separate states: hover = preview, click = pin |
| 6 | Overlay renders off-screen | `position:absolute` element positioned with coordinates relative to a different ancestor | `position:fixed` + `getBoundingClientRect()` viewport coordinates |
| 7 | A component stays dark on a light style | `rgba()`/`#hex` hardcoded in a component rule instead of a token | Only tokens in components; raw hue = the style system is already leaking |
| 8 | Text unreadable on the chosen style | `--txt3` or `--on-accent` never contrast-checked | Run the contrast assertions in `components.md` §0; ≥7:1 for `--txt`, ≥4.5:1 for `--txt3` and `--on-accent` on `--mint` |

Two more that cost time: hidden panels report `offsetTop === 0`, so scroll targets must
use `getBoundingClientRect().top + scrollY`; and a grid item stretches to its tallest
sibling by default, so mixed-height side-by-side visuals need `align-items:start`.

### 7. Deploy

`website_deploy` with `path` = the folder containing `index.html`, `source_path` = the
same folder. The tool publishes a **publicly accessible** URL and archives the source
privately. Confirm first if the user has not already asked for a URL, and tell them the
link is public. Verify after deploying with an HTTP check on the page and on 2–3 assets, including audio
or video when present — a 200 on the page alone does not prove the media resolved.

## Output contract

1. A deployed URL, plus the local file path
2. The angle set used, so the user can redirect
3. **The style used, and why it was the right register for this topic** — plus any accent
   override and its justification
4. The as-of date of the data
5. Which media were produced and which provider supplied them, plus any requested media
   that could not be generated in this environment
6. What was verified and what remains unverified (be explicit; never imply you tested
   something in a browser you could not actually reach or listened to audio you did not hear)

## Failure handling

- **Angle set feels weak** → reshape the list and rebuild the page shell; the shell is
  cheap, the research is the expensive part, so do not re-research.
- **No catalog style fits** → take the closest one and write a custom `:root` keeping the
  token contract, then append it to `styles.md` so it is reusable next time. Do not
  bolt colour onto a component.
- **The user rejects every candidate** → ask what the page should *feel* like, or offer
  the polar extremes (Gallery vs Telemetry) and let them pick a direction.
- **A style contrast check fails** → fix the palette, do not ship it. A light style that
  fails 4.5:1 is a broken page, not a stylistic opinion.
- **Generated images come back in the wrong style** → regenerate with a stronger style
  clause. Style is in the pixels; CSS cannot rescue it.
- **A source is unavailable or paywalled** → use a secondary authoritative source and say
  on the page which was used. Do not fill a gap from memory.
- **Image generation returns anatomically or factually wrong art** → regenerate with a
  corrected prompt, and do not place a hotspot on the misleading part. Check the output
  image before wiring hotspots onto it.
- **Video generation fails or times out** → ship the page without it. The static
  illustrations carry the content; the video is an enhancement, not the load-bearing part.
- **A requested media type has no compatible tool in this environment** → continue with the supported assets and state which output is missing; do not silently substitute another medium.
- **A control cannot be made to work correctly** → remove it and state that it was removed.
  A broken interactive element costs more trust than its absence.
- **The user reports "it doesn't respond"** → reproduce it, screenshot it, and read the
  computed styles before theorising. Then verify the fix the same way.

## Examples

**Input:** `視覺解剖 F1 新加坡站排位賽結果`
**Style:** Telemetry — dark, high-contrast, mono numerals. A result page about speed
should look fast. Not offered to the user as an open choice unless they ask: sport maps
cleanly to one style, so propose it with one alternative and let them redirect.
**Output:** 6 lenses (排位成績 / 車手三大段落 / 輪胎策略 / 車隊對比 / 為什麼是這個成績 /
明日預測) with a scale map ordered from track scale down to tyre-compound scale, a
scrubbable lap-time delta chart, per-driver sector comparison toggles, a generated
circuit aerial, and hotspots on the qualifying classification table.

**Input:** `照新冠那個網站的做法做血管內皮的致病機制`
**Style:** Clinical — light, restrained, flat anatomical diagram, no glow. The previous
version of this page was the dark cinematic default; that is exactly the register mistake
this step exists to prevent. Glowing volumetrics on a page explaining blood-vessel damage
reads as marketing a disease.
**Output:** lenses become 空氣→血管內皮→補體活化→微血栓→器官後遺症; a comparison slider
shows healthy vs damaged endothelium using **two separately generated images**; sources
pinned to the retrieval date.

**Input:** `2026 台北市長選舉`
**Style:** Broadsheet, with an **accent override** — `--mint` → `#1F3D8F`,
`--coral` → `#0E6B4F`, so the two parties read in their conventional blue/green rather
than the catalog's navy/teal. The override is stated in the final message, because in a
contested topic an unexpected colour assignment is itself a claim.
**Output:** 7 lenses (票倉解剖 / 選票機制 / 選民結構 / 民調解剖 / 雙方對決 / 爭議現場 /
翻盤條件), an interactive 12-district map, a scrubbable six-poll timeline that shows the
polls disagree, and a scenario model — with sources pinned to the retrieval date and the
page flagged as permanently stale after 11/28.

## References

- `references/styles.md` — **the token contract, the ten-style catalog, and how to run the
  style gate.** Read before writing any CSS.
- `references/components.md` — copy-paste component code (stage, hotspot, comparator,
  player, scale map, lightbox, text collapse) and their CSS. All tokenised.
- `references/imagery.md` — per-style image/video prompt blocks, aspect ratios, compression
- `references/audio.md` — provider-adaptive music, narration, custom voice and sound workflow
- `references/verify.md` — Playwright verification harness and assertion recipes

