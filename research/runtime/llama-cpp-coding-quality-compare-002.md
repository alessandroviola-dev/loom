# LOOM — llama.cpp Coding Quality Compare 002 Result

Date: 2026-08-19
Run: `20260819-114848`
Status: **PARTIAL — Q3 RESOURCE FAIL / NO VALID QUALITY ORDERING**

## Frozen comparison

Profiles:
1. Qwen3-8B Q3_K_M
2. Qwen3-4B Q4_K_M

Common runtime:
- pinned llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- context 4096
- `-np 1`
- FA auto
- `--fit on --fit-target 1024 --fit-ctx 4096`
- `-ctk q8_0 -ctv q8_0`
- no forced `-ngl -1`
- frozen 5% free-memory / 5600 MB swap guardrails
- Coding Benchmark 01 v1.0.1
- one attempt per task, no retry/salvage/test feedback
- delivery-adjusted score primary

## Observed console result

Disk free before: 43.650 GiB.

### Qwen3 8B Q3_K_M

- server readiness: PASS in 7.360 s
- T01 started
- T01: `guardrail abort`
- no later tasks authorized
- artifact score reported by frozen scorer: 15.0/100
- delivery-adjusted: 0/100
- profile classification: `PARTIAL_OR_RESOURCE_FAIL`

The 15.0 artifact score must not be interpreted as useful Q3 task quality because the delivery path aborted during T01 and the working tree can retain fixture/base-state points.

### Qwen3 4B Q4_K_M

- server readiness: PASS in 1.060 s
- T01 written
- T02 written
- T03 failed delivery
- T04 failed delivery
- T05 written
- T06 failed delivery
- artifact score: 36.43/100
- delivery-adjusted: 25.72/100
- classification: `COMPLETE`

### Top-level runner output

- printed Q3 delivery-adjusted: 0/100
- printed 4B delivery-adjusted: 25.72/100
- printed delta: -25.72
- printed relation: `4B_HIGHER`
- overall classification: `PARTIAL`
- disk free after: 43.643 GiB

Run directory:
`results-local/llama-cpp/coding-quality-compare-002/20260819-114848`

Summary:
`results-local/llama-cpp/coding-quality-compare-002/20260819-114848/comparison-summary.json`

## Scientific interpretation

The printed `4B_HIGHER` relation is **not a valid quality ordering** because the preregistered decision rule requires both profiles to complete. Q3 suffered a resource guardrail abort during the first real coding task, whereas 4B completed the benchmark.

This establishes a stronger operational boundary than the prior Q3 API smoke:

> The Qwen3-8B Q3_K_M + NP1 + Q8_0-KV profile is API-smoke viable at context 4096, but the current evidence does not establish it as workload-stable under the frozen LOOM memory guardrail. A real coding request pushed the profile into a resource abort before T01 could be delivered.

Do not infer that 4B has higher intrinsic coding quality from this run. Do not expose Q3 to Pi from this result.

## Required diagnostic before any rescue

Inspect the persisted Q3 profile summary and memory samples from run `20260819-114848` to recover:
- exact `guardrail_abort_reason`;
- Q3 peak RSS, peak swap and minimum free-memory percentage;
- memory sample immediately before and at the abort;
- whether T01 returned an API response before/after the guardrail;
- server/log evidence around context initialization and request execution.

No runtime parameter may be changed until this diagnostic is recorded.
