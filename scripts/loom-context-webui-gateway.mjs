#!/usr/bin/env node
/**
 * LOOM loopback-only llama.cpp WebUI/API gateway.
 *
 * CE-001 enforces a bounded final token envelope before forwarding chat
 * requests to the retained n_ctx=4096 model. Modern llama.cpp builds expose a
 * direct input-token endpoint. Older retained LOOM builds fall back to the
 * server's own chat-template renderer plus tokenizer, with conservative guard
 * margin and tool-schema verification.
 */
import http from "node:http";
import { appendFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { allocateOutputBudget } from "../src/forgeloom-runtime-hardening/output-budget.mjs";

const env = process.env;
const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  if (!process.argv[index]?.startsWith("--") || process.argv[index + 1] === undefined) {
    throw new Error("usage: loom-context-webui-gateway.mjs --host 127.0.0.1 --port PORT --backend-host 127.0.0.1 --backend-port PORT");
  }
  args.set(process.argv[index].slice(2), process.argv[index + 1]);
}

const host = args.get("host") ?? "127.0.0.1";
const port = Number(args.get("port"));
const backendHost = args.get("backend-host") ?? "127.0.0.1";
const backendPort = Number(args.get("backend-port"));
if (host !== "127.0.0.1" || backendHost !== "127.0.0.1" || !Number.isInteger(port) || !Number.isInteger(backendPort) || port < 1 || backendPort < 1) {
  throw new Error("gateway and backend must use valid 127.0.0.1 ports");
}

const enabled = (value) => !["0", "false", "off", "no"].includes(String(value ?? "1").trim().toLowerCase());
const positiveInt = (value, fallback) => {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
};

const ciEnabled = enabled(env.LOOM_CONTEXT_WEBUI_CI) && enabled(env.PI2_CONTEXT_INTELLIGENCE);
const hardGuardEnabled = enabled(env.LOOM_CONTEXT_WEBUI_HARD_GUARD ?? "0");
const guardFailClosed = enabled(env.LOOM_CONTEXT_WEBUI_GUARD_FAIL_CLOSED ?? "1");
const safeTotalTokens = positiveInt(env.LOOM_CONTEXT_WEBUI_SAFE_TOTAL_TOKENS, 3600);
const safeInputTokens = positiveInt(env.LOOM_CONTEXT_WEBUI_SAFE_INPUT_TOKENS, 2800);
const minOutputTokens = positiveInt(env.LOOM_CONTEXT_WEBUI_MIN_OUTPUT_TOKENS, 800);
const maxOutputTokens = positiveInt(env.LOOM_CONTEXT_WEBUI_MAX_OUTPUT_TOKENS, 1600);
const legacyCountMarginTokens = positiveInt(env.LOOM_CONTEXT_WEBUI_LEGACY_COUNT_MARGIN_TOKENS, 32);
if (
  safeTotalTokens >= 4096 ||
  safeInputTokens >= safeTotalTokens ||
  minOutputTokens >= safeTotalTokens ||
  maxOutputTokens >= safeTotalTokens ||
  maxOutputTokens < minOutputTokens ||
  safeInputTokens + minOutputTokens > safeTotalTokens
) {
  throw new Error("invalid CE token envelope: require safeInput + minOutput <= safeTotal < 4096 and minOutput <= maxOutput");
}

const runtimeDir = env.LOOM_CONTEXT_WEBUI_RUNTIME_DIR ?? join(env.PI_CODING_AGENT_DIR ?? join(env.HOME ?? homedir(), ".pi", "agent"), "context-intelligence", "loom-webui");
const accountingPath = join(runtimeDir, "accounting.jsonl");
const corePath = env.LOOM_PI2_CONTEXT_CORE ?? join(env.HOME ?? homedir(), ".pi", "agent", "extensions", "pi-minimal-plus", "pi2-context-intelligence-core.mjs");
let packPayload;
let coreStatus = ciEnabled ? "unavailable" : "disabled";
if (ciEnabled) {
  try {
    ({ packPayload } = await import(pathToFileURL(corePath).href));
    if (typeof packPayload !== "function") throw new Error("canonical core has no packPayload export");
    coreStatus = "ready";
  } catch (error) {
    console.error(`LOOM Context WebUI gateway: canonical Pi2 core unavailable; fail-open bypass (${error instanceof Error ? error.message : String(error)})`);
  }
}

