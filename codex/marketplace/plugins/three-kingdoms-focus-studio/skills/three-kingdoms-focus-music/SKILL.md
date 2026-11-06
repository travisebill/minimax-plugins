---
name: three-kingdoms-focus-music
description: |
  Create Three Kingdoms-inspired music release packages for listening, publishing, and archival reuse. Use when the user wants long instrumental focus music, theme songs, character songs, album tracks, matching cover art, looping video covers, YouTube copy, or a reusable record of Three Kingdoms-related releases in changing styles such as bossa nova, jazz, romantic, travel, or other calm variations.
  Trigger words: Three Kingdoms focus music, 三国志学习音乐, 三國志讀書音樂, strategy study BGM, historical focus music, 長時間專注音樂, 三国歌曲, 专辑封面, 封面记录, 作品记录, YouTube 封面, 循环封面.
---

# Three Kingdoms Focus Music

Read [Codex runtime guidance](../../CODEX.md) before using this skill. Resolve bundled skills and resources relative to this installed package.


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

**Size the release to the real per-track length, not the advertised maximum.** Music 3.0
generates a complete song of roughly 1.5–3.5 minutes when it is being used for good-quality
instrumental. Measured 2026-09-30: 2.90 minutes. A caption cannot extend this and the hosted API
exposes no duration parameter, so a 65-minute release needs about 22–26 tracks, not 6. Plan the
track count from a midpoint of 2.5 minutes and correct it after the first real measurement.

**Author a core set and a reserve set, not one fixed set.** The per-track length varies between
calls, so a single sized set either overshoots or leaves the release short.

- Core set: sized from the 2.5 minute midpoint, the intended running order.
- Reserve set: shorter, simpler arrangement timelines, written and held back. They exist to plug a
  shortfall revealed by measurement, not to be generated up front.
- Ship a decision table beside the prompts mapping the user's measured average to the action:
  at 3.5 minutes drop tracks, at 2.5 use everything, at 1.8 add the whole reserve bank. When even
  the full bank falls short, say so in advance with the number of extra tracks required — do not let
  the user discover the shortfall after generating everything.

For the 60-minute default, use 6 musical chapters of about 10 minutes each:

1. Opening desk lamp — establish quiet historical reading atmosphere.
2. Bamboo slips and distant banners — light forward motion.
3. Strategy map at night — deeper concentration, subtle tension.
4. Wind through command tent — airy middle section, reduced density.
5. Long campaign reflection — gentle emotional weight without climax.
6. Returning to stillness — soft resolution and loop-friendly ending.

**Give each chapter a minute range, not a track count.** A chapter is "8 to 12 minutes", and the
tracks that land there get decided after measurement. A track count stated in advance is a claim the
provider will not honour. Give the closing chapter the most tracks, because it carries the resolution.

Keep the descent on more than one axis at once — tempo, instrument count, density, and later in
assembly the frequency content and low-end weight. Reducing instrument count alone reads as thinning
out rather than settling down.

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

When MiniMax Music 3.0 is selected, **identify the delivery route before writing a payload**. There are four routes and their parameters are not interchangeable. Treating one route's limits as another's is the single most common source of wrong instructions.

| Route | Instrumental control | Duration control | Prompt limit |
|---|---|---|---|
| **MiniMax Design MCP** (`generate_music:music-3.0`) | `params.mode: "instrumental"` | **none — only a timeline inside the prompt** | 2,000 chars |
| **Hosted Music Generation API** | `is_instrumental: true` | none | 2,000 chars |
| **SGLang open-weight** (`/v1/audio/speech`) | none | `max_new_tokens` (25 frames/sec) | 5,000 tokens |
| **Local connector wrapper** | **no flag exists at all** | none | schema-dependent |

Two corrections that must not be repeated:

- **`max_new_tokens` exists only on the SGLang route.** It is not a parameter of the hosted API or of the MCP. The MCP exposes no duration parameter at all.
- **The instrumental control differs per route.** The hosted API's flag is `is_instrumental`. The MCP's is `params.mode: "instrumental"`. On the MCP, `lyrics` is **not** a control: it is only meaningful in `mode: "song"`, and a controlled experiment on 18 candidates found that five different `lyrics` values — including a deliberately empty control — all produced wordless vocals. Sending `mode: "instrumental"` and omitting `lyrics` entirely produced 18/18 clean instrumental results.

**Identify the route before assuming any capability.** A local connector wrapper is not the hosted API. Measured 2026-09-30 on the local `batch_text_to_music` connector, six calls returned 13.96, 28.21, 31.09, 40.05, 40.73 and 41.15 seconds — the length is random and uncontrollable, the schema has no duration parameter, and a caption asking for "about two to three minutes" still returned 40 seconds. The same schema also has no `is_instrumental` field, and 4 of 5 generations carried wordless vocals despite captions that spelled out `no vocals, no choir, no spoken word`.

The consequences are structural, not cosmetic:

