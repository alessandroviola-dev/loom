# Stretch 012 — Eight-Layer Persistent Hotset — Result

Date: 2026-08-19
Valid run: `20260819-192349`
Classification: **EIGHT_LAYER_PERSISTENT_HOTSET_PASS**

## Provenance

Plan:
`research/stretch/eight-layer-persistent-hotset-012-plan.md`

Runner:
`scripts/stretch_eight_layer_persistent_hotset_012.py`

Frozen runner blob:
`8e10660af778655a279f30e7d59785163bc204e3`

Frozen reconstruction:
- Stretch 009 source blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`
- Stretch 010 transform blob `ff3dc83abc6388113fca15594eef6b3ec00ebe50`
- Stretch 011 instrumentation blob `16125f7eb0b2fb662591e194de0498513a563a6d`.

Single scientific change vs Stretch 011:
transformer layers `0..7` were materialized once and retained across the streamed prompt and all 16 autoregressive feedback passes. Layers `8..35`, embedding, final RMSNorm and LM head remained streamed.

Environment/model/generation remained frozen:
- Apple M1 / 8 GB reference host
- Qwen3-8B 3-bit/group64
- mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- prompt token IDs `[[1,42,2048,151935]]`
- deterministic argmax
- 16 feedback tokens
- ordinary BF16 36-layer KVCache
- official resident control
- Darwin process-I/O attribution
- no tokenizer, sampling, KV quantization, prefetch, cache purge or download.

## Correctness — PASS

Prompt parity:
- max absolute logit difference: **0.0**
- mean absolute logit difference: **0.0**
- first-token equality: true.

All 16 feedback steps:
- max absolute logit difference: **0.0**
- mean absolute logit difference: **0.0**
- top-1 equality: true at every step.

Resident and hybrid generated sequence:
`[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`.

Generated-sequence equality: true.

Final resident/hybrid KV offsets: all **20**.
Final resident/hybrid KV allocation: **37,748,736 / 37,748,736 B**.

## Weight residency

Official resident full-model materialized delta:
**3,583,928,320 B**.

Persistent eight-layer hotset materialized delta:
**675,418,112 B**, exactly the preregistered payload.

Largest newly materialized stage outside the hotset:
**272,269,312 B**.

Hybrid maximum simultaneous raw-weight budget:
**947,687,424 B** (~903.79 MiB).

Resident / hybrid raw-weight budget ratio:
**3.7817620338074676x**.

The old `13.163x` resident/max-new-stage ratio excludes the persistent hotset and must not be used as the hybrid simultaneous-residency ratio.

## Timing

Hybrid 36-layer materialization walls by token:
`[0.211748,0.352766,0.388904,1.015762,0.248648,0.2633,0.204901,0.199582,0.307983,0.884046,0.425607,0.367652,0.471699,0.409322,0.306686,0.460923]` s.

Mean layer-materialization wall:
**0.407471 s/token**.

36-layer forward walls:
`[0.185901,0.194165,0.187677,0.189072,0.189363,0.188235,0.193785,0.195159,0.189716,0.186688,0.18726,0.199928,0.193909,0.187495,0.18938,0.188564]` s.

Mean layer-forward wall:
**0.190394 s/token**.

Full hybrid pass walls:
`[1.969002,1.996154,2.001992,2.72714,2.011843,1.877987,1.841273,1.842413,1.974444,2.576323,2.217495,2.07357,2.123065,2.072836,2.029316,2.142915]` s.

- mean full pass: **2.092360 s/token**
- median full pass: **2.020580 s/token**
- logical hybrid throughput: **0.477929 token/s**.

Relative to Stretch 011 logical throughput 0.312407 token/s, this is approximately **+52.98%**. The result remains far below the LOOM interactive usability target of ~20 token/s, so hotset residency alone is not sufficient.

## Darwin process I/O

Transformer materialization disk-read bytes/token:
`[138067968,392986624,516440064,2058403840,216055808,237404160,123437056,141082624,328122368,1804238848,681345024,517455872,678674432,663502848,368443392,683196416]`.

Full-pass disk-read bytes/token:
`[438689792,443854848,620085248,2368798720,611221504,348151808,285294592,294735872,499810304,2053341184,1152598016,770473984,837812224,894140416,687734784,900829184]`.

Materialization page-ins remained zero for all 16 token passes.

Early tokens 1–4:
- mean materialization wall **0.492295 s**
- mean materialization disk-read accounting **776,474,624 B/token**
- mean full-pass disk-read accounting **967,857,152 B/token**.

Late tokens 8–16:
- mean materialization wall **0.4259444444 s**
- mean materialization disk-read accounting **651,784,647.1 B/token**
- mean full-pass disk-read accounting **899,052,885.3 B/token**.

Materialization-time vs disk-read Pearson:
**0.9972018123495737**.

The observed I/O reduction is substantially larger than the simple eight-layer payload subtraction predicted from Stretch 011. This indicates that the persistent hotset changed the host/cache regime as well as directly removing eight layer reloads. Therefore the measured process-I/O reduction must be treated as an observed host/runtime outcome, not as a deterministic byte-saving formula attributable only to the retained layer payload.

## Resource telemetry

Launch gate:
- 72%, 72%, 72% free
- swap 1182.94 MB.

Whole run:
- minimum free memory: **23%**
- peak swap: **1634.62 MB**
- peak child RSS: **1054.344 MB**.

Phase buckets:
- resident min free **23%**
- stream prompt min free **60%**
- stream tokens min free **59%**, peak child RSS **1054.344 MB**.

Disk:
**36.276 -> 36.272 GiB**.

## Canonical interpretation

Stretch 012 validates a real RAM-for-I/O tradeoff: retaining eight transformer layers increases simultaneous raw-weight residency to ~947.7 MB but preserves exact resident-equivalent autoregressive behavior and improves the measured unoptimized logical runtime from 0.312407 to 0.477929 token/s in this host state.

The improvement is useful but nowhere near the ~20 token/s usability target. The larger-than-payload I/O reduction also shows that host/cache behavior strongly interacts with the residency policy.

Hotset residency should therefore remain one optimization axis, but the next priority is amortizing a target weight traversal across multiple accepted tokens rather than merely adding more resident layers.

## Decision

Proceed to an **oracle multi-token block-verification upper-bound experiment** while preserving the eight-layer hotset. Use the already frozen resident-greedy 16-token sequence as a perfect draft, verify four draft tokens per target traversal, require exact resident numerical/token parity, and measure target traversals, disk-read accounting, wall time and accepted-token-equivalent throughput.

This oracle experiment is not deployable speculative decoding and excludes draft-model cost. Its purpose is to measure whether multi-token verification can provide the order-of-magnitude acceleration required before investing in a real drafter.