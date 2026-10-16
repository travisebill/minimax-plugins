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

// 5b. STYLE: contrast must be checked, never eyeballed (components.md §0).
// Return verdicts, not ratios — a ratio nobody compares is just a number.
R.style = await pg.evaluate(() => {
  const v = k => getComputedStyle(document.documentElement).getPropertyValue(k).trim();
  // Parse hex AND rgb(). `\d+` is NOT enough — "#FFFFFF" has no digits at all and
  // crashes match(). Return null on anything unparseable so a bad token FAILS the
  // assertion instead of throwing out of the whole harness.
  const lum = c => {
    c = String(c).trim();
    let r, g, b;
    const hex = c.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
    if (hex) {
      let h = hex[1];
      if (h.length === 3) h = h[0]+h[0] + h[1]+h[1] + h[2]+h[2];
      r = parseInt(h.slice(0,2),16); g = parseInt(h.slice(2,4),16); b = parseInt(h.slice(4,6),16);
    } else {
      const n = c.match(/[\d.]+/g);
      if (!n) return null;
      [r, g, b] = n.slice(0,3).map(Number);
    }
    const f = x => { x /= 255; return x <= .03928 ? x/12.92 : Math.pow((x+.055)/1.055, 2.4); };
    return .2126*f(r) + .7152*f(g) + .0722*f(b);
  };
  const ratio = (a, b) => {
    const x = lum(a), y = lum(b);
    if (x === null || y === null) return null;
    return (Math.max(x,y) + .05) / (Math.min(x,y) + .05);
  };
  const test = (a, b, min) => {
    const r = ratio(v(a), v(b));
    if (r === null) return `UNPARSEABLE ${a}=${v(a)} — FAIL`;
    return `${r.toFixed(2)}:1 ${r >= min ? 'ok' : '*** FAIL (need ' + min + ')'}`;
  };
  return {
    style: document.documentElement.dataset.style || '(unnamed)',
    'txt/bg':     test('--txt','--bg',7),
    'txt3/bg':    test('--txt3','--bg',4.5),
    'on/mint':    test('--on-accent','--mint',4.5),
    accents: ['--mint','--coral','--amber','--peri','--sky'].filter(k => v(k)).length + '/5'
             + (['--mint','--coral','--amber','--peri','--sky'].every(k => v(k)) ? ' ok' : ' *** FAIL'),
  };
});

// 5c. STYLE LEAK: no component may carry a raw hue.
//
// Three traps this must avoid, all of which produce false alarms:
//   1. custom properties return their DECLARED text, so you cannot string-match a
//      `color-mix(...)` token. Apply each token to a probe and read it back.
//   2. Chrome serialises the SAME colour differently per property — `color-mix()` in
//      `background-color` comes back `rgba(...)` but in `border-color` it comes back
//      `color(srgb ...)`. Compare parsed channels, never strings.
//   3. `background-image` gradients are composite strings, so the value never equals
//      any single token. Extract each colour function and test those.
R.styleLeak = await pg.evaluate(() => {
  const KEYS = ['--mint','--coral','--amber','--peri','--sky','--bg','--bg2','--card',
                '--txt','--txt2','--txt3','--line','--line2','--on-accent','--amber-a10',
                '--mint-a12','--mint-a30','--coral-a30','--shade','--shade-deep','--veil',
                '--txt-a05','--txt-a12'];
  const parse = c => {
    c = String(c).trim();
    let m = c.match(/^color\(srgb ([\d.]+) ([\d.]+) ([\d.]+)(?:\s*\/\s*([\d.]+))?\)$/);
    if (m) return [+m[1]*255, +m[2]*255, +m[3]*255, m[4] === undefined ? 1 : +m[4]];
    m = c.match(/^rgba?\(([^)]+)\)$/);
    if (m) { const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
             return [p[0], p[1], p[2], p[3] === undefined ? 1 : p[3]]; }
    return null;
  };
  const key = c => { const p = parse(c); return p ? p.map(n => Math.round(n)).join(',') : null; };

  // resolve every token under BOTH a background and a border, to capture both serialisations
  const probe = document.createElement('i');
  probe.style.cssText = 'position:absolute;width:0;height:0;opacity:0';
  document.body.appendChild(probe);
  const ok = new Set();
  for (const k of KEYS) {
    for (const prop of ['backgroundColor','borderTopColor']) {
      probe.style[prop] = '';
      probe.style[prop] = `var(${k})`;
      const v = getComputedStyle(probe)[prop];
      if (v && v !== 'rgba(0, 0, 0, 0)' && v !== 'transparent') { const kk = key(v); if (kk) ok.add(kk); }
    }
  }
  probe.remove();

  // `color` is inherited, so it false-positives on every element — check paint only.
  const PAINT = ['backgroundColor','borderTopColor','borderLeftColor',
                 'borderRightColor','borderBottomColor','backgroundImage'];
  const COLORFN = /(color\(srgb[^)]*\)|rgba?\([^)]*\))/g;
  const bad = [];
  for (const el of document.querySelectorAll('.vstage,.vtip,.card,.chip,.cmp-l,.vhot,.vp-play,.tbl')) {
    const cs = getComputedStyle(el);
    for (const prop of PAINT) {
      const v = cs[prop];
      if (!v || v === 'none' || v === 'transparent' || v === 'rgba(0, 0, 0, 0)') continue;
      if (prop === 'backgroundImage') {
        for (const part of v.match(COLORFN) || []) {
          if (!ok.has(key(part))) bad.push(`${el.className.split(' ')[0]}:gradient ${part}`);
        }
        continue;
      }
      if (!ok.has(key(v))) bad.push(`${el.className.split(' ')[0]}:${prop}=${v}`);
    }
  }
  return { tokensResolved: ok.size, leaks: bad.length ? [...new Set(bad)].slice(0,6) : 'none' };
});
// 5d. the same check at the SOURCE level — a raw hue in a declaration is the real bug,
//     and it survives minification, so grep the css text too
R.styleLeakSource = await pg.evaluate(() => {
  const hits = [];
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch (_) { continue; }   // cross-origin fonts
    const walk = rs => { for (const r of rs) {
      if (r.cssRules) { walk(r.cssRules); continue; }
      if (!r.style) continue;
      const sel = r.selectorText || '';
      if (/:root/.test(sel)) continue;                  // the palette definition itself
      for (const prop of ['color','background','background-color','border','border-top-color',
                          'border-color','outline','box-shadow']) {
        const v = r.style.getPropertyValue(prop);
        if (/(#[0-9a-f]{3,6}\b|rgba?\()/i.test(v)) hits.push(`${sel} { ${prop}:${v} }`);
      }
    }};
    walk(rules);
  }
  return hits.length ? hits.slice(0,6) : 'none';
});

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
| Text is readable | `ratio(--txt,--bg) >= 7` — not "it looked fine" |
| Style system intact | computed component colours ∈ the token set — not "the page looks styled" |
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
