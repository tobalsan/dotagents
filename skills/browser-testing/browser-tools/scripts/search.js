#!/usr/bin/env node

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const port = getArg("--port", 9222);
const count = Math.max(1, Math.min(getArg("-n", 5), 50));
const fetchContent = args.includes("--content");
const timeout = getArg("--timeout", 10) * 1000;
const query = args.filter((a) => !a.startsWith("-") && a !== String(port) && a !== String(count) && a !== String(timeout / 1000)).join(" ");

function getArg(flag, defaultVal) {
  const idx = args.indexOf(flag);
  return idx === -1 ? defaultVal : parseInt(args[idx + 1], 10);
}

if (!query || args.includes("--help")) {
  console.log(`Usage: search.js <query> [options]
Options:
  -n <number>       Results count (default: 5, max: 50)
  --content         Fetch readable content for each result
  --timeout <secs>  Navigation timeout (default: 10)
  --port <number>   DevTools port (default: 9222)`);
  process.exit(query ? 0 : 1);
}

const browser = await puppeteer.connect({ browserURL: `http://localhost:${port}`, defaultViewport: null });

try {
  const pages = await browser.pages();
  const page = pages.at(-1);
  if (!page) {
    console.error("✗ No active tab");
    process.exit(1);
  }

  const results = [];
  let start = 0;

  while (results.length < count) {
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}&start=${start}`;
    await page.goto(searchUrl, { waitUntil: "domcontentloaded", timeout }).catch(() => {});
    await page.waitForSelector("div.MjjYud", { timeout: 3000 }).catch(() => {});

    const pageResults = await page.evaluate(() => {
      const items = [];
      document.querySelectorAll("div.MjjYud").forEach((r) => {
        const titleEl = r.querySelector("h3");
        const linkEl = r.querySelector("a");
        const snippetEl = r.querySelector("div.VwiC3b, div[data-sncf]");
        const link = linkEl?.getAttribute("href") ?? "";
        if (titleEl && linkEl && link && !link.startsWith("https://www.google.com")) {
          items.push({
            title: titleEl.textContent?.trim() ?? "",
            link,
            snippet: snippetEl?.textContent?.trim() ?? "",
          });
        }
      });
      return items;
    });

    for (const r of pageResults) {
      if (results.length >= count) break;
      if (!results.some((e) => e.link === r.link)) results.push(r);
    }

    if (pageResults.length === 0 || start >= 90) break;
    start += 10;
  }

  if (fetchContent) {
    for (const src of [
      "https://unpkg.com/@mozilla/readability@0.4.4/Readability.js",
      "https://unpkg.com/turndown@7.1.2/dist/turndown.js",
    ]) {
      try {
        await page.addScriptTag({ url: src });
      } catch {}
    }

    for (const r of results) {
      try {
        await page.goto(r.link, { waitUntil: "networkidle2", timeout }).catch(() => {});
        r.content = await page.evaluate(() => {
          try {
            if (window.Readability) {
              const article = new window.Readability(document.cloneNode(true)).parse();
              if (article?.textContent) return article.textContent.trim().slice(0, 2000);
            }
          } catch {}
          const main = document.querySelector("main, article") || document.body;
          return main?.textContent?.trim().slice(0, 2000) ?? "(No content)";
        });
      } catch (e) {
        r.content = `(Error: ${e.message})`;
      }
    }
  }

  results.forEach((r, i) => {
    console.log(`--- Result ${i + 1} ---`);
    console.log(`Title: ${r.title}`);
    console.log(`Link: ${r.link}`);
    if (r.snippet) console.log(`Snippet: ${r.snippet}`);
    if (r.content) console.log(`Content:\n${r.content}`);
    console.log("");
  });

  if (results.length === 0) console.log("No results found.");
} finally {
  await browser.disconnect();
}
