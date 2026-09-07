import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { archiveEvictedEvidence, hashEvidenceMessage } from "../src/loom-context-engine/evidence-archive.mjs";
import {
  buildEvidenceRetrieval,
  extractEvidenceIds,
  injectEvidenceIntoLatestUser,
  latestUserText,
} from "../src/loom-context-engine/evidence-retrieval.mjs";

function withTempRoot(fn) {
  const root = mkdtempSync(join(tmpdir(), "loom-ce002-retrieval-"));
  try {
    return fn(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test("extracts latest user text and stable explicit evidence ids", () => {
  const id = `ev1-${"a".repeat(64)}`;
  const messages = [
    { role: "user", content: "old" },
    { role: "assistant", content: [{ type: "text", text: "answer" }] },
    { role: "user", content: [{ type: "text", text: `show ${id} twice ${id}` }] },
  ];
  assert.equal(latestUserText(messages), `show ${id} twice ${id}`);
  assert.deepEqual(extractEvidenceIds(latestUserText(messages)), [id]);
});

test("explicit evidence retrieval is exact when it fits and injection is request-local", () => withTempRoot((root) => {
  const evidence = { role: "toolResult", toolCallId: "tc1", content: [{ type: "text", text: "EXACT_RECALL_9917" }] };
  archiveEvictedEvidence({
    rootDir: root,
    sessionId: "s1",
    originalMessages: [{ role: "user", content: "task" }, evidence],
    visibleMessages: [{ role: "user", content: "task" }],
  });
  const id = hashEvidenceMessage(evidence).evidenceId;
  const messages = [{ role: "user", content: `Use ${id} and report the marker.` }];
  const retrieval = buildEvidenceRetrieval({ rootDir: root, sessionId: "s1", messages, maxChars: 640, maxItems: 2 });
  assert.deepEqual(retrieval.evidenceIds, [id]);
  assert.equal(retrieval.explicitCount, 1);
  assert.equal(retrieval.exactExplicitCount, 1);
  assert.match(retrieval.text, /EXACT_RECALL_9917/);

  const injected = injectEvidenceIntoLatestUser(messages, retrieval.text);
  assert.equal(injected.changed, true);
  assert.match(injected.messages[0].content, /EXACT_RECALL_9917/);
  assert.equal(messages[0].content, `Use ${id} and report the marker.`);
}));

test("lexical retrieval is scoped to the current session", () => withTempRoot((root) => {
  const evidenceA = { role: "toolResult", toolCallId: "a", content: [{ type: "text", text: "compiler UNIQUE_SESSION_A_84721 src/widget.ts:41" }] };
  const evidenceB = { role: "toolResult", toolCallId: "b", content: [{ type: "text", text: "compiler UNIQUE_SESSION_B_84721 src/other.ts:9" }] };
  archiveEvictedEvidence({ rootDir: root, sessionId: "session-a", originalMessages: [{ role: "user", content: "a" }, evidenceA], visibleMessages: [{ role: "user", content: "a" }] });
  archiveEvictedEvidence({ rootDir: root, sessionId: "session-b", originalMessages: [{ role: "user", content: "b" }, evidenceB], visibleMessages: [{ role: "user", content: "b" }] });

  const messages = [{ role: "user", content: "What happened with UNIQUE_SESSION_A_84721 in src/widget.ts?" }];
  const sameSession = buildEvidenceRetrieval({ rootDir: root, sessionId: "session-a", messages, maxChars: 640, maxItems: 2 });
  assert.equal(sameSession.lexicalCount, 1);
  assert.match(sameSession.text, /UNIQUE_SESSION_A_84721/);
  assert.doesNotMatch(sameSession.text, /UNIQUE_SESSION_B_84721/);

  const otherSession = buildEvidenceRetrieval({ rootDir: root, sessionId: "session-b", messages, maxChars: 640, maxItems: 2 });
  assert.equal(otherSession.lexicalCount, 0);
  assert.equal(otherSession.text, "");
}));

test("retrieval output stays inside its character budget and labels clipped explicit evidence", () => withTempRoot((root) => {
  const evidence = { role: "toolResult", toolCallId: "big", content: [{ type: "text", text: `BIG_RECALL_5522 ${"x".repeat(4000)}` }] };
  archiveEvictedEvidence({
    rootDir: root,
    sessionId: "s1",
    originalMessages: [{ role: "user", content: "task" }, evidence],
    visibleMessages: [{ role: "user", content: "task" }],
  });
  const id = hashEvidenceMessage(evidence).evidenceId;
  const retrieval = buildEvidenceRetrieval({
    rootDir: root,
    sessionId: "s1",
    messages: [{ role: "user", content: `Recall ${id}` }],
    maxChars: 320,
    maxItems: 1,
  });
  assert.ok(retrieval.chars <= 320, `retrieval chars ${retrieval.chars} exceeded budget`);
  assert.equal(retrieval.exactExplicitCount, 0);
  assert.match(retrieval.text, /excerpt/);
  assert.match(retrieval.text, /BIG_RECALL_5522/);
}));
