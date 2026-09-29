# Writing Rules — the seven techniques that raise instrumental quality

Each rule is grounded in the official Music 3.0 technical blog or model card. Apply all seven.

---

## 1. Structure beats adjectives

The model reads a prompt as an **arrangement brief**, not a vibe description. A single global label
("epic, emotional, cinematic") is the weakest possible input because it cannot express *when* things
change. Use the three-block Structured Caption:

- `Global Metadata` — genre/subgenre, tempo, emotional progression, use case, production profile
- `Vocal Details` — for instrumental: state instrumental + name the lead melodic carrier
- `Arrangement` — the section-by-section timeline

`Arrangement` is where the quality lives in instrumental mode. It is the block most agents
under-write, and the one the model weights most heavily.

---

## 2. Instrument = role + performance technique

The official blog calls out glissando (pitch slides) and legato as specific things Music 3.0
reproduces with physical realism, alongside string attack/bowing, drum and bass impact, and
source separation in dense electronic arrangements. A bare instrument name spends none of that.

| Weak | Strong |
|---|---|
| strings | low strings gradually building tension |
| piano | sparse reverberant piano chords anchoring the harmony |
| acoustic guitar | softly fingerpicked acoustic guitar |
| drums | tight punchy kit with restrained fills |
| violin | expressive legato violin line, no vibrato until the climax |
| erhu | solo erhu with audible pitch slides and breathy bowing |

Ask of every instrument: **what does it do, and how is it played?**

---

## 3. Name the lead melodic carrier explicitly

The `Vocal Details` block is not dead weight in instrumental mode. Repurpose it to answer: *who
carries the melody?* A single named carrier with a described articulation is worth more than three
unassigned instruments.

> Instrumental — no vocals, no choir, no spoken word, no vocal samples. The lead melodic role is
> carried by a solo erhu with audible pitch slides, later doubled by a legato violin line; low cello
> and viola sustain the harmonic bed.

---

## 4. Write an energy arc, not a gear list

A gear list makes the model spread every instrument across the whole track. An energy arc gives each
one a lifecycle. Write who enters when, who recedes, and where the peak is.

A workable entry pattern:

```
solo erhu (Intro)
  + low cello sustain (Verse)
  + frame drum pulse (Pre-Chorus)
  + full string section, taiko, brass (Final Chorus)
  + everything strips back to a single decaying harmonic (Outro)
```

---

## 5. Embed exclusions as positive statements

There is no negative-prompt field. State exclusions inline, and make them specific enough not to
collateral-damage the track.

- ✅ `no vocals, no choir, no spoken word, no vocal samples`
- ✅ `no busy hi-hats, no abrupt tempo changes, no filter sweeps`
- ❌ `good`, `nice`, `high quality`, `professional` — zero control value

Always restate instrumental intent even when `is_instrumental: true` is set. The description and the
flag are independent controls, and one is a known weak point.

---

## 6. Describe the sound, not the plugin chain

The model understands listening impressions, not DAW configurations.

- ✅ `wide dark soundstage, deep sub-bass weight, shimmering high string textures, dynamic range
  from near-silence to dense wall-of-sound, long hall reverb tail`
- ❌ `Pro-C 2, Ozone, SPAN, Valhalla VintageVerb`

Reserve technical gear talk for cases where the user has a specific toolchain requirement in mind.

---

## 7. Be honestly vague rather than falsely precise

The official model card states plainly that descriptions are *generative control rather than strict
symbolic guarantees* — tempo, key, instrumentation, and structure may not match every requested
detail. Therefore:

- Use an exact BPM or key only when the user supplied it or it is strongly implied.
- Otherwise give a range or a qualitative tempo: `slow, 80–90 BPM`, `driving, mid-100s`.
- Describe the emotional trajectory even when you cannot pin the numbers. A trajectory survives a
  missed key; a confidently wrong key derails the whole render.

This is the same discipline the official skill enforces: *"Do not invent a precise key, BPM, vocal
gender, melodic interval, or production technique when a broader description is sufficient."*

---

## Length discipline

The hosted API caps instrumental prompts at **2,000 characters ≈ 300 English words**. The open-weights
model accepts up to 5,000 tokens, which is where the official "250–450 words" guidance comes from.

Budget in this order, and cut from the bottom when over:

1. `Arrangement` timeline — never cut this
2. `Global Metadata` core (genre, tempo, arc, use case)
3. Production profile
4. Decorative adjectives — cut first
5. `Vocal Details` — compress to the lead carrier plus exclusions
