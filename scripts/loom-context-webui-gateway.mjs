#!/usr/bin/env node
/**
 * LOOM_CONTEXT_WEBUI_001: loopback-only llama.cpp WebUI/API gateway.
 * It imports the canonical global Pi2 Context Intelligence core; it does not
 * implement or fork the packing algorithm.
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
const ciEnabled = enabled(env.LOOM_CONTEXT_WEBUI_CI) && enabled(env.PI2_CONTEXT_INTELLIGENCE);
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

const server = http.createServer(async (request, response) => {
	const pathname = new URL(request.url ?? "/", "http://127.0.0.1").pathname;
	if (request.method !== "POST" || !relevant(pathname)) return proxy(request, response);
	let original;
	try { original = await readBody(request); } catch (error) { response.writeHead(413, { "content-type": "application/json" }); return response.end(JSON.stringify({ error: { message: String(error.message ?? error), type: "invalid_request_error" } })); }
	let outgoing = original;
	let accounting = { processed: false, bypassed: true, reason: "non-json-or-non-chat", tokensBefore: 0, tokensAfter: 0, tokensRemoved: 0, wallDurationMs: 0 };
	const started = performance.now();
	try {
		const payload = JSON.parse(original.toString("utf8"));
		if (packPayload && Array.isArray(payload?.messages)) {
			const packed = packPayload(payload, { runtimeDir, query: lastUserText(payload.messages) });
			accounting = packed.accounting;
			if (packed.payload !== payload) outgoing = Buffer.from(JSON.stringify(packed.payload));
		} else if (ciEnabled && !packPayload) accounting.reason = "canonical-core-unavailable";
		else if (Array.isArray(payload?.messages)) accounting.reason = "ci-disabled";
	} catch {
		accounting = { ...accounting, reason: "invalid-json-fail-open" };
	}
	const gatewayPreparationMs = Math.round((performance.now() - started) * 1000) / 1000;
	record({ event: "pack", path: pathname, ciEnabled: Boolean(packPayload), coreStatus, gatewayPreparationMs, ...accounting });
	proxy(request, response, outgoing);
});
server.on("clientError", (_error, socket) => socket.end("HTTP/1.1 400 Bad Request\r\n\r\n"));
server.listen({ host, port, exclusive: true }, () => console.log(`LOOM Context WebUI gateway listening on http://${host}:${port}; backend=http://${backendHost}:${backendPort}; ci=${coreStatus}`));
