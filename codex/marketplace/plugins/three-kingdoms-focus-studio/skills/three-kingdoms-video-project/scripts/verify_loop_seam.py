#!/usr/bin/env python3
"""驗證循環影片的繞回接縫（loop seam）是否無縫。

用法:
    python3 verify_loop_seam.py <video.mp4> [--out-dir DIR] [--json OUT.json]

原理
----
對影片逐影格取灰階縮圖，計算「相鄰影格平均絕對差」。
無縫循環的定義是：繞回時的最後一幀 → 第一幀，其差異必須落在
逐幀基準分布之內（不該是整段影片中最大的一次跳變）。

門檻（皆為經驗值，必須在報告中一併寫出）
  - 主要判準：wrap <= max(diffs)
    「繞回差異不得大於片內本來就會出現的單次轉場」。
    慢速氛圍片的逐幀差異本來就會浮動（實測 0.03–0.91），
    用中位數或 p95 當門檻會誤判「來回鏡頭」這類
    繞回等於自然轉場的合法無縫版本。
  - 嚴格判準（僅供參考）：wrap <= p95
    代表繞回連「片內前 5% 的轉場」都不算。
  - 否則 → 軟接縫；用像素比例補充描述嚴重度
  - 注意：重新編碼會在差異量測上加入雜訊。
    同一素材以 libx264 crf 14 重編後，量得差異可由 0.65 升到 0.78。
    跨版本比較時要把編碼條件一併寫出。

自我檢查
--------
本腳本帶 --self-check：對一段「數學上保證無縫」的來回鏡頭影片
（ping-pong）與一段「已知有接縫」的影片跑同一套量測，確認
判定邏輯能分辨兩者。任何量測都必須先確認方法本身有效。
"""

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile

WIDTH, HEIGHT = 640, 360


def extract_frames(video, out_dir, width=WIDTH, height=HEIGHT):
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    cmd = [
        "ffmpeg", "-hide_banner", "-v", "error", "-i", video,
        "-vf", f"scale={width}:{height}",
        "-start_number", "0",
        os.path.join(out_dir, "f%04d.png"),
    ]
    subprocess.run(cmd, check=True)
    return sorted(
        os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.endswith(".png")
    )


def load_gray(paths):
    import numpy as np
    from PIL import Image

    return [np.asarray(Image.open(p).convert("L"), dtype=np.float32) for p in paths]


def analyze(video, out_dir=None):
    import numpy as np

    tmp = tempfile.mkdtemp(prefix="loopseam-")
    try:
        frames = extract_frames(video, out_dir or os.path.join(tmp, "frames"))
        if not frames:
            raise RuntimeError("抽不出影格")
        arrs = load_gray(frames)
        n = len(arrs)

        diffs = [float(np.mean(np.abs(arrs[i + 1] - arrs[i]))) for i in range(n - 1)]
        wrap = float(np.mean(np.abs(arrs[0] - arrs[-1])))

        # 首尾逐像素差異分布（描述軟接縫的嚴重程度）
        d = np.abs(arrs[0] - arrs[-1])
        over = {str(t): float((d > t).mean() * 100) for t in (2, 4, 8, 16, 32)}

        med = statistics.median(diffs)
        p95 = sorted(diffs)[int(len(diffs) * 0.95)]
        max_nat = max(diffs)
        rank = sorted([wrap] + diffs).index(wrap) + 1  # 1 = 最小

        # 主要判準：繞回不得大於片內已自然出現的最大轉場
        seamless = wrap <= max_nat
        # 嚴格判準：連片內前 5% 的轉場都不算
        strict = wrap <= p95

        return {
            "video": os.path.abspath(video),
            "frames": n,
            "consecutive_diff_median": round(med, 4),
            "consecutive_diff_mean": round(statistics.mean(diffs), 4),
            "consecutive_diff_p95": round(p95, 4),
            "consecutive_diff_max": round(max_nat, 4),
            "wrap_diff": round(wrap, 4),
            "wrap_over_median": round(wrap / med, 3) if med else None,
            "wrap_over_max_natural": round(wrap / max_nat, 3) if max_nat else None,
            "wrap_rank_among_transitions": f"{rank}/{len(diffs) + 1}",
            "threshold_used": round(max_nat, 4),
            "threshold_rule": "wrap <= max(natural consecutive diff)",
            "seamless": bool(seamless),
            "seamless_strict": bool(strict),
            "first_last_pixel_diff_mean": round(float(d.mean()), 4),
            "first_last_pixel_diff_max": round(float(d.max()), 1),
            "pct_pixels_over_diff": {k: round(v, 4) for k, v in over.items()},
            "verdict": (
                f"無縫：繞回差異 {wrap:.4f} 不大於片內最大自然轉場 {max_nat:.4f}"
                f"（為中位數的 {wrap / med:.2f}x）"
                if seamless else
                f"軟接縫：繞回差異 {wrap:.4f} 超過片內最大自然轉場 {max_nat:.4f}"
                f"（為中位數的 {wrap / med:.2f}x，且為全部 {len(diffs) + 1} 次轉場中第 {rank} 大）"
            ),
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def probe(video):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_frames",
        "-show_entries", "format=duration",
        "-of", "json", video,
    ]
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


def self_check(good, bad):
    """對照組驗證：確認判定邏輯能分辨已知無縫與已知有接縫的素材。

    GOOD 應該是「繞回等於片內自然轉場」的合法無縫版本（例如來回鏡頭）；
    BAD 應該是「繞回大於片內任何自然轉場」的真正接縫版本。
    """
    r_good = analyze(good)
    r_bad = analyze(bad)
    ok = r_good["seamless"] is True and r_bad["seamless"] is False
    print("=== 自我檢查（對照組）===")
    print(f"  對照組 A（應為無縫）{os.path.basename(good)}:")
    print(f"    wrap={r_good['wrap_diff']}  片內最大自然轉場={r_good['consecutive_diff_max']}  "
          f"中位數={r_good['consecutive_diff_median']}  → seamless={r_good['seamless']}")
    print(f"  對照組 B（應有接縫）{os.path.basename(bad)}:")
    print(f"    wrap={r_bad['wrap_diff']}  片內最大自然轉場={r_bad['consecutive_diff_max']}  "
          f"中位數={r_bad['consecutive_diff_median']}  → seamless={r_bad['seamless']}")
    print(f"  判定邏輯有效性: {'通過' if ok else '失敗 —— 量測方法不可信，結論不可用'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out-dir", default=None, help="保留抽出的影格到指定目錄")
    ap.add_argument("--json", default=None, help="把結果寫成 JSON")
    ap.add_argument("--self-check", nargs=2, metavar=("GOOD", "BAD"), default=None,
                    help="對照組自我檢查：GOOD 應無縫、BAD 應有接縫")
    ap.add_argument("--no-probe", action="store_true")
    args = ap.parse_args()

    if args.self_check:
        if not self_check(args.self_check[0], args.self_check[1]):
            return 2

    result = analyze(args.video, args.out_dir)
    if not args.no_probe:
        result["probe"] = probe(args.video)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
