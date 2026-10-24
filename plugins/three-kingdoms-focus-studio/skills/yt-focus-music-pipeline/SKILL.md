---
name: yt-focus-music-pipeline
description: >-
  統籌三國志 YouTube 專注音樂影片與音樂發布流程的單一入口。當使用者想做長時間專注音樂、
  角色人聲單曲 MV、專輯曲目，或需要從構思走到「已核准的音樂 prompt + 封面 + 章節圖 +
  循環影片 + 可上架文案」整套發布包時使用。負責分流到七個專門 skill、擋下必須人工確認的
  閘門、並管理 skill 之間的交接契約。若使用者只想要單一步驟（例如只寫 prompt、只做審查），
  直接呼叫對應 skill 即可，不必走本流程。
---

# 三國志專注音樂影片 — 流程協調層

本 skill **不重做**底下七個 skill 的工作。它只做三件事：

1. **分流** — 判斷這次要做哪一條路徑。
2. **擋閘門** — 認出哪些節點必須由使用者明確確認，不能由代理自行跨越。
3. **管交接** — 定義 skill 之間要傳什麼、怎麼命名、狀態怎麼記。

所有實際工作一律委派給下列 skill，不要在此複製它們的流程細節：

| Skill | 目錄 | 職責 |
|---|---|---|
| `three-kingdoms-focus-music` | `skills/three-kingdoms-focus-music/` | 發布類型分類、長時混音結構、封面圖、15 秒循環影片、發布包、QC |
| `three-kingdoms-video-project` | `skills/three-kingdoms-video-project/` | 角色導向的專案包、規格閘門、master prompt、候選審查、章節音訊拼接、兩階段封面 |
| `music3-instrumental-prompts` | `skills/music3-instrumental-prompts/` | 純器樂 Music 3.0 Structured Caption 撰寫（templates/ + references/） |
| `three-kingdoms-music-review` | `skills/three-kingdoms-music-review/` | prompt 與音檔的審查 QA，附 `scripts/measure_audio.py` |
| `three-kingdoms-vocal-single` | `skills/three-kingdoms-vocal-single/` | 角色人聲單曲、歌詞與發音鎖、分鏡圖、YouTube Short 分支 |
| `yt-publish-strategy` | `skills/yt-publish-strategy/` | **YouTube 發布策略**：標題與關鍵字選詞、說明結構、hashtag 使用、AI 揭露義務、YPP 變現合規、競爭者基準 |
| `audio-reactive-waveform` | `skills/audio-reactive-waveform/` | 由本地音樂渲染透明頻譜條 MOV，先做短片確認，再輸出全曲供剪輯疊加 |

讀取這些檔案時以套件內的相對路徑為準，不要假設它們存在於 `~/.agents/skills/` 或 `~/.codex/skills/`。

---

## MCP 執行層 — 代理直接生成

當環境提供 **`minimax-design` MCP** 時，音樂、圖像、影片的生成由代理**直接執行**，
不再走「人工貼 prompt → 人工上傳 → 人工回填」。使用者只保留**決策與修改意見**。

完整執行手冊（能力契約、參數表、坑 A–J、產出取回、閘門規則）：

> **讀 [references/design-mcp-execution.md](references/design-mcp-execution.md)** — 動手前先讀它。

### 三條路由，按環境選

| 情況 | 走哪條 | 結果 |
|---|---|---|
| 有 `minimax-design` MCP | **MCP 執行層**（首選） | 代理生成、取回、本地驗證、交付 |
| 只有 Hosted API key | Hosted API 路線 | 依 `music3-instrumental-prompts/references/api-contract.md` |
| 什麼都沒有 | 交付 prompt 文字 | **明說**這條路做不到長度控制與器樂保證 |

### 三個最容易錯譯的地方（全部實測過）

1. **`max_new_tokens` 不存在於 MCP。** 它只屬於 SGLang 開源權重路線。
   MCP 的時長**只能靠 prompt 內的分鐘級時間軸** —— 實測不寫時間軸得 59.9 秒、
   寫 `0:00 … 3:50` 得 188 秒。
