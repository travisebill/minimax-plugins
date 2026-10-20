# MiniMax 音樂驅動透明頻譜條

`three-kingdoms-focus-studio` v1.3.0 新增第 8 支 skill：
`three-kingdoms-focus-studio:audio-reactive-waveform`。
將本地音樂轉成可疊在 CapCut 或其他剪輯軟體上的無聲透明 MOV，
預設為 48 條金黃至橘色、上下鏡像的頻譜條。
這是頻率分析視覺化，不是逐取樣波形或節拍偵測。

## 安裝與載入

在此 repository 根目錄執行。先確認 MiniMax 使用的資料目錄；
通常是 `~/.minimax`，舊 profile 可能是 `~/.mavis`。
下列以 `~/.minimax` 為例；若安裝處有自行修改，先比對與備份再同步。

```sh
rsync -a --exclude '.DS_Store' --exclude '._*' --exclude '__pycache__' \
  plugins/three-kingdoms-focus-studio/ \
  "$HOME/.minimax/plugins/three-kingdoms-focus-studio/"
```

必須保留實體目錄，不能用 symlink。同步後重啟 MiniMax Code，
再用 `skill` 工具載入完整名稱：

```text
three-kingdoms-focus-studio:audio-reactive-waveform
```

只有成功載入，且回傳的 `Location` 指向此次安裝的外掛，才算主機識別成功。
僅檔案存在或渲染器測試通過，不能代替這項驗證。

## 使用範例

> 用 audio-reactive-waveform，讓這首音樂帶動金色透明頻譜條。
> 輸出供 CapCut 疊加的 MOV，先做 20 秒給我確認。

可另外提供參考影片或截圖，調整顏色、條數、粗細、位置與動態速度。
支援上下鏡像或向上的直條；目前不支援圓環、連續曲線、光暈或粒子。

需要可執行本地命令的環境、Python 3.10+、NumPy、FFmpeg 與 ffprobe；
FFmpeg 必須包含 `prores_ks`。依賴放在專案虛擬環境，產出放在專案資料夾，
不修改外掛安裝目錄。若 MiniMax 執行環境無法執行 Python／FFmpeg，
應回報缺少的能力並交付本地命令，不能宣稱已產出影片。
完整步驟見 [本地設定](skills/audio-reactive-waveform/references/local-setup.md)。

## 交付與驗證

- 先做最多 20 秒樣片；確認外觀與剪輯軟體透明匯入後才做全曲。
- MOV 使用 ProRes 4444、保留 alpha、沒有音軌；原音樂另外對齊起點。
- 一併保存 style JSON；修訂使用新檔名，預設不覆蓋既有媒體。
- 一般 H.264 MP4 沒有透明度，不能代替 MOV 疊加素材。
- 渲染器不需 API key，也不會上傳音檔；主機模型與參考圖分析仍受產品隱私設定影響。

在 repository 根目錄，以已安裝依賴的 Python 執行測試：

```sh
python -m unittest discover \
  -s plugins/three-kingdoms-focus-studio/skills/audio-reactive-waveform/tests -v
```

測試使用合成音訊，涵蓋透明度、音樂驅動變化、鏡像／單向樣式、時間、
參數錯誤與不覆蓋既有檔案。媒體測試若被跳過，不能記作渲染驗證通過。
MiniMax 載入與 CapCut 匯入仍需在實際主機各自確認。
