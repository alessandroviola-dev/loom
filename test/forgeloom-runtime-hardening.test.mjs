import test from "node:test";
import assert from "node:assert/strict";

import {
  MAX_EDIT_NEW_CHARS,
  MAX_EDIT_OLD_CHARS,
  MAX_NO_PROGRESS_TRUNCATIONS,
  OUTPUT_RECOVERY_GUIDANCE,
  RECOVERY_MESSAGE_TYPE,
  WORKSPACE_GROUNDING_GUIDANCE,
  continuationMessage,
  detectUserLanguage,
  inspectPagedMutation,
  nextTruncationState,
  promptExplicitlyAllowsNewFiles,
  rewritePagedToolGuidance,
  sanitizeRecoveryContext,
} from "../src/forgeloom-runtime-hardening/policy.mjs";
import { allocateOutputBudget } from "../src/forgeloom-runtime-hardening/output-budget.mjs";

test("length stops request fresh continuation pages before aborting", () => {
  assert.deepEqual(nextTruncationState(0, "length"), {
    consecutive: 1,
    shouldContinue: true,
    shouldAbort: false,
  });
  assert.deepEqual(nextTruncationState(2, "length"), {
    consecutive: 3,
    shouldContinue: true,
    shouldAbort: false,
  });
});

test("only repeated no-progress truncations trip the runaway guard", () => {
  assert.equal(MAX_NO_PROGRESS_TRUNCATIONS, 4);
  assert.deepEqual(nextTruncationState(3, "length"), {
    consecutive: 4,
    shouldContinue: false,
    shouldAbort: true,
  });
});

test("non-length assistant stop clears truncation state", () => {
  assert.deepEqual(nextTruncationState(2, "toolUse"), {
    consecutive: 0,
    shouldContinue: false,
    shouldAbort: false,
  });
  assert.deepEqual(nextTruncationState(2, "stop"), {
    consecutive: 0,
    shouldContinue: false,
    shouldAbort: false,
  });
});

test("continuation message is language-aware and tool-first", () => {
  const italian = continuationMessage(2, "it");
  assert.match(italian, /recupero pagina 2/i);
  assert.match(italian, /NESSUNA SPIEGAZIONE/);
  assert.match(italian, /Esegui SUBITO una sola tool call/);
  assert.match(italian, /torna a parlare in italiano/i);

  const english = continuationMessage(2, "en");
  assert.match(english, /recovery page 2/i);
  assert.match(english, /NO NARRATION/);
  assert.match(english, /Immediately issue exactly one complete tool call/);
});

test("user language detection keeps Italian recovery in Italian", () => {
  assert.equal(detectUserLanguage("Analizza questo file, correggi gli errori e spiegami cosa fai mentre lavori"), "it");
  assert.equal(detectUserLanguage("Analyze this file and fix the errors"), "en");
});

test("recovery context drops truncated pages, failed truncated tool results and stale continuation messages", () => {
  const messages = [
    { role: "user", content: [{ type: "text", text: "task" }] },
    {
      role: "assistant",
      stopReason: "length",
      content: [{ type: "toolCall", id: "tc1", name: "edit", arguments: {} }],
    },
    { role: "toolResult", toolCallId: "tc1", content: [{ type: "text", text: "not executed" }] },
    { role: "custom", customType: RECOVERY_MESSAGE_TYPE, content: "old recovery" },
    {
      role: "assistant",
      stopReason: "length",
      content: [{ type: "text", text: "repeated narration" }],
    },
    { role: "custom", customType: RECOVERY_MESSAGE_TYPE, content: "latest recovery" },
  ];
  const sanitized = sanitizeRecoveryContext(messages);
  assert.deepEqual(sanitized, [
    messages[0],
    messages[5],
  ]);
});

test("Forge generic batch-edit guidance is rewritten for paged mode", () => {
  const source = [
    "Make precise file edits with exact text replacement, including multiple disjoint edits in one call",
    "When changing multiple separate locations in one file, use one edit call with multiple entries in edits[] instead of multiple edit calls",
    "Use write only for new files or complete rewrites.",
  ].join("\n");
  const rewritten = rewritePagedToolGuidance(source);
  assert.doesNotMatch(rewritten, /multiple entries in edits\[\] instead of multiple edit calls/);
  assert.doesNotMatch(rewritten, /complete rewrites/);
  assert.match(rewritten, /multiple sequential edit calls/);
  assert.match(rewritten, /small new-file skeleton/);
});

test("paged mutation policy allows one small edit and blocks batching", () => {
  assert.deepEqual(
    inspectPagedMutation("edit", { edits: [{ oldText: "a", newText: "b" }] }),
    { ok: true },
  );
  const batched = inspectPagedMutation("edit", {
    edits: [
      { oldText: "a", newText: "b" },
      { oldText: "c", newText: "d" },
    ],
  });
  assert.equal(batched.ok, false);
  assert.match(batched.reason, /exactly 1 replacement/i);
});

test("paged mutation policy blocks oversized edit and write payloads", () => {
  const largeEdit = inspectPagedMutation("edit", {
    edits: [{ oldText: "x".repeat(MAX_EDIT_OLD_CHARS + 1), newText: "y" }],
  });
  assert.equal(largeEdit.ok, false);

  const largeNewText = inspectPagedMutation("edit", {
    edits: [{ oldText: "x", newText: "y".repeat(MAX_EDIT_NEW_CHARS + 1) }],
  });
  assert.equal(largeNewText.ok, false);

  const largeWrite = inspectPagedMutation("write", { content: "z".repeat(1201) });
  assert.equal(largeWrite.ok, false);
});

test("system guidance uses paged coding and forbids invented paths", () => {
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /PAGED-CODING OVERRIDE/i);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /language of the current user's request/i);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /EXACTLY ONE edits\[\] replacement/i);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /RECOVERY EXCEPTION/i);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /NEVER restart analysis/i);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /Do not create helper verification files/);
  assert.match(WORKSPACE_GROUNDING_GUIDANCE, /Never invent companion modules/);
  assert.match(WORKSPACE_GROUNDING_GUIDANCE, /ENOENT.*NOT authorization/i);
});

test("new-file permission is explicit rather than inferred from generic repair prompts", () => {
  assert.equal(promptExplicitlyAllowsNewFiles("Correggi wifi_hacker.py e installa le dipendenze necessarie"), false);
  assert.equal(promptExplicitlyAllowsNewFiles("Crea un nuovo file helper.py"), true);
  assert.equal(promptExplicitlyAllowsNewFiles("Create a new module for parsing"), true);
});

test("adaptive output budget keeps original 800-token floor while using spare headroom", () => {
  assert.deepEqual(
    allocateOutputBudget({ guardInputTokens: 1200, requestedOutputTokens: 1600 }),
    {
      blocked: false,
      requestInputCeiling: 2800,
      dynamicOutputCeiling: 1600,
      outputReserve: 1600,
      projectedTotalTokens: 2800,
    },
  );
  assert.deepEqual(
    allocateOutputBudget({ guardInputTokens: 2400, requestedOutputTokens: 1600 }),
    {
      blocked: false,
      requestInputCeiling: 2800,
      dynamicOutputCeiling: 1200,
      outputReserve: 1200,
      projectedTotalTokens: 3600,
    },
  );
  assert.equal(allocateOutputBudget({ guardInputTokens: 2801 }).blocked, true);
});
