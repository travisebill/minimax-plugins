# 教學遊戲工作室 — Codex 版

版本：0.2.1（上游 0.2.0，2026-10-05 移植）

Makes teaching interactions genuinely playable: selects a game mechanic that fits the learning objective, gives it readable feedback and game feel, aligns rewards with mastery, and blocks mechanics that would teach something wrong.

## 技能

- `learning-game-feel`
- `learning-mechanics`

## 使用

在 Codex 外掛介面選取「教學遊戲工作室」後，直接描述需求。技能可自然觸發；若環境有同名全域技能，從此外掛進入可確保使用移植版本。

本資料夾是單一 Agent Plugins 1.0 套件，另含 `.codex-plugin/plugin.json` 供 Codex 相容使用。本機 CLI 安裝請使用一併交付的完整 marketplace 包及其 `scripts/install_plugins.py`。

範例：「幫我為這章選擇適合學習目標的遊戲機制，並實作清楚的對錯回饋。」課程骨架與 3D 引擎的 companion skills 為可選能力，不影響本套件的機制與回饋設計。

## 來源

移植自 [travisebill/minimax-plugins](https://github.com/travisebill/minimax-plugins)，commit `0d74e7638bcb04bf589ed9b5e37e78efda3ec00c`。檔案對照與 SHA-256 見 `UPSTREAM.json`。保留上游作者與素材，未重新宣告授權；上游 README 記載部分素材授權仍待確認。本次為私人本機移植，未公開發布。
