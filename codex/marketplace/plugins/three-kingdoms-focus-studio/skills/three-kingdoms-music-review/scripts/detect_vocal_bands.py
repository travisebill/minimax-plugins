#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_vocal_bands.py — 人聲共振峰帶域的客觀佐證

用途：當音訊模型報告「有人聲」時，用頻譜走勢交叉驗證該主張。
原理：持續性人聲帶有共振峰結構，在 2.5–4 kHz 會出現與音節同步的
      週期性起伏，且與相鄰「無人聲」窗的走勢**不一致**。
      若爭議窗的 2.5–4 kHz 走勢與前後窗一致（同樣的週期性起伏），
      則較可能是樂器音色而非人聲。

這是「有多少」的量測，不是「那是什麼」的判定。最終仍需聆聽。
輸出為 JSON，證據標籤固定為 `measured`。

用法：
    python detect_vocal_bands.py <audio> --output <report.json> [--window 0.25]
"""
import argparse, json, hashlib, os, shutil, subprocess, sys
import numpy as np


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def decode_pcm(path, sr=22050):
    """解碼為 float32 mono PCM（用來算頻譜；不是交付格式）。"""
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-i", path,
           "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64), sr


def band_energy_db(spec, freqs, lo, hi):
    """取 [lo,hi) 頻帶的總能量，以 dB 表示。"""
    m = (freqs >= lo) & (freqs < hi)
    if not m.any():
        return None
    e = float(np.sum(spec[m] ** 2))
    return 10.0 * np.log10(e + 1e-20)


def analyse(path, window=0.25, sr=22050, nfft=2048):
    samples, sr = decode_pcm(path, sr)
    win = int(sr * window)
    hop = win
    n_windows = len(samples) // hop
    if n_windows < 4:
        raise RuntimeError("音檔過短，無法做帶域趨勢分析")

    hann = np.hanning(nfft)
    rows = []
    freqs = np.fft.rfftfreq(nfft, 1.0 / sr)

    for i in range(n_windows):
        seg = samples[i * hop: i * hop + nfft]
        if len(seg) < nfft:
            seg = np.pad(seg, (0, nfft - len(seg)))
        spec = np.abs(np.fft.rfft(seg * hann))
        rows.append({
            "index": i,
            "start_sec": round(i * hop / sr, 3),
            "b1_200_400": band_energy_db(spec, freqs, 200, 400),
            "b2_1000_2500": band_energy_db(spec, freqs, 1000, 2500),
            "b3_2500_4000": band_energy_db(spec, freqs, 2500, 4000),
            "b4_8000_12000": band_energy_db(spec, freqs, 8000, 12000),
        })

    # 2.5-4 kHz 的起伏：相鄰窗的一階差分絕對值平均
    b3 = np.array([r["b3_2500_4000"] for r in rows])
    diff = np.abs(np.diff(b3))
    modulation = float(np.mean(diff))

    # 高頻底噪參考（8-12 kHz 在最安靜段）
    b4 = np.array([r["b4_8000_12000"] for r in rows])
    quiet_idx = int(np.argmin(b4))
    floor_8k = float(b4[quiet_idx])

    return {
        "window_seconds": window,
        "sample_rate_analysis": sr,
        "windows_assessed": n_windows,
        "b3_2500_4000_modulation_db": round(modulation, 3),
        "b3_modulation_note": "2.5-4 kHz 相鄰窗一階差分絕對值平均（dB）。人聲共振峰會造成較大的週期性起伏。",
        "quietest_window_index": quiet_idx,
        "quietest_window_start_sec": rows[quiet_idx]["start_sec"],
        "floor_8k_12k_db_at_quietest": round(floor_8k, 2),
        "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("--output", required=True)
    ap.add_argument("--window", type=float, default=0.25)
    ap.add_argument("--focus-sec", type=float, default=None,
                    help="指定爭議時間點（秒），以該點前後各 2.5 秒做走勢比對")
    ap.add_argument("--focus-span", type=float, default=2.5)
    args = ap.parse_args()

    src = os.path.abspath(args.source)
    if not os.path.isfile(src):
        raise SystemExit(f"找不到檔案: {src}")
    for b in ("ffmpeg",):
        if not shutil.which(b):
            raise SystemExit(f"缺少必要程式: {b}")
    out = os.path.abspath(args.output)
    if os.path.exists(out):
        raise SystemExit("輸出必須是新檔案；拒絕覆寫。")

    before = sha256(src)
    result = analyse(src, window=args.window)
    if sha256(src) != before:
        raise SystemExit("量測期間來源檔被改動，結果作廢。")

    result["schema_version"] = 1
    result["created_at"] = None
    result["source"] = {"path": src, "sha256": before, "bytes": os.path.getsize(src)}
    result["evidence"] = "measured"
    result["interpretation_guide"] = {
        "SCOPE": "此報告是帶域能量的量測，不是「那是什麼」的判定。任何關於特定來源的結論都需要聆聽佐證。",
        "b3_modulation_db": "2.5-4 kHz 的窗間起伏量。人聲共振峰會產生較大的、與音節同步的起伏。若爭議窗的走勢與前後窗一致，較可能是樂器音色而非持續人聲。",
        "floor_8k_12k_db_at_quietest": "最安靜窗的 8-12 kHz 能量。接近 -90 dB 代表無高頻雜訊床。",
        "LIMITATION": "單靠頻譜無法分辨人聲與音色相近的樂器（例如人聲音色合成器、簫的泛音）。此為佐證，不是判定。",
    }

    if args.focus_sec is not None:
        span = int(args.focus_span / args.window)   # 窗數，三段等寬
        total_sec = result["windows_assessed"] * args.window
        fc_sec = min(max(args.focus_sec, span), max(span, total_sec - span))
        if abs(fc_sec - args.focus_sec) > 0.5:
            result["focus_clamped_from_sec"] = args.focus_sec
        c = int(fc_sec / args.window)
        b3 = [r["b3_2500_4000"] for r in result["rows"]]

        def stats(a, b):
            seg = b3[max(0, a):max(0, b)]
            if not seg:
                return {"mean_db": None, "std_db": None, "range_db": None, "n_windows": 0}
            return {"mean_db": round(float(np.mean(seg)), 2),
                    "std_db": round(float(np.std(seg)), 2),
                    "range_db": round(float(np.max(seg) - np.min(seg)), 2),
                    "n_windows": len(seg)}

        mid = c
        focus = stats(mid - span // 2, mid - span // 2 + span)
        before = stats(mid - span - span // 2, mid - span // 2)
        after = stats(mid + span // 2, mid + span // 2 + span)
        neigh = [v for v in (before["range_db"], after["range_db"]) if v is not None]
        neigh_max = max(neigh) if neigh else None
        same = (focus["range_db"] is not None and neigh_max is not None
                and focus["range_db"] <= neigh_max + 1.0)
        result["focus_comparison"] = {
            "focus_sec": round(fc_sec, 2),
            "span_seconds_each": round(span * args.window, 3),
            "focus": focus,
            "before": before,
            "after": after,
            "verdict_hint": (
                "focus 的 2.5-4 kHz 起伏與前後窗相當或更低 → 較可能是樂器音色/持續音，不是持續性人聲特徵"
                if same else
                "focus 的 2.5-4 kHz 起伏明顯高於前後窗 → 有可能是持續性人聲特徵，需聆聽確認"
            ),
        }

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({
        "report": out,
        "source_sha256": before,
        "windows_assessed": result["windows_assessed"],
        "b3_modulation_db": result["b3_2500_4000_modulation_db"],
        "floor_8k_12k_db_at_quietest": result["floor_8k_12k_db_at_quietest"],
        "focus_comparison": result.get("focus_comparison"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
