# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — 30B MoE external-expert runtime / whole-model residency research
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS`
Next core checkpoint: `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001`
Parallel next: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Every final promoted LOOM-produced model must eventually pass validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.
ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical dense baseline

Qwen3-8B full parameter count; affine 3-bit/group64; BF16 KV; MLX/mlx-metal 0.31.2; mlx-lm 0.31.3; thinking disabled.

REALGEN001 historical real M1 generation: 13.184615357 tok/s; E2E 12.046861457 tok/s.
CAPABILITY001: practical-agent 1/11 = 9.09%; Coding Benchmark 45/100; critical failures 0.

Dense partial-residency research remains a controlled implementation laboratory. Naive synchronous dense streaming is too slow; current cleanup/binding micro-axes are exhausted absent new evidence.

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
- mandatory/non-routed 819,015,680 B (0.763 GiB);
- routed expert bank 15,401,484,288 B (14.344 GiB);
- one expert 2,506,752 B;
- top-k/layer 20,054,016 B;
- zero-cache expert traffic/token 962,592,768 B (918 MiB).

Static result: `LOOM_30B_MOE_FEASIBILITY_001_STATIC_CONDITIONAL`.

## Expert-major storage — PASS

`LOOM_30B_MOE_EXPERT_PACK_001_PASS` proved lossless expert-major packing on layers 0 and 15:
- 256 experts / 641,728,512 B validated;
- zero hash/byte/metadata mismatches;
- source 9 ranges/expert -> packed 1 contiguous range/expert;
- top-k=8 reads 72 -> 8;
- byte amplification 1.0x;
- 100% packed useful/span efficiency.

Full 14.344 GiB repack remains deferred until whole-model runtime evidence makes it necessary.

## Physical I/O — DEVICE VERIFIED / CONDITIONAL

`LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL` established the real internal-SSD baseline on APPLE SSD AP0256Q (`disk0`) using device-level `iostat` evidence.

Canonical results:
- sequential physical 2,391.9 MB/s;
- random expert physical 1,890.4 MB/s;
- expert latency P50/P90/P95/P99 1.197 / 1.509 / 1.643 / 2.019 ms;
- top-k=8 physical 1,823.1 MB/s;
- top-k latency P50/P90/P95/P99 9.839 / 12.622 / 13.159 / 14.783 ms;
- token-like 384-read P50 460.074 ms;
- zero-cache storage-only lower bound 0.4816 s/token;
- storage-only maximum 2.076 tok/s.

Required external-traffic reduction from storage alone:
- 5 tok/s: 58.47%;
- 10 tok/s: 79.24%.

Interpretation: SSD bandwidth is not a structural NO-GO, but cache/reuse and/or multi-token amortization are primary requirements for high usability.

Report: `research/moe/loom-30b-moe-physical-io-002-result.md`.

## ONE-LAYER-EXTERNAL-EXPERT-001 — PASS

Report: `research/moe/loom-30b-moe-one-layer-external-expert-001-result.md`.
Raw evidence: `results-local/moe/one-layer-external-expert-001/20260824T070045Z/`.

A real layer-0 Qwen3-30B-A3B decoder layer executed with canonical MLX semantics while routed experts remained external and only one selected expert was live at a time.

Correctness:
- deterministic T1/T4/T8 float16 inputs;
- T1 top-k expert IDs `[118, 56, 65, 84, 98, 97, 119, 36]`;
- router IDs and weights bitwise exact;
- all 8 selected expert outputs bitwise exact;
- MoE output bitwise exact;
- complete decoder-layer output bitwise exact (`atol=0`, `rtol=0`).

Residency:
- CONTROL full expert bank: 320,864,256 B;
- SERIAL_EXPERT maximum logical expert bytes live: 2,506,752 B;
- expert residency reduction: 99.21875%;
- CONTROL peak MLX / RSS: 331,495,092 B / 644,284,416 B;
- SERIAL_EXPERT peak MLX / RSS: 12,938,408 B / 130,367,488 B;
- ownership/release audit PASS; expert arrays were dead before the next expert load.

Timing:
- external MoE P50 15.455 ms;
- full treatment layer P50 16.282 ms;
- descriptive physical-I/O+compute one-layer bound 14.103 ms;
- linear 48-layer descriptive extrapolation 0.677 s, explicitly not a full-model token prediction.

Early synthetic routing overlap only:
- T4: 30 unique experts / 32 selections;
- T8: 51 / 64.

Strategic consequence: external-expert computation is now proven correct and memory-efficient. The remaining primary questions are whole-model shared/backbone residency and traffic reduction, not per-expert correctness.

## DFlash / block speculative branch

Video/source review is complete. The supplied Qwen3.8-27B video does not demonstrate 27B viability on 8 GB, but independent research found an exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash` for `Qwen/Qwen3-30B-A3B`.

Published metadata indicates roughly ~0.7B draft parameters, 5 draft layers, target hidden-state taps at layers 1/12/23/34/45, and average acceptance length ~2.46–3.77 depending on workload.

DFlash is not a memory-fit solution. Potential LOOM value is multi-token target verification plus possible expert-union reuse across positions. This must be measured from real routing traces.

Canonical note: `research/architecture/dflash-qwen3-30b-a3b-relevance-001.md`.

## Exact next step — core

`LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001`

Goal: prove that the entire non-expert target structure can remain resident on the 8 GB M1 without materializing routed expert banks.

Required:
1. instantiate/load embeddings, all 48 attentions, all norms, all routers, final norm and LM head;
2. exclude every routed expert tensor and prove exclusion by ownership/inventory;
3. compare logical stored bytes with actual MLX active/peak/cache memory and RSS;
4. inspect Python/module overhead and temporary load peaks;
5. determine safe remaining memory budgets for KV/runtime/expert cache/DFlash;
6. do not run full generation and do not silently materialize expert banks.

If the shared backbone residency test passes, LOOM will have separately proven both components required for a full external-expert forward: resident shared structure + exact serial expert execution.

## After backbone residency

Next candidate: `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001` — first complete 48-layer forward using resident shared backbone and external selected experts, initially without speculative decoding or cache assumptions. This should also begin real router-trace collection.

Parallel: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`.

Then: `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001` using real routing traces, followed by cache/reuse policy and only then DFlash integration if net-positive under the 8 GB budget.

## Storage state

Historical Qwen3-4B-GGUF, Qwen3-8B-GGUF and Qwen3-8B-4bit MLX are archived externally. Qwen3-8B-3bit and Qwen3-30B-A3B-MLX-4bit remain local. Expert-pack prototype uses ~612 MiB plus metadata. Latest observed free internal space was ~63 GiB before subsequent small evidence files.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
