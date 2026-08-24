# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001_PASS`
Strategic next: `LOOM_30B_MOE_REAL_RAW_CACHE_001`
Then: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Architecture feasibility — PROVEN

Target: local `Qwen3-30B-A3B-MLX-4bit`.

Exact anatomy:
- total tensor payload 16,220,499,968 B;
- resident non-routed target 819,015,680 B;
- external routed bank 15,401,484,288 B;
- 48 layers, 128 experts/layer, top-k 8;
- one expert 2,506,752 B;
- zero-cache expert payload 962,592,768 B/token;
- BF16 KV 98,304 B/token.

Established on M1 8 GB:
- lossless expert-major representation;
- device-verified SSD feasibility;
- bitwise-exact one-layer external experts;
- complete shared-backbone residency;
- bitwise-exact 48-layer full forward;
- de-instrumented production-like full forward;
- first real greedy generation;
- real packed decode baseline;
- long real routing/cache trace.

## B — Real generation baseline

`LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`:
- correct `4` then EOS;
- source zero-cache decode ~1.545 s / 0.647 tok/s;
- no expert leak or swap growth.

`LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`:
- source 3,456 preads/token -> packed 384;
- bytes unchanged at 962,592,768 B/token;
- expert-read wall -59.27%;
- decode wall -43.72%;
- packed decode-equivalent ~1.0799 tok/s;
- exact output preserved.

`PACKED` is the correct miss/access baseline for cache economics.

## C — Routing/cache trace — PASS

`LOOM_30B_MOE_ROUTING_CACHE_TRACE_001_PASS`.

Report: `research/moe/loom-30b-moe-routing-cache-trace-001-result.md`.

Trace:
- 3/3 prompts;
- 96 decode positions;
- 36,864 selections;
- 3,747 unique `(layer, expert)` keys = 60.9863% of expert universe;
- consecutive same-layer intersection mean/P50/P90 3.545 / 3 / 6;
- reuse within 1/2/4/8/16/32 tokens 42.923 / 53.079 / 62.826 / 72.030 / 78.692 / 80.265%.

Best tested online policy: `GLOBAL_LRU`.

Global LRU:
- 1 GiB: 43.473% hit, 544,121,856 B external/token;
- 2 GiB: 59.961%, 385,413,120 B/token;
- 3 GiB: 71.864%, 270,833,664 B/token;
- 4 GiB: 79.598%, 196,388,352 B/token.

At 4 GiB, oracle Belady is 87.961% and the trace-fitted static hot set is 82.935%, so global LRU is close enough to justify a real implementation rather than further policy simulation.

Projected 4-GiB cache economics:
- raw packed-byte cache: ~0.6126 s/token = ~1.632 tok/s;
- optimistic live-MLX cache: ~0.5741 s/token = ~1.742 tok/s;
- logical cache + backbone + trace KV: ~5.122 GB;
- ~1.32 GB headroom under a conservative 6-GiB envelope.

## D — Structural cache ceiling

The current PACKED non-read floor is ~0.483941 s/token.

Even 100% expert-cache hits therefore cap the present single-token runtime near **2.066 tok/s**.

Cache alone:
- 2 tok/s: YES;
- 3 tok/s: NO;
- 5 tok/s: NO.

Therefore cache is necessary and worth implementing, but it is not sufficient for the final usability target. Multi-token/block amortization or further fixed-cost reduction is structurally required for 3+ tok/s.

## E — First real cache — NEXT CORE

Checkpoint: `LOOM_30B_MOE_REAL_RAW_CACHE_001`.

Implement one policy only:
- GLOBAL LRU;
- 4 GiB logical target;
- 1,713 complete expert entries;
- cache raw canonical expert bytes in RAM;
- cold miss reads original 9 source ranges, assembles the canonical 2,506,752-B expert object and admits it;
- hit avoids source/disk reads but still performs transient MLX reconstruction and expert compute;
- no persistent MLX expert objects in this first cache checkpoint.

Why raw bytes first:
- memory ownership is simpler;
- large live-MLX cache allocator/object overhead is not yet measured;
- simulation predicts ~1.63 tok/s if trace behavior generalizes.

Required real A/B:
- cache OFF vs 4-GiB GLOBAL LRU;
- same prompts / greedy decoding / BF16 KV / `GC_END_ONLY`;
- exact token-sequence parity;
- measured hit rate and cold-start/warm-state behavior;
- physical/source bytes per token;
- decode tok/s;
- MLX/RSS/swap/memory pressure;
- no expert accumulation outside cache semantics.

Use multiple prompts and enough decode positions to avoid one-prompt overfitting.

## F — Storage representation

Full 14.344-GiB expert-major pack remains `CONDITIONAL`.

Current preferred design from trace evidence:
`HOT_SET_PACK_SOURCE_COLD`.

Do not duplicate the entire routed bank yet. The first real cache may use source-range cold misses and raw in-RAM hot entries. After measured cache behavior, decide whether to pre-pack a persistent hot set, add on-demand packing, or build the full pack.

## G — DFlash / block branch — AFTER REAL CACHE

Exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Checkpoint: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`.

The cache trace makes this branch more important, not less: the measured single-token fixed-cost floor prevents 3+ tok/s even with perfect cache.

Audit:
- exact draft stored/resident bytes;
- quantization feasibility;
- target hidden-state dependencies;
- MLX/llama.cpp/custom compatibility;
- remaining memory after backbone + KV + a practical expert cache.

Then test block/speculative processing only if accepted-token economics can beat the single-token fixed-cost ceiling.

## H — Block-union structure

Real trace mean expert-union bytes/position fall with block length:
- 2: 749,343,645 B;
- 3: 642,396,979 B;
- 4: 570,480,569 B;
- 5: 519,237,866 B;
- 6: 479,315,740 B;
- 7: 446,068,713 B;
- 8: 417,808,712 B.

These values show structural overlap but are NOT a DFlash speedup or accepted-token result.

## I — Escalation path

1. real 4-GiB raw GLOBAL_LRU cache;
2. compare measured result with ~1.63 tok/s projection;
3. DFlash static audit;
4. multi-token/block execution experiment;
5. optional live-MLX cache if memory overhead is safe;
6. reconsider hot-set/full pack from measured miss behavior;
7. capability and long-context validation once practical speed improves;
8. route prediction/prefetch or lower-granularity sparsity if necessary;
9. LOOM-native architecture research if existing MoE remains insufficient;
10. behavioral decensoring validation before final promotion.

## Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.