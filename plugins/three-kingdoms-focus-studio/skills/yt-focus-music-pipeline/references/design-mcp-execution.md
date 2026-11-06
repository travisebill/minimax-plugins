# MiniMax Design MCP 執行層

這份文件是本外掛「實際生成」的執行手冊。全部內容來自 **S02-P01 專案的一手實測**
（2026-10-22，macOS，minimax-design MCP），不是文件轉述。

**適用時機**：使用者已核准創意、且目標環境提供 `minimax-design` MCP 工具時，
由代理直接完成音樂／圖像／影片生成，不再走「人工貼 prompt、人工上傳、人工回填」。

**不適用時機**：MCP 不可用、或使用者只想要 prompt 文字。此時退回各 skill 原本的
交付方式，並**明說**哪些能力這條路做不到。

---

## 1. 先選對路，再寫 prompt

MiniMax Music 3.0 有**四條**介面。它們的參數、限制與產出長度互不相同，
把某一條的規則套到另一條上是本外掛過去最常見的錯譯來源。

| 路線 | 器樂控制閥 | 時長控制 | 實測產出長度 | 適用 |
|---|---|---|---|---|
| **Hosted API**（`api.minimax.io/v1/music_generation`） | `is_instrumental: true` | 無直接參數 | 取決於 prompt | 有 API key 時 |
| **Design MCP**（本文件） | `params.mode: "instrumental"` | **只能靠 prompt 內的時間軸** | 見 §2.3 | **首選** |
| **SGLang 開源權重**（`/v1/audio/speech`） | 無旗標 | `max_new_tokens`（25 幀/秒） | 可控 | 有 GPU 時 |
| **Connector wrapper** | **沒有任何旗標欄位** | 無 | 隨機，不可控 | 不可用 |

> `max_new_tokens` **只存在於 SGLang 路線**。Design MCP 沒有這個參數；
> 看到任何宣稱 Design MCP 用 `max_new_tokens` 控制長度的條文，都是錯譯。

### 負向排除句：分兩類，證據不同

**foley／環境音類別 —— 不要寫，連負面寫都不要。**
寫了 `no rain / no hiss / no thunder`，那個類別仍可能被召喚出來（實測）。
→ 刪掉所有 foley 與環境音字樣，只描述音樂內容，環境音留到後期加。

**人聲類別 —— 可以留，但它從來不是機制。**
實測 2026-10-22（MCP，18 個候選）：帶著
`No lead vocals, backing vocals, choir, humming, spoken words, chants or vocal samples`
的 prompt **18/18 全部乾淨**，人工聆聽確認。
→ 這行可以當文件性說明留著，但**真正的控制是路線的旗標**，不是這行字。
   實測 2026-09-30：五份寫了 `no vocals, no choir, no spoken word` 的 caption
   **全部**仍產生無字人聲。

各路線的「真正的控制」：

- Hosted API：`is_instrumental: true` + **不送** `lyrics` + prompt 內**只寫正向描述**。
- Design MCP：`mode: "instrumental"` + **完全不送** `lyrics` 欄位 + prompt 內**只寫正向描述**。
- SGLang / connector：沒有任何旗標可依。此時**不要**假裝能用文字擋掉人聲；
  應改用後製（選擇性剔除指定頻段）或直接改變發布方向，並向使用者說明限制。

正向描述的寫法範例：

```text
a Chinese zither (guzheng) - a plucked many-stringed instrument with silk-string
timbre, a metallic ring, and a slight downward bend on held notes
```

**點名一種樂器 > 列舉多種樂器。** 實測四組控制：音色優先（不點名）3/4 乾淨、
名稱前置 4/4 乾淨、代理詞 4/4 乾淨、樂器群列舉 1/4 乾淨（且會附帶做出高潮段）。

---

## 2. `generate_music:music-3.0` 契約

### 2.1 參數

| 欄位 | 值 |
|---|---|
| `prompt` | **≤ 2000 字元**（含空白與段落斷行） |
| `mode` | `song` 或 `instrumental`（一級參數） |
| `lyrics` | **僅在 `mode: song` 有效**。`instrumental` 時完全不送此欄位 |
| `references` | `totalCount = 0` —— **不可帶參考素材** |

`execute` 呼叫必須同時宣告 `output.resources` 與 `output.composition.placements`，
否則產物不會落到可取回的 Resource 上。

