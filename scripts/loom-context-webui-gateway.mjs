#!/usr/bin/env node
/**
 * LOOM loopback-only llama.cpp WebUI/API gateway.
 *
 * CE-001 adds an exact final chat-input token guard plus a bounded output
 * reserve so the operating envelope stays deliberately below physical n_ctx.
 * The historical Pi2 Context Intelligence import remains only for rollback and
 * is disabled by the ForgeLoom launcher.
 */
import http from "node:http";
import { appendFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const env = process.env;
const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  if (!process.argv[index]?.startsWith("--") || process.argv[index + 1] === undefined) throw new Error("usage: loom-context-webui-gateway.mjs --host 127.0.0.1 --port PORT --backend-host 127.0.0.1 --backend-port PORT");
  args.set(process.argv[index].slice(2), process.argv[index + 1]);
}
const host = args.get("host") ?? "127.0.0.1";
const port = Number(args.get("port"));
const backendHost = args.get("backend-host") ?? "127.0.0.1";
const backendPort = Number(args.get("backend-port"));
if (host !== "127.0.0.1" || backendHost !== "127.0.0.1" || !Number.isInteger(port) || !Number.isInteger(backendPort) || port < 1 || backendPort < 1) throw new Error("gateway and backend must use valid 127.0.0.1 ports");

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
const maxOutputTokens = positiveInt(env.LOOM_CONTEXT_WEBUI_MAX_OUTPUT_TOKENS, 800);
if (safeTotalTokens >= 4096 || safeInputTokens >= safeTotalTokens || maxOutputTokens >= safeTotalTokens || safeInputTokens + maxOutputTokens > safeTotalTokens) {
  throw new Error("invalid CE-001 token envelope: require safeInput + maxOutput <= safeTotal < 4096");
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
  for (let index = messages.length - 1; index >= 0; index -= 1) if (messages[index]?.role === "user") return textOf(messages[index].content);
  return "";
}
function record(row) {
  if (!enabled(env.LOOM_CONTEXT_WEBUI_ACCOUNTING)) return;
  try {
    mkdirSync(runtimeDir, { recursive: true, mode: 0o700 });
    appendFileSync(accountingPath, `${JSON.stringify(row)}\n`, { encoding: "utf8", mode: 0o600 });
  } catch { /* Accounting is optional and must never affect the client request. */ }
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
    const chunks = []; let size = 0;
    request.on("data", (chunk) => { size += chunk.length; if (size > limit) { reject(new Error("request body exceeds 16 MiB gateway limit")); request.destroy(); } else chunks.push(chunk); });
    request.on("end", () => resolve(Buffer.concat(chunks)));
    request.on("error", reject);
  });
}
function postBackendJson(pathname, payload, timeoutMs = 15000) {
  return new Promise((resolve, reject) => {
    const body = Buffer.from(JSON.stringify(payload));
    const request = http.request({
      host: backendHost,
      port: backendPort,
      method: "POST",
      path: pathname,
      headers: {
        "content-type": "application/json",
        "content-length": String(body.length),
      },
    }, (response) => {
      const chunks = [];
      response.on("data", (chunk) => chunks.push(chunk));
      response.on("end", () => {
        const raw = Buffer.concat(chunks).toString("utf8");
        if ((response.statusCode ?? 500) < 200 || (response.statusCode ?? 500) >= 300) {
          reject(new Error(`backend token count HTTP ${response.statusCode ?? 500}: ${raw.slice(0, 300)}`));
          return;
        }
        try { resolve(JSON.parse(raw)); } catch { reject(new Error("backend token count returned invalid JSON")); }
      });
    });
    request.setTimeout(timeoutMs, () => request.destroy(new Error("backend token count timed out")));
    request.on("error", reject);
    request.end(body);
  });
}
async function exactChatInputTokens(payload) {
  const counted = await postBackendJson("/v1/chat/completions/input_tokens", payload);
  const tokens = Number(counted?.input_tokens);
  if (!Number.isInteger(tokens) || tokens < 0) throw new Error("backend token count response has no valid input_tokens");
  return tokens;
}
function boundedPositiveInt(value, fallback, ceiling) {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  if (!Number.isFinite(parsed) || parsed <= 0) return fallback;
  return Math.min(parsed, ceiling);
}
function capChatOutput(payload) {
  const next = { ...payload };
  const hasMaxTokens = Object.prototype.hasOwnProperty.call(next, "max_tokens");
  const hasMaxCompletionTokens = Object.prototype.hasOwnProperty.call(next, "max_completion_tokens");
  const requestedMaxTokens = hasMaxTokens ? boundedPositiveInt(next.max_tokens, maxOutputTokens, maxOutputTokens) : undefined;
  const requestedMaxCompletionTokens = hasMaxCompletionTokens ? boundedPositiveInt(next.max_completion_tokens, maxOutputTokens, maxOutputTokens) : undefined;

  if (hasMaxTokens) next.max_tokens = requestedMaxTokens;
  if (hasMaxCompletionTokens) next.max_completion_tokens = requestedMaxCompletionTokens;
  if (!hasMaxTokens && !hasMaxCompletionTokens) next.max_tokens = maxOutputTokens;

  const reserves = [requestedMaxTokens, requestedMaxCompletionTokens].filter((value) => Number.isInteger(value));
  const outputReserve = reserves.length > 0 ? Math.max(...reserves) : maxOutputTokens;
  return { payload: next, outputReserve };
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
      maxOutputTokens,
      physicalContextTokens: 4096,
      forbiddenReserveTokens: 4096 - safeTotalTokens,
      guardFailClosed,
      ciStatus: coreStatus,
    }));
  }
  if (request.method !== "POST" || !relevant(pathname)) return proxy(request, response);
  let original;
  try { original = await readBody(request); } catch (error) { response.writeHead(413, { "content-type": "application/json" }); return response.end(JSON.stringify({ error: { message: String(error.message ?? error), type: "invalid_request_error" } })); }
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
    } else if (ciEnabled && !packPayload) accounting.reason = "canonical-core-unavailable";
    else if (Array.isArray(payload?.messages)) accounting.reason = "ci-disabled";
  } catch {
    accounting = { ...accounting, reason: "invalid-json-fail-open" };
  }

  if (hardGuardEnabled && outgoingPayload && isChat(pathname, outgoingPayload)) {
    try {
      const bounded = capChatOutput(outgoingPayload);
      outgoingPayload = bounded.payload;
      const outputReserve = bounded.outputReserve;
      const requestInputCeiling = Math.min(safeInputTokens, safeTotalTokens - outputReserve);
      if (requestInputCeiling <= 0) throw new Error("configured output reserve leaves no safe input budget");
      const finalInputTokens = await exactChatInputTokens(outgoingPayload);
      const projectedTotalTokens = finalInputTokens + outputReserve;
      const blocked = finalInputTokens > requestInputCeiling || projectedTotalTokens > safeTotalTokens;
      accounting = {
        ...accounting,
        guardChecked: true,
        guardBlocked: blocked,
        finalInputTokens,
        outputReserve,
        projectedTotalTokens,
        requestInputCeiling,
        safeInputTokens,
        safeTotalTokens,
        maxOutputTokens,
      };
      if (blocked) {
        const gatewayPreparationMs = Math.round((performance.now() - started) * 1000) / 1000;
        record({ event: "hard_guard_block", path: pathname, ciEnabled: Boolean(packPayload), coreStatus, gatewayPreparationMs, ...accounting });
        response.writeHead(413, { "content-type": "application/json" });
        return response.end(JSON.stringify({
          error: {
            message: `LOOM Context Engine blocked an unsafe request (${finalInputTokens} input + ${outputReserve} reserved output = ${projectedTotalTokens}; safe total ${safeTotalTokens}).`,
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
  } else if (outgoingPayload && outgoingPayload !== undefined) {
    outgoing = Buffer.from(JSON.stringify(outgoingPayload));
  }

  const gatewayPreparationMs = Math.round((performance.now() - started) * 1000) / 1000;
  record({ event: "pack", path: pathname, ciEnabled: Boolean(packPayload), coreStatus, hardGuardEnabled, gatewayPreparationMs, ...accounting });
  proxy(request, response, outgoing);
});
server.on("clientError", (_error, socket) => socket.end("HTTP/1.1 400 Bad Request\r\n\r\n"));
server.listen({ host, port, exclusive: true }, () => console.log(`LOOM Context WebUI gateway listening on http://${host}:${port}; backend=http://${backendHost}:${backendPort}; ci=${coreStatus}; hard-guard=${hardGuardEnabled ? `on/${safeInputTokens}+${maxOutputTokens}<=${safeTotalTokens}` : "off"}`));
