# LOOM — Active Handoff

Last updated: 2026-08-30
Status: WP1 Runtime + Product Serving GO and fully persisted; WP2 Context Intelligence GO and persisted; WP3 Behavioral Transform completed valid NO_GO for three adapter families; **WP3-R2 Behavioral Unlock is now authorized and active**. WP4 remains blocked.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.87.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
Current R2 contract: `research/integration/loom-behavioral-unlock-wp3-r2.md`.

## Canonical product baseline

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Server binary SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`.

Runtime: **S32**. Rollback: S24.

Validated performance:
- S32 median decode `5.596 tok/s` vs S24 `4.382 tok/s`;
- S32 median E2E `23.849 s` vs S24 `29.185 s`;
- byte-identical matched outputs.

Operational endpoints:
- WebUI `http://127.0.0.1:18080/`;
- API base `http://127.0.0.1:18080/v1`;
- health `http://127.0.0.1:18080/health`.

Lifecycle:
`scripts/loom-deep-server start|status|health|stop`.

## WP1 — COMPLETE / GO / FULLY PERSISTED

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

## WP2 — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`

Implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`

Result:
`research/integration/loom-context-intelligence-wp2-result.md`

Evidence:
`results-local/context-intelligence-wp2/20260830T133259Z/`

Canonical Context Intelligence:
- Caveman deterministic context selection/compression/recovery;
- Cavemem SQLite/FTS5 progressive project memory;
- Pi host-side `before_provider_request` bridge for `loom-local`;
- combined heavy-context provider-input reduction `23.24%` median;
- no-op overhead `0%`;
- exact recovery `6/6`, SHA-verified.

Canonical Pi model label:
`loom-local/loom-deep-30b-s32`.

## WP3 — VALID NO_GO, NOT IMPOSSIBILITY

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Local result:
`research/integration/loom-behavioral-transform-wp3-result.md`

Evidence:
`results-local/behavioral-transform-wp3/20260830T144523Z/`

Tested actual GGUF LoRA families:
1. rank-1 directional;
2. MoE-router;
3. rank-4 subspace/multi-direction.

All loaded successfully but the original held-out refusal remained `6/6`, so those bounded adapter methods are rejected. Base S32 + WP2 was restored.

This does not establish architectural impossibility.

## Current — WP3-R2 Behavioral Unlock

Checkpoint:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2`

Status: **AUTHORIZED / ACTIVE**.

Contract:
`research/integration/loom-behavioral-unlock-wp3-r2.md`

### Priority route A — exact-base abliterated replacement

Discovered behavioral derivative:
`huihui-ai/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated`

Declared upstream base:
`Qwen/Qwen3-30B-A3B-Instruct-2507`.

GGUF source:
`mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF`

First candidate:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

Published around 13.3 GB, `qwen3moe`. Treat as untrusted until local hash/metadata/behavior/capability verification.

### Priority route B — llama.cpp native control vectors

Use `cvector-generator` and runtime control-vector flags on GGUF. This operates on activations during generation and is materially different from WP3 LoRA weight edits.

### Promotion

Retain the original frozen WP3 held-out behavior set unchanged.

R2 GO requires >=50% relative reduction from original `6/6`, practical capability preservation, local stability, exact provenance/hashes, measured resources/performance, Pi/WP2 integration and clean rollback.

If A/B fail, inspect other evidence-backed Qwen3-A3B derivatives. If local methods are exhausted and only full-weight/fine-tuning compute remains credible, return with an exact external-compute plan instead of proceeding to WP4.

## WP4

Not authorized. Do not begin until WP3-R2 completes or returns a genuine user-action/external-compute blocker.
