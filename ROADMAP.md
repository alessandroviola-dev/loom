# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS`
Strategic next: `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001`
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

`LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS` proved exact routed-expert computation with only one selected expert live at a time.

Correctness:
- router IDs/weights bitwise exact;
- all selected expert outputs bitwise exact;
- MoE output bitwise exact;
- full decoder-layer output bitwise exact.

Residency:
- full layer expert bank 320,864,256 B;
- serial external expert live bytes 2,506,752 B;
- logical residency reduction 99.21875%;
- CONTROL peak MLX/RSS 331,495,092 / 644,284,416 B;
- SERIAL_EXPERT peak MLX/RSS 12,938,408 / 130,367,488 B;
- ownership/release audit PASS.

Timing:
- external MoE P50 15.455 ms;
- full treatment layer P50 16.282 ms.

Report: `research/moe/loom-30b-moe-one-layer-external-expert-001-result.md`.

## F — Shared backbone residency — PASS

`LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS` proved the entire non-expert target can remain resident without any routed-expert tensor.

Exact results:
- 919 resident non-expert tensors;
- 819,015,680 B logical stored bytes — exact reconciliation PASS;
- routed expert tensors: 0 / 0 B;
- final MLX active 819,032,072 B;
- final RSS 817,463,296 B;
- peak MLX construction 819,032,072 B;
- peak RSS construction 1,122,189,312 B;
- swap unchanged 921.94 -> 921.94 MiB;
- memory-pressure gate PASS;
- embedding, attention, routers L0/L23/L47, final norm and LM head functional checks PASS.

BF16 KV geometry is 98,304 B/token (96 KiB/token): 96 MiB at 1,024 tokens, 384 MiB at 4,096, 768 MiB at 8,192.

Expert-cache capacity reference:
- 512 MiB: 214 experts;
- 1 GiB: 428;
- 2 GiB: 856;
- 3 GiB: 1,285;
- 4 GiB: 1,713.

Report: `research/moe/loom-30b-moe-shared-backbone-residency-001-result.md`.

Strategic consequence: memory-fit feasibility is now much stronger. Both required primitives are proven independently on M1 8 GB: full shared target residency and exact serial external-expert computation.

## G — Full forward external experts — NEXT CORE

Checkpoint: `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001`.

Goal: first complete target forward through embedding, all 48 decoder layers, final norm and LM head while keeping the shared backbone resident and routed experts external.

Correctness design:
1. use a short deterministic token sequence;
2. CONTROL may stream one complete layer expert bank at a time, never the whole 30B;
3. TREATMENT loads only router-selected experts and releases them serially;
4. compare per-layer checkpoints, final hidden state and logits;
5. record real router top-k choices across all 48 layers/positions;
6. prove no expert accumulation across layers;
7. measure peak MLX/RSS, swap, expert bytes read and stage timings;
8. no autoregressive generation yet and no cache/prefetch/DFlash assumptions.

The first full forward does not require the complete expert-major repack. Direct exact-range selected-expert reads from the original safetensors are acceptable for correctness; layer-0/layer-15 validated packs may be used where convenient.

PASS would mean LOOM has executed the full-capacity ~30B target end-to-end on the 8 GB reference machine without full routed-expert residency.

## H — DFlash / block speculative branch — PARALLEL

Exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Published metadata currently indicates roughly ~0.7B draft parameters, 5 draft layers and target hidden-state taps at layers 1/12/23/34/45.

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001` must establish exact stored/resident cost, quantization options, runtime compatibility and expert-cache budget impact before integration.

DFlash is not a memory-fit solution. Its possible value is multi-token target verification and expert-union amortization.

## I — Routing overlap / cache branch

Once full-target execution yields real traces:
- collect expert IDs per layer/position;
- measure temporal reuse and layer-local hotness;
- group positions into blocks 2–8;
- compute per-layer expert unions;
- derive unique expert bytes per accepted token;
- compare against 918 MiB/token baseline and the mandatory 58.47% / 79.24% traffic reductions;
- design cache and prefetch only from measured traces.

Checkpoint: `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`.

## J — First generation after full forward

If full forward passes:
1. decide whether to build the full expert-major pack from actual access costs;
2. add minimal KV-cache-compatible token stepping;
3. run first short greedy generation with zero expert cache;
4. collect router traces and real wall/token;
5. then add cache/reuse and block amortization experimentally.

## K — Decision matrix

If full external forward works:
- routing traces/cache study;
- full pack only if runtime evidence supports it;
- first real 30B generation;
- DFlash only if net-positive under 8 GB.

If traffic reduction remains insufficient after real traces:
- route prediction/prefetch;
- neuron/cluster-level storage granularity;
- stronger multi-token verification/coalescing;
- faster external NVMe only as a hardware branch;
- LOOM-native architecture research if necessary.

If full forward itself reveals a structural runtime blocker:
- localize whether it comes from attention/KV, expert reconstruction, allocator behavior or layer-to-layer ownership before changing architecture.

## L — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001`
2. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001` in parallel/next slot
3. real routing trace/cache instrumentation
4. `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`
5. decide full expert pack from runtime evidence
6. first real 30B generation benchmark
7. DFlash/block verification integration only if net-positive
8. capability validation
9. custom LOOM architecture research if necessary
10. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
