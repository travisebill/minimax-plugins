---
name: learning-game-feel
description: Give a learning interaction readable feedback and game feel without slowing it down or hiding the concept. Use when an interaction works but feels flat (按下去沒反應, 答對答錯長得一樣, 很乾, 沒回饋感), when adding answer feedback, animations, sound, XP/解鎖 effects, or transitions to a teaching site, when a feedback animation is too long or blocks the next action, or when a reward effect needs to stay readable on a mid-range phone, with reduced motion, or with sound off.
---

# Learning Game Feel（回饋層 / game feel）

## Overview

這一層只做一件事：**讓因果關係看得見。** 學生做了什麼 → 世界怎麼變 → 為什麼。

分層：機制（學生玩什麼）→ `learning-mechanics`；**回饋（做了之後看到什麼）→ 本 skill**；課程內容與事實審查 → `progressive-learning-site`；3D / Phaser → `game-studio`。

**這一層不是「加動畫」。** 動畫只是手段；判準永遠是「學生有沒有更清楚發生什麼事、為什麼」。

## 四條原則

1. **回饋即因果**：操作後 **100ms 內**必須有可見變化。超過 100ms 學生會以為沒按到，於是重複點擊。
2. **對錯可辨識且不只靠顏色**：顏色 + 形狀/圖示 + 文字，三取二以上。色盲學生、教室投影、灰階螢幕都要能分辨。
3. **獎勵不阻斷**：慶祝動畫 **≤600ms**，且**可被下一個操作打斷**（不鎖輸入、不排隊）。連答三題不該被三段動畫拖慢。
4. **手機優先**：以中低階手機為基準；動畫只用 `transform` / `opacity`；`prefers-reduced-motion` 有降級路徑；音效預設可關且不是必要資訊通道（教室環境）。

## Procedure

### 1. 列「回饋時刻表」

寫下這個互動裡每一次狀態改變，以及學生當下該看到什麼：

| 時刻 | 學生做了什麼 | 應該立刻看到 | 屬於哪一層 |
|---|---|---|---|
| 微 | 按下 / 懸停 | 按鍵壓下、選項被選取 | 微回饋 |
| 即時 | 送出答案 | 對 / 錯 + 為什麼 | 即時回饋 |
| 階段 | 過關 / 解鎖 / 拿 XP | 進度前進、新東西出現 | 階段回饋 |

**任何一格空白就是缺陷**：學生做了事卻沒有回應，體感就會「很乾」。

### 2. 把「回饋」與「解釋」分開處理

- **回饋**（對 / 錯）要**立刻**出現（≤100ms）
- **解釋**（為什麼錯、正解）可以稍慢，但**必須緊接在回饋之後**、不要彈窗阻斷
- 不要把解釋塞進動畫裡（學生會為了看動畫而亂答）；也不要只給對錯不給為什麼（那就退化成賭博）

### 3. 三層回饋的最小實作

- **微回饋**：`:active` 位移 1–2px、`:hover` 微亮、選取態有明顯邊框
- **即時回饋**：答對＝scale 脈動 + 綠 + ✓ + 文字；答錯＝輕搖（≤180ms）+ 紅 + ✗ + 正解卡（見 `references/feedback-recipes.md`）
- **階段回饋**：XP 進帳要在**同一畫面**看到數字或進度條變化；解鎖要有「新東西出現」的視覺，不只是文字提示

### 4. 實作硬規約（DOM / CSS 為主，兩種底盤都適用）

- 只動 `transform` / `opacity`（可合成，不觸發 layout / paint）；**不要**動 `width` / `top` / `box-shadow` 做動畫
- 動畫用 CSS `transition` / `animation`；需要數值連續變化（XP 跑動）才用 `requestAnimationFrame`
- 同時進行的動畫元素控制在 **~20 個以內**（低階機會掉幀）
- 動畫不得改變版面尺寸（避免周邊元素跳動）
- Vue 底盤：動畫狀態**不要**寫進 state machine（state machine 是 pure）；用 view 內的本機 state 或 CSS class
- 純靜態底盤：用 class toggle + `transitionend`，不要依賴外部動畫庫 CDN（PWA 離線會壞）

### 5. 音效（可選，且預設不依賴）

- 預設**克制或關閉**；提供開關並記進進度物件
- 用 WebAudio 短音（合成）優於載入音檔（PWA 快取 + 檔案大小）
- **音效不承載必要資訊**：關掉音效後所有資訊仍可取得
- 不要在錯誤回饋放刺耳音（會讓學生怕答錯）

### 6. 量測（不能靠目測）

- 回饋延遲：用 DevTools Performance 或 `performance.now()` 打點實測，不靠體感
- 動畫時長：量實際 duration（含 CSS 排隊）
- 手機基準：以「中低階手機 × 4x CPU throttle」跑一次，看有沒有掉幀
- 至少跑一次**灰階截圖**（判斷對錯是否仍可辨識）

### 7. 驗收

- **無回饋的操作清單 = 0**（第 1 步的表沒有空白格）
- **對錯差異測試**：轉成灰階後，答對 / 答錯仍能一眼分辨
- **reduced-motion 測試**：開啟系統設定後，資訊仍完整（只少了動態，不少資訊）
- **關音效測試**：關掉後資訊仍完整
- **連答測試**：連續快速作答 5 題，不被動畫拖慢、不遺漏回饋、不卡輸入
- **中低階手機測試**：4x CPU throttle 下沒有明顯掉幀

## 反模式（禁止）

- ❌ **用動畫掩蓋沒講清楚的概念** —— 動畫不等於教學；學生看得開心但答不出來就是失敗
- ❌ **阻斷式獎勵**（每次答對都播 2 秒動畫、要等它播完才能繼續）→ 連答被拖慢，學生開始煩躁
- ❌ **只靠顏色**傳達對錯
- ❌ **每題都放煙火** —— 慶祝強度與成果不成比例會邊際遞減；小成果用小回饋，里程碑才用大回饋
- ❌ **與「快」掛鉤的回饋**（連擊、速度徽章、倒數條）出現在理解階段 —— 與 `learning-mechanics` 的限時規約衝突，會訓練猜測
- ❌ 音效 / 動畫作為**必要**資訊通道（關掉就聽不懂、看不懂）
- ❌ 為了特效引入重量級依賴（在 PWA 離線與低階手機上都會付代價）

## Output contract

交付時要附：

- 回饋時刻表（每個狀態改變 → 對應回饋），無空白格
- 三層回饋的實作方式（微 / 即時 / 階段）
- 實測數據：回饋延遲、動畫時長、4x CPU throttle 結果
- 四項測試結果：灰階可辨識、reduced-motion、關音效、連答 5 題
- 用一句話回答：**「這個回饋讓學生更清楚哪一件因果關係？」** 答不出來就砍掉它

## Routing

- 該選哪個機制、機制是否安全 → `learning-mechanics`
- 課程骨架、demo 直覺化、事實審查 → `progressive-learning-site`
- 需要 3D / WebGL / 粒子系統或換渲染引擎 → `game-studio`（先確認真的需要）
- 專案既有決策優先：以該 repo 的 `CONTEXT.md` / `ROADMAP.md` 為準
