# Failure Modes — symptom → fix

Diagnose against these before rewriting a prompt from scratch. Most mediocre instrumental output is
one of the six rows below.

| Symptom | Root cause | Fix |
|---|---|---|
| **Generic, interchangeable output** | Adjective pile with no time axis | Switch to the three-block Structured Caption; write a real `Arrangement` timeline |
| **Every instrument plays all the way through** | Gear list instead of lifecycle | Assign each instrument an entry/exit point; write the energy arc |
| **Humming, chanting, or "oooh" appears** | Instrumental not stated in the description text | Add `no vocals, no choir, no spoken word, no vocal samples`, and confirm `is_instrumental: true` |
| **Flat, no build, no payoff** | Structure only exists in `lyrics`, which instrumental mode ignores | Move the entire section timeline into the `Arrangement` block of `prompt` |
| **Wrong or drifting key/tempo** | Fabricated precision | Drop the exact number, use a range or qualitative tempo, lean harder on the emotional arc |
| **Sounds like a specific film/artist** | Referencing rather than describing | Replace the reference with its constituent traits (instruments, groove, production character) |
| **Overstuffed / cluttered mix** | All instruments at equal prominence | Name one lead melodic carrier; demote the rest to bed, pad, or texture |
| **Weak or absent ending** | No resolution described | State the final cadence, decay length, and what survives into the last bar |
| **Rejects the request / feels generic-safe** | Named an artist or franchise | Never reference. Always describe style in musical terms |
| **Prompt rejected by the API** | Over 2,000 characters | Target 280–320 words; cut decorative adjectives first, never the `Arrangement` timeline |

---

## Fast diagnostic

Ask these three questions about any failed output:

1. **Did an unwanted vocal appear?** → Rule 3 and 5 (exclusions), plus verify the flag.
2. **Is the energy flat across the whole track?** → Rule 4 (energy arc, instrument lifecycles).
3. **Is it musically competent but forgettable?** → Rules 1 and 2 (structure and performance technique,
   not adjectives).

Change **one or two variables at a time** between generations — tempo, lead instrument, arc shape, or
ending. Rewriting the entire prompt destroys your ability to attribute the change.
