---
name: yt-publish-strategy
description: 專門處理三國志專注音樂頻道的 YouTube 發布策略 — 標題與關鍵字選詞、影片說明結構、hashtag 使用、AI 生成內容揭露義務、以及變現（YPP）合規檢查。當使用者要上架影片、調整標題或說明、選擇關鍵字、處理 hashtag、確認變現資格、或詢問「為什麼沒人看得到我的片」時使用。本 skill 內含 2026-09-30 一手實測的競爭者數據與官方政策條文，不是通用 SEO 建議。
---

# YouTube 發布策略（三國志專注音樂）

**這個 skill 存在的唯一理由**：頻道裡有大量用心製作的音樂，因為發布方式而沒有人聽到。
本 skill 把已驗證的發布規則固定下來，避免每次重新犯同一個錯。

**所有數據與政策條文皆為 2026-09-30 實測**，來源見 `references/`。
引用時必須標明日期，**不要憑記憶更新數字**。

---

## 頻道現況基準（2026-09-30 實測，引用時務必更新）

| 指標 | 數值 |
|---|---|
| 頻道 | @3kingdomsFocus（`UCPK3SjNlXfAF5QnERsSUQew`） |
| 訂閱 | 17 |
| 影片 | 15 支，近 15 支累計觀看 2,721（平均 181，區間 32～451） |
| 估計累積觀看小時 | ~1,587 h（假設平均觀看 35 分鐘，**未經 Analytics 驗證**） |

**關鍵事實**：在「專注音樂」「古箏 專注 音樂」「放鬆 音樂 讀書」「深度工作 音樂」
「古琴 音樂 專注」等通用詞上，**頻道前 25 名完全沒有上榜**。
只在自創的「三國 專注音樂」排第一——而沒有人搜那個詞。

---

## 硬性規則（違反就是白做）

### R1. 標題結構必須是 `時長 + 功能 + 樂器`，不是詩意人物名

**必做**：

```
1 Hour of Chinese Instrumental Focus Music | Guqin & Xiao for Deep Work
【古琴簫】1 小時深度專注純音樂 ｜ Deep Work / Study

Three Kingdoms: Cao Cao's Capital | 1HR Chinese Guqin Music for Study & Writing
【三國・許昌】曹操的都城 ｜ 1 小時古琴專注音樂 ｜ 閱讀・書寫
```

**不要**：`江東心流：孫尚香專注音樂｜67分鐘三國歷史氛圍專注 BGM｜工作・閱讀・學習`

**依據**：Fantasy Meditations 同一頻道內，
`Xian - Epic Chinese Music for Focus` = 882,227 觀看，
`Xuchang: Cao Cao's Capital` = 15,794 觀看。**差 56 倍**。
有功能關鍵字的那支贏。完整數據見 `references/title-keyword-strategy.md`。

### R2. 英文為主、中文為副

實測 `ancient chinese music for focus` 前 13 名中，單純中文標題者**沒有一支達到 10 萬觀看**。

### R3. 片長 60～120 分鐘，不要為了長而長

官方 16559651 明文："resist artificially stretching content"。
把 60 分鐘鋪成 3 小時會**同時**踩到 inauthentic content 政策與這條官方警告。

**只有在曲目結構本身能撐滿 3 小時時才做 3 小時版。**
（同一支曲子做 1h + 3h 兩版，只有在 3h 版是獨立曲目結構時才成立。）

### R4. 說明開頭必須有搜尋匹配句

官方 141805：搜尋匹配靠 "**the title, description, and video content**"。
說明開頭不能全是散文，**最前面要放 1～2 句給機器讀的純陳述描述**：

> 60～90 分鐘中國風專注音樂，古琴、簫與古箏，適合閱讀、學習與深度工作。
> Chinese instrumental focus music with guqin and xiao — for study, writing and deep work.

### R5. 必須加「創作筆記」段（變現保命）

政策禁止的是 AI 生成內容「**沒有加入創作者原創、真實的見解或觀點**」。
純器樂頻道沒有旁白，所以必須**在文字上讓創作決策可見**。範本見
`templates/description-template.md`。

**這段的真正用途**：寫不出來就代表那支片確實是模板，強迫自己做出不同創作決策。

### R6. hashtag 不是排名訊號

官方 hashtag 說明頁**全文沒有任何一句說 hashtag 提升搜尋排名或曝光**，
只說它是「與其他影片互相連結」的機制。排名靠 title + description + 影片內容。

**tag 判準**：要嘛是觀眾會搜的**需求詞**（專注、學習、放鬆、入睡、古琴），
要嘛是**品牌詞**（三國、趙雲）。
**刪掉**描述製作形式的 tag（`#AI動畫` `#沉浸式動畫` `#數位繪畫` `#通勤動畫`）。

官方：tag 越多相關性越低；超過 **60 個全部忽略**。
另注意 Non-hashtags 條款：**堆疊描述性標籤字串本身違反政策**。

