---
name: three-kingdoms-vocal-single
description: >-
  Plan and complete Three Kingdoms character-vocal single packages with
  reusable fictional singing-voice guidance, reviewed original lyrics, a
  roughly three-minute full-song video branch and/or a 20–45 second YouTube
  Short branch, including approved storyboard images for external video
  generation. Use for character songs; provider-selectable music branches
  include MiniMax Music 3.0 and Google Gemini API / Lyria 3.5. Do not use for
  instrumental long-form mixes or generic non-Three-Kingdoms music.
---

# Three Kingdoms Vocal Single

Read [Codex runtime guidance](../../CODEX.md) before using this skill. Resolve bundled skills and resources relative to this installed package.


Create one reusable `角色人聲單曲企劃包`. The core is one song identity tied to
one Three Kingdoms character and one versioned fictional singing-voice profile.
The package can select `full-song-video`, `youtube-short`, or `both` as output
branches. A full-song video targets roughly three minutes in 16:9; a Short is
20–45 seconds in 9:16 and uses a selected interval from the same approved song
audio. A single external video clip is at most 15 seconds, although shorter
clips are allowed.

The Skill owns discovery, lyrics, specifications, reusable English prompts,
storyboard-image generation, storyboard approval records, copy-ready handoff
materials, and QA. The selected external generator—MiniMax Design, MiniMax Music 3.0
API/runtime, or Google Gemini API / Lyria 3.5—remains responsible for music
generation and song candidate selection; video generation, clip assembly,
caption post-production, and publication also remain external. Never claim that
this Skill generated, mixed, assembled, uploaded, or published external media.

## Local context and routing

When the current repository contains `CONTEXT.md`, `AGENTS.md`, character
indexes, `docs/adr/`, or an asset index, read the relevant parts first. In the
`3kingdomsFocus` repository, preserve the existing long-form instrumental
boundary and treat `docs/adr/0014-add-character-vocal-short-series.md` and
`docs/adr/0015-separate-singing-voice-assets-from-speech-voice-ids.md` as
domain decisions. The Skill remains usable without those files.

Classify the request before asking questions:

- **Idea discussion** — run dynamic discovery and create or update
  `.scratch/<feature-slug>/discovery.md` when a meaningful idea exists.
- **Confirmed brief** — summarize the brief in Traditional Chinese and request
  the explicit gate `確認規格` before creating lyrics, prompts, or storyboard
  images.
- **Resume** — inspect the named `S01-Vxx`, language version, slug, asset, or
  recorded state and continue only at its allowed next gate.
- **Asset import** — preserve the supplied external file, create metadata and a
  new version, inspect it, and return to the appropriate approval gate.
- **Revision** — create a new version for every material lyrics, prompt,
  storyboard, voice asset, copy, or media-record change; keep old versions.

Facts are found in the workspace, not requested from the user. Inspect
character indexes, character-card versions, existing voice indexes, package
files, image dimensions, and current states yourself. Ask the user only for
creative or approval decisions that cannot be discovered locally.

If the requested character has no usable character card in the workspace,
stop at `character-reference-pending` and ask the user to provide one or
explicitly authorize creating a candidate reference. Never silently invent a
new visual identity or treat a newly generated candidate as approved. When a
usable card is supplied or an authorized candidate is created, record its
version and return to `idea-discussion` or `spec-ready` as appropriate.

## Discovery interview

Use a dynamic frontier. In each round ask only unresolved decisions whose
prerequisites are settled, normally three to five questions. Number each
question, provide a recommended answer, and wait for the user's answers before
opening the next frontier. Keep the user's conversation in their language;
human-facing project documents use Traditional Chinese and external-generation
prompts use English.

Resolve, when relevant:

- character slug and exact character-card version from the existing library;
- reusable role voice profile and whether its singing reference audio is
  `approved`, `candidate`, or `pending`;
- song language version, character point of view, world mode, Three Kingdoms
  anchor, and historical claims needing verification;
- song purpose, emotional lane, genre, tempo or pulse, instruments, density,
  vocal technique, complete song structure, and hard sound boundaries;
- original lyric direction, title candidates, and the exact chosen bilingual
  title;
- selected output branches, full-song and Short relationship, Short audio
  selection, caption choice, and external handoff plan;
- full-song and Short visual anchors, scene/action, palette, aspect ratio,
  clip timeline, storyboard units, continuity anchors, and transition intent.

Allow deliberate `modern-hybrid` and `modern-reimagining` concepts, but make
the choice explicit. Do not turn an unmarked historical scene into a modern
scene. Verify explicit historical events, relationships, quotations, places,
and objects when they are presented as factual; poetic character
interpretation remains creative content.

## Domain boundaries

- This is a separate character-vocal series under the Three Kingdoms channel.
  It does not relax the no-vocal boundary for first-season long-form
  background-music content.
- The core is a character-vocal single, not a video aspect ratio, clip, or
  playlist. Do not create a new song identity for its full-song and Short
  branches.
- A complete song means reviewed original lyrics and a singable structure, not
  merely a three-minute duration. Use meaningful sections such as verse,
  pre-chorus, chorus, bridge, or an equivalent intentional structure.
- The default sung language is Traditional Chinese. English, Korean, and
  other languages are separate language versions with their own lyrics,
  pronunciation guidance, and delivery constraints. Reuse visual storyboards
  only when the language change does not alter mouth movement, gesture,
  captions, or cultural context.
