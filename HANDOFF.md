# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — first complete 30B external-expert forward
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS`
Next core checkpoint: `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001`
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

A real layer-0 decoder layer executed with canonical MLX semantics while routed experts remained external and only one selected expert was live at a time.

Correctness:
- router IDs/weights bitwise exact;
- all 8 selected expert outputs bitwise exact;
- MoE output bitwise exact;
- complete decoder-layer output bitwise exact (`atol=0`, `rtol=0`).

Residency:
- CONTROL full expert bank: 320,864,256 B;
- SERIAL_EXPERT maximum logical expert bytes live: 2,506,752 B;
- expert residency reduction: 99.21875%;
- CONTROL peak MLX / RSS: 331,495,092 B / 644,284,416 B;
- SERIAL_EXPERT peak MLX / RSS: 12,938,408 B / 130,367,488 B;
- ownership/release audit PASS.

Timing:
- external MoE P50 15.455 ms;
- full treatment layer P50 16.282 ms;
- descriptive physical-I/O+compute one-layer bound 14.103 ms.

## SHARED-BACKBONE-RESIDENCY-001 — PASS

Report: `research/moe/loom-30b-moe-shared-backbone-residency-001-result.md`.
Raw evidence: `results-local/moe/shared-backbone-residency-001/20260824T071921Z/`.

The complete non-routed Qwen3-30B-A3B target was constructed by exact targeted safetensor reads while every routed-expert tensor remained absent.

Exact results:
- resident non-expert tensors: 919;
- logical stored bytes: 819,015,680 B — exact reconciliation PASS;
- routed-expert tensors resident: 0 / 0 B;
- final MLX active: 819,032,072 B;
- final MLX cache: 0 B;
- final RSS: 817,463,296 B;
- peak MLX construction: 819,032,072 B;
- peak RSS construction: 1,122,189,312 B;
- swap: 921.94 -> 921.94 MiB, no growth;
- memory-pressure gate: PASS.

Functional checks all PASS:
- embedding;
- layer-0 attention;
- routers L0/L23/L47;
- final norm;
- LM head.

BF16 KV accounting:
- 98,304 B/token = 96 KiB/token;
- 1,024 tokens = 96 MiB;
- 4,096 = 384 MiB;
- 8,192 = 768 MiB.

Capacity reference at 2,506,752 B/expert:
- 512 MiB cache: 214 experts;
- 1 GiB: 428;
- 2 GiB: 856;
- 3 GiB: 1,285;
- 4 GiB: 1,713.

Decision: complete shared target viable YES; serial external-expert headroom YES; meaningful expert-cache headroom YES; plausible quantized-DFlash headroom YES; complete 48-layer external forward justified YES.

Strategic consequence: both independent prerequisites for a full 30B external-expert model path are now proven on the M1 8 GB machine:
1. all non-expert target structure resident at ~0.82 GB;
2. exact routed-expert computation with only one ~2.39 MiB expert live at a time.

## DFlash / block speculative branch

Source/video review complete. The supplied Qwen3.8-27B video does not demonstrate 27B viability on 8 GB, but independent research found an exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash` for `Qwen/Qwen3-30B-A3B`.

Published metadata indicates roughly ~0.7B draft parameters, 5 draft layers, target hidden-state taps at layers 1/12/23/34/45, and average acceptance length ~2.46–3.77 depending on workload.

DFlash is not a memory-fit solution. Potential LOOM value is multi-token target verification plus possible expert-union reuse across positions. This must be measured from real routing traces.

Canonical note: `research/architecture/dflash-qwen3-30b-a3b-relevance-001.md`.

## Exact next step — core

`LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001`

Goal: first complete end-to-end target forward through embedding, all 48 decoder layers, final norm and LM head with the full shared backbone resident and routed experts loaded only when selected.

For correctness, do not require the full 14.344 GiB expert-major pack. The first treatment may read exact selected expert slices directly from the original safetensors (9 component ranges/expert) or consume validated layer packs where available. A reference path can stream one full layer expert bank at a time rather than loading the whole 30B.

Required:
1. deterministic short token sequence;
2. CONTROL full-target forward with one complete layer expert bank resident at a time, released before the next layer;
3. TREATMENT full-target forward with only selected experts live, serially released;
4. compare layer checkpoints, final hidden state and logits for exact/tolerance parity;
5. record all real router top-k IDs per layer/position;
6. prove zero accumulation of routed-expert parameters across layers;
7. measure full-forward memory and timing breakdown;
8. no autoregressive generation yet, no cache/prefetch/DFlash assumptions.

If this passes, LOOM has a real full-capacity 30B forward path on M1 8 GB. The next steps become routing-trace/cache analysis and first generation, not basic feasibility.

## Parallel next

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001` — exact draft bytes/architecture/quantization/runtime-compatibility and budget impact.

Then `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001` from real router traces, followed by cache/reuse policy and DFlash integration only if net-positive.

## Storage state

Historical Qwen3-4B-GGUF, Qwen3-8B-GGUF and Qwen3-8B-4bit MLX are archived externally. Qwen3-8B-3bit and Qwen3-30B-A3B-MLX-4bit remain local. Expert-pack prototype uses ~612 MiB plus metadata. Latest observed free internal space was ~63 GiB before subsequent small evidence files.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
