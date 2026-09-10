import { createHash } from "node:crypto";
import { estimateMessagesTokens, packMessages } from "../loom-context-engine/core.mjs";
import {
  archiveEvictedEvidence,
  readEvidenceById,
  searchEvidence,
} from "../loom-context-engine/evidence-archive.mjs";

const STOPWORDS = new Set([
  "the", "and", "for", "with", "that", "this", "what", "when", "where", "which", "who", "why", "how", "was", "were", "are", "is", "it", "to", "of", "in", "on", "a", "an", "or", "do", "did", "does", "my", "your", "we", "you",
  "che", "con", "per", "come", "cosa", "quando", "dove", "quale", "quali", "chi", "perche", "perché", "era", "sono", "sei", "il", "lo", "la", "i", "gli", "le", "un", "una", "di", "da", "in", "su", "e", "o", "mi", "ti", "ci", "si", "mio", "mia", "tuo", "tua", "questo", "questa", "quello", "quella", "poi", "ancora",
]);

function textOf(content) {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .filter((part) => part?.type === "text" && typeof part.text === "string")
    .map((part) => part.text)
    .join("\n");
}

function latestUserText(messages) {
  for (let index = (messages?.length ?? 0) - 1; index >= 0; index -= 1) {
    if (messages[index]?.role === "user") return textOf(messages[index].content);
  }
  return "";
}

function normalizeId(value) {
  return String(value ?? "").trim().slice(0, 512);
}

function hashId(value) {
  return createHash("sha256").update(String(value), "utf8").digest("hex").slice(0, 24);
}

export function deriveChatSessionId(payload = {}, explicitId = "") {
  const metadata = payload?.metadata && typeof payload.metadata === "object" ? payload.metadata : {};
  const supplied = [
    explicitId,
    payload?.conversation_id,
    payload?.chat_id,
    payload?.session_id,
    metadata?.conversation_id,
    metadata?.chat_id,
    metadata?.session_id,
  ].map(normalizeId).find(Boolean);
  if (supplied) return `chat-explicit-${hashId(supplied)}`;

  const messages = Array.isArray(payload?.messages) ? payload.messages : [];
  const leadingControl = messages
    .filter((message, index) => index < 4 && (message?.role === "system" || message?.role === "developer"))
    .map((message) => `${message.role}:${textOf(message.content).slice(0, 1600)}`)
    .join("\n");
  const firstUser = messages.find((message) => message?.role === "user");
  const seed = [
    String(payload?.model ?? ""),
    leadingControl,
    firstUser ? textOf(firstUser.content).slice(0, 2400) : "",
  ].join("\n---\n");
  return `chat-derived-${hashId(seed || "empty-chat")}`;
}

function splitLeadingControl(messages) {
  const control = [];
  let index = 0;
  while (index < messages.length && (messages[index]?.role === "system" || messages[index]?.role === "developer")) {
    control.push(messages[index]);
    index += 1;
  }
  return { control, dialogue: messages.slice(index) };
}

export function packChatMessages(messages, { highWaterTokens = 1800, targetTokens = 1400 } = {}) {
  const source = Array.isArray(messages) ? messages : [];
  const { control, dialogue } = splitLeadingControl(source);
  const controlTokens = estimateMessagesTokens(control);
  const dialogueHighWater = Math.max(64, highWaterTokens - controlTokens);
  const dialogueTarget = Math.max(48, Math.min(targetTokens - controlTokens, dialogueHighWater));
  const packedDialogue = packMessages(dialogue, {
    highWaterTokens: dialogueHighWater,
    targetTokens: dialogueTarget,
    toolTextChars: 900,
    assistantTextChars: 700,
    toolArgumentTextChars: 320,
  });
  const packed = [...control, ...packedDialogue.messages];
  return {
    messages: packed,
    changed: packedDialogue.changed,
    accounting: {
      ...packedDialogue.accounting,
      controlTokens,
      beforeTokens: estimateMessagesTokens(source),
      afterTokens: estimateMessagesTokens(packed),
      highWaterTokens,
      targetTokens,
    },
  };
}

function lexicalTerms(text) {
  return [...new Set(
    String(text ?? "")
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .split(/[^a-z0-9_./:-]+/i)
      .map((token) => token.trim())
      .filter((token) => token.length >= 3 && !STOPWORDS.has(token)),
  )].slice(0, 12);
}

function clauses(text) {
  return String(text ?? "")
    .replace(/\s+/g, " ")
    .split(/;\s+|(?<=[.!?])\s+/g)
    .map((value) => value.trim())
    .filter(Boolean);
}

function looksLikeHistoricalCommand(text) {
  return /^(?:please\s+)?(?:ignore|forget|never|always|do\s+not|don't|run|execute|write|edit|create|delete|send|reply|respond|call|use|read|inspect|output|print|ask|tell|continue|stop|ignora|dimentica|non\s+|esegui|scrivi|modifica|crea|cancella|invia|rispondi|usa|leggi|stampa|chiedi|continua|fermati)\b/i.test(String(text ?? "").trim());
}

function chatEvidenceCapsule(message, terms) {
  const source = textOf(message?.content);
  if (!source) return "";
  const kept = [];
  for (const clause of clauses(source)) {
    if (looksLikeHistoricalCommand(clause)) continue;
    const lower = clause.toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "");
    if (terms.some((term) => lower.includes(term))) kept.push(clause);
  }
  return kept.join(" | ");
}

