# minimax-plugins

存放 **MiniMax Code 本機外掛（local Plugin V1）** 與 **Codex 外掛** 的版控來源。MiniMax 版本位於 `plugins/`，Codex 版本位於 `codex/marketplace/plugins/`。

## Codex 版本

| 外掛 | 版本 | 技能數 | 說明 |
| --- | --- | --- | --- |
| `learning-game-studio` | 0.2.1 | 2 | 教學遊戲機制與互動回饋 |
| `three-kingdoms-focus-studio` | 1.7.0 | 8 | 三國音樂企劃、影片製作、提示詞、審查與 YouTube 發布 |

> 本表列的是**原始碼版本**。Codex 的已發布 ZIP 仍是 1.2.1（`codex/dist/`）——
> 發布產物與主機驗證紀錄另排期，理由見 `codex/validation/verification.md`；
> 原始碼更新不需要等發布，兩者的差異是刻意的。

使用支援 `codex plugin` 的 Codex CLI，並先完成此私人 repo 的 GitHub 存取設定：

```sh
codex plugin marketplace add travisebill/minimax-plugins
codex plugin add learning-game-studio@travis-codex-studios
codex plugin add three-kingdoms-focus-studio@travis-codex-studios
```

[Codex 使用與維護說明](codex/README.md) · [完整安裝 ZIP](codex/dist/minimax-codex-plugins-bundle.zip) · [驗證紀錄](codex/validation/verification.md)

根目錄 `.agents/plugins/marketplace.json` 是 GitHub 安裝入口；`codex/marketplace/.agents/plugins/marketplace.json` 供解壓或本機來源安裝。以下 MiniMax 安裝指令適用於原本的 `plugins/` 版本。

## 目錄結構

```
plugins/
  learning-game-studio/                # 教學網站遊戲化外掛 v0.2.0
    .minimax-plugin/plugin.json        # manifest（skills 清單在這裡）
    icon.png  icon-dark.png
    skills/
      learning-mechanics/              # 選機制 / 機制安全性 / 驗收
        SKILL.md
        references/mechanic-catalog.md
      learning-game-feel/              # 回饋層 / game feel
        SKILL.md
        references/feedback-recipes.md
  three-kingdoms-focus-studio/         # 三國志 YouTube 音樂發布外掛 v1.7.0
    .minimax-plugin/plugin.json
    icon.png                           # 單一圖示（無 darkIcon）
    skills/
      yt-focus-music-pipeline/         # 協調層：分流 / 閘門 / 交接契約（單一入口）
        SKILL.md
        references/design-mcp-execution.md  # minimax-design MCP 執行層與實測坑位
      three-kingdoms-focus-music/      # 發布類型 / 長時混音 / 封面 / 循環影片 / QC
        SKILL.md  SKILL.cn.md  meta.yaml
      three-kingdoms-video-project/    # 角色專案包 / 規格閘門 / 章節拼接 / 兩階段封面 / 整部影片製作
        SKILL.md
        scripts/verify_loop_seam.py       # 循環片接縫與場景穩定性量測
      music3-instrumental-prompts/     # 純器樂 Music 3.0 Structured Caption
        SKILL.md
        references/  templates/        # 4 份 references + 6 份模板
      three-kingdoms-music-review/     # 審查 QA（prompt / 技術 / 聆聽 / 銜接）
        SKILL.md
        references/  scripts/measure_audio.py
                   scripts/detect_vocal_bands.py
                   scripts/locate_level_jumps.py
      three-kingdoms-vocal-single/     # 角色人聲單曲 / 歌詞 / 分鏡 / Short
        SKILL.md
      audio-reactive-waveform/        # 音樂驅動透明頻譜條 MOV / 樣式 / CLI 測試
        SKILL.md  requirements.txt
        references/  assets/  scripts/  tests/   # 含 output-variants.md / make_variants.py
      yt-publish-strategy/             # YouTube 發布策略 / 關鍵字 / 標記 / AI 揭露 / YPP 變現合規
        SKILL.md
        references/  templates/        # 3 份 references + 1 份模板

hooks/                             # Plugin Hook：自動守門（SessionStart / PreToolUse / PostToolUse / Stop）
  hooks.json
  session-start.mjs  pre-git-clean.mjs  post-tool-clean.mjs  stop-delivery-gate.mjs
  lib/hook-utils.mjs

tools/                                  # repo 開發工具（不進外掛 package）
  validate_plugin.py                    # 靜態驗證外掛結構
  sync_codex_variant.py                 # MiniMax 版 → Codex 版同步（保留 Codex 差異）
  refresh_upstream_hashes.py            # 重算 UPSTREAM.json 的檔案雜湊
```

