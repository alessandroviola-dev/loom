# LOOM 8B Auto Capability Dispatch 001 FIX1 — Preregistration

Date: 2026-08-28
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Recover valid evidence for the already-frozen `LOOM_8B_AUTO_CAPABILITY_DISPATCH_001` scientific condition after a purely mechanical post-inference harness failure.

Original result remains permanently:
`LOOM_8B_AUTO_CAPABILITY_DISPATCH_NO_GO / INVALID FOR QUALITY OR PERFORMANCE`.

Observed failure:
`TypeError: object of type 'int' has no len()` while building cleanup evidence after inference.

This FIX1 is a separate checkpoint. It is not a retroactive repair/reclassification of the original run.

## Frozen scientific condition

Everything that affects model behavior or scoring remains exactly as in:
`research/architecture/loom-8b-auto-capability-dispatch-001-preregistration.md`.

Unchanged:
- exact Qwen3-8B 3-bit/group64 runtime/provenance;
- exact Capability Selector v0 source/rules;
- exact baseline NORMAL system message;
- exact accepted STRICT_OUTPUT system message;
- exact accepted VERIFY_FIRST system message;
- exact 9 user prompts;
- RAW8 and AUTO8 definitions;
- exact execution order;
- fresh state per condition;
- output token caps;
- scoring rules;
- selector expected labels;
- GO/NO_GO gate;
- all forbidden operations.

No 30B, 4B, calculator, network, downloads, runtime/model changes, retries/self-repair, memory/RAG, extra tools, fine-tuning, Heretic, provider/UI or production integration.

## Failed harness provenance

Failed harness must remain untouched:
`scripts/loom_8b_auto_capability_dispatch_001.py`

Expected SHA-256:
`a0346835bd927add1309ac800a9ae5c1fbffff25cb0f2307737186b526f9c460`.

Create a separate file only:
`scripts/loom_8b_auto_capability_dispatch_001_fix1.py`.

The fix1 file must be derived from the failed harness.

## Only authorized source change

The only semantic source change authorized is mechanical normalization of the cleanup-evidence value at the traceback site.

Required behavior:
- if the cleanup-events/count value supplied by the runtime is an integer count, persist that integer directly;
- if it is a collection/sequence, persist its count using `len(...)`;
- `None` may map to zero only if that matches the existing harness/runtime meaning;
- do not reinterpret cleanup timing or generation behavior;
- do not change model invocation, prompt construction, selector invocation, scoring or metric formulas.

A tiny helper may be introduced solely to make this type normalization explicit/testable.

No other mechanical cleanup/refactor is authorized.

## Mandatory pre-inference proof

Before model inference:
1. verify failed-harness SHA exactly;
2. verify fix1 differs from failed harness only in the authorized cleanup-evidence normalization;
3. persist a unified diff between failed and fix1 harnesses;
4. run no-model synthetic assertions demonstrating the normalization works for at least:
   - integer cleanup count;
   - list/sequence cleanup events;
5. verify frozen selector source SHA `5ccaae77862ceb60700115487ea4db5e5bdcae330d8dcb7583d3186e6521887d`;
6. verify exact 8B model/runtime provenance;
7. verify zero network/package/model mutation.

If any proof fails, classify `LOOM_8B_AUTO_CAPABILITY_DISPATCH_FIX1_MECHANICAL_NO_GO` and stop before inference.

## Execution

If preflight passes, execute the exact original 18 conditions once using fix1.

No retry of a failed condition.

If a **second independent harness defect** prevents valid evidence, classify `LOOM_8B_AUTO_CAPABILITY_DISPATCH_FIX1_MECHANICAL_NO_GO`, preserve completed evidence and STOP. Do not patch again inside FIX1.

## Evidence

Persist under:
`results-local/research/8b-auto-capability-dispatch-001-fix1/<timestamp>/`

Persist all evidence required by the original preregistration plus:
- original failed-harness SHA;
- fix1 SHA;
- exact unified diff;
- synthetic cleanup-normalization test output;
- traceback/failure if any.

## Scientific gate

If all 18 conditions are valid, apply the **original frozen GO gate unchanged**:
1. all 18 inference conditions valid;
2. selector accuracy >= `8/9`;
3. expected-NORMAL false activations = `0/3`;
4. AUTO8 utility >= RAW8 `+2`;
5. zero per-task utility regressions;
6. AUTO8 >= `7/9` CORRECT;
7. selector rules and capability strings unchanged.

Classification:
- `LOOM_8B_AUTO_CAPABILITY_DISPATCH_FIX1_GO` if the original scientific gate passes;
- `LOOM_8B_AUTO_CAPABILITY_DISPATCH_FIX1_NO_GO` if all evidence is valid but scientific gate fails;
- `LOOM_8B_AUTO_CAPABILITY_DISPATCH_FIX1_MECHANICAL_NO_GO` if valid evidence cannot be obtained.

Do not relax any threshold after seeing outputs.

## Interpretation boundary

FIX1 GO would validate the same end-to-end graph intended by the original checkpoint:
`prompt -> selector v0 -> conditional protocol -> 8B`.

It would not yet authorize 30B escalation thresholds or production integration.