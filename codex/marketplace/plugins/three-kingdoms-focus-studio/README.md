# 三國音樂工作室 — Codex 版

版本：1.5.0（原始碼版本；2026-10-05 移植自上游 1.2.0，已發布 ZIP 仍為 1.2.1）

三國主題音樂的企劃、純器樂提示詞、角色人聲單曲、候選審查、章節拼接、封面與 YouTube 發布策略。保存人工核准與來源紀錄；內附上游 2026-09-30 的歷史研究資料，實際使用前查核最新政策。

## 技能

- `music3-instrumental-prompts`
- `three-kingdoms-focus-music`
- `three-kingdoms-music-review`
- `three-kingdoms-video-project`
- `three-kingdoms-vocal-single`
- `yt-focus-music-pipeline`
- `yt-publish-strategy`

## 使用

在 Codex 外掛介面選取「三國音樂工作室」後，直接描述需求。技能可自然觸發；若環境有同名全域技能，從此外掛進入可確保使用移植版本。

本資料夾是單一 Agent Plugins 1.0 套件，另含 `.codex-plugin/plugin.json` 供 Codex 相容使用。本機 CLI 安裝請使用一併交付的完整 marketplace 包及其 `scripts/install_plugins.py`。

整體流程入口為 `yt-focus-music-pipeline`。範例：「規劃一支三國主題讀書音樂影片，先整理規格，再完成提示詞審查。」

技術量測需要 Python 3.11 以上、ffmpeg 與 ffprobe；部分 MiniMax 提示詞流程另需已安裝的 `music-caption-rewriter`。本外掛提供工作流程與量測脚本；音樂、圖片、影片生成及發布，使用 Codex 當次可用工具與經授權的服務。

## 來源

移植自 [travisebill/minimax-plugins](https://github.com/travisebill/minimax-plugins)，commit `0d74e7638bcb04bf589ed9b5e37e78efda3ec00c`。檔案對照與 SHA-256 見 `UPSTREAM.json`。保留上游作者與素材，未重新宣告授權；上游 README 記載部分素材授權仍待確認。本次為私人本機移植，未公開發布。
