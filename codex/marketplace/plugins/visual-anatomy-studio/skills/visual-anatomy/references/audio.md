# Music, narration and sound

## Choose only an available audio route

Audio-generation tools differ by computer and session. Inspect the current tool catalog
and load the relevant provider skill before use. Match the requested output to a tool
that actually produces it. If none is available, deliver the page with the supported
media and state which audio asset is missing; a script or MIDI file is not a rendered
audio track.

When MiniMax Design MCP is available, follow the project and live-contract workflow in
[imagery.md](imagery.md). Discover `generate_music` and `generate_speech` capabilities
with `capability_list`, then read each selected contract with `capability_get`. These
MiniMax examples describe the currently observed catalog; the live contract for the
current session takes precedence.

| Need | MiniMax route | Important boundary |
|---|---|---|
| Instrumental score or song | `generate_music:music-3.0` | `mode` is `instrumental` or `song`; no audio references are accepted. |
| Narration, dialogue or character speech | `generate_speech:seed-audio-1.0` | Default speech route; prompt can describe delivery and ambience or sound effects. |
| Preset voice, pronunciation override or speech effect | `generate_speech:speech-2.8-hd` | Search preset voices with `voice_search`; pass the selected `voice_id` and its source. |
| New voice from a description | `generate_speech:voice_design` | Use only when the user requests a custom voice; save and reuse its returned `voiceId`. |
| New voice from a recording | `generate_speech:voice_clone` | Use a recording the speaker owns or has authorized for cloning; follow the live sample limits. |

The currently observed MiniMax catalog has no standalone sound-effects generation
operation. Seed Audio can include ambience and effects with speech, but do not promise an
isolated Foley or SFX asset unless a live capability explicitly supports it. `voice_design`
creates a speaking voice; it does not create music or sound effects.

## Write and generate the audio plan

- Decide whether the page benefits from narration, music or ambience. Keep these tracks
  separate when they need independent playback, volume or later editing.
- For a song, show the lyrics and get the user's approval before generation. The current
  Music-3.0 contract may sing the prompt itself when lyrics are omitted. For instrumental
  music, use the instrumental mode and do not pass lyrics.
- For a voiceover, prepare the script and pronunciation of names or technical terms. Use
  a preset voice when the user wants a known catalog voice; create a custom voice only
  when requested. Reuse the same voice ID across clips instead of creating a new voice
  each time.
- A cloned voice requires an authorized recording. Do not upload a speaker sample to a
  provider unless the user requested that use and has permission to use the recording.
- Keep requested sound effects distinct from speech. If only a speech generator is
  available, describe effects only when that generator's contract supports them and
  disclose that a separate SFX track could not be confirmed.
- For precise narration or music over generated video, turn off video audio when that
  capability allows it. Use an available media editor to mix tracks; if none is present,
  deliver separate files and do not claim that they were mixed or synchronized.

## Tasks, cost and retrieval

Follow the provider's live task and billing contract. For MiniMax tasks, continue waiting
with `task_wait` and the same `taskId`; do not submit another generation because a wait
timed out. If a task enters `waiting_user` with a cost quote, show the amount and wait for
the user's explicit approval before calling `confirm_cost`. Creating a custom voice may
be separately billed; reuse the returned voice ID.

Retrieve finished audio through the provider's result method. For MiniMax Design, use
`get_output` with the returned `versionId`, then copy the local result into the website's
`audio/` folder. Do not expose temporary asset URLs as permanent page URLs. Retain the
source audio in the provider project when useful and keep website assets beside the HTML.

## Add audio to the page

Use a visible player with an explicit label. Do not autoplay speech, music or sound
effects. Give narration a transcript and make the player usable by keyboard and screen
readers.

```html
<figure class="audio-card">
  <figcaption>旁白｜血液如何運送氧氣</figcaption>
  <audio controls preload="none">
    <source src="audio/narration.mp3" type="audio/mpeg">
  </audio>
  <details>
    <summary>查看旁白文字</summary>
    <p>在肺部，氧氣進入血液並與血紅素結合……</p>
  </details>
</figure>
```

Check that the audio file loads and the player is visible. A successful load does not
prove the speech, mix or sound quality; report listening as unverified unless it was
actually heard.
