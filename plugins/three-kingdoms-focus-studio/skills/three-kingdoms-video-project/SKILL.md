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

- **`minimax-design` MCP** (preferred when the environment provides it): the
  agent executes generation itself. `generate_music:music-3.0` with
  `params.mode: "instrumental"`, no `lyrics` field, and a minute-level timeline
  inside the prompt as the only length lever. `generate_image` for covers and
  chapter images, `generate_video:MiniMax-H3` for the loop video. Read
  `skills/yt-focus-music-pipeline/references/design-mcp-execution.md` before
  executing — it carries the parameter contract, the ten measured failure
  modes and the output retrieval procedure.
- `MiniMax Music 3.0` hosted API / SGLang: retain the existing two-field
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

### Execution mode and its authorization

`execution-mode` records **who runs the generation**, and it is separate from
creative approval:

| `execution-mode` | Meaning | Authorization needed |
|---|---|---|
| `mcp` | the agent calls the provider through the MCP | the `prompt 已確認` gate already covers the approved provider, settings and candidate count; state the cost before any paid call |
| `api` | the agent calls a provider API directly | same as `mcp` |
| `manual` | the user runs the generation and hands the files back | the delivery contract; report nothing as produced until a real file exists |

**Creative approval is not execution authorization.** Approving a prompt says
the music is right; it does not by itself authorize spending credits. Before
any paid call, tell the user the amount. `confirm_cost` is never approved on
the user's behalf by the agent.

A reviewer's `agent-recommended` verdict never becomes `user-approved`, and an
agent that generated the file has not thereby selected it.

### What the agent must verify after an MCP generation

- the source file exists, decodes, and its hash is recorded;
- the instrumental condition holds (measurement plus listening — never a model's
  claim alone);
- the actual duration is measured and recorded as a **minute range**, not
  assumed from the prompt;
- a produced video carries no audio track, and a produced loop's seam is
  measured;
- the product is labelled as an external result, and any locally assembled
  chapter is labelled `assembly from supplied external results`.

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
├── chapter-images/                  # one image per declared chapter
│   ├── chapter-01-v1.png
│   ├── chapter-02-v1.png
│   └── ...
├── loop-video-prompt-v1.md          # 15-second loop video prompt
├── loop-video/                      # loop video delivery plus its verification record
│   ├── loop-video-v1.mp4            # verified delivery file (no audio track)
│   ├── loop-video-v1-seam.md        # wrap-transition measurement and any fix applied
│   └── ...
└── visual-measurements/             # machine-readable measurement output (JSON)

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
├── loop-video/                      # approved loop video delivery and its seam record
│   ├── loop-video-v1.mp4
│   └── loop-video-v1-seam.md
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
  structure. **This field is only real on routes where it is an actual input** —
  the hosted API, and the MCP only in `mode: "song"`. On the MCP instrumental
  route there is no `lyrics` field at all: omit it entirely rather than sending
  tag-only payloads. When the target interface supports tag-only input (hosted
  API), put one tag per line such as `[Intro]`, `[Instrumental]`, `[Solo]` and
  `[Outro]`. Never put scene prose, production notes or negative constraints in
  the lyrics field. Measured 2026-10-22 through the MCP: five `lyrics` values —
  `[Instrumental]`, `Instrumental`, structural tags, a descriptive sentence, and
  an **empty control** — all produced wordless vocals. The field is not a
  control surface and must never be described as one.
