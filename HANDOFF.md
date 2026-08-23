# LOOM — Active Handoff

Last updated: 2026-08-23
Status: ACTIVE — 30B MoE feasibility / sparse expert offload
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_MODEL_DOWNLOADED`
Next: `LOOM_30B_MOE_FEASIBILITY_001_STATIC`

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

## Dense streaming findings retained

Exact partial residency works, but naïve synchronous dense layer streaming is too slow. Shared stages embedding/final norm/LM head are hot/persistent.

Promoted cleanup improvements:
- shared intermediate cleanup consolidation: +25.206% generation / -35.678 ms/token;
- streamed-layer post-forward cleanup defer: +17.522% generation / -21.308 ms/token.

Retained boundaries:
- embedding eval removal NO-GO;
- norm eval removal SMALL/not promoted;
- select-time GC removal NO-GO: 8.293 -> 7.767 tok/s, +8.177 ms/token, free floor 19% -> 11%; retain select-time GC.

STREAMED-LAYER-GRADIENT002 under promoted lifecycle:
- S0 90.078 ms/token
- S1 124.425
- S2 152.775
- S4 199.383
- marginal penalties 34.347, 28.350, 23.304 ms/layer for first, second, layers 3–4 respectively.

Cleanup cadence is exhausted unless new evidence appears.

## STREAMED-BLOCK-REUSE-AUDIT001 — COMPLETE

Report: `research/memory/streamed-block-reuse-audit-001-result.md`.
Raw local evidence: `results-local/memory/streamed-block-reuse-audit-001/20260823-181531/`.

Audit proved that weight-independent Qwen3/quantized topology can exist without retaining streamed layer weights. A detached shell retained 0 native MLX parameter bytes, no recursively found MLX arrays and no surviving weakrefs to the 25 selected layer arrays; block-output parity passed.

However, current `Module.load_weights(..., strict=True)` requires existing same-shape parameter leaves. A truly parameter-free shell cannot preserve current binding semantics. Placeholder arrays violate the metadata-only requirement; direct path-wise rebinding changes a second factor.

Decision: do not run the construction-only block-reuse A/B. Revisit only if parameter binding itself becomes an explicit redesign factor.

## Strategic scale pivot — 30B MoE

Dense micro-optimization research remains valuable as controlled systems knowledge, but it is no longer the only primary path to ~30B on 8 GB. The high-impact scale hypothesis is sparse activation: full parameter count exists, but only a small routed subset is active/materialized per token.

Initial target: `Qwen/Qwen3-30B-A3B-MLX-4bit`.
Verified public architecture: 30.5B total parameters, 3.3B activated, 48 layers, 128 experts, 8 activated experts/token, ~16.2 GB MLX 4-bit repository.

Frozen plan: `research/moe/loom-30b-moe-feasibility-001-plan.md`.

## 30B model download — COMPLETE

Local model path:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Observed local snapshot:
- total model directory: ~15 GiB by `du`
- 4 safetensors shards
- shard sizes approximately 5.0 GiB, 4.9 GiB, 4.9 GiB and 260 MiB
- internal SSD free after download: ~64 GiB

No full-model inference has been attempted.

## Exact next step

`LOOM_30B_MOE_FEASIBILITY_001_STATIC`

1. parse local `config.json`, safetensors index and tensor headers without whole-model materialization;
2. recover exact tensor naming/layout for shared backbone, routers and routed experts;
3. byte-account shared tensors, router tensors, one expert, expert banks by layer and full model;
4. compute selected-expert bytes/token for top-k=8 across all MoE layers;
5. distinguish bytes that must be resident from bytes that can remain external;
6. inspect shard/range locality and whether one routed expert is contiguous or fragmented on disk;
7. model 8 GB resident-cache scenarios and external bandwidth lower bounds;
8. do not run generation and do not load the full model.

Static feasibility must decide whether a real external-expert runtime is structurally plausible before implementation.

## Storage state

Mac internal SSD was cleaned for the 30B phase. Historical Qwen3-4B-GGUF, Qwen3-8B-GGUF and Qwen3-8B-4bit MLX were moved to external archive. Canonical `Qwen3-8B-3bit` remains local. Internal free space after 30B download: ~64 GiB.

## Later if static feasibility passes

1. exact routed-expert access prototype;
2. expert cache/reuse measurement;
3. routing prediction/prefetch only after access trace evidence;
4. token-block/multi-token amortization where correctness permits;
5. storage layout/range-I/O redesign only when evidence supports it;
6. if existing MoE architecture remains fundamentally unsuitable, define LOOM-native architecture requirements from measured failure modes;
7. capability comparison and behavioral-freedom validation before final promotion.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