- The default lyric voice is first-person character perspective. Modern
  language is allowed when the specification declares a hybrid or reimagined
  world mode.
- A speech `voice_id` is not a singing voice control. Describe singing through
  the role voice profile, language-specific singing guidance, and approved
  singing reference audio when available. State consistency as a target, never
  as a guarantee of identical generated timbre.

- Google Gemini API / Lyria 3.5 is an optional music-generation branch:
  `lyria-3.5` creates full songs and `lyria-3-clip-preview` creates fixed
  30-second tests. It accepts documented text or text-plus-image inputs, not
  audio-reference conditioning. Its singer is descriptive and may vary between
  calls, so it cannot satisfy a hard fixed-singer requirement by itself. When
  stable character singing identity is required, route to a generator that
  explicitly supports authorized audio conditioning or keep Lyria as a
  musical/arrangement candidate only. Never represent a voice anchor as
  deterministic Lyria conditioning.

- Playlist curation and cover production are outside this Skill's core. Keep
  single-song metadata ready for a future playlist workflow and hand off cover
  work to the existing video-project workflow when explicitly requested.

## Specification and approval gates

Do not create lyrics, prompts, or storyboard images until the user approves the
settled brief with `確認規格` or an unmistakable equivalent. Preserve the
following package states:

```text
idea-discussion
→ character-reference-pending? → idea-discussion
→ spec-ready
→ lyrics-review
→ lyrics-approved
→ voice-profile-approved
→ voice-reference-audio-review? → voice-reference-audio-approved?
→ prompt-review
→ prompts-approved
→ storyboard-full-song-review? → storyboard-full-song-approved?
→ storyboard-short-review? → storyboard-short-approved?
→ package-completed
```

The optional storyboard branches are required only for selected output
branches. External media is reviewed separately:

```text
audio-review → audio-approved
full-video-review → full-video-approved
short-video-review → short-video-approved
caption-review → caption-approved
```

Use these user-facing approval phrases where applicable:

- `確認規格`
- `lyrics 已確認`
- `voice-profile 已確認`
- `批准 voice-reference-audio-v1`
- `prompt 已確認`
- `批准 storyboard-full-song-v1`
- `批准 storyboard-short-v1`
- `package 已完成`
- `批准 audio-v1`
- `批准 full-video-v1`
- `批准 short-v1`
- `批准 caption-v1`

`package-completed` means the selected local package artifacts, lyrics,
prompts, approved storyboards, copy, and QA record are complete. For a
selected Short whose canonical audio is not yet approved, record
`short-selection-status: planned` and `short-delivery-status: pending-audio`;
the package may be locally complete, but the Short's time range is not
canonical or ready for external delivery. After `audio-approved`, finalize the
time range, recheck or regenerate only the dependent Short prompt, timeline,
storyboard, copy, and QA, mark the package `package-revision-required` while
those artifacts are under review, then return that branch and the package to
their approval states. It does not mean external media was generated or
published. If no singing reference audio exists, preserve
`reference-audio-status: pending`; exploratory generation is allowed, but a
stable singer identity has not been verified.

The optional reference-audio gate is omitted, not failed, while
`reference-audio-status: pending`. A text profile can be
`voice-profile-approved` without implying that reusable singing reference
audio is approved. When reference audio is later supplied, use
`voice-reference-audio-review → voice-reference-audio-approved` and record
`批准 voice-reference-audio-v1`.

## Package layout

Use a collision-free `S01-Vxx` single ID. Keep language versions visibly tied to
that ID, for example `S01-V01-zh-Hant`, `S01-V01-en`, and `S01-V01-ko`.

In the `3kingdomsFocus` repository, use:

```text
.scratch/<feature-slug>/
├── discovery.md
├── spec.md
├── master-prompt-v1.md
├── lyrics-v1.md
├── music-prompt-v1.md
├── music-generation-manifest-v1.md # candidate runs and prompt-lock records
├── full-song-video-prompt-v1.md
├── short-video-prompt-v1.md
├── full-song-storyboard-v1.md
├── short-video-storyboard-v1.md
├── short-selection-v1.md          # when a Short branch is selected
├── audio-review-v1.md              # when external song candidates return
├── youtube-copy-v1.md
├── qa.md
└── caption-plan-v1.md             # only when captions are enabled

assets/vocal-singles/S01-Vxx/<language-version>/
├── storyboards/
│   ├── full-song/
│   └── short/
└── external-media/
    └── audio/
```

Keep `assets/voices/index.md` as the reusable voice-asset index. Store a
versioned character voice profile under:

```text
assets/voices/<character-slug>/
├── <character-slug>-voice-profile-v1.md
├── <character-slug>-voice-anchor-pack-v1.md
└── audio/
    ├── <character-slug>-voice-reference-v1-source-user.<ext>
    └── <character-slug>-voice-reference-v1.md
```

Never overwrite a user-supplied source. Keep original external files and
normalized delivery copies as separate versions. A voice reference file and a
single-song vocal result are different asset classes:

- **Voice reference audio** is reusable across songs only after provenance,
  rights, quality, and human approval.
- **Song audio** belongs to one song and language version and never silently
  updates the global character voice profile.

For every imported external audio asset record the provider, creation time,
language, related profile or song prompt version, format, duration, checksum,
original path, rights confirmation, and approval state. Use
`voice-rights-confirmed` before approving reusable voice reference audio. Do
not automatically commit or push large external media; metadata and approval
records may be tracked separately when the user chooses.