2. **器樂控制閥是 `params.mode: "instrumental"`，不是 `lyrics`。**
   實測 `lyrics` 欄位五種寫法（含留空控制組）**全部**帶無字人聲；
   `mode: "instrumental"` + 不送 `lyrics` + 正向描述 → 18/18 乾淨。
3. **`audio: false` 不保證無聲。** 實測兩次都產出 AAC 軌 → 產出後必須剝除並驗證。

### 代理仍然要自己驗收的兩件事

- **循環影片接縫**：`first-last-frame` 把首末幀綁成同一張圖**不保證**無縫
  （實測繞回差異 1.6949 > 片內最大自然轉場 0.9067）。
  必須量測，並在需要時用本地交叉溶解修掉。
- **圖像尺寸**：`resolution: "1k"` + `16:9` 實得 **1672×941**（不是 1920×1080），
  `2k` 得 2560×1440。要標準尺寸就在本地正規化。

### 授權邊界

MCP 執行層**不取消**任何閘門。創意核准 ≠ 供應商執行授權；
付費呼叫前要先向使用者說明**金額**（`confirm_cost` 不可代理自行核准）；
`deliver`、上傳、外部寫入都要先取得同意。

---

## 分流

先讀使用者的第一句話，再決定路徑。**不要**在需求已經夠具體時硬跑一輪問卷。

### 路徑 A — 長時專注音樂影片（純器樂，預設路徑）

觸發：長時間專注 / 讀書 / 工作 BGM、YouTube 發布、循環封面影片、專輯式長時混音。

**主導 skill：`three-kingdoms-focus-music`**

```
需求分流
  → 發布類型分類（focus-music STEP 1）
  → 專案規格閘門「確認規格」（video-project 的規格閘門）
  → 音樂 prompt：music3-instrumental-prompts 撰寫
  → three-kingdoms-music-review 審查確切最終 payload，保存版本化報告
  → 「prompt 已確認」後，依已核准的供應商、設定與候選數立即生成（MCP 執行層）
  → 音檔來源驗證，再審查 technical / listening / continuity
  → 候選選曲核准（使用者指定；代理只給 `agent-recommended`）
  → 章節拼接：video-project 的 chapter audio assembly
  → 封面圖兩階段：無文字母版 → 有標題成品（封面 prompt 需先確認；兩個階段各自需獨立核准）
  → 15 秒循環影片：MiniMax-H3，以已核准封面為首幀；產出後剝音軌 + 量測循環接縫
  → 發布文案 + 置頂留言 + 歸檔紀錄
  → 交付前 QC
```

### 路徑 B — 角色人聲單曲 MV

觸發：角色歌、有人聲、有歌詞、YouTube Short 或三分鐘完整 MV。

**主導 skill：`three-kingdoms-vocal-single`**

```
需求分流
  → 領域邊界確認（vocal-single §Domain boundaries）
  → 規格與核准閘門
  → 歌詞 + 虛構演唱音色指引 + 發音與韻律鎖
  → 音樂 prompt（Music 3.0 或 Lyria 3.5）
  → 分鏡圖核准
  → 外部生成（MCP 執行層或供應商介面）+ 字幕後製
  → 驗證
```

**不要**把路徑 B 混進路徑 A 的長時混音。一個 prompt 一個最終單位，不要把多首歌藏進同一次生成。

### 路徑 C — 續作或資產修訂

觸發：使用者提到既有的 project ID、slug、資產或狀態。

先檢查專案包現況再往下走。修訂時保留目前已核准或候選的版本，另開新版本，回到對應的核准閘門。

### 路徑 D — 發布策略（標題、說明、關鍵字、變現合規）

觸發：使用者要上架影片、調整標題或說明、選關鍵字或 hashtag、確認 YPP／變現資格、
問「為什麼沒人看到我的片」、或提到搜尋排名與曝光。

**主導 skill：`yt-publish-strategy`**

