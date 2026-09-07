#!/usr/bin/env node
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { packMessages } from "../src/loom-context-engine/core.mjs";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const RUNS = join(ROOT, ".loom", "runtime", "loom-deep", "ce001-realistic");

function fail(message) {
  console.error(`CE-001 REPLAY FAIL: ${message}`);
  process.exit(1);
}

function latestRpc() {
  if (!existsSync(RUNS)) fail(`run root missing: ${RUNS}`);
  const runs = readdirSync(RUNS, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort()
    .reverse();
  for (const name of runs) {
    const path = join(RUNS, name, "rpc.jsonl");
    if (existsSync(path)) return path;
  }
  fail("no realistic rpc.jsonl found");
}

const rpcPath = process.argv[2] ? resolve(process.argv[2]) : latestRpc();
if (!existsSync(rpcPath)) fail(`RPC log missing: ${rpcPath}`);

const rows = readFileSync(rpcPath, "utf8")
  .split(/\r?\n/)
  .filter(Boolean)
  .map((line) => {
    try { return JSON.parse(line); } catch { return null; }
  })
  .filter((row) => row && typeof row === "object");

const transcript = [];
const attempts = [];
let providerAttempt = 0;

for (const row of rows) {
  if (row.type === "message_start" && row.message?.role === "assistant") {
    providerAttempt += 1;
    const result = packMessages(transcript, { highWaterTokens: 1600, targetTokens: 1200 });
    attempts.push({
      attempt: providerAttempt,
      messageCount: transcript.length,
      before: result.accounting.beforeTokens,
      after: result.accounting.afterTokens,
      reason: result.accounting.reason,
      targetMet: result.accounting.targetMet,
      highWaterMet: result.accounting.highWaterMet,
      turnsDropped: result.accounting.turnsDropped,
      toolResultsCompacted: result.accounting.toolResultsCompacted,
      assistantMessagesCompacted: result.accounting.assistantMessagesCompacted,
      toolCallArgumentsCompacted: result.accounting.toolCallArgumentsCompacted ?? 0,
      activeTurnEmergencyPasses: result.accounting.activeTurnEmergencyPasses ?? 0,
    });
  }

  if (row.type === "message_end" && row.message && typeof row.message === "object") {
    const role = row.message.role;
    if (["user", "assistant", "toolResult", "branchSummary", "compactionSummary", "custom"].includes(role)) {
      transcript.push(row.message);
    }
  }
}

if (attempts.length === 0) fail("no assistant provider attempts reconstructed from RPC log");

const misses = attempts.filter((row) => !row.targetMet);
const highWaterMisses = attempts.filter((row) => !row.highWaterMet);
const maxBy = (key) => Math.max(...attempts.map((row) => Number(row[key] ?? 0)));
const maxAfter = maxBy("after");
const maxBefore = maxBy("before");
const compactions = attempts.filter((row) => row.after < row.before).length;
const argumentCompactions = attempts.reduce((sum, row) => sum + row.toolCallArgumentsCompacted, 0);
const emergencyPasses = attempts.reduce((sum, row) => sum + row.activeTurnEmergencyPasses, 0);
const worst = [...attempts].sort((a, b) => b.after - a.after)[0];

console.log("CE-001 realistic RPC replay");
console.log(`  rpc log                  : ${rpcPath}`);
console.log(`  provider attempts        : ${attempts.length}`);
console.log(`  max raw estimate         : ${maxBefore}`);
console.log(`  max replay visible       : ${maxAfter}`);
console.log(`  governor reductions      : ${compactions}`);
console.log(`  tool-arg compactions     : ${argumentCompactions}`);
console.log(`  emergency passes         : ${emergencyPasses}`);
console.log(`  target misses (>1200)    : ${misses.length}`);
console.log(`  high-water misses (>1600): ${highWaterMisses.length}`);
console.log(`  worst replay attempt     : ${JSON.stringify(worst)}`);

if (misses.length > 0 || highWaterMisses.length > 0 || maxAfter > 1200) {
  for (const row of misses.slice(0, 5)) console.log(`  miss detail              : ${JSON.stringify(row)}`);
  fail("updated governor still cannot bound every reconstructed realistic request")
}

console.log("CE-001 REPLAY PASS: every reconstructed realistic provider view is <=1200 estimated tokens with the updated governor");
