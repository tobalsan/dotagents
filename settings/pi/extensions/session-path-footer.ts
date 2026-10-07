import { homedir } from "node:os";
import { relative, resolve, sep } from "node:path";
import type { AssistantMessage } from "@earendil-works/pi-ai";
import { copyToClipboard, type ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { type TuiMouseEvent, truncateToWidth, visibleWidth } from "@earendil-works/pi-tui";

const COPY_LABEL = "copy session path";

function formatCount(count: number): string {
	if (count < 1_000) return String(count);
	if (count < 10_000) return `${(count / 1_000).toFixed(1)}k`;
	if (count < 1_000_000) return `${Math.round(count / 1_000)}k`;
	return `${(count / 1_000_000).toFixed(1)}M`;
}

function formatCwd(cwd: string): string {
	const home = resolve(homedir());
	const absolute = resolve(cwd);
	const rel = relative(home, absolute);
	if (rel === "") return "~";
	if (rel !== ".." && !rel.startsWith(`..${sep}`)) return `~${sep}${rel}`;
	return absolute;
}

export default function (pi: ExtensionAPI) {
	pi.on("session_start", (_event, ctx) => {
		if (ctx.mode !== "tui") return;

		ctx.ui.setFooter((tui, theme, footerData) => {
			const unsubscribe = footerData.onBranchChange(() => tui.requestRender());
			let labelX = -1;

			return {
				dispose: unsubscribe,
				invalidate() {},
				handleMouse(event: TuiMouseEvent) {
					const sessionFile = ctx.sessionManager.getSessionFile();
					if (!sessionFile || event.type !== "click" || event.button !== "left") return undefined;
					if (event.y !== 0 || labelX < 0 || event.x < labelX || event.x >= labelX + COPY_LABEL.length)
						return undefined;
					copyToClipboard(sessionFile).then(
						() => ctx.ui.notify("Session path copied", "info"),
						(err) => ctx.ui.notify(`Copy failed: ${err}`, "error"),
					);
					return { handled: true };
				},
				render(width: number): string[] {
					let cwd = formatCwd(ctx.cwd);
					const branch = footerData.getGitBranch();
					if (branch) cwd += ` (${branch})`;
					const sessionName = pi.getSessionName();
					if (sessionName) cwd += ` • ${sessionName}`;

					const dimLine = (text: string) =>
						truncateToWidth(theme.fg("dim", text), width, theme.fg("dim", "..."));
					const sessionFile = ctx.sessionManager.getSessionFile();
					const sepText = " • ";
					const suffix = sessionFile ? COPY_LABEL : "ephemeral session";
					const head = truncateToWidth(
						theme.fg("dim", cwd),
						Math.max(1, width - sepText.length - suffix.length),
						theme.fg("dim", "..."),
					);
					const prefix = head + theme.fg("dim", sepText);
					labelX = sessionFile ? visibleWidth(prefix) : -1;
					const styled = sessionFile
						? theme.fg("accent", `\x1b[4m${COPY_LABEL}\x1b[24m`)
						: theme.fg("dim", suffix);
					const lines = [truncateToWidth(prefix + styled, width)];

					let input = 0;
					let output = 0;
					let cacheRead = 0;
					let cacheWrite = 0;
					let cost = 0;
					for (const entry of ctx.sessionManager.getEntries()) {
						if (entry.type !== "message" || entry.message.role !== "assistant") continue;
						const message = entry.message as AssistantMessage;
						input += message.usage.input;
						output += message.usage.output;
						cacheRead += message.usage.cacheRead;
						cacheWrite += message.usage.cacheWrite;
						cost += message.usage.cost.total;
					}

					const stats = [];
					if (input) stats.push(`↑${formatCount(input)}`);
					if (output) stats.push(`↓${formatCount(output)}`);
					if (cacheRead) stats.push(`R${formatCount(cacheRead)}`);
					if (cacheWrite) stats.push(`W${formatCount(cacheWrite)}`);
					if (cost) stats.push(`$${cost.toFixed(3)}`);
					const usage = ctx.getContextUsage();
					if (usage) stats.push(`${usage.percent?.toFixed(1) ?? "?"}%/${formatCount(usage.contextWindow)}`);

					let model = ctx.model?.id ?? "no-model";
					if (ctx.model?.reasoning) model += ` • ${pi.getThinkingLevel()}`;
					const left = stats.join(" ");
					const padding = " ".repeat(Math.max(2, width - visibleWidth(left) - visibleWidth(model)));
					lines.push(dimLine(left + padding + model));

					const statuses = [...footerData.getExtensionStatuses().entries()]
						.sort(([a], [b]) => a.localeCompare(b))
						.map(([, text]) => text.replace(/[\r\n\t]+/g, " ").trim());
					if (statuses.length) lines.push(truncateToWidth(statuses.join(" "), width, "..."));
					return lines;
				},
			};
		});
	});
}
