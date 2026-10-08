# 本地安裝與執行（macOS 優先）

## 從外掛使用

此 skill 隨「三國音樂工作室」Codex 外掛提供。先依 [波形原始碼安裝說明](../../../WAVEFORM.md) 選取包含此技能的分支或 commit，再安裝或更新外掛；不要使用舊 ZIP，
在新對話確認 `three-kingdoms-focus-studio:audio-reactive-waveform` 可用。
使用已安裝外掛中的這份 skill；不必另外複製到全域 skills 目錄。

從主機實際回報的 skill 位置確認其目錄，將下列 `SKILL_DIR` 換成該完整路徑。
它應包含 `SKILL.md`、`scripts/render_waveform.py` 與 `requirements.txt`。
若無法取得安裝位置，先讀取主機技能清單或請使用者提供，不猜測安裝快取路徑。
原始碼驗證時可使用本插件目錄下的 `skills/audio-reactive-waveform`。

「使用這個外掛的 audio-reactive-waveform，參考這段影片的樣式，讓這首音樂帶動波形。
先做 20 秒透明 MOV 給我確認。」

依賴與產出放在專案工作區，保持外掛目錄唯讀。以下依賴安裝依當次授權執行，
skill 不會自動安裝軟體，也不會修改 Codex 快取或建立另一份全域 skill。

## 依賴與虛擬環境

需要 Python 3.10+、NumPy、FFmpeg 和 ffprobe。FFmpeg 要包含 `prores_ks` encoder。
不需要 Pillow、付費 API、登入或任何雲端渲染服務。安裝依賴可能會連網下載套件；
渲染腳本本身只接受本地檔案，沒有上傳、遙測或網路請求。
Codex 本身的模型服務與參考圖像分析則仍受你使用的產品及隱私設定影響，
不代表整個 Codex 都離線。

先確認：

```sh
python3 --version
ffmpeg -version
ffprobe -version
ffmpeg -hide_banner -encoders | grep prores_ks
```

缺少 Python 時，使用 [Python 官方 macOS 下載](https://www.python.org/downloads/macos/)。
缺少 FFmpeg 時，參考 [FFmpeg 官方下載頁](https://ffmpeg.org/download.html)。
此 skill 不會替你安裝 Homebrew 或執行遠端安裝腳本。

```sh
SKILL_DIR="/verified/plugin/path/skills/audio-reactive-waveform"
PROJECT_DIR="$HOME/Movies/Waveform Output"
mkdir -p "$PROJECT_DIR"
test ! -e "$PROJECT_DIR/.venv" && python3 -m venv "$PROJECT_DIR/.venv"
source "$PROJECT_DIR/.venv/bin/activate"
python -m pip install -r "$SKILL_DIR/requirements.txt"
python "$SKILL_DIR/scripts/render_waveform.py" --help
```

若虛擬環境建立或 NumPy 安裝失敗，先處理錯誤，不要使用 sudo pip。
每次開新終端機重新確認 `SKILL_DIR` 並啟用同一個專案虛擬環境。
若 `.venv` 已存在，確認它屬於此專案後再使用；不要重建或覆蓋不明環境。

## 先做 20 秒，再做整首

將範例路徑改成自己的檔案；保留雙引號以支援中文與空白路徑。
輸出資料夾必須存在。先將預設樣式複製至專案以保留本次設定：

```sh
mkdir -p "$HOME/Movies/Waveform Output"
test ! -e "$HOME/Movies/Waveform Output/style.json" && cp "$SKILL_DIR/assets/gold-mirrored.json" "$HOME/Movies/Waveform Output/style.json"
python "$SKILL_DIR/scripts/render_waveform.py" --input "$HOME/Music/my song.mp3" --output "$HOME/Movies/Waveform Output/sample.mov" --style "$HOME/Movies/Waveform Output/style.json" --duration 20
```

確認外觀、透明度與剪輯軟體匯入後，移除 `--duration` 做整首：

```sh
python "$SKILL_DIR/scripts/render_waveform.py" --input "$HOME/Music/my song.mp3" --output "$HOME/Movies/Waveform Output/full.mov" --style "$HOME/Movies/Waveform Output/style.json"
```

在 CapCut 將 MOV 放在影片上層，原音樂另放音軌並對齊起點。MOV **沒有聲音**。
不需去背或色度鍵。一般 H.264 MP4 不保留這份透明輸出，不能作為替代檔。

腳本預設拒絕覆蓋；需要重做時換檔名，或明確加入 `--overwrite`。
Ctrl+C 會中止並清掉這次的暫存目錄。ProRes 檔案通常比 MP4 大很多；
先用短片估計磁碟空間與速度，不保證特定機型的耗時。直接串流影格，
不會產生數千張 PNG，但分析音訊會使用記憶體，長音檔要預留資源。
最後一格會補足，MOV 可能比音訊長不到一格。20 秒與整首的音量正規化
分別計算，因此正式輸出的振幅可能略有差異。

## 驗證與相容性

```sh
python -m unittest discover -s "$SKILL_DIR/tests" -v
ffprobe -v error -show_streams -of json "$HOME/Movies/Waveform Output/sample.mov"
```

輸出應只有一個 ProRes 4444 影片串流，pixel format 包含 alpha (`yuva...`)，
沒有音軌。測試使用自行合成的音訊，還會實際解碼透明度、检查鏡像和單向樣式。
本版在 Linux 雲端測試；尚未在你的 Mac/Windows 執行。CapCut 各版本的匯入行為
請以短片實測為準。

Windows：使用本機 Python 3.10+ 與包含 ffprobe 的 FFmpeg，加入 PATH；以
`py -3 -m venv .venv` 建立環境，直接使用 `.venv\Scripts\python.exe` 執行
pip 與腳本可避免變更 PowerShell 執行政策。其餘參數相同，路徑改為 Windows
格式。請輸出到支援 hard link 的本機磁碟（通常為 NTFS）；macOS 建議本機 APFS。
不支援 hard link 的網路/FAT 磁碟可能無法完成無覆蓋式輸出，換本機資料夾即可。