Keep text-profile approval separate from reference-audio approval. A profile
may be `voice-profile-approved` while
`reference-audio-status: pending`; reusable reference audio needs its own
`voice-reference-audio-review → voice-reference-audio-approved` transition.
Song candidates use `audio-review → audio-approved` and never update the global
voice profile.

When external song candidates return, `audio-review-v1.md` records one row per
candidate with `candidate_id`, provider and external task reference,
`creation_time`, original source path, language, duration, audio format, source
prompt version, generator interface, prompt schema, prompt token or character
count, seed and generation settings, `max_new_tokens` or `audio_duration` when
applicable, character voice profile version, lyric completeness,
pitch/range, vibrato, sustain, articulation, breath, dynamics, emotion,
technique, timbre consistency, selection or rejection reason, checksum, rights
status, reviewer, explicit `approval_state`, approval phrase, and selected
canonical candidate. A candidate is canonical only after `批准 audio-v1` and
`approval_state: approved`.

## Prompt package

Create the following artifacts for the selected branches. Human-facing
explanations use Traditional Chinese; external-generation prompt text uses
English; `lyrics-v1.md` preserves the actual selected sung language.

1. **`master-prompt-v1.md`** — one concise, language-neutral content-and-
   context prompt. It states what the song and video are about, the character,
   Three Kingdoms situation, world mode, use case, emotional direction, and
   overall visual intention. It is the shared context for MiniMax Design, not a
   replacement for detailed prompts.
2. **`lyrics-v1.md`** — the exact lyrics in the selected sung language, a
   Traditional Chinese explanation when useful, song section labels, character
   and world-mode notes, singability checks, a pronunciation and prosody lock
   when the language needs one, historical-source notes, and revision history.
   Do not treat MiniMax candidate lyrics as local final lyrics.
3. **`music-prompt-v1.md`** — one model-specific music handoff for this single,
   keeping the master context, exact lyrics, section structure, and generation
   settings auditable. For MiniMax Music 3.0 it must contain separate
   `lyrics / input` and `music description / instructions` payloads; for
   Lyria it must contain one `input` payload, `model-id`, and the requested
   output settings. Both branches must record the character voice profile,
   language and pronunciation guidance, complete arrangement arc, high-impact
   negative sound boundaries, API or UI settings, and a copy-ready delivery
   block. Never claim that a speech `voice_id` controls the singer.
4. **`full-song-video-prompt-v1.md`** — the shared context, 16:9 full-song
   visual direction, continuity anchors, and one copy-ready delivery prompt
   per `clip_id`.
5. **`short-video-prompt-v1.md`** — the shared context, 9:16 Short direction,
   selected audio interval, hook, continuity anchors, and one copy-ready
   delivery prompt per `clip_id`.
6. **`youtube-copy-v1.md`** — separate full-song and Short sections using the
   same official bilingual song title, with output-specific title suggestions,
   descriptions, hashtags or tags, opening hook, credits, and relationship
   copy. It never performs upload or publication.

Keep the short master prompt canonical. Specialized files may include a
copy-ready rendering of it for easy handoff, but any mismatch must be resolved
against `master-prompt-v1.md`.


### Google Gemini API / Lyria 3.5 music-prompt construction

When this provider is selected, record
`generator-interface: Google Gemini API / Lyria 3.5` and do not map the
MiniMax two-field payload onto Lyria.

- Use `model-id: lyria-3.5` for the full-song branch. Use
  `lyria-3-clip-preview` only for a fixed 30-second prompt test, never as the
  final full-song source.
- Build one copy-ready `input` prompt, or a text-plus-image input list with
  up to 10 approved visual references. Keep musical directions in English and
  preserve the exact approved lyrics in the selected sung language with
  section tags such as `[Verse]`, `[Chorus]` and `[Bridge]`. Include
  duration wording and timestamps as guidance for the song structure.
- Include the fictional singer's register, timbre, diction, phrasing, breath,
  vibrato, harmony and section-specific delivery as descriptive instructions,
  but record `voice-control: descriptive-only` and
  `reference-audio-conditioning: unsupported-in-documented-input`. Do not
  name or imitate a real singer. If fixed identity is a hard requirement,
  stop the Lyria final branch and ask the user to accept the limitation or
  choose another authorized workflow.
- Use the Python `google-genai>=2.3.0` SDK with `GEMINI_API_KEY`, or the
  documented REST interface, only when the user explicitly requests local
  execution. Otherwise hand off the prompt and settings; never put the key in
  project files.
- Preserve Base64-decoded `output_audio.data` and returned `output_text`
  when present. The default output is MP3; if WAV is requested through the
  current official `response_format` schema, inspect the bytes and record
  actual format, duration and 44.1 kHz stereo properties when available.
- Treat every call as an independent candidate because results can vary and
  multi-turn editing/refinement is not supported. Do not use interaction
  history as if it were voice locking. Record the SynthID watermark and the
  provider safety boundary: named artist voices and copyrighted lyrics are not
  acceptable requests.

