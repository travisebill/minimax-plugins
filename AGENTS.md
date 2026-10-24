# AGENTS.md — minimax-plugins

> Agent cold-start 入口。進到這個 repo 不知道怎麼開始時，先讀這裡，再讀 `README.md`。

## 這個 repo 是什麼

MiniMax Code 與 Codex 外掛的版控來源。

- MiniMax：`plugins/<name>/`，下列操作規則適用於此版本。
- Codex：`codex/marketplace/plugins/<name>/`；先讀 `codex/AGENTS.md` 與 `codex/README.md`，使用 Codex manifest 和 CLI 流程。
- 根目錄 `.agents/plugins/marketplace.json` 僅供 Codex 從 GitHub 安裝，來源路徑必須指向 `codex/marketplace/plugins/`。

## 三個必知事實

1. **本機安裝處 ≠ 這個 repo**：runtime 要求外掛放在 `<activeDataDir>/plugins/<name>/` 且**拒絕 symlink**，所以兩邊是複製關係，改完要同步（指令見 `README.md`）。
2. **改了 skill 清單要重啟 app**：新增 skill（或新外掛）後 catalog 不會可靠地更新；實測等 8 分鐘仍載不到、重啟後立刻可載。
3. **驗證只能靠 `skill` 工具**：用 `<plugin-name>:<skill-name>` 載入成功（回傳的 `Location` 指向該外掛）才算「Desktop 已識別」。註冊狀態不在檔案系統裡，`<activeDataDir>/plugins/` 只有 `known_marketplaces.json`。

## 動工前

- 要改哪個外掛就讀 `plugins/<name>/.minimax-plugin/plugin.json`（`skills` 清單是權威）與該 skill 的 `SKILL.md`
- 動既有外掛前先確認本機那份與 repo 是否一致；不一致先對齊再改，不要兩邊各改一份
- 新外掛一律用 `plugin-creator` skill 建（manifest 格式、icon 選法、驗證清單都在那支 skill 裡，不要憑印象手寫）

## 改完的收工清單

1. bump `.minimax-plugin/plugin.json` 的 `version`（SemVer）
2. 靜態驗證：JSON 無重複 key / 無 BOM / 結尾換行、每個 skill frontmatter `name` == 目錄名、icon 位元組符合副檔名、無 symlink、無 `.DS_Store`
3. 同步到本機 → 重啟 app → `skill` 工具載入驗證
4. 更新 `README.md` 的外掛表格（新增外掛時）

## 雷區

- `.DS_Store`：只要在 Finder 裡開過外掛目錄就會生成，會混進 package。已列 `.gitignore`，但**不要**因此就放心用 Finder 瀏覽
- `._*` 與 `__pycache__`：外掛放在 exFAT 或外接磁碟時，macOS 會替每個檔案生成 AppleDouble 側車檔；
  跑過 skill 內的測試或 import 過腳本也會留下 `__pycache__`。
  兩者都已被 `.gitignore` 擋在版控外，但 `codex/scripts/package_plugins.py` 掃的是**檔案系統**，
  會被 `._README.md`、`__pycache__` 這種項目擋下而整包驗證失敗。
  **打包或整包驗證前先清一次**：`find . -name '._*' -type f -delete; find . -name '__pycache__' -type d -exec rm -rf {} +`
- 裸 skill 名載入失敗（`Local skill not found`）≠ 外掛沒被收錄，先確認有沒有帶 `<plugin>:<skill>` 前綴
- manifest 的 `apps` 必須是 `[]`；不要建 `*.app.json`
- 不要把 token / 憑證寫進 manifest、MCP headers 或 env（`.gitignore` 只是最後一道防線）
