import test from "node:test";
import assert from "node:assert/strict";
import { estimateMessagesTokens, groupTurns, packMessages } from "../src/loom-context-engine/core.mjs";

function user(text) {
  return { role: "user", content: [{ type: "text", text }], timestamp: 1 };
}
function assistant(text, toolCall) {
  const content = [{ type: "text", text }];
  if (toolCall) content.push({ type: "toolCall", id: toolCall, name: "bash", arguments: { command: "x" } });
  return { role: "assistant", content, timestamp: 2 };
}
function tool(text, id = "t1") {
  return { role: "toolResult", toolCallId: id, toolName: "bash", content: [{ type: "text", text }], isError: false, timestamp: 3 };
}

test("below high-water returns the same message array", () => {
  const messages = [user("small"), assistant("ok")];
  const result = packMessages(messages, { highWaterTokens: 500, targetTokens: 300 });
  assert.equal(result.changed, false);
  assert.equal(result.messages, messages);
});

test("groups complete user turns", () => {
  const messages = [user("u1"), assistant("a1", "x"), tool("r1", "x"), user("u2"), assistant("a2")];
  const turns = groupTurns(messages);
  assert.equal(turns.length, 2);
  assert.deepEqual(turns[0], messages.slice(0, 3));
  assert.deepEqual(turns[1], messages.slice(3));
});

test("drops oldest whole turns before touching the active turn", () => {
  const messages = [
    user("old ".repeat(250)),
    assistant("old answer ".repeat(200)),
    user("current request"),
    assistant("current answer"),
  ];
  const original = structuredClone(messages);
  const result = packMessages(messages, { highWaterTokens: 300, targetTokens: 120 });
  assert.equal(result.changed, true);
  assert.equal(result.accounting.turnsDropped, 1);
  assert.equal(result.messages[0].role, "user");
  assert.match(result.messages[0].content[0].text, /current request/);
  assert.deepEqual(messages, original, "persistent session input must not be mutated");
});

test("compacts oversized tool output inside the active turn", () => {
  const noisy = `${"line\n".repeat(500)}ERROR src/foo.ts:128 failed\n${"tail\n".repeat(500)}`;
  const messages = [user("fix it"), assistant("checking", "t1"), tool(noisy)];
  const before = estimateMessagesTokens(messages);
  const result = packMessages(messages, {
    highWaterTokens: Math.max(100, before - 1),
    targetTokens: 180,
    toolTextChars: 420,
    assistantTextChars: 200,
  });
  assert.equal(result.accounting.toolResultsCompacted, 1);
  const compacted = result.messages.find((message) => message.role === "toolResult");
  assert.match(compacted.content[0].text, /LOOM CE-001 compacted/);
  assert.match(compacted.content[0].text, /ERROR src\/foo\.ts:128 failed/);
  assert.ok(result.accounting.afterTokens < before);
});
