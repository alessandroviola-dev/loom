import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
  compactToolRecoveryMessage,
  constrainPagedEditTool,
  detectUserLanguage,
  inspectPagedMutation,
  outputLimitToolResult,
  promptExplicitlyAllowsNewFiles,
  promptRequiresMutation,
  requireToolChoice,
  taskSystemGuidance,
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
    return "(inventory unavailable)";
  }
}

function rewriteTruncatedToolResult(message: any, language: string): any {
  if (message?.role !== "toolResult" || !message?.isError || !outputLimitToolResult(message.content)) return message;
  return {
    ...message,
    content: [
      {
        type: "text",
        text: compactToolRecoveryMessage(message.toolName ?? "tool", language),
      },
    ],
  };
}

export default function forgeLoomRuntimeHardening(pi: ExtensionAPI): void {
  let allowNewFilesThisTurn = false;
  let userLanguage = "en";
  let taskRequiresMutation = false;
  let taskMutationSeen = false;
  let requiredToolChoiceApplied = false;
  const probedMissingPaths = new Set<string>();

  pi.on("agent_start", () => {
    probedMissingPaths.clear();
  });

  pi.on("before_agent_start", (event, ctx) => {
    userLanguage = detectUserLanguage(event.prompt);
    allowNewFilesThisTurn = promptExplicitlyAllowsNewFiles(event.prompt);
    taskRequiresMutation = promptRequiresMutation(event.prompt);
    taskMutationSeen = false;
    requiredToolChoiceApplied = false;

    const inventory = workspaceInventory(ctx.cwd);
    return {
      systemPrompt: `${event.systemPrompt}\n${taskSystemGuidance(taskRequiresMutation)}\nVerified top-level workspace entries: ${inventory}`,
    };
  });

  // Constrain the edit schema before generation, not only after the model has
  // already emitted an oversized/batched call. llama.cpp's tool grammar can then
  // generate at most one small replacement in each provider response.
  // For mutation tasks, also require some tool until the first real filesystem
  // mutation checkpoint lands.
  pi.on("before_provider_request", (event) => {
    const constrained = constrainPagedEditTool(event.payload as any);
    const required = taskRequiresMutation && !taskMutationSeen;
    const result = requireToolChoice(constrained.payload as any, required);
    if (required && Array.isArray((result.payload as any)?.tools) && (result.payload as any).tools.length > 0) {
      requiredToolChoiceApplied = true;
    }
    return constrained.changed || result.changed ? result.payload : undefined;
  });

  // Pi already continues automatically after tool results, including failed
  // tool calls from length-truncated responses. Replace only that short error in
  // the request-local view with precise chunking guidance; never create another
  // synthetic continuation loop.
  pi.on("context", (event) => {
    let changed = false;
    const messages = event.messages.map((message: any) => {
      const next = rewriteTruncatedToolResult(message, userLanguage);
      changed ||= next !== message;
      return next;
    });
    return changed ? { messages } : undefined;
  });

  // Keep a runtime backstop even though the provider schema now expresses the
  // same paging limits. If a backend ignores the JSON-schema constraints, the
  // unsafe/batched mutation still cannot execute.
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
        reason: `ForgeLoom paged-write policy: ${inputPath} already exists. Preserve it and use edit instead of rewriting the whole file.`,
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
      taskMutationSeen = true;
    }
  });

  // Do not manufacture retries here. If the backend ever returns a normal
  // prose-only stop despite tool_choice=required, surface the real incompatibility
  // once instead of hiding it behind another continuation loop.
  pi.on("message_end", (event, ctx) => {
    if (
      event.message.role === "assistant" &&
      event.message.stopReason === "stop" &&
      taskRequiresMutation &&
      !taskMutationSeen &&
      requiredToolChoiceApplied &&
      ctx.hasUI
    ) {
      ctx.ui.notify(
        "ForgeLoom backend returned a prose-only stop despite tool_choice=required; no edit/write was executed. Stopping without synthetic retries so the provider/tool-call incompatibility is visible.",
        "warning",
      );
    }
  });
}
