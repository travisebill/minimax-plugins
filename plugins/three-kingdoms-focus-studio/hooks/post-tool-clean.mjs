// PostToolUse(bash) — 在會產生雜項的指令結束後，清掉側車檔與 Python 快取。
//
// 為什麼需要：跑過測試或 import 過 skill 內的腳本會留下 `__pycache__`，
// 而整包驗證（`codex/scripts/package_plugins.py`）掃的是**檔案系統**不是版控，
// 遇到 `__pycache__` 或 `._*` 會直接斷言失敗 —— 讓人誤以為外掛壞了。
//
// 只在「可能產生雜項」的指令後才掃：外接 exFAT 磁碟上全樹巡覽要 1 秒以上，
// 而 hook 的事件預算只有 15 秒，每個 bash 都掃會把它吃光。
//
// 純副作用事件：成功就靜默結束，不輸出任何東西。
import { readHookInput, workDir, gitRootsUnder, cleanArtifacts } from "./lib/hook-utils.mjs";

const input = readHookInput();
const command = String(input?.tool_input?.command || "");

// 會產生 __pycache__／側車檔／pack 索引的指令
const RELEVANT = /\b(python[0-9.]*|pytest|unittest|pip[0-9]*|npm|npx|node|yarn|git)\b/i;

const base = workDir(input);

// git 相關：先清 repo 裡的側車檔（git 壞掉時錯誤訊息不可讀）
if (/\bgit\b/.test(command)) {
  for (const root of gitRootsUnder(base, 5)) {
    cleanArtifacts(root, { budgetMs: 1200, maxFiles: 12000, skipGit: false });
  }
}

// 其他會產生快取的指令：掃工作目錄
if (RELEVANT.test(command)) {
  cleanArtifacts(base, { budgetMs: 1400, maxFiles: 12000, skipGit: false });
}

process.exit(0);
