export const MAX_NO_PROGRESS_TRUNCATIONS = 4;
export const MAX_EDIT_REPLACEMENTS_PER_CALL = 1;
export const MAX_EDIT_OLD_CHARS = 500;
export const MAX_EDIT_NEW_CHARS = 1200;
export const MAX_WRITE_CHARS = 1200;
export const RECOVERY_MESSAGE_TYPE = "forgeloom-output-continuation";

export const OUTPUT_RECOVERY_GUIDANCE = [
  "FORGELOOM PAGED-CODING OVERRIDE: one provider response never needs to contain the whole patch or file.",
  "Keep assistant narration in the language of the current user's request unless code/tool syntax requires otherwise.",
  "For edit, emit EXACTLY ONE edits[] replacement per tool call. This overrides any generic Forge guidance that suggests batching multiple edits in one call.",
  `Keep edits[].oldText <= ${MAX_EDIT_OLD_CHARS} characters and edits[].newText <= ${MAX_EDIT_NEW_CHARS} characters. Make oldText the smallest exact unique anchor that works.`,
  "After a successful edit, let the tool result checkpoint the filesystem, then continue the SAME task in the next model response with another edit chunk.",
  "Do not use write to rewrite an existing file. For a legitimately new file, write only a small initial skeleton, then extend it incrementally with edit.",
  `Keep a new-file write payload <= ${MAX_WRITE_CHARS} characters.`,
  "Keep narration before a normal tool call to one short sentence; reserve response budget for tool arguments.",
  "RECOVERY EXCEPTION: after an output truncation, the task cannot finalize until a successful edit/write checkpoint lands. A narrow read is allowed only when needed to obtain an exact edit anchor.",
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

export function detectUserLanguage(prompt = "") {
  const text = String(prompt).toLowerCase();
  const matches = text.match(/\b(?:analizza|correggi|mantieni|individua|installa|istalla|modifica|mentre|spiegami|senza|della|delle|degli|questo|questa|perché|perche|quindi|file necessari)\b/g) ?? [];
  return matches.length >= 2 ? "it" : "en";
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

export function shouldForceRecoveryCheckpoint(recoveryNeedsCheckpoint, stopReason) {
  return Boolean(recoveryNeedsCheckpoint) && stopReason === "stop";
}

export function continuationMessage(attempt, language = "en") {
  const page = Number.isFinite(attempt) && attempt > 0 ? Math.trunc(attempt) : 1;
  if (language === "it") {
    return [
      `[ForgeLoom recupero pagina ${page}]`,
      "La risposta precedente è stata troncata: il relativo tool call NON è stato eseguito.",
      "NESSUNA SPIEGAZIONE in questa pagina di recupero. Non ripetere analisi o piano.",
      `Esegui SUBITO una sola tool call completa sullo STESSO task: edit con una sola sostituzione, oldText <= ${MAX_EDIT_OLD_CHARS} caratteri, newText <= ${MAX_EDIT_NEW_CHARS} caratteri.`,
      "Se ti manca l'oldText esatto puoi fare UNA read mirata; quella read NON completa il recovery e il turno successivo deve applicare l'edit.",
      "Usa lo stato attuale del filesystem come checkpoint e non ripetere il payload troncato. Il task non è concluso finché un edit/write non riesce.",
    ].join("\n");
  }
  return [
    `[ForgeLoom recovery page ${page}]`,
    "The previous response was truncated; its tool call was NOT executed.",
    "NO NARRATION on this recovery page. Do not repeat analysis or planning.",
    `Immediately issue exactly one complete tool call for the SAME task: one edit replacement, oldText <= ${MAX_EDIT_OLD_CHARS} chars, newText <= ${MAX_EDIT_NEW_CHARS} chars.`,
    "If you need the exact oldText, one narrow read is allowed; that read does NOT complete recovery and the following turn must apply the edit.",
    "Use the current filesystem as the checkpoint and do not repeat the truncated payload. The task is not complete until an edit/write succeeds.",
  ].join("\n");
}

export function sanitizeRecoveryContext(messages = []) {
  const input = Array.isArray(messages) ? messages : [];
  const truncatedToolIds = new Set();
  let lastRecoveryIndex = -1;

  for (let index = 0; index < input.length; index += 1) {
    const message = input[index];
    if (message?.customType === RECOVERY_MESSAGE_TYPE) lastRecoveryIndex = index;
    if (message?.role !== "assistant" || message?.stopReason !== "length" || !Array.isArray(message?.content)) continue;
    for (const part of message.content) {
      if (part?.type === "toolCall" && typeof part.id === "string") truncatedToolIds.add(part.id);
    }
  }

  return input.filter((message, index) => {
    if (message?.role === "assistant" && message?.stopReason === "length") return false;
    if (message?.role === "toolResult" && truncatedToolIds.has(message?.toolCallId)) return false;
    if (message?.customType === RECOVERY_MESSAGE_TYPE && index !== lastRecoveryIndex) return false;
    return true;
  });
}
