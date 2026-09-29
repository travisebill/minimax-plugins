---
name: music3-instrumental-prompts
description: Write high-quality instrumental (no-vocal) prompts for MiniMax Music 3.0 (`music-3.0`). Turns a brief into a Structured Caption with Global Metadata, Vocal Details (rewritten for instrumental), and a section-aware Arrangement timeline. Use when generating background music, soundtracks, BGM beds, ad or brand stings, game music, or any vocal-free track for Music 3.0.
---

# Music 3.0 Instrumental Prompt Writer

Produce a generation-ready **Structured Caption** for instrumental music on MiniMax Music 3.0.

This is the instrumental-only specialization of MiniMax's official `music-caption-rewriter`
skill. Where the two differ on instrumental handling, this file wins. For the general rewrite
workflow (routing, reference selection, template safety) defer to `music-caption-rewriter`.

---

## Non-negotiable rules

1. **Never add vocals.** If the user asks for instrumental, the output is instrumental — no lead
   vocal, no backing vocals, no choir, no humming, no vocal chops or samples.
2. **Never delete the `Vocal Details` block.** In instrumental music it becomes the block that
   names the **instrument or texture carrying the lead melodic role**. Deleting it surrenders your
   control over the melody and the model will pick a lead for you.
3. **Never put section structure in `lyrics`.** Section tags (`[Chorus]`, `[Verse]`, …) are a
   vocal-mode feature. In instrumental mode the entire section timeline lives in the
   `Arrangement` block of the prompt.
4. **Never name artists or copyrighted soundtracks.** Describe style; do not reference.
   ✅ "epic trailer orchestral with taiko and brass fanfare" — ❌ the soundtrack from ___
5. **Never fabricate precision.** State an exact BPM or key only when the user supplied it or it is
   strongly implied. Otherwise use a range or qualitative tempo ("slow, 80–90 BPM").
6. **Never pad with dead adjectives.** `good`, `nice`, `high quality`, `professional` carry zero
   control value and waste the character budget. Every word must change what the model renders.

---

## The core insight

Music 3.0 does not fail from too little description — it fails from description without a **timeline**.
The official model blog names the exact failure modes: requested instruments gradually disappear,
intended emotional character weakens as the track develops, and a requested character appears in
only one section instead of staying coherent.

> A good instrumental prompt is an **arrangement brief with a time axis**, not a list of adjectives.

---

## Workflow

1. **Build a private Music Brief** from the user request: macro genre/subgenre, mood arc, tempo
   range, lead instrument, core instruments, production texture, section plan, exclusions.
2. **Resolve constraints** with this precedence:
   1. explicit user requirements and exclusions
   2. strong implications from the user's description
   3. matched reference characteristics
   4. conservative musical defaults
   Never silently reverse an explicit instrumental requirement, tempo limit, required instrument, or
   prohibited element.
3. **Read `references/writing-rules.md`** for the seven techniques that raise instrumental quality.
4. **Read one template** from `templates/` that best matches genre and use case. Read a second only
   when the request is a genuine fusion.
5. **Design the section timeline** — for every section, state what enters, exits, changes, or
   intensifies. Keep instrument behaviour continuous.
6. **Render and validate** against the checklist below.

Do not expose the Music Brief, template IDs, or routing reasoning unless the user asks.

---

## Output contract

Return exactly these three top-level headings, in this order.

### Global Metadata
Genre and subgenre, tempo, emotional progression, intended listening scenario, and overall sonic +
production profile. Include key/scale only when explicit or musically useful.

### Vocal Details
Open by stating the piece is instrumental and name the exclusions (`no vocals, no choir, no spoken
word, no vocal samples`). Then name the **lead melodic carrier** — the specific instrument and how
it is played. Optionally describe the harmonic/instrumental bed underneath it.

### Arrangement
A readable section-by-section **timeline**. Cover primary and secondary instrument lifecycles,
groove development, transitions, embellishments, texture, and spatial effects — but only where they
actually happen. Concrete changes beat decorative prose.

Do not include a song title, track ID, template ID, reasoning trace, or any copied lyric line.

---

## Length budget — this differs by runtime

| Runtime | Prompt limit | Target output |
|---|---|---|
| Hosted API (`api.minimax.io`, `is_instrumental: true`) | **2,000 characters** | **280–320 words** |
| Open weights (HuggingFace `MiniMaxAI/MiniMax-Music3`) | 5,000 tokens | 250–450 words |

The official skill's "250–450 words" guidance is written for the open-weights model. **On the hosted
API it overflows the 2,000-character cap.** Write the `Arrangement` block first, then cut decorative
adjectives until you fit.

---

## Runtime access (verify before recommending)

As of **2026-08-20** the paid Music Generation / Lyrics Generation APIs are **no longer available to
new users**, and the free tier (`music-3.0-free`, `music-2.6-free`, `music-cover-free`) is
discontinued. Existing paying/Token Plan users retain access (`music-3.0`, 120 RPM).

Current paths:
- **MiniMax Audio** — the official web product, for general users.
- **HuggingFace `MiniMaxAI/MiniMax-Music3`** — open weights, 32 kHz 16-bit stereo WAV, via
  SGLang-Omni / diffusers / ComfyUI.

Do not send a new user to sign up for an API key. See `references/api-contract.md` for the full
parameter spec and request shapes.

---

## Validation checklist

Revise once if any check fails, then return only the corrected result.

- [ ] Exactly three headings, correct order, English output (unless another language was requested)
- [ ] Instrumental is stated explicitly, with concrete vocal exclusions
- [ ] A specific **lead melodic instrument** is named
- [ ] `Arrangement` reads as a timeline, not a static gear list
- [ ] Every instrument has entrance / exit / change accounted for
- [ ] No artist names, no copyrighted soundtrack references
- [ ] No fabricated exact BPM or key
- [ ] No dead adjectives
- [ ] Word count fits the runtime budget
- [ ] Callers were told `is_instrumental: true` and to leave `lyrics` empty

---

## References

- `references/api-contract.md` — full API parameter spec, limits, request/response shapes
- `references/writing-rules.md` — the seven techniques that actually raise quality
- `references/compressing-for-hosted-api.md` — **required** when targeting the hosted API: the bundled
  templates are open-weights length and exceed the 2,000-character cap
- `references/failure-modes.md` — symptom → fix table
- `templates/` — six complete instrumental Structured Captions across common use cases

### Template length warning

The bundled templates are **2,300–2,900 characters** each. They are the quality ceiling, written to
the official open-weights style — **not drop-in hosted-API request bodies**. Before sending to the
hosted API, compress as described in `references/compressing-for-hosted-api.md`. Never truncate
mid-block; that destroys the `Arrangement` timeline, which carries most of the control value.
