import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
  OUTPUT_RECOVERY_GUIDANCE,
  WORKSPACE_GROUNDING_GUIDANCE,
  nextTruncationState,
  promptExplicitlyAllowsNewFiles,
} from "./policy.mjs";

function workspaceInventory(cwd: string): string {
  try {
    const entries = readdirSync(cwd, { withFileTypes: true })
      .filter((entry) => entry.name !== ".git")
      .sort((a, b) => a.name.localeCompare(b.name))
      .slice(0, 80)
      .map((entry) => `${entry.name}${entry.isDirectory() ? "/" : ""}`);
    return entries.length > 0 ? entries.join(", ") : "(empty)";
  } catch {
    return "(inventory unavailable; inspect with bash before creating files)";
  }
}

export default function forgeLoomRuntimeHardening(pi: ExtensionAPI): void {
  let consecutiveLengthStops = 0;
  let allowNewFilesThisTurn = false;
  const probedMissingPaths = new Set<string>();

  pi.on("agent_start", () => {
    consecutiveLengthStops = 0;
    probedMissingPaths.clear();
  });

  pi.on("before_agent_start", (event, ctx) => {
    allowNewFilesThisTurn = promptExplicitlyAllowsNewFiles(event.prompt);
    const inventory = workspaceInventory(ctx.cwd);
    return {
      systemPrompt: `${event.systemPrompt}\n${OUTPUT_RECOVERY_GUIDANCE}\n${WORKSPACE_GROUNDING_GUIDANCE}\nVerified top-level workspace entries at turn start: ${inventory}`,
    };
  });

  pi.on("tool_call", (event, ctx) => {
    if (event.toolName !== "read" && event.toolName !== "write") return undefined;
    const inputPath = typeof event.input?.path === "string" ? event.input.path : "";
    if (!inputPath) return undefined;
    const absolutePath = resolve(ctx.cwd, inputPath);

    if (event.toolName === "read") {
      if (!existsSync(absolutePath)) probedMissingPaths.add(absolutePath);
      return undefined;
    }

    if (existsSync(absolutePath) || allowNewFilesThisTurn || !probedMissingPaths.has(absolutePath)) {
      return undefined;
    }

    if (ctx.hasUI) {
      ctx.ui.notify(
        `Blocked creation of unverified path after ENOENT probe: ${inputPath}. Inspect the workspace before creating it.`,
        "warning",
      );
    }
    return {
      block: true,
      reason: `ForgeLoom path-grounding policy: ${inputPath} was just probed as missing. Inspect the actual workspace and justify a new file instead of inventing a companion module.`,
    };
  });

  pi.on("message_end", (event, ctx) => {
    if (event.message.role !== "assistant") return;

    const stopReason = event.message.stopReason;
    const state = nextTruncationState(consecutiveLengthStops, stopReason);
    consecutiveLengthStops = state.consecutive;

    if (!state.shouldAbort) return;

    if (ctx.hasUI) {
      ctx.ui.notify(
        "ForgeLoom stopped after two consecutive output truncations. Continue with smaller edit/write calls; identical retries are blocked by policy.",
        "warning",
      );
    }
    ctx.abort();
  });
}
