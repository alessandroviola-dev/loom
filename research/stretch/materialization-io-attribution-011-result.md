# Stretch 011 — Materialization I/O Attribution — Result

Date: 2026-08-19
Valid run: `20260819-185036`
Classification: **MATERIALIZATION_IO_ATTRIBUTION_PASS**

## Provenance

Plan:
`research/stretch/materialization-io-attribution-011-plan.md`

Runner:
`scripts/stretch_materialization_io_attribution_011.py`

Frozen runner blob:
`16125f7eb0b2fb662591e194de0498513a563a6d`

Frozen upstream:
- Stretch 009 source blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`
- Stretch 010 transform blob `ff3dc83abc6388113fca15594eef6b3ec00ebe50`.

Scientific workload remained identical to valid Stretch 010:
- Qwen3-8B 3-bit/group64
- mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- prompt `[[1,42,2048,151935]]`
- deterministic argmax
- 16 generated/feedback tokens
- ordinary BF16 36-layer KVCache
- official fully resident control
- phase-streamed embedding -> 36 transformer layers -> final RMSNorm -> LM head
- no tokenizer, sampling, KV quantization, prefetch, model download or OS-cache purge.

New instrumentation only:
Darwin `proc_pid_rusage(..., RUSAGE_INFO_V2)` around weight-selection/materialization boundaries.

## Correctness and autoregressive state — PASS

Prompt and all 16 feedback steps:
- max absolute logit difference: **0.0**
- mean absolute logit difference: **0.0**
- top-1 equality: true at every step.

Resident and streamed generated sequence:
`[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`.

Generated-sequence equality: true.

Final resident/streamed KV offsets: all **20**.

Final resident/streamed KV allocation:
**37,748,736 / 37,748,736 B**.

Weight residency:
- official resident full model: **3,583,928,320 B**
- max streamed weight-stage delta: **272,269,312 B**
- resident/max-streamed ratio: **13.16317396798652x**.

## Reproduced timing transition

Transformer 36-layer materialization walls by feedback token:
`[0.215334,0.397099,1.401023,1.400275,1.391794,1.393371,1.390969,1.391072,1.394846,1.394058,1.404265,1.407967,1.393368,1.406864,1.400152,1.399045]` s.

Transformer 36-layer forward walls:
`[0.190743,0.194132,0.194521,0.191494,0.190237,0.190766,0.192213,0.191376,0.190405,0.195046,0.189887,0.191027,0.191136,0.191017,0.188944,0.189684]` s.

Means:
- layer materialization: **1.261344 s/token**
- layer forward: **0.191414 s/token**.

Full streamed pass walls:
`[1.950159,2.286514,3.368697,3.356515,3.343453,3.332238,3.336447,3.337109,3.349738,3.353168,3.357956,3.423926,3.359059,3.355009,3.345106,3.360165]` s.

- mean full streamed pass: **3.200954 s/token**
- median full streamed pass: **3.351453 s/token**
- logical streamed throughput: **0.312407 token/s**.

The forward compute remains approximately flat while the parameter-materialization interval moves into the slow regime.

## Darwin process I/O attribution

### Transformer materialization disk-read bytes/token

`[48513024,389873664,3023896576,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840]`

The late steady-state value, **3,039,395,840 B/token**, is extremely close to the frozen transformer-body tensor payload **3,039,381,504 B**; the small accounting difference must not be treated as exact model-file byte identity.

### Full-pass process disk-read bytes/token

`[161075200,625709056,3465527296,3584045056,3584032768,3584053248,3584081920,3584069632,3584057344,3584045056,3584045056,3584147456,3584032768,3584032768,3584032768,3584032768]`

Late steady-state full-pass process reads are approximately **3.584 GB/token**, close to the complete frozen tensor payload **3,583,928,320 B**.

### Build/select process disk reads

`[0,114688,0,0,0,0,0,0,0,0,0,114688,114688,114688,114688,114688]` B/token.

Build/select contributes negligible disk-read accounting compared with `mx.eval(block.parameters())` in the slow regime.

### Page-ins

Transformer materialization page-ins:
`[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]`.

The page-in counter therefore does not explain the observed transition in this workload; disk-read accounting does.

## Early vs late regime

Tokens 1–4 mean:
- materialization wall: **0.85343275 s**
- materialization disk-read bytes: **1,625,419,776 B**
- materialization page-ins: **0**
- full-pass disk-read bytes: **1,959,089,152 B**.

Tokens 8–16 mean:
- materialization wall: **1.3990707777777778 s**
- materialization disk-read bytes: **3,039,395,840 B**
- materialization page-ins: **0**
- full-pass disk-read bytes: **3,584,055,068.4444447 B**.

Diagnostic Pearson correlation:
- materialization wall vs materialization disk-read bytes: **0.9995866107996246**
- materialization wall vs page-ins: unavailable/undefined because all page-in deltas are zero.

## Resource telemetry

Launch gate:
- 73%, 73%, 74% free
- swap 1211.75 MB.

Whole run:
- minimum free memory: **22%**
- peak swap: **1606.94 MB**
- peak child RSS: **941.672 MB**.

Phase-scoped diagnostic buckets:
- resident: min free **22%**, peak swap **1606.94 MB**
- stream prompt: min free **66%**
- stream tokens: min free **65%**, peak child RSS **395.328 MB**.

Disk: **36.267 -> 36.269 GiB**.

## Canonical interpretation

Stretch 011 reproduces the late materialization slowdown while leaving transformer forward time essentially stable, and shows that the slowdown coincides extremely strongly with increased Darwin per-process disk-read accounting during parameter materialization.

In the steady-state slow regime, the measured process disk-read delta during transformer materialization is approximately one complete transformer-body payload per generated token, while the full streamed pass records approximately one complete model payload per token.

This supports the practical conclusion that **pure one-layer-at-a-time dense autoregressive streaming pays approximately one model-weight traversal per generated token once the host can no longer satisfy most accesses from a faster cached state**.

Interpretation boundary:
- `ri_diskio_bytesread` is process disk-I/O accounting, not a forensic per-file SSD trace;
- the near-payload-sized deltas and ~0.9996 timing correlation are strong diagnostic evidence, not proof that every counted byte is from `model.safetensors`;
- zero `ri_pageins` does not negate the disk-read result; it only means the page-in counter did not move in this path.

## Decision

The primary bottleneck is now sufficiently characterized to justify a controlled RAM-for-I/O tradeoff experiment before tokenizer integration.

Next experiment: retain a fixed subset of transformer layers persistently across autoregressive tokens while streaming the remainder, preserving exact resident parity and the 16-token workload. Measure whether the predicted reduction in repeated process disk-read bytes is accompanied by lower token latency at the expected increase in weight residency.