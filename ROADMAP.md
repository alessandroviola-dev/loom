# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`
Strategic next: `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001`
Parallel next: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Dense Qwen3-8B laboratory — RETAINED

Dense experiments established exact partial residency and several lifecycle rules. Dense research remains a controlled MLX implementation laboratory; it is no longer assumed to be the final 32B architecture.

## B — Primary architecture branch — Sparse MoE / external experts

Target: local `Qwen3-30B-A3B-MLX-4bit`.

Exact static anatomy:
- total tensor payload: 16,220,499,968 B;
- mandatory/non-routed: 819,015,680 B (0.763 GiB);
- routed expert bank: 15,401,484,288 B (14.344 GiB);
- 48 MoE layers;
- 128 experts/layer;
- top-k 8;
- one expert: 2,506,752 B;
- selected experts/layer: 20,054,016 B;
- zero-cache expert traffic/token: 962,592,768 B (918 MiB).

Static classification: `LOOM_30B_MOE_FEASIBILITY_001_STATIC_CONDITIONAL`.

## C — Expert-major storage — PASS

`LOOM_30B_MOE_EXPERT_PACK_001_PASS` proved lossless expert-major packing on layers 0 and 15:
- 256 experts / 641,728,512 B validated;
- zero mismatches;
- 9 source ranges/expert -> 1 packed range/expert;
- top-k reads 72 -> 8;
- byte amplification stays 1.0x;
- packed useful/span efficiency 100%.

Full pack remains conditional until runtime evidence justifies duplicating the entire 14.344 GiB routed bank.

## D — Physical I/O — DEVICE VERIFIED / CONDITIONAL

`LOOM_30B_MOE_PHYSICAL_IO_001_CACHE_CONTROL_INVALID` is closed as an instrumentation failure; its ~14 GB/s memory-like numbers are non-canonical.

`LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL` established the physical baseline with internal-device counters.

Canonical results:
- internal APPLE SSD AP0256Q (`disk0`);
- sequential physical: 2,391.9 MB/s;
- random expert physical: 1,890.4 MB/s;
- expert latency P50/P90/P95/P99: 1.197 / 1.509 / 1.643 / 2.019 ms;
- top-k=8 physical: 1,823.1 MB/s;
- top-k latency P50/P90/P95/P99: 9.839 / 12.622 / 13.159 / 14.783 ms;
- token-like 384-read P50: 460.074 ms;
- token-like physical: 1,998.8 MB/s;
- zero-cache storage-only lower bound: 0.4816 s/token;
- zero-cache storage-only maximum: 2.076 tok/s.

Necessary I/O traffic reduction:
- 1 tok/s: 0%;
- 2 tok/s: 0%;
- 5 tok/s: 58.47%;
- 10 tok/s: 79.24%.

Report: `research/moe/loom-30b-moe-physical-io-002-result.md`.

Strategic consequence: raw SSD speed alone is insufficient for high usability. Cache/reuse and multi-token/block amortization are now primary design requirements. The architecture remains viable enough to continue because 2 GB/s-class device-verified expert traffic is real, not a storage collapse.

## E — One-layer external-expert execution — NEXT CORE

Checkpoint: `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001`.

Goal: move from byte/storage feasibility to exact computation.

Required:
1. use packed layer-0 experts;
2. keep layer-0 non-expert tensors resident;
3. route a controlled activation through the real router;
4. load only selected expert blocks from external storage;
5. reconstruct exact MLX quantized projection semantics;
6. execute selected experts and combine top-k outputs;
7. compare against canonical layer-0 output from the same weights/input;
8. record parity/tolerance, peak memory, expert bytes, physical I/O and total wall time;
9. no full-model generation yet.

This checkpoint determines whether the external-expert architecture is not merely storable but executable correctly on the reference M1.

## F — DFlash / block speculative branch — PARALLEL

The supplied Qwen3.8-27B/DFlash2/Harness video was fully transcribed and audited. It does not establish 27B viability on 8 GB, but it surfaced block speculative decoding as a potentially high-leverage technique.

Independent research found an exact-target speculator:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Published metadata indicates roughly:
- ~0.7B parameters;
- 5 draft layers;
- target hidden-state taps at layers 1/12/23/34/45;
- average acceptance length ~2.46–3.77 depending on workload.

Canonical note: `research/architecture/dflash-qwen3-30b-a3b-relevance-001.md`.

### F1 — `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

Before integration:
1. recover exact draft tensor bytes/architecture;
2. quantify BF16/quantized resident footprint;
3. estimate the remaining 8 GB budget after mandatory target tensors + draft + runtime/KV;
4. determine MLX/llama.cpp/custom-runtime compatibility;
5. do not assume the draft is worthwhile if it consumes the expert-cache budget needed to save I/O.

### F2 — `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`

After exact external-expert execution exists:
1. capture real router choices per position;
2. group positions into blocks of 2–8;
3. compute per-layer union of expert IDs;
4. compute unique external bytes/block;
5. divide by accepted output tokens over measured/realistic acceptance distributions;
6. compare with the 918 MiB/token baseline;
7. test whether combined block overlap + cache can exceed the mandatory 58.47% reduction needed for a 5 tok/s storage-only envelope.

## G — Cache / routing trace branch

Once a correct external-expert layer/full path exists:
- capture temporal expert reuse;
- measure per-layer hotness and transition structure;
- size expert caches under 4.0–6.0 GiB model/runtime budgets;
- use measured traces, not assumed Zipf/hotness, for cache policy;
- evaluate prefetch/route prediction only after trace evidence.

## H — Decision matrix

If one-layer execution is correct and block/cache reduction reaches the required range:
- build full expert-major pack;
- extend execution across all 48 layers;
- integrate block verification/speculation where net-positive;
- benchmark real generation and capability.

If external-expert execution is correct but traffic reduction remains insufficient:
- deeper route prediction/prefetch;
- neuron/cluster-level storage granularity;
- multi-token verification/coalescing;
- consider faster external NVMe/Thunderbolt only as a hardware branch, not a substitute for architecture.

If exact execution or traffic economics fail structurally:
- move toward LOOM-native model-system co-design: stronger sparsity, recursive/shared weights, external learned memory, SSM/recurrent core, storage layout co-designed with routing.

## I — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001`
2. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001` in parallel/next available slot
3. routing trace/cache instrumentation
4. `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`
5. decide full expert pack from measured runtime value
6. full 48-layer external-expert execution
7. DFlash/block verification integration only if net-positive under the 8 GB budget
8. real generation benchmark
9. capability validation
10. custom LOOM architecture research if necessary
11. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
