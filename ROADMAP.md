# LOOM Roadmap

Last updated: 2026-08-23
Current checkpoint: `LOOM_30B_MOE_PHYSICAL_IO_001_CACHE_CONTROL_INVALID`
Source review: `VIDEO_RESEARCH_INGEST_001_COMPLETE`
Strategic next: `LOOM_30B_MOE_PHYSICAL_IO_002_DEVICE_VERIFIED`
Parallel next: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Dense Qwen3-8B laboratory — RETAINED

Dense experiments established exact partial residency and several lifecycle rules. Dense research remains a controlled MLX implementation laboratory; it is no longer assumed to be the final 32B architecture.

## B — High-leverage architecture branch — ACTIVE

Primary direction: sparse MoE / external experts.

Qwen3-30B-A3B is the first concrete ~30B target.

## C — 30B STATIC FEASIBILITY — CONDITIONAL

Exact local anatomy:
- total tensor payload 16,220,499,968 B;
- mandatory/non-routed 819,015,680 B (0.763 GiB);
- routed expert bank 15,401,484,288 B (14.344 GiB);
- 48 MoE layers;
- 128 experts/layer;
- top-k 8;
- one expert 2,506,752 B;
- selected expert bytes/layer 20,054,016 B;
- zero-cache useful expert traffic/token 962,592,768 B (918 MiB).

Decision: external-expert research is structurally justified.

## D — EXPERT-PACK-001 — PASS

Two-layer prototype proved lossless expert-major packing:
- 256 experts / 641,728,512 B validated;
- zero mismatches;
- 9 source ranges/expert -> 1 packed range/expert;
- top-k reads 72 -> 8;
- byte amplification stays 1.0x;
- 100% packed useful/span efficiency.

Pack correctness is canonical. Performance numbers from the pack run are not physical-SSD evidence.

## E — PHYSICAL-IO-001 — CACHE CONTROL INVALID

Run ID: `20260823T204945Z`.

The benchmark correctly stopped at its sanity gate:
- `F_NOCACHE` and `F_RDAHEAD` were verified and accepted;
- warm control measured ~14,439 MB/s;
- nominal cache-minimized path measured ~13,800 MB/s;
- only ~1.046x distinction;
- the >RAM/random/top-k/token-like phases were not run.

Conclusion: process-level timing plus these file flags did not prove physical SSD service. No physical bandwidth, physical latency, token-rate or cache-hit requirement is promoted from this run.

This is an instrumentation result, not an architectural NO-GO.

## F — PHYSICAL-IO-002 — NEXT CORE

Use device-level evidence to distinguish cache from physical storage.

Required:
1. resolve the actual internal physical disk backing the model volume;
2. sample macOS `iostat` device statistics/cumulative transfer totals around workloads;
3. require device-level MB transfer deltas to correspond materially to requested bytes before accepting storage throughput;
4. keep >RAM unique working set and 2,506,752 B expert-sized reads;
5. retain `F_NOCACHE` / no-read-ahead controls where supported;
6. only after the device-I/O gate passes, measure random expert, top-k=8 and 384-expert token-like storage workloads;
7. quantify physical I/O-only token bounds and required reuse from accepted device-verified data.

If this method still cannot isolate physical storage without privileged tooling, classify the physical baseline as unresolved rather than inventing a number.

## G — VIDEO / DFLASH SOURCE REVIEW — COMPLETE

The supplied Qwen3.8-27B + Harness video was transcribed and visually audited locally.

It does NOT show that a 27B model is viable on 8 GB. The presenter system is M4 Pro / 24 GB and showed very high memory use and swap. The video's DFlash2 acceleration example came from a separate M5 Max result.

The video is nevertheless useful because it surfaced block speculative decoding as a possible high-leverage runtime technique.

Canonical source-review note:
`research/architecture/dflash-qwen3-30b-a3b-relevance-001.md`.

## H — Exact-target DFlash branch — PROMOTED TO PARALLEL RESEARCH

Independent review found an existing DFlash speculator specifically for LOOM's exact target family:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash` for `Qwen/Qwen3-30B-A3B`.

Published metadata indicates roughly:
- ~0.7B draft parameters;
- 5 draft layers;
- target hidden taps at layers 1, 12, 23, 34, 45;
- published average acceptance length ~2.46–3.77 depending on workload.

This makes DFlash substantially more actionable than the Qwen3.8-only video example.

Critical interpretation:
- DFlash does not solve model residency by itself and costs additional draft memory;
- its potential benefit to LOOM is multi-token target verification;
- for external experts, the key metric becomes the UNIQUE/UNION expert set touched across all positions in a verification block, divided by accepted tokens;
- routing overlap must be measured rather than assumed.

### H1 — `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

Before downloading/integrating blindly:
1. audit exact draft tensor bytes, architecture and target-layer dependencies;
2. estimate/measure resident footprint under BF16 and plausible quantized variants;
3. determine whether draft + 0.763 GiB mandatory target + runtime/KV leaves enough space for a useful expert cache on M1 8 GB;
4. identify whether the exact-target draft can be adapted to MLX/llama.cpp or whether a custom LOOM path is required.

### H2 — `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`

After exact target execution becomes possible:
1. collect per-position router choices;
2. group positions into verification blocks (e.g. 2–8 positions);
3. compute union-of-experts/layer and total unique expert bytes/block;
4. divide by accepted-output-token counts over realistic acceptance distributions;
5. compare with the 918 MiB/token single-token zero-cache baseline;
6. do not claim I/O amortization until measured.

## I — Decision matrix

If physical I/O is strong and routing overlap is useful:
- full expert-major pack;
- one-layer and then full external-expert execution;
- block verification / DFlash integration;
- cache and prefetch from measured traces.

If physical I/O is weak but block routing overlap is strong:
- prioritize multi-token verification + expert union batching + cache.

If both are weak:
- move toward stronger model-system co-design: neuron/cluster sparsity, route prediction, recursive/shared-weight architectures, external memory or a LOOM-native model.

## J — Longer-term architecture options

If existing MoE remains insufficient:
- contextual neuron/cluster sparsity;
- multi-token/block amortization;
- recursive/shared-weight architectures;
- external learned memory;
- recurrent/SSM resident core;
- storage layout co-designed with routing.

## K — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. `LOOM_30B_MOE_PHYSICAL_IO_002_DEVICE_VERIFIED`
2. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`
3. one-layer exact external-expert execution
4. full expert pack if justified
5. routing trace/cache study
6. `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`
7. DFlash/block-verification integration only if routing/storage evidence supports it
8. full 48-layer external-expert execution
9. custom LOOM architecture research if necessary
10. capability validation
11. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