### 2.2 器樂控制：只有 `mode` 是真的閥

**實測（18 個候選，全數人工聆聽裁決）：**

| 做法 | 結果 |
|---|---|
| Design MCP + `mode: "instrumental"` + 不送 `lyrics` + 正向描述 | **18/18 無人聲** |
| Connector wrapper（**沒有** `mode` 欄位） | 88% 帶無字人聲 |
| `lyrics` 欄位五種寫法（`[Instrumental]` / `Instrumental` / 結構標籤 / 描述句 / **留空控制組**） | **五種全部帶無字人聲** |

> **`lyrics` 欄位完全無效。** 連「留空」這個控制組都帶人聲。
> 它不是控制閥，只是被模型忽略的欄位。**不要把 `lyrics` 當成開關。**

### 2.3 長度：prompt 時間軸是唯一的開關

Design MCP 沒有任何時長參數。實測同一模型：

| prompt 內容 | 實得長度 |
|---|---|
| 不寫時間軸 | **59.9 秒** |
| 寫 `0:00 … 3:50` 的分鐘級時間軸 | **188 秒** |

供應商知識卡明載「精確時長不可硬保」。
→ **不要宣報曲目數，要宣報分鐘區間。**

### 2.4 Prompt 三區塊結構

每首 prompt 三個區塊，空行分隔：

```text
<Global Metadata>

<Arrangement — 時間軸，寫明每段的進場與退場>

<Instrument identity — 主奏樂器的音色細節>
```

寫作規則見 `skills/music3-instrumental-prompts/`。

---

## 3. `generate_image:gpt-image-2.5-sunburst` 契約

| 欄位 | 值 |
|---|---|
| `prompt` | ≤ 7500 字元 |
| `aspect_ratio` | 支援 `16:9` 等 |
| `resolution` | `1k` / `2k` / `4k` |
| `quality` | `low` … `max`（預設 `high`） |
| `background` | 可指定 |
| 圖像 references | ≤ 16 |

### ★ 坑 D：`resolution` 的實際長邊

| 設定 | 實得尺寸 |
|---|---|
| `resolution: "1k"` + `aspect_ratio: "16:9"` | **1672×941**（**不是** 1920×1080） |
| `resolution: "2k"` + `aspect_ratio: "16:9"` | **2560×1440** |

要交付 1920×1080 就必須**在本地正規化**，不能假設輸出尺寸。

### ★ 坑 C：參考圖的版面元素無法剝除

把參考圖交給模型做 image-to-image 時，參考圖上的**版面元素（文字、浮水印、標誌）
不會被剝除**，會被一起學進去。

- 若成品必須乾淨 → 必須先在本地把元素裁掉再送參考圖。
- 若成品就是「一張圖」而非「合成」 → 直接說明限制，不要反覆重試。

---

## 4. `generate_video:MiniMax-H3` 契約

| 欄位 | 值 |
|---|---|
| `mode` | `reference` 或 `first-last-frame` |
| `duration` | 4–15 秒 |
| `resolution` | `768p` / `2k` |
| `audio` | 布林 |
| first-last-frame 圖像 references | ≤ 2（`lastFrameOnly`） |

### ★ `first-last-frame` 不接受固定 `aspect_ratio`

用 `first-last-frame` 時**不要**送固定寬高比參數；由參考圖決定畫面比例。
（`reference` 模式會吃掉參考圖上的文字。）

### ★ 坑 B：`audio: false` 不保證無聲

**實測兩次，都中招：**

| 產物 | 送出參數 | 實得音軌 |
|---|---|---|
| 6.58 秒 mp4 | `audio: false` | AAC 軌，mean −24.2 dB／max −3.6 dB |
| 15.08 秒 mp4 | `audio: false` | AAC 軌（32,000 Hz stereo，129,825 bps，473 幀），mean −46.5 dB／max −33.3 dB |

→ 產出後**必須**檢查並剝除：

```bash
ffprobe -v error -show_entries stream=index,codec_type,codec_name -of default=noprint_wrappers=0 out.mp4
ffmpeg -hide_banner -y -i out.mp4 -an -c:v copy out-nosound.mp4   # -an 才是丟音軌
ffmpeg -hide_banner -i out.mp4 -map 0:a:0 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
```

> `-vn` 是丟影片不是丟音軌，寫反會得到只有音軌的檔案。
> `-c:v copy` 不重編碼，影格數不變（實測 362 → 362）。

