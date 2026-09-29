# Compressing a Full Template to Hosted-API Length

The bundled `templates/` are written at **open-weights length** (250–450 words, matching MiniMax's
official caption style). The hosted API caps instrumental `prompt` at **2,000 characters ≈ 300 words**.

Every bundled template is therefore over the hosted cap. That is intentional — they are the quality
ceiling, and a reference model to compress from, not drop-in request bodies.

Do not silently truncate. Truncation destroys the `Arrangement` timeline, which is the block carrying
most of the control value. Compress deliberately.

---

## Compression order

Cut from the bottom of this list first. Stop as soon as you fit.

| Keep | Compress | Cut entirely |
|---|---|---|
| `Arrangement` timeline — the instrument lifecycle and groove progression | `Sonics & Production Profile` to two or three clauses | Decorative adjectives ("beautiful", "stunning", "epic") |
| `Global Emotional Progression` | `Application Scenarios & Imagery` to a single clause | Redundant exclusions already implied by `is_instrumental: true` |
| The lead melodic carrier sentence in `Vocal Details` | `Harmonic Bed` and `Spatial` merged into one line | Any field whose content is not an audible event |

Keep the negative constraints. `no vocals, no choir, no spoken word` is load-bearing, not decoration.

---

## Worked example — `cinematic-epic_0001.txt`

**Source: 2,802 characters.** Over the 2,000 cap.

### What gets cut

| Removed | Reason |
|---|---|
| "The climax must feel earned, never announced." | Decorative, not an audible instruction |
| "at roughly half the final tempo and sits behind the beat rather than on it, which keeps the opening feeling weighted rather than marching" → "at half the final tempo, sitting behind the beat" | Same instruction, half the words |
| "A beat of near-silence precedes the final rise." | Merged into the outro clause |
| "Ambient wind texture fills the quiet sections and sells the sense of scale." | Droppable ambience |
| `Spatial` field in `Vocal Details` | Merged into the production profile |
| "ever twice in the same form" from the risers clause | Detail the model infers |

### Result: 1,148 characters

```
Global Metadata: Cinematic Orchestral / Epic Score. 84 BPM, D minor. The arc moves from cold
isolation, through slow accumulating tension, into an explosive heroic release, then a hollow
restraint. Game boss-reveal trailer or war-drama montage. Wide dark soundstage, deep sub-bass
weight, shimmering high string textures, long hall reverb tail, dynamic range from near-silence
to wall-of-sound.

Vocal Details: Instrumental — no vocals, no choir, no spoken word, no vocal samples. The lead
melodic role is carried by a solo erhu with audible pitch slides, later doubled by a legato violin
line. Low cello and viola sustain a pedal drone; sparse reverberant piano chords fill the gaps.

Arrangement: Opens on the solo erhu motif with no percussion. A low cello drone enters beneath it,
then sparse frame-drum pulses at half the final tempo, sitting behind the beat, establish a slow
marching pulse. Violas add a rising countermelody. Low brass swells and a timpani roll mark the
pre-chorus. The climax lands with the full string section, taiko-driven low end, a brass fanfare,
and a distorted electric guitar layer cutting through. A beat of near-silence precedes the final
rise. The outro strips to a single sustained string harmonic decaying into silence. Cinematic
risers and reverse cymbal swells mark each transition; sub-bass drops accent only the heaviest
hits.
```

### What survived, and why it still works

- Every instrument still has a stated entry and exit
- The groove still has a placement instruction (behind the beat)
- The climax still has its full instrument stack
- The ending still has a described resolution
- The lead melodic carrier is intact
- The vocal exclusions are intact

That is the test: **compress until it is tight, then stop while the timeline still reads as a
timeline.** If the `Arrangement` block degrades into a gear list, you cut too far — restore detail
there and take it from `Global Metadata` instead.

---

## Quick check before sending

```
len(prompt) <= 2000
```

and confirm the `Arrangement` block still names what enters, what exits, and what intensifies.