- `music description` / API `instructions`: use a Structured Caption with all
  three sections below. Keep it in English and make the field names visible so
  the structure survives handoff between the model card, SGLang API and
  Diffusers-style interfaces.
  - `Global Metadata`: genre and subgenre, BPM, time signature, key and scale
    (or an explicit unconstrained choice), listening scenario, production
    profile, and a time-ordered emotional progression.
  - `Vocal Details`: for this focus-video workflow state the instrumental
    condition **in positive terms** — name the texture that carries the melody
    (for example `a solo Chinese zither carries the lead line; a Rhodes
    electric piano answers beneath it`). Do **not** enumerate absences as the
    mechanism (`instrumental only; no lead vocals, backing vocals, spoken
    words, chants, lyrics or vocal effects`): worded exclusions are not a
    control surface. Naming a sound category can seed it — measured for foley
    and ambience categories (rain, thunder, vinyl crackle), so do not enumerate
    those. For **vocal** categories the enumeration was inert on the MCP
    (2026-10-22: 18/18 candidates clean with the exclusions present), so the
    line may stay as documentation; it is simply never the mechanism.
    Measured 2026-09-30, five of five captions that spelled out `no vocals, no
    choir, no spoken word` still produced wordless vocals. The real control is the
    route's flag — `is_instrumental: true` on the hosted API, `params.mode:
    "instrumental"` on the MCP — and on a route with no flag, treat
    instrumental output as unguaranteed and disclose it. For a project that
    intentionally includes voice, specify gender, timbre, delivery, harmony,
    backing vocals and effects here instead of hiding them in the arrangement
    prose.
  - `Arrangement`: primary and secondary instruments, the groove and bass or
    low-end behavior, percussion, textures and spatial effects, plus the
    section-level entry, layering, transformation and exit of instruments.

Write the arrangement as a temporal map, not only as adjectives. Tie each
section to a tag or time range, state what enters and recedes, and describe how
density, emotional energy and low end change while the core motif remains
recognizable. Every per-song request must select exactly one declared chapter
and exactly one variation; include the chapter's action, density and emotional
function without pasting all chapter directions into one request.

Use this compact Music 3.0 handoff shape in the prompt artifact. **The shape
depends on the route** — the `lyrics/input` block exists only where `lyrics` is
a real input, and the instrumental control is the route's flag.

```text
# Hosted API / SGLang shape (lyrics is a real input on these routes):
lyrics/input:
[Intro]
[Instrumental]
[Solo]
[Outro]

