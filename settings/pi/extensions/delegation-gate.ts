/**
 * Delegation Gate
 *
 * Hard lever for the AGENTS.md "Delegation" rule. Per user prompt, the model must
 * call `classify_task` before any mutating tool runs:
 *   - direct      → single-file edit; mutations limited to one file path
 *   - orchestrate → must state the lightweight/medium/strong split; main agent
 *                   cannot edit/write until at least one `subagent` call ran
 *
 * Read-only tools (read, ffgrep, fffind, read-only bash, memory, web, …) always pass.
 * No-op inside subagent children (PI_SUBAGENT_CHILD=1).
 */

import { Type } from "typebox";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

type Mode = "direct" | "orchestrate";

const READ_ONLY_TOOLS = new Set([
	"read",
	"grep",
	"find",
	"ls",
	"ffgrep",
	"fffind",
	"codemode", // nested calls are gated individually
	"tool_search",
	"interview",
	"honcho_search",
	"honcho_chat",
	"honcho_remember",
	"web_enable",
	"web_search",
	"fetch_content",
	"get_search_content",
	"check_sources",
	"subagents_enable",
	"subagent_supervisor",
	"bg_wait",
	"classify_task",
]);

const FILE_TOOLS = new Set(["edit", "write"]);

const SAFE_BASH = [
	/^\s*(cat|head|tail|less|more|grep|rg|find|fd|ls|pwd|echo|printf|wc|sort|uniq|diff|file|stat|du|df|tree|which|whereis|type|env|printenv|uname|whoami|id|date|uptime|ps|jq|sed\s+-n|awk|cut|tr|basename|dirname|realpath|readlink|test|\[|true|cd)\b/,
	/^\s*git\s+(status|log|diff|show|branch|remote|rev-parse|describe|ls-|blame|config\s+--get|worktree\s+list)/,
	/^\s*(npm|pnpm|yarn)\s+(list|ls|view|info|search|outdated|audit|why)\b/,
	/^\s*(python3?|uv\s+run\s+python3?)\s+-c\b/,
	/^\s*(pi|exa|firecrawl|gh|linear|just)\s+(--help|-h|list|--list|search|view|issue\s+(view|list)|pr\s+(view|list|diff))\b/,
];

const BASH_WRITES_FILES = /[^2]>|>>|\btee\b|\bsed\s+-i\b|\bmv\b|\bcp\b|\brm\b|\bmkdir\b|\btouch\b|\bln\b|\bchmod\b|\bchown\b/;

function isReadOnlyBash(command: string): boolean {
	if (BASH_WRITES_FILES.test(command)) return false;
	const segments = command
		.split(/\n|&&|\|\||;|\|/)
		.map((s) => s.trim())
		.filter(Boolean);
	return segments.length > 0 && segments.every((s) => SAFE_BASH.some((p) => p.test(s)));
}

export default function delegationGate(pi: ExtensionAPI) {
	if (process.env.PI_SUBAGENT_CHILD === "1") return;

	let mode: Mode | undefined;
	let delegated = false;
	let touchedFile: string | undefined;

	function reset() {
		mode = undefined;
		delegated = false;
		touchedFile = undefined;
	}

	function status(ctx: ExtensionContext) {
		if (!ctx.hasUI) return;
		const label = mode === undefined ? "⚖ unclassified" : mode === "direct" ? "⚖ direct" : delegated ? "⚖ orchestrate ✓" : "⚖ orchestrate (no subagent yet)";
		const color = mode === undefined ? "warning" : mode === "orchestrate" && !delegated ? "warning" : "muted";
		ctx.ui.setStatus("delegation", ctx.ui.theme.fg(color, label));
	}

	pi.registerTool({
		name: "classify_task",
		label: "Classify task",
		description:
			"REQUIRED before any edit/write/mutating bash/subagent call, once per user prompt. " +
			"mode=direct: clearly scoped one-line or single-file edit (gate then allows mutations to ONE file). " +
			"mode=orchestrate: everything else; `plan` must say in prose which bounded tasks go to lightweight (scout/search), " +
			"medium (implementation), and strong (review/diagnosis) models. Main agent cannot edit/write until a `subagent` call ran.",
		parameters: Type.Object({
			mode: Type.Union([Type.Literal("direct"), Type.Literal("orchestrate")]),
			reason: Type.Optional(Type.String({ description: "direct: why this is a single-file edit" })),
			plan: Type.Optional(Type.String({ description: "orchestrate: lightweight/medium/strong split in prose" })),
		}),
		async execute(_id, params, _signal, _onUpdate, ctx) {
			if (params.mode === "orchestrate" && !params.plan?.trim()) {
				throw new Error("orchestrate requires `plan` (lightweight/medium/strong split)");
			}
			if (params.mode === "direct" && !params.reason?.trim()) {
				throw new Error("direct requires `reason`");
			}
			mode = params.mode;
			delegated = false;
			touchedFile = undefined;
			status(ctx);
			const text = params.mode === "direct" ? `direct: ${params.reason}` : `orchestrate:\n${params.plan}`;
			return { content: [{ type: "text", text: `Classified ${text}` }], details: { mode, plan: params.plan, reason: params.reason } };
		},
	});

	pi.on("before_agent_start", (event, ctx) => {
		if (event.messageType !== "user") return;
		reset();
		status(ctx);
	});

	pi.on("tool_call", (event, ctx) => {
		const name = event.toolName;
		if (READ_ONLY_TOOLS.has(name)) return;
		if (name === "bash" && isReadOnlyBash(String(event.input.command ?? ""))) return;

		if (mode === undefined) {
			return {
				block: true,
				reason:
					`[delegation-gate] \`${name}\` blocked: call \`classify_task\` first (direct = single-file edit; ` +
					`orchestrate = state lightweight/medium/strong split, then delegate via subagent).`,
			};
		}

		if (name === "subagent") {
			delegated = true;
			status(ctx);
			return;
		}

		if (mode === "direct" && name === "bash" && BASH_WRITES_FILES.test(String(event.input.command ?? ""))) {
			return {
				block: true,
				reason: "[delegation-gate] direct mode: write files with `edit`/`write` (single file), not bash redirects.",
			};
		}

		if (mode === "direct" && FILE_TOOLS.has(name)) {
			const file = String(event.input.path ?? "");
			if (touchedFile === undefined) touchedFile = file;
			else if (file !== touchedFile) {
				return {
					block: true,
					reason: `[delegation-gate] direct mode = single file (${touchedFile}). Re-run \`classify_task\` as orchestrate and delegate.`,
				};
			}
			return;
		}

		if (mode === "orchestrate" && !delegated && (FILE_TOOLS.has(name) || name === "bash")) {
			return {
				block: true,
				reason: `[delegation-gate] orchestrate mode: delegate implementation via \`subagent\` (medium model) before editing yourself. Integrate/verify after.`,
			};
		}
	});
}
