# Components — copy-paste starting points

All of these are the versions that survived real debugging. Extend them, do not re-derive
them. Markup assumes a page whose shell is: topbar → scale map → one `<section class="panel">`
per lens → Q&A → sources.

Global conventions: `C` is a colour object `{mint,coral,amber,peri,sky}`; `$` and `$$` are
`querySelector`/`querySelectorAll`; `REDUCED` is `matchMedia('(prefers-reduced-motion: reduce)').matches`.

## 0. The style layer — read this before writing any CSS

**The shell is style-agnostic. All visual personality lives in the `:root` block below.**
Choose the style with the user (see `styles.md` §3) *before* generating imagery, then paste
that style's `:root` over this one. Do not edit any other rule to re-skin the page.

**Never hardcode a hue in a component.** `rgba(72,224,189,.06)` is one style's mint, and it
breaks the moment a different style is chosen. Everything below is a token on purpose.

```css
:root{ /* ── BASE TOKENS. Replace this block wholesale with a style from styles.md. ── */
  --bg:#0A0E14; --bg2:#10161F; --card:#141B26; --line:#1E2836; --line2:#2E3D4F;
  --txt:#E6EDF5; --txt2:#93A5B8; --txt3:#6A7E96;
  --mint:#FFC44D; --coral:#FF5C5C; --amber:#48E0BD; --peri:#8B7BFF; --sky:#4DD0E1;
  --on-accent:#0A0E14;          /* text sitting ON a --mint fill */
  --radius:6px;
  --font-display:"Space Grotesk","Noto Sans TC",sans-serif;
  --font-body:"Noto Sans TC",system-ui,sans-serif;
  --font-mono:"JetBrains Mono",ui-monospace,monospace;
  --bar-h:58px;
}

/* ── DERIVED TOKENS. Keep this block byte-identical in every build. ──
   These are a pure function of the base tokens, so they belong in ONE shared place.
   A style that redefines only some of them leaves the rest unset and the components
   that use them lose their surfaces *silently* — the topbar, tooltip and lightbox all
   vanish. Never move these into a style block. If a tone the base set cannot express is
   needed, add it HERE, not per style. */
:root{
  --mint-a12: color-mix(in srgb, var(--mint) 12%, transparent);
  --mint-a30: color-mix(in srgb, var(--mint) 30%, transparent);
  --coral-a30:color-mix(in srgb, var(--coral) 30%, transparent);
  --amber-a10:color-mix(in srgb, var(--amber) 10%, transparent);
  --shade:     color-mix(in srgb, var(--bg) 72%, transparent);
  --shade-deep:color-mix(in srgb, var(--bg) 93%, transparent);
  --veil:      color-mix(in srgb, var(--bg) 94%, transparent);
  --txt-a05:   color-mix(in srgb, var(--txt)  5%, transparent);
  --txt-a12:   color-mix(in srgb, var(--txt) 12%, transparent);
}
```

The `C` object mirrors the tokens, so JS reads the same palette the CSS does:

```js
const css=getComputedStyle(document.documentElement);
const C=Object.fromEntries(['mint','coral','amber','peri','sky']
  .map(k=>[k,css.getPropertyValue('--'+k).trim()]));
```

`color-mix()` needs Chrome 111 / Safari 16.2 / Firefox 113. For older targets, write
resolved `rgba()` literals into the `:root` block — never back into a component.

**Five accents, always** (`--mint --coral --amber --peri --sky`). Components are
position-agnostic about which hue is which, so a style may re-map them freely — that is
how you give a political page blue/green parties on a neutral sheet.

**Before shipping, assert contrast rather than eyeballing it:**

```js
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
R.contrast_on   = ratio(v('--on-accent'), v('--mint')) >= 4.5 ? 'ok' : '❌ '+ratio(v('--on-accent'),v('--mint')).toFixed(2);
```

Light styles fail this most often. If `--on-accent` does not clear 4.5:1 against `--mint`,
re-map `--mint` or set `--on-accent` by hand — never leave it to `color: white`.

---

## 1. Visual stage (image + caption + hotspots)

The workhorse. Hotspots are absolutely-positioned buttons; `left/top` are percentages of the
image box, so they survive responsive layout.

```html
<figure class="vstage vstage-hero rv" data-img="img/thing.webp"
        data-cap="Caption text shown in the lightbox too.">
  <picture>
    <source srcset="img/thing-sm.webp" media="(max-width:760px)">
    <img src="img/thing.webp" alt="descriptive alt" loading="lazy" decoding="async">
  </picture>
  <button class="vzoom" type="button" aria-label="放大檢視">⤢</button>
  <button class="vhot" style="left:34%;top:30%" data-t="What this spot is"></button>
  <button class="vhot" style="left:60%;top:64%" data-t="What this spot is"></button>
  <div class="vcap">Caption text shown under the image.</div>
</figure>
```

