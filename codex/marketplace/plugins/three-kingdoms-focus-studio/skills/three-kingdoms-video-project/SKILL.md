---
name: three-kingdoms-video-project
description: >-
  Create and complete Three Kingdoms character-led video project packages from
  an early idea through approved per-song music prompts, a text-free cover, a
  titled cover, and per-chapter text-free images for chapterized music.
  Use for new or resumed Three Kingdoms focus-video concepts when the local
  deliverable is a reusable project package rather than locally generated music
  or video; approved chapter audio may be assembled locally from supplied tracks.
  Supports provider-selectable music prompts for MiniMax Music 3.0 or Google
  Gemini API / Lyria 3.5.
---

# Three Kingdoms Video Project

Read [Codex runtime guidance](../../CODEX.md) before using this skill. Resolve bundled skills and resources relative to this installed package.


This skill is self-contained. It does not require a repository SOP to run. If a
current repository contains `CONTEXT.md`, `AGENTS.md`, character indexes, or a
project index, inspect and respect them; those files refine local naming and
domain rules but are optional inputs, not runtime dependencies.

The target is one reusable `影片企劃` package. The local completion boundary is
the approved project record, the approved prompt package (a shared music master
plus one standalone prompt per declared song), an approved text-free cover, and
an approved titled cover. For a chapterized music project
(the default for long-form music), it also includes one approved text-free
image for every declared chapter and the matching chapter-image prompt artifact.
A project may omit the chapter bundle only when its spec explicitly records
that it has no chapter arc. Music generation and upload remain external
operations. Once all selected songs in a chapter have been supplied and
approved, deterministic chapter-level assembly into an uncompressed PCM WAV
and its validation are local deliverables described below. Full long-form
mixing/mastering, video generation, looping, upload, and publication remain
external unless the user explicitly expands the scope. Chapter assembly must
never be described as local audio generation.


## Music generator selection

For each declared music track, choose and record `generator-interface`,
`model-id`, `prompt-schema`, `execution-mode`, and `response-format` in
`spec.md`, `music-prompts/manifest.md`, and the candidate review record.
The provider branch changes the handoff payload and expected source format; it
does not change the specification gate, candidate review, continuity review, or
approval vocabulary.

Supported branches:

- `MiniMax Music 3.0`: retain the existing two-field
  `lyrics / input` plus `music description / instructions` workflow below.
- `Google Gemini API / Lyria 3.5`: use `lyria-3.5` for a full song and
  `lyria-3-clip-preview` only for a fixed 30-second prompt test. Use the
  Interactions API with one text prompt or a text-plus-image input list.
  Custom lyrics, section tags, timestamps, vocal direction and arrangement
  belong in that prompt. Lyria accepts up to 10 image inputs as inspiration,
  not as audio references. Its documented input does not expose audio-reference
  conditioning or a fixed singer identity.
- `manual/external`: use when the user supplies an audio file from another
  provider.

