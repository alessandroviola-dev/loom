# LOOM Roadmap

Last updated: 2026-08-23
Current checkpoint: `LOOM_30B_MOE_EXPERT_PACK_001_PASS`
Strategic next: `LOOM_30B_MOE_PHYSICAL_IO_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Dense Qwen3-8B laboratory — RETAINED

Dense experiments established exact partial residency and several lifecycle rules. Dense research remains the controlled MLX implementation lab; it is no longer assumed to be the final 32B architecture.

Key retained rules:
- shared stages stay resident;
- shared intermediate cleanup consolidation helps materially;
- streamed post-forward cleanup defer helps materially;
- select-time GC removal is NO-GO;
- block shell reuse cannot currently be isolated without changing parameter-binding semantics.

## B — High-leverage architecture branch — ACTIVE

Primary direction: sparse MoE / external experts.

Qwen3-30B-A3B matches the scale target while activating only a routed subset of its full parameter bank.

## C — LOOM-30B-MOE-FEASIBILITY001 — CONDITIONAL

Exact local static anatomy:
- total tensor payload: 16,220,499,968 B;
- mandatory/non-routed: 819,015,680 B (0.763 GiB);
- routed expert bank: 15,401,484,288 B (14.344 GiB);
- 48 MoE layers;
- 128 experts/layer;
- top-k 8;
- one expert: 2,506,752 B;
- selected experts/layer: 20,054,016 B;
- zero-cache useful expert traffic/token: 962,592,768 B (918 MiB).

Decision: sparse external-expert research is structurally justified, but the original safetensors are expert-bank-major and fragmented for per-expert access.

Report: `research/moe/loom-30b-moe-feasibility-001-result.md`.

## D — LOOM-30B-MOE-EXPERT-PACK001 — PASS

Prototype repacked all 128 experts for layers 0 and 15.

Proven:
- 256 experts / 641,728,512 B validated;
- zero byte/hash/metadata mismatches;
- source 9 data ranges/expert -> packed 1 contiguous range/expert;
- top-k=8 reads 72 -> 8;
- byte amplification 1.0x -> 1.0x;
- packed useful/span efficiency 100%.

This proves a LOOM-native expert-major storage layout is mechanically correct and suitable for independent expert addressing.

Important caveat: ~14–15 GB/s read results from this run are not accepted as physical SSD bandwidth. The files were already hot in the workflow and `F_NOCACHE` does not prove absence of pre-existing page-cache residency. The reported ~66 ms 48-layer I/O extrapolation is non-canonical pending a physically grounded storage benchmark.

Report: `research/moe/loom-30b-moe-expert-pack-001-result.md`.

## E — LOOM-30B-MOE-PHYSICAL-IO001 — NEXT

Before full repack or model execution, establish the actual physical/cold-ish internal-SSD economics.

Required:
1. expert-sized read unit = 2,506,752 B;
2. deterministic random access over a working set large enough to defeat RAM/page-cache residency or otherwise prove bypass;
3. top-k=8 and token-like 384-expert access patterns;
4. explicit Darwin cache/read-ahead controls and limitations;
5. sequential physical baseline and random-range latency;
6. cache-contamination sanity gates;
7. bandwidth-derived token-rate bounds using measured physical data only.

The checkpoint must not claim storage speed from memory/page-cache service.

## F — Decision after physical I/O

If physical I/O is strong enough:
1. build full expert-major pack;
2. implement one-layer exact external-expert execution;
3. capture routing traces;
4. measure hot/cold expert reuse;
5. design cache/prefetch only from trace evidence;
6. extend to full 48-layer execution.

If physical I/O is insufficient:
1. quantify required cache hit rate;
2. test multi-token/block amortization;
3. investigate route prediction/prefetch;
4. consider smaller storage granularity or neuron-cluster layouts;
5. if still structurally insufficient, move toward LOOM-native architecture design.

## G — Longer-term architecture options

- contextual neuron/cluster sparsity;
- multi-token/speculative amortization;
- recursive/shared-weight architectures;
- external learned memory;
- recurrent/SSM resident core;
- storage layout co-designed with routing.

## H — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. `LOOM_30B_MOE_PHYSICAL_IO_001`
2. full expert pack only if storage evidence supports it
3. one-layer external-expert execution
4. routing trace/cache study
5. flash-aware full execution
6. multi-token/block amortization if needed
7. custom LOOM architecture research if existing MoE remains insufficient
8. capability validation
9. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
