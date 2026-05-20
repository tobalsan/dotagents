import { CustomEditor, type ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { truncateToWidth, visibleWidth } from "@earendil-works/pi-tui";


function escapeRegex(value: string): string {
	return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function unique<T>(values: T[]): T[] {
	return [...new Set(values)];
}

class SkillConfirmEditor extends CustomEditor {
	constructor(
		tui: any,
		theme: any,
		keybindings: any,
		private readonly getSkillNames: () => string[],
		private readonly highlight: (text: string) => string,
		private readonly ghost: (text: string) => string,
	) {
		super(tui, theme, keybindings);
	}

	override handleInput(data: string): void {
		if (data === "\t") {
			const partial = this.getPartialMatch();
			if (partial) {
				this.setText(this.getText().replace(new RegExp(`(\\s/)${escapeRegex(partial.partial)}$`), `$1${partial.partial}${partial.completion} `));
				this.tui.requestRender();
				return;
			}
		}

		super.handleInput(data);
		this.tui.requestRender();
	}

	private getPartialMatch(): { partial: string; completion: string } | undefined {
		const token = this.getText().match(/\s\/([A-Za-z0-9_-]+)$/)?.[1];
		if (!token) return undefined;

		const matches = this.getSkillNames().filter((name) => name.toLowerCase().startsWith(token.toLowerCase()));
		if (matches.length !== 1) return undefined;

		const completion = matches[0]!.slice(token.length);
		return completion.length > 0 ? { partial: token, completion } : undefined;
	}

	private ghostAtCursor(cursor: string, completion: string): string {
		const [first, ...rest] = [...completion];
		if (!first) return cursor;
		return cursor.replace("\x1b[7m \x1b[0m", `\x1b[7m${first}\x1b[0m`) + this.ghost(rest.join(""));
	}

	override render(width: number): string[] {
		const skills = this.getSkillNames().sort((a, b) => b.length - a.length);
		const fullSkillPattern = skills.length > 0
			? new RegExp(`(\\s/)(${skills.map(escapeRegex).join("|")})(?=\\s|$)`, "gi")
			: undefined;
		const partial = this.getPartialMatch();
		const partialWithCursorPattern = partial
			? new RegExp(`(\\s/${escapeRegex(partial.partial)})(.*?\\x1b\\[7m \\x1b\\[0m)`)
			: undefined;
		const partialPattern = partial ? new RegExp(`(\\s/${escapeRegex(partial.partial)})`) : undefined;

		return super.render(width).map((line) => {
			let rendered = fullSkillPattern
				? line.replace(fullSkillPattern, (_all, prefix: string, name: string) => `${prefix}${this.highlight(name)}`)
				: line;
			if (partial && partialWithCursorPattern && partialPattern) {
				const withCursor = rendered.replace(partialWithCursorPattern, (_all, typed: string, cursor: string) => `${typed}${this.ghostAtCursor(cursor, partial.completion)}`);
				rendered = withCursor === rendered
					? rendered.replace(partialPattern, (_all, typed: string) => `${typed}${this.ghost(partial.completion)}`)
					: withCursor;
			}
			return visibleWidth(rendered) > width ? truncateToWidth(rendered, width) : rendered;
		});
	}
}

export default function (pi: ExtensionAPI) {
	const normalizeSkillName = (name: string) => name.replace(/^\//, "").replace(/^skill:/, "");
	const getSkillNames = () =>
		unique(
			pi
				.getCommands()
				.filter((command) => command.source === "skill")
				.flatMap((command) => [command.name, normalizeSkillName(command.name)])
				.map(normalizeSkillName)
				.filter(Boolean),
		).sort();

	const getTextMatch = (text: string, slashMode = false): { partial?: string; completion?: string; full?: string } | undefined => {
		const skills = getSkillNames();
		const fullTokens = [...text.matchAll(/\s\/([A-Za-z0-9_-]+)(?=\s|$)/g)].map((match) => match[1]!);
		const full = fullTokens
			.map((token) => skills.find((name) => name.toLowerCase() === token.toLowerCase()))
			.find(Boolean);
		if (full) return { full };

		const slashToken = text.match(/\s\/([A-Za-z0-9_-]*)$/)?.[1];
		if (skills.length === 0 || slashToken === undefined) return undefined;

		const token = slashToken ?? text.trimStart().match(/^[A-Za-z0-9_-]*/)?.[0] ?? "";
		if (token.length === 0) return undefined;

		const matches = skills.filter((name) => name.toLowerCase().startsWith(token.toLowerCase()));
		if (matches.length !== 1) return undefined;
		return { partial: token, completion: matches[0]!.slice(token.length) };
	};

	pi.registerCommand("skill-autocomplete-debug", {
		description: "Show loaded skill names used by skill-autocomplete",
		handler: async (_args, ctx) => {
			const names = getSkillNames();
			ctx.ui.notify(names.length ? `skill-autocomplete: ${names.join(", ")}` : "skill-autocomplete: no skills found", "info");
		},
	});

	pi.on("session_start", (_event, ctx) => {
		const installEditor = () =>
			ctx.ui.setEditorComponent((tui, theme, keybindings) =>
				new SkillConfirmEditor(
					tui,
					theme,
					keybindings,
					getSkillNames,
					(text) => ctx.ui.theme.fg("mdCode", text),
					(text) => ctx.ui.theme.fg("dim", text),
				),
			);
		installEditor();
		setTimeout(installEditor, 25);
		ctx.ui.addAutocompleteProvider((current) => ({
			async getSuggestions(lines, cursorLine, cursorCol, options) {
				const native = await current.getSuggestions(lines, cursorLine, cursorCol, options);
				const line = lines[cursorLine] ?? "";
				const before = line.slice(0, cursorCol);
				const slash = before.match(/\s\/([A-Za-z0-9_-]*)$/);
				if (!slash) return native;

				const query = slash[1] ?? "";
				if (query.length === 0) return native;

				const skillItems = getSkillNames()
					.filter((name) => name.toLowerCase().startsWith(query.toLowerCase()))
					.map((name) => ({ value: name, label: name, description: "skill" }));
				if (skillItems.length === 0) return native;

				const seen = new Set<string>();
				const items = [...skillItems, ...(native?.items ?? [])].filter((item) => {
					if (seen.has(item.value)) return false;
					seen.add(item.value);
					return true;
				});
				return { items, prefix: native?.prefix ?? `/${query}` };
			},
			applyCompletion(lines, cursorLine, cursorCol, item, prefix) {
				if (prefix.startsWith("/")) {
					const line = lines[cursorLine] ?? "";
					const beforePrefix = line.slice(0, cursorCol - prefix.length);
					if (beforePrefix.length > 0 && /\s$/.test(beforePrefix)) {
						const afterCursor = line.slice(cursorCol);
						const newLines = [...lines];
						newLines[cursorLine] = `${beforePrefix}/${item.value} ${afterCursor}`;
						return { lines: newLines, cursorLine, cursorCol: beforePrefix.length + item.value.length + 2 };
					}
				}
				return current.applyCompletion(lines, cursorLine, cursorCol, item, prefix);
			},
			shouldTriggerFileCompletion(lines, cursorLine, cursorCol) {
				return current.shouldTriggerFileCompletion?.(lines, cursorLine, cursorCol) ?? false;
			},
		}));
		ctx.ui.setWidget("skill-autocomplete", undefined);
	});
}