## 目前外掛

| 外掛 | 版本 | Skill | 用途 |
|---|---|---|---|
| `learning-game-studio` | 0.2.0 | `learning-mechanics` | 選適合學習目標的遊戲機制、擋掉會教錯的機制、驗收四訊號 |
| | | `learning-game-feel` | 回饋層：讓因果關係看得見、獎勵不阻斷、手機優先 |
| `three-kingdoms-focus-studio` | 1.7.0 | `yt-focus-music-pipeline` | **單一入口**：分流三條路徑、擋住人工確認閘門、定義 skill 間交接契約；內建 minimax-design MCP 執行層 |
| | | `three-kingdoms-focus-music` | 發布類型分類、長時混音結構、封面、15 秒循環影片、發布包、QC |
| | | `three-kingdoms-video-project` | 角色專案包、規格閘門 `確認規格`、master prompt、候選審查、章節音訊拼接、兩階段封面、**整部上傳影片製作**（背景循環片＋波形疊加＋章節名／書法標題、分章合成與幀級驗證）|
| | | `music3-instrumental-prompts` | 純器樂 Music 3.0 Structured Caption（6 份模板 + 4 份 references）|
| | | `three-kingdoms-music-review` | 審查 QA：prompt / 技術 / 聆聽 / 銜接四層，附 `measure_audio.py`、`detect_vocal_bands.py`、`locate_level_jumps.py` |
| | | `three-kingdoms-vocal-single` | 角色人聲單曲：歌詞、發音與韻律鎖、分鏡圖、YouTube Short 分支 |
| | | `yt-publish-strategy` | YouTube 發布策略：標題關鍵字選詞、說明結構、hashtag、**標記 (Tags)**、AI 生成揭露義務、YPP 變現合規（附 2026-09-30 實測基準）|
| | | `audio-reactive-waveform` | 本地音樂驅動透明頻譜條，輸出無聲 ProRes 4444 MOV 供 CapCut 疊加；附樣式變體產生器 |

[MiniMax waveform 安裝與使用](plugins/three-kingdoms-focus-studio/WAVEFORM.md)（Python 3.10+、NumPy、FFmpeg／ffprobe；先確認 20 秒短片再做全曲）。

載入方式（**名稱必須帶外掛前綴**）：

```
learning-game-studio:learning-mechanics
learning-game-studio:learning-game-feel

three-kingdoms-focus-studio:yt-focus-music-pipeline
three-kingdoms-focus-studio:three-kingdoms-focus-music
three-kingdoms-focus-studio:three-kingdoms-video-project
three-kingdoms-focus-studio:music3-instrumental-prompts
three-kingdoms-focus-studio:three-kingdoms-music-review
three-kingdoms-focus-studio:three-kingdoms-vocal-single
three-kingdoms-focus-studio:yt-publish-strategy
three-kingdoms-focus-studio:audio-reactive-waveform
```

## Plugin Hook — 自動守門

`three-kingdoms-focus-studio` 自帶四個 Hook（`hooks/hooks.json`），把「靠代理記得做」
的事變成機械性檢查。**Plugin Hook 隨外掛載入，不需要去 Settings 開關**
（那是專案 Hook 才有的限制）；但外掛更新後要**重啟 MiniMax Code** 才會被重新載入。