```css
.vstage{position:relative;margin:20px 0 0;border:1px solid var(--line);border-radius:18px;
  overflow:hidden;background:linear-gradient(160deg,var(--mint-a12),var(--shade))}
.vstage img{display:block;width:100%;height:auto}
.vstage.vstage-hero img{max-height:min(58vh,560px);object-fit:cover}
.vcap{padding:13px 17px;font-size:13.2px;color:var(--txt2);line-height:1.7;
  background:var(--shade);border-top:1px solid var(--line)}
.vzoom{position:absolute;top:10px;right:10px;width:34px;height:34px;border-radius:9px;
  border:1px solid var(--line2);background:var(--shade-deep);color:var(--txt2);cursor:pointer}
.vhot{position:absolute;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;
  border:2px solid var(--mint);background:var(--mint-a30);cursor:pointer;transition:.2s;z-index:3}
.vhot::after{content:"";position:absolute;inset:6px;border-radius:50%;background:var(--mint)}
.vhot::before{content:"";position:absolute;inset:-6px;border-radius:50%;border:1px solid var(--mint);
  opacity:.55;animation:vhot 2.3s ease-out infinite}
@keyframes vhot{0%{transform:scale(.7);opacity:.8}100%{transform:scale(1.9);opacity:0}}
.vhot:hover,.vhot.on{background:var(--mint);transform:scale(1.14)}
@media(max-width:720px){.vhot{width:25px;height:25px;margin:-12.5px 0 0 -12.5px}}
```

**Hotspot coordinates must be read off the actual generated image.** Generate, open the
image, look at it, place the dots. Guessing percentages puts labels on empty space.

---

## 2. Hotspot tooltip (hover = preview, click = pin)

`position:fixed` + viewport coordinates. Using coordinates relative to the image while the
tooltip is anchored to `<body>` throws it off-screen as soon as the page scrolls.

```js
const tip=document.createElement("div"); tip.className="vtip"; document.body.appendChild(tip);
let pinned=null;
function place(btn){
  tip.innerHTML=btn.dataset.t; tip.classList.add("on");
  const br=btn.getBoundingClientRect(), tw=tip.offsetWidth, th=tip.offsetHeight;
  let x=Math.max(10,Math.min(innerWidth-tw-10, br.left+br.width/2-tw/2));
  let y=br.top-th-14;
  if(y<10) y=Math.min(innerHeight-th-10, br.bottom+14);
  tip.style.left=Math.round(x)+"px"; tip.style.top=Math.round(y)+"px";
}
const close=()=>{ if(pinned)pinned.classList.remove("on"); pinned=null; tip.classList.remove("on"); };
addEventListener("pointerover",e=>{ const b=e.target.closest(".vhot"); if(!b)return;
  b.classList.add("on"); if(pinned&&pinned!==b){pinned.classList.remove("on");pinned=b;} place(b); });
addEventListener("pointerout",e=>{ const b=e.target.closest(".vhot"); if(!b||pinned===b)return;
  b.classList.remove("on"); if(!pinned)tip.classList.remove("on"); });
addEventListener("click",e=>{ const b=e.target.closest(".vhot");
  if(b){ e.stopPropagation();
    if(pinned===b){ b.classList.remove("on"); pinned=null; tip.classList.remove("on"); }
    else { if(pinned)pinned.classList.remove("on"); pinned=b; b.classList.add("on"); place(b); }
    return; }
  if(!e.target.closest(".vtip")) close(); });
addEventListener("keydown",e=>{ if(e.key==="Escape") close(); });
let raf=0;
addEventListener("scroll",()=>{ if(!pinned)return; cancelAnimationFrame(raf);
  raf=requestAnimationFrame(()=>{ if(pinned)place(pinned); }); },{passive:true});
```

```css
.vtip{position:fixed;z-index:300;max-width:min(320px,calc(100vw - 32px));padding:11px 14px;
  border-radius:11px;background:var(--shade-deep);border:1px solid var(--mint);
  font-size:12.8px;line-height:1.6;pointer-events:none;opacity:0;transform:translateY(4px);
  transition:.18s;box-shadow:0 12px 30px -10px var(--txt-a12)}
.vtip.on{opacity:1;transform:none}
```

---

## 3. Comparison slider — needs TWO different images

```html
<figure class="vstage vstage-hero vcompare rv" data-img="img/state-b.webp" data-cap="…">
  <div class="cmp" id="cmpX" style="--x:50%">
    <img class="cmp-a" src="img/state-b.webp" alt="B 狀態">
    <img class="cmp-b" src="img/state-a.webp" alt="A 狀態">
    <div class="cmp-line"><i></i></div>
    <span class="cmp-l cmp-lt">A</span><span class="cmp-l cmp-rt">B</span>
  </div>
  <div class="vcap">拖動中間的分割線比較 A 與 B。</div>
</figure>
```

