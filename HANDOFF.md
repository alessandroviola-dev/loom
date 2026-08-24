# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — full 30B external-expert execution proven; runtime-overhead attribution next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL`
Next core checkpoint: `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001`
Parallel next: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

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

## Proven prerequisites

### Expert-major storage — PASS

`LOOM_30B_MOE_EXPERT_PACK_001_PASS` proved lossless expert-major packing on layers 0 and 15: 9 source ranges/expert -> 1 contiguous range/expert, zero mismatches, no byte amplification.

### Physical I/O — CONDITIONAL / device verified

`LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL` established the real internal-SSD baseline:
- random expert physical ~1,890.4 MB/s;
- expert latency P50 1.197 ms;
- top-k latency P50 9.839 ms;
- zero-cache storage-only lower bound 0.4816 s/token;
- storage-only maximum 2.076 tok/s;
- required traffic reduction from storage alone: 58.47% for 5 tok/s, 79.24% for 10 tok/s.

### One-layer external experts — PASS

`LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS` proved exact decoder-layer computation with one selected expert live at a time:
- router, expert outputs, MoE and full layer bitwise exact;
- 320,864,256 B full expert bank -> 2,506,752 B maximum logical expert live;
- 99.21875% expert residency reduction;
- ownership/release gate PASS.

### Shared backbone residency — PASS

`LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS` proved the complete non-routed target can remain resident:
- 919 non-expert tensors;
- 819,015,680 B exact logical stored bytes;
- zero routed experts resident;
- final MLX active 819,032,072 B;
- peak construction MLX 819,032,072 B;
- no swap growth;
- functional embedding/attention/router/final-norm/LM-head checks PASS;
- BF16 KV = 98,304 B/token (96 KiB/token).

## FULL-FORWARD-EXTERNAL-001 — CONDITIONAL

Report: `research/moe/loom-30b-moe-full-forward-external-001-result.md`.
Raw evidence: `results-local/moe/full-forward-external-001/20260824T073551Z/`.

The complete full-capacity target executed end-to-end on the M1 8 GB machine with the shared backbone resident and routed experts external.

Correctness:
- CONTROL completed 48/48 layers;
- TREATMENT completed 48/48;
- router IDs/weights bitwise exact at all layers;
- layer hidden states bitwise exact 48/48;
- final hidden state and logits zero error;
- argmax and top-10 ranking parity PASS.

Capacity/residency:
- full model bytes represented 16,220,499,968 B;
- backbone resident 819,015,680 B;
- routed bank externally represented 15,401,484,288 B;
- F1 useful expert bytes read 962,592,768 B;
- maximum logical routed expert live 2,506,752 B;
- final routed expert resident count/bytes 0 / 0;
- ownership gate PASS;
- treatment peak MLX 821,640,984 B.

Memory caveat:
- swap 1,096.19 -> 1,227.19 MiB (+131 MiB);
- traversal completed, but memory-pressure gate failed on swap growth;
- therefore classification remains CONDITIONAL rather than unconditional PASS.

Runtime caveat — highest-priority unknown:
- F1 full-forward wall 20.333756 s;
- per-layer wall P50 ~0.420643 s;
- explicitly timed components total only ~2.18 s across the full forward:
  - attention/shared 0.148352 s;
  - expert read 1.486196 s;
  - decode/view 0.002486 s;
  - MLX reconstruction 0.160427 s;
  - expert compute 0.340194 s;
  - aggregation 0.043012 s.

Thus roughly 18 s of wall time is currently unattributed. This gap dominates the present runtime and must be localized before autoregressive speed or cache/DFlash impact is meaningfully evaluated.

Real routing-overlap observations:
- F4: 1,086 unique expert instances / 1,536 naive selections; potential union accounting 680,583,168 B/position;
- F8: 1,547 / 3,072; potential union accounting 484,743,168 B/position;
- F8 is 49.64% below the F1 962,592,768 B baseline.

This is promising real routing overlap but is observational only. It falls short by itself of the 58.47% storage-only reduction required for a 5 tok/s envelope, and actual compute/runtime costs remain larger.

## Exact next step — core

`LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001`

Goal: explain the ~18 s gap between full-forward wall time and explicitly instrumented work.

Priority suspects to isolate without changing semantics:
1. Python/module construction and destruction;
2. safetensors/index/header parsing and source-range setup outside read timers;
3. GC and weakref/ownership auditing;
4. `mx.eval` synchronization / lazy graph realization;
5. quantized parameter binding / tree update overhead;
6. per-expert/per-layer file open/close/manifest lookup overhead;
7. instrumentation itself;
8. allocator/cache cleanup and Python GC;
9. any repeated shard/index scan or tensor metadata reconstruction.

Do not optimize before attribution. Run one-factor timing probes and reconcile >95% of wall time into named categories.

## Parallel DFlash branch

Exact-target speculator exists: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001` should audit exact draft bytes/architecture/quantization/runtime compatibility and 8 GB budget impact. DFlash is relevant only after the baseline full-forward overhead is understood; it is not a memory-fit solution.

## After overhead attribution

1. remove/replace dominant mechanical overhead if safe;
2. repeat exact full forward;
3. collect cleaner real routing traces;
4. routing-cache / block-overlap study;
5. decide full expert-major pack from measured syscall/layout value;
6. first autoregressive generation only when token-step baseline is not dominated by unexplained overhead;
7. DFlash integration only if net-positive under the measured memory/cache budget.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
