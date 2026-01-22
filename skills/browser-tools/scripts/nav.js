#!/usr/bin/env node

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const url = args.find((a) => !a.startsWith("-"));
const newTab = args.includes("--new");
const port = getArg("--port", 9222);

function getArg(flag, defaultVal) {
  const idx = args.indexOf(flag);
  return idx === -1 ? defaultVal : parseInt(args[idx + 1], 10);
}

if (!url || args.includes("--help")) {
  console.log(`Usage: nav.js <url> [--new] [--port <number>]`);
  process.exit(url ? 0 : 1);
}

const browser = await puppeteer.connect({ browserURL: `http://localhost:${port}`, defaultViewport: null });

try {
  if (newTab) {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "domcontentloaded" });
    console.log("✓ Opened in new tab:", url);
  } else {
    const pages = await browser.pages();
    const page = pages.at(-1);
    if (!page) throw new Error("No active tab");
    await page.goto(url, { waitUntil: "domcontentloaded" });
    console.log("✓ Navigated to:", url);
  }
} finally {
  await browser.disconnect();
}
