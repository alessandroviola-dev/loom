# Stretch 012 — Eight-Layer Persistent Hotset — Preregistered Plan

Date: 2026-08-19
Status: READY AFTER RUNNER FREEZE

## Motivation

Stretch 011 established that, in the late steady-state regime of pure phase streaming, Darwin per-process disk-read accounting during transformer materialization is approximately one complete transformer-body payload per generated token:
- late 36-layer materialization reads ~3,039,395,840 B/token
- frozen transformer payload 3,039,381,504 B
- late full-pass process reads ~3.584 GB/token
- materialization-time vs disk-read correlation 0.9995866107996246
- transformer forward remains ~0.19 s/token.

Pure dense autoregressive layer streaming therefore trades low RAM residency for repeated weight traversal. Stretch 012 tests one controlled RAM-for-I/O tradeoff.

## Single scientific change

Compared with the valid 16-token Stretch 011 workload:

> Retain transformer layers **0..7** persistently materialized across the streamed prompt and all 16 autoregressive token passes.

Layers 8..35 remain one-layer-at-a-time streamed and evicted exactly as before.

No other model, generation, cache or safety policy changes are allowed.

This is persistence across autoregressive tokens. It is not temporary multi-layer grouping within a token.

## Frozen upstream

Stretch 009 source:
`scripts/stretch_four_token_kv_autoregressive_parity_009.py`
blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Stretch 010 transform:
`scripts/stretch_sixteen_token_autoregressive_stability_010.py`
blob `ff3dc83abc6388113fca15594eef6b3ec00ebe50`.

Stretch 011 instrumentation:
`scripts/stretch_materialization_io_attribution_011.py`
blob `16125f7eb0b2fb662591e194de0498513a563a6d`.

Stretch 011 canonical result:
`research/stretch/materialization-io-attribution-011-result.md`.

## Frozen workload

Preserve:
- Qwen3-8B 3-bit/group64
- mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- prompt token IDs `[[1,42,2048,151935]]`
- deterministic argmax
- exactly 16 generated/feedback tokens
- ordinary BF16 36-layer KVCache
- official fully resident control
- phase-streamed embedding, final RMSNorm and LM head
- exact resident-vs-hybrid full-logit parity at prompt and every feedback step
- same host launch gate and runtime guardrails
- Darwin `proc_pid_rusage(RUSAGE_INFO_V2)` attribution
- file-backed child state/final/stdout/stderr
- no tokenizer
- no sampling
- no KV quantization
- no prefetch/double buffering
- no OS-cache purge
- no new model/download.

## Persistent hotset

Frozen hotset layer IDs:
`[0,1,2,3,4,5,6,7]`.

Each layer payload:
84,427,264 B.

Expected persistent hotset payload:
8 × 84,427,264 = **675,418,112 B**.

Before the streamed prompt:
1. construct each hotset `TransformerBlock` using the same Qwen3 class and quantization policy;
2. load exact frozen weights;
3. `mx.eval(block.parameters())` once;
4. retain the block object in a persistent dictionary/list;
5. delete temporary selected-weight dictionaries;
6. do not evict these eight blocks until all streamed prompt/token work is complete.

Hotset materialization active-memory delta gate:
expected 675,418,112 B within ±8 MiB.

## Per-pass execution

For layers 0..7:
- reuse the persistent block object;
- pass the current layer-specific persistent KVCache exactly as before;
- no weight reload/build is performed in the pass;
- `mx.eval(block.parameters())` may be called diagnostically but must not create another layer-sized active-memory delta;
- block remains resident after the layer forward.

For layers 8..35:
- preserve exact Stretch 011 build/select/materialize/forward/evict behavior.

Embedding, final norm and LM head remain streamed for every pass exactly as before.

## Correctness gates

