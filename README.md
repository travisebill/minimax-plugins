# minimax-plugins

存放 **MiniMax Code 本機外掛（local Plugin V1）** 的版控來源。未來新增的外掛都放這裡的 `plugins/` 底下。

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
```

## 目前外掛

| 外掛 | 版本 | Skill | 用途 |
|---|---|---|---|
| `learning-game-studio` | 0.2.0 | `learning-mechanics` | 選適合學習目標的遊戲機制、擋掉會教錯的機制、驗收四訊號 |
| | | `learning-game-feel` | 回饋層：讓因果關係看得見、獎勵不阻斷、手機優先 |

載入方式（**名稱必須帶外掛前綴**）：

```
learning-game-studio:learning-mechanics
learning-game-studio:learning-game-feel
```

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
