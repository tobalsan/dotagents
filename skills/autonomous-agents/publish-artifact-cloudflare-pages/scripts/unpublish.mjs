#!/usr/bin/env node
// Unpublish an artifact: delete every Pages deployment on the given branch/slug,
// including the aliased (latest) one, so neither the alias URL nor any
// per-deploy hash URL keeps serving it.
// Usage: unpublish.mjs <slug> [--dry-run]
// Needs Node 18+ (global fetch). Same env vars as publish.sh.

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const raw = args.find((a) => !a.startsWith("--"));
const die = (msg, code = 1) => { console.error(`unpublish-artifact: ${msg}`); process.exit(code); };

if (!raw) die("usage: unpublish.mjs <slug> [--dry-run]");
const token = process.env.CLOUDFLARE_API_TOKEN || die("missing CLOUDFLARE_API_TOKEN");
const account = process.env.CLOUDFLARE_ACCOUNT_ID || die("missing CLOUDFLARE_ACCOUNT_ID");
const project = process.env.ARTIFACTS_PROJECT || "artifacts";
const base = process.env.CF_API_BASE || "https://api.cloudflare.com/client/v4";

// Normalise exactly like publish.sh so a slug copied from a URL matches.
const slug = raw.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 20);
if (!slug || slug === "main") die("refusing to touch the production branch or an empty slug");

const url = `${base}/accounts/${account}/pages/projects/${project}/deployments`;
const headers = { Authorization: `Bearer ${token}` };

async function api(method, u) {
  const res = await fetch(u, { method, headers });
  const body = await res.json().catch(() => ({}));
  if (!res.ok || body.success === false) {
    const err = (body.errors || []).map((e) => e.message).join("; ") || res.statusText;
    die(`${method} ${u.replace(base, "")} failed (${res.status}): ${err}`);
  }
  return body;
}

// Collect all preview deployments whose branch matches the slug.
const matches = [];
for (let page = 1; ; page++) {
  const body = await api("GET", `${url}?env=preview&page=${page}&per_page=25`);
  const items = body.result || [];
  for (const d of items) {
    const branch = d.deployment_trigger?.metadata?.branch ?? "";
    const alias = branch.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    if (alias === slug) matches.push(d);
  }
  const info = body.result_info || {};
  const total = info.total_count ?? 0;
  if (items.length === 0 || page * (info.per_page || 25) >= total) break;
}

if (matches.length === 0) die(`no deployments found for '${slug}' in project '${project}'`, 3);

// Delete oldest first, the aliased (newest) one last, all with force=true.
matches.sort((a, b) => new Date(a.created_on) - new Date(b.created_on));
for (const d of matches) {
  const label = `${d.id} (${d.url})${d.aliases?.length ? " [alias]" : ""}`;
  if (dryRun) { console.error(`would delete ${label}`); continue; }
  await api("DELETE", `${url}/${d.id}?force=true`);
  console.error(`deleted ${label}`);
}
console.log(`${dryRun ? "would unpublish" : "unpublished"} ${slug}: ${matches.length} deployment(s)`);
