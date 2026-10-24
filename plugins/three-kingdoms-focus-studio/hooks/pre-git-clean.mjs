// PreToolUse(bash) — 偵測到 git 指令就先清側車檔，再讓命令跑。
//
// 為什麼需要：外接／exFAT 磁碟上，macOS 會替每個檔案生成 `._檔名` 側車檔。
// 連 `.git/objects/pack/` 裡的側車檔都會被 git 當成 pack index 讀，於是
// 每個 git 指令都噴 `non-monotonic index ...`，錯誤訊息完全不可讀 ——
// 代理會誤以為是 git 壞掉或自己改壞了 repo。事前清理比事後收拾有效得多。
//
// 找不到 git 指令就靜默結束（exit 0、不輸出）。
import { readHookInput, workDir, gitRootsUnder, cleanArtifacts } from "./lib/hook-utils.mjs";

const input = readHookInput();
const command = String(input?.tool_input?.command || "");
if (!/\bgit\b/.test(command)) process.exit(0);

const base = workDir(input);
const roots = gitRootsUnder(base, 5);
const targets = roots.length ? roots : [base];

for (const root of targets) {
  cleanArtifacts(root, { budgetMs: 1200, maxFiles: 12000, skipGit: false });
}
process.exit(0);
