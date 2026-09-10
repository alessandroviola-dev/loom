#!/usr/bin/env node
import http from "node:http";
import { appendFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { applyChatContinuity } from "../src/loom-chat-continuity/core.mjs";

const env = process.env;
const enabled = (value, fallback = true) => {
  if (value === undefined) return fallback;
  return !["0", "false", "off", "no"].includes(String(value).trim().toLowerCase());
};
const positiveInt = (value, fallback) => {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
};

const host = env.LOOM_CHAT_HOST ?? "127.0.0.1";
const port = positiveInt(env.LOOM_CHAT_PORT, 18082);
const upstreamHost = env.LOOM_CHAT_UPSTREAM_HOST ?? "127.0.0.1";
const upstreamPort = positiveInt(env.LOOM_CHAT_UPSTREAM_PORT, 18080);
const continuityEnabled = enabled(env.LOOM_CHAT_CONTINUITY, true);
const highWaterTokens = positiveInt(env.LOOM_CHAT_HIGH_WATER_TOKENS, 1800);
const targetTokens = Math.min(positiveInt(env.LOOM_CHAT_TARGET_TOKENS, 1400), highWaterTokens);
const retrievalChars = positiveInt(env.LOOM_CHAT_RETRIEVAL_CHARS, 520);
const retrievalItems = positiveInt(env.LOOM_CHAT_RETRIEVAL_ITEMS, 2);
const runtimeDir = env.LOOM_CHAT_RUNTIME_DIR ?? join(env.HOME ?? homedir(), "Documents", "Progetti-atitvi", "loom", ".loom", "runtime", "loom-chat");
const accountingPath = join(runtimeDir, "accounting.jsonl");

if (host !== "127.0.0.1" || upstreamHost !== "127.0.0.1") {
  throw new Error("LoomChat proxy is loopback-only");
}
if (targetTokens > highWaterTokens) throw new Error("LOOM_CHAT_TARGET_TOKENS must be <= LOOM_CHAT_HIGH_WATER_TOKENS");

function record(row) {
  if (!enabled(env.LOOM_CHAT_ACCOUNTING, true)) return;
  try {
    mkdirSync(runtimeDir, { recursive: true, mode: 0o700 });
    appendFileSync(accountingPath, `${JSON.stringify({ timestamp: new Date().toISOString(), ...row })}\n`, {
      encoding: "utf8",
      mode: 0o600,
    });
  } catch {
    // Accounting must never affect chat.
  }
}

function readBody(request, limit = 16 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    request.on("data", (chunk) => {
      size += chunk.length;
      if (size > limit) {
        reject(new Error("request body exceeds 16 MiB LoomChat limit"));
        request.destroy();
      } else {
        chunks.push(chunk);
      }
    });
    request.on("end", () => resolve(Buffer.concat(chunks)));
    request.on("error", reject);
  });
}

function proxy(request, response, body) {
  const headers = { ...request.headers, host: `${upstreamHost}:${upstreamPort}` };
  if (body !== undefined) {
    headers["content-length"] = String(body.length);
    delete headers["transfer-encoding"];
  }
  const upstream = http.request({
    host: upstreamHost,
    port: upstreamPort,
    method: request.method,
    path: request.url,
    headers,
  }, (upstreamResponse) => {
    response.writeHead(upstreamResponse.statusCode ?? 502, upstreamResponse.statusMessage, upstreamResponse.headers);
    upstreamResponse.pipe(response);
  });
  upstream.on("error", (error) => {
    if (!response.headersSent) response.writeHead(502, { "content-type": "application/json" });
    response.end(JSON.stringify({ error: { message: `LoomChat upstream unavailable: ${error.message}`, type: "gateway_error" } }));
  });
  if (body !== undefined) upstream.end(body); else request.pipe(upstream);
}

function isChatPath(pathname) {
  return pathname === "/v1/chat/completions" || pathname === "/chat/completions";
}

function isPlainChatPayload(payload) {
  return Array.isArray(payload?.messages) && (!Array.isArray(payload?.tools) || payload.tools.length === 0);
}

const server = http.createServer(async (request, response) => {
  const pathname = new URL(request.url ?? "/", "http://127.0.0.1").pathname;

  if (request.method === "GET" && pathname === "/loom/chat-continuity/status") {
    response.writeHead(200, { "content-type": "application/json", "cache-control": "no-store" });
    return response.end(JSON.stringify({
      loomChatContinuity: true,
      enabled: continuityEnabled,
      host,
      port,
      upstreamHost,
      upstreamPort,
      physicalContextTokens: 4096,
      highWaterTokens,
      targetTokens,
      retrievalChars,
      retrievalItems,
      mode: "plain-chat-only",
    }));
  }

  if (!continuityEnabled || request.method !== "POST" || !isChatPath(pathname)) {
    return proxy(request, response);
  }

  let original;
  try {
    original = await readBody(request);
  } catch (error) {
    response.writeHead(413, { "content-type": "application/json" });
    return response.end(JSON.stringify({ error: { message: String(error?.message ?? error), type: "invalid_request_error" } }));
  }

  let outgoing = original;
  const started = performance.now();
  try {
    const payload = JSON.parse(original.toString("utf8"));
    if (isPlainChatPayload(payload)) {
      const explicitSessionId = String(request.headers["x-loom-chat-session"] ?? "");
      const result = applyChatContinuity({
        payload,
        rootDir: runtimeDir,
        explicitSessionId,
        highWaterTokens,
        targetTokens,
        retrievalChars,
        retrievalItems,
      });
      outgoing = Buffer.from(JSON.stringify(result.payload));
      record({
        event: "chat_pack",
        path: pathname,
        durationMs: Math.round((performance.now() - started) * 1000) / 1000,
        ...result.accounting,
      });
    } else {
      record({ event: "chat_bypass", path: pathname, reason: "tools-present-or-invalid-messages" });
    }
  } catch (error) {
    record({
      event: "chat_pack_error",
      path: pathname,
      message: error instanceof Error ? error.message : String(error),
    });
    // Fail open into the existing 18080 hard guard. The underlying LOOM gateway
    // remains the final authority and will reject an unsafe context if needed.
  }

  return proxy(request, response, outgoing);
});

server.on("clientError", (_error, socket) => socket.end("HTTP/1.1 400 Bad Request\r\n\r\n"));
server.listen({ host, port, exclusive: true }, () => {
  console.log(`LoomChat continuity proxy listening on http://${host}:${port}; upstream=http://${upstreamHost}:${upstreamPort}; window=${targetTokens}-${highWaterTokens}; retrieval=${retrievalItems}x${retrievalChars}`);
});
