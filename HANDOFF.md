# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — real 30B generation proven; packed decode baseline established; routing/cache trace next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`
Next core checkpoint: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`
Parallel later: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Every final promoted LOOM-produced model must eventually pass validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.
ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Target anatomy

Local model: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`.

- 48 MoE layers;
- 128 routed experts/layer;
- top-k 8;
- total tensor payload 16,220,499,968 B;
- resident non-routed target 819,015,680 B;
- external routed expert bank 15,401,484,288 B;
- one expert 2,506,752 B;
- zero-cache expert traffic 962,592,768 B/position (918 MiB);
- BF16 KV 98,304 B/token.

## Proven architecture

The following are established on the reference M1 8 GB:

1. `LOOM_30B_MOE_EXPERT_PACK_001_PASS`
   - lossless expert-major representation;
   - source 9 ranges/expert -> packed 1 range/expert.

2. `LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`
   - device-verified random expert physical ~1,890.4 MB/s;
   - zero-cache storage-only lower bound ~0.4816 s/token;
   - storage-only ceiling 2.076 tok/s.

3. `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS`
   - one decoder layer bitwise exact with one 2,506,752-B expert live at a time;
   - 99.21875% expert-bank residency reduction.

4. `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS`
   - complete 819,015,680-B non-expert target resident;
   - zero routed experts resident;
   - no construction swap growth.

5. `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL`
   - 48/48 layers and final logits exact;
   - full 16.22-GB target capacity represented with routed experts external.

6. `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`
   - original ~20 s forward was dominated by research GC/RSS instrumentation;
   - `GC_END_ONLY` exact full forward 1.641729 s;
   - zero swap delta.

7. `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`
   - first real autoregressive generation: prompt `Quanto fa 2+2? Rispondi solo con il numero.` -> `4` then EOS;
   - zero-cache decode 1.54535 s / 0.6471 tok/s;
   - no expert leak, no swap growth.

## TRACE-PACK-DECODE-AB-001 — PASS

Report: `research/moe/loom-30b-moe-trace-pack-decode-ab-001-result.md`.
Raw evidence: `results-local/moe/trace-pack-decode-ab-001/20260824T084956Z/`.

A trace-scoped packed binary was created for the canonical decode step:
- 384 selected experts;
- 962,592,768 B useful/binary bytes;
- 3,456 components validated;
- zero mismatches;
- no padding or byte amplification.

Strict real decode A/B:
- CONTROL source layout: 3,456 preads/token;
- TREATMENT packed layout: 384 preads/token;
- call reduction 88.888889%;
- useful bytes identical: 962,592,768 B.

Correctness:
- router parity PASS;
- logits parity PASS;
- generated EOS parity PASS.

Performance:
- expert-read median: 1.085528 -> 0.442087 s (-59.27%);
- total decode median: 1.645328 -> 0.926028 s (-43.72%);
- decode-equivalent rate: 0.607781 -> 1.079881 tok/s.

Treatment median categories:
- pread 0.381424 s;
- synchronization 0.207464 s;
- attention 0.181141 s;
- slicing 0.048317 s;
- MLX reconstruction 0.043738 s;
- router 0.019075 s;
- aggregation 0.013104 s;
- open 0.012078 s;
- expert compute 0.004186 s.

Treatment memory:
- MLX peak 881,152,008 B;
- RSS peak 910,983,168 B;
- swap delta 0 MiB;
- final routed expert residency 0 / 0 B.

Interpretation:
- expert-major layout is now a measured production-path win, not merely a static format improvement;
- `PACKED` becomes the baseline for cache economics;
- expert access remains the largest category (~47.7%), but synchronization/attention are now material;
- full 14.344-GiB pack remains conditional until longer routing traces determine whether full duplication is necessary versus trace/on-demand packed working sets.

## Exact next step — `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`

Collect a materially longer real autoregressive routing trace before implementing any cache.

Requirements:
1. use a deterministic short prompt that reliably produces >=16 decode positions, target 24–32 if safe;
2. preserve resident backbone, BF16 KV, serial external experts and `GC_END_ONLY`;
3. generation may use the original source layout for arbitrary experts, because the current trace pack covers only one canonical decode position;
4. record every `(token, layer, expert)` choice and weights;
5. calculate reuse distance, same-layer overlap, hotness and transition structure;
6. simulate cache policies without implementing them;
7. budgets: 512 MiB, 1 GiB, 2 GiB, 3 GiB, 4 GiB;
8. model cache economics against the **PACKED** 1-read/expert baseline using the measured packed-access cost, not the 9-range source baseline;
9. test LRU and at least one segmented/admission policy if evidence supports it;
10. quantify hit rate, bytes/token, estimated packed-read time/token and memory use;
11. no real cache, no prefetch, no DFlash.

## Full expert-major pack

Not yet built. Its measured value is strong, but before duplicating all 14.344 GiB we want the longer trace to answer whether a smaller hot/cold/on-demand packed representation can capture most of the benefit.

## DFlash

Exact-target speculator exists: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`. It remains a later parallel branch. Judge it only against measured packed/cache economics and available memory.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.