# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_REAL_RAW_CACHE_001_MEMORY_FAIL`
Strategic next: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

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
- long routing/cache trace.

## B — Real generation + packed baseline

`LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`:
- correct `4`, then EOS;
- source zero-cache decode ~1.545 s/token / 0.647 tok/s;
- no expert leak or swap growth.

`LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`:
- source 3,456 reads/token -> packed 384;
- bytes unchanged at 962,592,768 B/token;
- expert-read wall -59.27%;
- total decode wall -43.72%;
- packed decode-equivalent ~1.0799 tok/s;
- exact output preserved.

Packed on-disk expert-major geometry is a proven performance optimization when present.

## C — Routing/cache trace — PASS

`LOOM_30B_MOE_ROUTING_CACHE_TRACE_001_PASS` proved real temporal expert reuse:
- 96 positions;
- 36,864 expert selections;
- 3,747 unique `(layer, expert)` keys;
- best online simulation: global LRU;
- 4 GiB / 1,713 experts predicted 79.598% hit and 196,388,352 B external/token.

The current packed non-read floor is ~0.483941 s/token, implying a perfect single-token cache ceiling around **2.066 tok/s**.

Thus even ideal expert caching alone cannot reach 3/5/10 tok/s under the current one-token execution structure.

## D — Real 4-GiB raw cache — MEMORY FAIL

`LOOM_30B_MOE_REAL_RAW_CACHE_001_MEMORY_FAIL`.

Report: `research/moe/loom-30b-moe-real-raw-cache-001-result.md`.

The trace prediction itself was validated:
- actual real hit rate: **80.9056%**;
- simulated: 79.598%;
- traffic reduction: 80.9056%;
- per-prompt hit rates remained stable around ~78–84%.

But the 4-GiB resident raw payload is incompatible with practical M1-8GB execution:
- CONTROL: 1.428821 s/token / 0.699878 tok/s;
- TREATMENT: 4.883706 s/token / 0.204763 tok/s;
- swap delta: **+2410.56 MiB**;
- memory pressure FAIL;
- progressive memory growth YES;
- deterministic output still exact;
- persistent routed MLX expert residency remained 0 B.

Conclusion: reuse is real, but **4-GiB raw RAM caching is rejected**. Do not move directly to a persistent live-MLX cache, and do not silently reduce the cache size as a rescue of the failed checkpoint.

Immediate cold-path direction: `SOURCE_COLD_ONLY` unless a future separately preregistered storage/cache experiment changes it.

The prior expert-major disk-layout win remains valid independently; full 14.344-GiB pack remains conditional.

## E — Token-efficient Pi workflow — ACTIVE

LOOM now has root `/AGENTS.md`, derived from the Ophelia Vault token-efficient and bounded-agent protocols.

Stable project rules and already-proven invariants live there. Future Pi work should use compact work packages rather than multi-thousand-token prompts.

Default form:

```text
Read AGENTS.md.
LOOM WP <id>
Goal: ...
Inputs: ...
Change: ...
Gates: ...
Evidence: ...
Return: ...
STOP
```

Pi remains local execution only; ChatGPT keeps Git/HANDOFF/ROADMAP ownership. More restrictive LOOM rules override general Vault autonomy.

## F — DFlash exact-target static audit — NEXT

Checkpoint: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`.

Exact-target candidate:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Before integration, establish:
1. exact architecture and tensor payload;
2. precision and plausible quantized resident footprints;
3. target hidden-state dependencies / tap layers;
4. required runtime semantics;
5. MLX / llama.cpp / custom-runtime compatibility;
6. memory budget on M1 8 GB with 819-MB backbone + BF16 KV;
7. whether a useful drafter leaves enough working memory without reintroducing swap pressure;
8. published acceptance-length evidence separated from local measured facts.

DFlash is not a fit mechanism. Its value is potential target-verification amortization across multiple accepted tokens.

## G — Multi-token / block branch

After DFlash static feasibility:
- evaluate target verification of multiple positions in one step;
- combine real routing-union structure with accepted-token counts;
- measure unique expert bytes per accepted output token;
- determine whether expert loads can be shared across positions;
- preserve exact target semantics.

Real trace mean union bytes/position already fall with block length:
- 2: 749,343,645 B;
- 3: 642,396,979 B;
- 4: 570,480,569 B;
- 5: 519,237,866 B;
- 6: 479,315,740 B;
- 7: 446,068,713 B;
- 8: 417,808,712 B.

These are routing-structure observations, not DFlash speed measurements.

## H — Cache/storage reconsideration

Do not retry the failed 4-GiB raw-cache design.

Possible later experiments, only if block/DFlash evidence makes them useful:
- much smaller/admission-controlled cache under a strict memory-pressure gate;
- packed hot-set with source cold fallback;
- on-demand/layer-segmented pack;
- full expert-major pack only if arbitrary-generation cold misses justify the extra 14.344 GiB storage.

Persistent live-MLX expert cache is currently not promoted.

## I — Performance path

1. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`.
2. If static feasible, block/multi-token target-verification experiment.
3. Measure accepted tokens, target forwards, expert union bytes and real memory.
4. Revisit small cache/storage only if complementary rather than competing for the same memory budget.
5. Rebenchmark sustained real generation.
6. Capability/coding benchmark.
7. Context scaling and memory stability.
8. If existing MoE still cannot reach practical speed, escalate to route prediction/prefetch, finer-grained sparsity or LOOM-native model/system co-design.
9. Behavioral decensoring validation before final promotion.

## Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring with collateral-capability validation.

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.