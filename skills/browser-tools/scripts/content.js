#!/usr/bin/env node

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const port = getArg("--port", 9222);
const timeout = getArg("--timeout", 10) * 1000;
const url = args.find((a) => !a.startsWith("--") && a !== String(port) && a !== String(timeout / 1000));

function getArg(flag, defaultVal) {
  const idx = args.indexOf(flag);
  return idx === -1 ? defaultVal : parseInt(args[idx + 1], 10);
}

if (!url || args.includes("--help")) {
  console.log(`Usage: content.js <url> [--port <number>] [--timeout <secs>]`);
  process.exit(url ? 0 : 1);
}

const browser = await puppeteer.connect({ browserURL: `http://localhost:${port}`, defaultViewport: null });

try {
  const pages = await browser.pages();
  const page = pages.at(-1);
  if (!page) {
    console.error("✗ No active tab");
    process.exit(1);
  }

  await page.goto(url, { waitUntil: "networkidle2", timeout }).catch(() => {});

  // Inject Readability and Turndown
  try {
    await page.setBypassCSP?.(true);
  } catch {}

  for (const src of [
    "https://unpkg.com/@mozilla/readability@0.4.4/Readability.js",
    "https://unpkg.com/turndown@7.1.2/dist/turndown.js",
    "https://unpkg.com/turndown-plugin-gfm@1.0.2/dist/turndown-plugin-gfm.js",
  ]) {
    try {
      const loaded = await page.evaluate((u) => !!document.querySelector(`script[src="${u}"]`), src);
      if (!loaded) await page.addScriptTag({ url: src });
    } catch {}
  }

  const result = await page.evaluate(() => {
    const toMarkdown = (html) => {
      if (!html || !window.TurndownService) return "";
      const td = new window.TurndownService({ headingStyle: "atx", codeBlockStyle: "fenced" });
      if (window.turndownPluginGfm?.gfm) td.use(window.turndownPluginGfm.gfm);
      return td.turndown(html).replace(/\n{3,}/g, "\n\n").trim();
    };

    const fallback = () => {
      const main = document.querySelector("main, article, [role=main], .content, #content") || document.body;
      return main?.textContent?.trim() ?? "";
    };

    let title = document.title;
    let content = "";

    try {
      if (window.Readability) {
        const clone = document.cloneNode(true);
        const article = new window.Readability(clone).parse();
        title = article?.title || title;
        content = toMarkdown(article?.content) || article?.textContent || "";
      }
    } catch {}

    if (!content) content = fallback();
    return { title, content: content?.trim().slice(0, 8000), url: location.href };
  });

  console.log(`URL: ${result.url}`);
  if (result.title) console.log(`Title: ${result.title}`);
  console.log("");
  console.log(result.content || "(No readable content)");
} finally {
  await browser.disconnect();
}
