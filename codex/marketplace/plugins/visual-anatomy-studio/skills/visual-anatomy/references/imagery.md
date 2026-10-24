# Image and video generation

## Route by tools available now

Media tools vary by computer and session. Inspect the current tool catalog and load only
the relevant installed provider skill. Use a provider only when its live tools support the
requested asset. `mcode-tools` is optional; if no compatible generator is available,
continue with the rest of the page and report the missing media.

When MiniMax Design MCP is available and the user has not selected another provider:

1. Call `list_projects` first. Select a suitable project with `open: true`, then call
   `open_project` with its returned `projectId` before other project operations. If no
   suitable project is open, use another compatible provider when available unless the
   user specifically requires MiniMax; otherwise ask the user to open a project.
2. Call `capability_list` for the requested media operation and `capability_get` for the
   selected capability. The returned schema and rules are authoritative; do not reuse
   guessed or stale parameters.
3. Submit through `execute` when prompts and references are ready. Use `task_wait` with the
   same `taskId` until the task settles; never duplicate a task just because a wait timed
   out.
4. If a task requests cost approval, show the quote and wait for the user's explicit
   agreement before calling `confirm_cost`.
5. Retrieve completed results with `get_output` and the returned `versionId`, then copy
   them into the website's local `img/` or `video/` folder. Never construct download URLs
   from resource IDs.

For other providers, follow their own live project, schema, cost, wait and retrieval
contracts. If the user specified a provider, honor that choice or explain what it cannot
do. Do not assume model names, request formats or wait times from another host.

## Image prompts

### Two orthogonal axes — do not confuse them

1. **The style** (from `styles.md`, chosen with the user in step 2) decides the *render
   language*: flat vector vs 3D, dark vs light, illustration vs photograph. One style for
   the whole set.
2. **The slot** (table below) decides *what kind of thing* is being drawn. It does not
   decide the look.

Getting these backwards is how you ask for a "before/after comparator" and receive two
identical photoreal renders.

### The style block

Append the chosen style's fragment to **every** prompt so the set reads as one system.
Keep the no-text clause always, and keep the named composition clause for the slot.

| Style | Append this |
|---|---|
| Clinical | `clean scientific diagram, white background, restrained teal and slate linework, flat vector anatomy, even clinical lighting, high detail, no glow` |
| Ledger | `flat editorial data illustration, warm off-white background, muted ink linework, no gradients, screenprint texture, high detail` |
| Broadsheet | `newspaper-infographic aesthetic, flat vector, off-white background, two-colour duotone, bold geometric shapes, screenprint grain` |
| Telemetry | `dark telemetry dashboard aesthetic, high-contrast neon data on near-black, motion trails, precision grid, high detail` |
| Archive | `aged archival illustration, sepia and muted ochre, paper texture, engraved linework, documentary plate, high detail` |
| Blueprint | `technical blueprint schematic, white linework on deep blue, orthographic projection, dimension lines, drafting style, high detail` |
| Field guide | `natural history plate illustration, muted botanical greens, hand-drawn lithograph texture, soft natural light, high detail` |
| Gallery | `gallery print aesthetic, generous negative space, soft even light, muted tonal range, high detail` |
| Workbench | `clear instructional illustration, flat vector, bright even lighting, neutral background, diagram clarity, high detail` |
| Plate | `minimal geometric diagram, monochrome line work on white, single accent hue, generous margins, precise construction lines` |

Universal suffix, every prompt, every style:

```
No text, no letters, no labels, no numbers, no watermark, no scale bar.
```

`No text` matters: image models garble lettering, and a page whose illustration says
"Ploble" undermines everything around it.

**Style mismatch is a regeneration trigger.** If the returned art reads as a different
style than the page (a Clinical page that came back as neon 3D), regenerate with a
stronger style clause — no CSS change can fix an image baked in the wrong language.

### Render styles by what the slot needs