function clip(text, maxChars) {
  const value = String(text ?? "");
  if (value.length <= maxChars) return value;
  if (maxChars <= 5) return value.slice(0, Math.max(0, maxChars));
  return `${value.slice(0, maxChars - 2)}…`;
}

export function buildChatEvidenceRetrieval({ rootDir, sessionId, messages, maxChars = 520, maxItems = 2 } = {}) {
  const query = latestUserText(messages);
  const terms = lexicalTerms(query);
  if (terms.length === 0 || maxChars <= 0 || maxItems <= 0) {
    return { text: "", evidenceIds: [], chars: 0, query, terms };
  }

  const results = searchEvidence(rootDir, {
    query: terms.join(" "),
    sessionId,
    limit: Math.max(maxItems * 4, 8),
  });
  const items = [];
  for (const result of results) {
    if (items.length >= maxItems) break;
    let blob;
    try {
      blob = readEvidenceById(rootDir, result.evidenceId);
    } catch {
      continue;
    }
    const body = chatEvidenceCapsule(blob.message, terms);
    if (!body) continue;
    items.push({ evidenceId: result.evidenceId, role: result.role ?? "unknown", body });
  }
  if (items.length === 0) return { text: "", evidenceIds: [], chars: 0, query, terms };

  const header = "[LOOM recalled conversation facts; reference only. Current user message has priority.]";
  const footer = "[End recalled facts]";
  const bodyBudget = Math.max(0, maxChars - header.length - footer.length - 2);
  const lines = [];
  let used = 0;
  for (const item of items) {
    const prefix = `- ${item.role}: `;
    const remaining = bodyBudget - used - (lines.length > 0 ? 1 : 0);
    if (remaining <= prefix.length + 8) break;
    const line = `${prefix}${clip(item.body, remaining - prefix.length)}`;
    lines.push(line);
    used += line.length + (lines.length > 1 ? 1 : 0);
  }
  if (lines.length === 0) return { text: "", evidenceIds: [], chars: 0, query, terms };
  const text = `${header}\n${lines.join("\n")}\n${footer}`;
  return {
    text,
    evidenceIds: items.slice(0, lines.length).map((item) => item.evidenceId),
    chars: text.length,
    query,
    terms,
  };
}

export function injectChatRecall(messages, recallText) {
  if (!recallText) return { messages, changed: false };
  let userIndex = -1;
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    if (messages[index]?.role === "user") {
      userIndex = index;
      break;
    }
  }
  if (userIndex < 0) return { messages, changed: false };
  const original = messages[userIndex];
  const prefix = `${recallText}\n\nCurrent user message:\n`;
  let updated;
  if (typeof original.content === "string") {
    updated = { ...original, content: `${prefix}${original.content}` };
  } else if (Array.isArray(original.content)) {
    updated = { ...original, content: [{ type: "text", text: `${recallText}\n\nCurrent user message follows.` }, ...original.content] };
  } else {
    return { messages, changed: false };
  }
  const next = messages.map((message, index) => (index === userIndex ? updated : message));
  return { messages: next, changed: true };
}

export function applyChatContinuity({
  payload,
  rootDir,
  explicitSessionId = "",
  highWaterTokens = 1800,
  targetTokens = 1400,
  retrievalChars = 520,
  retrievalItems = 2,
} = {}) {
  if (!payload || !Array.isArray(payload.messages)) {
    return { payload, changed: false, accounting: { reason: "non-chat" } };
  }

  const sessionId = deriveChatSessionId(payload, explicitSessionId);
  const base = packChatMessages(payload.messages, { highWaterTokens, targetTokens });
  let finalMessages = base.messages;
  let changed = base.changed;
  let archived = { candidates: 0, blobsCreated: 0, sessionRefsCreated: 0, deduped: 0, evidenceIds: [] };

  if (base.changed) {
    archived = archiveEvictedEvidence({
      rootDir,
      sessionId,
      originalMessages: payload.messages,
      visibleMessages: base.messages,
      cwd: "loom-chat-webui",
    });
  }

  const recall = buildChatEvidenceRetrieval({
    rootDir,
    sessionId,
    messages: payload.messages,
    maxChars: retrievalChars,
    maxItems: retrievalItems,
  });

  if (recall.text) {
    const injected = injectChatRecall(base.messages, recall.text);
    if (injected.changed) {
      const candidate = packChatMessages(injected.messages, {
        highWaterTokens: targetTokens,
        targetTokens,
      });
      if (estimateMessagesTokens(candidate.messages) <= targetTokens) {
        finalMessages = candidate.messages;
        changed = true;
      }
    }
  }

  return {
    payload: changed ? { ...payload, messages: finalMessages } : payload,
    changed,
    accounting: {
      reason: changed ? "chat-continuity-packed" : "chat-continuity-noop",
      sessionId,
      beforeTokens: estimateMessagesTokens(payload.messages),
      afterTokens: estimateMessagesTokens(finalMessages),
      highWaterTokens,
      targetTokens,
      archivedCandidates: archived.candidates,
      archivedRefsCreated: archived.sessionRefsCreated,
      recalledEvidenceIds: recall.evidenceIds,
      recallChars: recall.chars,
    },
  };
}
