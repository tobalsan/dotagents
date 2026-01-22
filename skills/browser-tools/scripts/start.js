#!/usr/bin/env node

import { spawn, execSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const port = getArg("--port", 9222);
const copyExistingProfile = args.includes("--copy-existing-profile");
const killExisting = args.includes("--kill-existing");
const profileDir = getArg("--profile-dir", path.join(os.homedir(), ".cache", "scraping"));
const chromePath = getArg("--chrome-path", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome");

function getArg(flag, defaultVal) {
  const idx = args.indexOf(flag);
  if (idx === -1) return defaultVal;
  return typeof defaultVal === "number" ? parseInt(args[idx + 1], 10) : args[idx + 1];
}

if (args.includes("--help") || args.includes("-h")) {
  console.log(`Usage: start.js [options]
Options:
  --port <number>       DevTools port (default: 9222)
  --copy-existing-profile  Copy user Chrome profile (overwrites saved data)
  --profile-dir <path>  Profile directory (default: ~/.cache/scraping)
  --chrome-path <path>  Chrome binary path
  --kill-existing       Kill running Chrome first`);
  process.exit(0);
}

if (killExisting) {
  try {
    execSync("killall 'Google Chrome'", { stdio: "ignore" });
    await new Promise((r) => setTimeout(r, 1000));
  } catch {}
}

execSync(`mkdir -p "${profileDir}"`);

if (copyExistingProfile) {
  const source = path.join(os.homedir(), "Library", "Application Support", "Google", "Chrome") + "/";
  execSync(`rsync -a --delete "${source}" "${profileDir}/"`, { stdio: "ignore" });
}

spawn(chromePath, [
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${profileDir}`,
  "--no-first-run",
  "--disable-popup-blocking",
], { detached: true, stdio: "ignore" }).unref();

let connected = false;
for (let i = 0; i < 30; i++) {
  try {
    const browser = await puppeteer.connect({ browserURL: `http://localhost:${port}`, defaultViewport: null });
    await browser.disconnect();
    connected = true;
    break;
  } catch {
    await new Promise((r) => setTimeout(r, 500));
  }
}

if (!connected) {
  console.error(`✗ Failed to start Chrome on port ${port}`);
  process.exit(1);
}

console.log(`✓ Chrome listening on http://localhost:${port}${copyExistingProfile ? " (profile copied)" : ""}`);
