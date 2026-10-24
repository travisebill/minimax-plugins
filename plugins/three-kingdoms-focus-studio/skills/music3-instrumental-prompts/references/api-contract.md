# MiniMax Music 3.0 — API Contract for Instrumental Generation

Verified against the official MiniMax API reference. Last checked 2026-09-29.

## ★ First identify the route

Music 3.0 is reachable through four different interfaces with **different
parameters**. This file describes the hosted API and the SGLang open-weight
route; the MCP route and the local connector are listed so their limits are not
mistaken for these.

| Route | Instrumental control | Length control | Prompt limit | This file |
|---|---|---|---|---|
| Hosted Music Generation API | `is_instrumental: true` | none | 2,000 chars | § below |
| **MiniMax Design MCP** | `params.mode: "instrumental"` | **none — timeline in the prompt only** | 2,000 chars | pointer only |
| SGLang open-weight | none | `max_new_tokens` | 5,000 tokens | § below |
| Local connector wrapper | **no flag exists** | none | schema-dependent | § below |

Two corrections that must not be repeated:

- **`max_new_tokens` exists only on the SGLang route.** It is not a parameter of
  the hosted API and it is not a parameter of the MCP. The MCP exposes no length
  parameter at all; the only lever is a minute-level timeline inside the prompt
  (measured 2026-10-22: the same caption gave 59.9 s with no timeline and
  188 s with a `0:00 … 3:50` timeline).
- **The instrumental flag differs per route.** The hosted API's flag is
  `is_instrumental`. The MCP's is `params.mode: "instrumental"`. On the MCP the
  `lyrics` field exists only in `mode: "song"`, and it is **not** a control: five
  `lyrics` values including an empty control all produced wordless vocals
  (measured 2026-10-22, 18 candidates).

For the full MCP contract, the ten measured failure modes and the output
retrieval procedure, read
`skills/yt-focus-music-pipeline/references/design-mcp-execution.md`.

---

## Endpoint

```
POST https://api.minimax.io/v1/music_generation
Authorization: Bearer <API key>
Content-Type: application/json
```

## Instrumental request shape

```json
{
  "model": "music-3.0",
  "is_instrumental": true,
  "prompt": "<Structured Caption, 1-2000 characters>",
  "audio_setting": {
    "sample_rate": 44100,
    "bitrate": 256000,
    "format": "wav"
  },
  "output_format": "url"
}
```

`lyrics` is omitted entirely. `lyrics_optimizer` is a vocal-mode feature and is not used here.

---

## Parameters in instrumental mode

| Parameter | Rule | Notes |
|---|---|---|
| `model` | required | `music-3.0` (recommended), `music-2.6` for the previous generation |
| `is_instrumental` | required for instrumental | Set `true` to suppress vocals. This is the only switch that enables instrumental output **on the hosted API**. On the MiniMax Design MCP the equivalent is `params.mode: "instrumental"`; on the SGLang route and the local connector there is **no flag at all**, so instrumental output cannot be guaranteed on those routes |
| `prompt` | **required, 1–2000 characters** | The entire control channel for instrumental |
| `lyrics` | not required | Do not rely on it for structure in this mode |
| `lyrics_optimizer` | not applicable | Only for auto-generating lyrics on vocal requests |
| `stream` | optional, default `false` | When `true`, only `hex` output is supported |
| `output_format` | `url` \| `hex`, default `hex` | ⚠️ `url` links **expire after 24 hours** — download immediately |
| `audio_setting.sample_rate` | `16000` \| `24000` \| `32000` \| `44100` | Use `44100` |
| `audio_setting.bitrate` | `32000` \| `64000` \| `128000` \| `256000` | Use `256000` |
| `audio_setting.format` | `mp3` \| `wav` \| `pcm` | Use `wav` for delivery work |

### For comparison — the vocal-mode rules

