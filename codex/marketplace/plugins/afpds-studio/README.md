# AFP 文件工作室 — Codex 版

版本：1.0.0（上游 1.0.0，2026-11-08 移植）

AFP / AFPDS（Advanced Function Presentation）文件開發工具箱：內建 AFPC 完整出版品語料庫（32 份文件、5,490 頁、11.7 MB 純文字），每個位元組值、結構識別碼與繪圖規則都能追回規格頁碼；並附一套自建的 MO:DCA 資料流 → PNG 渲染器，可直接解出 FOCA 字型、PTOCA 文字、GOCA 圖形與 IOCA 影像並合成頁面預覽。

## 技能

- `afpds-expert` — 規格知識層：IPDS 傳輸、MO:DCA 文件結構、OCA 內容架構（IOCA / GOCA / PTOCA / BCOCA）、FOCA 字型與編碼。附 12 MB AFPC 全文語料、語料搜尋器、98 個 MO:DCA 結構識別碼資料表與位元組結構驗證器。
- `afp-renderer` — 渲染層：把 MO:DCA 資料流的一頁渲染成 PNG，含 FOCA 字型光柵化、PTOCA 文字排版、GOCA 圖形與 IOCA 影像解碼。

## 使用

在 Codex 外掛介面選取「AFP 文件工作室」後，直接描述需求。技能可自然觸發；若環境有同名全域技能，從此外掛進入可確保使用移植版本。

本資料夾是單一 Agent Plugins 1.0 套件，另含 `.codex-plugin/plugin.json` 供 Codex 相容使用。本機 CLI 安裝請使用一併交付的完整 marketplace 包及其 `scripts/install_plugins.py`。

範例：「解析這份 .afp 檔，列出它的物件結構與對應的規格頁碼。」「把這個 AFP 的第 1 頁 render 成 PNG 給我看。」「這個 AFP 在印表機上印出來是空白的，幫我查結構有沒有問題。」

## 執行需求

- **Node.js**：`skills/afpds-expert/scripts/` 下的語料搜尋器、結構表與位元組驗證器都是零相依的 `.mjs`，不需安裝任何套件。
- **Python 3.11+** ＋ `Pillow` ＋ `numpy`：渲染器在 `skills/afp-renderer/scripts/afp_render/`。缺少相依套件時裝進使用者環境，不要改寫渲染器來避開它。
- **外部資源**：渲染一頁需要 FOCA 字型檔與 MO:DCA 外部資源檔（`*.res`）。沒有 `.res` 時頁面會有本文與自身圖形，但**沒有 overlay、沒有條碼** —— 這是「看起來只畫一半」最常見的原因，交付時要說清楚。

## 來源

移植自 [travisebill/minimax-plugins](https://github.com/travisebill/minimax-plugins)，commit `0d4a7cdfb5c086e42a30197efd84b354df80d95a`。檔案對照與 SHA-256 見 `UPSTREAM.json`。

該上游的原始來源是本機的 `AFPDS_Expert` 專案（無公開 remote，因此無法用 commit 追溯）；`skills/afpds-expert/corpus/` 是 AFP Consortium 公開出版品（32 份 PDF）的純文字萃取。**AFPC 出版品的再散布授權條款尚未確認** —— 本套件目前只供私人本機使用，若要公開散布需先確認條款。

本次移植相對 MiniMax 版的差異：兩份 manifest 換成 Codex 的可攜格式與相容格式、每支 skill 補上 `agents/openai.yaml` 介面描述、新增 `CODEX.md` 與本檔，兩支 SKILL.md 各加一行 runtime 引導（其餘內容逐位元相同）。
