---
name: three-kingdoms-music-review
description: Review Three Kingdoms focus-music prompts, generated audio candidates, and chapter transitions against the approved project brief. Produce evidence-based arrangement, harmony, listening-purpose and technical QA recommendations while preserving human selection.
---

# Three Kingdoms Music Review

Read [Codex runtime guidance](../../CODEX.md) before using this skill. Resolve bundled skills and resources relative to this installed package.


Act as a music editor combining arrangement, harmony, critical listening and audio-engineering perspectives. This is an advisory reviewer, not a credentialed human musician or a guarantee of musical accuracy. The user chose advisory mode: provide a clear recommendation and plain-language reasons; the user retains final approval.

## Establish the review contract

Read the target project's spec, music master, track manifest, continuity map, exact prompt and candidate review. Resolve the current chapter, role, selected variation, chapter anchor and immediate predecessor. Preserve approved creative choices and historical candidate decisions. A project-specific approved instrumentation exception overrides a generic channel default; identify and explain any unresolved conflict.

Separate **tonality** (tonal center, mode, harmonic movement) from **tone** (mood and chapter identity). Do not assign a key based on the character's personality or demand one key throughout a long mix. Compatible voice leading, phrase, texture and intended transition matter as well as tonal distance.

Record mode and evidence coverage before conclusions:

- `prompt`: text, specification and arrangement feasibility only.
- `technical`: measured source files; use scripts/measure_audio.py.
- `listening`: actual audio-native model or human listener evidence, with model/listener, exact source hash and timestamp coverage.
- `continuity`: both actual adjacent sources are required; clearly mark when only a planned transition was assessed.

Use evidence labels `measured`, `audio-model-observation`, `human-observation`, `prompt-intent`, `inference`, `not-assessed`. An MP3 path, player embed, waveform, spectrogram or ffmpeg report does not itself give the language model auditory perception. Missing listening evidence remains `not-assessed`, never a pass. Numeric DSP estimates of BPM, key or instrument identity are estimates, not listening facts.

## Which question goes to which tool

Route by question type, because the two tool families fail in opposite directions.

| Question | Use | Why |
|---|---|---|
| Noise floor, band energy, dynamics, peaks, clipping, duration | `scripts/measure_audio.py` | Reproducible arithmetic on the samples. Deterministic and re-checkable. |
| Where exactly did a level jump happen? | `scripts/locate_level_jumps.py` | Same 100 ms ebur128 windows as `measure_audio.py`, with timestamps — turns a counter into a re-listenable moment, and shows whether a large share is many small jumps or one single event. |
| Does the spectrum support a claimed voice at the model's own timestamp? | `scripts/detect_vocal_bands.py` | Band-energy trend across 200–400 Hz, 1–2.5 kHz, 2.5–4 kHz and 8–12 kHz against the neighbouring windows. |
| Is there a voice? Which instruments? Does the emotional arc land? | An audio-capable model, labelled `audio-model-observation` | Genuine semantic judgement, but a judgement and not a measurement. |

A model asked whether it hears rain or crackle is answering a fine-grained perceptual question it is not built for. Two recorded failures on one 174 s lo-fi track:

- Asked the same question about two caption variants, it answered **backwards** — reporting ambience on the version whose prompt requested it least, and none on the version that named it as forbidden.
- On the accepted candidate it reported "vinyl crackle / tape hiss audible consistently throughout". The measured 10-16 kHz floor in that track's quietest passage was **-91 dB**, against -37 to -43 dB where the drum kit enters. A 50 dB separation, not a noise bed.

All figures from `measure_audio.py` are **genre-relative**. The separations quoted above come from
sparse lo-fi sleep material. A nylon-string bossa nova, a brass-forward jazz chart or a close-mic
folk recording will show a legitimately higher high-band floor and a wider short-term range. Compare
a track against its own sections and against other tracks of the same genre and instrumentation; never
apply one genre's absolute as another genre's pass/fail line. `windows_above_median_3lu` is a defect
signal for calm material and a normal reading for material that is supposed to move.

### The dynamic metric that actually detects an instant (LRA does not)

