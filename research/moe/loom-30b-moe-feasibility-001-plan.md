# LOOM-30B-MOE-FEASIBILITY 001 — Plan

Date: 2026-08-23
Status: FROZEN PLAN

## Objective

Determine whether a full-parameter-count ~30B Mixture-of-Experts model can be made practically usable on Apple M1 / 8 GB by exploiting sparse expert activation rather than dense layer streaming.

Initial target: `Qwen/Qwen3-30B-A3B-MLX-4bit`.

Verified public architecture:
- 30.5B total parameters;
- 3.3B activated parameters;
- 48 layers;
- 128 routed experts per MoE layer;
- 8 activated experts per token;
- MLX 4-bit model repository size approximately 16.2 GB.

## Research question

Can LOOM keep shared/hot components resident while treating routed experts as cold storage-backed components, such that only selected experts need to be materialized for a token or short token block?

The purpose of this checkpoint is feasibility/anatomy, not throughput optimization.

## Phase 0 — storage and provenance

Download the official MLX 4-bit snapshot to local internal SSD. Record repository identity, revision if available, file list, total bytes and local free-space state. Do not attempt full-model generation as part of this phase.

## Phase 1 — static safetensors anatomy

Without loading the full model into unified memory:
1. parse config and safetensors index/header metadata;
2. identify shared/non-expert tensors;
3. identify router tensors;
4. identify expert tensor naming and per-expert tensor groups;
5. calculate raw bytes for one expert, one layer's routed expert bank, all shared tensors and all expert tensors;
6. determine whether expert tensors are stored contiguously enough for range-oriented loading or are fragmented across shards;
7. calculate the minimum logical expert bytes required for 8 selected experts per MoE layer under the stored 4-bit representation.

No generation and no whole-model `mlx_lm.load()` are required.

## Phase 2 — memory lower-bound model

Build a static accounting model for:
- shared persistent bytes;
- router persistent bytes;
- one expert working-set bytes;
- 8-expert working-set bytes;
- per-layer selected expert bytes;
- KV cache at small context lengths;
- temporary/materialization overhead allowance.

Classify whether a plausible <=8 GB resident/working-set architecture exists before implementing a runtime.

## Phase 3 — routing/access feasibility

Only if Phase 2 is plausible, design a source-level runtime experiment that preserves all model parameters while loading or mapping only routed experts on demand. Expert caching/prefetch is a later factor; first prove exact routed expert access and token parity against a reference on a host/configuration where the reference can run.

## Scientific rules

- full parameter count remains available to the model;
- no expert pruning as a hidden simplification;
- no claim that 3.3B activated parameters equals 3.3B storage traffic without measuring actual expert reuse and shared computation;
- process-read telemetry is not physical SSD proof;
- static byte accounting precedes performance claims;
- do not infer practical speed from nominal USB/SSD bandwidth alone;
- dense Qwen3-8B remains the canonical controlled runtime baseline, but this 30B MoE direction is now the primary high-impact scale path.

## First completion criterion

`LOOM_30B_MOE_FEASIBILITY_001_STATIC_COMPLETE` when the local snapshot is fully indexed and a byte-accurate decomposition of shared/router/expert storage plus the theoretical per-token expert working set is recorded.

No requirement to generate a token in this first checkpoint.
