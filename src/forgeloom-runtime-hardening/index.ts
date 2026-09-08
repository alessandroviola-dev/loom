import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
  MAX_NO_PROGRESS_TRUNCATIONS,
  OUTPUT_RECOVERY_GUIDANCE,
  WORKSPACE_GROUNDING_GUIDANCE,
  continuationMessage,
  inspectPagedMutation,
  nextTruncationState,
  promptExplicitlyAllowsNewFiles,
  rewritePagedToolGuidance,
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
    const pagedBasePrompt = rewritePagedToolGuidance(event.systemPrompt);
    return {
      systemPrompt: `${pagedBasePrompt}\n${OUTPUT_RECOVERY_GUIDANCE}\n${WORKSPACE_GROUNDING_GUIDANCE}\nVerified top-level workspace entries at turn start: ${inventory}`,
    };
  });

  pi.on("tool_call", (event, ctx) => {
    if (event.toolName === "edit" || event.toolName === "write") {
      const paged = inspectPagedMutation(event.toolName, event.input);
      if (!paged.ok) {
        if (ctx.hasUI) ctx.ui.notify(paged.reason, "warning");
        return { block: true, reason: paged.reason };
      }
    }

    if (event.toolName !== "read" && event.toolName !== "write") return undefined;
    const inputPath = typeof event.input?.path === "string" ? event.input.path : "";
    if (!inputPath) return undefined;
    const absolutePath = resolve(ctx.cwd, inputPath);

    if (event.toolName === "read") {
      if (!existsSync(absolutePath)) probedMissingPaths.add(absolutePath);
      return undefined;
    }

    // In paged mode, write is reserved for explicitly requested NEW files.
    // Existing files must be changed through small edit checkpoints so work can
    // span arbitrarily many provider responses without monolithic rewrites.
    if (existsSync(absolutePath)) {
      return {
        block: true,
        reason: `ForgeLoom paged-write policy: ${inputPath} already exists. Preserve it and use one small edit replacement per provider response.`,
      };
    }

    if (allowNewFilesThisTurn) return undefined;

    const reason = probedMissingPaths.has(absolutePath)
      ? `ForgeLoom path-grounding policy: ${inputPath} was probed as missing. ENOENT is not permission to create it; inspect the actual workspace and continue with existing files.`
      : `ForgeLoom path-grounding policy: refusing unrequested new file ${inputPath}. Create new files only when the current user explicitly requests them.`;
    if (ctx.hasUI) ctx.ui.notify(reason, "warning");
    return { block: true, reason };
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

    // A truncated tool call is intentionally not executed by Pi. Queue a hidden
    // steering message for the next provider response so the fresh output budget
    // continues the same task from the durable filesystem checkpoint.
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