music description/instructions:
Global Metadata: [genre/subgenre], [BPM], [time signature], [key/scale], [listening scenario], [production profile], [emotional progression].
Vocal Details: [a positive statement of the lead instrumental texture that carries the melody].
Arrangement: [primary and secondary instruments]; [section-by-section entry and exit]; [groove, bass, percussion, textures, spatial effects]; [chapter direction and one variation].
```

```text
# MiniMax Design MCP instrumental route (there is no lyrics field at all):
params.mode: instrumental     # the only instrumental control
prompt:
Global Metadata: [genre/subgenre], [BPM], [time signature], [key/scale], [listening scenario], [production profile], [emotional progression].
Vocal Details: [a positive statement of the lead instrumental texture that carries the melody].
Arrangement: [primary and secondary instruments]; [section-by-section entry and exit]; [groove, bass, percussion, textures, spatial effects]; [chapter direction and one variation]; [a minute-level timeline, which is the only length control on this route].
```

The `Vocal Details` line must read as a positive statement. Never paste
`instrumental only; no lead vocals, ...` into a payload as the mechanism — see
the `Vocal Details` rule above.

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

**`max_new_tokens` belongs to the SGLang open-weight route only.** When handing
off Music 3.0 **SGLang** settings, `max_new_tokens` is a maximum number of audio
frames at 25 frames per second, not a guaranteed final duration. Use
`round(target_seconds × 25)` as the starting cap: 4,250–4,750 for a 2:50–3:10
cue and 7,500 for a five-minute ceiling. Generation may end earlier. Record the
requested cap and measure the returned file externally. The current documented
output is non-streaming 32 kHz, 16-bit stereo WAV; preserve the actual response
format in the handoff record rather than assuming the prompt controlled it.

**Do not carry `max_new_tokens` to the hosted API or to the MCP.** Neither
exposes it. On the hosted API the length lever is the caption plus the model
ceiling; on the **MiniMax Design MCP** there is **no length parameter at
all** — the only lever is a minute-level timeline written into the prompt.
Measured 2026-10-22 on the MCP with one identical caption: no timeline produced
**59.9 seconds**; the same caption carrying `0:00 … 3:50` produced **188
seconds**. Because exact length is not guaranteed, report a **minute range**
rather than a track count, and measure every returned file. Always invoke $music-caption-rewriter to draft the music description/instructions
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

**Level every song before the chapter is concatenated, not only the chapter.**

Chapter-level two-pass loudnorm gives the chapter one gain. It does **not** remove the
level steps *between* songs: measured on a 24-song release, every chapter sat at
−14.0 LUFS while adjacent tracks inside a chapter still differed by 0.1–9.3 dB.
The fix is to align each song once before concatenation with a two-pass loudnorm whose
LRA target is set **high** (e.g. 20): a target above the material's measured LRA makes
that pass apply gain only and leave the dynamics alone. Measured: the step count fell
by 21%, every chapter landed exactly on −14.0 LUFS, and the chapter's internal density
ranking survived.

Two facts follow, and they are different jobs:
- `two-pass loudnorm` with an LRA target **above** the material's measured LRA only adds
  gain; **below** it, it compresses dynamics.
- Per-song alignment therefore wants a **high** LRA target; the chapter-level pass is
  where any dynamic shaping belongs. Do not confuse the two.

**A seam that reads as a hole is usually the material's own tail, not the fade.**
Measured: the gaps between tracks averaged 3.05 s, but sampling the same metric *inside*
single tracks gave 0.32 s over 92 interior points. The holes came from the material
decaying to silence at its own end. Shortening the fade, deepening the crossfade or
trimming the tail silence each recovered only ~0.5 s. The real fix is in the prompt:
end every song unit on a sustained tone that **stops cleanly instead of fading to
silence**, so the fade has something to join to.

**Appending extra songs to lengthen a chapter.** When a release is short of its declared
length, add compatible songs rather than stretching the existing ones. Append them at the
**end of the chapter**, and do **not** renumber the existing slots or rename their
candidate files — the approved selection record points at those names. Keep the prompt
generator's existing track payloads byte-identical and diff the new prompt set against the
old one to prove it (measured: 18/18 identical, 3 added).

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

### Stage 3: 15-second loop video

Start only from the approved titled cover. Draft the exact video prompt and get
explicit approval before generating.

- `generate_video:MiniMax-H3`, `mode: first-last-frame`, `duration: 15`,
  `resolution: 2k`. Bind the **approved cover as both the first and the last
  frame** (`references: [{versionId: A}, {versionId: A}]`). `first-last-frame`
  does not accept a fixed `aspect_ratio`; the reference image sets the frame.
- Keep the camera still and the framing unchanged. Motion stays inside the
  scene — breathing light, drifting mist, faint particles, slow water, cloth.
- **Silence must be verified, not assumed.** `audio: false` does not guarantee
  a silent file: measured twice on 2026-10-22, a 6.58 s and a 15.08 s mp4 both
  came back with an AAC track (mean −24.2 dB and −46.5 dB). Probe the output,
  strip with `ffmpeg -an -c:v copy` (not `-vn`, which drops video instead), and
  confirm with `volumedetect`.
- **The seam must be measured.** Binding one image to both ends guarantees the
  opening frame, not the closing one. Measured 2026-10-22 on a 15.08 s / 24 fps
  clip: wrap transition 1.6949 mean absolute levels against a maximum
  *natural* in-clip transition of 0.9067 — the single largest transition in the
  clip, and the clip visibly decelerated to a near-stop before snapping back.
  The rule is **the wrap difference must not exceed the largest natural
  in-clip transition**; a re-encode control with identical content measured
  1.7000, which proves the seam came from the source and not from encoding.
  Fix locally with a 0.5 s cross-dissolve of the tail into the head (measured
  wrap 0.6601; pixels differing by more than 4/255 dropped from 5.68% to
  0.024%) and re-measure.
- Re-measure with `scripts/verify_loop_seam.py`, which has first been validated
  against a known seamless and a known seamed control (`--self-check GOOD BAD`).
  Record the measurement, the control, and the fix in
  `loop-video/loop-video-v1-seam.md`.
- Save the delivered file under `loop-video/` and wait for explicit approval
  such as `批准 loop-video-v1`.

## Full-length video production

Applies after the chapter audio assembly, the chapter image set and the titled
cover are approved. This is the upload master, not the loop video.

### Output spec

| Item | Value |
|---|---|
| Resolution / fps | 1920×1080 / 30 fps / yuv420p |
| Video codec | h264, `libx264 -preset medium -crf 22` |
| Audio codec | AAC 256 kbps / 44.1 kHz, sourced from the master WAV |
| Container | mp4 with `+faststart` |
| Frame count | `round(total_seconds × 30)`; the encoded file must match exactly |

**`crf 22`, not `crf 20`.** Measured on the same 60-second sample: `crf 20` = 7.24 Mbps
(3.12 GB for a 61-minute release), `crf 22` = 5.34 Mbps (2.30 GB). The picture
difference is mean 2.70/255, max 25, with only 1.97% of pixels differing by more
than 8 — imperceptible on ambient content. Pick the tier that keeps the delivery
file near the size of the previous release, then say which one you used.

### Layer order

```
background   per-chapter 15 s loop, scaled to 1920×1080, -stream_loop -1
  └ scrim    optional soft vignette under the waveform (local PNG, alpha)
      └ waveform   transparent 640×280 overlay, positioned per chapter
          └ text overlay   chapter name + title, one PNG per chapter
