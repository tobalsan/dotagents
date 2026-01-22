#!/usr/bin/env node

import { writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const port = getArg("--port", 9222);

function getArg(flag, defaultVal) {
  const idx = args.indexOf(flag);
  return idx === -1 ? defaultVal : parseInt(args[idx + 1], 10);
}

if (args.includes("--help")) {
  console.log(`Usage: screenshot.js [--port <number>]`);
  process.exit(0);
}

const browser = await puppeteer.connect({ browserURL: `http://localhost:${port}`, defaultViewport: null });

try {
  const pages = await browser.pages();
  const page = pages.at(-1);
  if (!page) {
    console.error("✗ No active tab");
    process.exit(1);
  }

  const client = await page.target().createCDPSession();
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const filePath = path.join(os.tmpdir(), `screenshot-${timestamp}.png`);

  try {
    const metrics = await client.send("Page.getLayoutMetrics").catch(() => null);
    const vp = metrics?.layoutViewport;
    let width = vp?.clientWidth || page.viewport()?.width;
    let height = vp?.clientHeight || page.viewport()?.height;

    if (!width || !height) {
      const dims = await page.evaluate(() => ({ width: innerWidth, height: innerHeight }));
      width = dims.width;
      height = dims.height;
    }

    const maxDim = 2000;
    const scale = Math.max(0.01, Math.min(1, maxDim / Math.max(width, height)));

    const shot = await client.send("Page.captureScreenshot", {
      format: "png",
      fromSurface: true,
      captureBeyondViewport: false,
      clip: { x: vp?.pageX ?? 0, y: vp?.pageY ?? 0, width, height, scale },
    });

    await writeFile(filePath, Buffer.from(shot.data, "base64"));
  } catch {
    await page.screenshot({ path: filePath });
  }

  console.log(filePath);
  await client.detach().catch(() => {});
} finally {
  await browser.disconnect();
}
