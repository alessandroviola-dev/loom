const DEFAULT_HIGH_WATER_TOKENS = 1600;
const DEFAULT_TARGET_TOKENS = 1200;
const DEFAULT_TOOL_TEXT_CHARS = 1800;
const DEFAULT_ASSISTANT_TEXT_CHARS = 900;
const DEFAULT_TOOL_ARGUMENT_TEXT_CHARS = 480;

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

function compactArgumentValue(value, maxChars, label) {
  if (typeof value === "string") {
    const result = compactText(value, maxChars, label);
    return { value: result.text, changed: result.changed };
  }
  if (Array.isArray(value)) {
    let changed = false;
    const next = value.map((item, index) => {
      const result = compactArgumentValue(item, maxChars, `${label}[${index}]`);
      changed ||= result.changed;
      return result.value;
    });
    return { value: changed ? next : value, changed };
  }
  if (value && typeof value === "object") {
    let changed = false;
    const next = {};
    for (const [key, item] of Object.entries(value)) {
      const result = compactArgumentValue(item, maxChars, `${label}.${key}`);
      changed ||= result.changed;
      next[key] = result.value;
    }
    return { value: changed ? next : value, changed };
  }
  return { value, changed: false };
}

function compactToolCallArguments(message, maxChars, eligibleIds = null) {
  if (message?.role !== "assistant" || !Array.isArray(message.content)) return { message, changed: false, partsChanged: 0 };
  let changed = false;
  let partsChanged = 0;
  const content = message.content.map((part) => {
    if (!part || typeof part !== "object" || part.type !== "toolCall") return part;
    const id = String(part.id ?? "");
    if (eligibleIds && !eligibleIds.has(id)) return part;
    const result = compactArgumentValue(part.arguments, maxChars, `tool call ${part.name ?? "unknown"} arguments`);
    if (!result.changed) return part;
    changed = true;
    partsChanged += 1;
    return { ...part, arguments: result.value };
  });
  return changed ? { message: { ...message, content }, changed: true, partsChanged } : { message, changed: false, partsChanged: 0 };
}

function completedToolCallIds(messages) {
  const ids = [];
  const seen = new Set();
  for (const message of messages) {
    if (message?.role !== "toolResult") continue;
    const id = String(message.toolCallId ?? "");
    if (!id || seen.has(id)) continue;
    seen.add(id);
    ids.push(id);
  }
  return ids;
}

function compactCompletedToolHistory(messages, options = {}) {
  const protectedCount = Math.max(0, Number(options.protectedCount ?? 1));
  const toolTextChars = positiveInt(options.toolTextChars, 320);
  const toolArgumentChars = positiveInt(options.toolArgumentChars, 320);
  const assistantTextChars = positiveInt(options.assistantTextChars, 260);
  const completed = completedToolCallIds(messages);
  const eligible = new Set(completed.slice(0, Math.max(0, completed.length - protectedCount)));
  if (eligible.size === 0) {
    return { messages, toolResultsCompacted: 0, assistantMessagesCompacted: 0, toolCallArgumentsCompacted: 0 };
  }

  let toolResultsCompacted = 0;
  let assistantMessagesCompacted = 0;
  let toolCallArgumentsCompacted = 0;
  const next = messages.map((message) => {
    if (message?.role === "toolResult" && eligible.has(String(message.toolCallId ?? ""))) {
      const result = compactToolResult(message, toolTextChars);
      if (result.changed) toolResultsCompacted += 1;
      return result.message;
    }
    if (message?.role === "assistant" && Array.isArray(message.content)) {
      const hasEligibleCall = message.content.some((part) => part?.type === "toolCall" && eligible.has(String(part.id ?? "")));
      if (!hasEligibleCall) return message;
      let updated = message;
      const args = compactToolCallArguments(updated, toolArgumentChars, eligible);
      if (args.changed) {
        updated = args.message;
        toolCallArgumentsCompacted += args.partsChanged;
      }
      const narration = compactAssistantNarration(updated, assistantTextChars);
      if (narration.changed) {
        updated = narration.message;
        assistantMessagesCompacted += 1;
      }
      return updated;
    }
    return message;
  });

  return { messages: next, toolResultsCompacted, assistantMessagesCompacted, toolCallArgumentsCompacted };
}

function completedToolExchangeGroups(messages) {
  const resultIds = new Set(
    messages
      .filter((message) => message?.role === "toolResult")
      .map((message) => String(message.toolCallId ?? ""))
      .filter(Boolean),
  );
  const groups = [];
  for (let index = 0; index < messages.length; index += 1) {
    const message = messages[index];
    if (message?.role !== "assistant" || !Array.isArray(message.content)) continue;
    const ids = message.content
      .filter((part) => part?.type === "toolCall")
      .map((part) => String(part.id ?? ""))
      .filter(Boolean);
    if (ids.length === 0 || !ids.every((id) => resultIds.has(id))) continue;
    groups.push({ assistantIndex: index, ids: new Set(ids) });
  }
  return groups;
}

