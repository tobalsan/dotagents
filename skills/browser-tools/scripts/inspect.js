#!/usr/bin/env node

import { execSync } from "node:child_process";
import http from "node:http";

const args = process.argv.slice(2);
const json = args.includes("--json");
const ports = getList("--ports");
const pids = getList("--pids");

function getList(flag) {
  const idx = args.indexOf(flag);
  if (idx === -1) return null;
  return args[idx + 1]?.split(",").map((n) => parseInt(n.trim(), 10)).filter((n) => n > 0) || null;
}

if (args.includes("--help")) {
  console.log(`Usage: inspect.js [options]
Options:
  --ports <list>   Filter by ports (comma-separated)
  --pids <list>    Filter by PIDs (comma-separated)
  --json           JSON output`);
  process.exit(0);
}

const fetchJson = (url, timeout = 2000) =>
  new Promise((resolve, reject) => {
    const req = http.get(url, { timeout }, (res) => {
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => {
        try {
          resolve(JSON.parse(Buffer.concat(chunks).toString()));
        } catch {
          resolve(undefined);
        }
      });
    });
    req.on("timeout", () => req.destroy(new Error("timeout")));
    req.on("error", reject);
  });

// Find Chrome processes with debugging enabled
let output = "";
try {
  output = execSync("ps -ax -o pid=,command=", { encoding: "utf8" });
} catch {
  console.error("Failed to list processes");
  process.exit(1);
}

const processes = [];
output.split("\n").forEach((line) => {
  const match = line.trim().match(/^(\d+)\s+(.+)$/);
  if (!match) return;
  const [, pidStr, cmd] = match;
  const pid = parseInt(pidStr, 10);
  if (!/chrome/i.test(cmd) || !(/--remote-debugging-port/.test(cmd) || /--remote-debugging-pipe/.test(cmd))) return;

  const portMatch = cmd.match(/--remote-debugging-port(?:=|\s+)(\d+)/);
  if (portMatch) {
    processes.push({ pid, port: parseInt(portMatch[1], 10), usesPipe: false });
  } else if (/--remote-debugging-pipe/.test(cmd)) {
    processes.push({ pid, usesPipe: true });
  }
});

// Filter
const filtered = processes.filter((p) => {
  if (!ports && !pids) return true;
  if (ports?.includes(p.port)) return true;
  if (pids?.includes(p.pid)) return true;
  return false;
});

// Fetch tab info
const sessions = await Promise.all(
  filtered.map(async (p) => {
    if (p.port === undefined) return { ...p, tabs: [] };
    const [version, tabs] = await Promise.all([
      fetchJson(`http://localhost:${p.port}/json/version`).catch(() => undefined),
      fetchJson(`http://localhost:${p.port}/json/list`).catch(() => []),
    ]);
    const filteredTabs = (tabs || []).filter((t) => {
      const type = t.type?.toLowerCase() ?? "";
      if (type && type !== "page" && type !== "app") {
        if (!t.url || t.url.startsWith("devtools://") || t.url.startsWith("chrome-extension://")) return false;
      }
      return t.url && t.url.trim().length > 0;
    });
    return { ...p, version, tabs: filteredTabs };
  })
);

if (json) {
  console.log(JSON.stringify(sessions, null, 2));
  process.exit(0);
}

if (sessions.length === 0) {
  console.log("No Chrome instances with DevTools ports found.");
  process.exit(0);
}

sessions.forEach((s, i) => {
  if (i > 0) console.log("");
  const transport = s.port !== undefined ? `port ${s.port}` : s.usesPipe ? "pipe" : "unknown";
  const browser = s.version?.Browser ? ` - ${s.version.Browser}` : "";
  console.log(`Chrome PID ${s.pid} (${transport})${browser}`);
  if (s.tabs.length === 0) {
    console.log("  (no tabs)");
    return;
  }
  s.tabs.forEach((t, idx) => {
    console.log(`  Tab ${idx + 1}: ${t.title || "(untitled)"}`);
    console.log(`           ${t.url || "(no url)"}`);
  });
});
