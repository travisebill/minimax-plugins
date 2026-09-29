---
name: three-kingdoms-focus-music
description: |
  Create Three Kingdoms-inspired music release packages for listening, publishing, and archival reuse. Use when the user wants long instrumental focus music, theme songs, character songs, album tracks, matching cover art, looping video covers, YouTube copy, or a reusable record of Three Kingdoms-related releases in changing styles such as bossa nova, jazz, romantic, travel, or other calm variations.
  Trigger words: Three Kingdoms focus music, 三国志学习音乐, 三國志讀書音樂, strategy study BGM, historical focus music, 長時間專注音樂, 三国歌曲, 专辑封面, 封面记录, 作品记录, YouTube 封面, 循环封面.
---

# Three Kingdoms Focus Music

Use this skill when the user wants a reusable Three Kingdoms-related music release workflow: long focus music, individual songs, album tracks, character-themed songs, and matching cover art or archive records for future reuse. The style can stay historical and restrained, or branch into other song styles as long as the Three Kingdoms identity remains recognizable.

The goal is not only one audio file. The goal is a repeatable release system for Three Kingdoms music, cover art, and publish-ready copy.

## Fixed Baseline

Unless the user overrides it for a specific run:

- Default music use: long focus music or a single publishable track, depending on the request.
- Default mood: strategy study room — calm, intelligent, restrained, historical, focused.
- Music generation: use the selected music generator for the current session; do not hardcode a model unless the user explicitly requests one.
- Mode: instrumental unless the user explicitly asks for vocals, lyrics, or character song performance.
- Listening use: reading / study / writing / quiet work / themed listening. Avoid attention-grabbing hooks, sudden hits, loud percussion, battle-climax scoring, or anything that breaks repeat listening.
- Visual anchor: Three Kingdoms historical atmosphere, bamboo slips, oil lamp, distant banners, quiet command tent, ink-wash landscape, scholar-general restraint, or related character-theme symbolism.
- Visual package style: Chinese ink-wash, seal-like identity, textured paper, minimal and readable at thumbnail size. YouTube cover images must use 16:9.
- Archive target: keep the music, cover, title, and release variant easy to reuse later for similar Three Kingdoms songs.

## Inputs

Ask only for missing information that materially affects the output:

1. Desired output type: long focus mix, single song, album track, or full release package.
2. Desired duration, if relevant.
3. Music temperament or sub-style.
4. Any explicit do-not-use elements, such as no percussion, no guqin, no rain ambience, no battlefield drums, no vocals.
5. If visuals are requested, whether the user needs cover art, avatar, banner, or loop video.
6. Any required title text or album name.
7. Whether this run should update the reusable archive of Three Kingdoms releases.

Do not ask for subtitles unless the user explicitly requests them.

## STEP 1: Classify the Release Type

Decide whether the request is:

- a long focus-music release,
- a single song,
- a themed album track,
- a character song,
- a character or album cover refresh,
- or an archival update for a previously created Three Kingdoms release.

Keep the Three Kingdoms identity stable while allowing the musical style to vary. A bossa nova or jazz song can still belong to the Three Kingdoms world if the lyrics, title, naming, or cover language keep that identity clear.

## STEP 2: Plan the Music

For long focus music, create a long-form structure before generation.

For the 60-minute default, use 6 musical chapters of about 10 minutes each:

1. Opening desk lamp — establish quiet historical reading atmosphere.
2. Bamboo slips and distant banners — light forward motion.
3. Strategy map at night — deeper concentration, subtle tension.
4. Wind through command tent — airy middle section, reduced density.
5. Long campaign reflection — gentle emotional weight without climax.
6. Returning to stillness — soft resolution and loop-friendly ending.

For a single song or album track, define one clear emotional lane and one clear listening use. Keep the song identity distinct instead of hiding multiple songs in one prompt.

If the user wants a broader song line-up, plan each track as its own release unit and keep title, mood, and cover logic aligned.

## STEP 3: Generate the Music

Generate one final musical unit per release target.

Prompt rules:

- One prompt = one final song or one final long mix.
- Preserve the user’s release topology: do not hide multiple songs in one generation call.
- Keep compatible tempo, instrumentation, loudness, and emotional intensity across related tracks when they belong to the same album family.
- For focus music, prefer low-distraction instruments and loop-friendly phrasing.
- For songs, allow the genre to vary, but keep the Three Kingdoms identity visible through lyrics, naming, mood, or arrangement.
- Avoid vocals only when the user has not asked for them.
- Make each track publishable as a standalone release asset.

