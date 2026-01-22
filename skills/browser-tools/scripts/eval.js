#!/usr/bin/env node

import { inspect } from "node:util";
import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const port = getArg("--port", 9222);
const pretty = args.includes("--pretty");
const codeArgs = args.filter((a) => !a.startsWith("--") && a !== String(port));
const code = codeArgs.join(" ");

function getArg(flag, defaultVal) {
  const idx = args.indexOf(flag);
  return idx === -1 ? defaultVal : parseInt(args[idx + 1], 10);
}

if (!code || args.includes("--help")) {
  console.log(`Usage: eval.js <code> [--port <number>] [--pretty]`);
  process.exit(code ? 0 : 1);
}

const browser = await puppeteer.connect({ browserURL: `http://localhost:${port}`, defaultViewport: null });

try {
  const pages = await browser.pages();
  const page = pages.at(-1);
  if (!page) {
    console.error("✗ No active tab");
    process.exit(1);
  }

  const result = await page.evaluate((c) => {
    const AsyncFn = Object.getPrototypeOf(async () => {}).constructor;
    return new AsyncFn(`return (${c})`)();
  }, code);

  if (pretty) {
    console.log(inspect(result, { depth: 6, colors: process.stdout.isTTY, compact: false }));
  } else if (Array.isArray(result)) {
    result.forEach((entry, i) => {
      if (i > 0) console.log("");
      Object.entries(entry).forEach(([k, v]) => console.log(`${k}: ${v}`));
    });
  } else if (typeof result === "object" && result !== null) {
    Object.entries(result).forEach(([k, v]) => console.log(`${k}: ${v}`));
  } else {
    console.log(result);
  }
} finally {
  await browser.disconnect();
}
