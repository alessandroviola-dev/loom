import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import {
  archiveEvictedEvidence,
  canonicalJson,
  collectEvictedEvidence,
  evidencePaths,
  hashEvidenceMessage,
  readEvidenceById,
  searchEvidence,
} from "../src/loom-context-engine/evidence-archive.mjs";

function withTempRoot(fn) {
  const root = mkdtempSync(join(tmpdir(), "loom-ce002-"));
  try {
    return fn(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test("canonical hashing is stable across object key order", () => {
  const a = { role: "toolResult", toolCallId: "x", content: [{ type: "text", text: "alpha" }], meta: { b: 2, a: 1 } };
  const b = { meta: { a: 1, b: 2 }, content: [{ text: "alpha", type: "text" }], toolCallId: "x", role: "toolResult" };
  assert.equal(canonicalJson(a), canonicalJson(b));
  assert.equal(hashEvidenceMessage(a).evidenceId, hashEvidenceMessage(b).evidenceId);
});

test("collectEvictedEvidence uses multiset semantics and captures transformed originals", () => {
  const kept = { role: "user", content: "keep" };
  const duplicate = { role: "assistant", content: [{ type: "text", text: "same" }] };
  const tool = { role: "toolResult", toolCallId: "tc1", content: [{ type: "text", text: "ORIGINAL FULL OUTPUT" }] };
  const compactedTool = { role: "toolResult", toolCallId: "tc1", content: [{ type: "text", text: "ORIGINAL … OUTPUT" }] };

  const evicted = collectEvictedEvidence([kept, duplicate, duplicate, tool], [kept, duplicate, compactedTool]);
  assert.equal(evicted.length, 2);
  assert.equal(evicted[0].messageIndex, 2);
  assert.deepEqual(evicted[0].message, duplicate);
  assert.equal(evicted[1].messageIndex, 3);
  assert.deepEqual(evicted[1].message, tool);
});

test("archive is content-addressed, session-deduped, and exactly recoverable", () => withTempRoot((root) => {
  const original = [
    { role: "user", content: "current task" },
    { role: "assistant", content: [{ type: "toolCall", id: "tc1", name: "bash", arguments: { command: "printf SECRET_MARKER" } }] },
    { role: "toolResult", toolCallId: "tc1", content: [{ type: "text", text: "SECRET_MARKER\nfull exact output\n" }] },
  ];
  const visible = [original[0]];

  const first = archiveEvictedEvidence({
    rootDir: root,
    sessionId: "session/a",
    originalMessages: original,
    visibleMessages: visible,
    cwd: "/tmp/project",
    capturedAt: "2026-09-07T20:00:00.000Z",
  });
  assert.equal(first.candidates, 2);
  assert.equal(first.blobsCreated, 2);
  assert.equal(first.sessionRefsCreated, 2);

  const second = archiveEvictedEvidence({
    rootDir: root,
    sessionId: "session/a",
    originalMessages: original,
    visibleMessages: visible,
    cwd: "/tmp/project",
    capturedAt: "2026-09-07T20:01:00.000Z",
  });
  assert.equal(second.candidates, 2);
  assert.equal(second.blobsCreated, 0);
  assert.equal(second.sessionRefsCreated, 0);
  assert.equal(second.deduped, 2);

  const toolEvidenceId = hashEvidenceMessage(original[2]).evidenceId;
  const recovered = readEvidenceById(root, toolEvidenceId);
  assert.equal(recovered.evidenceId, toolEvidenceId);
  assert.deepEqual(recovered.message, original[2]);

  const paths = evidencePaths(root, "session/a");
  const ref = JSON.parse(readFileSync(join(paths.sessionDir, `${recovered.sha256}.json`), "utf8"));
  assert.equal(ref.sessionId, "session/a");
  assert.equal(ref.reason, "not-visible-verbatim-after-pack");
}));

test("lexical search finds archived evidence and returns stable evidence id", () => withTempRoot((root) => {
  const original = [
    { role: "user", content: "task" },
    { role: "toolResult", toolCallId: "tc9", content: [{ type: "text", text: "compiler failure: UNIQUE_NEEDLE_8472 at src/widget.ts:41" }] },
  ];
  archiveEvictedEvidence({
    rootDir: root,
    sessionId: "s1",
    originalMessages: original,
    visibleMessages: [original[0]],
    capturedAt: "2026-09-07T20:02:00.000Z",
  });

  const results = searchEvidence(root, { query: "UNIQUE_NEEDLE_8472 widget.ts", sessionId: "s1", limit: 5 });
  assert.equal(results.length, 1);
  assert.equal(results[0].evidenceId, hashEvidenceMessage(original[1]).evidenceId);
  assert.match(results[0].snippet, /UNIQUE_NEEDLE_8472/i);
}));
