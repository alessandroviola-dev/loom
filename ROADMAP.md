# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001_CONDITIONAL_STATIC_MEMORY_FIT__INTEGRATION_BLOCKED`
Strategic next: `LOOM_30B_DFLASH_TARGET_INTERFACE_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Architecture feasibility — PROVEN

Target: local `Qwen3-30B-A3B-MLX-4bit`.

Established on M1 8 GB:
- lossless expert-major representation;
- device-verified SSD feasibility;
- bitwise-exact external expert computation;
- complete 819-MB shared backbone residency;
- bitwise-exact 48-layer full forward;
- production-like `GC_END_ONLY` runtime;
- real greedy generation;
- real packed decode improvement;
- long real routing/cache trace.

Canonical target values remain in `/AGENTS.md`.

## B — Real generation / storage baseline

`FIRST_GREEDY_GENERATION_001_PASS`:
- correct real autoregressive output;
- source zero-cache decode ~0.647 tok/s.

`TRACE_PACK_DECODE_AB_001_PASS`:
- expert-major 9->1 range access preserved exact output;
- expert-read wall -59.27%;
- total decode wall -43.72%;
- packed decode-equivalent ~1.0799 tok/s.

Packed disk geometry remains a proven optimization, though a full duplicate expert pack is still conditional.

## C — Cache branch result

`ROUTING_CACHE_TRACE_001_PASS` proved strong real temporal reuse and predicted ~79.6% hit for global LRU 4 GiB.

`REAL_RAW_CACHE_001_MEMORY_FAIL` then validated the hit rate (~80.9%) but rejected the implementation:
- +2410.56 MiB swap;
- memory pressure FAIL;
- decode slowed to ~0.205 tok/s.

Therefore:
- do not retry the same 4-GiB raw-cache design;
- do not jump to persistent live-MLX cache;
- cache alone cannot escape the current ~2.066 tok/s single-token fixed-cost ceiling anyway.

## D — DFlash exact-target static audit — COMPLETE / BLOCKED FOR INTEGRATION

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001`.

Report: `research/architecture/loom-30b-dflash-speculator-static-001-result.md`.

Candidate:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Static facts:
- learned BF16 weights: 680,813,824 elements;
- published safetensors: 1,362,042,120 B = 1.268501 GiB;
- 5 draft layers, H=2048, 32 Q / 4 KV heads, MLP 6144;
- block=8, configured proposals=7;
- exact target hidden-state taps `[1,12,23,34,45]`;
- five target states concatenate to width 10,240 and are fused to 2048;
- draft attention consumes fused target context.

Static memory fit on M1 8 GB is plausible, including BF16 draft, target KV and analytical draft KV. Quantized INT8/INT4 values currently remain lower-bound accounting only because exact quantizer metadata/scale overhead is not established.

Current integration status: **NO**.

Reason:
- no native DFlash path in current MLX/LOOM runtime;
- target-tap capture/fusion path absent;
- block-mask / multi-position target verification absent;
- local acceptance/workspace/routing-union economics unmeasured.

## E — Target-side DFlash interface — NEXT

Checkpoint: `LOOM_30B_DFLASH_TARGET_INTERFACE_001`.

Before implementing any draft model, modify only the target runtime interface enough to expose the exact required hidden states.

Required proof:
1. capture target outputs after layers `[1,12,23,34,45]` on real external-expert forward/decode;
2. define exact tensor contract: shape, dtype, token-position semantics and lifecycle;
3. keep target router selections and final logits bitwise exact to baseline;
4. measure tap memory overhead, MLX peak, RSS and swap;
5. preserve zero routed-expert accumulation and `GC_END_ONLY` lifecycle;
6. no DFlash weights, fusion, draft attention, block masking or speculative acceptance yet.

If this fails, DFlash custom integration remains blocked.

## F — Multi-position target verifier — AFTER E

If target taps pass, separately prove the second target-side prerequisite:
- process/verify multiple candidate positions in one target step while preserving exact causal semantics;
- measure expert union/reuse and unique external bytes per verified position;
- establish block-mask/KV behavior;
- no learned DFlash drafter required initially.

Real trace mean routing-union bytes/position already decline structurally with block length:
- B2 749,343,645 B;
- B3 642,396,979;
- B4 570,480,569;
- B5 519,237,866;
- B6 479,315,740;
- B7 446,068,713;
- B8 417,808,712.

These are structural counterfactuals, not measured block runtime or speculative speedup.

## G — DFlash implementation gate

Only after both:
- target interface PASS;
- multi-position target verification PASS;

should LOOM attempt a DFlash port/integration.

Then measure:
- real drafter resident/workspace bytes;
- acceptance length on local workloads;
- target verification steps/output token;
- unique expert bytes/accepted token;
- sustained tok/s and memory pressure;
- exact deterministic target correctness.

A drafter that fits but does not improve accepted-token economics is not promoted.

## H — Storage/cache later

Possible complementary experiments only after block economics are known:
- smaller/admission-controlled cache with strict swap gate;
- hot-set packed + source-cold fallback;
- on-demand/layer-segmented packed representation;
- full 14.344-GiB expert-major pack only when arbitrary cold-miss economics justify it.

## I — Promotion path

1. `LOOM_30B_DFLASH_TARGET_INTERFACE_001`.
2. Multi-position/block target verifier.
3. DFlash custom integration if both prerequisites pass.
4. Rebenchmark sustained generation.
5. Capability/coding benchmark.
6. Context scaling and memory stability.
7. If practical speed remains insufficient: route prediction/prefetch, finer-grained sparsity or LOOM-native system/model co-design.
8. Behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts should normally be compact work packages containing only the active delta, inputs, gates, evidence and requested return fields. Pi remains local execution only; ChatGPT owns Git/HANDOFF/ROADMAP.

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.