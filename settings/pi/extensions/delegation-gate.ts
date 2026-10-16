/**
 * Delegation Guidance
 *
 * Advisory task-routing reminders, not tool permissions or shell containment.
 * Keeps `classify_task` for compatibility with existing project instructions.
 * No-op inside subagent children (PI_SUBAGENT_CHILD=1).
 */

import { Type } from "typebox";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function delegationGate(pi: ExtensionAPI) {
	if (process.env.PI_SUBAGENT_CHILD === "1") return;

	pi.registerTool({
		name: "classify_task",
		label: "Classify task",
		description:
			"Optional task-routing note; this extension never requires it or blocks tools. " +
			"Use direct for bounded work you will handle yourself, orchestrate for authorized delegation. " +
			"Classification is informational: no tool permissions, file limits, or execution ordering depend on it.",
		parameters: Type.Object({
			mode: Type.Union([Type.Literal("direct"), Type.Literal("orchestrate")]),
			reason: Type.Optional(Type.String({ description: "Why direct work fits the task" })),
			plan: Type.Optional(Type.String({ description: "Bounded delegation split, when useful" })),
		}),
		async execute(_id, params) {
			const note = params.mode === "direct" ? params.reason : params.plan;
			return {
				content: [{ type: "text", text: `Task routing: ${params.mode}${note?.trim() ? ` — ${note.trim()}` : ""}. Advisory only; tools remain available.` }],
				details: { mode: params.mode, reason: params.reason, plan: params.plan },
			};
		},
	});

	pi.on("before_agent_start", (event) => {
		if (event.messageType !== "user") return;
		return {
			message: {
				customType: "delegation-guidance",
				content: `[Delegation guidance — advisory, not a permission gate]
- Handle clearly scoped single-file edits directly.
- For larger implementation tasks, follow applicable delegation instructions: lightweight scouting, medium implementation, strong review as useful; keep ownership bounded and verify integration yourself.
- Delegate only when authorized by the user or applicable instructions. Lookup, discovery, and approved CLI work need not be framed as single-file edits or delegated merely to satisfy this extension.
- Prefer edit/write for source changes; use normal CLI output files and shell tools when appropriate. No classification prerequisite or shell-syntax restrictions are imposed here.
- Existing approval, read-only, destructive-action, and external-mutation rules still apply. Classification grants no authorization.`,
				display: false,
			},
		};
	});
}
