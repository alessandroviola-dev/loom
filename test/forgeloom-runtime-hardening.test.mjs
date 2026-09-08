import test from "node:test";
import assert from "node:assert/strict";

import {
  OUTPUT_RECOVERY_GUIDANCE,
  nextTruncationState,
} from "../src/forgeloom-runtime-hardening/policy.mjs";

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

test("system guidance forbids identical truncated retries and large monolithic edits", () => {
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /NEVER retry the same payload/);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /split the work into multiple independent edits/);
  assert.match(OUTPUT_RECOVERY_GUIDANCE, /Do not create helper verification files/);
});
