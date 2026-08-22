# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — fixed stream-activation eval-boundary isolation
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `EMBED_EVAL_BOUNDARY_001_COMPLETE`
Next: `NORM_EVAL_BOUNDARY_001`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, jointly balancing:

1. memory / residency;
2. speed / usability;
3. practical capability;
4. behavioral freedom / decensoring.

A final promoted LOOM-produced LLM must also have a validated decensored behavioral profile produced through the Heretic approach or a LOOM-native independently implemented equivalent. Behavioral editing is a later promotion/release requirement and does **not** alter the current memory/runtime research sequence.

Frozen requirement:
`research/behavior/decensoring-requirement-v1.md`

Source research is based on the audited Heretic snapshot `p-e-w/heretic@bedb94ef117a271532ac2058447fbc165d5051bd`. Heretic is treated primarily as a generic contrastive residual-direction / low-rank behavioral editing framework, not merely as a prompt jailbreak. Because the audited repository is AGPL-3.0-or-later, a clean LOOM-native implementation is preferred where licensing compatibility matters.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical references

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- thinking disabled
- REALGEN 001 real M1 generation 13.184615357 tok/s; E2E 12.046861457 tok/s
- CAPABILITY 001 practical-agent baseline 1/11 = 9.09%; Coding Benchmark 45/100

Stable Pi bridge published at `4d204471aedb9262ccaa3b86f29b0e344d0c2884`.

## Memory/residency sequence

MEMORY-FRONTIER 001 proved exact real-M1 partial residency but naive synchronous streaming is too slow: FULL 13.433 tok/s; H32 2.527; H24 1.168; H16 0.526; H8 0.435.

SHARED-STAGE-RESIDENCY 001 established the first hierarchy rule: embedding/final norm/LM head should remain hot. Making only those shared stages persistent recovered +36.66% generation throughput with exact parity.

## Streamed-layer gradient

All shared stages persistent; streamed transformer count 0/1/2/4:

| Arm | Streamed layers | Gen tok/s | Wall/token |
|---|---:|---:|---:|
| S0 | 0 | 14.022271 | 71.315 ms |
| S1 | 1 | 5.819925 | 171.824 ms |
| S2 | 2 | 4.755397 | 210.287 ms |
| S4 | 4 | 3.463355 | 288.737 ms |

Exact parity PASS everywhere; no resource aborts.

Descriptive model:
`wall/token ≈ 71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms, R²≈0.999993.

This is a system-level description, not internal causal attribution.

## Streaming activation audit

Source audit found stream-only once-per-token non-scaling work:
- explicit embedding/norm/head `mx.eval` boundaries;
- post-embedding/post-norm/post-head shared cleanup;
- stream-region bookkeeping.

Per-layer load/select/reconstruction/materialization/forward/release scales exactly with streamed-layer count.

## SHARED-CLEANUP-CONSOLIDATION 001 — COMPLETE

Report: `research/memory/shared-cleanup-consolidation-001-result.md`.

Cleanup-consolidated S1 baseline:
- layers 0..34 persistent;
- layer 35 streamed;
- embedding/final norm/LM head persistent;
- persistent raw weights 3,499,501,056 B;
- logical streamed 84,427,264 B/token.

Treatment removed only post-embedding and post-norm cleanup, retaining layer-35 cleanup, final post-head cleanup and all eval boundaries.

Pooled:
- CONTROL 5.643 tok/s; 177.226 ms/token
- TREATMENT 7.065 tok/s; 141.548 ms/token

Causal effect:
- generation +25.206%
- E2E +22.960%
- wall/token -35.678 ms
- peak MLX delta 0 B
- exact parity PASS
- no resource aborts.

Shared-stage cleanup cadence is causally a material part of fixed stream activation. The cleanup-consolidated S1 is the current experimental baseline.

## EMBED-EVAL-BOUNDARY 001 — COMPLETE / NO-GO

Report: `research/memory/embed-eval-boundary-001-result.md`.
Raw evidence: `results-local/memory/embed-eval-boundary-001/20260822-173925/`.

Both arms used the cleanup-consolidated S1. CONTROL retained the explicit post-embedding `mx.eval(h)`; TREATMENT removed/deferred only that boundary.

Pooled:
- CONTROL 7.069 tok/s; 141.462 ms/token; E2E 6.198; TTFT 1.230 s
- TREATMENT 6.833 tok/s; 146.359 ms/token; E2E 6.001; TTFT 1.297 s

Effect:
- generation **-3.346%**
- E2E **-3.178%**
- wall/token **+4.897 ms**
- TTFT **+5.475%**
- peak MLX delta 0 B
- exact parity PASS
- no resource aborts.

Decision: `EMBED_EVAL_NO_GO`. Retain the post-embedding eval in the current runtime. Its removal is not a route to reducing the residual fixed activation cost.

## Exact next step — NORM-EVAL-BOUNDARY 001

Frozen plan: `research/memory/norm-eval-boundary-001-plan.md`.

Use the same cleanup-consolidated S1 baseline and retain the post-embedding eval.

CONTROL retains the explicit `mx.eval(h2)` immediately after final norm.

TREATMENT removes/defers only that final-norm eval. The downstream LM-head `mx.eval(logits)` remains, as do all cleanup, layer-35 streaming, residency, source representation and model math.

Run low-overhead ABBA with exact token parity and the first three REALGEN prompts. If this is also small/no-go, the fixed eval-boundary axis should be close to closure and work should move toward the measured marginal per-layer lifecycle.

## Behavioral-freedom / Heretic requirement — FROZEN, NOT ACTIVE YET

Every final promoted LOOM model must eventually pass a behavioral-edit stage intended to reduce unwanted refusal/alignment behavior while preserving measured capability and resource viability.

Accepted routes:
- use Heretic directly where licensing/backend fit is acceptable; or
- build a LOOM-native clean implementation of the same general research primitive.

Important source-derived design lessons to preserve when that phase begins:
- compute residual statistics in streaming/bounded-memory form;
- keep sensitive geometry in FP32/FP64 even when base weights are quantized;
- represent trial edits reversibly through low-rank adapters;
- optimize behavior change jointly with preservation/resource metrics;
- do not use keyword refusal rate or first-token KL as sole final validation;
- freeze model/dataset revisions, seed, code/environment provenance and output evidence.

Initial future checkpoint on this axis should be `STREAMING_RESIDUAL_MEAN_PARITY`, not immediate model editing.

## Later

1. NORM-EVAL-BOUNDARY 001
2. close fixed activation unless new evidence strongly justifies another boundary test
3. reduce/hide the ~39 ms/layer marginal streamed-layer lifecycle
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B full-parameter-count execution
7. capability comparison for promoted behavior-affecting systems
8. Heretic-derived / LOOM-native behavioral editing and decensoring validation before final model promotion

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
