#!/usr/bin/env node
// The last pass's checks, so they are not done by eye. Needs a Playwright package that Node can find.
// With no Playwright, use your browser testing skill or tool (for example buu) instead.
//
//   node check.mjs <url | file.html>
//
// Loads the page at 390, 768 and 1440 wide and reports: console errors, sideways scrolling, the heading outline,
// images without alt text, links that go nowhere, how many different actions the first screen asks for, whether
// keyboard focus can be seen, and what still moves (long or endless animations, and what is left when the visitor
// has asked for reduced motion). It prints PASS, WARN or FAIL per line and exits 1 if anything failed.
import path from 'node:path';

const target = process.argv[2];
if (!target) { console.error('usage: node check.mjs <url | file.html>'); process.exit(2); }
async function loadPlaywright() {      // from the project you run this in, or anywhere Node can find it
  try { return await import('playwright'); } catch { /* try require, which also honours NODE_PATH */ }
  const { createRequire } = await import('node:module');
  for (const from of [process.cwd() + '/', import.meta.url]) { try { return createRequire(from)('playwright'); } catch { /* next */ } }
  return null;
}
const pw = await loadPlaywright();
if (!pw) { console.error('Playwright not found. Use your browser testing skill or tool (for example buu) instead.'); process.exit(2); }
const url = /^https?:/.test(target) ? target : 'file://' + path.resolve(target);
const browser = await pw.chromium.launch();
let failed = 0;
const say = (level, what, detail = '') => { if (level === 'FAIL') failed++; console.log(`${level.padEnd(4)}  ${what}${detail ? '\n      ' + detail : ''}`); };
const short = (list, n = 5) => list.slice(0, n).join(' | ') + (list.length > n ? ` (+${list.length - n} more)` : '');

console.log(`\nUnslop check: ${target}\n`);

// --- at three widths: errors and sideways scroll
for (const width of [390, 768, 1440]) {
  const pg = await browser.newPage({ viewport: { width, height: 900 } });
  const errors = [];
  pg.on('pageerror', e => errors.push(String(e).split('\n')[0]));
  pg.on('console', m => { if (m.type() === 'error') errors.push(m.text().split('\n')[0]); });
  await pg.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(e => errors.push('did not load: ' + String(e).split('\n')[0]));
  await pg.waitForTimeout(800);
  const over = await pg.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  say(over > 1 ? 'FAIL' : 'PASS', `${width} px wide: ${over > 1 ? `scrolls sideways by ${over} px` : 'fits'}`);
  if (width === 1440) say(errors.length ? 'FAIL' : 'PASS', `console: ${errors.length ? errors.length + ' error(s)' : 'no errors'}`, short(errors, 3));
  await pg.close();
}

