#!/usr/bin/env node
// Check or render Mermaid diagrams with Pele (https://pele.run).
//   node pele.mjs check <file...>        validate every diagram in .html, .md, or .mmd files
//   node pele.mjs svg <in.mmd> [out.svg] render one diagram to a static SVG
// Pele is installed on first use into ~/.cache/pele-skill.
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const cache = join(homedir(), '.cache', 'pele-skill');
const entry = join(cache, 'node_modules', 'pele', 'dist', 'pele.js');
if (!existsSync(entry)) {
  console.error('Installing pele@1 into ' + cache + ' ...');
  execFileSync('npm', ['install', '--silent', '--no-audit', '--no-fund', '--prefix', cache, 'pele@1'], { stdio: 'inherit' });
}
const { render, PeleError } = await import(pathToFileURL(entry).href);

const unescape = (s) =>
  s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&');

function diagrams(file) {
  const text = readFileSync(file, 'utf8');
  if (/\.html?$/i.test(file)) {
    return [...text.replace(/<!--[\s\S]*?-->/g, '').matchAll(/<(pre|div)\b[^>]*class="[^"]*\bmermaid\b[^"]*"[^>]*>([\s\S]*?)<\/\1>/gi)].map((m) => unescape(m[2]));
  }
  if (/\.(md|markdown)$/i.test(file)) {
    return [...text.matchAll(/^(`{3,}|~{3,})mermaid[^\n]*\n([\s\S]*?)^\1/gm)].map((m) => m[2]);
  }
  return [text];
}

const [cmd, ...args] = process.argv.slice(2);

if (cmd === 'check' && args.length) {
  let failed = 0;
  for (const file of args) {
    const list = diagrams(file);
    if (!list.length) console.log(`${file}: no Mermaid diagrams found`);
    list.forEach((source, i) => {
      const label = `${file} diagram ${i + 1}`;
      try {
        const { type, width, height } = render(source);
        console.log(`OK   ${label}: ${type} ${Math.round(width)}x${Math.round(height)}`);
      } catch (error) {
        if (!(error instanceof PeleError)) throw error;
        failed++;
        console.log(`FAIL ${label}: [${error.code}] ${error.message}`);
        if (error.snippet) console.log(error.snippet.replace(/^/gm, '     '));
      }
    });
  }
  process.exit(failed ? 1 : 0);
} else if (cmd === 'svg' && args.length) {
  const { svg } = render(readFileSync(args[0], 'utf8'), { fontFamily: 'system-ui, -apple-system, sans-serif' });
  if (args[1]) writeFileSync(args[1], svg);
  else process.stdout.write(svg + '\n');
} else {
  console.error('Usage: pele.mjs check <file...> | pele.mjs svg <in.mmd> [out.svg]');
  process.exit(2);
}
