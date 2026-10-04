---
name: music3-instrumental-prompts
description: Write high-quality instrumental (no-vocal) prompts for MiniMax Music 3.0 (`music-3.0`). Turns a brief into a Structured Caption with Global Metadata, Vocal Details (rewritten for instrumental), and a section-aware Arrangement timeline. Use when generating background music, soundtracks, BGM beds, ad or brand stings, game music, or any vocal-free track for Music 3.0.
---

# Music 3.0 Instrumental Prompt Writer

Read [Codex runtime guidance](../../CODEX.md) before using this skill. Resolve bundled skills and resources relative to this installed package.


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
7. **Do not request a foley sound source as a separate layer.** Rain, thunder, water, wind as a
   weather sound, birds, insects, fire, fireplace, static, tape hiss and vinyl crackle compete with
   the music rather than support it, and generation gives you no decibel control over them. The model
   renders them as loudly as it likes, usually over the instruments. Keep these out of the caption
   and add them in post where the level is measurable.

   **The carve-out: ambience that is the subject.** Some genres *are* air. Epic scoring lives on wind
   and distance. Live jazz records carry room tone, crowd and the acoustic of the room. Chinese
   instrumental work lives on the breath of a suona and the air inside a dizi. Stripping those out
   produces a technically clean track that no longer sounds like its genre.

   When the ambience is the subject it stays in the caption, and it obeys level discipline:

   - **Never place it at `0:00`.** The opening is where the ear is most sensitive and where the model
     puts it loudest. Bring it in after the first third.
   - **Request character, not a sound effect.** "Air around the low strings" is controllable;
     "wind sound" is a named effect the model realises literally and prominently.
   - **Anchor it underneath something.** "Beneath the pad, below the low strings" gives the model a
     reference to stay under.
   - **Never combine it with "every audible element is a musical instrument."** That sentence
     contradicts the request, and a contradiction is resolved arbitrarily. Write the framing that
     matches what you actually want.
   - **Measure it afterwards.** A genre-appropriate ambience that renders 20 dB over the mix is still
     a defect, and post is the only place that gets fixed.

   The difference between the two cases is not the sound, it is whether the sound is the point. Vinyl
   crackle under a lo-fi beat is decoration, and decoration that cannot be levelled is a liability.
   Wind across a desert vista is the scene, and a scene belongs in the caption.

8. **Never name what you do not want.** An explicit `no rain / no hiss / no crackle` is unreliable
   and can seed the concept it forbids. Verified 2026-09-30: a caption stating "absolutely no rain,
   no thunder, no fire, no crackle, no hiss" still produced audible tape hiss, while a caption that
   simply never mentioned those words did not. Exclude by positive framing — describe only the
   musical content and state what the mix *is*, never what it is not. Reserve named exclusions for
   instrument-level choices where the model can act on them, not for ambience categories.

   Scope this rule to ambience categories. Naming a specific unwanted *instrument* is different and
   generally useful: "no saxophone" and "no vibraphone" are choices the model can act on, and several
   genres need them, because a bossa nova without a nylon string lead or a folk arrangement with no
   accordion fails for exactly that reason.

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
- [ ] **No foley sound source requested as a separate layer** (Rule 7)
- [ ] If genre-defining ambience is present: it is deferred past the first third, requested as character
      rather than as a named effect, anchored beneath an instrument, and never paired with
      "every audible element is a musical instrument"
- [ ] **No ambience category named even in a negative clause** (Rule 8)
- [ ] No unwanted **instrument** named as a negative, unless the genre requires the exclusion
- [ ] No self-contradiction: anything asked for in `Arrangement` must not also appear in an exclusion list
- [ ] Word count fits the runtime budget
- [ ] Callers were told `is_instrumental: true` and to leave `lyrics` empty

## Text edits that break the structure

A global whitespace collapse such as `re.sub(r"\s{2,}", " ", text)` silently destroys the
three-block contract, because the blank line before `**Vocal Details**` and `**Arrangement**` is
the only thing separating the blocks. The result reads as one run-on paragraph beginning
`...late-night listening. **Vocal Details**`, and the model loses the block boundaries it relies on.

Split on the headings and rejoin with blank lines instead of collapsing the whole string:

```python
parts = [p.strip() for p in re.split(r"(\*\*(?:Global Metadata|Vocal Details|Arrangement)\*\*)", text) if p.strip()]
text = "\n".join("" if i else part for i, part in enumerate(parts))
```

Verify after any bulk word edit: the three headings must each start their own line, the line before
each must be empty, and the production paragraph must sit below the timeline rather than trailing
the final timestamp.

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