See the [Lyria 3.5 music-generation guide](https://ai.google.dev/gemini-api/docs/music-generation)
and [Interactions API](https://ai.google.dev/gemini-api/docs/interactions-overview).

### MiniMax Music 3.0 music-prompt construction

When the target is MiniMax Music 3.0, record
`generator-interface: MiniMax Music 3.0` and build the handoff as two
complementary fields. The model card defines `lyrics` / API `input` as the
words and macro section structure, and `music description` / API `instructions`
as the style, emotion, vocal performance, instrumentation, arrangement and
production direction. Keep those responsibilities separate; do not hide
production notes, negative constraints or scene prose inside the lyrics field.

1. **`lyrics / input`** — paste the exact approved lyrics from `lyrics-vN.md` in
   the selected sung language. Put supported section tags on their own lines,
   such as `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`,
   `[Bridge]`, `[Instrumental]`, `[Solo]`, and `[Outro]`. Use only the tags that
   match the approved song structure, keep repeated sections explicit, and do
   not use ellipses, scene descriptions, arrangement notes, or a list of
   instruments as filler. For an instrumental opening or break, use the
   appropriate tag and leave that section lyric-free. Keep the lyric text
   unchanged between candidate generations; a lyric revision is a new prompt
   version and a new audio review.
2. **`music description / instructions`** — write one English Structured
   Caption with the following visible headings:

   - `Global Metadata`: genre and subgenre, historical or contemporary
     influence when relevant, BPM or a narrow BPM range, time signature, key and
     scale, target song duration, sung language, listening scenario, production
     character, and a time-ordered emotional progression. State how the song
     moves from opening restraint through verse, pre-chorus, chorus, bridge or
     instrumental break to its final resolution; do not use contradictory mood
     labels.
   - `Vocal Details`: the approved fictional singer role and character voice
     profile, perceived age and gender presentation, register and practical
     range, timbre, diction and pronunciation priorities, phrasing, consonant
     clarity, breath placement, vibrato, sustain, onset, ornamentation, and
     section-specific delivery. Specify where the lead is intimate, restrained,
     conversational, lifted, powerful, or softened. State harmony and backing
     vocal entry, voicing, octave or interval relationship, and whether ad-libs
     are allowed. Describe vocal effects such as room, delay, or restrained
     tuning only when they serve the approved sound. Never name or imitate a
     real singer, and never use a speech `voice_id` as singing control.
   - `Arrangement`: the primary and secondary instruments, groove, bass and
     low-end behavior, percussion, ornamental textures, and spatial effects,
     followed by a time- or section-ordered map. For every major section state
     which instruments enter, layer, transform, recede, or stop; how density and
     energy change; how the hook and harmonic identity remain recognizable; and
     how the ending resolves. Tie vocal delivery, harmony, dynamics, and
     instrumental changes to the same section map instead of listing unrelated
     adjectives.

Use this copy-ready shape in `music-prompt-vN.md`, replacing every placeholder
with project-specific values and leaving the headings visible:

```text
generator-interface: MiniMax Music 3.0

lyrics / input:
[Intro]
[approved lyrics for this section]
[Verse]
[approved lyrics for this section]
[Pre-Chorus]
[approved lyrics for this section]
[Chorus]
[approved lyrics for this section]
[Bridge]
[approved lyrics for this section]
[Final section tag from the approved structure]
[approved lyrics for this section]

music description / instructions:
Global Metadata:
Genre/subgenre: [specific genre and subgenre].
BPM: [number or narrow range]. Time signature: [meter]. Key/scale: [key and scale].
Target duration: [duration]. Sung language: [language].
Listening scenario: [use case]. Production profile: [sonic character].
Emotional progression: [opening] → [development] → [climax] → [resolution].
Melodic profile: [comfortable range, contour, and memorable chorus hook].
Harmony: [tonal center, chord motion, tension, and cadence; keep flexible if unknown].

Vocal Details:
Lead: [fictional role voice profile, register, range, timbre].
Pronunciation lock: [only critical readings and tone-melody exceptions].
Delivery map: [section-by-section phrasing, breath, articulation, dynamics,
vibrato and sustain]. Harmony/backing vocals: [where, how, and how many layers].
Effects: [only approved restrained effects].

Arrangement:
Core instruments: [primary and secondary hierarchy]. Groove/low end: [details].
Melody/harmony support: [how instruments support the lead and hook without masking diction].
[0:00–0:15 Intro]: [entries, exits, vocal state, density, spatial field].
[Verse 1]: [entries, exits, vocal state, density, spatial field].
[Pre-Chorus]: [development and lift].
[Chorus]: [fullness, hook support, vocal and harmony expansion].
[Bridge or Instrumental]: [contrast and controlled reset].
[Final section/Outro]: [resolution, tail, and final exits].
Hard boundaries: [only high-impact prohibited sounds or performances].
```

The template is a structure, not a request to copy all sections into every
song. Keep the arrangement map proportional to the actual lyric structure and
make each section earn its instructions. Keep negative boundaries short and
specific; put them in `music description / instructions`, not in the lyrics.

Give every music prompt a visible priority block so detail does not weaken the
core identity:

```text
Must keep: character, language, approved lyrics, fictional voice profile,
core melody or hook direction, and world mode.
Controlled: BPM, meter, key/scale, section structure, vocal range, and primary
instrument hierarchy.
Flexible: fills, ornaments, secondary textures, and small transition details.
Avoid: only high-impact wrong vocals, wrong language, prohibited techniques,
unapproved instruments, or unwanted production artifacts.
```

Keep `Must keep` and `Controlled` short and internally consistent. Let
`Flexible` remain generative; do not turn the prompt into an impossible note-
by-note score. Put `Avoid` in `music description / instructions`, not in the
lyrics payload.

For the SGLang-compatible API, map the fields as `input` = lyrics and
`instructions` = music description, set `response_format: wav` and
`stream: false`, and preserve a seed when the interface supports one. For a
Diffusers-style interface, record the corresponding `lyrics`, `prompt`, and
`audio_duration` parameters instead of mixing parameter names across examples.
`max_new_tokens` is a cap on audio frames at 25 frames per second, not a
guaranteed duration: start with `round(target_seconds × 25)` (about 4,250–4,750
for a 2:50–3:10 song) and measure the returned file. Keep the request within
the model's five-minute complete-song target and its documented acoustic-frame
limit. Record the actual settings and output, not only the intended values.

Treat the documented 5,000-token limit as applying to the complete textual
handoff unless the selected interface exposes a different measured budget.
Leave headroom for the exact lyrics and substituted Structured Caption. Do not
reuse the old MiniMax Design 2,000-character rule for Music 3.0. If the target
is MiniMax Design or another UI with a separate limit, create a compact
delivery rendering, measure the actual substituted plain text including
whitespace, and record that UI limit and count separately; never claim that the
Music 3.0 token limit is the UI limit without evidence.

The optional `music-caption-rewriter` may expand a concise draft into a
Structured Caption, but it is not an approval authority. Compare its result
against the approved genre, tempo, key, language, voice profile, lyrics,
section arc, instrument list, vocal constraints and negative boundaries. Remove
invented singers, lyrics, instruments, effects or sections before handoff.

Music 3.0 is generative control, not a strict score renderer. After every
external candidate returns, measure duration and inspect lyric completeness,
section order, melody and pitch behavior, pronunciation, vocal timbre,
breathing, vibrato, sustain, diction, harmony, instrumentation, emotional arc,
tempo or key when measurable, clipping and unwanted sounds. Record mismatches
and retries in `audio-review-vN.md`; prompt approval never implies audio
approval.

For current model behavior and limits, consult the official [MiniMax Music 3
model card](https://huggingface.co/MiniMaxAI/MiniMax-Music3), its
[limitations](https://huggingface.co/MiniMaxAI/MiniMax-Music3#limitations), and
the [MiniMax Music 3.0 announcement](https://www.minimax.io/blog/minimax-music-3-0-next-generation-open-weights-production-ready-versatile-music-model).

If MiniMax Design has a current text limit, measure the actual substituted
plain-text delivery string after removing Markdown headings, code fences, and
operating notes. Never invent a limit. When the limit matters, verify it from
the current MiniMax interface or authoritative documentation available in the
environment; if neither is available, record the limit as unknown and keep
the delivery string compact without claiming a numeric threshold. Compress
repetition before removing identity, language, lyrics, voice, world mode,
timing, or safety constraints.

For every song, `spec.md` must identify `generator-interface`, `model-id`,
the current `music-prompt-vN.md` version, `prompt-schema`,
`execution-mode`, target duration, candidate count, and the generation
settings needed to reproduce or audit the request. For MiniMax Music 3.0,
also record the measured combined text-token count when available, the
`input`/`instructions` mapping, seed, `max_new_tokens` or
`audio_duration`, `response_format`, streaming mode, actual returned format,
and the external candidate-review state. For Lyria, record the exact `input`
text or multimodal-input manifest, requested `response_format`, actual
returned format, actual duration, `output_text` capture status, and the
external candidate-review state. Never mark a prompt `approved` as an audio
result; `audio-approved` still requires human review of a returned candidate.
For Traditional Chinese or another tonal language, also record the
pronunciation-lock status and path. When stable character singing identity is
required, record the voice-anchor-pack version and status; when candidates are
generated, record the current music-generation-manifest version and path.

### Prompt lock and candidate generation manifest

Before the first candidate is generated, freeze the exact approved lyrics,
music description or provider input, voice-profile version, world mode,
interface, model ID and candidate count. Create
`music-generation-manifest-v1.md` and record one entry per run with
`generation_id`, `candidate_id`, prompt version, provider/model ID, lyrics
hash when applicable, MiniMax instructions hash when applicable, Lyria input
and image-reference hashes when applicable, prompt token or character count,
interface, creation time, seed or variation settings, requested response
format, actual output path/format/duration, output hash and review state. Hash
the actual substituted payload(s), not a template with unresolved placeholders.

Use three candidates by default for the first song-generation pass unless the
specification records a different count. Send the identical approved provider
payload to every candidate; for MiniMax this means both lyrics and music
description, while for Lyria it means the single `input` payload and the same
image references. Vary only a supported seed or explicitly recorded variation
setting. Do not change lyrics, pronunciation notes, section order, voice
profile or arrangement between candidates. A changed payload creates a new
prompt version and a new review set.

## Lyrics, voice, and audio workflow

Write original lyrics from the approved character, anchor, world mode, and
song purpose. Review sentence length, breath points, vowel/consonant density,
pronunciation, difficult syllables, range load, chorus function, and whether
the lyric is realistically singable. After external audio returns, also check
pitch and range, vibrato, sustain, articulation, breath, dynamics, emotion,
technique, timbre consistency, lyric completeness, and language clarity.
Also verify the returned file's duration, sample rate, channel layout, bit
depth, sample peak or clipping, loudness consistency, silence or abrupt cuts,
and severe rendering artifacts. Treat a wrong reading of a pronunciation-locked
word as a critical audio failure even when the overall performance sounds good.

Use a reusable role voice profile with:

- fictional singer name;
- perceived age and gender presentation;
- bright or dark timbre direction;
- range and register;
- singing languages;
- style and phrasing;
- articulation and pronunciation;
- vibrato and breathiness;
- common emotional range;
- vocal techniques and prohibited traits;
- language-specific singing supplements;
- reference-audio status and rights status.

### Pronunciation and prosody lock

For Traditional Chinese or any other tonal language, add a pronunciation lock
to `lyrics-vN.md` before `lyrics 已確認`. Review every character in semantic
context and record a table with `section`, `line`, high-risk word or character,
intended reading, pinyin or Zhuyin when useful, lexical tone, syllable count,
breath or sustain note, melodic-risk note, and review status. Explicitly resolve
every polyphonic character (`多音字／破音字`); an unresolved reading is a lyric
gate failure, not a generation detail to leave to chance.

For each line, check whether the planned melody, sustained note, stress, or
melodic rise/fall could obscure the lexical tone or change the word's
intelligibility. If the conflict matters, choose one deliberate fix before
prompt approval: rewrite the lyric, change the intended melodic contour, move
the stressed syllable, or record a reviewed expressive exception. Do not assume
Music 3.0 will infer the intended reading from context every time.

Keep the `lyrics / input` payload in the selected written language and original
characters. Put pronunciation aids in the pronunciation notes or
`music description / instructions` only when they clarify a genuinely risky
word; never replace the complete lyric with pinyin or Zhuyin. The approved
pronunciation lock must be copied into `Vocal Details` as a concise list of
critical readings and section-specific diction instructions.

Reference audio should, when available, use one consistent generated singer,
stable melody, low/mid/high range, varied vowels and consonants, no other
singers or harmonies, no distracting accompaniment, and restrained effects.
Save its generation record and preserve the original. This is a consistency
aid, not a deterministic singing model.

When stable character singing identity matters, create
`<character-slug>-voice-anchor-pack-vN.md` beside the voice profile. It defines
short approved calibration phrases or reference clips for low, middle and
high register; soft, neutral and intense delivery; sustained vowels;
consonant-heavy diction; and any approved pronunciation-critical words. Keep
the melody and accompaniment of calibration clips controlled, preserve their
source and checksums, and compare every candidate against the same anchor
dimensions. A voice anchor is a review reference, not deterministic conditioning
unless the selected generator explicitly supports audio reference input.

For a candidate set, submit the same approved `lyrics / input` and
`music description / instructions` for every candidate. Vary only a supported
seed or explicitly recorded generation setting. Keep the lyrics, voice profile,
language, section map, and musical brief fixed so the review compares
interpretations of one song rather than different songs. If the result has
missing lyrics, an unapproved vocal identity, an unintended duet, or a broken
section arc, record the failure in `audio-review-vN.md` and create a new prompt
version before retrying; do not silently edit the approved brief.

Use this default candidate scorecard unless `spec.md` records another weighting:

| Dimension | Weight | Critical failure examples |
| --- | ---: | --- |
| lyric completeness, pronunciation and prosody | 30 | missing line, wrong polyphonic reading, unintelligible key word |
| fictional voice identity and vocal control | 25 | voice drift, unintended duet, wrong register or prohibited technique |
| melody, hook and singability | 15 | weak chorus hook, broken phrasing, unusable range |
| structure, emotion and arrangement | 20 | missing section, flat arc, wrong instrument hierarchy |
| technical audio quality | 10 | clipping, severe artifact, corrupt or unexpected format |

Any critical failure rejects the candidate regardless of its total score. Keep
the score and evidence for every candidate, preserve ties as ties, and give a
recommendation without silently selecting the canonical file. The user still
must approve the exact candidate with `批准 audio-v1`.

Use this minimal recovery matrix when a candidate fails:

| Failure | First revision target | Preserve |
| --- | --- | --- |
| wrong 多音字／破音字 or tone intelligibility | pronunciation lock, lyric wording, or `Vocal Details` diction note | approved song identity and unrelated arrangement |
| missing, reordered or altered lyric | section tags, explicit repeated lines, line length and `lyrics / input` | voice profile and musical brief |
| voice drift, duet, or wrong register | `Vocal Details` and voice-anchor comparison | exact lyrics and section map unless independently failed |
| weak hook or buried chorus | melodic hook direction, chorus lift, vocal layering and arrangement map | pronunciation lock and core voice identity |
| flat or rushed emotional arc | section timing, density, dynamics and instrument entries/exits | approved lyrics and language |
| wrong genre or dominant instrument | `Global Metadata` and primary instrument hierarchy | character, lyrics and voice profile |
| clipping or severe rendering artifact | generation settings or candidate replacement; retain the source record | prompt content unless the prompt caused the failure |

Every material recovery change creates a new prompt version and candidate review;
do not patch a failed candidate into approval by editing only its review note.

The Short selection is finalized only after a human approves the canonical
song audio. Record the exact start time, end time, duration, song section, hook
reason, and source audio candidate in `short-selection-v1.md`. Planned timing
before audio approval must be marked `planned-selection`, not treated as
canonical or ready for external delivery.

When an approved audio candidate or its timing changes, update
`audio-review-v1.md` and `short-selection-v1.md`. Re-review the Short delivery
prompt, Short storyboard timeline, affected storyboard units, Short copy, and
caption plan if enabled. A full-song audio change also triggers a full-song
timeline and caption recheck when their timing depends on the changed audio.

## Storyboard image workflow

Generate storyboard image candidates only after `prompt 已確認` and the
selected output branch's visual brief is settled. Use the image-generation
capability available in the current environment, and read its applicable
instructions before generating images. Use the approved or explicitly
permitted character-card version as visual reference; do not reproduce its
grid, labels, measurements, seals, or source-image text.

Each storyboard branch declares an image mode:

```text
storyboard-image-mode: single-frame | frame-pair
```

Use `single-frame` only when the external video provider does not require
boundary images or the project explicitly chooses a single visual reference.
Use `frame-pair` when the provider accepts or recommends a start frame and an
end frame for motion generation. The mode is part of the branch revision and
must be recorded in the branch prompt and storyboard; changing it is a
material storyboard-delivery change.

For every storyboard unit:

- assign a stable `clip_id` and version;
- set a duration no longer than 15 seconds, allowing shorter durations;
- record song start/end time and song section;
- describe action, camera, composition, transition intent, and emotion;
- in `single-frame` mode, link the reference image and its source prompt;
- in `frame-pair` mode, link one still `start-frame` and one still `end-frame`,
  plus their separate still-image prompts and the video handoff prompt;
- state the world mode and continuity anchors;
- keep the image free of title, lyric, logo, watermark, or accidental text;
- preserve original generated files and create a delivery copy separately.

Use 1920×1080 PNG delivery copies for full-song storyboards and 1080×1920
PNG delivery copies for Short storyboards. Inspect actual dimensions and
legibility. Separate full-song and Short storyboard timelines; never blindly
crop one into the other.

In `frame-pair` mode, every start and end asset is a clean static keyframe, not
a video frame export or a motion-blurred action sketch. Use this naming pattern
for delivery copies, with the original generation kept under the matching
`source/` path when applicable:

```text
<clip-id>-start-vN-delivery.png
<clip-id>-end-vN-delivery.png
```

The start and end prompts describe stable visual states; the video handoff
prompt describes the motion between them. For contiguous clips, reuse the
exact approved boundary image when one clip ends where the next clip starts:
`clip-A-end` and `clip-B-start` must point to the same approved asset rather
than two independently generated near-duplicates. A storyboard may therefore
have fewer unique stills than frame positions, but every frame position must
remain explicitly listed in its timeline and handoff record.

For any subject that changes position between a frame pair, record a feasible
screen-space path, direction, relative scale, depth plane, and occlusion
change in the video handoff prompt. If an endpoint would require the subject
to appear from outside the visible scene, jump from distant to near scale, or
cross an unexplained depth or occlusion change, keep that subject anchored in
the same position and scale or add an intermediate keyframe／split the clip.
Do not rely on the video model to invent a path for a material character or
prop movement.

For continuity, carry forward the approved character identity and use an
approved preceding frame as reference when appropriate. Check face, hair,
clothing, props, setting, lighting, palette, and world mode across units. A
drifted candidate receives a new version or is rejected; it is not silently
used.

`full-song-storyboard-v1.md` and `short-video-storyboard-v1.md` must each
contain a complete timeline table, image links or frame-pair links, the image
mode, approval state, and continuity notes. In `frame-pair` mode, the table
must identify the start asset, end asset, still-image prompt, video handoff
prompt, and any shared boundary asset. A selected branch cannot reach
`package-completed` without its approved storyboard set.

## External handoff and caption post-production

The local handoff is:

```text
approved master prompt
+ branch-specific delivery prompts
+ approved storyboard delivery copies or approved start/end frame pairs
+ branch storyboard timeline
+ music-generation-manifest and audio-review record when candidates exist
+ approved canonical audio or recorded audio selection
```

For the selected music provider, include the provider-specific payload,
named interface/model, requested response format and recorded generation
settings. For MiniMax Music 3.0, include the complete `lyrics / input` and
`music description / instructions` fields; if the destination only exposes
one text box, render the two fields with visible labels, measure the UI's
actual limit, and preserve the two-field source artifact for audit. For Lyria,
include `model-id`, the single `input` text or multimodal input manifest,
the optional image references, the Interactions API/REST path and the actual
output metadata when a candidate exists.

For a `frame-pair` branch, the user supplies each clip's start-frame and
end-frame together with the matching video handoff prompt. The same approved
boundary file is supplied in both adjacent positions when clips are chained.
Frame-pair approval remains a local storyboard approval; it does not imply
that the external video exists or that `批准 short-v1` has been granted.

The user manually supplies this package to the selected external generator.
The Skill does not assume a connector, does not upload files, and does not
report external generation as completed merely because prompts or images exist.
Local Lyria execution is reported only after an explicit request, a configured
`GEMINI_API_KEY`, and a recorded returned candidate.

Initial video generation is text-free. If captions are enabled, wait until the
external video passes its own review, then create `caption-plan-v1.md` with
exact lyrics, timecodes, line breaks, language, placement, style, and a
caption QA record. Caption approval is independent; a captioned video never
retroactively approves the text-free source video.

## Validation and revisions

Before `package 已完成`, verify all of the following:

- the selected `S01-Vxx` and language version are collision-free and linked;
- the named character-card and voice-profile versions exist and retain their
  recorded statuses;
- lyrics are present, original, language-correct, structurally complete, and
  reviewed for singability and historical claims;
- for Traditional Chinese or another tonal language, `lyrics-vN.md` contains a
  pronunciation and prosody lock, every high-risk 多音字／破音字 has an intended
  reading, and any tone-melody conflict has a recorded resolution or exception;
- when stable character singing identity is required, the versioned voice
  anchor pack exists, retains its source/checksums, and its review dimensions
  are used consistently across candidates;
- `master-prompt-v1.md` is concise, current, and the shared context of all
  specialized prompts;
- `music-prompt-vN.md` contains the exact approved lyrics, selected interface
  and model ID, the provider-specific prompt schema (MiniMax's separate
  payloads or Lyria's single `input` payload), Structured Caption or equivalent
  musical headings, voice and pronunciation guidance, section-level arrangement
  map, negative boundaries, measured prompt budget when applicable, and
  generation settings;
- when targeting Music 3.0, `lyrics / input` matches the approved
  `lyrics-vN.md`, `music description / instructions` contains `Global Metadata`,
  `Vocal Details`, and `Arrangement`, and the API or Diffusers field mapping is
  recorded without mixing interfaces;
- when targeting Lyria, the manifest records `lyria-3.5` for a full-song
  request or `lyria-3-clip-preview` for a 30-second test, preserves the single
  `input` payload and actual output metadata, and does not claim fixed-singer
  or audio-reference conditioning;
- when external candidates are generated, `music-generation-manifest-vN.md`
  records one prompt-locked entry per candidate with payload hashes, model or
  interface, seed/settings, output path/hash and review state;
- every selected branch has the correct aspect ratio, prompt, timeline,
  storyboard images, clip IDs, durations, and approvals;
- every clip is no longer than 15 seconds;
- every branch records `single-frame` or `frame-pair` image mode;
- in `frame-pair` mode, each clip has a readable start and end still, each
  still has the correct branch dimensions, source/delivery provenance, and
  its own prompt record;
- in `frame-pair` mode, shared clip boundaries reuse the exact same approved
  asset, and no independently generated near-duplicate is used as the next
  clip's start frame;
- every moving subject has either an explicit feasible path between its start
  and end states or a stable anchored position／scale; unexplained appearance,
  disappearance, depth jumps, and scale jumps fail storyboard QA;
- a selected Short has either an explicitly planned, pending-audio selection or
  a canonical selection that points to the approved audio candidate; planned
  selection is not reported as external-ready;
- storyboard PNG delivery copies are 1920×1080 or 1080×1920 as appropriate;
- continuity anchors and world mode are consistent across the branch;
- captions, if enabled, are post-production artifacts with their own approval;
- imported audio preserves original files, provenance, checksum, rights status,
  and candidate／approved state;
- each Music 3.0 candidate review records the actual duration, lyric and section
  completeness, vocal behavior, pronunciation, arrangement, technical result,
  and the seed/settings used for that candidate, with scorecard evidence and
  any critical-failure decision;
- `youtube-copy-v1.md` separates full-song and Short copy while retaining one
  official song identity;
- no local document claims that external media was generated, mixed, assembled,
  uploaded, or published here;
- old versions and user-supplied sources remain present;
- text files pass `git diff --check` in a Git repository.

Every material change increments only the affected artifact's version. A
changed lyric or voice profile invalidates dependent music prompts, audio
selection, and video branches as appropriate; a localized storyboard change
does not silently rewrite lyrics or the song identity. Stop at the current
gate when a validation fails, state the concrete failure, and create a new
candidate or request the missing decision.

When an already completed package receives an upstream change, preserve the
last approved state, set `package-revision-required`, reopen only the affected
dependent artifacts, and return to `package-completed` only after those
artifacts pass their gates again. This applies to audio timing, lyrics,
language, voice profile, world mode, prompt, storyboard, caption, and copy
changes according to the dependency rules below.

Use this dependency rule when revising:

- lyrics, language, world mode, character, or voice profile changes invalidate
  dependent music prompts, audio candidates, Short selection, video prompts,
  storyboards, captions, and copy as applicable;
- a music prompt or approved song candidate change triggers audio review and
  reopens any timing-dependent Short or full-song branch;
- a pronunciation-lock change or voice-anchor-pack change reopens music prompt
  review and audio review, because it can change the sung reading or character
  timbre even when the visible lyric and title are unchanged;
- a new model version, prompt hash, seed policy, or generation setting creates a
  new manifest entry and candidate review set; never merge results from
  materially different generation conditions into one comparison group;
- a change to the generator interface, prompt schema, lyrics section map,
  Structured Caption, vocal delivery instructions, or generation settings
  creates a new music-prompt version and reopens audio review; do not treat a
  new model or field mapping as the same prompt merely because the title and
  lyrics are unchanged;
- a Short audio-window change reopens only the Short delivery prompt, Short
  timeline, affected Short storyboards, Short copy, and optional captions;
- a full-song timing change reopens full-song timeline, affected storyboards,
  full-song copy, and optional captions;
- a storyboard change reopens its branch's external video review, not the song
  lyrics or song identity;
- a caption change reopens caption review only.

The user's latest explicit decision outranks defaults. Preserve the complete
approval record and keep this Skill self-contained; it may interoperate with
the existing video-project Skill but must not require its SOP or silently
inherit its cover-only workflow.
