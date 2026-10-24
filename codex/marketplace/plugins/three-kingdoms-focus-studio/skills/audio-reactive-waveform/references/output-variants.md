# 輸出衍生檔與檔案大小

ProRes 4444 的透明 MOV 很忠實，但很大。實測基準（2026-10-21，macOS，ffmpeg 8.1.2）：

| 產出 | 20 秒 | 61.4 分鐘 | alpha |
|---|---|---|---|
| ProRes 4444 640×280 @30fps（預設） | 73.2 MB | **14.3 GB** | ✅ |
| ProRes 4444 480×210 @15fps | 36.4 MB | ~7.2 GB | ✅ |
| 扁平 H.264 MP4（**不透明**） | 0.35 MB | ~0.2 GB | ❌ |

## ★ MP4 能不能透明？—— 不能（以 H.264 而言）

**H.264 MP4 格式本來就不支援 alpha。** 任何 MP4 都不能當成透明疊加條使用。

MP4 *容器*「可以」放帶 alpha 的編碼（VP9-alpha、AV1-alpha），但**實測本機 ffmpeg 會靜默丟掉 alpha**：

| 編碼 | 結果 |
|---|---|
| ProRes 4444 (MOV) | ✅ 唯一能保住 alpha |
| H.264 (MP4) | ❌ 格式不支援 |
| VP9 (MP4 / WebM / MKV) | ❌ 編碼器列有 `yuva420p`，但實測 alpha 被丟棄，輸出回報 `yuv420p` |
| SVT-AV1 | ❌ 此 build 只列 `yuv420p` / `yuv420p10le` |
| libx265 | ❌ 明確報錯 `Loaded libx265 does not support alpha layer encoding` |

> 測試涵蓋 ProRes→VP9、PNG→VP9、VP9→MP4/WebM/MKV、SVT-AV1。
> **不要產出「看起來正常但其實不透明」的 MP4** —— 那比沒有更糟。

## 怎麼把檔案變小

### 1. 較小的透明 MOV（維持 ProRes 4444 + alpha）

`scripts/make_variants.py --smaller-mov` 會由已渲染的 MOV 轉出，並**實測驗證 alpha 存活**：

```sh
python "$SKILL_DIR/scripts/make_variants.py" \
  --input "/path/to/full.mov" \
  --smaller-mov "/path/to/full-small.mov" \
  --fps 15 --width 480 --height 210
```

降低 fps 對頻譜條影響很小（這是慢速視覺化，不是運動鏡頭），畫布縮小則線性縮小容量。
**要更小就再降**：320×140 @ 12 fps ≈ 14.3 GB → 2.5 GB 左右。

也可以直接用渲染器的覆寫參數重跑（要重新做頻譜分析，約 40 分鐘／61 分鐘音檔）：

```sh
python "$SKILL_DIR/scripts/render_waveform.py" --input music.wav --output small.mov \
  --style style.json --width 480 --height 210 --fps 15
```

### 2. 扁平 MP4 預覽（**不透明**，僅供觀看）

```sh
python "$SKILL_DIR/scripts/make_variants.py" --input full.mov --flat-mp4 preview.mp4
```

★ **這不是疊加條。** 它是給人看的預覽，不能疊在別的影片上。交付時必須標註為 nontransparent。

### 3. 分章輸出

要匯入剪輯軟體時，61 分鐘的單一檔案很大。依章節切成數個透明 MOV 會好匯入得多
（每段各自可單獨拖進時間軸）。用 `--duration` 逐段渲染，或由完整 MOV 切片：

```sh
# 每章各自的時間區間由音檔的章節起點決定
ffmpeg -y -i full.mov -ss "$START" -t "$LEN" -c copy chapter-NN.mov
```

### 4. 上傳用的最終影片

**最終上傳影片不需要 alpha。** 用 ffmpeg 把背景與透明疊加條合成，再接音軌，輸出 H.264 MP4：

```sh
ffmpeg -y -stream_loop -1 -i background.mp4 -i overlay.mov -i music.wav \
  -filter_complex "[0:v]scale=1920:1080,setsar=1[bg];[bg][1:v]overlay=X:Y:shortest=1[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 256k -movflags +faststart final.mp4
```

61.4 分鐘的 1920×1080 成品約 2 GB —— 比 14.3 GB 的透明 MOV 小七倍，而且可以直接上傳。

## 驗證

`make_variants.py --verify` 會回報串流數、編碼、pixel format、是否有 alpha、
以及**實際解碼一幀後的 alpha 統計**（min/max/透明百分比）。
不要只信 ffprobe 報告的 pixel format —— 實測有編碼器會「宣稱」支援 alpha 卻產出全不透明的檔案。
