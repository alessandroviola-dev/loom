import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
  MAX_NO_PROGRESS_TRUNCATIONS,
  OUTPUT_RECOVERY_GUIDANCE,
  RECOVERY_MESSAGE_TYPE,
  WORKSPACE_GROUNDING_GUIDANCE,
  continuationMessage,
  detectUserLanguage,
  inspectPagedMutation,
  nextTruncationState,
  promptExplicitlyAllowsNewFiles,
  rewritePagedToolGuidance,
  sanitizeRecoveryContext,
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
  let userLanguage = "en";
  let recoveryContextActive = false;
  let recoveryNeedsCheckpoint = false;
  let continuationQueued = false;
  const probedMissingPaths = new Set<string>();

  pi.on("agent_start", () => {
    probedMissingPaths.clear();
  });

  pi.on("before_agent_start", (event, ctx) => {
    // sendMessage(... triggerTurn:true) may start another provider turn. Do not
    // mistake that internal continuation for a fresh user task: doing so would
    // clear the recovery state and allow Forge to finalize before any mutation.
    if (continuationQueued) {
      continuationQueued = false;
    } else if (!recoveryNeedsCheckpoint) {
      noProgressLengthStops = 0;
      recoveryContextActive = false;
      userLanguage = detectUserLanguage(event.prompt);
      allowNewFilesThisTurn = promptExplicitlyAllowsNewFiles(event.prompt);
    }

    const inventory = workspaceInventory(ctx.cwd);
    const pagedBasePrompt = rewritePagedToolGuidance(event.systemPrompt);
    return {
      systemPrompt: `${pagedBasePrompt}\n${OUTPUT_RECOVERY_GUIDANCE}\n${WORKSPACE_GROUNDING_GUIDANCE}\nVerified top-level workspace entries at turn start: ${inventory}`,
    };
  });

  // During automatic recovery, do not feed truncated assistant pages back to
  // the model. Pi keeps them in the persistent transcript; this is request-local
  // sanitization only, so the new provider response gets a clean working page.
  pi.on("context", (event) => {
    if (!recoveryContextActive) return undefined;
    const messages = sanitizeRecoveryContext(event.messages);
    if (messages.length === event.messages.length) return undefined;
    return { messages };
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

  pi.on("tool_execution_end", (event) => {
    if (!event.isError && (event.toolName === "edit" || event.toolName === "write")) {
      // A successful mutation is the durable checkpoint required to leave
      // recovery mode. From here the task may continue normally and may later
      // enter another independent paged-recovery cycle.
      noProgressLengthStops = 0;
      recoveryNeedsCheckpoint = false;
    }
  });

  function queueRecovery(ctx: any): void {
    recoveryContextActive = true;
    recoveryNeedsCheckpoint = true;
    const state = nextTruncationState(noProgressLengthStops, "length");
    noProgressLengthStops = state.consecutive;

    if (state.shouldAbort) {
      if (ctx.hasUI) {
        ctx.ui.notify(
          `ForgeLoom stopped after ${MAX_NO_PROGRESS_TRUNCATIONS} recovery pages without a successful edit/write checkpoint.`,
          "warning",
        );
      }
      ctx.abort();
      return;
    }

    continuationQueued = true;
    pi.sendMessage(
      {
        customType: RECOVERY_MESSAGE_TYPE,
        content: continuationMessage(state.consecutive, userLanguage),
        display: false,
        details: { page: state.consecutive, language: userLanguage },
      },
      { triggerTurn: true, deliverAs: "steer" },
    );
  }

  pi.on("message_end", (event, ctx) => {
    if (event.message.role !== "assistant") return;

    if (event.message.stopReason === "length") {
      queueRecovery(ctx);
      return;
    }

    // A recovery page is not allowed to silently become a final answer before
    // any edit/write has actually landed. Reads and other tool calls are fine;
    // Pi will naturally continue after toolUse. But a normal stop with no
    // mutation checkpoint is treated as another no-progress recovery page.
    if (recoveryNeedsCheckpoint && event.message.stopReason === "stop") {
      queueRecovery(ctx);
    }
  });
}