| 事件 | 觸發 | 做什麼 | 為什麼 |
|---|---|---|---|
| `SessionStart` | 回合開始 | 檢查波形疊加條母檔是否還在（缺 → 提醒 A/V 驗證會失敗並附重生指令）、列出本工作目錄已有的發布包 | 母檔只存在本機、不在發布包裡，刪掉時最後一項驗證會直接失敗且不說原因 |
| `PreToolUse` (`bash`) | 指令含 `git` | **先清側車檔再讓命令跑** | exFAT 上 macOS 替每個檔案生成 `._檔名`，連 `.git/objects/pack/` 裡的都被 git 當 pack index 讀 → 每個指令都噴 `non-monotonic index`，錯誤訊息不可讀 |
| `PostToolUse` (`bash`) | 指令含 python／pytest／npm／node／git | 清掉 `__pycache__` 與側車檔（工作目錄 ＋ 外掛套件目錄） | 整包驗證掃的是**檔案系統**不是版控，遇到這些直接斷言失敗 |
| `Stop` | 代理準備結束 | **交付前守門**：ffprobe 比對成片影片軌／音軌時長（差 > 0.05 s 就擋）、幀數 == round(時長 × fps) | 「影片軌比音軌短幾幀」不會報錯、音軌比對也會過，只有兩軌互相比才看得出來 |

**Hook 的硬限制**：每個事件的**所有** handler 共享 **15 秒**（`SessionEnd` 只有 3 秒），
單一 handler 的 `timeout` 是 1–10 秒。所以 Hook 裡**只能做 0.05～0.5 秒的快速量測** ——
完整的最終驗證（約 10 分鐘）**不能**放進 Hook，仍然要代理顯式呼叫
`verify_final_video.py`。

**Hook 的驗證**：`tools/validate_plugin.py` 會檢查 hooks 檔案存在、欄位合規
（type/command/name≤64/timeout 1–10/matcher≤256）、`${PLUGIN_ROOT}` 引用路徑存在、
以及**每個 `.mjs` 都跑 `node --check`**。`node --check` 只解析語法，抓不到
`import { os } from "node:os"` 這種錯誤（要執行時才炸），而 Hook 腳本是在
使用者每個回合都會跑的 —— 一個壞掉的 import 會燒掉整個事件預算。

> `node --check` 只驗證語法，**不代表 hook 會被 runtime 執行**；
> 載入後仍要用代表性 JSON 餵 stdin 實跑一次確認。

## 重要：本機安裝處是「複製」，不是 symlink

MiniMax Code 的外掛必須在 `<activeDataDir>/plugins/<name>/`（`activeDataDir` 通常是 `~/.minimax`，舊 profile 可能是 `~/.mavis`）。**runtime 會拒絕 symlink 的外掛目錄**，所以本 repo 與本機安裝處是兩份實體檔案，需要同步。

### 安裝 / 更新到本機

```bash
rsync -a --exclude '.DS_Store' --exclude '._*' \
  plugins/learning-game-studio/ ~/.minimax/plugins/learning-game-studio/
```

然後**重啟 MiniMax Code**。實測結論（2026-09-26，別再重踩）：

- 新增外掛、或**既有外掛新增 skill** 之後，skill catalog 不一定會自己更新
- 實測：新增 skill 後等 8 分鐘仍載不到；**重啟 app 後立刻可載**
- 驗證方式：用 `skill` 工具載入 `<plugin-name>:<skill-name>`。若只給裸 skill 名會得到 `Local skill not found` —— 那個訊息代表**名稱形式錯**，不代表「沒收錄」，兩者要分開判斷
- 診斷法：同一外掛的舊 skill 載得到、新 skill 載不到 = 就是 catalog 列舉延遲，不用去改 manifest

