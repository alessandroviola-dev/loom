# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — full 30B generation proven; 4-GiB raw cache rejected; DFlash static fit plausible but integration blocked
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001_CONDITIONAL_STATIC_MEMORY_FIT__INTEGRATION_BLOCKED`
Next core checkpoint: `LOOM_30B_DFLASH_TARGET_INTERFACE_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models must eventually pass validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent: `research/behavior/decensoring-requirement-v1.md`.

## Operating split / token-efficient protocol

Pi: local code/runtime inspection, implementation, tests/benchmarks and concise local evidence.
ChatGPT: scientific direction, experiment design/review, GitHub synchronization, `HANDOFF.md`, `ROADMAP.md` and project continuity.

Local override: Pi does not perform Git/GitHub administration or edit HANDOFF/ROADMAP unless explicitly overridden.

Root `/AGENTS.md` is the persistent Pi context. Future prompts should be compact work packages; do not restate stable history. `.qwen/settings.json` configures a 4096-token local agent context, so unnecessary repetition is explicitly avoided.

## Stable target anatomy

Local model: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`.

- 48 MoE layers; 128 routed experts/layer; top-k 8;
- total tensor payload 16,220,499,968 B;
- resident non-routed target 819,015,680 B;
- external routed bank 15,401,484,288 B;
- one expert 2,506,752 B;
- zero-cache expert traffic 962,592,768 B/token (918 MiB);
- BF16 KV 98,304 B/token.

## Proven architecture/runtime

1. `LOOM_30B_MOE_EXPERT_PACK_001_PASS`: lossless expert-major `9 ranges -> 1 contiguous read`.
2. `LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`: device-verified random expert ~1.89 GB/s; zero-cache storage-only floor ~0.4816 s/token.
3. `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS`: bitwise-exact layer with one 2,506,752-B expert live at a time; 99.21875% expert-bank residency reduction.
4. `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS`: complete 819,015,680-B shared target resident; zero routed experts.
5. `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL`: all 48 layers and final logits exact; full 16.22-GB capacity represented with routed bank external.
6. `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`: observer GC/RSS overhead removed; clean `GC_END_ONLY` full forward 1.641729 s, zero isolated swap delta.
7. `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`: first real generation, `4` then EOS; source zero-cache decode ~0.6471 tok/s; BF16 KV correct; no expert leak/swap growth.
8. `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`: packed layout reduced real expert-read wall 59.27% and total decode wall 43.72%; packed decode-equivalent ~1.0799 tok/s, exact output.
9. `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001_PASS`: real temporal reuse confirmed; simulated 4-GiB global LRU ~79.598% hit, but current single-token perfect-cache ceiling only ~2.066 tok/s.
10. `LOOM_30B_MOE_REAL_RAW_CACHE_001_MEMORY_FAIL`: real 4-GiB raw LRU achieved 80.9056% hit but swap grew +2410.56 MiB and decode slowed to 0.204763 tok/s. Do not reuse this cache design or jump to persistent live-MLX caching.

## DFLASH-SPECULATOR-STATIC-001 — CONDITIONAL STATIC FIT / INTEGRATION BLOCKED

Report: `research/architecture/loom-30b-dflash-speculator-static-001-result.md`.
Raw evidence: `results-local/research/dflash-speculator-static-001/20260824T100455Z/`.

Exact-target candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Recovered exact/static facts:
- learned BF16 weight elements: 680,813,824;
- total tensor elements including mappings: 680,997,760;
- published safetensors: **1,362,042,120 B = 1.268501 GiB**;
- tensor payload: 1,362,035,584 B;
- 5-layer Qwen3-style draft;
- hidden 2048; 32 Q heads; 4 KV heads; head_dim 128; MLP 6144;
- draft vocab 32,000;
- block=8 / proposals=7;
- exact target taps: **[1,12,23,34,45]**;
- concatenate 5 target states to width 10,240, then `fc[2048,10240] + RMSNorm`;
- fused target context is injected into draft K/V in each draft layer.

Footprint accounting:
- BF16 published: 1.268501 GiB exact;
- FP16 same-shape: same width-equivalent footprint;
- INT8 raw lower bound: 681,228,296 B / 0.634443 GiB; quantization metadata unknown;
- INT4 raw lower bound: 340,821,384 B / 0.317415 GiB; quantization metadata unknown.

Static M1/8-GB accounting remains plausible. With measured LOOM hybrid resident basis 1,538,371,592 B, 1 GiB runtime reserve and target BF16 KV, a BF16 draft at 2,048 target tokens leaves ~4.111 GiB arithmetic headroom under 8 GiB and ~2.111 GiB under a conservative 6-GiB process budget. Analytical DFlash BF16 KV is 10,240 B/context-token; 2,048+8 adds ~21.05 MB. This is not a measured MLX runtime footprint.

Compatibility:
- current MLX/LOOM: no native DFlash path; custom port required;
- llama.cpp: upstream draft-dflash/GGUF support exists conditionally, but no local compatible LOOM external-expert target path is established;
- vLLM publisher path is CUDA/server-oriented and not M1 evidence.

Gate:
- architecture/bytes PASS;
- target taps PASS;
- footprint `PASS_WITH_QUANTIZATION_LIMIT`;
- M1 static memory `CONDITIONAL_PASS`;
- current-runtime compatibility `FAIL_NO_NATIVE_PATH`;
- integration **NO**.

## Exact next step — `LOOM_30B_DFLASH_TARGET_INTERFACE_001`

Do **not** integrate the drafter yet.

First prove the target-side interface required by DFlash in the existing external-expert MLX runtime:
1. capture exact hidden states after target layers `[1,12,23,34,45]` during a real target forward/decode;
2. preserve target router choices and final logits exactly versus the current baseline;
3. quantify tap-buffer bytes and MLX/RSS/swap overhead;
4. prove no routed-expert lifecycle regression;
5. establish a stable tensor contract `(shape,dtype,position semantics)` usable by a future drafter port;
6. do not implement DFlash fusion, draft layers, masking or speculative acceptance yet.

If this passes, the next checkpoint should isolate **multi-position target verification/block semantics** independently of the drafter. Only after both target interface and block verifier exist should a DFlash port be attempted.

## Strategic interpretation

DFlash is no longer being considered as a memory-fit mechanism; the full 30B already generates on M1 8 GB. Its potential value is escaping the ~2.066 tok/s single-token fixed-cost ceiling through multiple accepted tokens per target verification and expert-union amortization.

Real trace union structure remains favorable but not sufficient evidence of DFlash speed:
- block 2: 749,343,645 B/position;
- 3: 642,396,979;
- 4: 570,480,569;
- 5: 519,237,866;
- 6: 479,315,740;
- 7: 446,068,713;
- 8: 417,808,712.

## Later branches

1. `LOOM_30B_DFLASH_TARGET_INTERFACE_001`.
2. Multi-position/block target verification with exact parity and external-expert lifecycle.
3. Only then port/instantiate the DFlash drafter if target-side prerequisites pass.
4. Measure accepted tokens/verification, unique external expert bytes per accepted token, workspace and sustained generation speed.
5. Revisit smaller/admission-controlled cache only if complementary to block/DFlash memory economics; the 4-GiB raw cache remains rejected.
6. Capability benchmark after practical speed improves.
7. Behavioral decensoring validation before final promotion.

## Local-only warning

Experimental scripts/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.