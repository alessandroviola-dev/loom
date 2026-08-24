# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — real 30B generation + packed decode + routing/cache economics proven
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001_PASS`
Next core checkpoint: `LOOM_30B_MOE_REAL_RAW_CACHE_001`
Then: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

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
- zero-cache expert traffic 962,592,768 B/token (918 MiB);
- BF16 KV 98,304 B/token.

## Proven architecture/runtime

1. `LOOM_30B_MOE_EXPERT_PACK_001_PASS`: lossless 9-range -> 1-range expert-major representation.
2. `LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`: device-verified random expert ~1.89 GB/s; zero-cache storage-only floor ~0.4816 s/token.
3. `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS`: bitwise-exact decoder layer with one 2,506,752-B expert live at a time; 99.21875% layer expert-bank residency reduction.
4. `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS`: complete 819,015,680-B shared target resident with zero routed experts.
5. `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL`: all 48 layers and final logits exact with full 16.22-GB model capacity represented externally/resident as designed.
6. `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`: research GC/RSS instrumentation caused almost all apparent ~20 s wall; clean `GC_END_ONLY` full forward 1.641729 s, zero swap delta.
7. `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`: first real autoregressive generation on M1 8 GB, answer `4` then EOS, source zero-cache decode ~0.6471 tok/s.
8. `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`: real hot-path packed layout cut expert-read wall 59.27% and total decode 43.72%; packed decode-equivalent ~1.0799 tok/s.

## ROUTING-CACHE-TRACE-001 — PASS

Report: `research/moe/loom-30b-moe-routing-cache-trace-001-result.md`.
Raw evidence: `results-local/moe/routing-cache-trace-001/20260824T090555Z/`.

Trace corpus:
- 3/3 prompts completed;
- 96 traced decode positions / 93 one-position transitions;
- 36,864 routing selections;
- 3,747 unique `(layer, expert)` keys = 60.9863% of 6,144 universe;
- consecutive same-layer intersection mean/P50/P90 = 3.545 / 3 / 6 out of 8;
- reuse within 1/2/4/8/16/32 tokens = 42.923 / 53.079 / 62.826 / 72.030 / 78.692 / 80.265%.

Working sets grow materially with window size: mean unique experts ~598 over 2 tokens, ~1,333 over 8, ~1,824 over 16 and ~2,425 over 32.

### Cache simulation

Best tested online policy: `GLOBAL_LRU`.

- 1 GiB / 428 experts: 43.473% hit, 544,121,856 B/token;
- 2 GiB / 856: 59.961%, 385,413,120 B/token;
- 3 GiB / 1,285: 71.864%, 270,833,664 B/token;
- 4 GiB / 1,713: **79.598%**, 196,388,352 B/token.

At 4 GiB:
- offline Belady oracle: 87.961% hit;
- trace-fitted static hot set: 82.935%;
- online global LRU is therefore reasonably close to the available upper bounds.

Projected 4-GiB packed economics:
- APPLICATION_PACKED expert-read ~0.090195 s/token;
- projected current-runtime decode ~0.574136 s/token = 1.74175 tok/s;
- raw-packed-byte cache projection ~0.612595 s/token = 1.63240 tok/s;
- live-MLX cache optimistic ~1.74175 tok/s, but large-cache allocator/object overhead is unmeasured.

Logical 4-GiB cache + backbone + max trace KV = 5,122,322,432 B, leaving ~1.32 GB below a 6-GiB envelope.

### Structural ceiling

Current packed non-read floor is ~0.483941 s/token. Therefore even perfect expert-cache hits cap the present single-token runtime near **2.066 tok/s**.

Cache alone:
- 2 tok/s: possible;
- 3 tok/s: no;
- 5 tok/s: no.

Thus cache is worth implementing, but 3+ tok/s structurally requires multi-token/block amortization and/or further fixed-cost reduction.

Block-union routing structure is also material: mean union bytes/position fall from 918 MiB single-token to ~715/613/544/495/457/425/398 MiB for 2–8-token windows (exact byte values are in the result report). This is routing structure only, not DFlash speed.

## Exact next step — `LOOM_30B_MOE_REAL_RAW_CACHE_001`

Implement the first real expert cache using the safest realization:
- global LRU;
- 4 GiB logical target / 1,713-expert capacity;
- cache **raw reconstructed packed expert bytes**, not persistent MLX expert objects;
- cold miss reads current source exact ranges and assembles one canonical expert byte object, then inserts it;
- hit avoids disk/source reads but still reconstructs transient MLX arrays and computes normally;
- preserve `GC_END_ONLY`, exact output, BF16 KV and zero expert accumulation;
- benchmark multiple long greedy outputs and compare to zero-cache packed/source baselines;
- measure actual hit rate, bytes read/token, decode tok/s, cache memory overhead, RSS/MLX/swap and cross-prompt behavior.

Why RAW first: the 4-GiB live-MLX cache has unmeasured object/allocator overhead. Raw-byte caching tests the cache economics with much cleaner ownership/memory semantics.

The cold path may remain source-range based for this first real cache test; do not build the full 14.344-GiB pack. Preferred storage direction remains `HOT_SET_PACK_SOURCE_COLD` if real cache results justify it.

## After real cache

1. Compare measured cache runtime with ~1.63 tok/s raw-cache projection.
2. Audit exact-target DFlash: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`.
3. Use real cache result + block-union structure to design multi-token/block verification experiment.
4. Consider live-MLX caching only if raw-cache hit economics are strong and measured allocator overhead leaves safe 8-GB headroom.
5. Full 14.344-GiB expert-major pack remains CONDITIONAL.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.