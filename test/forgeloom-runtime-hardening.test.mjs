import test from "node:test";
import assert from "node:assert/strict";

import {
  MAX_EDIT_NEW_CHARS,
  MAX_EDIT_OLD_CHARS,
  compactToolRecoveryMessage,
  detectUserLanguage,
  inspectPagedMutation,
  outputLimitToolResult,
  promptExplicitlyAllowsNewFiles,
  promptRequiresMutation,
  requireToolChoice,
  taskSystemGuidance,
} from "../src/forgeloom-runtime-hardening/policy.mjs";
import { allocateOutputBudget } from "../src/forgeloom-runtime-hardening/output-budget.mjs";

test("mutation requests are detected without affecting read-only tasks", () => {
  assert.equal(promptRequiresMutation("Analizza wifi_hacker.py e correggilo per macOS. Modifica direttamente il file."), true);
  assert.equal(promptRequiresMutation("Fix retry_policy.py and update the implementation."), true);
  assert.equal(promptRequiresMutation("Analizza wifi_hacker.py ma non modificare il file."), false);
  assert.equal(promptRequiresMutation("Read only: explain what this module does."), false);
  assert.equal(promptRequiresMutation("Spiegami cosa fa questo file."), false);
});

test("user language detection keeps recovery guidance in the user language", () => {
  assert.equal(detectUserLanguage("Analizza questo file, correggi gli errori e spiegami cosa fai mentre lavori"), "it");
  assert.equal(detectUserLanguage("Analyze this file and fix the errors"), "en");
});

test("native paged coding guidance requires real work for mutation tasks", () => {
  const mutation = taskSystemGuidance(true);
  assert.match(mutation, /NATIVE PAGED CODING/i);
  assert.match(mutation, /Pi automatically continues after tool results/i);
  assert.match(mutation, /prose-only response is not completion/i);
  assert.match(mutation, /at least one edit\/write must succeed/i);
  assert.match(mutation, /exactly one small edits\[\] replacement/i);

  const readOnly = taskSystemGuidance(false);
  assert.doesNotMatch(readOnly, /CURRENT TASK REQUIRES A REAL FILE\/CODE CHANGE/i);
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
  const largeOld = inspectPagedMutation("edit", {
    edits: [{ oldText: "x".repeat(MAX_EDIT_OLD_CHARS + 1), newText: "y" }],
  });
  assert.equal(largeOld.ok, false);

  const largeNew = inspectPagedMutation("edit", {
    edits: [{ oldText: "x", newText: "y".repeat(MAX_EDIT_NEW_CHARS + 1) }],
  });
  assert.equal(largeNew.ok, false);

  const largeWrite = inspectPagedMutation("write", { content: "z".repeat(1201) });
  assert.equal(largeWrite.ok, false);
});

test("new-file permission is explicit and explicit prohibitions win", () => {
  assert.equal(promptExplicitlyAllowsNewFiles("Correggi wifi_hacker.py e installa le dipendenze necessarie"), false);
  assert.equal(promptExplicitlyAllowsNewFiles("Crea un nuovo file helper.py"), true);
  assert.equal(promptExplicitlyAllowsNewFiles("Create a new module for parsing"), true);
  assert.equal(promptExplicitlyAllowsNewFiles("Non creare file."), false);
  assert.equal(promptExplicitlyAllowsNewFiles("Non creare nuovi file o moduli."), false);
  assert.equal(promptExplicitlyAllowsNewFiles("Do not create new files."), false);
  assert.equal(promptExplicitlyAllowsNewFiles("Without creating new files, modify the existing module."), false);
});

test("required tool choice is applied structurally without mutating the original payload", () => {
  const original = {
    messages: [{ role: "user", content: "fix it" }],
    tools: [{ type: "function", function: { name: "read" } }],
    tool_choice: "auto",
    parallel_tool_calls: true,
  };
  const result = requireToolChoice(original, true);
  assert.equal(result.changed, true);
  assert.equal(result.payload.tool_choice, "required");
  assert.equal(result.payload.parallel_tool_calls, false);
  assert.equal(original.tool_choice, "auto");
  assert.equal(original.parallel_tool_calls, true);

  assert.deepEqual(requireToolChoice(original, false), { payload: original, changed: false });
  const noTools = { messages: [{ role: "user", content: "fix it" }] };
  assert.deepEqual(requireToolChoice(noTools, true), { payload: noTools, changed: false });
});

test("Pi output-limit tool errors are detected and rewritten into one small next-step instruction", () => {
  const piError = [{
    type: "text",
    text: 'Tool call "edit" was not executed: the response hit the output token limit, so its arguments may be truncated. Re-issue the tool call with complete arguments.',
  }];
  assert.equal(outputLimitToolResult(piError), true);
  assert.equal(outputLimitToolResult([{ type: "text", text: "ENOENT: file missing" }]), false);

  const italian = compactToolRecoveryMessage("edit", "it");
  assert.match(italian, /Pi sta già continuando/i);
  assert.match(italian, /nuova chiamata/i);
  assert.match(italian, /UNA tool call/i);
  assert.match(italian, /oldText <= 500/i);
  assert.match(italian, /newText <= 1200/i);

  const english = compactToolRecoveryMessage("edit", "en");
  assert.match(english, /Pi is already continuing/i);
  assert.match(english, /fresh provider call/i);
  assert.match(english, /ONE smaller complete tool call/i);
});

test("adaptive output budget keeps 4096 envelope while using spare headroom", () => {
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
