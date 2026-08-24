# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL`
Strategic next: `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001`
Parallel next: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — 30B sparse-MoE target

Target: local `Qwen3-30B-A3B-MLX-4bit`.

Exact anatomy:
- total tensor payload 16,220,499,968 B;
- mandatory/non-routed 819,015,680 B;
- routed expert bank 15,401,484,288 B;
- 48 MoE layers;
- 128 experts/layer;
- top-k 8;
- one expert 2,506,752 B;
- zero-cache useful expert traffic 962,592,768 B/position (918 MiB).

## B — Storage representation — PASS

`LOOM_30B_MOE_EXPERT_PACK_001_PASS` proved lossless expert-major packing on two representative layers:
- 9 ranges/expert -> 1 contiguous range;
- zero hash/byte/metadata mismatches;
- no byte amplification.

Full 14.344 GiB repack is still deferred because direct source-range execution is correct and the runtime has not yet shown that the 9->1 call reduction is worth duplicating the whole expert bank.

## C — Physical SSD — DEVICE VERIFIED / CONDITIONAL

`LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL` established:
- random expert physical ~1,890.4 MB/s;
- expert latency P50 1.197 ms;
- top-k=8 latency P50 9.839 ms;
- zero-cache storage-only lower bound 0.4816 s/token;
- storage-only maximum 2.076 tok/s.

Required external-traffic reduction from storage alone:
- 5 tok/s: 58.47%;
- 10 tok/s: 79.24%.

Cache/reuse and/or block amortization are primary requirements for high usability.

## D — External expert computation — PASS

`LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS` proved one real decoder layer bitwise exact with one selected expert live at a time:
- full layer expert bank 320,864,256 B;
- serial expert live bytes 2,506,752 B;
- 99.21875% expert residency reduction;
- ownership/release PASS.

## E — Shared backbone residency — PASS

`LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS` proved:
- all 919 expected non-expert tensors resident;
- 819,015,680 B exact logical target backbone;
- zero routed experts resident;
- final MLX active ~819 MB;
- no swap growth during construction;
- embedding/attention/router/final-norm/LM-head checks PASS;
- BF16 KV = 96 KiB/token.

## F — First complete 30B external-expert forward — CONDITIONAL

`LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL` is the first end-to-end full-capacity proof.

Correctness:
- CONTROL 48/48 layers;
- TREATMENT 48/48 layers;
- router IDs/weights bitwise exact throughout;
- hidden states bitwise exact 48/48;
- final logits zero error;
- argmax/top-10 parity PASS.

Representation/residency:
- full 16,220,499,968 B model capacity represented;
- 819,015,680 B backbone resident;
- 15,401,484,288 B routed bank external;
- 962,592,768 B useful expert data consumed for F1;
- maximum logical routed expert live 2,506,752 B;
- final routed expert residency 0 B;
- ownership gate PASS;
- treatment peak MLX 821,640,984 B.

Memory caveat:
- swap grew +131 MiB during the full run, so classification remains CONDITIONAL.

Routing overlap from real target forwards:
- F4: 1,086 unique expert instances / 1,536 naive selections; 680,583,168 B potential union bytes/position;
- F8: 1,547 / 3,072; 484,743,168 B/position;
- F8 potential union accounting is 49.64% below the single-position 962,592,768 B baseline.

This is meaningful real routing overlap, but by itself it does not yet reach the 58.47% storage-only reduction required for a 5 tok/s envelope.

### Critical runtime finding

F1 full-forward wall time was 20.333756 s, with per-layer wall P50 ~0.420643 s.

Explicitly instrumented categories total only about 2.18 s:
- attention/shared 0.148352 s;
- expert reads 1.486196 s;
- decode/view 0.002486 s;
- MLX reconstruction 0.160427 s;
- expert compute 0.340194 s;
- aggregation 0.043012 s.

Therefore ~18 s of the observed forward is currently unattributed. This dominates the practical runtime and must be explained before generation/cache/DFlash speed work is interpreted.

Report: `research/moe/loom-30b-moe-full-forward-external-001-result.md`.

## G — Full-forward overhead attribution — NEXT CORE

Checkpoint: `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001`.

Goal: account for >95% of the 20.33 s F1 wall time without changing model semantics.

Candidate categories to isolate:
1. safetensors/index/header parsing outside timed preads;
2. file open/close and source-range setup;
3. Python expert/module construction/destruction;
4. parameter-tree rebinding/update overhead;
5. `mx.eval` synchronization and lazy graph realization;
6. GC / weakref / recursive ownership audits;
7. allocator/cache cleanup;
8. instrumentation/hash/JSON/tracing overhead;
9. repeated shard/index scans or metadata reconstruction;
10. any unmeasured per-layer barriers.

Method rule: attribution first, optimization second. Instrument the existing exact path and reconcile wall time before changing factors.

Promotion target after attribution: repeat the bitwise-exact full forward with the dominant mechanical overhead removed or reduced by a controlled one-factor change.

## H — Routing/cache branch

Real routing traces now exist, so a routing-cache study is scientifically justified.

After the overhead baseline is understood:
- measure cross-token and block-local expert reuse;
- quantify per-layer hotness and transitions;
- test LRU/segmented caches under realistic 512 MiB–4 GiB budgets;
- compare measured bytes/token against the 918 MiB baseline and 58.47% / 79.24% reduction requirements;
- no assumed Zipf/popularity.

## I — DFlash / block speculative branch — PARALLEL

Exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001` should establish exact draft bytes, architecture, quantization feasibility, hidden-state dependencies and 8 GB budget impact.

DFlash is not a memory-fit mechanism. Potential value: verification of multiple positions plus union-of-experts amortization. Integration is deferred until baseline full-forward overhead and memory cost are understood.

## J — Generation gate

Autoregressive generation is technically possible in principle after the successful full forward, but it is not yet the next scientific experiment because a 20.33 s baseline forward is dominated by unexplained overhead.

First real generation becomes justified after:
1. overhead attribution;
2. a cleaner token-step baseline;
3. memory-pressure/swap behavior understood;
4. minimal KV stepping implemented without changing expert semantics.

## K — Decision path

If overhead attribution reveals removable mechanical cost:
- optimize one factor;
- repeat full-forward exactness;
- perform routing/cache study;
- first greedy generation;
- then DFlash/block verification if net-positive.

If the ~18 s gap is inherent MLX synchronization/runtime cost:
- redesign expert execution/binding path;
- consider persistent weightless expert modules, direct quantized kernels or lower-level MLX/C++ implementation;
- preserve exactness gates.

If traffic remains limiting after runtime overhead is reduced:
- expert cache;
- block union/coalescing;
- DFlash/speculative verification;
- route prediction/prefetch;
- neuron/cluster-level storage;
- faster external NVMe only as a secondary hardware branch.

## Immediate order

1. `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001`
2. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001` in parallel/next available slot
3. controlled removal of dominant full-forward overhead
4. routing-cache / block-overlap study
5. repeat full forward and memory-pressure validation
6. first real greedy 30B generation
7. DFlash integration only if net-positive
8. capability benchmark
9. custom LOOM architecture research if necessary
10. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
