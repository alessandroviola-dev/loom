# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`
Strategic next: `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001`
Parallel later: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

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

`LOOM_30B_MOE_EXPERT_PACK_001_PASS` proved lossless expert-major packing on two representative layers: 9 ranges/expert -> 1 contiguous range, zero mismatches, no byte amplification.

Full 14.344 GiB repack remains deferred because source exact-range execution is correct and profiling has not shown a dominant read-call/layout cost.

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

Cache/reuse and/or block amortization remain primary requirements for high usability.

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
- BF16 KV = 96 KiB/token.

## F — First complete 30B external-expert forward — CORRECT / CONDITIONAL

`LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL` proved complete model execution:
- CONTROL and TREATMENT 48/48 layers;
- router IDs/weights bitwise exact;
- hidden states bitwise exact 48/48;
- final logits zero error;
- full 16,220,499,968 B model capacity represented;
- routed bank external;
- maximum logical routed expert live 2,506,752 B;
- final routed expert residency 0 B.

Real multi-position routing overlap:
- F4: 1,086 unique / 1,536 selections; 680,583,168 B potential union bytes/position;
- F8: 1,547 / 3,072; 484,743,168 B/position;
- F8 potential union accounting is 49.64% below F1.

The original 20.333756 s F1 timing is not the clean runtime baseline because observer overhead dominated it.

## G — Full-forward overhead attribution — PASS

`LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS` reconciled 100% of the instrumented wall and identified the dominant observer effects.

Report: `research/moe/loom-30b-moe-full-forward-overhead-attribution-001-result.md`.

Dominant costs in the audited path:
- forced per-expert `gc.collect`: 13.350101 s / 61.63%;
- per-expert RSS sampling: 5.879225 s / 27.14%;
- source `pread`: 1.217114 s / 5.62%;
- expert-output synchronization: 0.301939 s / 1.39%;
- remaining categories small.

GC cadence experiment:
- every expert: 14.188257 s;
- every layer: 2.359604 s;
- end only: **1.641729 s**.

`GC_END_ONLY` is bitwise exact and memory-safe in the isolated run:
- logits parity PASS;
- router parity PASS;
- final routed expert count/bytes 0 / 0;
- maximum logical expert live 2,506,752 B;
- MLX peak 821,640,984 B;
- RSS peak 1,247,002,624 B;
- swap delta 0.0 MiB;
- memory-pressure PASS.

Clean per-layer P50/P90/P95/max:
0.032469 / 0.033652 / 0.034337 / 0.063860 s.

Fastest-safe forward-equivalent rate: 0.6091/s, NOT generation TPS.

Approximate clean cost shares:
- file/pread 65.36%;
- compute 21.93%;
- other runtime/software 12.71%.

Strategic consequence: the apparent 20 s model cost was primarily the research harness. Basic correctness and memory feasibility are now established strongly enough to begin real autoregressive stepping.

## H — First greedy generation — NEXT CORE

Checkpoint: `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001`.

Goal: obtain the first real bounded autoregressive output from the full-capacity 30B target on M1 8 GB with no expert cache, no prefetch and no DFlash.

Requirements:
1. use normal tokenizer/chat template and disable thinking where supported;
2. use the proven resident backbone and `GC_END_ONLY` external-expert hot path;
3. implement/reuse canonical BF16 KV cache semantics;
4. generate a short bounded greedy sequence sufficient for multiple decode steps;
5. record TTFT/prefill separately from decode;
6. record per-generated-token wall time, useful expert bytes, router selections, KV bytes, MLX/RSS/swap and output token/text;
7. prove routed experts do not accumulate across tokens;
8. preserve exact/controlled correctness checks without putting expensive audits in the hot loop;
9. do not add expert cache yet.

This checkpoint establishes the zero-cache sequential baseline and produces the first canonical real token-to-token routing trace.

## I — Routing/cache trace branch — AFTER H

Checkpoint: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`.

From real generation traces:
- measure same-layer cross-token expert reuse;
- simulate LRU/segmented/admission policies under 512 MiB–4 GiB budgets;
- quantify actual physical bytes/token avoided;
- estimate cache hit rates from traces, not assumptions;
- compare against the 58.47% and 79.24% traffic-reduction requirements;
- only then implement the smallest promising cache.

## J — DFlash / block speculative branch — PARALLEL LATER

Exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001` should audit exact draft bytes, architecture, quantization feasibility, hidden-state dependencies, compatibility and 8 GB budget impact.

DFlash is not a memory-fit mechanism. Its value must be judged against the measured greedy/cache baseline, particularly unique expert bytes per accepted output token.

## K — Generation decision path

If zero-cache greedy generation is correct but slow:
1. use its real routing trace to model expert cache;
2. implement one cache policy only if trace-backed;
3. remeasure real tok/s and bytes/token;
4. then test block/DFlash amortization if still needed.

If KV/runtime introduces new memory pressure:
- localize KV allocation, allocator cache and token-step ownership before adding optimization complexity.

If cache + block amortization still cannot approach practical speed:
- route prediction/prefetch;
- neuron/cluster-level storage granularity;
- faster external NVMe as a secondary hardware branch;
- LOOM-native architecture research if necessary.

## L — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001`
2. `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`
3. implement smallest trace-backed expert cache
4. remeasure real greedy generation
5. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`
6. DFlash/block verification only if net-positive against measured baseline
7. capability benchmark
8. custom LOOM architecture research if necessary
9. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