```css
.vcompare .cmp{position:relative;overflow:hidden;touch-action:none;cursor:ew-resize;user-select:none}
.vcompare img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.vcompare .cmp-a{position:relative}
.vcompare .cmp-b{clip-path:inset(0 calc(100% - var(--x)) 0 0)}
.vcompare .cmp-line{position:absolute;top:0;bottom:0;left:var(--x);width:2px;background:var(--txt);
  box-shadow:0 0 14px var(--txt-a12);pointer-events:none}
.vcompare .cmp-line i{position:absolute;top:50%;left:50%;width:38px;height:38px;margin:-19px 0 0 -19px;
  border-radius:50%;background:var(--txt);box-shadow:0 4px 16px var(--shade-deep)}
.vcompare .cmp-l{position:absolute;top:12px;font-size:11.5px;font-weight:800;padding:5px 12px;
  border-radius:99px;background:var(--shade-deep)}
.vcompare .cmp-lt{left:12px;color:var(--mint);border:1px solid var(--mint-a30)}
.vcompare .cmp-rt{right:12px;color:var(--coral);border:1px solid var(--coral-a30)}
```

Drag handling — listen on `window`, not the element, and suppress the click that follows a
drag so the lightbox does not hijack it:

```js
const c=$("#cmpX"); let drag=false,moved=false,sx=0;
const set=t=>c.style.setProperty("--x",Math.max(0,Math.min(100,t))+"%");
c.addEventListener("pointerdown",e=>{drag=true;moved=false;sx=e.clientX;
  try{c.setPointerCapture(e.pointerId)}catch(_){} set((e.clientX-c.getBoundingClientRect().left)/c.getBoundingClientRect().width*100); e.preventDefault();});
addEventListener("pointermove",e=>{ if(!drag)return;
  if(Math.abs(e.clientX-sx)>3) moved=true;
  set((e.clientX-c.getBoundingClientRect().left)/c.getBoundingClientRect().width*100); },{passive:true});
addEventListener("pointerup",()=>{ if(drag&&moved){ c.dataset.dragged="1"; setTimeout(()=>c.dataset.dragged="0",60);} drag=false; });
```

---

## 4. Lightbox

```js
const lb=$("#lb"), im=$("#lbImg"), cap=$("#lbCap");
addEventListener("click",e=>{
  const f=e.target.closest(".vstage[data-img]"); if(!f) return;
  if(e.target.closest(".vhot")) return;                 // hotspot handles its own click
  if(f.dataset.dragged==="1") return;                   // just finished a comparator drag
  if(e.target.closest(".vplayer")) return;              // player has its own logic
  im.src=f.dataset.img; im.alt=(f.dataset.cap||"").replace(/<[^>]+>/g,"");
  cap.innerHTML=f.dataset.cap||""; lb.classList.add("on"); document.body.style.overflow="hidden";
});
const close=()=>{ lb.classList.remove("on"); document.body.style.overflow=""; };
$("#lbX").addEventListener("click",close);
lb.addEventListener("click",e=>{ if(e.target===lb) close(); });
addEventListener("keydown",e=>{ if(e.key==="Escape") close(); });
```

```css
.lb{position:fixed;inset:0;z-index:200;background:var(--veil);backdrop-filter:blur(10px);
  display:none;place-items:center;padding:3vh 3vw}
.lb.on{display:grid}
.lb img{max-width:100%;max-height:90vh;object-fit:contain;border-radius:12px}
.lb-x{position:absolute;top:16px;right:16px;width:42px;height:42px;border-radius:11px;
  border:1px solid var(--line2);background:var(--txt-a12);color:var(--txt);cursor:pointer;font-size:19px}
.lb-cap{position:absolute;left:0;right:0;bottom:16px;text-align:center;color:var(--txt2);font-size:13.5px;padding:0 5vw}
```

---

## 5. Video player with a custom play button

Do not set `controls` in markup — it double-renders with the custom button and can suppress
the poster. Enable it on first play.

```html
<figure class="vstage vplayer rv" data-img="img/clip-poster.jpg">
  <div class="vp-wrap">
    <video src="video/clip-720.mp4" poster="img/clip-poster.jpg" preload="metadata" playsinline></video>
    <button class="vp-play" type="button" aria-label="播放影片"><span>▶</span></button>
  </div>
  <div class="vcap">10 秒動態版。</div>
</figure>
```

```js
$$(".vplayer").forEach(fig=>{
  const wrap=$(".vp-wrap",fig), v=$("video",fig), btn=$(".vp-play",fig);
  btn.addEventListener("click",e=>{ e.stopPropagation(); v.controls=true;
    wrap.classList.add("playing"); v.play().catch(()=>{}); });
  v.addEventListener("click",()=>{ if(v.paused){v.play().catch(()=>{}); wrap.classList.add("playing");} else v.pause(); });
  v.addEventListener("ended",()=>wrap.classList.remove("playing"));
});
```

