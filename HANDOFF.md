# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — full 30B generation proven; 4-GiB raw cache rejected; multi-token/DFlash branch next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_REAL_RAW_CACHE_001_MEMORY_FAIL`
Next core checkpoint: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Every final promoted LOOM-produced model must eventually pass validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

## Operating split

Pi: local code/runtime inspection, implementation, tests/benchmarks and concise local evidence.
ChatGPT: scientific direction, experiment design/review, GitHub synchronization, `HANDOFF.md`, `ROADMAP.md` and project continuity.

Local override remains strict: Pi does **not** perform Git/GitHub administration or edit HANDOFF/ROADMAP unless explicitly overridden.

## Token-efficient Pi protocol — ACTIVE

Root `/AGENTS.md` is now the persistent Pi context and implements the Ophelia Vault token-efficient / bounded-agent workflow for LOOM.

Future Pi prompts should normally be compact work packages:

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

Do not restate project history already in `AGENTS.md`. Read `HANDOFF.md` only when a work package explicitly needs volatile state. This is especially important because `.qwen/settings.json` currently configures the local agent with a 4096-token context window.

## Target anatomy

Local model: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`.

- 48 MoE layers;
- 128 routed experts/layer;
- top-k 8;
- total tensor payload 16,220,499,968 B;
- resident non-routed target 819,015,680 B;
- external routed expert bank 15,401,484,288 B;
- one expert 2,506,752 B;
- zero-cache expert traffic 962,592,768 B/token (918 MiB);
- BF16 KV 98,304 B/token.

## Proven architecture/runtime

1. `LOOM_30B_MOE_EXPERT_PACK_001_PASS`
   - lossless 9-range -> 1-range expert-major representation.

2. `LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`
   - device-verified random expert ~1.89 GB/s;
   - zero-cache storage-only floor ~0.4816 s/token.

3. `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS`
   - bitwise-exact decoder layer;
   - one 2,506,752-B expert live at a time;
   - 99.21875% layer expert-bank residency reduction.

4. `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS`
   - complete 819,015,680-B shared target resident;
   - zero routed experts resident.

5. `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL`
   - all 48 layers and final logits exact;
   - full 16.22-GB capacity represented with routed bank external.

6. `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`
   - research GC/RSS instrumentation caused almost all apparent ~20 s wall;
   - clean `GC_END_ONLY` full forward 1.641729 s;
   - zero isolated swap delta.

7. `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`
   - first real generation on M1 8 GB;
   - prompt `Quanto fa 2+2? Rispondi solo con il numero.` -> `4`, then EOS;
   - source zero-cache decode ~0.6471 tok/s;
   - BF16 KV advances correctly;
   - no expert leak or swap growth.

8. `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`
   - real packed hot-path A/B;
   - source 3,456 reads/token -> packed 384;
   - same 962,592,768 useful B/token;
   - expert-read wall -59.27%;
   - total decode wall -43.72%;
   - packed decode-equivalent ~1.0799 tok/s;
   - exact output preserved.

9. `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001_PASS`
   - 96 real traced positions / 36,864 selections;
   - 3,747 unique `(layer,expert)` keys;
   - real temporal reuse is material;
   - best simulated online policy: global LRU;
   - 4 GiB / 1,713 entries projected 79.598% hit;
   - single-token current-runtime perfect-cache ceiling only ~2.066 tok/s, so 3+ tok/s requires multi-token/block amortization and/or fixed-cost reduction.

## REAL-RAW-CACHE-001 — MEMORY FAIL

Report: `research/moe/loom-30b-moe-real-raw-cache-001-result.md`.
Raw evidence: `results-local/moe/real-raw-cache-001/20260824T092553Z/`.

Preregistered treatment:
- `GLOBAL_LRU`;
- 4,294,967,296-B raw cache budget;
- 1,713 expert capacity;
- persistent raw canonical expert bytes;
- transient MLX expert arrays only;
- source-range cold misses.

Correctness/cache prediction:
- P1/P2/P3 CONTROL/TREATMENT completed;
- deterministic token parity PASS;
- actual decode hit rate **80.9056%** vs simulated 79.598% (+1.3076 pp);
- P1/P2/P3 hit rates 83.6694 / 78.4610 / 80.5864%;
- traffic fell to 183,801,525.68 B/token, an 80.9056% reduction;
- cache reuse is therefore scientifically real and the trace simulation was accurate.

But implementation performance/memory failed:
- CONTROL: 1.428821 s/token = 0.699878 tok/s;
- TREATMENT: **4.883706 s/token = 0.204763 tok/s**;
- relative throughput effect: -70.7431%;
- treatment cold-read ~1.928012 s/token;
- MLX reconstruction ~1.791990 s/token;
- peak raw payload 4,294,066,176 B;
- swap **829.50 -> 3240.06 MiB (+2410.56 MiB)**;
- memory pressure FAIL;
- progressive memory growth YES;
- final routed MLX expert residency 0 / 0 B and ownership cleanup PASS.

Interpretation:
- routing reuse is not the problem;
- a 4-GiB raw Python/RAM cache on an 8-GB M1 is operationally invalid because the system compresses/swaps heavily and the hot path becomes much slower;
- do not rescue this checkpoint by silently choosing a smaller cache;
- do not proceed to a persistent live-MLX cache from this result;
- full expert-major disk packing remains independent: its prior 9->1 decode benefit remains proven, but a full 14.344-GiB pack is still not automatically justified.

Immediate runtime direction returned by the checkpoint: `SOURCE_COLD_ONLY` while the architecture moves to multi-token/block amortization.

## Next core — DFlash static audit

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

Known candidate:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash` for `Qwen/Qwen3-30B-A3B`.

Published/source-review metadata previously indicated roughly:
- ~0.7B draft parameters;
- 5 draft layers;
- target hidden-state taps at layers 1/12/23/34/45;
- acceptance length reported around ~2.46–3.77 depending on workload.

The next checkpoint must establish exact draft bytes, architecture, precision/quantization feasibility, runtime compatibility and M1-8GB memory impact **before download/integration is assumed useful**.

The strategic purpose is no longer “make the model fit”: full 30B generation already works. The purpose is to reduce effective target/expert work per accepted output token and escape the ~2.066 tok/s single-token fixed-cost ceiling.

## Later branches

- Multi-token/block routing union and exact target verification economics.
- Smaller/admission-controlled caches only as separate preregistered experiments if later evidence shows they complement the block/DFlash memory budget; the failed 4-GiB raw cache is not a template to retry casually.
- Full/hot/on-demand expert-major storage only from measured runtime value.
- Capability benchmark after practical speed improves.
- Behavioral decensoring validation before final promotion.

## Local-only warning

Experimental scripts/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.