Lyria generation may be executed locally only when the user explicitly asks for
execution and `GEMINI_API_KEY` is available. Keep the key in the environment,
never in prompts, manifests or release files; otherwise create a copy-ready
handoff and do not report external audio as generated. See the [Lyria 3.5
music-generation guide](https://ai.google.dev/gemini-api/docs/music-generation)
and [Interactions API](https://ai.google.dev/gemini-api/docs/interactions-overview).

## Entry routing

Classify the user's first message before asking questions:

- **Idea discussion** — the user has a theme, character, mood, scene, or rough
  title but not a settled brief. Run the dynamic discovery interview.
- **Confirmed brief** — the user gives enough settled decisions to draft the
  package. Summarize the brief and ask for the explicit specification gate.
- **Resume** — the user names an existing project ID, slug, asset, or status.
  Inspect the package and continue from its recorded state.
- **Asset revision** — the user points to an image or asks for a localized
  change. Preserve the current approved or candidate version, create a new
  version, inspect the result, and return to the relevant approval gate.

Do not force a full questionnaire when the message is already specific. Do not
ask the user for facts that can be found in the workspace: inspect indexes,
existing prompts, asset dimensions, file names, and current statuses yourself.

## Discovery interview

Use a dynamic frontier. In each round, ask only the unresolved decisions whose
prerequisites are settled, normally three to five questions. State a recommended
answer for each question and wait for the user's answers before opening the
next frontier. Keep the user's language for the conversation; write human-facing
project documents in Traditional Chinese and external-generation prompts in
English.

Resolve, when relevant:

- working character or Three Kingdoms anchor and whether an existing character
  reference card should be used;
- listening use case, duration, morning/night/travel/focus context, and target
  emotional lane;
- music identity, instruments, tempo, density, chapter arc, and hard boundaries;
- declared chapter count, ordered chapter IDs, chapter visual arc, and how each
  chapter changes without breaking visual continuity; never assume six chapters
  when the brief declares another count;
- Chinese and English title direction, including title candidates when needed;
- cover action, setting, composition, negative space, palette, props, and future
  subtle-animation anchors;
- exact bilingual cover text and the user's approval vocabulary.
- whether the music branch needs three-candidate anchor reviews for the opening
  and chapter-core tracks, the candidate count for other tracks, and the
  acceptance rules for continuity between songs.

When the first meaningful idea exists, create or update
`.scratch/<feature-slug>/discovery.md` in a repository. It records the current
idea, confirmed decisions, open questions, rejected directions, and the next
frontier. Keep it concise; it is a working trace, not the final specification.

## Specification gate

Before creating prompts or generating an image, summarize the settled design in
Traditional Chinese and ask for the explicit gate `確認規格` (or an unmistakable
equivalent). Do not treat a compliment, a partial answer, or a proposed title
as specification approval.

After approval, create the stable project ID and package directory. In the
`3kingdomsFocus` repository, preserve the proven layout:

```text
.scratch/<feature-slug>/
├── discovery.md
├── spec.md
├── music-prompt-v1.md            # shared music master, not the only song prompt
├── music-prompts/                  # one independently usable prompt per song
│   ├── manifest.md
│   ├── continuity-map.md
│   ├── opening-core-prompt-v1.md
│   ├── chapter-01-core-prompt-v1.md
│   ├── chapter-01-track-02-prompt-v1.md
│   └── ...
├── music-review/                   # external candidate review records
│   └── <track-id>-review-v1.md
├── external-audio/                 # optional user-supplied external results
│   └── <track-id>/candidate-XX-source.<ext>
├── music-assembly/                 # chapter assembly records and QA logs
│   └── chapter-01-assembly-v1.md
├── chapter-audio/                  # locally assembled chapter WAV delivery
│   └── chapter-01-v1.wav
├── cover-image-prompt-v1.md
├── chapter-image-prompt-v1.md       # required for chapterized projects
└── chapter-images/                  # one image per declared chapter
    ├── chapter-01-v1.png
    ├── chapter-02-v1.png
    └── ...

assets/releases/S01-Pxx/
├── README.md
├── music-prompt-v1.md            # same-version shared music master
├── music-prompts/                  # same-version per-song prompt snapshots
│   ├── manifest.md
│   ├── opening-core-prompt-v1.md
│   ├── chapter-01-core-prompt-v1.md
│   ├── chapter-01-track-02-prompt-v1.md
│   └── ...
├── music-review/                   # external candidate review records
│   └── <track-id>-review-v1.md
├── music-assembly/                 # same-version chapter assembly records
│   └── chapter-01-assembly-v1.md
├── chapter-audio/                  # approved locally assembled chapter WAVs
│   └── chapter-01-v1.wav
├── cover-image-prompt-v1.md
├── chapter-image-prompt-v1.md       # required for chapterized projects
├── cover-v1.png
├── cover-titled-v1.png
├── chapter-images/                  # approved delivery copies
│   ├── chapter-01-v1.png
│   ├── chapter-02-v1.png
│   └── ...
└── later revisions with new version numbers
```

In `3kingdomsFocus`, `.scratch/<feature-slug>/` remains the canonical working
source. A completed project also gets a release handoff snapshot in
`assets/releases/S01-Pxx/`: copy the same-version `music-prompt-vN.md` and
`cover-image-prompt-vN.md` into that folder. For any project with declared music
tracks, also copy `music-prompts/manifest.md`, `music-prompts/continuity-map.md`, and
every same-version per-song prompt. For a chapterized project, also copy
`chapter-image-prompt-vN.md` and every approved delivery image into its
`chapter-images/` directory. When chapter assembly has been completed, also
copy each approved chapter WAV and its same-version assembly record into
`chapter-audio/` and `music-assembly/`. Add a `README.md` that names the project, links
the handoff prompts, identifies the approved cover versions, lists the chapter
IDs, image paths, and assembled chapter-audio paths when present, and links back
to the canonical spec. The release snapshot
is not an independent draft; when a prompt changes, create the next version in
both locations and update the README. Keep `assets/releases/README.md` and the
project index linked to each completed release package. Historical release
folders that predate the chapter-image extension are not migrated
automatically.

If another repository declares a different project layout in its context, use
that layout. If no repository conventions exist, ask once for an output root
when writing files is necessary; the workflow remains the same.

Allocate the next collision-free project ID, normally `S01-P04` after P03.
Inspect existing paths before choosing an ID. If the repository has
`docs/video-projects/index.md`, update it; otherwise create it when the first
project is completed. The index records ID, Chinese title, English title,
Three Kingdoms anchor, use case, status, and links to the package.

## Prompt package

Create the prompt artifacts required by the project topology:

1. `music-prompt-v1.md` — an English reusable master prompt for the requested
   external music generation. It defines the project-wide sonic constitution:
   a coherent family of short source cues, the declared chapter count and
   ordered chapter arc, duration arithmetic, shared anchors, and all positive
   and negative sound boundaries. Five or six chapters are common, but the
   actual declared count is authoritative; do not silently substitute a
   six-chapter arc. Do not treat this master as the only generation prompt or
   claim local audio generation. When the project contains actual songs, create
   the per-song prompt set described below. The chapter assembly workflow below
   turns approved, user-supplied song files into one local chapter WAV; it does
   not generate the songs.


### Google Gemini API / Lyria 3.5 music-prompt construction

When this provider is selected, record
`generator-interface: Google Gemini API / Lyria 3.5` and keep the model branch
explicit:

- Full-song requests use `model-id: lyria-3.5`. Use
  `lyria-3-clip-preview` only for a 30-second prompt experiment, never as the
  final full-song or long-form source. Song duration is approximate and should
  be guided with duration wording and timestamped sections, then measured from
  the returned file.
- Use the Interactions API request shape
  `client.interactions.create(model=..., input=...)`. For Python, use
  `google-genai>=2.3.0` and `GEMINI_API_KEY`; never hardcode the key.
- Use English musical directions for genre, BPM, meter, key/scale, instruments,
  mood, vocal state, structure, timestamps and hard boundaries. Preserve
  approved lyrics in their selected language in the same prompt with tags such
  as `[Verse]`, `[Chorus]`, `[Bridge]` or `[Instrumental]`. For focus
  music, explicitly say instrumental only, no vocals, no spoken words and no
  lyrics.
- Optional visual references may be sent as up to 10 image inputs. They shape
  inspiration only; they do not lock a singer or supply audio conditioning.
- Save `output_audio.data` after Base64 decoding and preserve
  `output_text` when returned. The default output is MP3; if WAV is requested
  through the current official `response_format` schema, inspect the actual
  bytes before recording the format and duration.
- Treat each request as an independent candidate. The same prompt can vary,
  multi-turn editing/refinement is not supported, and a voice description is
  descriptive guidance rather than a fixed singer. Do not request a named
  artist's voice or copyrighted lyrics; retain the SynthID watermark note.
- For long-form focus music, generate independent short Lyria tracks and use
  the existing chapter-audio assembly branch only after each source is
  available and approved. Record candidate IDs, prompt/model metadata, source
  format and actual duration for every segment.

For MiniMax Music 3.0, treat each generated cue as a complete song of no more
than five minutes, not as a request for the whole 60–75 minute mix. Keep the
long-form chapter plan in the master prompt, then generate short cues (normally
2:50–3:10) externally. After all selected songs in a chapter are available, use
the Chapter audio assembly workflow below to produce its local chapter WAV;
full long-form mixing and mastering remain external. Use the model's two
separate inputs rather than merging lyrics and musical instructions:

- `lyrics` / API `input`: lyrics are optional and section tags define macro
  structure. For instrumental focus music, use no lyric text; when the target
  interface supports tag-only input, put one tag per line such as `[Intro]`,
  `[Instrumental]`, `[Solo]` and `[Outro]`. Never put scene prose, production
  notes or negative constraints in the lyrics field.
- `music description` / API `instructions`: use a Structured Caption with all
  three sections below. Keep it in English and make the field names visible so
  the structure survives handoff between the model card, SGLang API and
  Diffusers-style interfaces.
  - `Global Metadata`: genre and subgenre, BPM, time signature, key and scale
    (or an explicit unconstrained choice), listening scenario, production
    profile, and a time-ordered emotional progression.
  - `Vocal Details`: for this focus-video workflow explicitly state
    `instrumental only; no lead vocals, backing vocals, spoken words, chants,
    lyrics or vocal effects`. For a project that intentionally includes voice,
    specify gender, timbre, delivery, harmony, backing vocals and effects here
    instead of hiding them in the arrangement prose.
  - `Arrangement`: primary and secondary instruments, the groove and bass or
    low-end behavior, percussion, textures and spatial effects, plus the
    section-level entry, layering, transformation and exit of instruments.

Write the arrangement as a temporal map, not only as adjectives. Tie each
section to a tag or time range, state what enters and recedes, and describe how
density, emotional energy and low end change while the core motif remains
recognizable. Every per-song request must select exactly one declared chapter
and exactly one variation; include the chapter's action, density and emotional
function without pasting all chapter directions into one request.

Use this compact Music 3.0 handoff shape in the prompt artifact:

```text
lyrics/input:
[Intro]
[Instrumental]
[Solo]
[Outro]

music description/instructions:
Global Metadata: [genre/subgenre], [BPM], [time signature], [key/scale], [listening scenario], [production profile], [emotional progression].
Vocal Details: instrumental only; no lead vocals, backing vocals, spoken words, chants, lyrics or vocal effects.
Arrangement: [primary and secondary instruments]; [section-by-section entry and exit]; [groove, bass, percussion, textures, spatial effects]; [chapter direction and one variation].
```

The current MiniMax Music 3.0 model card limits the tokenized text prompt to
5,000 tokens. Treat that as the hard ceiling for the final substituted music
description, leave practical headroom, and do not apply the older 1,750–1,900
character target to this interface. If the handoff target is MiniMax Design or
another explicitly character-limited interface, use a separate compact
per-song delivery string instead:

- include the master core, exactly one chapter direction and exactly one
  variation guidance; never paste all chapter directions or all variations into
  one song request;
- preserve identity, use case, instruments, tempo or pulse, density, emotional
  lane, duration strategy, instrumental-only rule and high-impact negative
  sound boundaries;
- remove repeated adjectives, explanatory prose and examples before removing
  any production constraint; count the final substituted plain text, including
  whitespace, after removing Markdown headings and operating notes; target
  1,750–1,900 characters and reject any delivery string over 2,000;
- record the selected chapter, variation and measured character count in the
  project notes. The full master remains unchanged as the reusable source of
  truth.

When handing off Music 3.0 API settings, remember that `max_new_tokens` is a
maximum number of audio frames at 25 frames per second, not a guaranteed final
duration. Use `round(target_seconds × 25)` as the starting cap: 4,250–4,750 for
a 2:50–3:10 cue and 7,500 for a five-minute ceiling. Generation may end earlier.
Record the requested cap and measure the returned file externally. The current
documented output is non-streaming 32 kHz, 16-bit stereo WAV; preserve the
actual response format in the handoff record rather than assuming the prompt
controlled it. Always invoke $music-caption-rewriter to draft the music description/instructions
field for every MiniMax Music 3.0 song prompt, including material prompt
revisions. This is required whenever MiniMax Music 3.0 is selected. If it is
missing, install it globally for Codex with:
npx skills add MiniMax-AI/MiniMax-Music3 --skill music-caption-rewriter --global --agent codex --yes
Verify that it is discoverable before continuing. If installation fails, stop at
the prompt gate and report the failure rather than claiming the rewriter was used.

Give it the approved English music brief and only the track-local context it
needs: the single chapter, single variation, target duration, approved
project/core/predecessor anchors, and required or forbidden sound details. Keep
track IDs and operational handoff metadata outside the rewritten caption. For
lyric-free cues, provide tag-only structure when the target interface supports
it and no lyric text. For songs with approved lyrics, keep that text unchanged
in lyrics/input and pass only its section tags to the rewriter; never put the
rewritten caption in lyrics/input.

Treat the three-section caption as a draft. Integrate it into the standalone
per-song prompt and preserve the visible Global Metadata, Vocal Details, and
Arrangement headings. Recheck it against the spec, approved core and
predecessor, exact chapter and variation, target duration, instrument hierarchy,
vocal rules, negative constraints, and selected interface limit. In this
focus-video workflow, preserve the explicit instrumental-only rule; remove any
invented voice or instrument, unsupported precise BPM/key, or unapproved
production claim. Restore omitted constraints, and explicitly carry the chosen
chapter function and single variation into Arrangement if the draft leaves them
implicit. For a character-limited MiniMax Design handoff, derive a compact
delivery string from the full caption and apply that interface's separate limit.

Invoke $three-kingdoms-music-review on the exact final payload before presenting
it for prompt approval. After any payload edit, review the revised version.
Caption rewriting and prompt review do not approve the prompt or generated
audio.

Music 3.0's section tags and descriptions are generative controls, not strict
symbolic guarantees. After an external cue is generated, verify its actual
duration, vocal absence or presence, section progression, required instruments,
tempo/key when measurable, and banned-sound boundaries. Record mismatches and
retries as external results; approving a prompt never implies audio approval.

The prompt artifact should include the applicable MiniMax Music 3.0, MiniMax
Design, or Google Lyria 3.5 template, the chosen interface and model ID, and
the validation fields above. Keep each model-specific branch explicit so a
character-limited delivery is never mistaken for a token-limited delivery.
For current model details, consult the [MiniMax Music 3 model card](https://huggingface.co/MiniMaxAI/MiniMax-Music3), its
[limitations](https://huggingface.co/MiniMaxAI/MiniMax-Music3#limitations), the
[MiniMax Music 3.0 announcement](https://www.minimax.io/blog/minimax-music-3-0-next-generation-open-weights-production-ready-versatile-music-model),
the [Lyria 3.5 music-generation guide](https://ai.google.dev/gemini-api/docs/music-generation),
and the [Interactions API](https://ai.google.dev/gemini-api/docs/interactions-overview).

### Per-song prompt and candidate review workflow

`music-prompt-vN.md` is the shared musical constitution: it defines the
project-wide identity, chapter arc, hard boundaries and duration arithmetic. It
is not the only prompt used for generation. Create
`music-prompts/manifest.md`, `music-prompts/continuity-map.md`, and one
standalone, paste-ready prompt file for every actual song. A per-song file may
link back to the master for audit, but it must repeat every constraint needed
to run that song; `use the master` alone is not a usable prompt.

Use stable track IDs such as `opening-core`, `chapter-01-core`, and
`chapter-01-track-02`. `spec.md` is canonical for project-level track order;
`music-prompts/manifest.md` is the detailed operational index and must mirror
that order. It must record at least `track-id`, role, chapter, sequence position,
prompt path and version, target duration, candidate count, predecessor,
successor,
anchor-track, prompt status, candidate-review status, selected candidate and
approval state. Each per-song prompt must contain:

- track metadata and the selected chapter or opening role;
- the complete provider-specific handoff: MiniMax's two `lyrics/input` and
  `music description/instructions` fields when selected, or Lyria's one
  `input` text/multimodal payload with its `model-id` and output settings;
- the shared musical anchors inherited from the master and, when available, the
  approved anchor track: BPM range, time signature, key/scale when fixed,
  instrument hierarchy,
  motif language, spatial profile, dynamic ceiling and density envelope;
- an explicit transition contract with the previous and next track when one
  exists: what is carried in, the opening texture and energy, what develops in
  the middle, how
  the ending releases, and which sound or phrase can lead into the next track;
- target duration, model/interface, candidate count and any generation
  settings that belong to the handoff. Keep audio files and external results
  separate from the prompt text.

The anchor-selection sequence is deliberate:

1. Create `opening-core-prompt-v1.md` and use that exact prompt to generate
   three candidates. These are three audio candidates for one track, not three
   different prompt files. Vary the seed only when the target interface
   supports it, and preserve each candidate's filename, seed and settings.
2. Inspect the uploaded candidates against the same rubric: project identity,
   instrumental and vocal compliance, chapter function, motif and instrument
   hierarchy, arrangement arc, technical quality, and compatibility with the
   planned next track. Rank them and make a recommendation; do not silently
   select one on the user's behalf. If the environment cannot audibly inspect
   the files, state that limitation and restrict the recommendation to available
   metadata and user-provided notes.
3. Record the candidate review in
   `music-review/opening-core-review-v1.md`, then wait for an explicit user
   selection or approval. Record the selected candidate ID, rejection reasons,
   actual measured properties and the approval phrase.
4. Create `chapter-01-core-prompt-v1.md` from the approved opening anchor,
   generate three candidates with that exact prompt, review them, and wait for
   approval. Repeat the same core-first sequence in declared chapter order;
   each chapter core inherits the approved preceding anchor while expressing
   its own chapter function.
5. Only after a chapter core is approved, create the remaining prompts in that
   chapter one song at a time. Each additional song gets its own prompt and
   uses the approved chapter core plus its immediate predecessor as anchors.
   Start with the declared candidate count (one is acceptable for a confident
   variation); if the uploaded result fails review, create a new prompt version
   or regenerate candidates without changing the approved core silently.

For every candidate review, preserve all candidates, including rejected ones,
and distinguish these states: `prompt-ready`, `candidates-requested`,
`candidates-uploaded`, `agent-recommended`, `user-approved`, and
`audio-review-failed`. Prompt approval and audio-candidate approval are
separate gates. Music generation and uploading remain external. Chapter-level
assembly is allowed only after the selected external files are available and
approved; a user-uploaded file may be inspected and assembled, but must never
be described as locally generated.

The continuity map must be concrete rather than aspirational. For each adjacent
pair, record the shared anchors, incoming carryover, outgoing handoff, planned
overlap or crossfade behavior, and the check result after both audio files are
available. A text prompt can make two songs more compatible, but it cannot
prove a seamless join before the actual files are heard and measured. Do not
claim audio continuity when only the prompt has been reviewed. Do not claim
audio-reference conditioning unless the selected interface explicitly supports
it; otherwise use textual anchors and the external review record.

2. `cover-image-prompt-v1.md` — an English prompt package with Stage 1 and
   Stage 2 exact prompts. Stage 1 must be text-free, 16:9, 1920×1080, and leave
   deliberate title space. Stage 2 must use the approved Stage 1 image as its
   primary reference and quote the exact Chinese and English text.

3. `chapter-image-prompt-v1.md` — required when the spec declares a chapter
   arc. It is an English prompt package with one independently usable prompt
   for every declared chapter, plus a shared continuity block. Every chapter
   prompt must specify:

   - the stable chapter ID and its chapter-specific visual state, action,
     composition, lighting, and emotional function;
   - the shared character identity, costume, props, environment, art style,
     palette, lens language, and aspect ratio that must remain consistent;
   - the relationship to adjacent chapter images, including a physically
     believable route when a character changes position. Do not depict a
     character appearing at an end position that has no possible path from the
     preceding state; show a walkway, boat, doorway, cut in time, or another
     stated transition when the scene requires it;
   - `16:9`, `1920×1080`, text-free output with no title, lyrics, logo,
     watermark, fake signature, or storyboard labels.

   Generate exactly one image per declared chapter. Chapter images are
   text-free visual states for chapter switching, not alternate cover versions,
   not a request to generate video, and not a replacement for either cover.
   Keep the declared chapter order and count in the prompt and project notes.

For a project without a chapter arc, omit item 3 only when `spec.md` records
`chapter-image-status: not-applicable` and explains why. For any project with
declared music tracks, the initial prompt gate presents the shared master,
track manifest, continuity map and `opening-core-prompt-vN.md`; create
downstream per-song prompts only after their anchor decisions are approved. At
each staged prompt gate, wait
for `prompt 已確認` (or a clear equivalent) before handing that prompt to the
external generator.

Keep the project brief and operating notes in Traditional Chinese. Keep the
external-generation prompt text in English. If a character reference card is
candidate or approved, preserve its version and use it as reference only; do
not silently promote, overwrite, or redesign the character asset.

For a chapterized project, `spec.md` is the canonical chapter manifest. It must
record `chapter-image-status: required`, `chapter-count`, and an ordered table
with at least `chapter-id`, chapter name, music time range or section,
chapter-specific visual state, adjacent transition note, image path, image
version, and approval state. A project without a chapter arc must instead
record `chapter-image-status: not-applicable` and the reason.

For any project with declared music tracks, `spec.md` must also record
`music-prompt-status`, `music-track-count`, and an ordered music table with at
least `generator-interface`, `model-id`, `prompt-schema`,
`execution-mode`, `response-format`, `track-id`, role, chapter, sequence
position, prompt path and version, target duration, candidate count, predecessor,
successor, anchor-track, prompt status, candidate-review status, selected
candidate and approval state.
For the opening core and every declared chapter core, the default candidate
count is three; additional tracks may use a different declared count. If the
user has not supplied external candidates, keep the candidate and continuity
states explicitly `external-unreviewed` rather than inferring approval.

For a chapterized project whose declared songs will be assembled locally,
`spec.md` must additionally record `chapter-audio-status` for each chapter,
`chapter-audio-count`, and an ordered assembly table with at least `chapter-id`,
input track IDs in order, selected candidate IDs, assembly record path and
version, output WAV path and version, source and target PCM formats, boundary
fade/crossfade plan, expected and actual duration, QA status and approval state.
Use `external-unreviewed` when any selected source file is not available; do not
create a placeholder WAV or infer that the chapter is complete.

If the user changes one prompt, revise only that artifact and increment its
version where the change is material. A change to the declared chapter count,
chapter order, shared visual anchors, or any chapter prompt requires a new
chapter-image prompt version; keep the old prompt and affected image versions.
For music, a track-local change increments only that track prompt first. A
change to a shared musical anchor, selected core, chapter order or continuity
contract invalidates every dependent downstream prompt and requires new
versions plus another candidate review; never silently propagate a changed
anchor into already approved songs.

After chapter audio assembly begins, a changed source candidate, input order,
trim, gain, fade, crossfade or target format invalidates that chapter's WAV and
requires a new assembly-record and output version. Preserve the previous
assembly record and WAV, and re-run the boundary and technical checks before
requesting chapter-audio approval again.

## Music candidate review and continuity

Use this as a staged branch for a chapterized music project when the user will
upload externally generated audio for inspection:

```text
music-prompt-review
→ opening-core-candidate-review
→ opening-core-approved
→ chapter-core-candidate-review
→ chapter-core-approved
→ chapter-track-prompt-review
→ chapter-track-candidate-review
→ music-continuity-review
→ music-selection-recorded
→ chapter-audio-assembly-review   # per chapter when all inputs are approved
→ chapter-audio-approved          # per chapter
```

This branch does not replace the cover or chapter-image approval states. It
keeps musical decisions in their own gates and never treats prompt approval as
audio approval. For each candidate set:

- send the same per-song prompt for every candidate in the set; vary only a
  supported seed or generation setting, not the musical brief;
- inspect every uploaded candidate using the same rubric: identity and
  instrument hierarchy, chapter function, emotional and density arc,
  instrumental/vocal compliance, technical quality, and incoming/outgoing
  compatibility;
- rank the candidates and give a recommendation with evidence. Wait for the
  user's explicit selection or approval before writing `user-approved` or
  using that candidate as the next anchor. An approval may use a phrase such as
  `批准 music-candidate-opening-core-02`; if the user selects by filename,
  record the exact wording and map it to the candidate ID;
- preserve candidate IDs, filenames, prompt version, seed/settings, measured
  duration and review reasons, including rejected candidates.

The opening core is the first anchor: create one `opening-core` prompt, send it
three times, review the three uploaded candidates, and record the approved
selection. Then create the next chapter-core prompt from that approved anchor;
repeat three-candidate review in chapter order. Only after a chapter core is
approved may the agent finalize the prompts for that chapter's remaining
tracks. A chapter track must identify its approved core and immediate
predecessor as anchors, its own role, and its declared candidate count.

For each adjacent song pair, review the actual boundary when both files exist:
shared BPM/meter/key or scale when fixed, motif and instrument carryover,
opening and closing energy, low-end change, reverb/spatial profile, tail or
pickup behavior, and crossfade or overlap suitability. If one file is missing,
record the continuity result as `planned` or `external-unreviewed`, never as
passed. If an approved core changes, invalidate and re-review every dependent
track before completion.

## Chapter audio assembly

Use a separate assembly branch for each declared chapter after every song in
that chapter has a user-approved candidate and its exact source file is
available:

```text
music-selection-recorded
→ chapter-audio-assembly-review
→ chapter-audio-approved
```

The assembly branch produces one chapter WAV from approved, externally
generated song files. It is local deterministic post-processing, not music
generation. Do not start it from prompt approval alone, from an unreviewed
candidate, or while any declared song in the chapter is missing. If the source
files are unavailable, keep the chapter assembly state `external-unreviewed`
and stop at the missing-input gate.

Use `not-started`, `inputs-pending`, `assembly-review`, `approved`,
`external-unreviewed` and `failed` as the chapter-audio status vocabulary. A
chapter reaches `approved` only after its WAV, assembly record and technical
and listening checks are complete and the user has approved that exact version.

For each chapter:

1. Freeze the ordered input list from `spec.md` and
   `music-prompts/manifest.md`. Never infer order from filenames or filesystem
   order. Record the selected candidate ID, original path, file hash, duration,
   sample rate, channel count and bit depth for every input. Preserve the
   supplied source files, optionally under `external-audio/<track-id>/`, and
   never overwrite or silently normalize the originals.
2. Inspect the inputs before assembly. Reject missing, duplicate, corrupt or
   ambiguous files. Convert working copies to one declared uncompressed PCM
   target only when needed. For Music 3.0 sources, the default target is
   `PCM signed 16-bit little-endian, 32 kHz, stereo`, matching the documented
   non-streaming output; retain a higher-quality common source format when the
   project explicitly requires it. For Lyria sources, record the actual
   returned MP3 or WAV and its measured 44.1 kHz stereo properties when
   available; do not apply the Music 3.0 32 kHz default by assumption. Do not
   upsample to claim quality improvement and do not pass through MP3/AAC or
   another lossy intermediary.
3. Treat WAV precisely: it is a container, not automatically a lossless codec.
   The chapter delivery must be an uncompressed PCM WAV, so the assembly step
   adds no lossy compression. A PCM conversion cannot restore quality already
   lost in a lossy source; record the actual source and target formats instead
   of calling the result lossless without qualification.
4. Resolve every internal boundary from the continuity map and the actual
   files. Choose and record one explicit mode per boundary: a phrase-aligned
   tail fade followed by the next song, a phrase-aligned crossfade with an
   overlap, or a hard cut when the chapter intentionally resets. Use the
   shortest musically natural fade that removes an abrupt cutoff; do not apply
   one blanket fade duration to every song. The final song may receive its own
   gentle tail fade when the chapter plan calls for one. Never hide a missing
   transition with an unexplained silence, jump in loudness, or duplicated tail.
5. Render `chapter-audio/chapter-XX-vN.wav` with a deterministic tool such as
   `ffmpeg` or SoX, without a lossy intermediate. Record the exact tool version,
   command or filter graph, target PCM format, each boundary mode and duration,
   any trim or gain, and the output hash in
   `music-assembly/chapter-XX-assembly-vN.md`. Do not apply normalization,
   limiting or clipping repair silently; any gain or headroom decision must be
   explicit in the assembly record.
6. Inspect the rendered file and every boundary. Verify the input count and
   order, PCM WAV format, expected duration (input durations minus declared
   crossfade overlaps and any explicitly trimmed-away time), absence of sample
   clipping,
   audible phrase continuity, and a natural chapter ending. If the environment
   cannot audibly inspect audio, report that limitation and mark the listening
   checks `metadata-only` rather than `passed`.
7. Present the chapter WAV together with its assembly record and wait for a
   separate user approval such as `批准 chapter-audio-chapter-01-v1`. A chapter
   audio approval does not retroactively approve a candidate, prompt, cover or
   video. If a source, order or boundary changes, create a new assembly version
   and re-run the affected checks; preserve the prior WAV and record.

The assembly record must include at least `chapter-id`, assembly version,
ordered input track IDs, selected candidate IDs and source hashes, target PCM
format, per-boundary mode and duration, output path, output duration, output
hash, tool/version, QA result and approval state. The chapter WAV is a local
chapter handoff; a full cross-chapter or 60–75 minute master remains outside
this branch unless the user explicitly requests that additional scope.

## Cover production and approval

Use this state machine and do not skip a gate:

```text
idea-discussion
→ spec-ready
→ prompt-review
→ prompts-approved
→ cover-stage1-review
→ cover-stage1-approved
→ chapter-images-review       # required for chapterized projects
→ chapter-images-approved     # required for chapterized projects
→ cover-stage2-review
→ completed
```

For a project explicitly marked `chapter-image-status: not-applicable`, skip
the two chapter-image states and record the reason in `spec.md`. A long-form
music project with declared chapters must not skip them.

### Stage 1: text-free master

- Generate a clean text-free 16:9 cover after the prompt gate.
- Use the approved character reference when one exists. Do not reproduce its
  grid, labels, measurements, seals, or source-image text.
- Preserve readable faces, hands, action, composition, title negative space,
  and future subtle-animation anchors.
- If the user supplies an image, view it before editing, preserve it as
  `*-source-user.png`, and never overwrite the supplied source.
- Save each generated or edited candidate with a new version. Normalize the
  delivery copy to 1920×1080 PNG and verify it before presenting it.
- Present the image and wait for explicit approval such as `批准 cover-v1`.

If the user requests a change, describe the localized edit, generate a new
version, inspect it, and ask for approval again. A failed revision stays in the
history; it is never silently replaced.

### Chapter images: one approved image per chapter

- Start only after the prompt gate and approval of the text-free Stage 1 cover,
  so the approved cover can anchor the shared visual identity.
- Generate exactly one text-free `chapter-XX-vN.png` delivery image for each
  declared chapter ID, preserving the chapter order. Do not fill missing
  chapters with duplicate images or create unlisted extras.
- Keep the same character identity, costume, environment, style, palette,
  camera language, and recurring props across the set. Make the chapter
  difference legible through the declared action, composition, light, or
  emotional state rather than unrelated redesign.
- Inspect every boundary between adjacent images. If a person or object moves
  to a new location, the pair must state a credible movement path or a clear
  temporal/spatial cut; an unexplained teleport is a failed continuity check.
- Keep every delivery image text-free, 16:9, 1920×1080 PNG. Preserve raw or
  user-supplied sources when available, and never overwrite an earlier
  candidate or approved version.
- Present the complete set with its chapter manifest and wait for explicit
  approval such as `批准 chapter-images-v1`. Approval is for the set and does
  not approve the cover images.

If one chapter is rejected, keep the approved chapters, create a new version
for the affected chapter and the chapter prompt when needed, then return to
`chapter-images-review`. If a shared anchor changes, recheck or regenerate the
whole affected set before requesting approval.

### Stage 2: titled cover

- Start only from the approved Stage 1 master.
- Preserve the approved composition, identity, expression, action, props,
  lighting, palette, and visual focus.
- Add only the exact Traditional Chinese main title and English subtitle.
- Keep the Chinese title readable and exact, including punctuation. If a visual
  effect places a glyph behind a curtain or object, preserve its legibility and
  document the localized revision.
- Reject extra words, logos, seals, watermarks, fake signatures, or material
  composition drift.
- Save a new version, inspect the actual image, and wait for explicit approval
  such as `批准 cover-titled-v1`.

Reference-based titled generation is allowed when the approved Stage 1 master
is used and the user manually checks text and composition. Deterministic human
typography is the fallback when generated typography is not exact.

## Completion and validation

After the staged music branch (when used), any required chapter audio assembly,
the chapter image set (when applicable), and the final titled cover are
approved:

1. Mark the titled image as approved and preserve all prior versions.
2. Mark the project `completed`.
3. Copy the same-version master and every per-song prompt in `music-prompts/`
   into the release handoff folder. Copy the music manifest, continuity map and
   approved candidate review records when that branch was used. For chapterized
   projects, copy every approved chapter delivery image into `chapter-images/`;
   when chapter assembly was completed, also copy each approved chapter WAV and
   its same-version assembly record into `chapter-audio/` and
   `music-assembly/`. Create or update `README.md` with both manifests. Do not
   copy or describe externally generated song files as locally generated; label
   the chapter WAV as local assembly from approved external results.
4. Update `assets/releases/README.md` and `docs/video-projects/index.md` when
   those repository indexes exist.
5. Record the approval phrase and final asset path in the spec or cover prompt.
6. State clearly that external music generation, full-length mastering, video,
   and publication work remain outside local completion; chapter-level WAV
   assembly is local only when its assembly record and approval are present.

At every gate, and again before completion, verify:

- required files exist and links point to the current project ID;
- for a chapterized project, `spec.md`, `music-prompt-vN.md`,
  `chapter-image-prompt-vN.md`, the declared chapter manifest, and the actual
  chapter image files have a one-to-one match with no missing or extra chapter;
- for a project with declared music tracks, every declared track has exactly one
  current standalone prompt file, and the music manifest agrees with its track ID,
  order, role,
  chapter, candidate count and anchor references;
- opening-core and every chapter-core candidate set has three preserved
  candidates unless the spec records an explicit exception; each reviewed set
  has a recommendation, a user decision, and a selected candidate or a clear
  failure state;
- each dependent track points to an approved core and predecessor, and the
  continuity map records incoming/outgoing handoffs plus `passed`, `planned` or
  `external-unreviewed` boundary status;
- the release handoff folder has `README.md`, same-version prompt snapshots,
  direct links to the approved cover assets, and direct links to every approved
  chapter image when applicable;
- the release handoff includes the per-song prompt directory and, when used,
  music manifest, continuity map and selection records;
- every music track records its selected provider and model ID, and a Lyria
  track records the correct full-song or 30-second-test role, actual output
  format and duration, without claiming fixed-singer or audio-reference
  conditioning;
- when chapter assembly is required and completed, each assembled chapter has
  exactly one current WAV and one same-version assembly record, with the input
  order, source hashes, PCM format, boundary fades/crossfades, duration, QA
  result and approval state agreeing with `spec.md`;
- release prompt snapshots match the canonical `.scratch/` artifacts byte for
  byte and the README links back to the source package;
- the state matches the allowed next transition;
- cover PNGs are 1920×1080 and 16:9;
- chapter delivery PNGs, when applicable, are all 1920×1080 and 16:9, are
  text-free, and have the correct chapter IDs and versions;
- the prompt files contain the correct bilingual title, declared chapter count,
  chapter-specific directions, and character reference rules;
- adjacent chapter images pass the continuity check and retain shared visual
  anchors while showing their declared chapter states;
- the approved Stage 2 image is derived from the approved Stage 1 master;
- old versions and user-supplied sources remain present;
- no local claim says that external song audio was generated or that external
  full-length mastering, video or publication was performed here; any local
  chapter WAV is explicitly identified as assembly from supplied external
  results; Lyria execution is reported only when the user explicitly requested
  it and the returned candidate is recorded;
- prompt approval, candidate selection and audio continuity approval remain
  separately recorded;
- text files pass `git diff --check` when working in a Git repository.

If a validation fails, stop at the current gate, state the concrete failure,
and create a new revision or ask for the missing decision. Do not mark the
project completed merely because a file was generated.

## Revision and scope rules

Use a new version for every meaningful change. A cover-only change keeps the
same project ID and does not require new chapter images unless it changes a
shared visual anchor. A chapter-local change keeps the same project ID and
creates a new chapter image version; a chapter-count, chapter-order, or shared
visual change updates the chapter prompt/spec and revalidates the affected set.
Reconsider the project ID only when the title identity, Three Kingdoms anchor,
listening use case, or core music/visual concept changes enough to be a
different `影片企劃`.

The user's latest explicit decision outranks defaults. Existing repository
context and ADRs refine the defaults when present. This Skill remains usable
without those files and must not require a companion SOP to proceed.
