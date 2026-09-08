import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
  MAX_NO_PROGRESS_TRUNCATIONS,
  OUTPUT_RECOVERY_GUIDANCE,
  WORKSPACE_GROUNDING_GUIDANCE,
  continuationMessage,
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
  let noProgressLengthStops = 0;
  let allowNewFilesThisTurn = false;
  const probedMissingPaths = new Set<string>();

  pi.on("agent_start", () => {
    noProgressLengthStops = 0;
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

  // A successful filesystem mutation is a durable checkpoint. Once progress is
  // made, later output truncations get a fresh no-progress allowance. This lets
  // a large coding task span arbitrarily many provider responses while still
  // stopping a true retry loop that never manages to apply a change.
  pi.on("tool_execution_end", (event) => {
    if (!event.isError && (event.toolName === "edit" || event.toolName === "write")) {
      noProgressLengthStops = 0;
    }
  });

  pi.on("message_end", (event, ctx) => {
    if (event.message.role !== "assistant" || event.message.stopReason !== "length") return;

    const state = nextTruncationState(noProgressLengthStops, "length");
    noProgressLengthStops = state.consecutive;

    if (state.shouldAbort) {
      if (ctx.hasUI) {
        ctx.ui.notify(
          `ForgeLoom stopped after ${MAX_NO_PROGRESS_TRUNCATIONS} output truncations without a successful edit/write checkpoint.`,
          "warning",
        );
      }
      ctx.abort();
      return;
    }

    // Pi already starts another provider turn after a truncated tool call. Add
    // a hidden steering message so that the fresh output budget is used to
    // continue the same file/task from the last successful checkpoint rather
    // than restarting or repeating the oversized payload.
    pi.sendMessage(
      {
        customType: "forgeloom-output-continuation",
        content: continuationMessage(state.consecutive),
        display: false,
        details: { page: state.consecutive },
      },
      { triggerTurn: true, deliverAs: "steer" },
    );
  });
}
