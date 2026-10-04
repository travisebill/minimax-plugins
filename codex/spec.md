# MiniMax 外掛轉為 Codex 版本

日期：2026-10-05

使用者確認移植兩個外掛，保留為兩個獨立套件，交付 ZIP 並安裝到本機 Codex。

來源：[travisebill/minimax-plugins](https://github.com/travisebill/minimax-plugins)，固定 commit `0d74e7638bcb04bf589ed9b5e37e78efda3ec00c`。

| 外掛 | 上游版本 | Codex 版本 | 技能數 |
| --- | --- | --- | --- |
| learning-game-studio | 0.2.0 | 0.2.1 | 2 |
| three-kingdoms-focus-studio | 1.2.0 | 1.2.1 | 7 |

交付範圍：保留技能、參考資料、模板、圖示與音訊量測腳本；增加 Agent Plugins 1.0 manifest、Codex 相容 manifest、技能 UI metadata、套件內路由與本機 marketplace。

行為修正：音樂提示詞必須先審查再取得核准並生成；沿用既有核准範圍；技能以套件內檔案為優先；歷史供應商與 YouTube 資料在實際使用時查核最新官方來源。

驗收：9 個技能 frontmatter 與 UI metadata、manifest 與圖示、套件內連結、ZIP 內容、本機安裝與 Codex 技能列舉，以及量測腳本的無修改來源、拒絕覆寫與有效音訊量測。

本次不執行實際音樂、圖片、影片生成或 YouTube 上架。這些是外掛後續工作流程，需要當次任務的供應商能力與授權。
