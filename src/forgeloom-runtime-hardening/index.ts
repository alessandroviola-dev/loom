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
  promptRequiresMutation,
  rewritePagedToolGuidance,
  sanitizeRecoveryContext,
  shouldForceRecoveryCheckpoint,
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
  let taskRequiresMutation = false;
  let taskMutationSeen = false;
  const probedMissingPaths = new Set<string>();

  pi.on("agent_start", () => {
    probedMissingPaths.clear();
  });

  pi.on("before_agent_start", (event, ctx) => {
    // Internally queued continuations are part of the same task. Any other
    // before_agent_start is a genuine new user request and starts fresh state.
    if (continuationQueued) {
      continuationQueued = false;
    } else {
      noProgressLengthStops = 0;
      recoveryContextActive = false;
      userLanguage = detectUserLanguage(event.prompt);
      allowNewFilesThisTurn = promptExplicitlyAllowsNewFiles(event.prompt);
      taskRequiresMutation = promptRequiresMutation(event.prompt);
      taskMutationSeen = false;
      recoveryNeedsCheckpoint = taskRequiresMutation;
    }

    const inventory = workspaceInventory(ctx.cwd);
    const pagedBasePrompt = rewritePagedToolGuidance(event.systemPrompt);
    return {
      systemPrompt: `${pagedBasePrompt}\n${OUTPUT_RECOVERY_GUIDANCE}\n${WORKSPACE_GROUNDING_GUIDANCE}\nVerified top-level workspace entries at turn start: ${inventory}`,
    };
  });

  // Persistent transcript fidelity is untouched. Recovery only removes failed
  // or premature pages from the request-local model view.
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
      noProgressLengthStops = 0;
      taskMutationSeen = true;
      recoveryNeedsCheckpoint = false;
    }
  });

  function queueRecovery(ctx: any, reason: "truncation" | "checkpoint"): void {
    recoveryContextActive = true;
    recoveryNeedsCheckpoint = true;
    const state = nextTruncationState(noProgressLengthStops, "length");
    noProgressLengthStops = state.consecutive;

    if (state.shouldAbort) {
      if (ctx.hasUI) {
        ctx.ui.notify(
          `ForgeLoom stopped after ${MAX_NO_PROGRESS_TRUNCATIONS} no-progress continuation pages without a successful edit/write checkpoint.`,
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
        content: continuationMessage(state.consecutive, userLanguage, reason),
        display: false,
        details: { page: state.consecutive, language: userLanguage, reason },
      },
      { triggerTurn: true, deliverAs: "steer" },
    );
  }

  pi.on("message_end", (event, ctx) => {
    if (event.message.role !== "assistant") return;

    if (event.message.stopReason === "length") {
      queueRecovery(ctx, "truncation");
      return;
    }

    // A coding/modification task cannot terminate as prose before any actual
    // mutation checkpoint. Reads/toolUse may precede the mutation; a normal stop
    // before edit/write is automatically converted into another working page.
    const mutationStillRequired = taskRequiresMutation && !taskMutationSeen;
    if (shouldForceRecoveryCheckpoint(recoveryNeedsCheckpoint || mutationStillRequired, event.message.stopReason)) {
      queueRecovery(ctx, "checkpoint");
    }
  });
}