### R6b. 「標記 (Tags)」是另一個欄位，規則和 hashtag 不同

**不要把兩者混為一談** —— 它們在不同地方、規則不同、寬限度不同。

| | hashtag | 標記 (Tags) |
|---|---|---|
| 位置 | 影片說明裡，觀眾**看得到** | YouTube Studio → Details → Show more → Tags，觀眾**看不到** |
| 上限 | 官方 60 個即全部忽略 | **總計 500 字元**（含逗號） |
| 超標 | 關聯性稀釋 | **從尾端無聲截斷，不跳錯誤訊息** |
| 作用 | 把影片跟其他影片／播放清單連結 | 讓 YouTube 讀懂內容，補標題放不下的變體與生僻詞 |

官方說明頁（support.google.com/youtube/answer/146402）對標記的定位只有一句：

> "Tags can be useful if the content of your video is commonly misspelled.
> Otherwise, tags play a minimal role in your video's discovery."

**也就是說：標記唯一被官方點名的用途是「拼錯的搜尋詞」與「標題放不下的生僻詞」。**
它不是排名工具 —— 標題、縮圖、說明開頭的權重遠高於它。

實務規則：

- **不要填滿 500 字元。** 官方與業界一致的口徑是 5～15 個就夠，
  填滿只會讓不相干的詞稀釋相關性；留餘裕給日後微調。
- **YouTube 依序讀取標記，第一個權重最高**；截斷也從尾端發生 →
  最重要的放最前面，最不重要的放最後。
- **把「觀眾真的會打、但標題塞不進去」的變體放在這裡**：
  含空格的查詢字串（`專注 音樂`）、樂器別名與拼音變體（`hsiao flute`）、
  標題裡只有裸樂器名而沒有可搜片語的情況（`erhu music`）。
- **不要用不相關的熱門關鍵字填額度** —— 官方明文說這會讓系統混淆影片內容。
- **頻道層級另有一個「關鍵字 (Keywords)」欄位**（Settings → Channel → Basic info），
  同樣 500 字元上限，但它描述**整個頻道**，應放樂器與品牌詞而非單片專屬的用途詞。
- 「堆疊描述性標籤字串違反政策」是**說明欄**的條款，不是標記欄的 ——
  不要把兩邊的限制互相套用。

### R7. AI 揭露是強制的

官方「必須揭露」清單**第一項就是 `AI generated music`**。
上傳時 Attributes → "AI use" 勾 **Yes**，不論視覺是否寫實。

官方明文揭露無成本：
> "Disclosing AI content won't limit a video's audience or impact its eligibility to earn money."

不揭露的處罰包含移除內容或 YPP 停權。**永遠不要為了躲標籤而不揭露。**

### R8. 統一片頭片尾是允許的

官方明文："Same intro and outro for your videos, but the bulk of your content is different"
屬於可變現範例。**不要為了避嫌而破壞美學一致性**。

---

## 不可做的事

| # | 不要做 | 理由 |
|---|---|---|
| 1 | 純中文標題 | 已實測 0 上榜 |
| 2 | 競爭「專注音樂」等中文大詞 | 已被 5～11 年前的大頻位鎖死，同頁差距 1,700～7,700 倍 |
| 3 | 投入 Shorts | 短片 199 vs 長片 176，**無漏斗效應**；2027 起 Shorts 需 90 天 1,000 萬觀看才分收益 |
| 4 | 刪掉重傳（re-upload） | 損失觀看數與留言，且解決不了「長得像」的結構問題 |
| 5 | 重寫文案風格 | 文學性是這批片唯一的差異化資產（望樓筆記靠的就是這類文案） |
| 6 | 在說明裡堆疊大量描述性 tag 串 | 官方 Non-hashtags 條款明文禁止 |

---

## 發布前檢查清單

上架前逐項打勾，**任何一項不過就不要上架**：

- [ ] 標題含時長 + 用途關鍵字 + 樂器名
- [ ] 標題有英文版（主）+ 中文版（副）
- [ ] 說明**最前面**有搜尋匹配句（含中英文關鍵字）
- [ ] 說明有「創作筆記」段，寫出**這支片獨有的**創作決策
- [ ] 章節時間軸與音樂實際結構對齊
- [ ] hashtag ≤ 15 個，每個都是需求詞或品牌詞，無黏連、無簡繁混用
- [ ] 沒有描述製作形式的 tag（AI 動畫、沉浸式、數位繪畫…）
- [ ] AI 揭露已勾選
- [ ] 「關於作品：非歷史還原」免責仍在
- [ ] 縮圖在 64px 仍可讀

---

## 變現合規（申請 YPP 前必讀）

**門檻**（官方原文，2026-09-30）：

| 層級 | 門檻 | 備註 |
|---|---|---|
| fan funding | **500 訂閱 + 3,000 合格觀看小時** | 不受 2027 變更影響，近期務實目標 |
| 廣告（現況） | 1,000 訂閱 + 4,000 h | |
| 廣告（2027-02-01 起） | 1,000 訂閱 + **8,000 h** | 籌備期只剩約 4 個月 |