```
需求分流
  → 讀 SKILL.md 的硬性規則 R1–R8（標題結構、片長、搜尋匹配句、創作筆記、hashtag、AI 揭露）
  → 標題選詞：references/title-keyword-strategy.md（實測競品數據 + 可套用範本）
  → 說明撰寫：templates/description-template.md（分層範本：搜尋匹配句 / 正文 / 創作筆記 / 章節 / hashtag）
  → 變現合規檢查：references/monetization-policy.md（YPP 門檻、inauthentic content、AI 揭露、Content ID、mid-roll）
  → 競品與失敗對照：references/channel-baseline.md（同策略失敗案例 + 成功案例做法）
  → 發布前檢查清單（SKILL.md 末段）
```

**路由 A/B/C 任一路徑在產出發布包時，都必須呼叫本路徑檢查標題與說明。**
不要在 A/B/C 裡自行發明標題格式或 hashtag 組合。

---

## 音樂視覺化 — waveform / 頻譜條

觸發：音樂驅動波形、透明頻譜條、music visualizer，或 CapCut 疊加素材。
直接載入 `three-kingdoms-focus-studio:audio-reactive-waveform`；僅需疊加素材時，
依其流程確認音檔與樣式、先做最多 20 秒的透明 MOV，不必啟動完整影片企劃。

交接：本地音樂路徑、參考圖或影片（若有）、畫布與 FPS、輸出資料夾。
交付無聲 ProRes 4444 MOV 與確切 style JSON；原音樂另放音軌、對齊起點。
確認短片外觀與剪輯軟體的透明匯入後，才能做全曲。普通 MP4 預覽沒有透明度。
這是 Python／FFmpeg 本地渲染，不使用音樂生成 API 或 MiniMax-H3。

---

## 供應商選擇

音樂生成供應商由使用者決定，不要自行改：

- **MiniMax Design MCP**（環境有 MCP 時的首選）— `generate_music:music-3.0`，`prompt` ≤ **2,000 字元**，
  器樂控制閥是 `params.mode: "instrumental"`（**不是** `lyrics`），**沒有任何時長參數**，
  長度只能靠 prompt 內的分鐘級時間軸。詳見 [MCP 執行層](references/design-mcp-execution.md)。
- **MiniMax Music 3.0 公開 API** — 公開 API 與網頁欄位使用 `model: music-3.0`，`prompt` 上限 **2,000 字元**，`lyrics` 分開送出，器樂控制閥是 `is_instrumental: true`。上限 5 分鐘。既有付費／Token Plan 用戶保留存取權（120 RPM）；**自 2026-08-20 起付費 Music Generation API 不再開放新用戶** — 不要把新用戶導去申請金鑰。
- **Google Gemini API / Lyria 3.5** — 全曲用 `lyria-3.5`，走 Interactions API 的**單一 `input`**（文字或文字＋圖片清單）payload。`lyria-3-clip-preview` 僅供 30 秒 prompt 測試。**不可**套用 MiniMax 的 `lyrics` + `instructions` 兩欄制。

**絕對不要**把開源權重（`MiniMaxAI/MiniMax-Music3`）的 token 上限當成公開 API 的字元上限，兩者不同；
也**不要**把 SGLang 的 `max_new_tokens` 當成 MCP 或公開 API 的長度控制。詳情讀 `skills/music3-instrumental-prompts/references/api-contract.md`。

視覺供應商：**循環影片一律 MiniMax-H3**（預設 15 秒無縫循環），**封面圖 16:9**（YouTube 封面與縮圖），只有明確要求專輯平台作品時才用正方形。MCP 路線下，**圖像尺寸不會自動等於 1920×1080**（`1k` + `16:9` 實得 1672×941），交付前要本地正規化。

---

## 硬性閘門（不可自行跨越）

以下每一個都必須取得使用者的明確確認才能往下走。代理給建議不等於使用者核准。先核對既有紀錄；相同版本與範圍的核准直接沿用，不重複詢問。

1. **規格閘門 `確認規格`** — 動任何 prompt 或生成任何圖之前，先用繁體中文總結已定案的設計並取得此明確回應。
2. **`prompt 已確認`（音樂）** — 音樂 prompt 先經**確切 payload 審查**（不是概念描述），再取得核准。
   此回應已包含該供應商、設定與候選數的**立即生成授權**；明確授權「修訂後立即生成」時，
   完成修訂版本的審查即可執行，不必再問一次。