function textOf(content) {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content.filter((part) => part?.type === "text" && typeof part.text === "string").map((part) => part.text).join("\n");
}
function lastUserText(messages) {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    if (messages[index]?.role === "user") return textOf(messages[index].content);
  }
  return "";
}
function record(row) {
  if (!enabled(env.LOOM_CONTEXT_WEBUI_ACCOUNTING)) return;
  try {
    mkdirSync(runtimeDir, { recursive: true, mode: 0o700 });
    appendFileSync(accountingPath, `${JSON.stringify(row)}\n`, { encoding: "utf8", mode: 0o600 });
  } catch {
    // Accounting is optional and must never affect the client request.
  }
}
function relevant(pathname) {
  return pathname === "/v1/chat/completions" || pathname === "/chat/completions" || pathname === "/v1/completions" || pathname === "/completion";
}
function isChat(pathname, payload) {
  return (pathname === "/v1/chat/completions" || pathname === "/chat/completions") && Array.isArray(payload?.messages);
}
function proxy(request, response, body) {
  const headers = { ...request.headers, host: `${backendHost}:${backendPort}` };
  if (body !== undefined) {
    headers["content-length"] = String(body.length);
    delete headers["transfer-encoding"];
  }
  const upstream = http.request({ host: backendHost, port: backendPort, method: request.method, path: request.url, headers }, (upstreamResponse) => {
    response.writeHead(upstreamResponse.statusCode ?? 502, upstreamResponse.statusMessage, upstreamResponse.headers);
    upstreamResponse.pipe(response);
  });
  upstream.on("error", (error) => {
    if (!response.headersSent) response.writeHead(502, { "content-type": "application/json" });
    response.end(JSON.stringify({ error: { message: `LOOM gateway backend unavailable: ${error.message}`, type: "gateway_error" } }));
  });
  if (body !== undefined) upstream.end(body); else request.pipe(upstream);
}
function readBody(request, limit = 16 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    request.on("data", (chunk) => {
      size += chunk.length;
      if (size > limit) {
        reject(new Error("request body exceeds 16 MiB gateway limit"));
        request.destroy();
      } else {
        chunks.push(chunk);
      }
    });
    request.on("end", () => resolve(Buffer.concat(chunks)));
    request.on("error", reject);
  });
}
function postBackendJson(pathname, payload, timeoutMs = 15000) {
  return new Promise((resolve, reject) => {
    const body = Buffer.from(JSON.stringify(payload));
    const upstream = http.request({
      host: backendHost,
      port: backendPort,
      method: "POST",
      path: pathname,
      headers: { "content-type": "application/json", "content-length": String(body.length) },
    }, (response) => {
      const chunks = [];
      response.on("data", (chunk) => chunks.push(chunk));
      response.on("end", () => {
        const raw = Buffer.concat(chunks).toString("utf8");
        const status = response.statusCode ?? 500;
        if (status < 200 || status >= 300) {
          const error = new Error(`backend token count HTTP ${status}: ${raw.slice(0, 300)}`);
          error.statusCode = status;
          reject(error);
          return;
        }
        try {
          resolve(JSON.parse(raw));
        } catch {
          reject(new Error("backend token count returned invalid JSON"));
        }
      });
    });
    upstream.setTimeout(timeoutMs, () => upstream.destroy(new Error("backend token count timed out")));
    upstream.on("error", reject);
    upstream.end(body);
  });
}

function templatePayloadFromChat(payload, includeTools) {
  const result = {
    messages: payload.messages,
    add_generation_prompt: true,
  };
  if (includeTools && Array.isArray(payload.tools) && payload.tools.length > 0) result.tools = payload.tools;
  if (includeTools && payload.tool_choice !== undefined) result.tool_choice = payload.tool_choice;
  if (payload.chat_template_kwargs && typeof payload.chat_template_kwargs === "object") result.chat_template_kwargs = payload.chat_template_kwargs;
  return result;
}
function toolNames(payload) {
  if (!Array.isArray(payload?.tools)) return [];
  return payload.tools
    .map((tool) => tool?.function?.name)
    .filter((name) => typeof name === "string" && name.length > 0);
}
async function legacyTemplateTokenCount(payload) {
  const withTools = await postBackendJson("/apply-template", templatePayloadFromChat(payload, true));
  if (typeof withTools?.prompt !== "string") throw new Error("legacy /apply-template response has no prompt");

  const names = toolNames(payload);
  if (names.length > 0) {
    const withoutTools = await postBackendJson("/apply-template", templatePayloadFromChat(payload, false));
    if (typeof withoutTools?.prompt !== "string") throw new Error("legacy /apply-template tool probe has no prompt");
    if (withoutTools.prompt === withTools.prompt) throw new Error("legacy /apply-template did not incorporate tool schemas");
    const missing = names.filter((name) => !withTools.prompt.includes(name));
    if (missing.length > 0) throw new Error(`legacy /apply-template omitted tool names: ${missing.join(", ")}`);
  }

  const tokenized = await postBackendJson("/tokenize", {
    content: withTools.prompt,
    add_special: false,
    parse_special: true,
  });
  if (!Array.isArray(tokenized?.tokens)) throw new Error("legacy /tokenize response has no tokens array");
  return {
    tokens: tokenized.tokens.length,
    guardMarginTokens: legacyCountMarginTokens,
    method: "apply-template+tokenize",
  };
}
async function exactChatInputTokens(payload) {
  try {
    const counted = await postBackendJson("/v1/chat/completions/input_tokens", payload);
    const tokens = Number(counted?.input_tokens);
    if (!Number.isInteger(tokens) || tokens < 0) throw new Error("backend token count response has no valid input_tokens");
    return { tokens, guardMarginTokens: 0, method: "chat-input-tokens" };
  } catch (error) {
    if (error?.statusCode !== 404) throw error;
    return legacyTemplateTokenCount(payload);
  }
}

