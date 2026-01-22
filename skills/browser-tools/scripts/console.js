#!/usr/bin/env node

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const port = getArg("--port", 9222);
const follow = args.includes("--follow");
const timeout = getArg("--timeout", follow ? 0 : 5);
const typesFilter = getArgStr("--types");
const useColor = process.stdout.isTTY;

function getArg(flag, defaultVal) {
  const idx = args.indexOf(flag);
  return idx === -1 ? defaultVal : parseInt(args[idx + 1], 10);
}

function getArgStr(flag) {
  const idx = args.indexOf(flag);
  return idx === -1 ? null : args[idx + 1];
}

if (args.includes("--help")) {
  console.log(`Usage: console.js [options]
Options:
  --port <number>    DevTools port (default: 9222)
  --timeout <secs>   Capture duration (default: 5, 0 for infinite)
  --follow           Continuous mode (Ctrl+C to stop)
  --types <list>     Filter: log,error,warn,info,debug,pageerror`);
  process.exit(0);
}

const allowedTypes = typesFilter ? new Set(typesFilter.split(",").map((t) => t.trim().toLowerCase())) : null;

const color = (text, code) => (useColor ? `\x1b[${code}m${text}\x1b[0m` : text);
const colors = {
  error: (t) => color(t, "31"),
  warn: (t) => color(t, "33"),
  info: (t) => color(t, "36"),
  debug: (t) => color(t, "90"),
  log: (t) => t,
  pageerror: (t) => color(t, "31"),
};

const timestamp = () => {
  const d = new Date();
  return d.toTimeString().split(" ")[0] + "." + d.getMilliseconds().toString().padStart(3, "0");
};

const formatValue = (v, depth = 0) => {
  if (depth > 10) return "[Object]";
  if (v === null) return "null";
  if (v === undefined) return "undefined";
  if (typeof v === "string") return `'${v}'`;
  if (typeof v === "number" || typeof v === "boolean") return String(v);
  if (typeof v === "function") return "[Function]";
  if (Array.isArray(v)) return `[ ${v.map((x) => formatValue(x, depth + 1)).join(", ")} ]`;
  if (typeof v === "object") {
    const entries = Object.entries(v).map(([k, val]) => `${k}: ${formatValue(val, depth + 1)}`);
    return entries.length ? `{ ${entries.join(", ")} }` : "{}";
  }
  return String(v);
};

const browser = await puppeteer.connect({ browserURL: `http://localhost:${port}`, defaultViewport: null });

try {
  const pages = await browser.pages();
  const page = pages.at(-1);
  if (!page) {
    console.error("✗ No active tab");
    process.exit(1);
  }

  page.on("console", async (msg) => {
    const type = msg.type().toLowerCase() === "warning" ? "warn" : msg.type().toLowerCase();
    if (allowedTypes && !allowedTypes.has(type)) return;

    let text;
    try {
      const values = await Promise.all(
        msg.args().map(async (arg) => {
          try {
            return formatValue(await arg.jsonValue());
          } catch {
            return "[Unserializable]";
          }
        })
      );
      text = values.join(" ");
    } catch {
      text = msg.text();
    }

    const loc = msg.location();
    const locStr = loc?.url && loc?.lineNumber ? ` ${loc.url}:${loc.lineNumber}` : "";
    const fmt = colors[type] || colors.log;
    console.log(fmt(`[${type.toUpperCase()}] ${timestamp()} ${text}${locStr}`));
  });

  page.on("pageerror", (err) => {
    if (allowedTypes && !allowedTypes.has("pageerror") && !allowedTypes.has("error")) return;
    console.log(colors.pageerror(`[PAGEERROR] ${timestamp()} ${err.message}`));
  });

  if (follow) {
    console.log(color("Monitoring console (Ctrl+C to stop)...", "90"));
    await new Promise((resolve) => {
      process.on("SIGINT", resolve);
      process.on("SIGTERM", resolve);
    });
  } else {
    console.log(color(`Capturing console for ${timeout}s...`, "90"));
    await new Promise((r) => setTimeout(r, timeout * 1000));
  }
} finally {
  await browser.disconnect();
}