- The connector cannot produce a long-form release. Sixty minutes would need roughly 130 tracks.
- The connector cannot guarantee an instrumental result. Worded exclusions are not a control surface.
- File metadata confirms the producer but carries no model version, so it cannot establish which model ran.

**Prefer the MCP route when it is available.** Measured 2026-10-22 through `minimax-design`: 18 candidates across six chapters, `params.mode: "instrumental"`, no `lyrics` field, positive-only captions — 18/18 confirmed instrumental by measurement, spectral corroboration and human listening. Duration came from a minute-level timeline written into the prompt: a prompt with no timeline produced 59.9 seconds; the same prompt with a `0:00 … 3:50` timeline produced 188 seconds. Because exact length is not guaranteed, report a **minute range**, not a track count. Read `skills/yt-focus-music-pipeline/references/design-mcp-execution.md` before executing through the MCP.

When only the connector is available, hand over the paste-ready payloads and the chapter plan instead of attempting generation, and say plainly which capabilities the route cannot deliver. Do not spend many turns generating short candidates and stitching them to simulate a long release; the user can produce properly sized tracks in one pass.

Apply the official Music 3.0 guide's structured prompting principles to focus music: state the global creative intent, describe the emotional arc, and give a fine-grained temporal arrangement that names instrument entry, layering, transformation, and exit. Keep the full reusable master separate from each constrained delivery version.

**Where the structure actually goes.** Put the entire section timeline — entry, layering, transformation and exit of every instrument — into the `Arrangement` block of the prompt. Section tags belong in `lyrics` only on routes where `lyrics` is a real input (the hosted API, `mode: "song"`); on the MCP instrumental route there is no `lyrics` field at all. Structural tags are generative hints, not symbolic constraints: they do not by themselves define an instrumental arrangement. Likewise, worded exclusions in the caption are not a control surface — measured 2026-09-30, five of five captions that spelled out `no vocals, no choir, no spoken word` still produced wordless vocals. Write positive descriptions of what should be there, and use the route's real flag for what should not.

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
- **Every release carries one cat.** Since S02-P04 this is a channel rule, not a per-release
  choice: the cat is not obvious but is observable, and it must be in motion. The roster of
  permanent cat assets lives in the previous release package under
  `character-assets/manifest.md`; read it, pick from it, and do not regenerate the sheets.
  See `skills/three-kingdoms-video-project/SKILL.md` §The cat.
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

**Write the manifest as a machine-readable file, not a note in a plan document.** A release that spans many sessions loses track state if it lives only in prose. The manifest holds the release intent, the prompt-set path and version, per-track entries, the QA gate definitions, and the open questions. Per track: track ID, chapter, slot, selected candidate number, filename, duration, bitrate, integrated loudness, true peak, and one row per gate.

**Approval state is a field, and it defaults to pending.** Distinguish `pending_user_confirmation` from `user_approved`, and never set the latter on the user's behalf. Improvements are not approvals: when a user reports something is better, that is progress on the previous defect, not a statement that the current candidate is accepted. A track that passes every measurement and has never been listened to is still pending.

**The user's listening is the binding gate.** Measurements establish that nothing measurable is wrong. They cannot establish that a room, a pair of earphones and a listener at bedtime find it right. Keep both facts: the measurement is a pass, the gate is open, and neither substitutes for the other.

**Designate an intent, then let the judgment follow from it.** When the user describes an atmosphere rather than a specification, record the intent in the project file as the criterion that later decisions are measured against. This prevents a specific, checkable failure: framing an atmosphere as a set of per-device playback paths or usage instructions, which converts a mood into a manual. Every processing decision then answers one question — how does this bring the listening closer to the stated intent — and a decision that cannot answer it is not made, however technically correct it looks.

## STEP 6: Produce a Loopable Video Cover When Requested

If the user wants a loopable video cover for YouTube or a music platform:

- Before generating any video cover, draft the exact video prompt and ask the user to confirm or revise it. Do not start video generation until the user explicitly confirms the prompt.
- For YouTube loopable cover videos, use MiniMax-H3 and generate a 15-second seamless loop unless the user explicitly requests another available duration or model.
- Use the approved 16:9 YouTube cover as the first frame or reference anchor.
- Keep the camera stable unless the user asks for camera movement. For calm focus releases, prefer fixed-camera animation where the character, lamp, mist, particles, banners, cloth, water, or ink atmosphere moves gently inside the scene.
- Keep motion extremely restrained.
- Prefer slow breathing light, drifting mist, faint particle movement, water ripples, gentle fabric movement, eye blinks, or a slow fan gesture when compatible with the cover.
- Maintain a seamless loop, with no abrupt cuts or attention-grabbing effects.
- The video should be silent unless the user explicitly asks for sound. **But `audio: false` does not guarantee silence** — measured twice on the MCP (2026-10-22), a 6.58 s and a 15.08 s mp4 both came back with an AAC track (mean −24.2 dB and −46.5 dB, i.e. near-silence but a real track). Always probe the produced file, strip with `ffmpeg -an -c:v copy`, and verify with `volumedetect`. `-vn` drops video, not audio.
- **A loop is not seamless until it is measured.** Binding the same image to both the first and last frame (`mode: first-last-frame`, two identical references) guarantees the opening frame but not the closing one. Measured 2026-10-22 on a 15.08 s / 24 fps clip: the wrap transition differed by 1.6949 mean absolute levels against a maximum *natural* in-clip transition of 0.9067 — the single largest transition in the whole clip. The clip visibly decelerated to a near-stop and then snapped back. Use a local cross-dissolve of the last 0.5 s into the first frames (measured wrap 0.6601, with differing pixels above 4/255 dropping from 5.68% to 0.024%) and re-measure. The measurement rule and the script shape are in `skills/yt-focus-music-pipeline/references/design-mcp-execution.md`.

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