function boundedPositiveInt(value, fallback, ceiling) {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  if (!Number.isFinite(parsed) || parsed <= 0) return fallback;
  return Math.min(parsed, ceiling);
}
function requestedChatOutput(payload) {
  const reserves = [];
  if (Object.prototype.hasOwnProperty.call(payload, "max_tokens")) {
    reserves.push(boundedPositiveInt(payload.max_tokens, maxOutputTokens, maxOutputTokens));
  }
  if (Object.prototype.hasOwnProperty.call(payload, "max_completion_tokens")) {
    reserves.push(boundedPositiveInt(payload.max_completion_tokens, maxOutputTokens, maxOutputTokens));
  }
  return reserves.length > 0 ? Math.max(...reserves) : maxOutputTokens;
}
function capChatOutput(payload, ceiling) {
  const next = { ...payload };
  const hasMaxTokens = Object.prototype.hasOwnProperty.call(next, "max_tokens");
  const hasMaxCompletionTokens = Object.prototype.hasOwnProperty.call(next, "max_completion_tokens");
  const reserves = [];
  if (hasMaxTokens) {
    next.max_tokens = boundedPositiveInt(next.max_tokens, ceiling, ceiling);
    reserves.push(next.max_tokens);
  }
  if (hasMaxCompletionTokens) {
    next.max_completion_tokens = boundedPositiveInt(next.max_completion_tokens, ceiling, ceiling);
    reserves.push(next.max_completion_tokens);
  }
  if (!hasMaxTokens && !hasMaxCompletionTokens) {
    next.max_tokens = ceiling;
    reserves.push(ceiling);
  }
  return { payload: next, outputReserve: Math.max(...reserves) };
}