All inherited correctness gates remain mandatory:
- prompt full-logit numerical parity
- generated token equality
- all 16 feedback full-logit parity gates
- top-1 equality at every feedback step
- identical 16-token generated sequence
- KV offsets 4 -> ... -> 20
- KV allocation remains 37,748,736 B below the 256-position boundary.

A correctness failure is not rescued by performance improvement.

## Weight-residency gates

Persistent hotset:
- initial materialized delta ~675,418,112 B ±8 MiB
- all 8 block objects remain present throughout streamed prompt + 16 token passes.

For hotset cycles:
- per-pass pre-eval/materialized active delta attributable to layer weights should be near 0; tolerance ±4 MiB.

For streamed layers 8..35:
- pre-eval delta <=32 MiB
- materialized delta ~84,427,264 B ±1 MiB
- existing eviction behavior preserved relative to the persistent-hotset baseline.

Actual simultaneous raw-weight budget must be reported as:
- persistent hotset payload
+ maximum newly materialized streamed/shared stage.

Expected worst raw-weight combination is hotset + embedding or LM head:
675,418,112 + 272,269,312 = **947,687,424 B** (~903.79 MiB).

This is intentionally higher than pure streaming's ~272.27 MB max stage but far below the complete 3.584 GB model payload.

## I/O hypothesis — diagnostic, not PASS threshold

Stretch 011 late steady state:
- transformer materialization process reads ~3,039,395,840 B/token.

If retaining eight layers works as intended, the approximate late steady-state transformer read accounting should fall by one 8-layer payload:
3,039,395,840 - 675,418,112 ≈ **2,363,977,728 B/token**.

The exact measured number is not a PASS threshold because `ri_diskio_bytesread` is process accounting, not per-file tracing.

Similarly, late full-pass process reads may fall from ~3.584 GB/token toward ~2.909 GB/token while embedding/head remain streamed.

Report:
- materialization disk-read bytes/token
- full-pass disk-read bytes/token
- page-ins
- early vs late means
- timing correlation
- delta vs Stretch 011 late means.

## Timing hypothesis — diagnostic

If disk-read reduction is the dominant effect, late materialization and full-pass wall should improve relative to Stretch 011.

No minimum speedup is required for PASS. More retained memory can alter host caching/pressure, so measured latency is an outcome rather than a gate.

Report:
- 36-layer/hybrid materialization wall per token
- 36-layer forward wall per token
- full-pass wall per token
- mean/median full-pass
- logical streamed/hybrid tok/s.

Do not label logical tok/s as physical SSD throughput.

## Resource safety

Host launch gate unchanged:
- 3 samples each >=60% system free memory
- swap <=5600 MB.

Runtime abort unchanged:
- system free <5%
- swap >5600 MB.

System-wide telemetry is decisive; child RSS remains diagnostic.

No automatic reduction of hotset size is permitted after launch. If 8 retained layers hit the resource guardrail, classify the result and stop; do not rescue with 4 layers in the same experiment.

## Primary PASS

`EIGHT_LAYER_PERSISTENT_HOTSET_PASS`

requires:
- all inherited 16-token correctness/cache gates PASS
- exact hotset layer IDs 0..7 retained
- hotset initial materialization within the preregistered byte tolerance
- hotset cycles do not rematerialize layer-sized weights per token
- streamed layers 8..35 preserve their existing materialization gates
- runtime guardrails not crossed
- complete I/O/timing diagnostics available.

## Decision rule after result

If PASS and repeated process disk reads decrease approximately as expected, the RAM-for-I/O tradeoff is validated. Then build a small residency frontier (for example 0/8/16 retained layers in separate preregistered runs) before selecting a practical profile.

If hotset retention raises memory pressure enough to erase the I/O/latency gain, record that tradeoff and test a smaller retained set only in a separately preregistered experiment.

If process disk reads do not fall despite hotset cycles showing zero rematerialization, investigate accounting/harness behavior before further optimization.

Tokenizer/text integration remains queued until the first RAM-for-I/O optimization point is characterized.