### ★ 循環接縫：`first-last-frame` 綁同一張圖**不保證**無縫

把首幀與末幀都綁成同一張參考圖（`references: [{versionId: A}, {versionId: A}]`），
由建構保證首幀就是該圖 —— 但**末幀回到該圖是模型的自由發揮**，實測並未回到。

**S02-P01 實測（15.08 秒 / 24 fps / 362 幀）：**

| 指標 | 值 |
|---|---|
| 逐幀平均絕對差中位數 | 0.3575 |
| 片內最大自然單次轉場 | 0.9067 |
| **繞回差異（末幀→首幀）** | **1.6949** ← 全片 362 次轉場中最大的一次 |
| 重編碼控制組（內容不變） | 1.7000 |

控制組（內容完全不變、只換編碼參數）差異僅 0.005
→ **接縫來自來源內容，不是編碼假象。**

觀感是「慢動作走完 → 停住 → 彈回」。差異分布均勻（天空 1.41／中帶 1.56／近景 2.12），
最大單像素差 48，5.68% 像素差 > 4/255 → 屬**整體光影漂移**，不是局部破圖。

#### 判準

**繞回差異不得大於片內本來就會出現的最大單次轉場。**

不要用中位數或 p95 當門檻：慢速氛圍片的逐幀差異本來就會浮動
（實測 0.03–0.91），用中位數當門檻會誤判「來回鏡頭」這類
繞回**等於自然轉場**的合法無縫版本。

#### 兩個本地零成本修法

| 修法 | 長度 | 繞回平均像素差 | 差 > 4 的像素 | 備註 |
|---|---|---|---|---|
| **交叉溶解版**（末 0.5 s 溶解回首幀） | 14.583 s | 0.6601 | **0.024%** | 建議；長度仍符合目標、不做運動反向 |
| 來回鏡頭版（正放＋倒放） | 30.083 s | 0.7828 | 0.578% | 數學上保證無縫，但長度加倍、運動反向 |

交叉溶解版的可見差異像素比原始少 **234 倍**。

#### 量測必須自我檢查

量測腳本要先用「已知應無縫」與「已知應有接縫」兩組素材跑同一套邏輯，
確認能分辨才採信結論。並且**跨版本比較時要把編碼條件一併寫出**：
同一素材以 libx264 crf 14 重編後，量得差異可由 0.65 升到 0.78。

---

## 5. `execute` 呼叫形狀與產出取回

```jsonc
{
  "capabilityId": "generate_music:music-3.0",
  "prompt": "<≤2000 字元>",
  "params": { "mode": "instrumental" },
  "output": {
    "resources": [{ "mode": "create", "name": "使用者可見名稱" }],
    "composition": {
      "compositionId": "<既有 Composition ID>",
      "placements": [{ "key": "primary", "role": "主音軌" }]
    }
  }
}
```

- `composition.name` **會被拒**，必須用 `compositionId`。
- 產物落地為 `store/ver_<versionId>.png|.mp3|.mp4`。
- `get_output(versionId)` 可反查本機絕對路徑。
- `count` 用於同一 prompt 的付費變體；不同內容必須分開呼叫。
- 失敗的變體不會出現在 `task.outputs`，也不會自動重試。

---

## 6. 坑 A–K（全部為實測）

