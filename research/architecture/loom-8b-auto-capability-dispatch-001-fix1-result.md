# LOOM 8B Auto Capability Dispatch 001 FIX1 — Result

Date: 2026-08-28
Status: **LOOM_8B_AUTO_CAPABILITY_DISPATCH_FIX1_NO_GO**

## Classification

All 18 frozen RAW8/AUTO8 inference conditions completed with valid evidence after the separately preregistered cleanup-telemetry FIX1. No second harness defect occurred.

The scientific GO gate failed.

## Provenance

- original failed harness SHA-256: `a0346835bd927add1309ac800a9ae5c1fbffff25cb0f2307737186b526f9c460`;
- FIX1 harness SHA-256: `a56c1b818d29eb924d47571473b8cf541fc6ec32f1c578cd656d68052f8ed472`;
- selector SHA-256: `5ccaae77862ceb60700115487ea4db5e5bdcae330d8dcb7583d3186e6521887d`;
- model: `mlx-community/Qwen3-8B-3bit@619ded3`;
- weight SHA-256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- quantization: 3-bit/group64;
- MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- offline/no model or package mutation.

Synthetic no-model FIX1 assertions passed for integer, sequence and `None` cleanup shapes.

Evidence:
`results-local/research/8b-auto-capability-dispatch-001-fix1/20260828T165528Z/`

## Frozen gate

Observed:
- all 18 conditions valid: **PASS**;
- selector accuracy >=8/9: **FAIL**, `7/9`;
- expected-NORMAL false activations =0/3: **FAIL**, `1/3` (T07);
- AUTO8 utility >= RAW8 +2: **PASS**, `8 vs 6`;
- zero per-task utility regressions: **PASS**;
- AUTO8 >=7/9 CORRECT: **FAIL**, `2/9`.

Therefore classification is NO_GO. Do not relax or retry this gate on the same prompts.

## Selector behavior

Expected -> predicted:
- T01 NORMAL -> NORMAL;
- T02 STRICT_OUTPUT -> STRICT_OUTPUT;
- T03 VERIFY_FIRST -> STRICT_OUTPUT;
- T04 NORMAL -> NORMAL;
- T05 STRICT_OUTPUT -> STRICT_OUTPUT;
- T06 VERIFY_FIRST -> VERIFY_FIRST;
- T07 NORMAL -> VERIFY_FIRST;
- T08 STRICT_OUTPUT -> STRICT_OUTPUT;
- T09 VERIFY_FIRST -> VERIFY_FIRST.

Selector accuracy `7/9`.

Material errors:
- T03 priority/cue collision selected STRICT_OUTPUT instead of VERIFY_FIRST;
- T07 false-positive VERIFY_FIRST on an expected NORMAL fallback discussion.

Do not tune selector v0 using these exposed prompts.

## RAW8 vs AUTO8 quality

Per-task utility RAW8 -> AUTO8:
- T01 `2 -> 2`;
- T02 `0 -> 2`;
- T03 `1 -> 1`;
- T04 `0 -> 0`;
- T05 `0 -> 0`;
- T06 `1 -> 1`;
- T07 `0 -> 0`;
- T08 `1 -> 1`;
- T09 `1 -> 1`.

Aggregates:

### RAW8
- utility `6`;
- CORRECT/PARTIAL/INCORRECT `1/4/4`;
- median TTFT `1.517422 s`;
- pooled generation `12.865656 tok/s`;
- E2E wall `45.979878 s`;
- peak MLX `3,822,184,920 B`;
- peak swap `2641.44 MB`.

### AUTO8
- utility `8`;
- CORRECT/PARTIAL/INCORRECT `2/4/3`;
- median TTFT `2.091046 s`;
- pooled generation `13.167506 tok/s`;
- E2E wall `58.924179 s`;
- peak MLX `3,880,168,240 B`;
- peak swap `2626.56 MB`.

AUTO8 improved utility by `+2` with no per-task utility regressions, but only `2/9` tasks were fully correct and selector generalization failed the frozen gate.

## Interpretation

This result closes the current deterministic pre-inference selector + static protocol dispatch design as a production candidate.

Supported findings:
- targeted strict-output can materially rescue some explicit formatting failures (T02);
- static protocol dispatch does not reliably solve semantic errors or incomplete answers;
- the selector v0 rules do not generalize cleanly to mixed prompt cues;
- increasing protocol instructions alone is insufficient: AUTO8 still produced only 2/9 fully correct outputs.

Do not interpret this as evidence that the 8B runtime is unusable. It remains fast and can solve many individual tasks, but LOOM must validate output quality rather than trusting a pre-inference capability label.

## 8B 4-bit boundary

Historical Direct MLX 8B 4-bit remains closed: the exact unquantized-KV continuous profile resource-failed even after controlled host-state launch, and the subsequent KV8 branch has no canonical quality result. There is no current evidence that reopening 4-bit would solve the observed correctness problem.

## Next direction

Pivot from pre-inference selector-first routing to **post-generation validation-first architecture**:

`prompt -> 8B -> task/contract validator -> accept if verified; otherwise fail/uncertain -> later selective repair or 30B escalation`.

First validate whether cheap deterministic/task-specific validators can identify unacceptable 8B outputs with very low false-accept rate on fresh tasks. Do not involve 30B in the validator-v0 checkpoint.
