# Verify — the Playwright harness

The single highest-leverage habit in this workflow. Every bug that reached a user was
missed by a test that asserted the wrong thing.

```bash
npx playwright install chromium   # once per environment
```

## The rule

> **Assert on position and pixels, not on classes and text.**
> `.vhot.on` existing with the right text passes while the tooltip renders 3000px above
> the viewport, invisible. Assert the bounding rect is inside the viewport. Screenshot.

## Harness

```js
// verify.mjs
import { chromium } from '/usr/local/lib/node_modules/playwright/index.mjs';
const errs = [];
const b = await chromium.launch();
const pg = await b.newPage({ viewport:{width:1440,height:1000} });
pg.on('pageerror', e => errs.push('ERR:'+e.message));
pg.on('console', m => { if (m.type()==='error' && !/CERT|Failed to load resource/.test(m.text())) errs.push('CON:'+m.text()); });
pg.on('response', r => { if (r.status() >= 400) errs.push('HTTP'+r.status()+' '+r.url().split('/').pop()); });
await pg.goto('file://' + PAGE, { waitUntil:'load' });
await pg.waitForTimeout(1500);

const settle = () => pg.waitForFunction(() => {
  const y = scrollY; return new Promise(r => setTimeout(() => r(Math.abs(scrollY-y) < 1), 200));
}, null, { timeout: 9000 });
const R = {};

// 1. every lens switches AND actually scrolls
for (const l of LENSES) {
  await pg.locator(`.lens-btn[data-lens="${l}"]`).click();
  await pg.waitForTimeout(800); await settle();
  R['scroll_'+l] = await pg.evaluate(() => Math.round(scrollY)) > 300 ? 'ok' : '❌ did not scroll';
  R['panel_'+l] = await pg.locator('.panel.on').count() === 1 ? 'ok' : '❌';
  R['assets_'+l] = await pg.evaluate(() =>
    [...document.querySelectorAll('.panel.on img')].filter(i => i.offsetParent !== null)
      .map(i => i.naturalWidth > 0));                 // every visible image actually decoded
}

// 2. hotspot tooltip is INSIDE the viewport, at depth, after scrolling
await pg.locator('.panel.on .vhot').first().scrollIntoViewIfNeeded();
await pg.evaluate(() => scrollBy(0, -120));             // force an awkward scroll position
const h = pg.locator('.panel.on .vhot').first();
await h.click();
R.tooltip = await pg.evaluate(() => {
  const t = document.querySelector('.vtip');
  if (!t || !t.classList.contains('on')) return '❌ not shown';
  const r = t.getBoundingClientRect();
  return (r.top >= 0 && r.left >= 0 && r.bottom <= innerHeight && r.right <= innerWidth)
    ? 'ok' : '❌ off-screen: ' + JSON.stringify({top:r.top,left:r.left});
});
R.tooltipSurvivesScroll = await (async () => {
  await pg.evaluate(() => scrollBy(0, 200)); await pg.waitForTimeout(500);
  return pg.evaluate(() => { const r = document.querySelector('.vtip').getBoundingClientRect();
    return r.top >= 0 && r.bottom <= innerHeight; });
})();
await pg.screenshot({ path:'shot-tooltip.png' });        // look at it

// 3. every control actually moves its readout
for (const [sel, reads] of CONTROLS) {
  const before = await pg.locator(reads).innerText();
  await pg.locator(sel).fill('0'); await pg.waitForTimeout(300);
  const at0    = await pg.locator(reads).innerText();
  await pg.locator(sel).fill(String(MAXVAL)); await pg.waitForTimeout(300);
  const atMax  = await pg.locator(reads).innerText();
  R[sel] = (before !== at0 && at0 !== atMax) ? 'ok' : `❌ dead control: ${before}|${at0}|${atMax}`;
}

// 4. comparator pixels actually change
const cmpBox = await pg.locator('.cmp').boundingBox();
const px = async (t) => { await pg.mouse.move(cmpBox.x+cmpBox.width*.5, cmpBox.y+cmpBox.height*.5);
  await pg.mouse.down(); await pg.mouse.move(cmpBox.x+cmpBox.width*t, cmpBox.y+cmpBox.height*.5, {steps:14});
  await pg.mouse.up(); await pg.waitForTimeout(300);
  return pg.locator('.cmp').screenshot(); };
const a = await px(0.12), c = await px(0.88);
R.comparator = Buffer.compare(a, c) !== 0 ? 'ok' : '❌ images identical (same file in both layers?)';
R.cmpSrcs = await pg.evaluate(() => [document.querySelector('.cmp-a').src, document.querySelector('.cmp-b').src]);

// 5. animation is alive (two snapshots of canvas alpha must differ)
const sample = () => pg.evaluate(() => { const c=document.querySelector('canvas'), d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
  let s=0,n=0; for(let i=3;i<d.length;i+=400){s+=d[i];n++;} return +(s/n).toFixed(3); });
const p1 = await sample(); await pg.waitForTimeout(1400); const p2 = await sample();
R.animation = p1 !== p2 ? 'ok' : '❌ frozen';

// 6. layout integrity
R.overflowDesktop = await pg.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
const m = await b.newPage({ viewport:{width:390,height:844}, isMobile:true, hasTouch:true });
await m.goto('file://' + PAGE); await m.waitForTimeout(2000);
R.overflowMobile = await m.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
await m.screenshot({ path:'shot-mobile.png' });

R.errs = errs;
console.log(JSON.stringify(R, null, 1));
await b.close();
```

## Assertion recipes

| Want to prove | Assert this — not this |
|---|---|
| Tooltip is visible | `rect.top >= 0 && rect.bottom <= innerHeight` — not `.classList.contains('on')` |
| Comparator works | screenshot buffers differ — not `getComputedStyle(...).clipPath` alone |
| Canvas animates | two pixel samples differ — not `requestAnimationFrame` was called |
| A control is alive | readout text differs at min vs max — not "the handler was attached" |
| Images load | `naturalWidth > 0` on every visible `<img>` — not that the `<img>` tag exists |
| Page didn't break | `errs` empty including 404s — not just no `pageerror` |
| Lens switch works | `scrollY` actually changed — not the tab has class `on` |

## Post-deploy

Playwright cannot reach the deployed host in every environment (TLS trust). Fall back:

```bash
curl -sSL -o live.html -w "HTTP %{http_code} %{size_download}B\n" "$URL"
grep -c 'class="vhot"' live.html
for u in img/a.webp img/b.webp video/c.mp4; do
  curl -sS -o /dev/null -w "$u HTTP %{http_code}\n" "$BASE/$u"; done
```

A 200 on the page alone proves nothing about its assets.

## When a user says "it doesn't respond"

1. Reproduce it in the harness
2. **Screenshot the failure** — the bug is often visible and was invisible in the DOM
3. Read the *computed* styles and the live rect, not the source
4. Only then theorise
5. Re-verify the same way. Never declare a fix on the strength of "the class is now set".
