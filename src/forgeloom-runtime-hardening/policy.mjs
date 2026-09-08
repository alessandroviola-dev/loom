export const MAX_NO_PROGRESS_TRUNCATIONS = 4;
export const MAX_EDIT_REPLACEMENTS_PER_CALL = 1;
export const MAX_EDIT_OLD_CHARS = 500;
export const MAX_EDIT_NEW_CHARS = 1200;
export const MAX_WRITE_CHARS = 1200;

export const OUTPUT_RECOVERY_GUIDANCE = [
  "FORGELOOM PAGED-CODING OVERRIDE: one provider response never needs to contain the whole patch or file.",
  "For edit, emit EXACTLY ONE edits[] replacement per tool call. This overrides any generic Forge guidance that suggests batching multiple edits in one call.",
  `Keep edits[].oldText <= ${MAX_EDIT_OLD_CHARS} characters and edits[].newText <= ${MAX_EDIT_NEW_CHARS} characters. Make oldText the smallest exact unique anchor that works.`,
  "After a successful edit, let the tool result checkpoint the filesystem, then continue the SAME task in the next model response with another edit chunk.",
  "Do not use write to rewrite an existing file. For a legitimately new file, write only a small initial skeleton, then extend it incrementally with edit.",
  `Keep a new-file write payload <= ${MAX_WRITE_CHARS} characters.`,
  "Keep narration before a tool call to one short sentence; reserve response budget for tool arguments.",
  "If output is truncated, NEVER restart analysis, NEVER restart the file, and NEVER repeat the same truncated payload. Resume from the last successful filesystem checkpoint with one smaller complete edit.",
  "Do not create helper verification files unless the user explicitly requests them; use a short bash command for verification instead.",
].join("\n");

export const WORKSPACE_GROUNDING_GUIDANCE = [
  "Ground file operations in the actual workspace. Never invent companion modules or assume a file exists because its name seems plausible.",
  "A read ENOENT means that exact path was not found; it is NOT authorization to create the file.",
  "Before creating a path that was just missing, inspect the real workspace with pwd plus ls/find/git ls-files and confirm the path is genuinely required by the current task.",
  "Prefer modifying existing project files. Create a new file only when the current user request explicitly asks for one or the inspected repository structure clearly requires it.",
].join("\n");

export function rewritePagedToolGuidance(systemPrompt = "") {
  let prompt = String(systemPrompt);
  const replacements = [
    [
      "Make precise file edits with exact text replacement, including multiple disjoint edits in one call",
      "Make precise file edits with exact text replacement. ForgeLoom paged mode uses one small replacement per edit call",
    ],
    [
      "When changing multiple separate locations in one file, use one edit call with multiple entries in edits[] instead of multiple edit calls",
      "ForgeLoom override: when changing multiple locations, use multiple sequential edit calls with exactly one edits[] entry per call",
    ],
    [
      "Each edits[].oldText is matched against the original file, not after earlier edits are applied. Do not emit overlapping or nested edits. Merge nearby changes into one edit.",
      "Each edit call contains one small exact replacement. After it succeeds, re-read only if necessary and continue with the next replacement in a fresh call.",
    ],
    [
      "Use write only for new files or complete rewrites.",
      "ForgeLoom override: use write only for a small new-file skeleton; never use write for a complete rewrite of an existing file.",
    ],
  ];
  for (const [from, to] of replacements) prompt = prompt.split(from).join(to);
  return prompt;
}

export function inspectPagedMutation(toolName, input = {}) {
  if (toolName === "edit") {
    const edits = Array.isArray(input?.edits) ? input.edits : [];
    if (edits.length !== MAX_EDIT_REPLACEMENTS_PER_CALL) {
      return {
        ok: false,
        reason: `ForgeLoom paged-edit policy: send exactly ${MAX_EDIT_REPLACEMENTS_PER_CALL} replacement per edit call, then continue after the successful checkpoint.`,
      };
    }
    const oldText = typeof edits[0]?.oldText === "string" ? edits[0].oldText : "";
    const newText = typeof edits[0]?.newText === "string" ? edits[0].newText : "";
    if (oldText.length > MAX_EDIT_OLD_CHARS || newText.length > MAX_EDIT_NEW_CHARS) {
      return {
        ok: false,
        reason: `ForgeLoom paged-edit policy: this replacement is too large (${oldText.length}/${newText.length} chars old/new). Keep oldText <= ${MAX_EDIT_OLD_CHARS} and newText <= ${MAX_EDIT_NEW_CHARS}, apply one chunk, then continue in the next response.`,
      };
    }
    return { ok: true };
  }

  if (toolName === "write") {
    const content = typeof input?.content === "string" ? input.content : "";
    if (content.length > MAX_WRITE_CHARS) {
      return {
        ok: false,
        reason: `ForgeLoom paged-write policy: new-file write payload is too large (${content.length} chars). Write a <= ${MAX_WRITE_CHARS}-character skeleton, then extend it with sequential edit chunks.`,
      };
    }
  }

  return { ok: true };
}

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
    `Issue exactly ONE complete edit replacement now: one edits[] entry, oldText <= ${MAX_EDIT_OLD_CHARS} chars, newText <= ${MAX_EDIT_NEW_CHARS} chars.`,
    "After that edit succeeds, continue the next chunk on the following model response. Spend almost no tokens on narration until the file changes are complete.",
  ].join("\n");
}
