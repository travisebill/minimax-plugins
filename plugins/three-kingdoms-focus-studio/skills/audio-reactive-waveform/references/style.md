# Style JSON

All fields are optional; omitted fields use `assets/gold-mirrored.json` defaults.
Unknown keys fail fast. Pass `--style "/path/to/style.json"`; `--width`, `--height`
and `--fps` override the corresponding JSON fields.

| Field | Meaning and accepted value |
| --- | --- |
| `width`, `height` | Even pixels; width 320–3840, height 140–2160 |
| `fps` | Integer 1–60; default 30 |
| `bars` | Integer 8–96, default 48; log-spaced 55 Hz–14 kHz frequency bands |
| `shape` | `mirrored` grows above/below baseline; `single` grows upward |
| `top_color`, `bottom_color` | RGB arrays of three integers 0–255; equal values give a flat color |
| `bar_width` | Full bar width / canvas width; greater than 0 and at most 0.1 |
| `margin` | Left/right bar-center inset / width; 0–0.45 exclusive at upper bound |
| `baseline` | Baseline y / height; 0 is top, 1 bottom; strictly between 0 and 1 |
| `min_height`, `max_height` | Above-baseline height / canvas height; mirrored adds the same amount below |
| `attack`, `release` | Smoothing coefficients at 30 fps, greater than 0 and at most 1; larger means faster |

Bars must fit within horizontal margins without overlap (including the antialias
edge). The renderer rejects combinations that cannot fit. Require
0 < min_height <= max_height < baseline for single bars; mirrored additionally
requires max_height < 1 - baseline. Reduce bar count/width when necessary.

Example: cool blue upward bars. This changes only listed fields:

```json
{
  "shape": "single",
  "bars": 32,
  "baseline": 0.8,
  "max_height": 0.6,
  "top_color": [95, 220, 255],
  "bottom_color": [35, 100, 240],
  "attack": 0.6,
  "release": 0.15
}
```

The 8192-sample FFT, logarithmic bands, frequency compensation and percentile
normalization are fixed in this version. Frame-rate changes preserve the
approximate smoothing time in seconds. The canvas stays fixed: put this small
transparent overlay wherever desired in the video editor. No automatic subject
tracking or baked-in background is applied.
