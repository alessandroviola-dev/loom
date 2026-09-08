export const OUTPUT_RECOVERY_GUIDANCE = [
  "ForgeLoom uses paged coding: one provider response does NOT need to contain the whole patch or file.",
  "Treat every successful edit/write tool call as a checkpoint. Continue the same task with another small tool call on the next model response.",
  "Keep narration before a tool call to one short sentence; reserve response budget for tool arguments.",
  "For large changes, split work into multiple independent edit/write calls instead of replacing a whole file in one response.",
  "For an existing file, preserve the file and modify targeted sections incrementally. For a legitimately new file, create only a minimal skeleton first, then extend it with small edits.",
  "If output is truncated, NEVER restart the file and NEVER repeat the same truncated payload. Resume from the last successful filesystem state with a materially smaller complete tool call.",
  "Do not create helper verification files unless the user explicitly requests them; use a short bash command for verification instead.",
].join("\n");

export const WORKSPACE_GROUNDING_GUIDANCE = [
  "Ground file operations in the actual workspace. Never invent companion modules or assume a file exists because its name seems plausible.",
  "A read ENOENT means that exact path was not found; it is NOT authorization to create the file.",
  "Before creating a path that was just missing, inspect the real workspace with pwd plus ls/find/git ls-files and confirm the path is genuinely required by the current task.",
  "Prefer modifying existing project files. Create a new file only when the current user request explicitly asks for one or the inspected repository structure clearly requires it.",
].join("\n");

export const MAX_NO_PROGRESS_TRUNCATIONS = 4;

export function promptExplicitlyAllowsNewFiles(prompt = "") {
  return /\b(create|creating|add a new|new file|new module|generate a file|crea|creare|aggiungi|aggiungere|nuovo file|nuovo modulo|genera(?:re)? un file)\b/i.test(String(prompt));
}

export function nextTruncationState(currentCount, stopReason, maxNoProgress = MAX_NO_PROGRESS_TRUNCATIONS) {
  const current = Number.isFinite(currentCount) && currentCount > 0 ? Math.trunc(currentCount) : 0;
  const limit = Number.isFinite(maxNoProgress) && maxNoProgress > 0 ? Math.trunc(maxNoProgress) : MAX_NO_PROGRESS_TRUNCATIONS;
  if (stopReason === "length") {
    const consecutive = current + 1;
    return {
      consecutive,
      shouldContinue: consecutive < limit,
      shouldAbort: consecutive >= limit,
    };
  }
  return { consecutive: 0, shouldContinue: false, shouldAbort: false };
}

export function continuationMessage(attempt) {
  const page = Number.isFinite(attempt) && attempt > 0 ? Math.trunc(attempt) : 1;
  return [
    `[ForgeLoom continuation page ${page}]`,
    "The previous model response hit its output-token limit. Continue the SAME current task; do not restart analysis or rewrite the file from the beginning.",
    "Use the last successful filesystem state as the checkpoint. The truncated tool call was not executed.",
    "Issue one materially smaller, complete edit/write call that can finish inside this response. After it succeeds, continue with the next chunk on the following model response.",
    "Spend almost no tokens on narration until the file changes are complete.",
  ].join("\n");
}