// --- structure, at desktop width
const pg = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await pg.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
await pg.waitForTimeout(800);
const info = await pg.evaluate(() => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const heads = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(vis).map(h => ({ level: +h.tagName[1], text: h.textContent.trim().replace(/\s+/g, ' ').slice(0, 50) }));
  const noAlt = [...document.images].filter(i => vis(i) && !i.hasAttribute('alt')).map(i => (i.currentSrc || i.src).split('/').pop().slice(0, 40));
  const dead = [...document.querySelectorAll('a')].filter(vis).filter(a => { const h = a.getAttribute('href'); return h === null || h === '' || h === '#' || /^javascript:/i.test(h); }).map(a => a.textContent.trim().replace(/\s+/g, ' ').slice(0, 30) || '(no text)');
  const first = [...document.querySelectorAll('a,button,[role=button],input[type=submit]')].filter(vis).filter(e => { const r = e.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; });
  const looksLikeButton = e => { const s = getComputedStyle(e), bg = s.backgroundColor; return e.tagName !== 'A' || (bg && !/rgba?\(0, 0, 0, 0\)|transparent/.test(bg)) || parseFloat(s.borderTopWidth) > 0; };
  const actions = [...new Set(first.filter(looksLikeButton).map(e => (e.textContent || e.value || '').trim().replace(/\s+/g, ' ').toLowerCase()).filter(Boolean))];
  return { heads, noAlt, dead, actions, title: document.title, desc: (document.querySelector('meta[name=description]') || {}).content || '', lang: document.documentElement.lang };
});
const h1 = info.heads.filter(h => h.level === 1);
say(h1.length === 1 ? 'PASS' : 'FAIL', `headings: ${h1.length} h1`, h1.length === 1 ? `"${h1[0].text}"` : short(h1.map(h => h.text)));
const skips = info.heads.filter((h, i) => i && h.level - info.heads[i - 1].level > 1).map(h => `h${h.level} "${h.text}"`);
say(skips.length ? 'WARN' : 'PASS', `heading order: ${skips.length ? 'levels skipped' : 'no skipped levels'}`, short(skips));
say(info.noAlt.length ? 'FAIL' : 'PASS', `images: ${info.noAlt.length ? info.noAlt.length + ' with no alt attribute' : 'all have alt text (or are marked decorative)'}`, short(info.noAlt));
say(info.dead.length ? 'WARN' : 'PASS', `links: ${info.dead.length ? info.dead.length + ' go nowhere (href missing or "#")' : 'all go somewhere'}`, short(info.dead, 8));
say(info.actions.length > 2 ? 'WARN' : 'PASS', `first screen asks for ${info.actions.length} different action(s)`, short(info.actions, 6));
say(info.title && info.desc ? 'PASS' : 'WARN', `title and description: ${info.title ? 'title' : 'NO title'}, ${info.desc ? 'description' : 'NO meta description'}${info.lang ? '' : ', no lang on <html>'}`, `${info.title}${info.desc ? '  /  ' + info.desc.slice(0, 90) : ''}`);

// --- keyboard focus: tab to the first few controls and see whether anything draws
const focus = [];
for (let i = 0; i < 4; i++) {
  await pg.keyboard.press('Tab');
  const f = await pg.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const s = getComputedStyle(e); return { name: (e.textContent || e.value || e.tagName).trim().replace(/\s+/g, ' ').slice(0, 24), seen: (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== 'none' }; });
  if (f) focus.push(f);
}
const unseen = focus.filter(f => !f.seen).map(f => f.name);
say(!focus.length ? 'WARN' : unseen.length ? 'FAIL' : 'PASS', `keyboard focus: ${!focus.length ? 'nothing could be tabbed to' : unseen.length ? 'no visible outline on some controls' : 'visible on the first ' + focus.length + ' controls'}`, short(unseen));
await pg.close();

// --- motion: what runs, for how long, and what is left under reduced motion
const motion = async reduced => {
  const p = await browser.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: reduced ? 'reduce' : 'no-preference' });
  await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch(() => {});
  await p.waitForTimeout(150);
  const a = await p.evaluate(() => document.getAnimations().map(x => { const t = x.effect.getComputedTiming(); return { ms: Math.round((+t.delay || 0) + (t.duration === 'auto' ? 0 : +t.duration) * (t.iterations === Infinity ? 1 : t.iterations)), endless: t.iterations === Infinity, name: x.animationName || x.transitionProperty || 'animation' }; }));
  await p.close();
  return a;
};
const moving = await motion(false), still = await motion(true);
const longest = Math.max(0, ...moving.filter(m => !m.endless).map(m => m.ms)), endless = moving.filter(m => m.endless);
say(longest > 1500 ? 'WARN' : 'PASS', `entrance: ${moving.length} animation(s), the last one ends at ${(longest / 1000).toFixed(2)} s`, longest > 1500 ? 'aim for the first screen to settle in about 1.2 s' : '');
say(endless.length > 1 ? 'WARN' : 'PASS', `${endless.length} thing(s) keep moving for ever`, short([...new Set(endless.map(m => m.name))]));
const left = still.filter(m => m.ms > 200 || m.endless);
say(left.length ? 'FAIL' : 'PASS', `reduced motion: ${left.length ? left.length + ' animation(s) still run' : 'respected'}`, short([...new Set(left.map(m => m.name))]));

await browser.close();
console.log(`\n${failed ? failed + ' failed.' : 'Nothing failed.'} WARN lines want a look, not necessarily a change. This does not judge how the page looks.\n`);
process.exit(failed ? 1 : 0);
