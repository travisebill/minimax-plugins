---
name: visual-anatomy
description: |
  Build a single-file, multi-perspective interactive HTML explainer on any topic and
  deploy it to a public URL. Researches current data, generates scientific-style
  illustrations and 10s H3 video clips, and wires clickable hotspots, drag
  comparators, scrubber timelines and a scale map of the "lenses" (viewpoints).
  Trigger phrases: "視覺解剖", "像新冠那個網站", "多視角互動網站", "用互動的方式解釋",
  "做成可互動的網頁來解釋", "visual anatomy of", "interactive explainer for",
  or a bare topic noun when the user has just praised a previously built one of
  these sites. Do NOT use for: a single chart or diagram request, a slide deck,
  a written report with no interactive requirement, or a plain factual question
  that one paragraph answers.
---

# Visual Anatomy

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

### 2. Research, and pin the data to a date

Search for current figures. Every number that appears on the page must be traceable to a
source you actually retrieved — put a `## Sources` section at the bottom with the URLs.

Record an **as-of date** and surface it in the page header. This is what separates a page
that will be trusted next month from one that will silently rot. When sources disagree,
say so on the page rather than picking whichever is convenient.

Where a number is an estimate, model output, or a schematic, **label it on the page**
("示意模型 · 非實測"). Fabricated precision is worse than an honest range.

### 3. Start the slow generation first

Video generation (H3) takes 15–30 minutes and the images ~2 minutes. Submit video
tasks immediately after the angle set, then do images, then build the page, then collect
the video. Do not reorder this — it is the single biggest wall-clock saving.

Use `mcode-tools` for both. Load the `mcode-tools-master` skill first, discover the
tools, and read `references/imagery.md` in this skill for prompt patterns and the
compression steps. Batch image generation in one `requests[]` call.

### 4. Build the page

Single file: inline `<style>` and `<script>`, assets in a sibling `img/` and `video/`
folder next to `index.html`. No frameworks, no CDN JS. Google Fonts is fine (it is a
stylesheet, and the page degrades to system fonts offline).

Copy component code from `references/components.md` rather than rewriting it. It is
already free of the six bugs listed below.

Standard shell: sticky top bar with lens tabs → scale map showing where each lens sits →
one panel per lens → a compact Q&A / sources section → footer.

Interaction budget — a page feels thin if it has fewer than these:
- lens switcher that also **scrolls to** the panel
- at least one **draggable or scrubbable** control
- at least one **generated illustration** with 3+ clickable hotspots
- one **comparison** the reader manipulates (slider, or A/B toggle)
- long text collapsed to ~2 lines behind a click

### 5. Verify visually before deploying

Non-negotiable, and it is where every real bug has been found. Run
`references/verify.md` — it is a ready Playwright harness. It must assert on **element
position inside the viewport** and on **pixels changing**, not on class names or text
content.

> **The lesson that cost the most:** asserting "element has class `.on` and contains text"
> passes while the element sits 3000px above the viewport, invisible to the user. DOM state
> correct ≠ user can see it. Every overlay, tooltip, modal and tooltip must be screenshot-
> verified or boundary-asserted at least once.

Six bug classes this exact architecture has actually produced — check each explicitly:

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | Rotating 3D object drifts off-canvas | CSS `transform: rotate()` on a 2D projection of a 3D point set | Project properly per frame with a rotation matrix; recompute depth, length, opacity; hide back-facing points |
| 2 | Labels "jump" when selected | CSS `font-weight` change alters CJK glyph width | Hold weight constant, change colour only; never animate a dimension that affects layout |
| 3 | A control has zero effect on the readout | Normalisation constant built from the same variable it should be independent of (`score = D/DL` where `DL` also contains `D`'s input) | The reference constant must be a **fixed literal**; verify by moving each control and checking the number actually moves |
| 4 | Drag handle moves, image does not | Both layers of a comparator are the same image — the composite never changes | A before/after comparator needs **two different source images** |
| 5 | Click on a hotspot appears to do nothing | Hover already opened it, and click toggles "already open" → closes it | Separate states: hover = preview, click = pin |
| 6 | Overlay renders off-screen | `position:absolute` element positioned with coordinates relative to a different ancestor | `position:fixed` + `getBoundingClientRect()` viewport coordinates |

Two more that cost time: hidden panels report `offsetTop === 0`, so scroll targets must
use `getBoundingClientRect().top + scrollY`; and a grid item stretches to its tallest
sibling by default, so mixed-height side-by-side visuals need `align-items:start`.

### 6. Deploy

`website_deploy` with `path` = the folder containing `index.html`, `source_path` = the
same folder. The tool publishes a **publicly accessible** URL and archives the source
privately. Confirm first if the user has not already asked for a URL, and tell them the
link is public. Verify after deploying with an HTTP check on the page and on 2–3 assets —
a 200 on the page alone does not prove the images and video resolved.

## Output contract

1. A deployed URL, plus the local file path
2. The angle set used, so the user can redirect
3. The as-of date of the data
4. What was verified and what remains unverified (be explicit; never imply you tested
   something in a browser you could not actually reach)

## Failure handling

- **Angle set feels weak** → reshape the list and rebuild the page shell; the shell is
  cheap, the research is the expensive part, so do not re-research.
- **A source is unavailable or paywalled** → use a secondary authoritative source and say
  on the page which was used. Do not fill a gap from memory.
- **Image generation returns anatomically or factually wrong art** → regenerate with a
  corrected prompt, and do not place a hotspot on the misleading part. Check the output
  image before wiring hotspots onto it.
- **Video generation fails or times out** → ship the page without it. The static
  illustrations carry the content; the video is an enhancement, not the load-bearing part.
- **A control cannot be made to work correctly** → remove it and state that it was removed.
  A broken interactive element costs more trust than its absence.
- **The user reports "it doesn't respond"** → reproduce it, screenshot it, and read the
  computed styles before theorising. Then verify the fix the same way.

## Examples

**Input:** `視覺解剖 F1 新加坡站排位賽結果`
**Output:** 6 lenses (排位成績 / 車手三大段落 / 輪胎策略 / 車隊對比 / 為什麼是這個成績 /
明日預測) with a scale map ordered from track scale down to tyre-compound scale, a
scrubbable lap-time delta chart, per-driver sector comparison toggles, a generated
circuit aerial, and hotpots on the qualifying classification table.

**Input:** `照新冠那個網站的做法做血管內皮的致病機制`
**Output:** Reuses the same shell; lenses become 空氣→血管內皮→補體活化→微血栓→器官後遺症;
a comparison slider shows healthy vs damaged endothelium using **two separately generated
images**; sources pinned to the retrieval date.

## References

- `references/components.md` — copy-paste component code (stage, hotspot, comparator,
  player, scale map, lightbox, text collapse) and their CSS
- `references/imagery.md` — image/video prompt patterns, aspect ratios, compression
- `references/verify.md` — Playwright verification harness and assertion recipes
