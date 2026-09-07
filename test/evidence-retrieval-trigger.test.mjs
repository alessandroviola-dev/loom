import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { archiveEvictedEvidence } from "../src/loom-context-engine/evidence-archive.mjs";
import { buildEvidenceRetrieval } from "../src/loom-context-engine/evidence-retrieval.mjs";

function withTempRoot(fn) {
  const root = mkdtempSync(join(tmpdir(), "loom-ce002-trigger-"));
  try {
    return fn(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test("generic prose does not trigger automatic lexical retrieval", () => withTempRoot((root) => {
  const evidence = { role: "assistant", content: [{ type: "text", text: "historical implementation discussion about configuration behavior" }] };
  archiveEvictedEvidence({
    rootDir: root,
    sessionId: "s1",
    originalMessages: [{ role: "user", content: "old" }, evidence],
    visibleMessages: [{ role: "user", content: "old" }],
  });

  const retrieval = buildEvidenceRetrieval({
    rootDir: root,
    sessionId: "s1",
    messages: [{ role: "user", content: "Can you explain the previous implementation and configuration behavior?" }],
  });
  assert.equal(retrieval.text, "");
  assert.equal(retrieval.lexicalCount, 0);
}));
