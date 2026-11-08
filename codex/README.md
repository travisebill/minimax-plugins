# Codex 教學、音樂與 AFP 工作室

這是 [travisebill/minimax-plugins](https://github.com/travisebill/minimax-plugins) 的 Codex 移植版本，保留三個獨立外掛，共 12 個技能。

> **版本要分清兩件事**：本表列的是**原始碼版本**；已發布的 ZIP 仍是較早的版本（`dist/`），移植當時的規格與驗證紀錄保留在 `spec.md` 與 `validation/`。原始碼可以先跑，發布產物與主機驗證另排期 —— 見 `marketplace/plugins/three-kingdoms-focus-studio/WAVEFORM.md`。

最初的移植來源固定於 commit `0d74e7638bcb04bf589ed9b5e37e78efda3ec00c`，移植日期為 2026-10-05。`afpds-studio` 於 2026-11-08 加入，來源 commit `aca8d6a75cc9f15648f4530f0d11080a8b6ae638`。

| 外掛 | 版本 | 可以做什麼 |
| --- | --- | --- |
| 教學遊戲工作室 `learning-game-studio` | 0.2.1 | 學習目標與遊戲機制配對、互動實作、回饋動畫、進度獎勵、手機與無障礙驗收 |
| 三國音樂工作室 `three-kingdoms-focus-studio` | 1.7.1 | 音樂與影片企劃、純器樂提示詞、角色人聲單曲、候選審查、章節拼接、封面、整部上傳影片製作與 YouTube 文案 |
| AFP 文件工作室 `afpds-studio` | 1.0.0 | AFP / MO:DCA 規格知識（附 AFPC 全文語料與位元組驗證器）＋ MO:DCA 資料流 → PNG 頁面渲染器 |

## 安裝

需要支援 `codex plugin` 的 Codex CLI。解壓完整包 `dist/minimax-codex-plugins-bundle.zip` 到要長期保存的資料夾後，在該資料夾執行：

```sh
python3 scripts/install_plugins.py
```

這會透過 Codex 支援的 CLI 註冊 `travis-codex-studios` 本機 marketplace，並安裝、啟用三個外掛。來源路徑會被保存，請保留解壓後的資料夾。安裝程式不會直接修改既有全域技能；如果有同名技能，使用外掛名稱選取，外掛內部也會優先讀取自己的版本。

確認安裝結果：

```sh
codex plugin list --marketplace travis-codex-studios --json
```

在 Codex 的外掛介面搜尋「教學遊戲工作室」、「三國音樂工作室」或「AFP 文件工作室」，加入對話後描述工作即可。現有對話的技能清單可能保留起始快照；若沒有新外掛，先開新對話，必要時重新開啟 Codex。

兩份獨立 ZIP 各包含一個 Agent Plugins 1.0 套件及 Codex 相容 manifest，適合分開保存或後續私人匯入；在本機透過 CLI 安裝時，使用含 marketplace 的完整包。

## 開始使用

- 教學：「把這一章的互動改成有目標、有回饋、有進度的遊戲，先說明它如何幫助學習。」
- 回饋：「答對和答錯看起來一樣，幫我改善回饋並檢查 reduced motion 與手機操作。」
- 音樂：「規劃一支三國主題讀書音樂影片，先整理規格，再走提示詞審查與確認。」
- 審查：「檢查這批候選音檔的技術品質，清楚標示尚未有聆聽證據的部分。」
- 發布：「整理這支影片的 YouTube 標題與說明，查核最新官方政策。」
- AFP：「解析這份 .afp 檔，列出它的物件結構與對應的規格頁碼。」「把這個 AFP 的第 1 頁 render 成 PNG 給我看。」

三國音樂的整體入口是 `yt-focus-music-pipeline`；單一步驟可直接選擇對應技能。

## 需要的能力

一般企劃與教學修改使用 Codex 已有的檔案、終端機與瀏覽器工具。音訊技術檢查另需 Python 3.11 以上、`ffmpeg` 與 `ffprobe`。部分 MiniMax 提示詞流程要求已安裝的 `music-caption-rewriter`，外掛會先確認是否可用。

本套件沒有內建 MiniMax、Lyria 或 YouTube MCP 服務，也不包含 API 金鑰。生成與上架使用當次環境實際可用的工具和使用者授權；缺少能力時，交付可執行的交接資料。文字、技術量測、實際聆聽與人工核准分開記錄。

## 移植調整

- 增加根目錄 `plugin.json` 與 `.codex-plugin/plugin.json`，保留原圖示與教學外掛的深色圖示。
- 當初移植的 9 個技能補上 Codex UI metadata（`afpds-studio` 加入後共 12 個）；套件內的 `CODEX.md` 統一處理技能路由與執行能力。
- 把音樂流程改為「最終 payload 審查 → 核准 → 生成 → 候選審查」，沿用使用者已授權的確切版本、設定和候選數。
- 保存上游研究內容，明確標示其歷史日期；現行供應商限制與 YouTube 政策在使用時查核官方來源。
- 原樣保留參考資料、模板與音訊量測腳本。來源差異、每個檔案的 hash 見 `UPSTREAM.json`。

`afpds-studio`（2026-11-08 加入）的移植調整：

- 兩支 SKILL.md 各加一行 runtime 引導，其餘內容逐位元相同；每個檔案的 hash 見該套件自己的 `UPSTREAM.json`。
- 隨套件附帶 AFPC 出版品的全文語料（32 份文件 / 5,490 頁 / 12 MB）與 MO:DCA 結構表，讓技能離開來源專案也能運作。
- 執行需求：語料搜尋器與位元組驗證器只需 Node.js；渲染器需 Python 3.11 以上、Pillow 與 numpy。

## 驗證與更新

`validation/` 保存本次套件、schema、音訊腳本與主機識別的驗證結果。這些檢查不代表已生成音樂、影片或完成 YouTube 上架，也不替代學習者實測或音訊聆聽。

更新時修改 `marketplace/plugins/`，同步調整兩份 manifest 的版本，再重新驗證、打包與安裝；不要直接修改 Codex 安裝快取。

```sh
# 打包工具需要 PyYAML
python3 scripts/package_plugins.py
python3 scripts/install_plugins.py
```

上游未提供完整授權聲明，且其 README 記載部分素材授權尚待確認。本次保留來源與作者資訊，供個人本機使用；沒有新增 MIT 等未獲授權的宣告，也沒有公開發布。
