# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — first real 30B greedy generation proven; decode hot-path optimization next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`
Next core checkpoint: `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001`
Then: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`
Parallel later: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Every final promoted LOOM-produced model must eventually pass validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.
ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## 30B target — exact anatomy

Local model: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`.

- Qwen3MoeForCausalLM;
- 48 MoE layers;
- hidden 2048;
- 128 routed experts/layer;
- top-k 8;
- MoE intermediate 768;
- MLX 4-bit/group128;
- total tensor payload 16,220,499,968 B;
- mandatory/non-routed 819,015,680 B;
- routed expert bank 15,401,484,288 B;
- one routed expert 2,506,752 B;
- zero-cache useful expert traffic 962,592,768 B/position (918 MiB).

## Proven primitives

### Expert-major storage — PASS

`LOOM_30B_MOE_EXPERT_PACK_001_PASS` proved lossless packing on representative layers:
- source 9 exact component ranges/expert;
- packed 1 contiguous range/expert;
- zero byte/hash/metadata mismatches;
- no byte amplification.

Full 14.344 GiB repack remains deferred.

### Physical I/O — DEVICE VERIFIED / CONDITIONAL

`LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL` established the internal APPLE SSD baseline:
- random expert physical ~1,890.4 MB/s;
- expert latency P50 1.197 ms;
- top-k=8 P50 9.839 ms;
- zero-cache storage-only lower bound 0.4816 s/token;
- storage-only maximum 2.076 tok/s;
- traffic reduction needed from storage alone: 58.47% for 5 tok/s, 79.24% for 10 tok/s.

### One-layer external experts — PASS

`LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS` proved exact routed-expert computation with one selected expert live at a time:
- router/expert/MoE/full-layer bitwise exact;
- full layer expert bank 320,864,256 B -> 2,506,752 B maximum logical live expert;
- 99.21875% expert residency reduction;
- ownership/release PASS.

### Shared backbone residency — PASS

`LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS` proved:
- 919 non-expert tensors;
- 819,015,680 B exact logical backbone;
- zero routed experts resident;
- final MLX active ~819 MB;
- no swap growth during construction;
- BF16 KV = 98,304 B/token (96 KiB/token).

### Full forward — exact, then de-instrumented

`LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL` executed all 48 layers and final logits with routed experts external:
- 48/48 layer bitwise parity;
- router IDs/weights bitwise exact;
- final logits zero error;
- full 16,220,499,968 B model capacity represented;
- maximum logical routed expert live 2,506,752 B;
- final routed expert residency 0 B.

`LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS` showed the original ~20 s forward was dominated by observer effect:
- forced `gc.collect`: 13.350101 s;
- per-expert RSS sampling: 5.879225 s.

GC cadence:
- every expert: 14.188257 s;
- every layer: 2.359604 s;
- end only: **1.641729 s**.

`GC_END_ONLY` remained bitwise exact and memory-safe with zero swap delta. It is the production-like baseline.

## FIRST-GREEDY-GENERATION-001 — PASS

Report: `research/moe/loom-30b-moe-first-greedy-generation-001-result.md`.
Raw evidence: `results-local/moe/first-greedy-generation-001/20260824T081701Z/`.

The full-capacity target produced its first real autoregressive output on M1 8 GB using resident backbone + BF16 KV + source-external serial experts, with zero expert cache/prefetch/DFlash.

Prompt:
`Quanto fa 2+2? Rispondi solo con il numero.`

Result:
- prompt: 28 formatted tokens;
- generated IDs: `[19, 151645]`;
- decoded answer: `4`, then canonical EOS;
- deterministic 2-token rerun: PASS.

Performance:
- prefill: 18.666122750 s / 1.500043709 prompt tok/s;
- one measured decode step: 1.545350791 s;
- actual decode baseline: **0.647102267 tok/s**;
- E2E: 20.281761667 s.

Decode cost:
- attention/shared: 0.163348212 s;
- expert source reads: **1.044226996 s**;
- MLX reconstruction: 0.040544777 s;
- expert compute: 0.197101287 s;
- aggregation: 0.012058625 s.

Traffic per decode token:
- 962,592,768 useful expert bytes;
- 384 selected experts;
- 3,456 component `pread` calls (`384 × 9`).

Memory/KV:
- BF16 KV after prefill: 2,752,512 B;
- after final token: 2,850,816 B;
- growth: 98,304 B/token;
- peak MLX: 923,521,032 B;
- peak RSS: 861,634,560 B;
- swap: 922.12 -> 922.12 MiB;
- memory pressure PASS;
- no progressive memory growth;
- final routed expert residency 0 / 0 B.

Short-trace routing reuse:
- 768 routed selections across the two relevant positions;
- consecutive-token same-layer reuse ratio: 27.8646%;
- perfect previous-token retention / whole-run union counterfactual: 828,481,536 B/token;
- reduction: 13.9323%.

This two-position trace is too short for cache-policy design.

## Current bottleneck

Real decode is now dominated by source expert access: 1.044 s of 1.545 s/token.

The hot path still reads each expert as 9 exact safetensor component ranges, i.e. 3,456 `pread` calls/token. The device-verified contiguous expert-sized baseline suggested ~0.4816 s/token storage-only. The difference may reflect small-read/random-range/layout overhead and must be isolated directly on the generation path.

Do not assume packing solves it; measure it.

## Exact next step — `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001`

Run a one-factor real decode A/B without creating the full 14.344 GiB pack:
1. use the exact FIRST-GREEDY trace to identify the `(layer, expert)` instances required for the measured decode step;
2. build only a trace-scoped expert-major pack for those required experts (roughly <= 918 MiB plus metadata);
3. validate every packed component byte-for-byte against source;
4. CONTROL: current 9-range source reads;
5. TREATMENT: one contiguous packed read/expert;
6. keep all model math, routing, KV and GC cadence identical;
7. require identical logits/token output;
8. compare read calls, expert-read wall, total decode wall, MLX/RSS/swap;
9. use device counters if practical to distinguish physical transfer from cache service;
10. decide whether a complete expert-major pack is justified by measured runtime value.

This checkpoint should not implement an expert cache.

## After trace-pack A/B

`LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`:
- use a deterministic prompt that produces a materially longer generation (target >=16 decode positions if model behavior permits);
- collect real layer/expert routing traces;
- simulate cache policies under measured 512 MiB–4 GiB capacities;
- quantify bytes/token reduction from real traces;
- only then implement the smallest promising cache.

## DFlash

Exact-target speculator exists: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

DFlash remains a parallel later branch. Its value must be judged against the real zero-cache/cache baseline and available memory, not as a model-fit solution.

## Full expert-major pack

Still not automatically justified. The next trace-scoped A/B exists specifically to decide this from the real decode hot path rather than from synthetic/warm I/O tests.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
