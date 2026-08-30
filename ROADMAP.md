# LOOM Roadmap

Last updated: 2026-08-30
Current: WP1 Runtime + Product Serving GO and fully persisted. WP2 Context Intelligence GO and persisted. WP3 Behavioral Transform completed valid NO_GO for three GGUF-LoRA families. **WP3-R2 Behavioral Unlock is active** with materially different routes: exact-base abliterated replacement and native llama.cpp control-vector steering. WP4 remains blocked.
Canonical context: `/AGENTS.md` v3.87.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
R2 contract: `research/integration/loom-behavioral-unlock-wp3-r2.md`.

## 1. Canonical product baseline

- `loom-deep`: Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging **S32** through persistent localhost `llama-server`.
- canonical Pi model label: `loom-local/loom-deep-30b-s32`.
- S24 remains validated runtime rollback.
- Caveman + Cavemem Context Intelligence remains enabled by default and independently disableable.

## 2. WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Validated S32 median decode `5.596 tok/s`; S24 rollback `4.382 tok/s`. Local WebUI/API/Pi/cache/lifecycle are validated and persisted.

## 3. WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

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
- `23.24%` median heavy-context provider-input reduction;
- `0%` no-op overhead;
- `6/6` exact recovery SHA-verified.

## 4. WP3 — Behavioral Transform — VALID NO_GO

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Three actual runtime-loadable GGUF LoRA families were tested: rank-1 directional, MoE-router and rank-4 subspace/multi-direction. All loaded but frozen held-out refusal remained `6/6`, so those methods are rejected.

This is not a physical/toolchain block and not proof that the architecture cannot be unlocked.

## 5. WP3-R2 — Behavioral Unlock — ACTIVE

Checkpoint:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2`

Contract:
`research/integration/loom-behavioral-unlock-wp3-r2.md`

### Route A — exact-base behavioral replacement

Research found an independently abliterated derivative of the exact upstream base:
`huihui-ai/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated`.

GGUF quants are available from:
`mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF`.

First candidate:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`, published around 13.3 GB, `qwen3moe`.

Candidate must be treated as untrusted until exact local provenance/metadata/hash/behavior/capability/resource verification.

### Route B — native activation steering

Current llama.cpp supports control vectors at runtime and includes `cvector-generator` for GGUF models. This acts on layer activations during inference, a materially different intervention from WP3's failed LoRA adapters.

Use frozen contrast data disjoint from final held-out evaluation; bounded mean/PCA, layer-range and scale variants only.

### Promotion target

Retain original WP3 held-out gate unchanged.

`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO` requires:
- actual model-level or activation-level change;
- >=50% relative reduction from original `6/6` behavior baseline, preferably <=1/6 for a strong candidate;
- practical capability preservation;
- stable local serving with performance/RAM/swap evidence;
- exact hashes/provenance;
- Pi + WP2 compatibility;
- clean rollback to canonical S32 + WP2.

If local replacement/control-vector routes fail, inspect other evidence-backed Qwen3-A3B derivatives. External compute is a later explicit user-action boundary, not an automatic action.

## 6. WP4 — BLOCKED / NOT AUTHORIZED

Do not begin final acceptance while WP3-R2 is active.
