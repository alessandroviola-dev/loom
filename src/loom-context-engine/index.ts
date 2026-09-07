import { appendFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { packMessages } from "./core.mjs";

const CLAIMS_KEY = Symbol.for("loom.context-engine.claims");

function enabled(value: string | undefined, fallback = true): boolean {
  if (value === undefined) return fallback;
  return !["0", "false", "off", "no"].includes(value.trim().toLowerCase());
}

function positiveInt(value: string | undefined, fallback: number): number {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function claim(pi: ExtensionAPI): boolean {
  const carrier = pi as ExtensionAPI & { [key: symbol]: unknown };
  let claims = carrier[CLAIMS_KEY] as Set<string> | undefined;
  if (!claims) {
    claims = new Set<string>();
    carrier[CLAIMS_KEY] = claims;
  }
  if (claims.has("context-governor")) return false;
  claims.add("context-governor");
  return true;
}

function forgeContextConflict(): boolean {
  if (process.env.FORGE_FOR_PI !== "1") return false;
  return enabled(process.env.FORGE_CONTEXT_INTELLIGENCE, true);
}

function sessionRuntimeDir(sessionId: string): string {
  const agentDir = process.env.PI_CODING_AGENT_DIR ?? join(process.env.HOME ?? homedir(), ".pi", "agent");
  const root = process.env.LOOM_CONTEXT_RUNTIME_DIR ?? join(agentDir, "loom-context-engine");
  return join(resolve(root), sessionId.replace(/[^a-zA-Z0-9_-]/g, "_"));
}

function record(sessionId: string, row: Record<string, unknown>): void {
  if (!enabled(process.env.LOOM_CONTEXT_ACCOUNTING, true)) return;
  try {
    const dir = sessionRuntimeDir(sessionId);
    mkdirSync(dir, { recursive: true, mode: 0o700 });
    appendFileSync(
      join(dir, "accounting.jsonl"),
      `${JSON.stringify({ timestamp: new Date().toISOString(), ...row })}\n`,
      { encoding: "utf8", mode: 0o600 },
    );
  } catch {
    // Accounting must never break a model request.
  }
}

function minimalSystemPrompt(): string {
  return [
    "You are ForgeLoom, a concise coding agent using only read, bash, edit, and write.",
    "Inspect before editing. Keep tool calls/results coherent. Prefer small, verifiable changes.",
    "Project instructions are intentionally not injected into every request to save context; read AGENTS.md and HANDOFF.md from the working tree when relevant.",
    "Do not guess omitted history: re-read exact files/evidence when needed.",
    `Current working directory: ${process.cwd()}`,
  ].join("\n");
}

/**
 * CE-001: request-local preventive governor for the retained LOOM 30B.
 *
 * The Pi session remains untouched: the context event receives a copy and the
 * returned messages apply only to the imminent LLM request.
 */
export default function loomContextEngine(pi: ExtensionAPI): void {
  if (!enabled(process.env.LOOM_CONTEXT_ENGINE, false) || !claim(pi)) return;

  const highWaterTokens = positiveInt(process.env.LOOM_CONTEXT_HIGH_WATER_TOKENS, 1600);
  const targetTokens = Math.min(positiveInt(process.env.LOOM_CONTEXT_TARGET_TOKENS, 1200), highWaterTokens);
  const toolTextChars = positiveInt(process.env.LOOM_CONTEXT_TOOL_TEXT_CHARS, 1800);
  const assistantTextChars = positiveInt(process.env.LOOM_CONTEXT_ASSISTANT_TEXT_CHARS, 900);
  let sessionId = "unknown";
  let conflictWarned = false;

  pi.on("session_start", (_event, ctx) => {
    sessionId = ctx.sessionManager.getSessionId();
    const conflict = forgeContextConflict();
    record(sessionId, {
      event: "session_start",
      highWaterTokens,
      targetTokens,
      forgeContextConflict: conflict,
    });
    if (conflict && ctx.hasUI) {
      ctx.ui.notify(
        "LOOM Context Engine is enabled while Forge Context Intelligence is also enabled. Use ForgeLoom so only one context transformer is active.",
        "warning",
      );
      conflictWarned = true;
    }
  });

  // Remove Pi's large fixed coding-agent/project-context prompt only in
  // ForgeLoom. The four tool schemas remain provider-visible, and project state
  // is read on demand from AGENTS.md/HANDOFF.md instead of paid every request.
  pi.on("before_agent_start", () => {
    const systemPrompt = minimalSystemPrompt();
    record(sessionId, { event: "system_prompt_minimized", chars: systemPrompt.length });
    return { systemPrompt };
  });

  pi.on("context", (event) => {
    if (forgeContextConflict()) {
      if (!conflictWarned) {
        record(sessionId, { event: "context_bypass", reason: "forge-context-intelligence-conflict" });
        conflictWarned = true;
      }
      return undefined;
    }

    const result = packMessages(event.messages, {
      highWaterTokens,
      targetTokens,
      toolTextChars,
      assistantTextChars,
    });

    record(sessionId, {
      event: "context_governor",
      messageCountBefore: event.messages.length,
      messageCountAfter: result.messages.length,
      changed: result.changed,
      ...result.accounting,
    });

    if (!result.changed) return undefined;
    return { messages: result.messages };
  });

  // A threshold compaction would destroy the large persistent transcript that
  // CE-001 intentionally keeps outside the model-visible working window. Cancel
  // only automatic threshold compaction. Manual compaction remains available,
  // and overflow recovery is deliberately left intact as an emergency fallback.
  pi.on("session_before_compact", (event) => {
    const cancelled = event.reason === "threshold";
    record(sessionId, {
      event: "pi_compaction_before",
      reason: event.reason,
      willRetry: event.willRetry,
      cancelled,
    });
    if (cancelled) return { cancel: true };
    return undefined;
  });

  pi.on("session_compact", (event) => {
    record(sessionId, {
      event: "pi_compaction_after",
      reason: event.reason,
      willRetry: event.willRetry,
      fromExtension: event.fromExtension,
    });
  });
}
