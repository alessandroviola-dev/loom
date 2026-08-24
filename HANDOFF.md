# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — full 30B external-expert forward proven and de-instrumented; first greedy generation next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`
Next core checkpoint: `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001`
Parallel later: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Every final promoted LOOM-produced model must eventually pass validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.
ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## 30B target — exact local anatomy

Local model: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`.

- Qwen3MoeForCausalLM;
- 48 MoE layers;
- hidden 2048;
- 128 routed experts/layer;
- top-k 8;
- MoE intermediate 768;
- MLX 4-bit/group128;
- total tensor payload 16,220,499,968 B;
- mandatory/non-routed 819,015,680 B;
- routed expert bank 15,401,484,288 B;
- one routed expert 2,506,752 B;
- zero-cache useful expert traffic 962,592,768 B/position (918 MiB).

## Proven architecture primitives

### Expert-major storage — PASS

`LOOM_30B_MOE_EXPERT_PACK_001_PASS` proved lossless expert-major packing on representative layers: 9 source ranges/expert -> 1 contiguous range/expert, zero mismatches, no byte amplification. Full 14.344 GiB repack remains deferred.

### Physical I/O — CONDITIONAL / device verified

`LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL` established the internal SSD baseline:
- random expert physical ~1,890.4 MB/s;
- expert latency P50 1.197 ms;
- top-k latency P50 9.839 ms;
- zero-cache storage-only lower bound 0.4816 s/token;
- storage-only maximum 2.076 tok/s;
- traffic reduction needed from storage alone: 58.47% for 5 tok/s, 79.24% for 10 tok/s.

### One-layer external experts — PASS

`LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS` proved exact decoder-layer computation with one selected routed expert live at a time:
- router/expert/MoE/full-layer outputs bitwise exact;
- 320,864,256 B full expert bank -> 2,506,752 B maximum logical live expert;
- 99.21875% expert residency reduction;
- ownership/release PASS.

### Shared backbone residency — PASS

`LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS` proved:
- 919 non-expert tensors resident;
- 819,015,680 B exact logical target backbone;
- zero routed experts resident;
- final MLX active ~819 MB;
- no swap growth during construction;
- embedding/attention/router/final-norm/LM-head checks PASS;
- BF16 KV = 98,304 B/token (96 KiB/token).

## FULL-FORWARD-EXTERNAL-001 — CONDITIONAL, correctness proven

Report: `research/moe/loom-30b-moe-full-forward-external-001-result.md`.
Raw evidence: `results-local/moe/full-forward-external-001/20260824T073551Z/`.

The full-capacity target executed end-to-end on M1 8 GB:
- CONTROL 48/48 layers;
- TREATMENT 48/48;
- router IDs/weights bitwise exact all layers;
- layer hidden states bitwise exact 48/48;
- final hidden/logits zero error;
- argmax and top-10 parity PASS;
- full 16,220,499,968 B model capacity represented;
- backbone 819,015,680 B resident;
- routed bank 15,401,484,288 B external;
- one 2,506,752 B expert maximum live;
- final routed expert residency 0 B.

The original instrumented F1 wall was 20.333756 s, but this was later shown to be dominated by research instrumentation rather than target computation.

Real routing overlap from ordinary target multi-position forwards:
- F4: 1,086 unique expert instances / 1,536 naive selections; potential union accounting 680,583,168 B/position;
- F8: 1,547 / 3,072; potential union accounting 484,743,168 B/position;
- F8 potential union bytes/position are 49.64% below the F1 962,592,768 B baseline.

## FULL-FORWARD-OVERHEAD-ATTRIBUTION-001 — PASS

Report: `research/moe/loom-30b-moe-full-forward-overhead-attribution-001-result.md`.
Raw evidence: `results-local/moe/full-forward-overhead-attribution-001/20260824T080141Z/`.

The ~18 s unexplained gap was overwhelmingly observer effect:
- forced `gc.collect`: 13.350101 s / 61.63%;
- per-expert RSS sampling: 5.879225 s / 27.14%;
- `pread`: 1.217114 s / 5.62%;
- expert-output `mx.eval`: 0.301939 s / 1.39%;
- all other named categories individually small.

864 explicit GC calls were issued by the research path.

Controlled GC cadence result:
- GC every expert: 14.188257 s;
- GC every layer: 2.359604 s;
- GC at end only: **1.641729 s**.

`GC_END_ONLY` is the new clean exact baseline for the next generation experiment:
- logits parity PASS;
- router parity PASS;
- final routed expert residency 0 / 0 B;
- maximum logical expert live 2,506,752 B;
- MLX peak 821,640,984 B;
- RSS peak 1,247,002,624 B;
- isolated swap delta 0.0 MiB;
- memory-pressure PASS;
- per-layer P50/P90/P95/max 0.032469 / 0.033652 / 0.034337 / 0.063860 s.

Fastest-safe forward-equivalent rate is 0.6091/s, explicitly not generation TPS.

Approximate fastest-safe cost shares:
- file/pread 65.36%;
- compute 21.93%;
- remaining software/runtime overhead 12.71%.

Strategic consequence: the 30B architecture is no longer blocked by correctness, baseline residency, or the apparent 20 s forward. The next unknown is real autoregressive token stepping with KV cache, sequential routing reuse and sustained memory behavior.

## Exact next step — `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001`

Run the first short real autoregressive greedy generation using the clean `GC_END_ONLY` external-expert path.

Requirements:
1. normal local tokenizer/chat formatting with thinking disabled where supported;
2. resident shared backbone from the proven loader;
3. BF16 KV cache with exact accounting;
4. routed experts remain source-external; no full pack/cache/prefetch/DFlash;
5. generate only a short bounded sequence initially (enough to measure multiple decode steps safely);
6. record per-token wall time, expert bytes, selected expert IDs, KV growth, MLX/RSS/swap, and final text;
7. verify no routed-expert accumulation and no swap growth attributable to the treatment;
8. use the resulting real consecutive-token routing trace as the canonical input for routing-cache/reuse simulation.

Do not add expert cache in this first generation checkpoint. We need a clean zero-cache sequential baseline first.

## After first generation

1. `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001` — simulate measured cache policies from real token traces and quantify bytes/token reduction;
2. decide whether a minimal real expert cache can reach a useful speed envelope;
3. audit exact-target DFlash footprint/compatibility only against the measured baseline and memory budget;
4. integrate block/speculative decoding only if it improves net accepted-token economics;
5. capability benchmark after practical generation speed exists;
6. decensoring validation before final promotion.

## Full expert-major pack

Still NOT justified by the measured bottleneck. Source exact-range execution is correct; packing should be reconsidered only if future production profiling shows read-call/layout overhead is material relative to transfer volume.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
