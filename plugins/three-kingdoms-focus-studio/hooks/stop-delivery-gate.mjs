// Stop — 交付前最後一道閘門：成片的影片軌與音軌必須等長，幀數必須對得上時間軸。
//
// 為什麼需要：這個工作流曾經交付過一支「影片軌比音軌短 3 幀」的母檔
// （111075 幀 = 3702.500 s，音軌與母帶都是 3702.600 s）。它不會壞掉、不會報錯，
// 音軌比對也會過（因為音軌本身是對的），只有「影片軌 vs 音軌」才看得出來 ——
// 而那正是造成波形疊加條相對音訊漸進漂移 100 ms 的原因。
//
// 這個閘門只做 0.14 秒就能完成的量測，不跑完整驗證（完整驗證要 10 分鐘，
// 遠超 Hook 的 15 秒事件預算）。
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { readHookInput, projectDir, probeStreams, emitBlock } from "./lib/hook-utils.mjs";

const input = readHookInput();

// 已經在續跑時不要再擋一次（否則會無限續跑）
if (input?.stop_hook_active) process.exit(0);

const proj = projectDir(input);
const releasesRoot = join(proj, "assets", "releases");
if (!existsSync(releasesRoot)) process.exit(0);

const problems = [];
let checked = 0;

for (const rel of readdirSync(releasesRoot, { withFileTypes: true })) {
  if (!rel.isDirectory() || rel.name.startsWith(".")) continue;
  const coverDir = join(releasesRoot, rel.name, "cover");
  if (!existsSync(coverDir)) continue;
  for (const f of readdirSync(coverDir, { withFileTypes: true })) {
    if (!f.isFile() || !f.name.toLowerCase().endsWith(".mp4")) continue;
    const file = join(coverDir, f.name);
    const s = probeStreams(file);
    if (!s) continue;             // 沒有 ffprobe 或讀不到 → fail open
    checked++;
    const where = `assets/releases/${rel.name}/cover/${f.name}`;

    // 影片軌與音軌必須等長
    if (s.audioDuration != null && Number.isFinite(s.audioDuration)) {
      const diff = Math.abs(s.videoDuration - s.audioDuration);
      if (diff > 0.05) {
        problems.push(
          `${where}：影片軌 ${s.videoDuration.toFixed(3)}s 與音軌 ${s.audioDuration.toFixed(3)}s ` +
          `相差 ${diff.toFixed(3)}s（> 0.05s）。重新合併時章節要以「幀號」切，` +
          `不是以秒數切，否則每章會各自 ±1 幀而累積偏移。`
        );
      }
    }
    // 幀數必須對得上時間軸
    if (s.fps > 0 && Number.isFinite(s.frames) && s.frames > 0) {
      const expect = Math.round(s.videoDuration * s.fps);
      if (Math.abs(expect - s.frames) > 1) {
        problems.push(
          `${where}：實際 ${s.frames} 幀，但 ${s.videoDuration.toFixed(3)}s × ${s.fps}fps ` +
          `應為 ${expect} 幀（差 ${s.frames - expect}）。`
        );
      }
    }
  }
}

if (problems.length) {
  emitBlock(
    `交付前檢查未通過（已檢查 ${checked} 支影片）：\n` +
    problems.map((p) => `- ${p}`).join("\n") +
    `\n請先修正再交付。`
  );
}
process.exit(0);
