#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
locate_level_jumps.py — 找出短時響度跳變的具體時間戳

用途：當某候選的 `windows_above_median_3lu` / `_6lu` 偏離群體時，
把「哪些瞬間跳了」變成可複聽的時間點，而不是一個抽象的計數。

沿用 `three-kingdoms-music-review/scripts/measure_audio.py` 的
`short_term_windows()` 同一套量測方式（ffmpeg ebur128，100 ms 窗），
所以數字與該工具產出的報告一致。

用法：
    python locate_level_jumps.py <audio> [--above 6] [--output report.json]
"""
import argparse, json, os, re, shutil, subprocess, sys
import numpy as np


def short_term_windows(source):
    """100 ms 短時響度（含時間戳）。與 measure_audio.py 相同作法。"""
    ebu = subprocess.run(
        ['ffmpeg', '-hide_banner', '-nostdin', '-nostats', '-i', str(source),
         '-map', '0:a:0', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    text = ebu.stderr.decode('utf-8', 'replace')
    events = []
    for line in text.splitlines():
        # ebur128 每行帶 [Parsed_ebur128_0 @ 0x...] 前綴，必須用 regex 不可用 startswith
        stamp = re.search(r'\bt:\s*([\d.]+)', line)
        value = re.search(r'\bS:\s*(-?[\d.]+|-inf)(?=\s)', line)
        if not stamp or not value or value.group(1) == '-inf':
            continue
        events.append((float(stamp.group(1)), float(value.group(1))))
    return events


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("--above", type=float, default=6.0,
                    help="高於中位數多少 LU 算一次跳變（預設 6）")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    src = os.path.abspath(args.source)
    if not os.path.isfile(src):
        raise SystemExit(f"找不到檔案: {src}")
    if not shutil.which("ffmpeg"):
        raise SystemExit("缺少 ffmpeg")

    ev = short_term_windows(src)
    if not ev:
        raise SystemExit("取不到短時響度資料")
    values = [v for _, v in ev]
    ordered = sorted(values)
    median = ordered[len(ordered) // 2]
    thr = median + args.above

    jumps = [(t, v) for t, v in ev if v > thr]
    over3 = [(t, v) for t, v in ev if v > median + 3.0]

    report = {
        "schema_version": 1,
        "source": {"path": src, "bytes": os.path.getsize(src)},
        "window_seconds": 0.1,
        "windows_assessed": len(values),
        "median_lufs": round(median, 2),
        "threshold_lufs": round(thr, 2),
        "windows_above_median_3lu": len(over3),
        "windows_above_median_6lu": len(jumps),
        "above_3lu_ratio_pct": round(100 * len(over3) / len(values), 2),
        "above_6lu_ratio_pct": round(100 * len(jumps) / len(values), 2),
        "jumps": [{"time_sec": round(t, 2),
                   "timecode": f"{int(t//60):02d}:{t % 60:05.2f}",
                   "short_term_lufs": round(v, 2),
                   "above_median_lu": round(v - median, 2)} for t, v in jumps],
        "evidence": "measured",
        "interpretation_guide": {
            "SCOPE": "數字是 genre-relative 的參考值，不是 pass/fail 線。工具本身註明 "
                      "'Never apply a cross-genre absolute as a pass/fail line'，"
                      "且 rubric 說明 technical loudness alone cannot establish focus suitability。"
                      "本報告的用途是指出可複聽的時間點，不是宣告缺陷。",
            "METHOD": "沿用 measure_audio.py 的 short_term_windows()：ffmpeg ebur128 的 100 ms 短時響度窗。",
        },
    }
    if args.output:
        with open(os.path.abspath(args.output), "x", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(json.dumps({k: v for k, v in report.items() if k != "jumps"}, ensure_ascii=False, indent=2))
    if jumps:
        print("\n跳變時間點：")
        for j in report["jumps"]:
            print(f"  {j['timecode']}  短時 {j['short_term_lufs']:>7} LUFS  （高於中位數 {j['above_median_lu']:+.2f} LU）")


if __name__ == "__main__":
    main()
