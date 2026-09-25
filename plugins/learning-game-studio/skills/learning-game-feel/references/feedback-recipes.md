# 回饋 recipe（learning-game-feel）

可直接貼用的最小實作。**時長是經驗值**，上線前要在中低階手機實測覆蓋（見 §7 量測清單）。

所有動畫只動 `transform` / `opacity`，不觸發 layout / paint。

---

## 1. 微回饋（按下 / 懸停）

```css
.opt { transition: transform 90ms ease, background-color 90ms ease; }
.opt:hover { background: #f1f5f9; }
.opt:active { transform: translateY(1px); }
```

判準：按下去「有感覺」。1–2px 就夠，不要做成按鈕跳起來。

## 2. 答對

```css
@keyframes correct-pulse {
  0%   { transform: scale(1); }
  40%  { transform: scale(1.06); }
  100% { transform: scale(1); }
}
.opt-correct {
  animation: correct-pulse 320ms ease-out;
  border: 2px solid #16a34a;
  background: #f0fdf4;
}
```

三個通道同時給：**顏色**（綠框）+ **圖示**（✓，放 markup）+ **文字**（「答對了」）。動畫只是加分，不是資訊本身。

## 3. 答錯

```css
@keyframes wrong-shake {
  0%, 100% { transform: translateX(0); }
  25%      { transform: translateX(-5px); }
  75%      { transform: translateX(5px); }
}
.opt-wrong {
  animation: wrong-shake 180ms ease-in-out;
  border: 2px solid #dc2626;
  background: #fef2f2;
}
```

- 幅度小（5px）、時間短（≤180ms）：**錯誤回饋不該像懲罰**
- 不要用刺耳音效
- 錯誤回饋結束後，正解卡**緊接出現**（不要等動畫播完才開始載入）

## 4. 正解卡（解釋，不阻斷）

- 放在選項**下方**原地展開，不要用 modal / 彈窗（彈窗會擋住題目，學生無法對照）
- 內容順序：`你的答案 → 正解 → 為什麼`（先指出差異，再給理由）
- 展開用 CSS `grid-template-rows: 0fr → 1fr` 或 `max-height` transition（純 `transform` 做不到高度變化；接受一次 layout，但只做一次、且元素小）
- 若專案已用分層提示（`progressive-learning-site` §3），把提示層級接在這裡，**不要**用回饋取代提示

## 5. XP 進帳（數值跑動）

```js
function tweenXP(el, from, to, duration = 480) {
  const t0 = performance.now()
  const step = (now) => {
    const p = Math.min(1, (now - t0) / duration)
    const eased = 1 - Math.pow(1 - p, 3) // easeOutCubic
    el.textContent = String(Math.round(from + (to - from) * eased))
    if (p < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}
```

- 時長 ≤600ms；跑動期間**不鎖**任何按鈕
- 進度條與數字**同時**動（兩個通道），不要只有數字跳
- 若 XP 因重試而遞減（見 `learning-mechanics`），結算時要**說明原因**，不要只是數字變小

## 6. 解鎖（階段回饋）

```css
@keyframes unlock-pop {
  0%   { transform: scale(0.85); opacity: 0; }
  60%  { transform: scale(1.03); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}
.unlock-card { animation: unlock-pop 480ms cubic-bezier(.2, .8, .2, 1) both; }
```

- 解鎖必須讓「新東西出現」看得見（新卡片 / 新關卡入口），不是只跳一行文字
- 大回饋留給里程碑（完成一章、解鎖新關卡）；小成果用小回饋

## 7. reduced-motion 降級

```css
@media (prefers-reduced-motion: reduce) {
  .opt-correct,
  .opt-wrong,
  .unlock-card { animation: none; }
  .xp-bar-fill { transition: none; }
}
```

關鍵：**顏色、圖示、文字要寫在 class 上而不是 keyframes 裡**，這樣關掉動畫後資訊仍然完整。關掉動畫後跑一次灰階截圖，確認答對 / 答錯仍可分辨。

## 8. 音效（可選、可關）

```js
let ctx
let soundEnabled = false // 預設關；使用者開啟後記進進度物件

function blip(freq = 660, ms = 90, gain = 0.04) {
  if (!soundEnabled) return
  ctx ??= new AudioContext()
  if (ctx.state === 'suspended') ctx.resume() // 瀏覽器要求先有使用者互動
  const osc = ctx.createOscillator()
  const g = ctx.createGain()
  osc.frequency.value = freq
  g.gain.value = gain
  osc.connect(g).connect(ctx.destination)
  osc.start()
  g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + ms / 1000)
  osc.stop(ctx.currentTime + ms / 1000)
}
```

- 合成短音優於音檔：PWA 快取小、無額外請求
- **音效不承載必要資訊**：關掉後所有資訊仍可取得
- 錯誤音要柔和（低音量、不刺耳），避免學生怕答錯

## 9. 量測清單（不能靠目測）

| 項目 | 怎麼量 | 通過標準 |
|---|---|---|
| 回饋延遲 | `performance.now()` 在 dispatch 前後打點，或 DevTools Performance | ≤100ms |
| 動畫時長 | DevTools Performance 看實際 duration | 慶祝類 ≤600ms |
| 灰階可辨識 | DevTools → Rendering → Emulate vision deficiencies → **Achromatopsia** | 答對 / 答錯仍可一眼分辨 |
| reduced-motion | 系統設定開啟後重跑，或 DevTools Rendering → prefers-reduced-motion | 資訊完整，只少動態 |
| 中低階手機 | DevTools Performance → CPU **4x slowdown**（或 `emulate` cpuThrottlingRate: 4） | 無明顯掉幀、無長任務 |
| 連答 | 連按 5 次作答 | 不被動畫拖慢、回饋不漏、輸入不卡 |

## 10. 反例對照（同樣的機制，乾 vs 有回饋）

| 情境 | 乾（現況常見） | 有回饋 |
|---|---|---|
| 送出答案 | 選項無變化，兩秒後換下一題 | 選項立刻變色 + 圖示 + 文字；解釋原地展開 |
| 拿到 XP | 數字直接跳成新值 | 數字跑動 + 進度條同步前進 + 說明有無遞減 |
| 解鎖關卡 | 地圖上多一行文字 | 新關卡卡片彈出 + 可點擊入口 |
| 答錯 | 只變紅 | 變紅 + 輕搖 + 指出差異 + 為什麼 |
