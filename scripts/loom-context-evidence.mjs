#!/usr/bin/env node
import { homedir } from "node:os";
import { join, resolve } from "node:path";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";

import {
  evidencePaths,
  parseEvidenceId,
  readEvidenceById,
  searchEvidence,
  hashEvidenceMessage,
} from "../src/loom-context-engine/evidence-archive.mjs";

function runtimeRoot() {
  const agentDir = process.env.PI_CODING_AGENT_DIR ?? join(process.env.HOME ?? homedir(), ".pi", "agent");
  return resolve(process.env.LOOM_CONTEXT_RUNTIME_DIR ?? join(agentDir, "loom-context-engine"));
}

function fail(message) {
  console.error(`LOOM evidence: ${message}`);
  process.exit(1);
}

function usage() {
  console.log(`usage:
  node scripts/loom-context-evidence.mjs show <ev1-sha256>
  node scripts/loom-context-evidence.mjs search <query> [--session <id>] [--limit <n>]
  node scripts/loom-context-evidence.mjs sessions
  node scripts/loom-context-evidence.mjs verify

Environment:
  LOOM_CONTEXT_RUNTIME_DIR   override ~/.pi/agent/loom-context-engine
`);
}

function parseOption(args, name) {
  const index = args.indexOf(name);
  if (index < 0) return null;
  if (index + 1 >= args.length) fail(`${name} requires a value`);
  return args[index + 1];
}

function listSessionRefs(root, sessionName) {
  const { sessionsDir } = evidencePaths(root, "unused");
  const dir = join(sessionsDir, sessionName);
  if (!existsSync(dir) || !statSync(dir).isDirectory()) return [];
  const refs = [];
  for (const file of readdirSync(dir).sort()) {
    if (!file.endsWith(".json")) continue;
    try {
      refs.push(JSON.parse(readFileSync(join(dir, file), "utf8")));
    } catch {
      // verify reports malformed files; listing skips them.
    }
  }
  return refs;
}

const args = process.argv.slice(2);
const command = args.shift();
const root = runtimeRoot();

if (!command || ["-h", "--help", "help"].includes(command)) {
  usage();
  process.exit(0);
}

if (command === "show") {
  const evidenceId = args[0];
  if (!evidenceId) fail("show requires an evidence id");
  const blob = readEvidenceById(root, evidenceId);
  console.log(JSON.stringify(blob, null, 2));
  process.exit(0);
}

if (command === "search") {
  const sessionId = parseOption(args, "--session");
  const limitRaw = parseOption(args, "--limit");
  const limit = limitRaw === null ? 10 : Number.parseInt(limitRaw, 10);
  if (!Number.isFinite(limit) || limit <= 0) fail("--limit must be a positive integer");

  const positional = [];
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--session" || args[i] === "--limit") {
      i += 1;
      continue;
    }
    positional.push(args[i]);
  }
  const query = positional.join(" ").trim();
  if (!query) fail("search requires a query");

  const results = searchEvidence(root, { query, sessionId, limit });
  console.log(JSON.stringify({ query, sessionId, count: results.length, results }, null, 2));
  process.exit(0);
}

if (command === "sessions") {
  const { sessionsDir } = evidencePaths(root, "unused");
  if (!existsSync(sessionsDir)) {
    console.log(JSON.stringify({ count: 0, sessions: [] }, null, 2));
    process.exit(0);
  }
  const sessions = readdirSync(sessionsDir)
    .filter((name) => {
      try {
        return statSync(join(sessionsDir, name)).isDirectory();
      } catch {
        return false;
      }
    })
    .sort()
    .map((name) => ({ name, evidenceCount: listSessionRefs(root, name).length }));
  console.log(JSON.stringify({ count: sessions.length, sessions }, null, 2));
  process.exit(0);
}

if (command === "verify") {
  const { blobsDir, sessionsDir } = evidencePaths(root, "unused");
  let blobsChecked = 0;
  let refsChecked = 0;
  const errors = [];

  if (existsSync(blobsDir)) {
    for (const file of readdirSync(blobsDir).sort()) {
      if (!file.endsWith(".json")) continue;
      const path = join(blobsDir, file);
      try {
        const blob = JSON.parse(readFileSync(path, "utf8"));
        parseEvidenceId(blob.evidenceId);
        if (`${blob.sha256}.json` !== file) throw new Error("filename/hash mismatch");
        if (hashEvidenceMessage(blob.message).sha256 !== blob.sha256) throw new Error("message hash mismatch");
        blobsChecked += 1;
      } catch (error) {
        errors.push(`${path}: ${error instanceof Error ? error.message : String(error)}`);
      }
    }
  }

  if (existsSync(sessionsDir)) {
    for (const sessionName of readdirSync(sessionsDir).sort()) {
      const sessionDir = join(sessionsDir, sessionName);
      let isDir = false;
      try { isDir = statSync(sessionDir).isDirectory(); } catch {}
      if (!isDir) continue;
      for (const file of readdirSync(sessionDir).sort()) {
        if (!file.endsWith(".json")) continue;
        const path = join(sessionDir, file);
        try {
          const ref = JSON.parse(readFileSync(path, "utf8"));
          parseEvidenceId(ref.evidenceId);
          if (`${ref.sha256}.json` !== file) throw new Error("filename/hash mismatch");
          const blob = readEvidenceById(root, ref.evidenceId);
          if (blob.sha256 !== ref.sha256) throw new Error("reference/blob mismatch");
          refsChecked += 1;
        } catch (error) {
          errors.push(`${path}: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    }
  }

  console.log(JSON.stringify({ ok: errors.length === 0, blobsChecked, refsChecked, errors }, null, 2));
  process.exit(errors.length === 0 ? 0 : 1);
}

fail(`unknown command: ${command}`);