```css
.vp-wrap{position:relative;background:var(--bg)}
.vp-wrap video{display:block;width:100%;height:auto;max-height:min(56vh,520px);object-fit:cover}
.vp-play{position:absolute;inset:0;margin:auto;width:74px;height:74px;border-radius:50%;
  border:1px solid var(--txt-a12);background:var(--shade);backdrop-filter:blur(8px);
  color:var(--txt);font-size:26px;cursor:pointer;display:grid;place-items:center;transition:.2s}
.vp-play:hover{background:var(--mint);color:var(--on-accent);transform:scale(1.07)}
.vp-wrap.playing .vp-play{opacity:0;pointer-events:none}
```

**Check the poster path has its extension.** A missing `.jpg` yields a black rectangle and
one 404 that is easy to miss.

---

## 6. Scale map — why the lenses differ

Turns a tab bar into a statement about the topic. Bands are deliberately allowed to
overlap; overlap is the point (the topics genuinely interleave).

```js
const LM_MIN=-9, LM_MAX=0.5;                       // log10 metres at the ends
const lmXlog=lg=>6+(Math.max(LM_MIN,Math.min(LM_MAX,lg))-LM_MIN)/(LM_MAX-LM_MIN)*88;
const lmX=v=>lmXlog(Math.log10(v));                // metres → percent
const LENS=[{id:"a",icon:"🌫",name:"空間",tag:"1 m → 1 µm",lo:1e-6,hi:1,c:C.mint}, /* … */ ];
$("#lensMap").innerHTML = LENS.map(l=>
  `<div class="lmrow" data-lens="${l.id}" style="color:${l.c}">
     <span class="lm-name">${l.icon}${l.name}</span>
     <span class="lm-track"><i class="lm-bar" style="left:${lmX(l.lo)}%;width:${Math.max(2.2,lmX(l.hi)-lmX(l.lo))}%"></i></span>
     <span class="lm-tag">${l.tag}</span></div>`).join("")
  + `<div class="lm-axis">${[1e-9,1e-6,1e-3,1].map(v=>
     `<i style="left:${lmX(v)}%"></i><span style="left:${lmX(v)}%">…</span>`).join("")}</div>`;
```

For lenses that are not spatial (a "state of play" / "today" lens), give the row a dashed
full-width bar and say in the caption that it is not a spatial scale — do not fake a band.

---

## 7. Text collapse — visual-first, text one click away

Auto-flag long paragraphs at init so the HTML stays readable and every card is covered.

```js
$$(".card p, .psim-hint, .sources li").forEach(el=>{
  if(el.textContent.trim().length>78 && !el.querySelector("a")) el.classList.add("long");
});
```

```css
body.t-light .long{position:relative;max-height:4.6em;overflow:hidden;cursor:pointer;
  mask-image:linear-gradient(180deg,#000 62%,transparent 100%);  /* alpha-only: safe on any bg */
body.t-light .long.open{max-height:none;overflow:visible;cursor:default;mask-image:none}
body.t-light .long::after{content:"⋯ 點擊展開";position:absolute;right:0;bottom:0;font-size:11.5px;
  color:var(--mint);background:linear-gradient(90deg,transparent,var(--bg) 30%);padding-left:34px}
body.t-light .long.open::after{content:""}
```

A topbar button toggles `body.t-light` and flips its own label. Default **on** — that is the
reader's stated preference.

---

## 8. Panel switching

Hidden panels report `offsetTop === 0`, so the scroll target must be computed from the
live rect.

```js
$$(".lens-btn").forEach(b=>b.addEventListener("click",()=>{
  $$(".lens-btn").forEach(x=>x.classList.remove("on"));
  $$(".panel").forEach(x=>x.classList.remove("on"));
  b.classList.add("on");
  const p=$("#p-"+b.dataset.lens); p.classList.add("on");
  p.querySelectorAll(".rv").forEach(e=>e.classList.add("in"));
  const top=p.getBoundingClientRect().top+scrollY-70;
  scrollTo({top:Math.max(0,top),behavior:REDUCED?"auto":"smooth"});
}));
```

## 9. Layout gotcha

Grid items stretch to the tallest sibling by default, so a short visual beside a tall
portrait one leaves a large void. Add `align-items:start` to that grid.

## 10. Canvas/loop lifecycle

Pause when off-screen and when the panel is hidden; an IntersectionObserver that
unconditionally stops on first fire will kill a loop started during init.

```js
new IntersectionObserver(es=>es.forEach(e=>{
  if(e.isIntersecting) start(); else if(scrollY>40) stop();
}),{threshold:0.05}).observe(el);
```
