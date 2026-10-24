// SessionStart — 開工前檢查這個工作流稍後會撞到的環境問題。
//
// 為什麼需要：這個工作流的 A/V 驗證需要「疊加層母檔」（ProRes 4444，約 13 GB）。
// 它不在發布包裡，只存在本機；一旦被清掉，最後一項驗證會直接失敗，
// 而且失敗訊息不會告訴你缺的是什麼。這裡先把缺口講清楚。
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import os from "node:os";
import { readHookInput, projectDir, emit } from "./lib/hook-utils.mjs";

const input = readHookInput();
const proj = projectDir(input);
const notes = [];

// 1) 波形疊加條母檔：目錄存在但母檔不見 → A/V 驗證會失敗
const waveRoot = join(os.homedir(), "Movies", "Waveform Output");
if (existsSync(waveRoot)) {
  const missing = [];
  for (const name of readdirSync(waveRoot, { withFileTypes: true })) {
    if (!name.isDirectory() || name.name.startsWith(".")) continue;
    if (!existsSync(join(waveRoot, name.name, "waveform-full.mov"))) missing.push(name.name);
  }
  if (missing.length) {
    notes.push(
      `波形疊加條母檔缺失：${missing.join("、")}。` +
      `最終驗證第 6 項（端到端 A/V 同步）需要帶 alpha 的 waveform-full.mov；` +
      `請用 audio-reactive-waveform 的 render_waveform.py 從母帶 WAV 與 style.json 重產後再跑驗證。`
    );
  }
}

// 2) 本專案是否已有發布包（有 → 提醒交付前會跑時長守門）
const releasesRoot = join(proj, "assets", "releases");
if (existsSync(releasesRoot)) {
  const releases = readdirSync(releasesRoot, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith("."))
    .map((d) => d.name);
  if (releases.length) {
    notes.push(
      `這個工作目錄已有發布包：${releases.join("、")}。` +
      `交付前會自動檢查成片的影片軌／音軌時長是否一致、幀數是否等於 round(時長×30)。`
    );
  }
}

emit("SessionStart", notes.length ? notes.join("\n") : "");
