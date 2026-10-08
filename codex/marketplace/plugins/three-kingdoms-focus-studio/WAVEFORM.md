# 透明音樂波形：原始碼整合

Codex 三國音樂工作室 1.3.0 新增 `audio-reactive-waveform`，音樂技能由 7 個增為 8 個。

## 從 repository 安裝

請讓本機 agent 使用已包含本次變更的 commit 或分支，讀取 repository 的 `codex/AGENTS.md`，安裝來源為：

`codex/marketplace/plugins/three-kingdoms-focus-studio/`

repository 根目錄的 marketplace 已指向這個來源目錄，無需另增 marketplace 或全域 skill。草稿 PR 尚未合併前，`main` 不含新技能；先明確選取包含變更的分支／commit，合併後才可直接從 `main` 安裝。請依本機實際支援的 Codex 插件安裝流程操作，不要直接修改安裝快取。

本次只更新原始碼。既有 README、UPSTREAM 移植紀錄、`codex/dist/` ZIP 與舊驗證報告保留原樣，可能仍顯示 1.2.1／7 個音樂技能；它們不代表本次版本。請勿用舊 ZIP 安裝新技能。需要 ZIP 時，可在取得最新原始碼後本機執行 `python3 codex/scripts/package_plugins.py` 重新打包。

安裝後，請確認插件版本為 1.3.0，技能清單包含 `three-kingdoms-focus-studio:audio-reactive-waveform`，並讀取其實際檔案位置。這份文件不表示已替你完成安裝或主機驗證。

## 使用

範例：「用這首音樂做透明金色波形，先給我 20 秒 MOV 樣片。」

- 輸出：帶真正 alpha 的靜音 ProRes 4444 MOV；原音樂另放對齊音軌。
- 支援：鏡像／單向直條、色彩、數量、位置、尺寸、振幅與平滑度。
- 依賴：Python、NumPy、FFmpeg 與 ffprobe；渲染不呼叫付費生成 API。
- 先核准樣片外觀與剪輯軟體的透明匯入，再渲染全曲。

依賴檢查與專案虛擬環境見 [本機設定](skills/audio-reactive-waveform/references/local-setup.md)。使用外掛內已核對的 skill 路徑，保持外掛目錄唯讀。

## 來源與驗證

來源、固定 commit、原始及整合後的 SHA-256 見 [波形來源紀錄](skills/audio-reactive-waveform/UPSTREAM.json)。保留來源資訊，不新增授權聲明；既有外掛的作者與授權紀錄未修改。

渲染器、樣式與 8 項合成音訊 CLI 測試原樣保留，僅設定指南配合外掛路徑與專案虛擬環境調整。打包測試核對單插件及完整包包含渲染器、依賴和樣式，維持 8 個音樂技能、2 個教學技能。重跑：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s codex/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s codex/marketplace/plugins/three-kingdoms-focus-studio/skills/audio-reactive-waveform/tests -v
```

本次在 Linux 雲端測試；尚未完成 Mac 渲染、1.3.0 插件安裝或 Codex 主機列舉。