**LRA measures the overall loudness range of a track, not whether it contains a sudden jump.** It is
the wrong proxy and it misclassifies in both directions. Measured on four tracks (2026-10-22):

| Track | LRA | Verdict LRA gives | `w>3LU` windows | `w>6LU` windows | What was actually true |
|---|---|---|---|---|---|
| `c01-t04` | 11.9 | over threshold | 1 | 0 | no instant at all — wrongly rejected |
| `c06-t01` | 15.8 | over threshold | 1 | 0 | no instant at all — wrongly rejected |
| `c02-t02` | 8.2 | within threshold | 296 | **5** | a real dynamic jump — wrongly passed |
| `c06-t03` | 9.0 | within threshold | 543 | **116** | a real dynamic jump — wrongly passed |

Use the **short-term dynamics** counters instead:

- **`windows_above_median_6lu == 0` is the hard gate.** Any window sitting more than 6 LU above the
  track's own median is an instant jump — a dropped edit, a slammed limiter, a splice.
- `windows_above_median_3lu` is the "calm material defect" signal, but it is **not** an absolute
  pass/fail line. Every number is genre-relative.
- Two layers: `w>6LU == 0` is the hard gate; the share of `w>3LU` windows is a strict layer at ≤3%
  and a concern layer at ≤6%. Use the relaxed layer only when the strict layer cannot fill the
  required minute range, and **record that it was relaxed**.

A large `w>3LU` share is also not automatically scattered jumps. In one measured track, a 17.13%
share turned out to be a **single one-second event** (00:23.30–00:24.30), not many small ones.
Locate the timestamps before describing the distribution — `locate_level_jumps.py` reuses the same
ebur128 100 ms windows as `measure_audio.py` and reports where the jumps actually are.

So: **never let a model's foley or ambience claim trigger regeneration on its own.** Measure first. If the measurement is clean and the model objects, the model's observation is recorded and set aside. If the measurement is dirty, still confirm by listening, because a band level shows how much of a sound there is, never what the sound is.

Conversely, do not let a clean measurement overrule a listener. If the user hears something objectionable that the numbers do not show, the finding stands and the number is reported as insufficient, not as a rebuttal.

## Consistency is not correctness

**A model's agreement with itself is not a reliability signal.** Judge the model against the human
and the measurement, never against the model's own repeated answers.

Measured 2026-10-22 on one 142.7 s candidate, across **four independent calls** (one prompt run
twice plus two other phrasings): the model reported `VOICE PRESENT` **every time**, and one response
added "synthesized vocaloid-style 'oooh' sounds and pitch-shifted vocal chops starting around the
25-second mark", naming specific timestamps. The human listening verdict was **no voice**, and the
spectral corroboration at the model's own reported timestamps (25 s and 33 s) showed 2.5–4 kHz
undulation of 14.3 and 14.7 dB — both **below** the 30.8/33.1 and 21.7/17.6 dB of the surrounding
windows. Two independent methods agreed and the model was wrong, **consistently** wrong. The likely
cause: the lead instrument is a breathy ocarina-like timbre whose formant structure resembles a
voice, and the model classified the instrument as a voice.

Consistency also fails the other way. Running one identical prompt over 18 candidates twice flipped
the answer on 4 of them — `VOICE`→`NO_VOICE` on one, `NO_VOICE`→`VOICE` on another, and a third
changed from a specific timestamped claim to a clean negative.

### Verification order for any "is there a voice?" claim

1. **Ask the same segment three ways.** If the answers disagree, the model is unreliable on this
   question and its answer carries no weight. A model that reverses with the phrasing of the
   question is hallucinating, not describing.
2. **Corroborate at the model's own timestamps.** Do not pick your own convenient spot — a
   self-chosen point may support the claim while the model's own point does not, and then the
   self-chosen point was a false signal. Human voice has formant structure: take a 0.25 s window and
   scan 200–400 Hz, 1–2.5 kHz, **2.5–4 kHz** and 8–12 kHz against the neighbouring windows. If the
   disputed window's 2.5–4 kHz trend matches its neighbours, there is no sustained voice feature.