| 坑 | 現象 | 處理 |
|---|---|---|
| **A** | 使用者在 App 介面手動生成的產物全在 `store/.pending-<uuid>`；`composition_search`／`task_query`／`index.sqlite` **都看不到** | 代理只能直接掃 `store/` 目錄 |
| **B** | `audio: false` 仍產出 AAC 音軌（兩次實測） | 產出後剝除並以 `volumedetect` 驗證 |
| **C**（修訂） | 參考圖的版面元素「無法」剝除 —— **這條已被推翻** | **多格設定圖可以直接當參考圖**，只要 prompt 寫明 `do not reproduce the reference layout: no panel grid, no borders, no colour strip, no other poses, no lettering of any kind`。實測零格線洩漏、角色外觀逐項一致。本地裁主格降為**備援**（需要單一姿勢參考，或真的洩漏版面時才用） |
| **D** | `1k` + `16:9` → 1672×941（不是 1920×1080）；`2k` → 2560×1440 | 要標準尺寸就在本地正規化 |
| **E** | `.pending` 檔名**沒有副檔名** | 靠 `file`／ffprobe 判斷型別 |
| **F** | 專案重新命名 → `projectId` 改變 | 綁定後不要重新命名；必須綁定時重新 `open_project` |
| **G** | store 116 個檔案只有 37 份**唯一內容** | 必須 hash 去重，不能用檔案數當產物數 |
| **H** | 目視判讀小型索引圖會誤讀（本次誤讀出 16 個不存在的角色） | 索引圖只當導覽，數量與內容以 API／檔案清單為準 |
| **I** | `open_project` 對**未在 App 開啟**的專案回 `PROJECT_NOT_OPEN` | 請使用者在 App 開啟該專案後重試 |
| **J** | `deliver` 匯入本機檔案：路徑驗證只接受當前開啟專案資料夾內，但 4 次重播全在 `materialize` 階段回 `MATERIALIZATION_OUTCOME_UNKNOWN` | 改用**文字完全鎖定風格**替代參考圖；不要無限重試 |
| **K** | 透過 deferred 工具路徑呼叫 `execute` 時，**陣列與整數參數會被字串化**（`references: [{…}]`、`count`、`output.resources`、`output.composition.placements`）→ schema 驗證必然失敗（`/references: must be array`）。**重試沒有用** —— 同一份 payload 重送仍失敗 | **直連 MCP 端點**講 JSON-RPC（見 §9）。注意 `capability_get` 的 `ids: ["…"]` 這種「字串陣列」反而會過 —— **不要把兩者混為一談** |

---

## 7. 閘門與授權

| 事件 | 需要什麼 |
|---|---|
| 核准創意（prompt、封面方向、章節圖） | 使用者明確回覆 |
| 付費生成 | 先向使用者說明**金額**；`confirm_cost` **不可**代理自行核准 |
| 產出選候選 | 代理只給 `agent-recommended`，**不代使用者選** |
| `deliver`、上傳、外部寫入 | 先取得同意 |

**創意核准 ≠ 供應商執行授權。** 兩者分開記錄。

## 8. 誠實標記

成品若由外部結果組裝而來，必須標為
`assembly from supplied external results`，
**不得宣稱本地生成了音樂**。

## 9. 直連 MCP 端點（deferred 工具路徑不可用時）

碰到坑 K 時，直接對 MCP 端點講 JSON-RPC：

1. `mavis mcp list` 取 `endpoint`（Design = `http://127.0.0.1:18810/mcp`）
2. `initialize` → **記下回應的 `Mcp-Session-Id` 標頭** → `notifications/initialized`
3. `tools/call`，body 是 `{"name": "<tool>", "arguments": {…}}`
4. **回應是 SSE**：跳過 `: keepalive` 行，取**最後一個** `data:` 行再 JSON.parse
5. **每次 HTTP 連線都是新的 MCP session** → 專案綁定要重取
   （`tools/call` 前先送一次 `open_project`）

好處：參數原樣送出、不受字串化影響，還能一次送出多個獨立生成做批次並行。

實作參考（**本 skill 的 `scripts/` 內，隨外掛走**）：
`scripts/design_mcp_call.py`（直連 client，endpoint 自動從 `~/.minimax/mcp.json` 發現，
專案用 `DESIGN_MCP_PROJECT` 指定）、`scripts/design_wait.py`（等任務到終態）、
`scripts/design_wait_many.py`（等多個任務）、`scripts/design_batch.py`（多任務並行批次）。

```sh
# 確認連線與綁定
python3 scripts/design_mcp_call.py --endpoint
# 列出工具
python3 scripts/design_mcp_call.py --list
```

## 10. 付費生成的實測單價（2026-11-01）

| 能力 | 設定 | credits |
|---|---|---:|
| `generate_image:gpt-image-2.5-sunburst` | 2k/high，**無參考圖** | **160**／張 |
| | 2k/high，**1 張參考圖** | **170**／張 |
| | 2k/high，**2 張參考圖** | **180**／張 |
| `generate_music:music-3.0` | count=2 | **40**／批 |
| | count=3 | **60**／批 |
| `generate_video:MiniMax-H3` | 15 秒 / 2k | **1,440**／支 |

**參考圖越多越貴** —— 先前記過「帶 1 張或 2 張同價 170」是**錯的**。
H3 的 15 秒 / 2k 實測 **1,440**（先前估的 1,950 高估 35%）。