### MiniMax Music 3.0 interface and guide reference

When MiniMax Music 3.0 is selected, identify the delivery route before writing a paste-ready payload. The public Music Generation API and web prompt field use model `music-3.0`, with `prompt` limited to 2,000 characters and `lyrics` sent separately. Count the actual plain-text `prompt`, including spaces and paragraph breaks, and record the safety margin. The open-weight model-card/SGLang route uses a different `input`/`instructions` contract and token budget; never use its limit as the public prompt-field limit.

Apply the official Music 3.0 guide's structured prompting principles to focus music: state the global creative intent, describe the emotional arc, and give a fine-grained temporal arrangement that names instrument entry, layering, transformation, and exit. Use section-level structure when it improves coherence, while keeping the public payload concise. For instrumental cues, use structural tags only in `lyrics`; place arrangement and negative constraints in `prompt`. Keep the full reusable master separate from each constrained delivery version.

The guide describes Music 3.0 as generating a complete song from creative intent and optional lyrics, with duration up to five minutes. This does not change a project's release topology: a 60-minute focus release still uses independent cues when the plan calls for them. Since instrument, arrangement, and other details can drift, audio QA must verify the intended emotional arc, timed entries/exits, instrument presence, vocal absence, section order, and technical file properties against the prompt.

Reference the [official Music 3.0 guide](https://www.minimax.io/blog/minimax-music-3-0-next-generation-open-weights-production-ready-versatile-music-model), the [public Music Generation API documentation](https://platform.minimax.io/docs/api-reference/music-generation), and the [MiniMax-Music3 model card](https://huggingface.co/MiniMaxAI/MiniMax-Music3) when documenting interface limits or provider-specific handoffs.

If the user asks for a series of related songs, treat each song as a separate deliverable and preserve the shared identity across the set.

For duration-bound focus releases, calculate the total generated music duration before final assembly. If the generated music is shorter than the requested duration, generate additional compatible instrumental tracks or cues until the available total duration is greater than or equal to the requested duration. Prefer adding new low-distraction music over simply stretching or looping too-short material, unless the user explicitly asks for looping.

## STEP 4: Generate Matching Cover Art and Release Visuals

If the user asks for cover art, avatar, banner, or album art, reuse the same Three Kingdoms visual language from the music.

- Cover art: use 16:9 for YouTube covers and thumbnails. Use square only for explicitly requested album-platform artwork.
- Avatar: small, seal-like, highly legible, emblematic.
- Banner: wide 16:9, with safe-area composition for YouTube.
- Album art: clear title hierarchy, strong symbol, readable at thumbnail size.
- Style: Chinese ink-wash, seal-carving, scholar-warrior restraint, minimal clutter, readable at thumbnail size.
- If the user gives title text, preserve it; otherwise use symbolic or abstract identity marks.
- Before generating any cover image, draft the exact cover prompt and ask the user to confirm or revise it. Do not start cover generation until the user explicitly confirms the prompt.

For song covers, choose one clear visual metaphor that fits the track: river mist, bamboo slips, moonlit corridor, command desk, seal emblem, quiet travel, court scene, or character-themed symbolism.

## STEP 5: Maintain a Reusable Release Record

When the user wants to keep adding more Three Kingdoms-related songs later, record the release family consistently.

Keep track of:

- title or track name,
- genre or sub-style,
- duration if relevant,
- cover image,
- version or alternate cut,
- whether it belongs to a larger album or series,
- and any reusable visual identity notes.

When a new song or cover is added, make sure it still fits the same archive family unless the user explicitly starts a new series.

### Audio naming and provenance

Use stable, lowercase-kebab track IDs and preserve the release ID in every generated filename. The canonical source-candidate pattern is `<release-id>-<track-id>-candidate-<NN>-source.<actual-ext>`, for example `S01-P06-opening-core-candidate-01-source.wav` or `S01-P06-chapter-01-core-candidate-02-source.mp3`. Use a two-digit candidate number, never reuse a number, and keep the actual returned extension.

If the provider assigns a filename, preserve that provider-original filename and bytes; record it beside the canonical candidate ID rather than silently replacing it. Do not rename a source file to imply selection or approval. Record `selected candidate` and approval state in the manifest. A chapter assembly uses `<release-id>-chapter-<NN>-mix-v<NN>.<ext>`, and a complete release uses `<release-id>-full-mix-v<NN>.<ext>`. Increment the version for a changed render or mix, preserve earlier siblings, and do not use `final` or `approved` in a filename before the corresponding approval gate.

## STEP 6: Produce a Loopable Video Cover When Requested

If the user wants a loopable video cover for YouTube or a music platform:

- Before generating any video cover, draft the exact video prompt and ask the user to confirm or revise it. Do not start video generation until the user explicitly confirms the prompt.
- For YouTube loopable cover videos, use MiniMax-H3 and generate a 15-second seamless loop unless the user explicitly requests another available duration or model.
- Use the approved 16:9 YouTube cover as the first frame or reference anchor.
- Keep the camera stable unless the user asks for camera movement. For calm focus releases, prefer fixed-camera animation where the character, lamp, mist, particles, banners, cloth, water, or ink atmosphere moves gently inside the scene.
- Keep motion extremely restrained.
- Prefer slow breathing light, drifting mist, faint particle movement, water ripples, gentle fabric movement, eye blinks, or a slow fan gesture when compatible with the cover.
- Maintain a seamless loop, with no abrupt cuts or attention-grabbing effects.
- The video should be silent unless the user explicitly asks for sound.

The loopable video cover should visually match the audio mood so it can be combined with the final audio into a publishable release.

## STEP 7: Assemble the Final Publishing Package

When the user wants a publishable package, produce the full set:

- Long focus-music audio, or a single song / album track audio.
- Matching cover image.
- Optional 15-second MiniMax-H3 seamless loopable video cover for YouTube.
- Optional YouTube avatar and banner.
- Optional YouTube description, pinned comment, or release copy.
- Optional archived release notes for future reuse.

Keep the description concise, readable, and SEO-friendly. Mention reading, study, work, focus, Three Kingdoms, Chinese-style atmosphere, album release, or the genre when relevant. Pinned comments should use a literary, reflective, gentle style rather than a purely functional marketing style.

## STEP 8: Quality Check

Before delivery, check:

- Final duration is greater than or equal to the requested duration when the user specifies a minimum or exact long-form release length; generate more compatible music if the available total is short.
- No vocals or spoken words are present unless explicitly requested.
- No sudden loud moments break concentration.
- Visual assets remain legible at thumbnail size.
- The cover and video still feel like the same release family.
- The release can be reused later as part of the same Three Kingdoms archive.

## Confirmation Points

- Ask before generating if the user requests more than 60 minutes or asks for an unusually specific instrumentation plan.
- Ask before shifting from calm focus music into a clearly dramatic battle-score direction.
- Ask before generating vocals if the user has only asked for instrumental music.
- Ask before generating a full release package if the user has only asked for audio and the visual direction is not yet defined.
- For standard long focus-music releases, if the user asks to generate immediately, music generation can proceed without extra confirmation. Cover-image generation and video-cover generation still require prompt confirmation first.
- Always confirm the cover prompt before generating a cover image.
- Always confirm the video prompt before generating a loopable video cover.

## Failure and Repair Rules

- If a music generation fails, preserve successful cues and retry only the failed module.
- If a cue is too dramatic, regenerate that cue with lower percussion, lower density, fewer hits, and more sustained ambience.
- If a cue contains vocals when vocals were not requested, discard it and regenerate appropriately.
- If generated music is shorter than the requested duration, generate additional compatible music tracks or cues until the total source music length reaches or exceeds the requested duration, then assemble. Use tail/crossfade repair only for small transitions, not as the primary fix for missing minutes.
- If a visual asset comes out too busy, simplify the composition and push the identity toward seal, emblem, or quiet study iconography.
- If a loop video does not feel seamless, reduce motion amplitude rather than adding new motion types.

## Delivery

Deliver one or more of the following, depending on the request:

- Final long-focus mix, single song, or album track audio.
- Optional individual chapter cues.
- Matching cover image or album art.
- Optional 15-second MiniMax-H3 seamless loopable video cover for YouTube.
- Optional YouTube avatar and banner.
- Optional release description or pinned-comment text.
- Optional archival notes for future reuse.
- A brief chapter list or track list with approximate timings.

Reference exact filenames in the final reply so the user can click the canvas assets.
