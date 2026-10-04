# Failure Modes — symptom → fix

Diagnose against these before rewriting a prompt from scratch. Most mediocre instrumental output is
one of the rows below.

| Symptom | Root cause | Fix |
|---|---|---|
| **Generic, interchangeable output** | Adjective pile with no time axis | Switch to the three-block Structured Caption; write a real `Arrangement` timeline |
| **Every instrument plays all the way through** | Gear list instead of lifecycle | Assign each instrument an entry/exit point; write the energy arc |
| **Humming, chanting, or "oooh" appears** | Instrumental not enforced at the provider level | Set `is_instrumental: true` and omit `lyrics` entirely. Measured 2026-09-30: 5 of 5 captions that spelled out `no vocals, no choir, no spoken word` still produced wordless vocals. The caption text is not the control; the request flag is. Keep the text exclusions as documentation, never as the fix |
| **Flat, no build, no payoff** | Structure only exists in `lyrics`, which instrumental mode ignores | Move the entire section timeline into the `Arrangement` block of `prompt` |
| **Wrong or drifting key/tempo** | Fabricated precision | Drop the exact number, use a range or qualitative tempo, lean harder on the emotional arc |
| **Sounds like a specific film/artist** | Referencing rather than describing | Replace the reference with its constituent traits (instruments, groove, production character) |
| **Overstuffed / cluttered mix** | All instruments at equal prominence | Name one lead melodic carrier; demote the rest to bed, pad, or texture |
| **Weak or absent ending** | No resolution described | State the final cadence, decay length, and what survives into the last bar |
| **Rejects the request / feels generic-safe** | Named an artist or franchise | Never reference. Always describe style in musical terms |
| **Prompt rejected by the API** | Over 2,000 characters | Target 280–320 words; cut decorative adjectives first, never the `Arrangement` timeline |
| **Rain, thunder, fire, water or wind bleeds into the background** | An ambience category was named in the caption | Delete every foley and ambience word from all three blocks. Do not replace them with `no rain / no hiss` — naming the category, even negatively, can still seed it. Describe the musical content only, and add ambience in post where the level is measurable |
| **A requested texture becomes the loudest thing in the mix** | A decorative foley word was written with no level qualifier | `vinyl crackle` / `tape hiss` / `air texture` are rendered at whatever level the model chooses. A texture that is decoration, not the subject, does not belong in the caption. Achieve it through musical means: tape saturation, rounded low-pass, muted instruments, detuned oscillators |
| **The genre is gone after removing the ambience** | The rule was applied without asking whether the air is the subject | Epic scoring lives on wind and distance; live jazz carries room tone and crowd; Chinese instrumental work lives on breath and air. Keep those in the caption and control them with discipline: defer past the first third, request character rather than a named effect, anchor beneath an instrument, and measure afterwards |
| **Genre-defining ambience renders far above the mix** | A level discipline item was skipped | Ask for character, not the effect name. Then measure the band floor in the quietest passage and tame it in post, where dB is actually controllable. Genre-appropriate does not mean level-appropriate |
| **The output contradicts itself** | An exclusion list names a category the `Arrangement` also requests | Remove the contradiction before anything else. A caption that both asks for and forbids a sound produces unpredictable behaviour, not a compromise. Re-read the whole caption as one instruction set |
| **Three blocks collapse into one paragraph** | A bulk whitespace collapse ran over the whole caption | Split on the headings and rejoin with blank lines; never collapse `\s{2,}` across the whole string. See the note in `SKILL.md` |
| **Track is far shorter than requested** | Length was requested in the caption | Duration is not a caption parameter on the hosted API and a caption cannot extend it. Design the release as a track count sized to the provider's real per-track length, then assemble |

---

## Fast diagnostic

Ask these three questions about any failed output:

1. **Did an unwanted vocal appear?** → Rule 3 and 5 (exclusions), plus verify the flag.
2. **Is the energy flat across the whole track?** → Rule 4 (energy arc, instrument lifecycles).
3. **Is it musically competent but forgettable?** → Rules 1 and 2 (structure and performance technique,
   not adjectives).

Change **one or two variables at a time** between generations — tempo, lead instrument, arc shape, or
ending. Rewriting the entire prompt destroys your ability to attribute the change.
