# LOOM — Active Handoff

Last updated: 2026-08-23
Status: ACTIVE — high-leverage architecture / external-expert exploration
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STREAMED_BLOCK_REUSE_AUDIT_001_COMPLETE`
Strategic next: `QWEN3_30B_A3B_EXTERNAL_EXPERT_FEASIBILITY_001`

## Mission

**Big models. Small machines.** Target ~27B/32B-class local capability on Apple M1 / 8 GB while balancing memory, speed, capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

## Operating split

Pi: local code/runtime inspection/tests/evidence.
ChatGPT: research direction, experiment design/review, GitHub synchronization, HANDOFF/ROADMAP.

## Canonical dense laboratory

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2 / mlx-lm 0.31.3.

Dense research remains valuable as a controlled laboratory for MLX lifecycle and exact partial residency, but is no longer assumed to be the only route to the 27B/32B objective.

## Dense-streaming results retained

- MEMORY-FRONTIER001: exact partial residency proven; naive synchronous streaming too slow.
- shared stages embedding/final norm/LM head should remain resident.
- shared intermediate cleanup consolidation: +25.206%, promoted.
- embedding eval removal: NO-GO; norm eval removal: SMALL/not promoted.
- streamed post-forward cleanup defer: +17.522%, promoted.
- Gradient002 under improved lifecycle: S0/S1/S2/S4 = 11.101/8.037/6.546/5.015 tok/s; exact; resource-safe through four streamed layers.
- Gradient002 descriptive fit: `90.078 + 11.043*I(streaming) + 24.746*N` ms/token, R² 0.998866.
- select-time GC removal: NO-GO (-6.351%); retain it.

Cleanup cadence is considered exhausted on the current implementation.

## STREAMED-BLOCK-REUSE-AUDIT001 — COMPLETE

Report: `research/memory/streamed-block-reuse-audit-001-result.md`.
Raw local evidence: `results-local/memory/streamed-block-reuse-audit-001/20260823-181531/`.

Current layer-35 path constructs a fresh Qwen3 block and quantized structure every token after loading/selecting 84,427,264 B of layer weights.

Audit proved that a weightless topology shell can exist with zero retained native MLX parameter bytes and release all current streamed arrays. However, current strict `Module.load_weights` requires existing same-shape parameter leaves. A parameter-free shell cannot preserve the current binding path; placeholder parameters violate the metadata-only requirement; direct path-wise rebinding changes a second factor.

Classification: `STREAMED_BLOCK_REUSE_AUDIT_001_COMPLETE`.
Decision: do not run a construction-only reuse A/B under the present strict binding lifecycle.

## High-leverage architecture exploration — NEW

Research note: `research/architecture/high-leverage-architecture-exploration-001.md`.

Main conclusion: a dense 32B that reads most weights every token is probably the wrong end-state for 8 GB. The highest-leverage literature changes the model-system contract so most parameters are cold by construction.

Priority evidence:

1. **Sparse MoE / external experts.** Qwen3-30B-A3B has 30.5B total parameters but only 3.3B active per token (128 experts, 8 active). PowerInfer-2, EdgeMoE, MoE-Infinity, Fiddler and KTransformers show that sparse experts can be split across a memory hierarchy with prediction/caching/orchestration.
2. **Neuron/cluster-level sparse access.** PowerInfer/DejaVu and Apple's `LLM in a Flash` show that active neuron subsets and flash-aware storage/layout can reduce transferred bytes dramatically compared with layer-wise loading.
3. **Multi-token/block execution.** Medusa, multi-token prediction, EAGLE and Lookahead reduce the number of full decode sweeps. This is especially valuable out-of-core because one weight load may serve several accepted positions.
4. **Recursive/shared weights.** Mixture-of-Recursions reuses a shared stack with adaptive recursion depth, attacking parameter capacity and compute together.
5. **External learned memory.** Memory Layers at Scale / RETRO / Memorizing Transformers suggest a smaller resident reasoning core plus large sparsely accessed external memory.
6. **Recurrent/SSM cores.** Mamba/Mamba-2, Griffin/RecurrentGemma and RWKV reduce state/KV costs; useful as a resident core but not sufficient alone for weight bandwidth.

## Strategic next — QWEN3_30B_A3B_EXTERNAL_EXPERT_FEASIBILITY001

Do not attempt full 30B inference first. Perform anatomy/traffic modeling only:
- exact shared/dense bytes per layer;
- exact expert bytes and active-expert bytes/token;
- quantized storage sizes relevant to M1;
- theoretical NVMe bandwidth floor for naive active-expert reads;
- routing/expert temporal-locality opportunities;
- hot-expert cache sizes that fit 8 GB;
- whether route prediction can overlap SSD fetch with preceding compute;
- compare whole-expert vs neuron-cluster granularity.

This is a parallel high-leverage track. Dense Qwen3-8B evidence is preserved and may continue as the implementation laboratory, but the project should no longer assume dense 32B streaming is the final architecture.

## Later high-leverage directions

1. external-expert feasibility/anatomy for Qwen3-30B-A3B
2. expert activation trace + cache/prefetch model
3. flash-aware contiguous expert/neuron-cluster representation
4. multi-token/block amortization under out-of-core weights
5. if needed, LOOM-native sparse/recursive model-system co-design
6. capability validation
7. behavioral decensoring validation before final promotion

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
