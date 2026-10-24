#!/usr/bin/env python3
"""音樂驅動透明頻譜條 —— 輸出衍生檔。

用途：ProRes 4444 的透明 MOV 很忠實但很大（61 分鐘約 14 GB）。
本工具由**已渲染好的 MOV** 產生三種衍生檔，並逐一驗證 alpha：

  --verify                 只驗證來源 MOV 的 alpha 與規格
  --smaller-mov OUT        較小的透明 MOV（維持 ProRes 4444 + alpha，降低 fps／畫布）
  --flat-mp4 OUT           扁平 MP4 預覽（**不透明**，僅供觀看／上傳，不可當疊加條用）
  --transparent-mp4 OUT    嘗試產生帶 alpha 的 MP4；不支援時明確報錯而不是產出假檔

★ 關於 MP4 與 alpha（實測，2026-10-21，ffmpeg 8.1.2 / macOS）：
  - H.264 MP4 **格式本來就不支援 alpha**，任何 MP4 都不能當透明疊加條。
  - MP4 容器「可以」放帶 alpha 的編碼（VP9-alpha、AV1-alpha），但**本機 ffmpeg 會靜默丟掉 alpha**：
      ProRes/PNG → libvpx-vp9 → MP4 / WebM / MKV，輸出皆回報 yuv420p（alpha 全變 255）。
      libsvtav1 在此 build 只列 yuv420p / yuv420p10le；libx265 明確報
      「Loaded libx265 does not support alpha layer encoding」。
  - 因此本工具的 --transparent-mp4 會**先驗證**再決定，不會產出看起來正常但其實不透明的檔案。
"""
import argparse
import json
import os
import subprocess
import sys


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r


def ensure_parent(path):
    """輸出目錄不存在就建立。ffmpeg 不會自動建目錄。"""
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)
    return path


def ffprobe(path):
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    return json.loads(r.stdout)


def verify(path):
    d = ffprobe(path)
    v = [s for s in d["streams"] if s["codec_type"] == "video"]
    a = [s for s in d["streams"] if s["codec_type"] == "audio"]
    info = {
        "path": path,
        "video_streams": len(v),
        "audio_streams": len(a),
        "codec": v[0].get("codec_name") if v else None,
        "pix_fmt": v[0].get("pix_fmt") if v else None,
        "alpha": bool(v and str(v[0].get("pix_fmt", "")).startswith("yuva")),
        "size": v[0].get("width") if v else None,
        "height": v[0].get("height") if v else None,
        "fps": v[0].get("r_frame_rate") if v else None,
        "duration": float(d["format"].get("duration", 0)),
        "bytes": int(d["format"].get("size", 0)),
    }
    return info


def decode_alpha_stats(path, at=5.0):
    """實際解碼一幀，確認 alpha 不是被壓平。"""
    out = "/tmp/_alpha_check.png"
    r = run(["ffmpeg", "-y", "-v", "error", "-ss", str(at), "-i", path,
             "-frames:v", "1", "-pix_fmt", "rgba", out])
    if r.returncode != 0 or not os.path.exists(out):
        return None
    try:
        import numpy as np
        from PIL import Image
        a = np.asarray(Image.open(out))
        al = a[:, :, 3]
        return {"min": int(al.min()), "max": int(al.max()),
                "transparent_pct": round(float((al == 0).mean() * 100), 1),
                "opaque_pct": round(float((al == 255).mean() * 100), 1)}
    except Exception:
        return None
    finally:
        if os.path.exists(out):
            os.remove(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="已渲染的透明 MOV")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--smaller-mov")
    ap.add_argument("--fps", type=int, default=15)
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--flat-mp4")
    ap.add_argument("--flat-crf", type=int, default=22)
    ap.add_argument("--transparent-mp4")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    info = verify(a.input)
    print("來源檔：")
    for k, v in info.items():
        print(f"  {k}: {v}")
    st = decode_alpha_stats(a.input)
    if st:
        print(f"  alpha 實解碼: {st}")

    if a.verify:
        return 0

    if a.smaller_mov:
        ensure_parent(a.smaller_mov)
        w = a.width or info["size"]
        h = a.height or info["height"]
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.input,
               "-vf", f"scale={w}:{h}:flags=lanczos",
               "-r", str(a.fps),
               "-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le",
               "-alpha_bits", "16", "-vendor", "apl0", "-threads", "2"]
        if a.overwrite:
            cmd.append("-y")
        cmd.append(a.smaller_mov)
        r = run(cmd)
        if r.returncode != 0:
            print("較小透明 MOV 失敗：", r.stderr[-800:])
            return 1
        new = verify(a.smaller_mov)
        nst = decode_alpha_stats(a.smaller_mov)
        print("\n較小透明 MOV：")
        for k, v in new.items():
            print(f"  {k}: {v}")
        if nst:
            print(f"  alpha 實解碼: {nst}")
        print(f"  縮小比：{info['bytes'] / max(new['bytes'], 1):.1f}×")

    if a.flat_mp4:
        ensure_parent(a.flat_mp4)
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.input,
               "-c:v", "libx264", "-preset", "medium", "-crf", str(a.flat_crf),
               "-pix_fmt", "yuv420p", "-an", a.flat_mp4]
        r = run(cmd)
        if r.returncode != 0:
            print("扁平 MP4 失敗：", r.stderr[-800:])
            return 1
        new = verify(a.flat_mp4)
        print("\n扁平 MP4 預覽（**不透明**，不可當疊加條用）：")
        for k, v in new.items():
            print(f"  {k}: {v}")
        print(f"  縮小比：{info['bytes'] / max(new['bytes'], 1):.1f}×")

    if a.transparent_mp4:
        ensure_parent(a.transparent_mp4)
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.input,
               "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-auto-alt-ref", "0",
               "-b:v", "0", "-crf", "32", a.transparent_mp4]
        r = run(cmd)
        if r.returncode != 0:
            print("透明 MP4 編碼失敗：", r.stderr[-600:])
            return 1
        new = verify(a.transparent_mp4)
        nst = decode_alpha_stats(a.transparent_mp4)
        print("\n透明 MP4 嘗試結果：")
        for k, v in new.items():
            print(f"  {k}: {v}")
        if nst:
            print(f"  alpha 實解碼: {nst}")
        if not new["alpha"] or (nst and nst["min"] == 255):
            print("  ✗ 這個 ffmpeg 產不出帶 alpha 的 MP4 —— 檔案已刪除，不要使用。")
            if os.path.exists(a.transparent_mp4):
                os.remove(a.transparent_mp4)
            return 2
        print("  ✓ alpha 存活")
    return 0


if __name__ == "__main__":
    sys.exit(main())
