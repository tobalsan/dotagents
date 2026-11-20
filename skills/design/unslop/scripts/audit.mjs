#!/usr/bin/env node
// Lists what makes a page read as generated, with evidence and a rough score for comparing before and after.
//
//   node audit.mjs https://example.com            a live page (fetches the HTML and its stylesheets)
//   node audit.mjs ./index.html                   a file
//   node audit.mjs ./src                          a source folder (.html .jsx .tsx .vue .svelte .astro .css ...)
//   node audit.mjs <target> --browser             render it first (needs Playwright): for pages built by JavaScript
//   node audit.mjs <target> --json report.json    also write the findings as JSON
//
// Node 18 or newer, no packages. It reads text, not pixels: it cannot see a bad photo or weak hierarchy, so look at
// the screenshots too. A low score means the known tells are gone, not that the page is good.
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const target = args.find(a => !a.startsWith('--') && args[args.indexOf(a) - 1] !== '--json');
const flag = k => args.includes('--' + k);
const opt = k => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : null; };
if (!target) { console.error('usage: node audit.mjs <url | file.html | folder> [--browser] [--json out.json]'); process.exit(2); }

// ---------------------------------------------------------------- gather: markup, css, visible text
async function get(url) {
  const r = await fetch(url, { headers: { 'user-agent': 'unslop-audit/1.0', accept: 'text/html,text/css,*/*' }, redirect: 'follow', signal: AbortSignal.timeout(20000) });
  if (!r.ok) throw new Error(`${r.status} for ${url}`);
  return r.text();
}
async function loadPlaywright() {      // from the project you run this in, or anywhere Node can find it
  try { return await import('playwright'); } catch { /* try require, which also honours NODE_PATH */ }
  const { createRequire } = await import('node:module');
  for (const from of [process.cwd() + '/', import.meta.url]) { try { return createRequire(from)('playwright'); } catch { /* next */ } }
  return null;
}
async function gather() {
  if (flag('browser')) {
    const pw = await loadPlaywright();
    if (!pw) { console.error('--browser needs Playwright, which Node cannot find. Use your browser testing skill or tool (for example buu) instead.'); process.exit(2); }
    const b = await pw.chromium.launch();
    const pg = await b.newPage({ viewport: { width: 1440, height: 900 } });
    const url = /^https?:/.test(target) ? target : 'file://' + path.resolve(target);
    await pg.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    const out = await pg.evaluate(() => {
      let css = '';
      for (const s of document.styleSheets) { try { for (const r of s.cssRules) css += r.cssText + '\n'; } catch { /* another origin */ } }
      return { html: document.documentElement.outerHTML, css, links: [...document.styleSheets].map(s => s.href).filter(Boolean) };
    });
    await b.close();
    for (const href of out.links) { try { out.css += '\n' + await get(href); } catch { /* skip */ } }
    return { html: out.html, css: out.css, mode: 'rendered page' };
  }
  if (/^https?:/.test(target)) {
    const html = await get(target);
    let css = '';
    const hrefs = [...html.matchAll(/<link\b[^>]*rel=["']?stylesheet["']?[^>]*>/gi)].map(m => (m[0].match(/href=["']([^"']+)["']/i) || [])[1]).filter(Boolean).slice(0, 14);
    for (const h of hrefs) { try { css += '\n' + await get(new URL(h, target).href); } catch { /* skip */ } }
    return { html, css, mode: 'fetched page' };
  }
  const st = fs.statSync(target);
  if (st.isDirectory()) {
    let html = '', css = '', n = 0;
    const walk = d => {
      for (const e of fs.readdirSync(d, { withFileTypes: true })) {
        if (e.name.startsWith('.') || ['node_modules', 'dist', 'build', 'out', '.next', 'vendor', 'coverage'].includes(e.name)) continue;
        const p = path.join(d, e.name);
        if (e.isDirectory()) walk(p);
        else if (/\.(html?|jsx|tsx|vue|svelte|astro|mdx|njk|liquid|erb|php)$/i.test(e.name) && n < 400) { html += '\n' + fs.readFileSync(p, 'utf8'); n++; }
        else if (/\.(css|scss|sass|less|styl)$/i.test(e.name) && n < 400) { css += '\n' + fs.readFileSync(p, 'utf8'); n++; }
      }
    };
    walk(target);
    return { html, css, mode: `source folder (${n} files)`, source: true };
  }
  const html = fs.readFileSync(target, 'utf8');
  let css = '';
  for (const m of html.matchAll(/<link\b[^>]*rel=["']?stylesheet["']?[^>]*>/gi)) {
    const h = (m[0].match(/href=["']([^"']+)["']/i) || [])[1];
    if (h && !/^https?:|^\/\//.test(h)) { try { css += '\n' + fs.readFileSync(path.resolve(path.dirname(target), h), 'utf8'); } catch { /* skip */ } }
  }
  return { html, css, mode: 'file' };
}

const page = await gather();
const html = page.html;
const css = page.css + '\n' + [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)].map(m => m[1]).join('\n') + '\n' + [...html.matchAll(/\sstyle=(?:"([^"]*)"|'([^']*)')/gi)].map(m => m[1] || m[2]).join(';\n');
const classes = [...html.matchAll(/\sclass(?:Name)?=(?:"([^"]*)"|'([^']*)'|\{`([^`]*)`\})/g)].map(m => m[1] || m[2] || m[3]).join(' ');
const decode = s => s.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&#39;|&rsquo;/g, "'").replace(/&quot;/g, '"').replace(/&[a-z]+;/g, ' ');
const strip = s => decode(s.replace(/<script[\s\S]*?<\/script>/gi, ' ').replace(/<style[\s\S]*?<\/style>/gi, ' ').replace(/<!--[\s\S]*?-->/g, ' ').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
const text = strip(html);
const body = html.replace(/^[\s\S]*?<body[^>]*>/i, '');
const jsOnly = !page.source && text.length < 200 && /<script/i.test(html);

// ---------------------------------------------------------------- colour helpers
const hexRgb = h => { h = h.replace('#', ''); if (h.length === 3 || h.length === 4) h = [...h].map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
function hsl([r, g, b]) { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, d = mx - mn; if (!d) return [0, 0, l]; const s = d / (1 - Math.abs(2 * l - 1)); let h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; return [(h * 60 + 360) % 360, s, l]; }
function colours(s) {
  const out = [];
  for (const m of s.matchAll(/#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})\b/gi)) out.push(hsl(hexRgb(m[1])));
  for (const m of s.matchAll(/rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)/gi)) out.push(hsl([+m[1], +m[2], +m[3]]));
  for (const m of s.matchAll(/hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%/gi)) out.push([+m[1], +m[2] / 100, +m[3] / 100]);
  return out;
}
const purple = ([h, s, l]) => s > 0.35 && l > 0.25 && l < 0.92 && h >= 232 && h <= 335;
const vivid = ([, s, l]) => s > 0.45 && l > 0.2 && l < 0.85;

// ---------------------------------------------------------------- the tells
const found = [];
const clip = (s, n = 150) => s.length <= n ? s : s.slice(0, n).replace(/[\s,]+\S*$/, '') + ' …';      // cut on a word, and say it was cut
const add = (id, pass, weight, count, threshold, what, evidence = []) => { if (count > 0) found.push({ id, pass, weight, count, score: +(weight * Math.min(1, count / threshold)).toFixed(1), what, evidence: [...new Set(evidence.map(e => String(e).replace(/\s+/g, ' ').trim()))].slice(0, 4).map(e => clip(e)) }); };
const tw = re => (classes.match(re) || []);

// gradients
const grads = [...css.matchAll(/(?:linear|radial|conic)-gradient\(([^;{}]*?)\)(?=[;,}\s]|$)/gi)].map(m => m[0]);
const purpleGrads = grads.filter(g => colours(g).filter(purple).length >= 1 && colours(g).length >= 2);
const twGrad = tw(/\b(?:from|via|to)-(?:indigo|violet|purple|fuchsia|pink)-\d{2,3}\b/g);
add('purple-gradient', 'Color', 10, purpleGrads.length + (twGrad.length ? Math.ceil(twGrad.length / 2) : 0), 2, 'Purple, indigo or pink gradients', [...purpleGrads, ...twGrad]);
const gradText = (css.match(/background-clip\s*:\s*text/gi) || []).length ? css.match(/-webkit-background-clip\s*:\s*text|(?<!-webkit-)background-clip\s*:\s*text/gi).length : 0;
add('gradient-text', 'Color', 8, Math.max(gradText ? 1 : 0, tw(/\bbg-clip-text\b/g).length), 1, 'Gradient-filled text', gradText ? ['background-clip: text'] : tw(/\bbg-clip-text\b/g));
const blobs = [...css.matchAll(/filter\s*:[^;{}]*blur\(\s*(\d+)px/gi)].filter(m => +m[1] >= 40);
add('blur-blobs', 'Declutter', 5, blobs.length + tw(/\bblur-(?:2xl|3xl)\b/g).length, 1, 'Big blurred colour blobs behind the content', [...blobs.map(m => m[0]), ...tw(/\bblur-(?:2xl|3xl)\b/g)]);
const glass = (css.match(/backdrop-filter\s*:[^;{}]*blur/gi) || []).length + tw(/\bbackdrop-blur(?:-\w+)?\b/g).length;
add('glass', 'Declutter', 5, glass, 1, 'Frosted glass cards', ['backdrop-filter: blur']);
const glows = [...css.matchAll(/box-shadow\s*:([^;{}]+)/gi)].filter(m => colours(m[1]).some(c => c[1] > 0.4) && /\b(?:[2-9]\d|\d{3})px/.test(m[1]));
add('glow-shadows', 'Color', 4, glows.length + tw(/\bshadow-(?:indigo|violet|purple|fuchsia|pink|blue|cyan)-\d{2,3}/g).length, 2, 'Coloured glow shadows', glows.map(m => 'box-shadow:' + m[1]));

// emoji, badges, proof, calls to action
const emoji = text.match(/\p{Emoji_Presentation}|\p{Extended_Pictographic}️/gu) || [];
add('emoji', 'Declutter', 8, emoji.length, 4, 'Emoji used as icons or decoration', [emoji.slice(0, 14).join(' ')]);
const h1at = body.search(/<h1\b/i);
const before = h1at > 0 ? strip(body.slice(Math.max(0, h1at - 700), h1at)) : '';
const badge = before.match(/(?:[\p{Emoji_Presentation}✨🚀🎉]\s*)?\b(?:new|beta|introducing|announcing|now (?:with|available|live)|just launched|v\d(?:\.\d)?)\b.{0,70}$/iu);
add('badge', 'Declutter', 4, badge ? 1 : 0, 1, 'An announcement pill above the headline', badge ? [badge[0]] : []);
// a few words after the claim, not a run of characters: stripped text has no element edges, so a long reach reads into the next element
const proof = [...text.matchAll(/trusted by(?: [\w,+&'’-]+){1,3}|\b[\d,.]+\s?[km]?\+\s*(?:happy |active |satisfied )?(?:customers|companies|users|teams|businesses|developers|clients|brands)|(?:★|⭐){3,}|#1(?: [\w-]+){1,3}|world['’]s (?:leading|best|first)(?: [\w-]+){0,3}|award[- ]winning|\b99\.9+%\s*uptime/gi)].map(m => m[0]);
add('unverified-proof', 'Copy', 8, proof.length, 2, 'Proof nobody can check (cut it or back it up)', proof);
const first = strip(body).slice(0, 1400);
const ctaRe = /\b(get started(?: (?:for )?free| now| today)?|start (?:free|now|for free|your free trial)|try (?:it )?(?:free|now|for free)|sign up(?: free)?|book (?:a )?demo|request (?:a )?demo|learn more|watch (?:the )?demo|see (?:how )?it works|contact sales|join (?:the )?waitlist|explore (?:features|more))\b/gi;
const ctas = [...new Set((first.match(ctaRe) || []).map(s => s.toLowerCase()))];
add('too-many-ctas', 'Declutter', 5, ctas.length >= 3 ? ctas.length - 1 : 0, 2, 'Three or more calls to action on the first screen', ctas);
const generic = (first.match(/\b(get started|learn more)\b/gi) || []).length;
add('generic-cta', 'Copy', 3, generic, 2, 'Buttons that say nothing ("Get Started", "Learn More")', [...new Set((first.match(/\b(get started[\w ]{0,10}|learn more)\b/gi) || []))]);
const navBlock = (body.match(/<nav\b[\s\S]*?<\/nav>/i) || body.match(/<header\b[\s\S]*?<\/header>/i) || [''])[0];
const navLinks = (navBlock.match(/<a\b/gi) || []).length;
add('nav-links', 'Declutter', 3, navLinks > 6 ? navLinks - 5 : 0, 3, 'More than six things in the navigation', [`${navLinks} links`]);

// copy
const BUZZ = ['revolutioni[sz]e', 'unlock(?:ing)? (?:the )?(?:full |true )?(?:potential|power)', 'supercharge', 'seamless(?:ly)?', 'cutting[- ]edge', 'next[- ]gen(?:eration)?', 'ai[- ]powered', 'elevate', 'empower(?:ing|s)?', 'streamline', 'leverag(?:e|es|ing)', 'game[- ]chang(?:er|ing)', 'transform(?:ing)? (?:your|the way)', 'all[- ]in[- ]one', 'state[- ]of[- ]the[- ]art', 'world[- ]class', 'robust', 'effortless(?:ly)?', 'take (?:your )?[\\w ]{1,20} to the next level', 'drive (?:growth|results|innovation)', 'best[- ]in[- ]class', 'innovative solutions?', 'solutions? for (?:modern|today)', 'the future of', 'reimagin(?:e|ed|ing)', 'blazing[- ]fast', 'lightning[- ]fast', 'enterprise[- ]grade', 'harness the power', 'at scale', 'unleash'];
const buzz = [...text.matchAll(new RegExp('\\b(?:' + BUZZ.join('|') + ')\\b', 'gi'))].map(m => m[0].toLowerCase());
add('buzzwords', 'Copy', 10, buzz.length, 6, 'Copy that could be about any company', [[...new Set(buzz)].slice(0, 10).join(', ')]);
const heads = [...body.matchAll(/<h[2-4]\b[^>]*>([\s\S]*?)<\/h[2-4]>/gi)].map(m => strip(m[1]));
const stockFeature = heads.filter(h => /^(?:lightning[- ]fast|blazing[- ]fast|fast(?: (?:&|and) \w+)?|secure(?: (?:&|and) reliable)?|reliable|scalable(?: growth)?|easy to use|simple|powerful(?: \w+)?|24\/7 support|seamless integrations?|(?:advanced |real[- ]time |smart )?analytics|customi[sz]able|user[- ]friendly|real[- ]time(?: \w+)?|collaboration|automation|smart insights)$/i.test(h));
add('stock-features', 'Declutter', 6, stockFeature.length >= 2 ? stockFeature.length : 0, 3, 'The fast / secure / scalable feature cards', stockFeature);
const stockSections = heads.filter(h => /^(?:features|how it works|testimonials|what (?:our )?(?:customers|clients) say|pricing|frequently asked questions|faq|why choose us|our services|get in touch)$/i.test(h));
add('template-sections', 'Proof', 4, stockSections.length >= 4 ? stockSections.length : 0, 5, 'The stock run of sections, in the stock order', stockSections);
const lorem = text.match(/lorem ipsum|your (?:tagline|company name|text) here|placeholder text|john doe|jane doe|acme (?:inc|corp)/gi) || [];
add('placeholder', 'Copy', 5, lorem.length, 1, 'Placeholder text left in', lorem);

// type, shape, palette, pictures
const fams = [...css.matchAll(/font-family\s*:\s*([^;{}]+)/gi)].map(m => m[1].split(',')[0].replace(/["']/g, '').trim().toLowerCase()).filter(f => f && !/^(inherit|var\(|unset|initial)/.test(f));
const gfonts = [...html.matchAll(/fonts\.googleapis\.com\/css2?\?([^"' >]+)/gi)].flatMap(m => [...m[1].matchAll(/family=([^:&]+)/g)].map(x => decodeURIComponent(x[1]).replace(/\+/g, ' ').toLowerCase()));
const families = [...new Set([...fams, ...gfonts])].filter(f => !/^(monospace|ui-monospace|sans-serif|serif|system-ui|-apple-system|blinkmacsystemfont)$/.test(f));
const DEFAULTS = ['inter', 'roboto', 'poppins', 'open sans', 'montserrat', 'arial', 'helvetica', 'segoe ui', 'space grotesk', 'geist', 'plus jakarta sans', 'dm sans', 'manrope'];
const onlyDefault = families.length <= 1 && (families.length === 0 || DEFAULTS.includes(families[0]));
add('default-type', 'Font', 5, onlyDefault ? 1 : 0, 1, 'The default typeface, set with no particular voice', [families[0] || 'system fonts only']);
add('too-many-fonts', 'Font', 4, families.length > 3 ? families.length - 2 : 0, 2, 'More than three type families', families);
const radii = [...css.matchAll(/border-radius\s*:\s*([\d.]+)(px|rem)/gi)].map(m => +m[1] * (m[2] === 'rem' ? 16 : 1));
const bigRadius = radii.filter(r => r >= 16 && r < 200).length + tw(/\brounded-(?:2xl|3xl)\b/g).length;
add('soft-everything', 'Spacing', 3, bigRadius >= 4 ? bigRadius : 0, 8, 'Large rounded corners on everything', [`${new Set(radii).size} different radii`]);
const hues = new Set(colours(css).filter(vivid).map(c => Math.round(c[0] / 30) % 12));
add('palette', 'Color', 6, hues.size >= 4 ? hues.size - 2 : 0, 3, 'Four or more strong colours competing', [`${hues.size} hue families`]);
const centred = (css.match(/text-align\s*:\s*center/gi) || []).length + tw(/\btext-center\b/g).length;
add('centred', 'Layout', 3, centred >= 8 ? centred : 0, 14, 'Nearly everything centre-aligned', [`${centred} uses`]);
const imgs = [...html.matchAll(/<img\b[^>]*>/gi)].map(m => m[0]);
const stock = imgs.filter(i => /unsplash|pexels|freepik|shutterstock|istock|undraw|storyset|placehold|picsum|dashboard[-_ ]?(?:mock|preview)|mockup|hero[-_ ]?illustration|ai[-_ ]generated|midjourney|dall-?e/i.test(i));
const fakeUi = /analytics dashboard|dashboard (?:preview|mockup)/i.test(text) ? 1 : 0;
add('stock-visual', 'The made thing', 5, stock.length + fakeUi, 1, 'A stock picture or a made-up dashboard where the product should be', [...stock.map(i => (i.match(/src=["']([^"']+)/i) || [])[1] || i), ...(fakeUi ? ['a generic "analytics dashboard"'] : [])]);
const motion = (css.match(/@keyframes/gi) || []).length + tw(/\banimate-(?:pulse|bounce|ping|spin)\b/g).length;
add('restless', 'Motion', 3, motion >= 8 ? motion : 0, 12, 'A lot of things animating', [`${motion} animations`]);

// ---------------------------------------------------------------- report
found.sort((a, b) => b.score - a.score);
const total = Math.min(100, Math.round(found.reduce((s, f) => s + f.score, 0)));
const order = ['Declutter', 'Copy', 'Font', 'Color', 'Spacing', 'The made thing', 'Layout', 'Motion', 'Proof'];
console.log(`\nUnslop audit: ${target}  (${page.mode})`);
if (jsOnly) console.log('\n  This page is built by JavaScript, so there is almost nothing to read in its HTML.\n  Run again with --browser (needs Playwright), or point this at the source folder.\n');
console.log(`Slop score: ${total} / 100   (rough; use it to compare before and after)\n`);
if (!found.length) console.log('  None of the known tells. Look at the screenshots: hierarchy, the picture, and the copy still need a human eye.\n');
for (const p of order) {
  const list = found.filter(f => f.pass === p);
  if (!list.length) continue;
  console.log(`${p}`);
  for (const f of list) console.log(`  [${String(f.score).padStart(4)}] ${f.what}  (${f.count})${f.evidence.length ? '\n         ' + f.evidence.join('\n         ') : ''}`);
  console.log('');
}
const out = opt('json');
if (out) { fs.writeFileSync(out, JSON.stringify({ target, mode: page.mode, score: total, tells: found, families, words: text.split(' ').length }, null, 1)); console.log(`wrote ${out}`); }
