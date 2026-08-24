# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS`
Strategic next: `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001`
Parallel next: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Dense Qwen3-8B laboratory — RETAINED

Dense experiments established exact partial residency and several lifecycle rules. Dense research remains a controlled MLX implementation laboratory; it is no longer assumed to be the final 32B architecture.

## B — 30B sparse-MoE target

Target: local `Qwen3-30B-A3B-MLX-4bit`.

Exact static anatomy:
- total tensor payload 16,220,499,968 B;
- mandatory/non-routed 819,015,680 B (0.763 GiB);
- routed expert bank 15,401,484,288 B (14.344 GiB);
- 48 MoE layers;
- 128 experts/layer;
- top-k 8;
- one expert 2,506,752 B;
- selected experts/layer 20,054,016 B;
- zero-cache expert traffic/token 962,592,768 B (918 MiB).

Static classification: `LOOM_30B_MOE_FEASIBILITY_001_STATIC_CONDITIONAL`.

## C — Expert-major storage — PASS

`LOOM_30B_MOE_EXPERT_PACK_001_PASS` proved lossless expert-major packing on layers 0 and 15:
- 256 experts / 641,728,512 B validated;
- zero mismatches;
- 9 source ranges/expert -> 1 packed range/expert;
- top-k reads 72 -> 8;
- byte amplification 1.0x;
- 100% packed useful/span efficiency.

Full 14.344 GiB pack remains deferred until whole-model runtime evidence requires it.

## D — Physical I/O — DEVICE VERIFIED / CONDITIONAL

`LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL` established the internal-SSD baseline:
- random expert physical 1,890.4 MB/s;
- expert latency P50 1.197 ms;
- top-k latency P50 9.839 ms;
- token-like 384-read P50 460.074 ms;
- zero-cache storage-only lower bound 0.4816 s/token;
- storage-only maximum 2.076 tok/s.

Necessary I/O traffic reduction:
- 5 tok/s: 58.47%;
- 10 tok/s: 79.24%.

Consequence: raw SSD is sufficient to continue research but not sufficient for high usability without cache/reuse and/or multi-token amortization.

## E — One-layer external-expert execution — PASS

`LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS` is the first true computational proof of the architecture.

Layer 0 executed using canonical Qwen3 MoE MLX semantics with routed experts external and only one selected packed expert live at a time.

Correctness:
- router IDs and weights bitwise exact;
- all selected expert outputs bitwise exact;
- MoE output bitwise exact;
- full decoder-layer output bitwise exact (`atol=0`, `rtol=0`).

Residency:
- full layer expert bank 320,864,256 B;
- serial external expert live bytes 2,506,752 B;
- logical residency reduction 99.21875%;
- CONTROL peak MLX/RSS 331,495,092 / 644,284,416 B;
- SERIAL_EXPERT peak MLX/RSS 12,938,408 / 130,367,488 B;
- ownership/release audit PASS.

Timing:
- external MoE P50 15.455 ms;
- full treatment layer P50 16.282 ms;
- descriptive physical-I/O+compute lower bound 14.103 ms/layer.

Report: `research/moe/loom-30b-moe-one-layer-external-expert-001-result.md`.

Strategic consequence: expert externalization is now proven correct and memory-efficient. The next unknown is whole-model shared/non-expert residency.

## F — Shared backbone residency — NEXT CORE

Checkpoint: `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001`.

Goal: validate the real MLX/RSS cost of keeping the entire 0.763 GiB non-expert target structure resident while all routed experts remain absent.

Required:
1. embeddings + 48 attention blocks + all norms + all routers + final norm + LM head;
2. zero routed-expert tensors resident;
3. exact logical byte audit against 819,015,680 B;
4. MLX active/peak/cache memory and RSS before/during/after load;
5. temporary-loading peak audit;
6. remaining 8 GB budget for runtime, KV, expert cache and potential DFlash;
7. no generation and no full expert-bank materialization.

PASS would complete the two independent prerequisites for a complete external-expert model path:
- shared target structure resident;
- routed expert computation external and exact.

## G — Full forward external experts — AFTER F

Candidate: `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001`.

Goal: first complete 48-layer forward with resident shared backbone and external selected experts. Initially use the simplest exact expert-access path; no cache/speculation assumptions are required for correctness.

The run should begin real per-layer router-trace collection. Full generation is a later gate.

## H — DFlash / block speculative branch — PARALLEL

Exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Published metadata currently indicates roughly ~0.7B draft parameters, 5 draft layers and target hidden-state taps at layers 1/12/23/34/45.

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001` must establish exact stored/resident cost, quantization options, runtime compatibility and expert-cache budget impact before integration.

DFlash is not a memory-fit solution. Its possible value is multi-token target verification and expert-union amortization.

## I — Routing overlap / cache branch

After a complete target forward can produce real routing traces:
- collect expert IDs per layer/position;
- measure temporal reuse;
- group positions into blocks 2–8;
- compute per-layer expert unions;
- derive unique expert bytes per accepted token;
- compare against 918 MiB/token baseline and the mandatory 58.47% / 79.24% traffic reductions;
- design cache and prefetch only from measured traces.

Checkpoint: `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`.

## J — Decision matrix

If shared residency passes and full external forward works:
- collect real routing traces;
- quantify cache/block savings;
- create full expert pack only if runtime access geometry justifies it;
- integrate DFlash only if net-positive under 8 GB;
- proceed to real generation/capability tests.

If shared residency is unexpectedly expensive:
- reduce persistent target structures;
- investigate streamed/shared subcomponents or more aggressive quantization before full forward.

If traffic reduction remains insufficient after real traces:
- route prediction/prefetch;
- neuron/cluster-level storage granularity;
- stronger multi-token verification/coalescing;
- faster external NVMe only as a hardware branch;
- LOOM-native architecture research if necessary.

## K — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001`
2. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001` in parallel/next slot
3. `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001`
4. real routing trace/cache instrumentation
5. `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`
6. decide full expert pack from runtime evidence
7. DFlash/block verification integration only if net-positive
8. first real 30B generation benchmark
9. capability validation
10. custom LOOM architecture research if necessary
11. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