3. **Human listening is the only binding gate.** Every measurement passing is not a pass. A
   measurement can be clean and the model can still be right about something the numbers do not
   model (a lyric in a language you do not read, a very quiet voice under the noise floor).

The same rule applies to a model's foley or ambience claim: it never triggers regeneration on its
own. Measured 2026-10-22, a candidate was said to carry "vinyl crackle", while the quietest passage
measured a 10–16 kHz floor of −91.0 dB — effectively digital silence. The claim was refuted by
measurement, not by argument.

## The listening gate belongs to the user

`agent-recommended` is not `user-approved`, and this is not a formality. A track the user has heard in their own room on their own equipment at their own volume is a stronger observation than any desk measurement, and it is the only observation that accounts for the listening context.

A track is not verified until the user says so. "Much better" is progress, not approval. When a technical check passes but the listening gate is open, report `pending_user_confirmation` and keep working; never close the gate by inferring intent from an earlier comment.

Record the candidate number the user generated, not just the filename. `t03-v05.mp3` means five attempts existed; knowing which one was selected, and why, is the part that is lost when only the final file is kept.


## Review

Read [references/rubric.md](references/rubric.md) for the selected modes. Compare against the approved chapter function and exact musical intent, not generic prestige genres. Report the highest-impact findings first and give the smallest repair that preserves identity. Distinguish deliberate style from unwanted distraction and technical defects from artistic preference.

For prompts, inspect the actual paste-ready payload: independent track scope, selected chapter/variation, playable instrument roles, density, rhythmic and harmonic direction, temporal development, carryover, outgoing phrase, contradictions, achievable timing and provider field limits. Provider behavior is probabilistic; timestamps and named instruments are requested intent. Count actual payload including whitespace. Propose changes separately; editing an approved prompt requires a new version and its established approval gate.

For audio, first validate source provenance and full decode. Use the measurement helper if no current trustworthy same-hash measurements exist. Read output before making a technical claim. Preserve the originals. Technical failure can coexist with human artistic selection; record the repair obligation without revoking the user's choice.

For audible review, use an available audio-input-capable route with authorized file/destination scope. See [references/audio-listening.md](references/audio-listening.md). If unavailable, complete text/technical work and provide an exact handoff; say that perceptual review is incomplete. Full-track claims require documented full-track coverage. Label excerpts and do not extrapolate vocal absence from a few excerpts. Models can misidentify timbres, meter and chords; lower confidence or obtain a second targeted observation where a disputed finding would trigger regeneration.

For continuity, compare predecessor ending, candidate entry, phrase/pulse, harmonic behavior, low-end, timbral density, spatial decay and local loudness. Compare the candidate with the chapter anchor too. Integrated loudness difference alone does not establish a boundary jump. A crossfade cannot automatically solve incompatible rhythm/harmony. Do not render or alter audio without authorization.

## Recommendation and artifacts

Write a versioned Traditional Chinese human report under the project's `music-review/`. Keep AI handoffs and machine JSON separately in English. Include:

1. Plain-language recommendation: proceed to human review / revise prompt / repair audio / regenerate / insufficient listening evidence.
2. Scope: source paths/hashes, prompt version, project/track/chapter, anchors, tools/models and coverage.
3. Table: requirement, status (`pass`, `concern`, `fail`, `not-assessed`), evidence type, quote or timestamp, confidence, practical impact and proposed action.
4. Separate prompt, technical, listening and continuity verdicts; no misleading combined numeric score that hides missing evidence or a hard constraint failure.
5. A minimal suggested change or generation revision, and the decisions actually left to the user. Do not ask the novice to identify keys or diagnose audio engineering problems.

Candidate comparison: rank only on assessed evidence, equalize listening presentation when authorized, disclose unavailable dimensions and preserve every candidate. An `agent-recommended` assessment is not `user-approved`. Human candidate/prompt/assembly approval and external generation authorization remain separate records. Reuse explicit authorization already granted for the same scope; do not manufacture repeated confirmation requirements.

Review completes when every relevant rubric dimension has a supported result or an explicit `not-assessed` reason, and the next action is concrete. Do not change selected candidates, approve prompts, generate replacement music, upload audio or publish solely because the reviewer recommends it.