function dropOldestCompletedToolExchange(messages, protectedCount = 1) {
  const groups = completedToolExchangeGroups(messages);
  const eligibleCount = Math.max(0, groups.length - Math.max(0, protectedCount));
  if (eligibleCount === 0) return { messages, dropped: 0, messagesDropped: 0 };
  const group = groups[0];
  let messagesDropped = 0;
  const next = messages.filter((message, index) => {
    const dropAssistant = index === group.assistantIndex;
    const dropResult = message?.role === "toolResult" && group.ids.has(String(message.toolCallId ?? ""));
    if (dropAssistant || dropResult) messagesDropped += 1;
    return !dropAssistant && !dropResult;
  });
  return { messages: next, dropped: 1, messagesDropped };
}

function flatten(turns) {
  return turns.flatMap((turn) => turn);
}

export function packMessages(messages, options = {}) {
  const highWaterTokens = positiveInt(options.highWaterTokens, DEFAULT_HIGH_WATER_TOKENS);
  const targetTokens = Math.min(positiveInt(options.targetTokens, DEFAULT_TARGET_TOKENS), highWaterTokens);
  const toolTextChars = positiveInt(options.toolTextChars, DEFAULT_TOOL_TEXT_CHARS);
  const assistantTextChars = positiveInt(options.assistantTextChars, DEFAULT_ASSISTANT_TEXT_CHARS);
  const toolArgumentTextChars = positiveInt(options.toolArgumentTextChars, DEFAULT_TOOL_ARGUMENT_TEXT_CHARS);
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
        toolCallArgumentsCompacted: 0,
        activeTurnEmergencyPasses: 0,
        activeTurnToolExchangesDropped: 0,
        activeTurnMessagesDropped: 0,
        targetMet: beforeTokens <= targetTokens,
        highWaterMet: true,
      },
    };
  }

  let turns = groupTurns(messages).map((turn) => [...turn]);
  let turnsDropped = 0;
  let toolResultsCompacted = 0;
  let assistantMessagesCompacted = 0;
  let toolCallArgumentsCompacted = 0;
  let activeTurnEmergencyPasses = 0;
  let activeTurnToolExchangesDropped = 0;
  let activeTurnMessagesDropped = 0;

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

  if (estimateMessagesTokens(packed) > targetTokens) {
    for (let index = 0; index < packed.length; index += 1) {
      if (estimateMessagesTokens(packed) <= targetTokens) break;
      const result = compactToolCallArguments(packed[index], toolArgumentTextChars);
      if (result.changed) {
        packed = packed.map((message, position) => (position === index ? result.message : message));
        toolCallArgumentsCompacted += result.partsChanged;
      }
    }
  }

  // Real coding turns can contain several completed read/edit/bash exchanges.
  // Preserve the newest exchange first, but compact older completed call/result
  // pairs together so provider sequencing remains coherent.
  if (estimateMessagesTokens(packed) > targetTokens) {
    const result = compactCompletedToolHistory(packed, {
      protectedCount: 1,
      toolTextChars: 360,
      toolArgumentChars: 300,
      assistantTextChars: 260,
    });
    packed = result.messages;
    toolResultsCompacted += result.toolResultsCompacted;
    assistantMessagesCompacted += result.assistantMessagesCompacted;
    toolCallArgumentsCompacted += result.toolCallArgumentsCompacted;
    activeTurnEmergencyPasses += 1;
  }

  // If the active turn is still too large, compact every completed exchange more
  // aggressively. The current user request is never truncated here.
  if (estimateMessagesTokens(packed) > targetTokens) {
    const result = compactCompletedToolHistory(packed, {
      protectedCount: 0,
      toolTextChars: 180,
      toolArgumentChars: 160,
      assistantTextChars: 160,
    });
    packed = result.messages;
    toolResultsCompacted += result.toolResultsCompacted;
    assistantMessagesCompacted += result.assistantMessagesCompacted;
    toolCallArgumentsCompacted += result.toolCallArgumentsCompacted;
    activeTurnEmergencyPasses += 1;
  }

  // Last resort for structurally large active turns: evict oldest *completed*
  // assistant tool-call + matching tool-result groups as whole units. This keeps
  // provider sequencing coherent and never truncates the current user request.
  while (estimateMessagesTokens(packed) > targetTokens) {
    const result = dropOldestCompletedToolExchange(packed, 1);
    if (!result.dropped) break;
    packed = result.messages;
    activeTurnToolExchangesDropped += result.dropped;
    activeTurnMessagesDropped += result.messagesDropped;
  }
  while (estimateMessagesTokens(packed) > targetTokens) {
    const result = dropOldestCompletedToolExchange(packed, 0);
    if (!result.dropped) break;
    packed = result.messages;
    activeTurnToolExchangesDropped += result.dropped;
    activeTurnMessagesDropped += result.messagesDropped;
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
      toolCallArgumentsCompacted,
      activeTurnEmergencyPasses,
      activeTurnToolExchangesDropped,
      activeTurnMessagesDropped,
      targetMet: afterTokens <= targetTokens,
      highWaterMet: afterTokens <= highWaterTokens,
    },
  };
}

export { textFromContent };
