// 共用工具：讀取 hook 輸入、路徑解析、有界限的側車檔清理、ffprobe 探測。
// Plugin Hook 的環境變數：
//   PLUGIN_ROOT / MINIMAX_PLUGIN_ROOT — 外掛套件根目錄（唯讀）
//   MINIMAX_PROJECT_DIR              — 目前回合的工作目錄
//   PLUGIN_DATA                       — 這個外掛自己的可寫入狀態目錄
import { readFileSync, existsSync, readdirSync, unlinkSync, rmSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";

/** 讀 stdin 的 hook 輸入 JSON；壞了也要能繼續。 */
export function readHookInput() {
  try {
    const raw = readFileSync(0, "utf8");
    if (!raw || !raw.trim()) return {};
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

/** 回合的實際工作目錄：指令的 cwd 優先，其次環境變數。 */
export function workDir(input) {
  const cwd = input?.cwd;
  if (cwd && existsSync(cwd)) return resolve(cwd);
  const env = process.env.MINIMAX_PROJECT_DIR;
  if (env && existsSync(env)) return resolve(env);
  return resolve(process.cwd());
}

/** 專案根：環境變數優先，其次由工作目錄往上找。 */
export function projectDir(input) {
  const env = process.env.MINIMAX_PROJECT_DIR;
  if (env && existsSync(env)) return resolve(env);
  const start = workDir(input);
  let dir = start;
  for (let i = 0; i < 12; i++) {
    if (existsSync(join(dir, ".git")) || existsSync(join(dir, ".minimax"))) return dir;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return start;
}

/** 找出工作目錄「底下」的 git 儲存庫根（含工作目錄本身與其子目錄）。 */
export function gitRootsUnder(base, maxDepth = 5) {
  const roots = new Set();
  const queue = [[base, 0]];
  while (queue.length) {
    const [dir, depth] = queue.shift();
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const e of entries) {
      if (!e.isDirectory()) continue;
      if (e.name === "node_modules") continue;
      if (e.name === ".git") {
        // 找到 .git → 它的上一層就是 repo 根；不要往下走進 .git 裡面。
        roots.add(dir);
        continue;
      }
      if (depth >= maxDepth) continue;
      queue.push([join(dir, e.name), depth + 1]);
    }
  }
  return [...roots];
}

const SIDECAR = "._";
const CACHE = "__pycache__";

/** 只清一層目錄裡的側車檔與快取。 */
function cleanLeaf(dir) {
  let removed = 0;
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return removed;
  }
  for (const e of entries) {
    const full = join(dir, e.name);
    if (e.isDirectory()) {
      if (e.name === CACHE) {
        try { rmSync(full, { recursive: true, force: true }); removed++; } catch { /* 忽略 */ }
      }
    } else if (e.name.startsWith(SIDECAR)) {
      try { unlinkSync(full); removed++; } catch { /* 忽略 */ }
    }
  }
  return removed;
}

/**
 * 有界限地清除 AppleDouble 側車檔與 Python 快取。
 *
 * 迴圈外磁碟（exFAT／外接）上 macOS 會替每個檔案生成 `._檔名`，
 * 這些側車檔會讓 git 讀錯 pack index、讓整包驗證腳本斷言失敗。
 *
 * 以**廣度優先**巡覽：淺層先清，預算用完時已處理的是最常見的檔案位置。
 * `.git` 只清「自己那一層」與 `objects/pack` —— `.git/objects` 有海量檔案，
 * 遞迴進去會把預算吃光。
 * 回傳清除數量。
 */
export function cleanArtifacts(root, { budgetMs = 2000, maxFiles = 20000, skipGit = false } = {}) {
  const deadline = Date.now() + budgetMs;
  let removed = 0;
  let visited = 0;
  // 佇列元素一律是 [路徑]；若放字串再解構，`dir` 會變成路徑的第一個字元，
  // 整個巡覽會從「/」開始跑。
  const queue = [[root]];

  while (queue.length) {
    if (Date.now() > deadline || visited > maxFiles) break;
    const [dir] = queue.shift();
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const e of entries) {
      if (visited > maxFiles || Date.now() > deadline) break;
      visited++;
      const full = join(dir, e.name);
      if (e.name.startsWith(SIDECAR)) {
        // exFAT 會替「目錄」也生成 `._目錄名` 側車檔，一樣要刪掉
        try { rmSync(full, { recursive: true, force: true }); removed++; } catch { /* 忽略 */ }
        continue;
      }
      if (e.isDirectory()) {
        if (e.name === CACHE) {
          try { rmSync(full, { recursive: true, force: true }); removed++; } catch { /* 忽略 */ }
          continue;
        }
        if (e.name === ".git") {
          if (skipGit) continue;
          removed += cleanLeaf(join(full, "objects", "pack"));
          removed += cleanLeaf(full);
          continue;
        }
        if (e.name === "node_modules") continue;
        queue.push([full]);
      } else if (e.name.startsWith(SIDECAR)) {
        try { unlinkSync(full); removed++; } catch { /* 忽略 */ }
      }
    }
  }
  return { removed, visited };
}

/** 探測某個 mp4 的影片／音軌時長、幀數與影格率。找不到 ffprobe 就回 null（fail open）。 */
export function probeStreams(file) {
  const bin = process.platform === "win32" ? "ffprobe.exe" : "ffprobe";
  let r;
  try {
    r = spawnSync(bin, ["-v", "error", "-show_entries",
      "stream=codec_type,duration,nb_frames,r_frame_rate", "-of", "json", file],
      { encoding: "utf8", timeout: 4000, maxBuffer: 4 * 1024 * 1024 });
  } catch {
    return null;
  }
  if (!r || r.status !== 0 || !r.stdout) return null;
  try {
    const data = JSON.parse(r.stdout);
    const streams = data.streams || [];
    const video = streams.find((s) => s.codec_type === "video");
    const audio = streams.find((s) => s.codec_type === "audio");
    if (!video) return null;
    let fps = 0;
    const rate = String(video.r_frame_rate || "");
    if (rate.includes("/")) {
      const [n, d] = rate.split("/").map(Number);
      if (d) fps = n / d;
    }
    return {
      videoDuration: Number(video.duration),
      audioDuration: audio ? Number(audio.duration) : null,
      frames: Number(video.nb_frames),
      fps,
    };
  } catch {
    return null;
  }
}

/** 輸出 hookSpecificOutput；content 為空時靜默結束。 */
export function emit(event, content) {
  if (!content) return;
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext: content,
    },
  }));
}

/** Stop 事件的阻擋輸出。 */
export function emitBlock(reason) {
  process.stdout.write(JSON.stringify({ decision: "block", reason }));
}