const server = http.createServer(async (request, response) => {
  const pathname = new URL(request.url ?? "/", "http://127.0.0.1").pathname;
  if (request.method === "GET" && pathname === "/loom/context-engine/status") {
    response.writeHead(200, { "content-type": "application/json", "cache-control": "no-store" });
    return response.end(JSON.stringify({
      contextEngineGateway: true,
      hardGuardEnabled,
      safeTotalTokens,
      safeInputTokens,
      minOutputTokens,
      maxOutputTokens,
      adaptiveOutputBudget: true,
      legacyCountMarginTokens,
      physicalContextTokens: 4096,
      forbiddenReserveTokens: 4096 - safeTotalTokens,
      guardFailClosed,
      ciStatus: coreStatus,
    }));
  }
  if (request.method !== "POST" || !relevant(pathname)) return proxy(request, response);

  let original;
  try {
    original = await readBody(request);
  } catch (error) {
    response.writeHead(413, { "content-type": "application/json" });
    return response.end(JSON.stringify({ error: { message: String(error.message ?? error), type: "invalid_request_error" } }));
  }

  let outgoing = original;
  let outgoingPayload;
  let accounting = { processed: false, bypassed: true, reason: "non-json-or-non-chat", tokensBefore: 0, tokensAfter: 0, tokensRemoved: 0, wallDurationMs: 0 };
  const started = performance.now();
  try {
    const payload = JSON.parse(original.toString("utf8"));
    outgoingPayload = payload;
    if (packPayload && Array.isArray(payload?.messages)) {
      const packed = packPayload(payload, { runtimeDir, query: lastUserText(payload.messages) });
      accounting = packed.accounting;
      outgoingPayload = packed.payload;
    } else if (ciEnabled && !packPayload) {
      accounting.reason = "canonical-core-unavailable";
    } else if (Array.isArray(payload?.messages)) {
      accounting.reason = "ci-disabled";
    }
  } catch {
    accounting = { ...accounting, reason: "invalid-json-fail-open" };
  }

  if (hardGuardEnabled && outgoingPayload && isChat(pathname, outgoingPayload)) {
    try {
      const counted = await exactChatInputTokens(outgoingPayload);
      const finalInputTokens = counted.tokens;
      const guardInputTokens = finalInputTokens + counted.guardMarginTokens;
      const requestedOutputTokens = requestedChatOutput(outgoingPayload);
      const allocation = allocateOutputBudget({
        guardInputTokens,
        safeInputTokens,
        safeTotalTokens,
        minOutputTokens,
        maxOutputTokens,
        requestedOutputTokens,
      });
      const requestInputCeiling = allocation.requestInputCeiling;
      let outputReserve = 0;
      let projectedTotalTokens = allocation.projectedTotalTokens;
      let dynamicOutputCeiling = allocation.dynamicOutputCeiling;
      const blocked = allocation.blocked;

      if (!blocked) {
        const bounded = capChatOutput(outgoingPayload, dynamicOutputCeiling);
        outgoingPayload = bounded.payload;
        outputReserve = bounded.outputReserve;
        projectedTotalTokens = guardInputTokens + outputReserve;
      }

      accounting = {
        ...accounting,
        guardChecked: true,
        guardBlocked: blocked,
        tokenCountMethod: counted.method,
        tokenCountMargin: counted.guardMarginTokens,
        finalInputTokens,
        guardInputTokens,
        requestedOutputTokens,
        minOutputTokens,
        maxOutputTokens,
        dynamicOutputCeiling,
        outputReserve,
        projectedTotalTokens,
        requestInputCeiling,
        safeInputTokens,
        safeTotalTokens,
      };

      if (blocked) {
        const gatewayPreparationMs = Math.round((performance.now() - started) * 1000) / 1000;
        record({ event: "hard_guard_block", path: pathname, ciEnabled: Boolean(packPayload), coreStatus, gatewayPreparationMs, ...accounting });
        response.writeHead(413, { "content-type": "application/json" });
        return response.end(JSON.stringify({
          error: {
            message: `LOOM Context Engine blocked an unsafe request (${guardInputTokens} guarded input exceeds safe input ceiling ${requestInputCeiling}; minimum output reserve ${minOutputTokens}; safe total ${safeTotalTokens}).`,
            type: "context_guard_error",
          },
        }));
      }
      outgoing = Buffer.from(JSON.stringify(outgoingPayload));
    } catch (error) {
      accounting = {
        ...accounting,
        guardChecked: false,
        guardBlocked: guardFailClosed,
        safeInputTokens,
        safeTotalTokens,
        minOutputTokens,
        maxOutputTokens,
        guardError: error instanceof Error ? error.message : String(error),
      };
      if (guardFailClosed) {
        const gatewayPreparationMs = Math.round((performance.now() - started) * 1000) / 1000;
        record({ event: "hard_guard_unavailable", path: pathname, ciEnabled: Boolean(packPayload), coreStatus, gatewayPreparationMs, ...accounting });
        response.writeHead(503, { "content-type": "application/json" });
        return response.end(JSON.stringify({
          error: {
            message: `LOOM Context Engine could not verify the safe token envelope; request not forwarded (${accounting.guardError}).`,
            type: "context_guard_error",
          },
        }));
      }
    }
  } else if (outgoingPayload !== undefined) {
    outgoing = Buffer.from(JSON.stringify(outgoingPayload));
  }

  const gatewayPreparationMs = Math.round((performance.now() - started) * 1000) / 1000;
  record({ event: "pack", path: pathname, ciEnabled: Boolean(packPayload), coreStatus, hardGuardEnabled, gatewayPreparationMs, ...accounting });
  proxy(request, response, outgoing);
});

server.on("clientError", (_error, socket) => socket.end("HTTP/1.1 400 Bad Request\r\n\r\n"));
server.listen({ host, port, exclusive: true }, () => {
  console.log(`LOOM Context WebUI gateway listening on http://${host}:${port}; backend=http://${backendHost}:${backendPort}; ci=${coreStatus}; hard-guard=${hardGuardEnabled ? `on/input<=${safeInputTokens}, output=${minOutputTokens}-${maxOutputTokens} adaptive, total<=${safeTotalTokens}` : "off"}`);
});
