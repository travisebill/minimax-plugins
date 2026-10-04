# Music-review rubric

## Prompt and chapter identity

- Approved use: reading, work, commute, sleep or another recorded lane. Focus does not inherently mean slow, percussion-free, harmonically static or Chinese-instruments-led.
- Chapter function: identify its contribution and contrast with its neighbors. A texture variation should change register/articulation/spacing; an observing chapter may allow concise responses; an ending may remove activity. Avoid turning every track into an independent dramatic song arc.
- Character/Three Kingdoms identity: use the project's declared modern-hybrid or historical-inspired design; audio need not literally depict weapons or battles. Do not claim music alone proves a historical identity.
- Instrument hierarchy: assign lead, comping, bass, pulse and color roles. Consider overlap/masking, register, attack, sustain and realistic density. Guqin/xiao presence and sparse participation require listening, not only a named prompt.
- Rhythm: requested pulse/meter/syncopation support the intended activity. Separate bossa-derived accents from full dance instrumentation. Avoid confusing half/double tempo estimates with actual change.
- Harmony/tonality: key or modal center if specified; harmonic rhythm, voicing, dissonance, resolution, voice leading and bass movement. 6/9 and maj7 are chord colors, not a key or a full harmonic plan. An unspecified key is not automatically a prompt defect; mark actual tonal compatibility pending.
- Arc: meaningful entry, development and exit with feasible phrase lengths. Approximate timestamps do not guarantee duration. Assess actual returned structure; do not reject a longer coherent cue solely for missing the requested minute mark unless duration is a hard constraint.
- Distraction: evaluate foreground salience, busy fills, bright transients, bass activity, rhythmic instability, dramatic builds and repetitive fatigue. Quiet but prominent sax can still attract attention. Technical loudness alone cannot establish focus suitability.
- Payload: coherent positive instructions, relevant exclusions, no contradictory lead hierarchy, full standalone context and correct field/character constraints. A long negative list may dilute intent but is not by itself a hard failure.

## Source and technical QA

Record hash, actual codec, sample rate, channels, duration, file size and full decode result. Lossy codecs have no equivalent fixed source PCM bit depth. Use integrated LUFS, measured true peak, LRA and silence intervals as measurements, not artistic verdicts. Report method, tool version, silence threshold/duration and decoded coverage.

- Decode failure: technical fail; source preserved, assess reacquisition before regeneration.
- True peak above 0 dBTP: reconstructed overshoot concern requiring output headroom/limiting and remeasurement; not proof of audible clipping or irreversible source damage.
- A peak below 0 is not universal release compliance. Use the project's delivery target; when absent, propose a target separately rather than inventing an approved standard.
- Silence detection reports low-level intervals under a configured threshold; it is not automatically an abrupt edit, dead air or compositional failure.
- LRA is contextual. Do not set one universal acceptable range or reject all dynamic expression.
- Loudness matching: compare full-track measurements for planning and local boundary measurements/listening for actual transitions. Keep technical edits versioned, lossless where appropriate and separate from source audio.

## Audible evidence and continuity

For each observation: file ID, timestamp range, duration coverage, evidence route and confidence. Describe what is heard before assigning exact instrument/chord labels. If unsure, say plucked-string color or breathy wind timbre rather than inventing certainty. Vocal detectors/transcription cannot establish all vocal or environmental absence.

Evaluate beginning, development and ending, then inspect relevant events across the full track. Compare the actual predecessor tail and candidate opening, with enough musical context for at least a phrase when available. Record excerpt origin offsets. Same-key cues may clash; different-key cues may transition naturally. Check bass notes, resolution/entry, pulse phase, room tails and layer changes. A meaningful unresolved conflict blocks a continuity pass, not necessarily candidate artistic selection.

## Severity and confidence

- `must-fix`: violates a recorded hard requirement, unplayable source, or unresolved delivery defect.
- `should-improve`: plausible chapter/continuity/distraction issue with evidence.
- `optional`: artistic preference or modest craft improvement.
- `unknown`: missing or ambiguous evidence; no numeric grade.

Confidence high/medium/low reflects the evidence, not how forcefully the reviewer writes. Give the user a recommended decision and a short explanation of the likely listening effect.