### The release package is a deliverable, not a copy of the working directory

Ship the deliverables and the evidence, not the scratch. Measured on S02-P04: the first
packaging run was 10.1 GB; after excluding test intermediates it was 5.2 GB. The whole
difference was leftovers — per-song alignment test WAVs (1.8 GB), crossfade-method test
WAVs (876 MB), superseded masters and chapter audio (1.5 GB), the previous chapter-audio
set (671 MB).

**Exclude from the package, but keep inside it:** the trimmed candidate set that the
approved selection points at, the measurement JSON, the waveform reference JSON, the
render style JSON, and the rebuild instructions for anything large. Excluding a file the
approved selection references breaks the package's own reproducibility check, so those
stay.

**Packaging order, and it is not interchangeable:**
1. build the README, the sha256 manifest and the representative stills **in the project
   directory**;
2. copy the project into the release package, sweeping the `._*` sidecar files that
   macOS creates on exFAT destinations;
3. run the package self-check against the package.
Reversing steps 1 and 2 ships a stale README and a manifest whose hashes no longer match —
measured, and it cost a full re-packaging cycle to find.

### Fill a short release with more music, never with stretched music

If the assembled master falls short of the declared length, add compatible songs rather
than time-stretching the existing ones. Measured on S02-P04: 24 songs produced 54:35
against a 60-minute declaration and a cover subtitle that promised "1 Hour"; three added
songs took it to 60:04 with the chapter arc intact. The added songs belong at the **end of
their chapter** and must not renumber the existing slots or rename their candidate files.

**🔴 標題、說明、hashtag 與 AI 揭露一律交給 `yt-publish-strategy`，不要在本 skill 自行發明格式。**

那裡有 2026-09-30 實測的競品數據與官方政策條文，包含：

- 標題必須是 `時長 + 功能 + 樂器`，英文為主中文為副（實測「有功能關鍵字的那支贏 56 倍」）
- 說明**最前面**必須有搜尋匹配句（官方：搜尋匹配靠 title + description + 影片內容）
- 說明必須有**創作筆記**段（政策禁止 AI 內容「沒有原創見解」，純器樂頻道靠這段自保）
- hashtag 只用需求詞與品牌詞，刪掉描述製作形式的 tag
- 上傳時務必勾 **AI use: Yes**（官方強制清單第一項是 `AI generated music`）

本頻道實測：通用關鍵字（專注音樂、古箏專注音樂、深度工作音樂…）**前 25 名完全沒有上榜**，
只在自創的「三國 專注音樂」排第一。**詩意人物標題是這頻道沒有流量的直接原因。**

## STEP 8: Quality Check

Before delivery, check:

- Final duration is greater than or equal to the requested duration when the user specifies a minimum or exact long-form release length; generate more compatible music if the available total is short.
- No vocals or spoken words are present unless explicitly requested.
- No sudden loud moments break concentration.
- At master level the loudness-evenness gate is a **3-second sliding RMS exceedance ratio
  ≤ 0.15%**, not a 100 ms window count — a 100 ms window measures the gaps between notes
  and the isolated attacks, not what a listener hears as unevenness. See
  `three-kingdoms-music-review`.
- No environmental or foley sound is present. This one needs a measurement, not a caption review: locate the quietest sustained passage and read the 10-16 kHz floor there, using one-second sub-windows and taking the minimum so instrument attacks do not masquerade as a bed. A floor near digital silence argues against a continuous bed; a raised floor can be cymbals, tape colour or a real noise layer, and only listening separates them.
- No low-frequency content that ignores the arrangement. A 20-60 Hz level identical in the intro and the outro is a fixed bed; a level that moves with the passage is authored content.
- Visual assets remain legible at thumbnail size.
- The cover and video still feel like the same release family.
- The release can be reused later as part of the same Three Kingdoms archive.

Route each item to the right instrument. Loudness, peaks, band levels, dynamics and duration come from `three-kingdoms-music-review`'s `scripts/measure_audio.py`. Vocals, instruments and whether the emotional arc landed come from listening, and are labelled as such. See [three-kingdoms-music-review](../three-kingdoms-music-review/SKILL.md) for the routing rules and the recorded model failures that justify them.

- If a cue contains vocals when vocals were not requested, check first whether the route can set the instrumental flag. Regenerating with better wording does not fix a route that lacks the control.

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
