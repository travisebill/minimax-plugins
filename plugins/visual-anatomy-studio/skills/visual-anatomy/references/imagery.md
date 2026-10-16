# Imagery — generating and shipping art

Load the `mcode-tools-master` skill before running any `mcode-tools` command. Discover the
tools rather than assuming the names below are current; they are the ones last observed.

## Order of operations

1. Submit **video** tasks first (15–30 min), then do everything else
2. Batch **images** in one `generate_image` call (`requests[]`, not a flat prompt)
3. Build the page while video runs
4. Collect video, compress, embed

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

## Video (MiniMax H3)

```json
{"model":"MiniMax-H3","duration":10,"ratio":"16:9","resolution":"2K","prompt":"<…>"}
```

- H3 renders a **synchronized native audio track**. Prompt for ambience/SFX only —
  `"no voiceover, no speech, no music, only soft room tone"` — otherwise you get narration
  you did not ask for and cannot control.
- **Carry the chosen style into the video prompt too.** H3 is biased toward photoreal
  cinematic footage; on a flat-vector style (Ledger, Broadsheet, Clinical, Plate) say so
  explicitly — `flat 2D vector animation, paper-textured background, no volumetric light,
  no depth of field` — or the clip reads as a different style from the page it sits on.
- Submit 2, not more. One for the mechanism, one for the scene. More is latency you do not need.
- `duration` 4–15 for H3, 5–15 for H3-Max.
- Re-query for a fresh URL; download links are temporary and results are retained ~7 days.
- Keyframe mode (`input_image` + `reference_type`) gives visual continuity with your
  generated stills — worth it when the video must match a specific illustration.

## Download and compress

```bash
url=$(mcode-tools get_asset_url <node_id> | python3 -c "import sys,json;print(json.load(sys.stdin)['download_url'])")
curl -sSL -o raw.jpg "$url"
```

Never construct a CDN URL from `node_id` — it does not work.

Then, with Pillow:

```python
im = Image.open("raw.jpg").convert("RGB")
tw = 1800 if slot_is_hero else 1600
im2 = im.resize((tw, round(h*tw/w)), Image.LANCZOS)
im2.save(f"{name}.webp", "WEBP", quality=82, method=6)     # primary
im2.resize((im2.width//2, im2.height//2), LANCZOS).save(f"{name}-sm.webp","WEBP",quality=72)
```

Serve `.webp` directly; browsers that do not support it are a rounding error. Keep the
`-sm` variant and reference it with `<source media="(max-width:760px)">` so phones do not
pull the full-size file.

**Budget check before deploying:** a set of 8 raw 2K images is ~22 MB. Compressed webp it
should land under ~1.5 MB. If it does not, the resize step was skipped.

## Video compress

```bash
ffmpeg -i in.mp4 -vf "scale=1280:-2" -c:v libx264 -profile:v high -crf 24 -preset slow \
       -c:a aac -b:a 96k -movflags +faststart out-720.mp4
ffmpeg -y -ss 3 -i out-720.mp4 -frames:v 1 -q:v 4 poster.jpg
```

720p H.264 plays everywhere; a 10 s 2K master compresses from ~8 MB to ~1.8 MB. Extract the
poster **after** compressing and use it as the `poster` attribute.

`ffmpeg` in some builds has no VP9 encoder, which silently produces a 264-byte `.webm`.
Check the output size, and if webm is not viable just ship mp4.

## Checklist before wiring hotspots

- [ ] Open and **look at** each generated image
- [ ] Regenerate anything anatomically or factually wrong
- [ ] Regenerate anything in the **wrong style** — a 3D render on a flat page, a light
      image on a dark page. CSS cannot fix this; it is baked into the pixels
- [ ] Only then place hotspot coordinates, reading percentages off the actual image
- [ ] Confirm the two comparator images are genuinely different files