3. **封面 prompt 確認** — 產生封面圖之前必須先給出確切 prompt 讓使用者確認或修改。
4. **影片 prompt 確認** — 產生循環影片之前同樣必須先確認。
5. **候選選曲核准** — `agent-recommended` 不等於 `user-approved`。候選比較只能就實際評估過的維度排序。
6. **人工審查保留** — 使用者保留最終核准權。審查者的建議不得自動變更已選候選、核准 prompt、重新生成、置入或發布。

**創意核准 ≠ 供應商執行授權。** 兩者是分開的紀錄，不可互相代替。

另外，未被要求時不要主動生成人聲；未定義視覺方向時不要擅自擴張成完整發布包；超過 60 分鐘或明顯轉向戲劇化戰爭配樂前要先問。完整確認點清單見 `skills/three-kingdoms-focus-music/SKILL.md` §Confirmation Points — 本節不是窮舉。

---

## 交接契約

skill 之間靠檔案與命名交接，**不要靠對話記憶**。

### 檔案命名（照 `three-kingdoms-focus-music` §Audio naming and provenance）

- 來源候選：`<release-id>-<track-id>-candidate-<NN>-source.<actual-ext>`
- 章節混音：`<release-id>-chapter-<NN>-mix-v<NN>.<ext>`
- 完整發布：`<release-id>-full-mix-v<NN>.<ext>`

候選編號兩位數、不重用、不改寫供應商原始檔名與位元組 — 把供應商檔名記在 canonical ID 旁邊，不要取代它。**在對應核准閘門之前，檔名不可出現 `final` 或 `approved`。**

### 時長算術

時長綁定型的專注發布要先把總時長算出來。音樂總長不足指定時長時，**新增相容的音樂單位直到總長 ≥ 需求**，不要靠拉長或循環太短的素材硬湊。tail / crossfade 修補只用於小幅銜接，不是缺分鐘的主要解法。

### 時序

音樂生成 **Music 3.0 單次上限 5 分鐘**，這不改變專案的發布拓樸 — 60 分鐘的專注發布仍依計畫切成獨立 cue 再拼接。整片完整覆蓋過，才能宣稱全曲性質的結論。

### 審查交接

交給 `three-kingdoms-music-review` 時要附上：prompt 版本、專案／track／章節、anchor、來源路徑與 hash。審查只回建議與證據標籤（`measured` / `audio-model-observation` / `human-observation` / `prompt-intent` / `inference` / `not-assessed`）。

**沒有實際聆聽證明就是 `not-assessed`，永遠不等於通過。** MP3 路徑、播放器嵌入、波形、頻譜或 ffmpeg 報告本身都不構成語言模型的聽覺知覺。技術失敗可以和使用者的人工藝術選擇並存 — 記下修復義務，不要撤銷使用者的選擇。

---

## 不做的事

- 不在本地生成音樂。這個套件產出的是 prompt、規格、審查、交接，以及**由已核准外部音檔做的本地確定性章節拼接 WAV** — 拼接必須標示為 `assembly from supplied external results`，不得描述為本地生成音樂。原始音檔由外部供應商生成，可由使用者提供或經已授權工具取得。
- 只對實際取得或本地渲染並驗證的檔案宣稱已產出；透明頻譜條 MOV 必須標明為由提供音樂驅動的本地視覺化，不是生成新音樂或外部影片。只有實際工具結果、供應商任務狀態或經驗證的來源檔案，才能支持已生成音訊或影片的陳述。
- 不把 MCP 產生的音訊說成「本地生成」。MCP 產物仍由 MiniMax 模型產生；本地的部分只有拼接、正規化與量測。
- 不跨越上面任何一個硬性閘門。
- 不在沒有既有專案包的情況下假設章節數。`three-kingdoms-focus-music` 對 60 分鐘的預設是 6 章 × 約 10 分鐘，但使用者宣告的章節數才是權威。
- 不把兩條路徑混在同一次生成裡。

---

## 語言

對話用使用者的語言。人類閱讀的專案文件（spec、審查報告、發布紀錄、發布文案、置頂留言）用繁體中文。送給外部生成模型的 prompt 用英文。機器可讀的交接檔與 manifest 維持英文。
