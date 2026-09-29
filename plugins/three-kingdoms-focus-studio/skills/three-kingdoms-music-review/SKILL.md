---
name: three-kingdoms-music-review
description: Review Three Kingdoms focus-music prompts, generated audio candidates, and chapter transitions against the approved project brief. Produce evidence-based arrangement, harmony, listening-purpose and technical QA recommendations while preserving human selection.
---

# Three Kingdoms Music Review

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
