import test from "node:test";
import assert from "node:assert/strict";

import {
  OUTPUT_RECOVERY_GUIDANCE,
  WORKSPACE_GROUNDING_GUIDANCE,
  nextTruncationState,
  promptExplicitlyAllowsNewFiles,
} from "../src/forgeloom-runtime-hardening/policy.mjs";
import { allocateOutputBudget } from "../src/forgeloom-runtime-hardening/output-budget.mjs";

test("first length stop allows one recovery attempt", () => {
  assert.deepEqual(nextTruncationState(0, "length"), {
    consecutive: 1,
    shouldAbort: false,
  });
});

test("second consecutive length stop trips abort guard", () => {
  assert.deepEqual(nextTruncationState(1, "length"), {
    consecutive: 2,
    shouldAbort: true,
  });
});

test("non-length assistant stop resets truncation counter", () => {
  assert.deepEqual(nextTruncationState(1, "toolUse"), {
    consecutive: 0,
    shouldAbort: false,
  });
  assert.deepEqual(nextTruncationState(2, "stop"), {
    consecutive: 0,
    shouldAbort: false,
  });
});

test("system guidance reserves output for tools and forbids invented paths", () => {
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /NEVER retry the same payload/);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /one short sentence/);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /split the work into multiple independent edits/);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /Do not create helper verification files/);
  assert.match(WORKSPACE_GROUNDING_GUIDANCE, /Never invent companion modules/);
  assert.match(WORKSPACE_GROUNDING_GUIDANCE, /ENOENT.*NOT authorization/i);
});

test("new-file permission is explicit rather than inferred from generic repair prompts", () => {
  assert.equal(promptExplicitlyAllowsNewFiles("Correggi wifi_hacker.py e installa le dipendenze necessarie"), false);
  assert.equal(promptExplicitlyAllowsNewFiles("Crea un nuovo file helper.py"), true);
  assert.equal(promptExplicitlyAllowsNewFiles("Create a new module for parsing"), true);
});

test("adaptive output budget keeps original 800-token reserve while using spare headroom", () => {
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