- `prompt`: optional, 0–2000 characters
- `lyrics`: **required**, 1–3500 characters
- Supported structure tags in `lyrics`: `[Intro]`, `[Verse]`, `[Pre Chorus]`, `[Chorus]`,
  `[Interlude]`, `[Bridge]`, `[Outro]`, `[Post Chorus]`, `[Transition]`, `[Break]`, `[Hook]`,
  `[Build Up]`, `[Inst]`, `[Solo]`

These tags are a **vocal-mode** feature. In instrumental mode, express the section timeline in the
`prompt` instead.

---

## Model availability

Official notice, verbatim:

> Starting August 20, 2026, the paid APIs (Music Generation and Lyrics Generation) will no longer be
> available to new users; existing paying users can continue to use the current API services. The
> free music generation APIs (Music-3.0-free, Music-2.6-free, music-cover-free) will be discontinued.
> To experience or use music generation capabilities, please visit MiniMax Audio, or use the
> open-source MiniMax Music 3 model on Hugging Face.

| Path | Who | Notes |
|---|---|---|
| MiniMax Audio (web) | Everyone | The official consumer entry point |
| Hosted API `music-3.0` | Existing paid / Token Plan users | 120 RPM |
| HuggingFace `MiniMaxAI/MiniMax-Music3` | Teams with GPUs | Open weights, 32 kHz 16-bit stereo WAV |

Rate limits, where access still exists: `music-3.0` / `music-2.6` / `music-cover` = 120 RPM;
the `-free` variants were 3 RPM before discontinuation.

---

## Response shape

```json
{
  "data": {
    "audio": "<hex-encoded audio data>",
    "status": 2
  },
  "trace_id": "04ede0ab069fb1ba8be5156a24b1e081",
  "extra_info": {
    "music_duration": 25364,
    "music_sample_rate": 44100,
    "music_channel": 2,
    "bitrate": 256000,
    "music_size": 813651
  },
  "base_resp": { "status_code": 0, "status_msg": "success" }
}
```

---

## Open-weights runtime (SGLang route)

> **This section is the SGLang route only.** `max_new_tokens` below is a
> parameter of *this* interface only. It does not exist on the hosted API, and it
> does not exist on the MiniMax Design MCP — the MCP has no length parameter
> whatsoever, and its only length lever is a minute-level timeline written into
> the prompt.

Model: `MiniMaxAI/MiniMax-Music3` — 8B Global LLM (Qwen3-8B init) + 0.6B Local LLM, with
continuous hidden-state synthesis through Flow Matching (2.4B) and Flow-VAE (123M).
Output is **32 kHz, 16-bit stereo WAV**. Up to ~5 minutes per generation.

```bash
hf download MiniMaxAI/MiniMax-Music3 --local-dir /path/to/minimax_music3
sgl-omni serve --model-path MiniMaxAI/MiniMax-Music3 --port 8000
```

Served over the shared speech API — lyrics go in `input`, the music description in `instructions`:

```bash
curl http://127.0.0.1:8000/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "MiniMaxAI/MiniMax-Music3",
    "input": "",
    "instructions": "<your Structured Caption>",
    "response_format": "wav",
    "seed": 7,
    "max_new_tokens": 750,
    "stream": false
  }' \
  --output track.wav
```

`max_new_tokens` caps audio frames at 25 frames/second (750 ≈ 30 s). Generation may finish earlier
when the model emits an end-of-audio token. To target ~5 minutes, set it near 7500.

**Limitations:** inference requires CUDA; non-streaming only; text prompt capped at 5,000 tokens;
audio capped at 9,000 acoustic frames (≈ 6 minutes).

**The model does not guarantee literal compliance.** Section tags and descriptions are generative
control, not symbolic constraints — actual tempo, key, instrumentation, and structure may deviate
from what you asked for. This is why vague-but-honest beats confidently-wrong.

---

## Sources

- <https://platform.minimax.io/docs/api-reference/music-generation>
- <https://platform.minimax.io/docs/guides/music-generation>
- <https://huggingface.co/MiniMaxAI/MiniMax-Music3>
