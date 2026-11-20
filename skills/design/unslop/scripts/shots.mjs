#!/usr/bin/env node
// Screenshots for before and after, and a side-by-side of the two. Needs a Playwright package that Node can find.
// With no Playwright, use your browser testing skill or tool (for example buu) instead.
//
//   node shots.mjs <url | file.html> <outdir> [--name before] [--wait 1500]
//       -> <name>-desktop.png  (1440 x 900, the first screen)
//          <name>-full.png     (the whole page at 1440 wide)
//          <name>-mobile.png   (390 x 844 at 2x, so the file is 780 px wide; the first screen)
//   node shots.mjs --pair before.png after.png out.png [--labels "Before,After"] [--ground "#e9e9e7"]
//       -> the two side by side. Any two pictures of the same shape: desktop with desktop, mobile with mobile.
//
// --name is yours to choose: "before" and "after" are the two the hand-over needs; use "pass-7" and the like to look
// at a pass on the way. Keep the output folder out of the site's git history (add it to .gitignore).
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
async function loadPlaywright() {      // from the project you run this in, or anywhere Node can find it
  try { return await import('playwright'); } catch { /* try require, which also honours NODE_PATH */ }
  const { createRequire } = await import('node:module');
  for (const from of [process.cwd() + '/', import.meta.url]) { try { return createRequire(from)('playwright'); } catch { /* next */ } }
  return null;
}
const pw = await loadPlaywright();
if (!pw) { console.error('Playwright not found. Use your browser testing skill or tool (for example buu) instead.'); process.exit(2); }
const browser = await pw.chromium.launch();

if (args[0] === '--pair') {
  const [, a, b, out] = args;
  if (!a || !b || !out) { console.error('usage: node shots.mjs --pair before.png after.png out.png'); process.exit(2); }
  const [la, lb] = opt('labels', 'Before,After').split(','), ground = opt('ground', '#e9e9e7');      // a neutral grey, so it favours neither page
  const uri = f => 'data:image/png;base64,' + fs.readFileSync(f).toString('base64');
  const pg = await browser.newPage({ viewport: { width: 2000, height: 200 }, deviceScaleFactor: 1 });      // short, so the picture ends where the content does
  await pg.setContent(`<body style="margin:0;background:${ground};font:600 22px system-ui,sans-serif;color:#11110f"><div style="display:flex;gap:32px;padding:32px;align-items:flex-start">${[[la, a], [lb, b]].map(([l, f]) => `<figure style="margin:0;flex:1;min-width:0"><figcaption style="margin:0 0 14px">${l}</figcaption><img src="${uri(f)}" style="display:block;width:100%;border:1px solid rgba(17,17,15,.15)"></figure>`).join('')}</div></body>`);
  await pg.waitForFunction(() => [...document.images].every(i => i.complete));
  await pg.screenshot({ path: out, fullPage: true });
  console.log('wrote', out);
} else {
  const [target, outdir] = args.filter((a, i) => !a.startsWith('--') && !(args[i - 1] || '').startsWith('--'));
  if (!target || !outdir) { console.error('usage: node shots.mjs <url | file.html> <outdir> [--name before]'); process.exit(2); }
  const name = opt('name', 'shot'), wait = +opt('wait', 1500);
  const url = /^https?:/.test(target) ? target : 'file://' + path.resolve(target);
  fs.mkdirSync(outdir, { recursive: true });
  for (const [kind, viewport, scale, full] of [['desktop', { width: 1440, height: 900 }, 1, false], ['full', { width: 1440, height: 900 }, 1, true], ['mobile', { width: 390, height: 844 }, 2, false]]) {
    const pg = await browser.newPage({ viewport, deviceScaleFactor: scale });
    await pg.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    await pg.waitForTimeout(wait);
    const file = path.join(outdir, `${name}-${kind}.png`);
    await pg.screenshot({ path: file, fullPage: full });
    console.log('wrote', file);
    await pg.close();
  }
}
await browser.close();
