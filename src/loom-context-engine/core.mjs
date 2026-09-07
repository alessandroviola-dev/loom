const DEFAULT_HIGH_WATER_TOKENS = 1600;
const DEFAULT_TARGET_TOKENS = 1200;
const DEFAULT_TOOL_TEXT_CHARS = 1800;
const DEFAULT_ASSISTANT_TEXT_CHARS = 900;

function positiveInt(value, fallback) {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function textFromContent(content) {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .filter((part) => part && typeof part === "object" && part.type === "text" && typeof part.text === "string")
    .map((part) => part.text)
    .join("\n");
}

function stableJson(value) {
  try {
    return JSON.stringify(value) ?? "";
  } catch {
    return "";
  }
}

export function estimateMessageTokens(message) {
  if (!message || typeof message !== "object") return 1;
  let chars = 0;
  const role = message.role;

  if (typeof message.content === "string") {
    chars += message.content.length;
  } else if (Array.isArray(message.content)) {
    for (const part of message.content) {
      if (!part || typeof part !== "object") continue;
      if (part.type === "text" && typeof part.text === "string") chars += part.text.length;
      else if (part.type === "thinking" && typeof part.thinking === "string") chars += part.thinking.length;
      else if (part.type === "toolCall") {
        chars += String(part.name ?? "").length;
        chars += String(part.id ?? "").length;
        chars += stableJson(part.arguments).length;
      } else if (part.type === "image") {
        chars += 4800;
      } else {
        chars += stableJson(part).length;
      }
    }
  } else {
    chars += stableJson(message).length;
  }

  if (role === "toolResult") {
    chars += String(message.toolName ?? "").length + String(message.toolCallId ?? "").length + 32;
  } else {
    chars += String(role ?? "").length + 16;
  }

  // Deliberately conservative for the governor. Exact final accounting is done
  // by the llama.cpp gateway guard. The working thresholds intentionally leave
  // room for system/template/tool-schema overhead measured outside messages.
  return Math.max(1, Math.ceil(chars / 3) + 4);
}

export function estimateMessagesTokens(messages) {
  if (!Array.isArray(messages)) return 0;
  return messages.reduce((sum, message) => sum + estimateMessageTokens(message), 0);
}

function startsTurn(message) {
  const role = message?.role;
  return role === "user" || role === "branchSummary" || role === "compactionSummary" || role === "custom";
}

export function groupTurns(messages) {
  const turns = [];
  let current = [];
  for (const message of messages ?? []) {
    if (startsTurn(message) && current.length > 0) {
      turns.push(current);
      current = [];
    }
    current.push(message);
  }
  if (current.length > 0) turns.push(current);
  return turns;
}

function compactText(text, maxChars, label) {
  if (typeof text !== "string" || text.length <= maxChars) return { text, changed: false };
  const lines = text.split(/\r?\n/);
  const signalPattern = /(error|exception|fail(?:ed|ure)?|warning|warn|traceback|stack|assert|enoent|econn|timeout|panic|fatal|\/[^\s:]+\.[A-Za-z0-9]+(?::\d+)?|[A-Za-z0-9_.-]+\.(?:ts|tsx|js|mjs|cjs|py|sh|swift|rs|go|cpp|h|md):\d+)/i;
  const selected = [];
  const seen = new Set();
  const add = (line) => {
    if (seen.has(line)) return;
    seen.add(line);
    selected.push(line);
  };

  for (const line of lines.slice(0, 12)) add(line);
  for (const line of lines) if (signalPattern.test(line)) add(line);
  for (const line of lines.slice(-12)) add(line);

  const marker = `[LOOM CE-001 compacted ${label}; original remains in persistent session history; ${text.length} chars]`;
  const joined = selected.join("\n");
  let compacted = `${marker}\n${joined}`;
  if (compacted.length > maxChars) {
    const room = Math.max(0, maxChars - marker.length - 2);
    const head = Math.ceil(room * 0.6);
    const tail = Math.floor(room * 0.4);
    const tailText = tail > 0 ? joined.slice(-tail) : "";
    compacted = `${marker}\n${joined.slice(0, head)}${tailText ? `\n…\n${tailText}` : ""}`;
  }
  return { text: compacted, changed: true };
}

function compactToolResult(message, maxChars) {
  if (message?.role !== "toolResult" || !Array.isArray(message.content)) return { message, changed: false };
  let changed = false;
  const content = message.content.map((part) => {
    if (!part || typeof part !== "object" || part.type !== "text" || typeof part.text !== "string") return part;
    const result = compactText(part.text, maxChars, `tool result ${message.toolName ?? "unknown"}`);
    if (!result.changed) return part;
    changed = true;
    return { ...part, text: result.text };
  });
  return changed ? { message: { ...message, content }, changed: true } : { message, changed: false };
}

function compactAssistantNarration(message, maxChars) {
  if (message?.role !== "assistant" || !Array.isArray(message.content)) return { message, changed: false };
  let changed = false;
  const content = message.content.map((part) => {
    if (!part || typeof part !== "object") return part;
    if (part.type === "text" && typeof part.text === "string") {
      const result = compactText(part.text, maxChars, "assistant narration");
      if (result.changed) {
        changed = true;
        return { ...part, text: result.text };
      }
    }
    if (part.type === "thinking" && typeof part.thinking === "string" && part.thinking.length > maxChars) {
      changed = true;
      return { ...part, thinking: `[LOOM CE-001 removed stale assistant reasoning; original remains in persistent session history]` };
    }
    return part;
  });
  return changed ? { message: { ...message, content }, changed: true } : { message, changed: false };
}

function flatten(turns) {
  return turns.flatMap((turn) => turn);
}

export function packMessages(messages, options = {}) {
  const highWaterTokens = positiveInt(options.highWaterTokens, DEFAULT_HIGH_WATER_TOKENS);
  const targetTokens = Math.min(positiveInt(options.targetTokens, DEFAULT_TARGET_TOKENS), highWaterTokens);
  const toolTextChars = positiveInt(options.toolTextChars, DEFAULT_TOOL_TEXT_CHARS);
  const assistantTextChars = positiveInt(options.assistantTextChars, DEFAULT_ASSISTANT_TEXT_CHARS);
  const beforeTokens = estimateMessagesTokens(messages);

  if (beforeTokens <= highWaterTokens) {
    return {
      messages,
      changed: false,
      accounting: {
        reason: "below-high-water",
        beforeTokens,
        afterTokens: beforeTokens,
        highWaterTokens,
        targetTokens,
        turnsDropped: 0,
        toolResultsCompacted: 0,
        assistantMessagesCompacted: 0,
        targetMet: beforeTokens <= targetTokens,
        highWaterMet: true,
      },
    };
  }

  let turns = groupTurns(messages).map((turn) => [...turn]);
  let turnsDropped = 0;
  let toolResultsCompacted = 0;
  let assistantMessagesCompacted = 0;

  while (turns.length > 1 && estimateMessagesTokens(flatten(turns)) > targetTokens) {
    turns.shift();
    turnsDropped += 1;
  }

  let packed = flatten(turns);

  if (estimateMessagesTokens(packed) > targetTokens) {
    const ranked = packed
      .map((message, index) => ({ index, tokens: estimateMessageTokens(message), role: message?.role }))
      .filter((entry) => entry.role === "toolResult")
      .sort((a, b) => b.tokens - a.tokens || a.index - b.index);

    for (const entry of ranked) {
      if (estimateMessagesTokens(packed) <= targetTokens) break;
      const result = compactToolResult(packed[entry.index], toolTextChars);
      if (result.changed) {
        packed = packed.map((message, index) => (index === entry.index ? result.message : message));
        toolResultsCompacted += 1;
      }
    }
  }

  if (estimateMessagesTokens(packed) > targetTokens) {
    for (let index = 0; index < packed.length; index += 1) {
      if (estimateMessagesTokens(packed) <= targetTokens) break;
      const result = compactAssistantNarration(packed[index], assistantTextChars);
      if (result.changed) {
        packed = packed.map((message, position) => (position === index ? result.message : message));
        assistantMessagesCompacted += 1;
      }
    }
  }

  const afterTokens = estimateMessagesTokens(packed);
  return {
    messages: packed,
    changed: true,
    accounting: {
      reason: afterTokens <= targetTokens ? "compacted-to-target" : "best-effort-active-turn-too-large",
      beforeTokens,
      afterTokens,
      highWaterTokens,
      targetTokens,
      turnsDropped,
      toolResultsCompacted,
      assistantMessagesCompacted,
      targetMet: afterTokens <= targetTokens,
      highWaterMet: afterTokens <= highWaterTokens,
    },
  };
}

export { textFromContent };
