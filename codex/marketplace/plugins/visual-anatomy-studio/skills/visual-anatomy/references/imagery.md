# Imagery — generating and shipping art

Load the `mcode-tools-master` skill before running any `mcode-tools` command. Discover the
tools rather than assuming the names below are current; they are the ones last observed.

## Order of operations

1. Submit **video** tasks first (15–30 min), then do everything else
2. Batch **images** in one `generate_image` call (`requests[]`, not a flat prompt)
3. Build the page while video runs
4. Collect video, compress, embed

## Image prompts

### The style block

Append this to every prompt so the whole set reads as one system. Swap the palette per
domain; keep the "no text" clause always.

```
<render style>, deep navy background, <accent> and <secondary accent> accents,
volumetric soft lighting, ultra clean, high detail, cinematic, centered composition.
No text, no letters, no labels, no watermark, no scale bar.
```

`No text` matters: image models garble lettering, and a page whose illustration says
"Ploble" undermines everything around it.

### Render styles by what the slot needs

| Slot | Style | Aspect |
|---|---|---|
| Subject hero (one object, fill the frame) | `extreme macro 3D scientific render, shallow depth of field` | `1:1` |
| Process / mechanism | `scientific 3D cross-section illustration` | `16:9` |
| Before/after comparator (each half) | `scientific 3D medical/technical illustration` | `16:9` |
| Scene with a person or environment | `cinematic 3D visualization, volumetric haze, moody lighting` | `16:9` |
| Body / system overview | `3D visualization of a translucent <subject>, glowing glass` | `3:4` |
| Side-by-side comparison of N variants | `N objects floating in a row` | `21:9` |

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

## Video (MiniMax H3)

```json
{"model":"MiniMax-H3","duration":10,"ratio":"16:9","resolution":"2K","prompt":"<…>"}
```

- H3 renders a **synchronized native audio track**. Prompt for ambience/SFX only —
  `"no voiceover, no speech, no music, only soft room tone"` — otherwise you get narration
  you did not ask for and cannot control.
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
- [ ] Only then place hotspot coordinates, reading percentages off the actual image
- [ ] Confirm the two comparator images are genuinely different files