**兩個容易踩的坑**：

1. **Shorts Feed 的觀看不計入門檻觀看小時**（官方明文）。
2. **24/7 直播未轉 VOD 不計入**。只能用長片 VOD 累積。

**審核者會檢查**（官方明列）：Main theme / Most viewed videos / Newest videos /
Biggest proportion of watch time / **Video metadata（含 titles, thumbnails, descriptions）** /
**About 頁面**。

**15 支的頻道等於每支都可能被看到。** 這是 R1–R8 全部存在的原因。

完整條文與逐條引用見 `references/monetization-policy.md`。

---

## mid-roll 廣告（變現後才會遇到的問題）

官方 6175006：

> "On monetized videos that are **8 minutes or longer**, you can turn on ads during the middle."
> "Ad slots placed at **natural breakpoints**, such as **a pause in audio or transition in visual**,
> are more likely to serve ads as our systems generally find higher viewer retention at these breakpoints."

**→ 60～120 分鐘的片，官方可以在音樂停頓處插 9～15 支廣告。**
**→ 反直覺：留存高的地方反而更容易被插廣告。**

**章節切點同時是你的廣告切點，排版時要一起想。**

---

## 診斷「為什麼沒人看」

依序檢查，**不要跳過前項**：

1. **在通用關鍵字上榜了嗎？** 用 InnerTube search API 實測前 25 名，不要靠感覺。
2. **標題有功能關鍵字與樂器名嗎？**（R1）
3. **片長落在 60～120 分鐘嗎？**（R3）
4. **前 30 秒留存如何？** 這是唯一我無法從公開資料取得的必要數據。
5. **頻道是否有 12 支以上內容？** 官方 16559651：新頻道關鍵在「critical mass of content」。

**已知對照組（同策略失敗實測）**：

| 頻道 | 策略 | 結果 |
|---|---|---|
| `@MissMusDaily` | 中文古風讀書音樂、1h+6h 成對、詩意標題 | 290 訂閱，30 支，觀看 12～450，**無一破 500** |
| `Attraction Space` | **三國 + AI 音樂 + 3 小時** | 287 訂閱，觀看 6～86 |
| `@3kingdomsFocus` | 中文三國、55～85 分鐘、詩意人物標題 | 17 訂閱，觀看 32～451 |

**成功對照組**：

| 頻道 | 訂閱 | 做法 |
|---|---|---|
| 望樓筆記 | 11,300 | 中文 + `功能＋樂器`結構（`ADAGIO 深藍迴響｜深海療癒純音樂｜毛氈鋼琴 × 大提琴 × 低音黑管`），單支 249,103 |
| 阿鮑 Abao | 1,290,000 | 繁中、8K 實景、`地點 + 動作 / 8K / 音樂類型` |
| Quiet Quest | 524,000 | 純英文、`4 Hours Of...` 時長前置、每週一支 |

**關鍵對照**：望樓筆記 11,300 訂閱能在「專注音樂」排第 6、在「心流 音樂」排第 3。
**訂閱數不是護城河，關鍵字覆蓋才是。**

---

## 誠實邊界

以下**無法從公開資料驗證**，不可用猜的數字做決策：

- **ambient 類別的 RPM** — 官方從未公布，Reddit API 與 8 個搜尋引擎全部 403。
  只能給計算結構：`收入 = 觀看小時 × 每小時曝光次數 × RPM`，不給數字。
- **改舊片標題後排名是否真的會變** — 官方只說「Maybe」且歸因於觀眾互動變化。
- **hashtag 對推薦系統的實際權重** — 官方文件完全不提。
- **MiniMax Music 3.0 / Lyria 的商業授權條款** — 未查證，**上架前必須自行確認**，
  直接影響 Content ID 索賠時的權利主張強度。

---

## 相關 skill

| Skill | 職責 |
|---|---|
| `yt-focus-music-pipeline` | 流程協調層，本 skill 由它分流 |
| `three-kingdoms-focus-music` | 發布類型分類、長時混音結構、封面、循環影片 |
| `three-kingdoms-video-project` | 專案包、章節音訊拼接、兩階段封面 |
| `three-kingdoms-music-review` | 音檔技術與藝術審查 |
| `music3-instrumental-prompts` | 純器樂 prompt 撰寫 |
| `three-kingdoms-vocal-single` | 角色人聲單曲、歌詞、分鏡、Short 分支 |

**本 skill 不取代它們的任何職責**：本 skill 只管「片子做完成之後怎麼讓人找到」。

---

## 參考檔案

- `references/title-keyword-strategy.md` — 關鍵字與標題實測數據（競品對照表）
- `references/monetization-policy.md` — YPP 門檻、inauthentic content、AI 揭露、Content ID
- `references/channel-baseline.md` — 頻道現況、競爭者全景、失敗案例
- `templates/description-template.md` — 可直接填的說明範本（含創作筆記）