```

### ★ The ffmpeg length trap — always limit the output

**ffmpeg encodes until the *longest* mapped output stream ends, not the shortest.**
A full-length transparent waveform MOV is thousands of seconds long, so a chapter
segment silently renders as the whole film.

Measured failure: a 650 s chapter segment rendered 3702 s and 2 GB+ before it was
caught. Always pass `-t <segment_seconds>` **as an output option**, and verify the
resulting duration with `ffprobe` before moving on.

### ★ The waveform overlay must be written to a local APFS folder

`audio-reactive-waveform`'s renderer finalizes by moving its temp directory into
place, which fails on exFAT with `Cannot finalize on this filesystem. Use a local
APFS/NTFS/ext4 folder`. Render the overlay to a local APFS path (for example
`~/Movies/Waveform Output/`), then reference it from the composition. A 61-minute
overlay is about 13 GB.

### Per-chapter background loops

Generate one loop per chapter from that chapter's approved image with
`generate_video:MiniMax-H3`, `mode: first-last-frame`, the same image bound to
both the first and the last frame.

- `audio: false` still returns an AAC track (measured repeatedly). Strip it with
  `ffmpeg -an -c:v copy` and confirm with `volumedetect`.
- **`first-last-frame` binds the opening frame only.** The closing frame is the
  model's free choice, and it often is not the same picture. Measured on a
  chapter loop: the wrap transition differed by 14.88 while the largest natural
  in-clip transition was 1.10 — 36× the median, and the single largest transition
  in the clip. The model had drifted the light and the mist density and never
  returned.
- **Measure the seam and choose the fix by how far it overshoots:**
  - **within ~3× of the largest natural transition** → a short cross-dissolve is
    enough, because both ends are similar pictures;
  - **far beyond it** → the ends are different pictures, so a dissolve reads as an
    obvious blend. Use a **ping-pong** instead (forward plus reverse, dropping the
    duplicated end frames): every transition is then a natural single-frame step,
    which makes the loop seamless by construction. It doubles the length and
    reverses the motion, which is acceptable when the camera is fixed and only
    atmosphere drifts.
- **A seamless seam is not the same as correct content.** `first-last-frame`
  guarantees the *opening* frame only; the model is free to drift anywhere after
  that, and a ping-pong will faithfully replay a scene change in the middle of
  the clip. Measured on a chapter loop: the wrap difference was 14.88 while the
  model had abandoned the reference scene entirely and drifted through two
  unrelated landscapes before going black. The seam could be fixed; the content
  could not.
  → **Check scene stability separately.** Take the first frame as the reference
  and compute the structural correlation of every frame against it. Measured on
  the bad loop the minimum fell to **−0.126**; on the good ones it stayed above
  0.87. A loop whose minimum drops below zero has swapped scenes and must be
  regenerated, however clean its seam is.
- Verify with the same rule used elsewhere: a loop is seamless when the wrap
  difference does not exceed the largest natural transition inside the clip.

### Chapter name and title overlay

Render one RGBA PNG per chapter containing the chapter name and the title.

- **Measure the background, then pick the colour.** A bright cover needs dark ink;
  a night chapter needs ivory. Compute the contrast of both candidates against
  the actual pixels of that chapter's region and take the higher one. On the
  S02-P01 chapter images the ivory used by the previous release scored 1.16:1
  against the dawn sky — invisible — while deep ink scored 16.81:1.
- **Extract the calligraphic title from the approved titled cover instead of
  rendering it.** macOS has no matching calligraphic or regular-script Chinese
  face for a brush-style title, but the approved cover already carries the exact
  strokes. Threshold the luminance inside the title's crop into an alpha mask and
  reuse it in every chapter, recoloured per scene. This costs nothing and cannot
  drift.
- **Clean the extracted alpha before using it.** A plain luminance threshold over
  the title's crop also captures the cover's terrain: measured, the terrain
  averaged alpha 123 while the brush strokes averaged 250. Binarise the alpha,
  label the connected components, and keep only the components whose mean alpha
  is high — the strokes are nearly solid, the terrain is not. Left in, the terrain
  shows up in the final frame as a visible rectangular patch.
- **Component-level filtering cannot separate photographic background that touches the
  title.** The rule above holds while the terrain is a separate blob. It **fails when a
  stroke lands on bright background**: the two then share one connected component, the
  mean is dominated by the strokes, and the background passes. Measured on the S02-P04
  cover: the 「夜」's long left sweep sits directly on a lit temple eave, the eave came
  through as a stepped rectangle under the glyph, and it showed up on every chapter
  frame of the finished film.
  **Fix: classify per pixel, not per component.** Strokes are **bright and warm**
  (ivory → gold: R > 150, R ≥ G ≥ 0.85B); the eave is **cool blue-grey photographic
  texture**. Take the large components of that warm-bright mask, dilate them into a
  *stroke neighbourhood*, and keep the alpha only inside that neighbourhood. Measured:
  921 intruder pixels removed, all four glyphs intact with their soft edges, extraction
  coverage still 1.0000 and the damage self-test still failing at 0.8791.
  **The separator here is colour temperature and saturation, not brightness.**
- **Give the text a contrasting outline.** One fill colour only works if the
  whole glyph sits on a background of similar brightness. Measured on the S02-P01
  chapter images, the deep-ink brush title fell to 1.15:1 in one chapter (the
  strokes crossed a near-black market canopy) and 1.04:1 in another (a
  watchtower). A 3 px outline in the opposite luminance — ivory under a dark
  fill, dark under a light fill — raised the same worst cases to 15–17:1 while
  leaving the chapters that already read cleanly unchanged. Apply the same
  treatment to the chapter name.
- **Pick the fill colour from the background luminance *under the strokes*, not
  from the whole region.** The strokes can land on a different part of the scene
  than the region's average; in one chapter the region averaged mid-grey while
  the strokes sat on near-black.
- **Search the layout across all chapters.** Score candidate positions for the
  title and the waveform by how much fine detail and how much luminance spread
  they contain across every chapter image, and forbid the three elements from
  overlapping. Score alone is not enough: it does not know that a watchtower or
  the moon is the subject. Render the top candidates and look at them.
  Measured on S02-P04: the waveform's best-scoring position sat directly on the
  chapter-1 cat and had to be moved to the lower left. The score cannot see a cat.
- **The extraction region and the placement position are two different things.** When
  the title has to clear an object in the frame — S02-P04: the cat in chapter 6 — the
  overlay builder needs a placement scale and an offset on top of the extraction box.
  Measured: scale 1.00 overlapped the cat's face, 0.78 touched its ear, 0.70 came
  within a few pixels, and **0.63 cleared it** while each glyph still read at ~89 px,
  larger than the 60 px chapter name, so the visual hierarchy held. Keep the scale and
  the placement in the overlay record, and point the verification scripts at the
  *placed* box rather than the *extracted* one.
- **Residual-ink checks must use the soft edge, not the binarised core.** After a
  downscale, LANCZOS spreads the anti-aliased fringe wider than the binary mask. The
  tolerance is `alpha > 2` dilated by the outline width, not `alpha > threshold`;
  measured, the binary version reported 414 px of phantom residue on a clean overlay.
- **Measure the rendered ink extent, not the nominal box.** A chapter name
  drawn at x=104 with a 60 px face can still have ink out to x=590, and an
  extracted brush mask carries its own left bearing. Lay the title out from the
  **measured** right edge of the name and require a real gap (measured: a title
  placed 44 px from the name read as colliding; moving it to 190 px apart read
  as two separate elements).
- Put the loop's dynamic elements in the calm band of the frame — the sky, not
  over foreground detail. The waveform is a good candidate for the lower band:
  the sky of these scenes is the calm area, and the lower third is usually the
  most detailed part of the frame.

### Verification

Port the checks from the previous release's verification scripts and re-point them
at the new paths. They must cover:

1. structure, duration and codec;
2. a **full decode with no errors**;
3. **frame count exactly matching the 30 fps timeline**;
4. the audio track against the master WAV by raw sample correlation, with the
   offset found by FFT cross-correlation and the RMS envelope as the primary
   criterion (see *Comparing the final audio to the master*);
5. **end-to-end A/V sync** between the visible waveform and the audio. The
   waveform overlay is a *spectrogram*, not a time-domain envelope: extract the
   48 bar heights and compare them against the 48 band energies of the audio,
   scanning for the best alignment. A time-domain envelope comparison measures
   the wrong thing. Three traps, all of which produce **false failures**:
   - **Reproduce the renderer's own ceiling.** `render_waveform.py` normalises
     against the **98.5th percentile of the whole track**, not of a local
     block. Approximating it with a per-block ceiling re-anchors the dB scale,
     the `clip(0, 1)` then truncates the shape, and the correlation drops
     without anything being wrong. Recompute the reference with the renderer's
     algorithm and a **global** ceiling, and prove the reimplementation is
     faithful with a self-test (measured: max relative error 8.8e-16 against
     the renderer's own loop).
   - **Do not measure bar heights on the composite.** The overlay sits on top of
     the loop and a scrim, and warm background content — lanterns, autumn
     foliage, low sun — is the same colour as the bars. Measured on the
     S02-P01 cut, extracting bar heights from the final frame by saturation
     gave a correlation as low as **−0.36** against the audio reference, and
     the fix was not a better threshold: background removal, column-majority
     voting and row-wise background estimates all stayed under 0.93.
     → **Compare only the bar cores.** The overlay file's alpha channel *is* the
     exact bar geometry; the pixels where alpha > 0.9 are the bar colour
     itself in the final frame, so the background cannot influence them.
     Extract those pixels, compare their **luma** (yuv420p subsamples chroma,
     so luma is the only channel that survives), and scan for the best frame
     offset. Measured on the same cut: 0.975–0.992 at the best offset at every
     test point.
   - **The check needs the overlay file itself, with its alpha channel.** The
     encoded film alone is not enough — the bar geometry comes from the
     overlay's alpha, not from the picture. A 61-minute overlay is about
     13 GB. Keep it (and the audio-derived reference track) until the release
     is signed off; if it has to be reclaimed, regenerate it with
     `audio-reactive-waveform`'s renderer from the master WAV and the saved
     style JSON — no credits, but the regeneration has to happen before the
     A/V check can be re-run.
   - **Give the check a negative control.** Re-run the comparison against a
     deliberately shifted reference (measured: ±20 frames, 667 ms) and require
     the score to drop clearly below the real one. Without it, a check that
     passes for any offset is not a check. The reference's own shape
     self-correlation at 667 ms averages 0.47, so a correct score near 0.98
     separates cleanly from a shifted one.
5. the **chapter name shown at each chapter boundary is the right one**. Do not
   settle for "the pixels in the name region changed by more than 3" — the
   background is moving, so that region changes on its own and the check passes
   whether or not the name switched. Do not settle for a "darkness inside the
   mask minus darkness outside the mask" score either: with four of six names
   in the same ink colour it only separates the light group from the dark one,
   and measured on the S02-P01 cut it picked the wrong chapter in three of six.
   → **Treat the overlay PNG as ground truth.** It *is* what was composited, so
   for each candidate chapter compute what the region would look like —
   take the overlay's alpha and colour, estimate the clean background with a
   large-kernel median filter, and build the predicted luminance deviation —
   then take the cosine between the prediction and the deviation actually
   measured in the frame. The prediction carries the polarity, so dark-ink and
   ivory names can be compared in one scale. Measured: every chapter matched
   its own overlay with a margin of 0.26–0.52 over the runner-up. Then check
   that the winner flips from chapter *i* to chapter *i+1* across each
   boundary.
6. the chapter boundaries come from the assembly record, not from the plan: each
   chapter starts at the previous chapter's length minus the inter-chapter
   crossfade overlap. The final boundary is the last chapter's start plus its
   length — never the last chapter's length alone.

Build one segment per chapter, then produce the final cut. **Do not stitch the
chapter segments with the concat demuxer and `-c copy`.**

The concat demuxer shifts each file's timestamps by the **container duration** of
the previous file. In a chapter segment the audio runs a few milliseconds longer
than the video, so that shift is slightly too large and the error accumulates
across chapters. Measured on a 61-minute cut: the final audio drifted up to
**240 ms** from the master and ended 0.24 s long, with timestamp gaps at the
chapter joins. The content was still correct — the RMS envelope matched the
master at 0.88–0.999 — but the sample-level correlation collapsed, so a
sample-exact audio check fails for a reason that has nothing to do with the
audio.

Two ways out:

- **Single-pass concat (preferred).** One ffmpeg call: each chapter's loop
  input is `-stream_loop -1` and is cut with `trim` to the exact chapter
  boundary, each chapter gets its own scrim, waveform slice and text overlay,
  the six video streams are joined with the **concat filter**, and the master
  WAV is mapped straight in as the audio. The timeline is rebuilt rather than
  copied, so nothing can drift, and the audio never passes through an
  intermediate encode.
- **Mux the master audio last.** Concat the video only, then mux the master WAV.
  Cheap, but the video still carries the accumulated per-chapter rounding.

### ★ Cut the chapters by frame number, not by seconds

A `trim` whose bounds are given in **seconds** yields a per-chapter frame count
that rounds independently, so the video track drifts against the audio track by
one frame here and there. Measured on a 61-minute cut: the video came out
**111075 frames = 3702.500 s** while the audio and the master were
**3702.600 s** — three frames short.

Nothing looks broken at that scale, and the audio check still passes, because
the *content* is right; but anything derived from the video timeline slides
relative to the audio as the film runs. Measured on the same cut, the visible
waveform overlay moved from **0 frames** ahead of the audio at the start to
**+3 frames (100 ms)** at the end, and the chapter name switched to the next
chapter's title about half a second early at one boundary.

Cut by frame instead:

```
frame_bounds = [round(boundary_seconds * 30) for boundary_seconds in bounds]
chapter_frames = [frame_bounds[i+1] - frame_bounds[i] for i in range(n)]
#   trim=start_frame=0:end_frame=<chapter_frames[i]>          (loop segment)
#   trim=start_frame=<frame_bounds[i]>:end_frame=<frame_bounds[i+1]>   (overlay)
```

The chapter totals then add up to exactly `round(total_seconds * 30)`, the
video and audio tracks have the same length, and the chapter boundaries land on
the same frame index on both sides. **Assert the encoded frame count and the
duration in the composition script itself** — a self-check that fails loudly is
cheaper than a drift that only shows up in a downstream measurement.

### Comparing the final audio to the master

Do **not** assume the MP4's AAC track is offset by one AAC frame (1024 samples
≈ 23.2 ms). Measured on the S02-P01 cut with ffmpeg's MP4 demuxer, the best
alignment was **0 samples at all five test points** — the demuxer applies the
container's edit list, so the encoder priming is already compensated.

What *is* true, and costly to learn the hard way: **an alignment search on an
equally spaced grid can miss the correct offset, and a music signal's
sample-level correlation is extremely sensitive to a few samples of shift.**
The grid `range(-2822, 2823, 32)` never contains 0 (`-2822 + 32k = 0` has no
integer solution), and on the same 3-second excerpt the correlation was
**0.99988 at lag 0, 0.95516 at lag −6 and 0.82 at lag −30**. A grid search
reported 0.82–0.96 for a track that was bit-identical to the master.

- Find the offset with an **FFT cross-correlation**, which yields the exact
  integer-sample peak instead of whatever the grid happens to contain.
- Use the **RMS envelope** (10 ms hop) as the primary criterion and the raw
  sample correlation as a secondary one. The envelope is insensitive to
  sub-millisecond shifts, so it judges *is this the same track* without
  failing on encoder bookkeeping.
- Report the best offset, the sample correlation and the envelope correlation
  together; a zero lag with high envelope correlation is the expected result
  for a correctly muxed master.

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
- **the upload master itself is verified by measurement, not by file presence** —
  codec, resolution, frame rate, pixel format, frame count against
  `round(duration × fps)`, and that the video and audio tracks are the same
  length. A release package whose self-check only confirms the file *exists*
  will happily ship a master that is three frames short of its own audio;
- **every number in the delivery documents is reproducible by a command** —
  frame count, byte size, duration, and the README/spec figures are compared
  against the measured values by the package's own check;
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