### 從本機回寫到 repo

如果你用 `plugin-creator` 直接改本機那份，記得同步回來並 bump 版本：

```bash
rsync -a --delete --exclude '.DS_Store' --exclude '._*' \
  ~/.minimax/plugins/learning-game-studio/ plugins/learning-game-studio/
```

## 新增外掛的流程

1. 用 `plugin-creator` skill 把外掛建在 `<activeDataDir>/plugins/<new-name>/`
2. 複製進本 repo：`plugins/<new-name>/`
3. 在 README 的表格補一列、commit

## 注意事項

- **不要在 Finder 裡瀏覽外掛目錄** —— 會生成 `.DS_Store` 混進 package（已列入 `.gitignore`，但仍建議用編輯器開啟）
- 外掛路徑規則：相對路徑、`/` 分隔、每段符合 `^[A-Za-z0-9._-]+$`、不得有 symlink、不得用 Windows 保留名（`CON`/`NUL`/`COM1`…）
- 每個 skill 的 frontmatter `name` 必須等於它的目錄名
- manifest 的 `apps` 必須是 `[]`（本機外掛的 App capability 無效）

## Provenance

`learning-game-studio` 為**原創撰寫**（兩支 SKILL.md 與兩份 reference 都是自寫內容）。設計時參考了 OpenAI 的 `game-studio` 外掛（MIT，MiniMax 官方打包）的**分層思路與品質標準**，但**未複製其任何檔案**。若未來要公開散布、且內容開始包含上游素材，需補上 MIT 授權聲明與來源標註（repo + commit）。

### `three-kingdoms-focus-studio`

這個外掛是**整合包**，內含兩種來源不同的內容：

- **`yt-focus-music-pipeline`（1 支）＝本次新撰寫。** 依據另外 5 支 skill 的實際內容撰寫協調層（分流、閘門、交接契約），未複製它們的流程細節。撰寫後交由獨立 verifier 逐項比對來源，修正 1 個 Critical 供應商契約錯誤與 5 個較小缺陷後定稿。
- **另外 5 支＝自既有本機 skill 原樣搬入**，來源為：
  - `three-kingdoms-video-project`、`music3-instrumental-prompts`、`three-kingdoms-focus-music`、`three-kingdoms-vocal-single` ← `~/.agents/skills/`
  - `three-kingdoms-music-review` ← `~/.codex/skills/`

**最初搬入時**做的唯一改動是移除 2 個 Codex 專用介面檔 `agents/openai.yaml`（Codex UI 描述檔，MiniMax plugin 不使用）。
自 v1.4.0 起本 repo 開始自行維護這幾支 skill（實測修正錯譯、補 MCP 執行層與整部影片製作章節），
**不再與來源保持位元組一致**；每次變更的逐條依據見各 skill 的 SKILL.md 與 git 歷史。
`audio-reactive-waveform` 則相反：它是從本 repo 的 Codex 版移植回 MiniMax 版的。

其中 `music3-instrumental-prompts` 自述為 MiniMax 官方 `music-caption-rewriter` skill 的**純器樂特化分支**（該 skill 另存於 `~/.agents/skills/music-caption-rewriter/`）。若本 repo 日後要公開散布，這一支需補上上游的來源標註與授權聲明。

⚠️ 這 5 支的原作者與授權狀態尚未確認。**發布前需先確認**再對外散布。

### `audio-reactive-waveform` 移植

MiniMax v1.3.0 從本 repo 的 Codex 版移植此技能（v1.5.0 起同步兩側的樣式變體說明）；保留原始渲染程式、測試、
樣式與參考文件，改寫安裝說明並省略 MiniMax 不使用的 `agents/openai.yaml`。
確切來源 commit、原始來源鏈與檔案雜湊見
[UPSTREAM.json](plugins/three-kingdoms-focus-studio/skills/audio-reactive-waveform/UPSTREAM.json)。
