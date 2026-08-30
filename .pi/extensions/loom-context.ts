// LOOM WP2: host-side Caveman/Cavemem bridge.  No model-visible tool is registered.
import { mkdirSync, readFileSync, rmSync, writeFileSync, appendFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const ENABLE = "LOOM_CONTEXT_INTELLIGENCE";
const ROOT = process.cwd();
const CLI = join(ROOT, "scripts", "loom-context");
const RUNTIME = join(ROOT, ".loom", "runtime");

function enabled(): boolean { return process.env[ENABLE] !== "0" && process.env[ENABLE] !== "false"; }
function textOf(content: unknown): string {
	if (typeof content === "string") return content;
	if (!Array.isArray(content)) return "";
	return content.filter((x): x is { type: string; text?: string } => !!x && typeof x === "object")
		.filter(x => x.type === "text").map(x => x.text ?? "").join("\n");
}
function queryOf(payload: Record<string, unknown>): string {
	const messages = Array.isArray(payload.messages) ? payload.messages : [];
	for (let i = messages.length - 1; i >= 0; i--) {
		const message = messages[i] as Record<string, unknown>;
		if (message?.role === "user") return textOf(message.content);
	}
	return "";
}
function cli(command: string[], input?: unknown): unknown | undefined {
	try {
		mkdirSync(RUNTIME, { recursive: true, mode: 0o700 });
		const path = join(RUNTIME, `request-${process.pid}-${Date.now()}.json`);
		if (input !== undefined) writeFileSync(path, JSON.stringify(input), { mode: 0o600 });
		const result = spawnSync("python3", [CLI, ...command, ...(input === undefined ? [] : ["--input", path])], {
			cwd: ROOT, encoding: "utf8", timeout: 5000, maxBuffer: 2 * 1024 * 1024,
		});
		if (input !== undefined) rmSync(path, { force: true });
		if (result.status !== 0) throw new Error(result.stderr.trim() || `status ${result.status}`);
		return JSON.parse(result.stdout);
	} catch (error) {
		// Fail open: the WP1 provider path must remain runnable if WP2 has an implementation fault.
		try { appendFileSync(join(RUNTIME, "bridge-errors.log"), `${new Date().toISOString()} ${String(error)}\n`, { mode: 0o600 }); } catch { /* noop */ }
		return undefined;
	}
}

/** Active only for the canonical local provider. Disable with LOOM_CONTEXT_INTELLIGENCE=0. */
export default function loomContext(pi: ExtensionAPI): void {
	pi.on("before_provider_request", (event, ctx) => {
		if (!enabled() || ctx.model?.provider !== "loom-local") return;
		const payload = event.payload as Record<string, unknown>;
		if (!Array.isArray(payload.messages)) return;
		const packed = cli(["pack-payload", "--query", queryOf(payload), "--budget", "120"], payload) as { payload?: unknown; accounting?: unknown } | undefined;
		if (!packed?.payload) return;
		try { appendFileSync(join(RUNTIME, "packing.jsonl"), `${JSON.stringify({ timestamp: new Date().toISOString(), ...((packed.accounting ?? {}) as object) })}\n`, { mode: 0o600 }); } catch { /* telemetry is non-fatal */ }
		return packed.payload;
	});

	pi.on("tool_execution_end", (event, ctx) => {
		if (!enabled() || ctx.model?.provider !== "loom-local") return;
		const result = event.result as { content?: unknown };
		const text = textOf(result?.content);
		if (!text || text.length > 200_000) return;
		// The CLI persists only durable decisions/results/failures/constraints; ordinary turns are dropped.
		cli(["observe", "--source", `pi:${event.toolName}`, "--text", text]);
	});
}