| Slot | Style | Aspect |
|---|---|---|
| Subject hero (one object, fill the frame) | `extreme macro 3D render, shallow depth of field` | `1:1` |
| Process / mechanism | `3D cross-section illustration` | `16:9` |
| Before/after comparator (each half) | `3D technical illustration` | `16:9` |
| Scene with a person or environment | `3D visualization, volumetric haze, moody lighting` | `16:9` |
| Body / system overview | `3D visualization of a translucent <subject>, glowing glass` | `3:4` |
| Side-by-side comparison of N variants | `N objects floating in a row` | `21:9` |

These render phrases are the **default for dark 3D styles**. For **Clinical, Ledger,
Broadsheet, Field guide, Gallery, Workbench and Plate**, swap the 3D/glow vocabulary for
flat-illustration language (`flat vector`, `isometric`, `cross-section diagram`,
`engraved plate`) — a photoreal 3D render sitting inside a flat-vector page is the most
visible style break you can ship.

### Describe the difference, not just the thing

For a comparator the two prompts must be **one sentence apart** and produce visibly
different results:

```
…of HEALTHY <thing>. <descriptors of the healthy state> …
…of DAMAGED <thing>. <same noun>. <descriptors of the failure state> …
```

Worked example that worked: *healthy alveoli — thin clean uniform walls, clear air, open
spaces, bright* vs *damaged — swollen, walls thickened and rough, air spaces collapsed and
filled with cloudy fluid, angry red and coral, opaque and heavy*.

The sentence-apart rule holds for light styles too — *in dry season: pale, dry, cracked,
warm ochre* vs *in flood: swollen, dark, saturated, standing water*.

## Video

Use the selected provider's live video contract for duration, frame ratio, resolution,
reference limits and audio settings. For MiniMax Design, the observed H3 catalog supports
short 4–15 second clips; re-read `capability_get` before each generation session and obey
its current schema.

- Carry the chosen style into every video prompt. H3 tends toward cinematic footage; for a
  flat style, state the intended 2D or illustration language explicitly so the clip does
  not clash with the page.
- Generate separate clips and merge them only with an available editing tool; do not call
  them one continuous video unless they were actually joined.
- When separately generated narration or music will accompany a clip, disable video audio
  if the live capability exposes that option. See [audio.md](audio.md) for the audio path.
- Pass image or video references only when the live capability accepts their type and
  limits.

## Retrieve and compress

Use the output path or retrieval method returned by the selected provider. Never derive a
CDN or download URL from an asset ID. Copy media into the page's local `img/` and `video/`
folders before embedding them. If an image library or `ffmpeg` is available, resize images
and compress video; otherwise keep the returned format and report it accurately.

With Pillow, a responsive WebP can be produced like this:

```python
im = Image.open("raw.jpg").convert("RGB")
tw = 1800 if slot_is_hero else 1600
im2 = im.resize((tw, round(h*tw/w)), Image.LANCZOS)
im2.save(f"{name}.webp", "WEBP", quality=82, method=6)
im2.resize((im2.width//2, im2.height//2), Image.LANCZOS).save(f"{name}-sm.webp", "WEBP", quality=72)
```

When `ffmpeg` is available, compress video and extract its poster after compression:

```bash
ffmpeg -i in.mp4 -vf "scale=1280:-2" -c:v libx264 -profile:v high -crf 24 -preset slow \
       -c:a aac -b:a 96k -movflags +faststart out-720.mp4
ffmpeg -y -ss 3 -i out-720.mp4 -frames:v 1 -q:v 4 poster.jpg
```

Check transformed file sizes and playability; some `ffmpeg` builds lack a VP9 encoder and
may produce a tiny invalid WebM. Keep the original output until the optimized file has
been checked.

## Checklist before wiring hotspots

- [ ] Open and **look at** each generated image
- [ ] Regenerate anything anatomically or factually wrong
- [ ] Regenerate anything in the **wrong style** — a 3D render on a flat page, a light
      image on a dark page. CSS cannot fix this; it is baked into the pixels
- [ ] Only then place hotspot coordinates, reading percentages off the actual image
- [ ] Confirm the two comparator images are genuinely different files

