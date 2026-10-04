# 移植驗證紀錄

日期：2026-10-05

結果：兩個外掛均已安裝、啟用，Codex runtime 已識別全部 9 個外掛技能。

| 驗證 | 結果與證據 |
| --- | --- |
| 可攜 manifest | 依 Agent Plugins 1.0 官方 JSON Schema 檢查，兩份通過；見 `portable-schema.json` |
| Codex manifest | `plugin/read` 成功讀取名稱、版本、圖示與技能；見 `host.json` |
| 技能格式 | 9 份 SKILL.md 均通過官方 `quick_validate.py` |
| 技能 UI | 檢查 frontmatter 名稱、說明長度與 default prompt；維持自然觸發 |
| 檔案完整性 | 套件內 Markdown 連結、圖示格式與尺寸、JSON 重複鍵、占位字、symlink 與雜檔檢查通過 |
| 原始碼保存 | 參考資料、模板、圖示、量測腳本與上游 hash 相同；變更記錄於 `UPSTREAM.json` |
| 音訊腳本 | 15 秒雙聲道測試訊號完成全檔解碼、响度與頻帶量測；來源 hash 不變；重複報告路徑遭拒絕，原報告未變；見 `audio-smoke.json` |
| 證據界線 | 音訊測試結果的 listening 與 continuity 仍為 `not-assessed` |
| 安裝 | CLI 回傳兩個外掛 `installed: true`、`enabled: true` |
| 主機列舉 | `skills/list` 回傳 9 個啟用技能，路徑均在 `travis-codex-studios` 的安裝快取中；見 `host.json` |
| 安裝內容 | 安裝快取與來源套件逐檔 SHA-256 一致；見 `installed-integrity.json` |
| ZIP | 每份個別 ZIP 只有一個外掛根目錄，包含隱藏的 Codex manifest；解壓 CRC 檢查通過。完整包另含 marketplace 與安裝程式 |

主機驗證使用已安裝的 Codex app-server metadata API，沒有模型生成請求。介面視覺呈現未做螢幕走查；安裝及技能載入已由 runtime 驗證。

本次未執行真實供應商生成、音檔聆聽、YouTube 上架或教學學習成效試驗；外掛仍保留原工作流程的各項實測與人工確認要求。上游 2026-09-30 研究未重新執行，其資料在工作流程內標示為歷史參考。
