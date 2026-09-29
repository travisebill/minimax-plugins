---
name: yt-focus-music-pipeline
description: >-
  統籌三國志 YouTube 專注音樂影片與音樂發布流程的單一入口。當使用者想做長時間專注音樂、
  角色人聲單曲 MV、專輯曲目，或需要從構思走到「已核准的音樂 prompt + 封面 + 章節圖 +
  循環影片 + 可上架文案」整套發布包時使用。負責分流到五個專門 skill、擋下必須人工確認的
  閘門、並管理 skill 之間的交接契約。若使用者只想要單一步驟（例如只寫 prompt、只做審查），
  直接呼叫對應 skill 即可，不必走本流程。
---

# 三國志專注音樂影片 — 流程協調層

本 skill **不重做**底下五個 skill 的工作。它只做三件事：

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

讀取這些檔案時以套件內的相對路徑為準，不要假設它們存在於 `~/.agents/skills/` 或 `~/.codex/skills/`。

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
  → 音樂生成 prompt：music3-instrumental-prompts 撰寫 → 產出音檔
  → 審查：three-kingdoms-music-review（prompt / technical / listening / continuity）
  → 章節拼接：video-project 的 chapter audio assembly（音檔由使用者提供）
  → 封面圖兩階段：無文字母版 → 有標題成品（封面 prompt 需先確認；兩個階段各自需獨立核准）
  → 15 秒無縫循環影片：MiniMax-H3，以已核准封面為首幀
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
  → 外部生成交接 + 字幕後製
  → 驗證
```

**不要**把路徑 B 混進路徑 A 的長時混音。一個 prompt 一個最終單位，不要把多首歌藏進同一次生成。

### 路徑 C — 續作或資產修訂

觸發：使用者提到既有的 project ID、slug、資產或狀態。

先檢查專案包現況再往下走。修訂時保留目前已核准或候選的版本，另開新版本，回到對應的核准閘門。

---

## 供應商選擇

音樂生成供應商由使用者決定，不要自行改：

- **MiniMax Music 3.0** — 公開 API 與網頁欄位使用 `model: music-3.0`，`prompt` 上限 **2,000 字元**，`lyrics` 分開送出。上限 5 分鐘。既有付費／Token Plan 用戶保留存取權（120 RPM）；**自 2026-08-20 起付費 Music Generation API 不再開放新用戶** — 不要把新用戶導去申請金鑰。
- **Google Gemini API / Lyria 3.5** — 全曲用 `lyria-3.5`，走 Interactions API 的**單一 `input`**（文字或文字＋圖片清單）payload。`lyria-3-clip-preview` 僅供 30 秒 prompt 測試。**不可**套用 MiniMax 的 `lyrics` + `instructions` 兩欄制。

**絕對不要**把開源權重（`MiniMaxAI/MiniMax-Music3`）的 token 上限當成公開 API 的字元上限，兩者不同。詳情讀 `skills/music3-instrumental-prompts/references/api-contract.md`。

視覺供應商：**循環影片一律 MiniMax-H3**（預設 15 秒無縫循環），**封面圖 16:9**（YouTube 封面與縮圖），只有明確要求專輯平台作品時才用正方形。

---

## 硬性閘門（不可自行跨越）

以下每一個都必須取得使用者的明確確認才能往下走。代理給建議不等於使用者核准。

1. **規格閘門 `確認規格`** — 動任何 prompt 或生成任何圖之前，先用繁體中文總結已定案的設計並取得此明確回應。
2. **封面 prompt 確認** — 產生封面圖之前必須先給出確切 prompt 讓使用者確認或修改。
3. **影片 prompt 確認** — 產生循環影片之前同樣必須先確認。
4. **候選選曲核准** — `agent-recommended` 不等於 `user-approved`。候選比較只能就實際評估過的維度排序。
5. **人工審查保留** — 使用者保留最終核准權。審查者的建議不得自動變更已選候選、核准 prompt、重新生成、置入或發布。

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

- 不在本地生成音樂。這個套件產出的是 prompt、規格、審查、交接，以及**由已核准外部音檔做的本地確定性章節拼接 WAV** — 拼接必須標示為 `assembly from supplied external results`，不得描述為本地生成音樂。原始音檔由外部供應商生成後由使用者提供。
- 不宣稱已生成任何音訊或影片，除非使用者已提供該檔案。
- 不跨越上面任何一個硬性閘門。
- 不在沒有既有專案包的情況下假設章節數。`three-kingdoms-focus-music` 對 60 分鐘的預設是 6 章 × 約 10 分鐘，但使用者宣告的章節數才是權威。
- 不把兩條路徑混在同一次生成裡。

---

## 語言

對話用使用者的語言。人類閱讀的專案文件（spec、審查報告、發布紀錄、發布文案、置頂留言）用繁體中文。送給外部生成模型的 prompt 用英文。機器可讀的交接檔與 manifest 維持英文。
