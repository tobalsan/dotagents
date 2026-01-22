#!/usr/bin/env node

import puppeteer from "puppeteer-core";

const args = process.argv.slice(2);
const port = getArg("--port", 9222);
const message = args.filter((a) => !a.startsWith("--") && a !== String(port)).join(" ");

function getArg(flag, defaultVal) {
  const idx = args.indexOf(flag);
  return idx === -1 ? defaultVal : parseInt(args[idx + 1], 10);
}

if (!message || args.includes("--help")) {
  console.log(`Usage: pick.js <message> [--port <number>]`);
  process.exit(message ? 0 : 1);
}

const browser = await puppeteer.connect({ browserURL: `http://localhost:${port}`, defaultViewport: null });

try {
  const pages = await browser.pages();
  const page = pages.at(-1);
  if (!page) {
    console.error("✗ No active tab");
    process.exit(1);
  }

  await page.evaluate(() => {
    if (window.__pickInjected) return;
    window.__pickInjected = true;
    window.pick = (msg) =>
      new Promise((resolve) => {
        const selections = [];
        const selected = new Set();

        const overlay = document.createElement("div");
        overlay.style.cssText = "position:fixed;inset:0;z-index:2147483647;pointer-events:none";

        const highlight = document.createElement("div");
        highlight.style.cssText = "position:absolute;border:2px solid #3b82f6;background:rgba(59,130,246,0.1);transition:all 0.05s";
        overlay.appendChild(highlight);

        const banner = document.createElement("div");
        banner.style.cssText = "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1f2937;color:#fff;padding:12px 24px;border-radius:8px;font:14px system-ui;box-shadow:0 4px 12px rgba(0,0,0,0.3);pointer-events:auto;z-index:2147483647";

        const update = () => {
          banner.textContent = `${msg} (${selections.length} selected, Cmd/Ctrl+click to add, Enter to finish, ESC to cancel)`;
        };

        const cleanup = () => {
          document.removeEventListener("mousemove", onMove, true);
          document.removeEventListener("click", onClick, true);
          document.removeEventListener("keydown", onKey, true);
          overlay.remove();
          banner.remove();
          selected.forEach((el) => (el.style.outline = ""));
        };

        const serialize = (el) => {
          const parents = [];
          let cur = el.parentElement;
          while (cur && cur !== document.body) {
            const id = cur.id ? `#${cur.id}` : "";
            const cls = cur.className ? `.${cur.className.trim().split(/\s+/).join(".")}` : "";
            parents.push(`${cur.tagName.toLowerCase()}${id}${cls}`);
            cur = cur.parentElement;
          }
          return {
            tag: el.tagName.toLowerCase(),
            id: el.id || null,
            class: el.className || null,
            text: el.textContent?.trim()?.slice(0, 200) || null,
            html: el.outerHTML.slice(0, 500),
            parents: parents.join(" > "),
          };
        };

        const onMove = (e) => {
          const el = document.elementFromPoint(e.clientX, e.clientY);
          if (!el || overlay.contains(el) || banner.contains(el)) return;
          const r = el.getBoundingClientRect();
          highlight.style.cssText = `position:absolute;border:2px solid #3b82f6;background:rgba(59,130,246,0.1);top:${r.top}px;left:${r.left}px;width:${r.width}px;height:${r.height}px`;
        };

        const onClick = (e) => {
          if (banner.contains(e.target)) return;
          e.preventDefault();
          e.stopPropagation();
          const el = document.elementFromPoint(e.clientX, e.clientY);
          if (!el || overlay.contains(el) || banner.contains(el)) return;
          if (e.metaKey || e.ctrlKey) {
            if (!selected.has(el)) {
              selected.add(el);
              el.style.outline = "3px solid #10b981";
              selections.push(serialize(el));
              update();
            }
          } else {
            cleanup();
            resolve(selections.length > 0 ? selections : serialize(el));
          }
        };

        const onKey = (e) => {
          if (e.key === "Escape") {
            cleanup();
            resolve(null);
          } else if (e.key === "Enter" && selections.length > 0) {
            cleanup();
            resolve(selections);
          }
        };

        document.addEventListener("mousemove", onMove, true);
        document.addEventListener("click", onClick, true);
        document.addEventListener("keydown", onKey, true);
        document.body.append(overlay, banner);
        update();
      });
  });

  const result = await page.evaluate((m) => window.pick(m), message);

  if (Array.isArray(result)) {
    result.forEach((entry, i) => {
      if (i > 0) console.log("");
      Object.entries(entry).forEach(([k, v]) => console.log(`${k}: ${v}`));
    });
  } else if (result && typeof result === "object") {
    Object.entries(result).forEach(([k, v]) => console.log(`${k}: ${v}`));
  } else {
    console.log(result);
  }
} finally {
  await browser.disconnect();
}
