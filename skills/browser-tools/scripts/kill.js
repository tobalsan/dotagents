#!/usr/bin/env node

import { execSync } from "node:child_process";
import http from "node:http";
import readline from "node:readline/promises";

const args = process.argv.slice(2);
const all = args.includes("--all");
const force = args.includes("--force");
const ports = getList("--ports");
const pids = getList("--pids");

function getList(flag) {
  const idx = args.indexOf(flag);
  if (idx === -1) return null;
  return args[idx + 1]?.split(",").map((n) => parseInt(n.trim(), 10)).filter((n) => n > 0) || null;
}

if (args.includes("--help")) {
  console.log(`Usage: kill.js [options]
Options:
  --all            Kill all debuggable Chrome instances
  --ports <list>   Kill by ports (comma-separated)
  --pids <list>    Kill by PIDs (comma-separated)
  --force          Skip confirmation`);
  process.exit(0);
}

if (!all && !ports && !pids) {
  console.error("Specify --all, --ports <list>, or --pids <list>");
  process.exit(1);
}

// Find Chrome processes
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
const targets = processes.filter((p) => {
  if (all) return true;
  if (ports?.includes(p.port)) return true;
  if (pids?.includes(p.pid)) return true;
  return false;
});

if (targets.length === 0) {
  console.log("No matching Chrome instances found.");
  process.exit(0);
}

if (!force) {
  console.log("About to terminate:");
  targets.forEach((t) => {
    const transport = t.port !== undefined ? `port ${t.port}` : t.usesPipe ? "pipe" : "unknown";
    console.log(`  PID ${t.pid} (${transport})`);
  });
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const answer = (await rl.question("Proceed? [y/N] ")).trim().toLowerCase();
  rl.close();
  if (answer !== "y" && answer !== "yes") {
    console.log("Aborted.");
    process.exit(0);
  }
}

let failed = false;
targets.forEach((t) => {
  try {
    process.kill(t.pid);
    const transport = t.port !== undefined ? `port ${t.port}` : t.usesPipe ? "pipe" : "unknown";
    console.log(`✓ Killed PID ${t.pid} (${transport})`);
  } catch (e) {
    console.error(`✗ Failed to kill PID ${t.pid}: ${e.message}`);
    failed = true;
  }
});

if (failed) process.exit(1);
