---
name: audio-reactive-waveform
description: Render local music as a transparent audio-reactive bar overlay for CapCut or other editors; adapt colors, bar layout and motion from a reference video or screenshots. Use for music visualizers and waveform-style overlays, not audio synthesis or automatic video recreation.
---

# Audio-reactive waveform

Create a silent ProRes 4444 MOV with real alpha using the bundled local Python/FFmpeg renderer. The default is 48 gold-to-orange mirrored bars at a fixed center baseline. The animation is a 48-band frequency spectrum, not a sample-by-sample waveform or beat detector.

## Workflow

1. Identify the local music input, reference video/screenshots if supplied, desired canvas/FPS, and output directory. Keep the reference's appearance separate from the music that drives the output. For missing paths or an inaccessible reference link, ask for a local clip or representative screenshots; do not claim to have seen inaccessible content.
2. Inspect actual reference pixels before describing its style. Use local FFmpeg to extract a few representative frames into a task-owned temporary directory. A still frame can establish colors, spacing and layout; motion, attack/release and timing require multiple frames or playback. Label inferred settings and avoid promising an exact reconstruction of an unknown algorithm. Read [reference matching](references/reference-matching.md) for supported adaptations and limits.
3. Read [local setup](references/local-setup.md) to check dependencies and choose commands. Run in the user's requested environment. Rendering is local and requires no API key. Installing packages or sending a private reference to a model/service requires the permissions applicable to that environment; creating this skill does not grant either. If visual inspection would transmit private media outside the computer, explain that distinction and obtain required approval first.
4. Copy [the default preset](assets/gold-mirrored.json) into the task's output folder and edit supported fields using [the style schema](references/style.md). Propose the settings in plain language, including approximations. Use a new preset/output filename for revisions; do not silently replace the approved sample or overwrite existing media.
5. Render at most 20 seconds from the beginning (or the full input if shorter). Quote all paths. Use the verified script location and an explicit output path:

   ```sh
   python "$SKILL_DIR/scripts/render_waveform.py" --input "/path/to/music.wav" --output "/path/to/output/sample.mov" --style "/path/to/output/style.json" --duration 20
   ```

6. Verify the sample: ffprobe reports a single ProRes 4444 video stream, alpha-capable pixel format, requested size/FPS and no audio; decode alpha and confirm transparent background plus visible bars. Inspect on contrasting backgrounds and across time. Deliver the transparent MOV for import above a video in the editor. If a flattened preview is requested, label any MP4 preview as **nontransparent**; it is not the overlay deliverable. Ask the user to approve the look and their editor's alpha import before full rendering.
7. After creative approval, rerun with the same settings and omit `--duration` to render the full song. Whole-file normalization can produce slightly different amplitudes than a 20-second sample; disclose this and inspect representative full-output frames. Deliver the MOV and the exact style JSON, noting it is silent: the original music belongs on a separate, time-aligned audio track. Report verified results, limits and local paths; never claim a runtime/platform test that did not occur.

## Boundaries

- Supported geometry: `mirrored` bars or upward `single` bars. The script supports color gradients, count, width, margins, baseline, height limits and attack/release. It does not implement radial rings, continuous curves, rounded caps, glow, particles or perspective tracking. Explain the nearest supported approximation or scope a separately approved implementation.
- Keep source assets out of the skill/repository. Do not upload references, music, generated media or paths containing private information as part of publishing code.
- Frames stream directly into FFmpeg. Only this run's private temporary directory is cleaned up; existing files survive unless the user explicitly authorizes replacement and `--overwrite` is passed.
- Code validation and creative approval are separate. For renderer changes, follow the repository's applicable engineering guidance and test through the CLI with synthetic inputs. Run `python -m unittest discover -s "$SKILL_DIR/tests" -v`; media tests require NumPy, FFmpeg and ffprobe. A skipped media test is not a media pass.
