// Pi port of the asd-ste100 Claude Code hooks. Reuses the skill's Python hook
// scripts by feeding them Claude-shaped payloads.
//   ste-inject.py   -> before_agent_start (rule card + last-reply feedback)
//   ste-pregate.py  -> tool_call on bash (deny sloppy git commit messages)
//   ste-refresh.py  -> tool_result (mid-turn card every 12 calls, md file lint)
//   ste-gate.py     -> agent_before_settle (lint final reply, warn or one rewrite)
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { isAbsolute, join, resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const HOOKS = join(process.env.HOME ?? "", "dotagents/skills/autonomous-agents/asd-ste100/hooks");

function runHook(script: string, payload: unknown, timeoutMs: number): any | undefined {
	const proc = spawnSync("python3", [join(HOOKS, script)], {
		input: JSON.stringify(payload),
		encoding: "utf-8",
		timeout: timeoutMs,
	});
	const out = proc.stdout?.trim();
	if (proc.status !== 0 || !out) return undefined;
	try {
		return JSON.parse(out);
	} catch {
		return undefined;
	}
}

function textOf(content: unknown): string {
	if (typeof content === "string") return content;
	if (!Array.isArray(content)) return "";
	return content
		.filter((b: any) => b?.type === "text")
		.map((b: any) => b.text ?? "")
		.join("\n");
}

export default function (pi: ExtensionAPI) {
	// Set once the gate asked for a rewrite in the current run (Claude's stop_hook_active).
	let gateFired = false;

	pi.on("before_agent_start", (event, ctx) => {
		if (event.messageType !== "user") return;
		gateFired = false;
		const res = runHook("ste-inject.py", { session_id: ctx.sessionManager.getSessionId() }, 10_000);
		const text = res?.hookSpecificOutput?.additionalContext;
		if (!text) return;
		return { message: { customType: "asd-ste100", content: text, display: false } };
	});

	pi.on("tool_call", (event) => {
		if (event.toolName !== "bash") return;
		const command = (event.input as { command?: string }).command ?? "";
		if (!/\bgit\b[\s\S]*\bcommit\b/.test(command)) return;
		const res = runHook("ste-pregate.py", { tool_name: "Bash", tool_input: { command } }, 15_000);
		const out = res?.hookSpecificOutput;
		if (out?.permissionDecision === "deny") return { block: true, reason: out.permissionDecisionReason };
	});

	pi.on("tool_result", (event, ctx) => {
		const toolName = event.toolName === "write" ? "Write" : event.toolName === "edit" ? "Edit" : event.toolName;
		const raw = (event.input as { path?: string }).path;
		const filePath = raw ? (isAbsolute(raw) ? raw : resolve(ctx.cwd, raw)) : undefined;
		const res = runHook(
			"ste-refresh.py",
			{ session_id: ctx.sessionManager.getSessionId(), tool_name: toolName, tool_input: { file_path: filePath } },
			15_000,
		);
		const note = res?.hookSpecificOutput?.additionalContext;
		if (!note) return;
		return {
			content: [...event.content, { type: "text" as const, text: `\n\n${note}` }],
			structuredContent: event.structuredContent,
		};
	});

	pi.on("agent_before_settle", (event, ctx) => {
		if (event.outcome !== "completed") return;
		// ste-gate.py reads a Claude-format transcript; synthesize one from the context.
		const lines: string[] = [];
		for (const m of event.context.contextMessages as any[]) {
			if (m.role === "user") {
				lines.push(JSON.stringify({ type: "user", message: { content: textOf(m.content) } }));
			} else if (m.role === "assistant") {
				lines.push(
					JSON.stringify({ type: "assistant", message: { content: [{ type: "text", text: textOf(m.content) }] } }),
				);
			}
		}
		const dir = mkdtempSync(join(tmpdir(), "ste-gate-"));
		const transcript = join(dir, "transcript.jsonl");
		let res: any;
		try {
			writeFileSync(transcript, lines.join("\n"));
			res = runHook(
				"ste-gate.py",
				{
					session_id: ctx.sessionManager.getSessionId(),
					transcript_path: transcript,
					stop_hook_active: gateFired,
				},
				30_000,
			);
		} finally {
			rmSync(dir, { recursive: true, force: true });
		}
		// canContinue here predates our entry; the appended custom message makes the context runnable.
		if (res?.decision !== "block") return;
		gateFired = true;
		if (res.systemMessage && ctx.hasUI) ctx.ui.notify(res.systemMessage, "warning");
		return {
			entries: [{ type: "custom_message", customType: "asd-ste100-gate", content: res.reason, display: false }],
			continue: true,
		};
	});
}
