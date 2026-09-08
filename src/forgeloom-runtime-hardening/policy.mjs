export const OUTPUT_RECOVERY_GUIDANCE = [
  "ForgeLoom has a strict response budget. Tool-call arguments must fit inside it.",
  "Keep narration before a tool call to one short sentence; reserve response budget for the tool arguments.",
  "Prefer small, targeted edit calls. For large changes, split the work into multiple independent edits instead of replacing a whole file in one call.",
  "Keep each edit/write payload compact. Re-read only the narrow region needed for the next edit.",
  "If a tool call is rejected because the response hit the output-token limit or its arguments were truncated, NEVER retry the same payload. Make the next tool call materially smaller.",
  "Do not create helper verification files unless the user explicitly requests them; use a short bash command for verification instead.",
].join("\n");

export const WORKSPACE_GROUNDING_GUIDANCE = [
  "Ground file operations in the actual workspace. Never invent companion modules or assume a file exists because its name seems plausible.",
  "A read ENOENT means that exact path was not found; it is NOT authorization to create the file.",
  "Before creating a path that was just missing, inspect the real workspace with pwd plus ls/find/git ls-files and confirm the path is genuinely required by the current task.",
  "Prefer modifying existing project files. Create a new file only when the current user request explicitly asks for one or the inspected repository structure clearly requires it.",
].join("\n");

export function promptExplicitlyAllowsNewFiles(prompt = "") {
  return /\b(create|creating|add a new|new file|new module|generate a file|crea|creare|aggiungi|aggiungere|nuovo file|nuovo modulo|genera(?:re)? un file)\b/i.test(String(prompt));
}

export function nextTruncationState(currentCount, stopReason) {
  const current = Number.isFinite(currentCount) && currentCount > 0 ? Math.trunc(currentCount) : 0;
  if (stopReason === "length") {
    const consecutive = current + 1;
    return { consecutive, shouldAbort: consecutive >= 2 };
  }
  return { consecutive: 0, shouldAbort: false };
}
