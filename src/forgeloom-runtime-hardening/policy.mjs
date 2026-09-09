export const MAX_EDIT_REPLACEMENTS_PER_CALL = 1;
export const MAX_EDIT_OLD_CHARS = 500;
export const MAX_EDIT_NEW_CHARS = 1200;
export const MAX_WRITE_CHARS = 1200;

export function promptExplicitlyAllowsNewFiles(prompt = "") {
  const text = String(prompt);
  // Explicit prohibitions always win over generic create/add wording. This
  // prevents phrases such as "non creare file" from being misclassified as
  // permission merely because they contain the verb "creare".
  if (
    /\b(?:non\s+(?:creare|crea|aggiungere|aggiungi|generare|genera)(?:\s+(?:nuov[oi]\s+)?(?:file|modul[oi]))?|senza\s+creare\s+(?:nuov[oi]\s+)?(?:file|modul[oi])|do\s+not\s+(?:create|add|generate)(?:\s+(?:new\s+)?(?:files?|modules?))?|don't\s+(?:create|add|generate)(?:\s+(?:new\s+)?(?:files?|modules?))?|without\s+creating\s+(?:new\s+)?(?:files?|modules?))\b/i.test(text)
  ) {
    return false;
  }
  return /\b(create|creating|add a new|new file|new module|generate a file|crea|creare|aggiungi|aggiungere|nuovo file|nuovo modulo|genera(?:re)? un file)\b/i.test(text);
}

export function promptRequiresMutation(prompt = "") {
  const text = String(prompt);
  // Scoped constraints such as "non modificare le righe X" must not turn a
  // mutation task into read-only. Only explicit whole-task prohibitions do.
  const explicitReadOnly = /\b(?:solo\s+lettura|read\s*only|non\s+(?:modificare|cambiare|scrivere|toccare)\s+(?:nulla|niente|il\s+file|questo\s+file|alcun\s+file|nessun\s+file)|do\s+not\s+(?:edit|modify|write|change)\s+(?:anything|the\s+file|this\s+file|any\s+files?))\b/i.test(text);
  if (explicitReadOnly) return false;
  return /\b(?:correggi|correggere|modifica|modificare|aggiorna|aggiornare|implementa|implementare|sistema|sistemare|rifattorizza|refactor|fix|repair|edit|modify|update|implement|rewrite|change)\b/i.test(text);
}

export function detectUserLanguage(prompt = "") {
  const text = String(prompt).toLowerCase();
  const matches = text.match(/\b(?:analizza|correggi|mantieni|individua|installa|istalla|modifica|mentre|spiegami|senza|della|delle|degli|questo|questa|perché|perche|quindi|file necessari)\b/g) ?? [];
  return matches.length >= 2 ? "it" : "en";
}

export function taskSystemGuidance(requiresMutation = false) {
  const lines = [
    "FORGELOOM NATIVE PAGED CODING: Pi automatically continues after tool results; never try to fit the whole task or patch in one model response.",
    `The provider schema for edit is constrained to exactly one replacement per call, with oldText <= ${MAX_EDIT_OLD_CHARS} chars and newText <= ${MAX_EDIT_NEW_CHARS} chars. After a successful edit result, continue the same task with the next edit chunk in the next provider call.`,
    "Narration may be one short sentence, but working turns should use tools. Do not use write to replace an existing file and do not invent companion files.",
  ];
  if (requiresMutation) {
    lines.push("CURRENT TASK REQUIRES A REAL FILE/CODE CHANGE: a prose-only response is not completion. Begin/continue work with a tool call; at least one edit/write must succeed before a normal final answer.");
  }
  return lines.join("\n");
}

function constrainEditParameters(parameters) {
  if (!parameters || typeof parameters !== "object") return { parameters, changed: false };
  const properties = parameters.properties;
  const edits = properties?.edits;
  const items = edits?.items;
  if (!edits || typeof edits !== "object" || !items || typeof items !== "object") {
    return { parameters, changed: false };
  }

  const itemProperties = items.properties && typeof items.properties === "object" ? items.properties : {};
  const oldText = itemProperties.oldText && typeof itemProperties.oldText === "object" ? itemProperties.oldText : {};
  const newText = itemProperties.newText && typeof itemProperties.newText === "object" ? itemProperties.newText : {};

  const nextEdits = {
    ...edits,
    minItems: 1,
    maxItems: MAX_EDIT_REPLACEMENTS_PER_CALL,
    description: "Exactly one targeted replacement. Pi continues automatically after the tool result; use the next provider call for the next replacement.",
    items: {
      ...items,
      properties: {
        ...itemProperties,
        oldText: {
          ...oldText,
          maxLength: MAX_EDIT_OLD_CHARS,
          description: `Exact unique text for one targeted replacement; at most ${MAX_EDIT_OLD_CHARS} characters.`,
        },
        newText: {
          ...newText,
          maxLength: MAX_EDIT_NEW_CHARS,
          description: `Replacement text for this one targeted edit; at most ${MAX_EDIT_NEW_CHARS} characters.`,
        },
      },
    },
  };

  return {
    parameters: {
      ...parameters,
      properties: {
        ...properties,
        edits: nextEdits,
      },
    },
    changed: true,
  };
}

export function constrainPagedEditTool(payload) {
  if (!payload || typeof payload !== "object" || !Array.isArray(payload.tools)) {
    return { payload, changed: false };
  }

  let changed = false;
  const tools = payload.tools.map((tool) => {
    if (!tool || typeof tool !== "object" || tool?.function?.name !== "edit") return tool;
    const constrained = constrainEditParameters(tool.function.parameters);
    if (!constrained.changed) return tool;
    changed = true;
    return {
      ...tool,
      function: {
        ...tool.function,
        description: "Edit one file with exactly one small exact replacement per tool call. Pi will continue automatically for subsequent chunks.",
        parameters: constrained.parameters,
      },
    };
  });

  return changed ? { payload: { ...payload, tools }, changed: true } : { payload, changed: false };
}

export function inspectPagedMutation(toolName, input = {}) {
  if (toolName === "edit") {
    const edits = Array.isArray(input?.edits) ? input.edits : [];
    if (edits.length !== MAX_EDIT_REPLACEMENTS_PER_CALL) {
      return {
        ok: false,
        reason: `ForgeLoom paged-edit policy: send exactly ${MAX_EDIT_REPLACEMENTS_PER_CALL} replacement per edit call. Pi will continue automatically after the tool result.`,
      };
    }
    const oldText = typeof edits[0]?.oldText === "string" ? edits[0].oldText : "";
    const newText = typeof edits[0]?.newText === "string" ? edits[0].newText : "";
    if (oldText.length > MAX_EDIT_OLD_CHARS || newText.length > MAX_EDIT_NEW_CHARS) {
      return {
        ok: false,
        reason: `ForgeLoom paged-edit policy: replacement too large (${oldText.length}/${newText.length} chars old/new). Use one smaller edit: oldText <= ${MAX_EDIT_OLD_CHARS}, newText <= ${MAX_EDIT_NEW_CHARS}.`,
      };
    }
  }
  if (toolName === "write") {
    const content = typeof input?.content === "string" ? input.content : "";
    if (content.length > MAX_WRITE_CHARS) {
      return {
        ok: false,
        reason: `ForgeLoom paged-write policy: new-file payload too large (${content.length} chars). Write <= ${MAX_WRITE_CHARS} chars, then extend incrementally with edit.`,
      };
    }
  }
  return { ok: true };
}

export function requireToolChoice(payload, required) {
  if (!required || !payload || typeof payload !== "object") return { payload, changed: false };
  const tools = Array.isArray(payload.tools) ? payload.tools : [];
  if (tools.length === 0) return { payload, changed: false };
  return {
    payload: {
      ...payload,
      tool_choice: "required",
      parallel_tool_calls: false,
    },
    changed: payload.tool_choice !== "required" || payload.parallel_tool_calls !== false,
  };
}

export function outputLimitToolResult(content = []) {
  const text = (Array.isArray(content) ? content : [])
    .filter((part) => part?.type === "text" && typeof part.text === "string")
    .map((part) => part.text)
    .join("\n");
  return /response hit the output token limit|arguments may be truncated|output token limit/i.test(text);
}

export function compactToolRecoveryMessage(toolName = "tool", language = "en") {
  if (language === "it") {
    return `ForgeLoom: ${toolName} NON eseguito perché la tool call è stata troncata. Pi sta già continuando con una nuova chiamata e un nuovo budget output. Non ripetere la patch intera: emetti subito UNA tool call completa e più piccola; per edit usa una sola sostituzione con oldText <= ${MAX_EDIT_OLD_CHARS} e newText <= ${MAX_EDIT_NEW_CHARS} caratteri.`;
  }
  return `ForgeLoom: ${toolName} was NOT executed because the tool call was truncated. Pi is already continuing with a fresh provider call and fresh output budget. Do not repeat the whole patch: immediately emit ONE smaller complete tool call; for edit use one replacement with oldText <= ${MAX_EDIT_OLD_CHARS} and newText <= ${MAX_EDIT_NEW_CHARS} chars.`;
}
