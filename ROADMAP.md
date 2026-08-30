# LOOM Roadmap

Last updated: 2026-08-30
Current: WP1 Runtime + Product Serving is GO. WP2 Context Intelligence is GO and persisted. Canonical DEEP is S32 at 5.596 tok/s median decode with local `llama-server`, serving-path cache reuse, and Caveman+Cavemem integrated into Pi. Before WP3, persist the single validated WP1 lifecycle script `scripts/loom-deep-server`, which remains local/untracked.
Canonical context: `/AGENTS.md` v3.84.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.

## 1. Canonical product state

- `loom-deep`: Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging **S32** through persistent localhost `llama-server`.
- canonical Pi model label: `loom-local/loom-deep-30b-s32`.
- S24 remains validated runtime rollback.
- `loom-balanced`: Qwen3-8B 3-bit ~13 tok/s remains lighter provisional tier.

## 2. WP1 — Runtime + Product Serving — COMPLETE / GO

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Validated S24/S32 matched A/B:
- S24 median decode `4.382 tok/s`, E2E `29.185 s`;
- S32 median decode **5.596 tok/s**, E2E **23.849 s**;
- decode improvement `1.2768x`;
- byte-identical outputs.

S32 resources:
- peak RSS `3914.6 MiB`;
- peak sampled swap `1651.88 MiB`;
- no critical crash/OOM/corruption.

Operational stack:
- embedded existing WebUI `http://127.0.0.1:18080/`;
- OpenAI-compatible API base `http://127.0.0.1:18080/v1`;
- localhost-only/offline;
- Pi verified against local server;
- serving-path stable-prefix reuse validated under `--cache-ram 512`.

Repository persistence gap:
`config/loom-deep-server.env` is persisted, but the validated lifecycle script `scripts/loom-deep-server` is still only local/untracked. Persist that single file before WP3.

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
- Pi `before_provider_request` bridge for `loom-local`;
- no extra LLM, embedding model, daemon or model-visible tool schema;
- reversible/fail-open integration.

Validated final comparison:
- A/B/C task success `6/7` each;
- combined heavy-context provider-input reduction **23.24%** median;
- no-op input overhead **0%**;
- exact recovery **6/6, 100% SHA-verified**;
- no accepted stale-memory error;
- real combined Pi task passed;
- server remained healthy.

Do not add LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

## 4. Current mechanical action

Persist only:
`scripts/loom-deep-server`

Do not sweep in unrelated untracked historical/research scripts. After the exact validated lifecycle script is safely committed and verified, this repository-persistence gap is closed.

## 5. WP3 — Behavioral Transform — PLANNED / NOT YET AUTHORIZED

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Goal:
produce an actual model/adapter-level behavioral transform with provenance, behavior evidence, capability preservation, resource measurement and a runtime-loadable artifact.

Technical priority:
1. Abliterix-derived MoE-aware methodology adapted to LOOM;
2. Heretic;
3. Senbonzakura-style multi-direction methods;
4. clean LOOM-native equivalent if upstream stacks are incompatible.

Select by fit to GGUF/llama.cpp/Apple Silicon, not popularity. Prefer a small reversible/runtime-loadable adapter when technically valid. Prompt-only behavior does not count.

## 6. WP4 — Final Integration + Acceptance — PLANNED

Assemble best validated WP1-WP3 outputs and run final end-to-end acceptance with exact hashes, capability/resource tests and documented operation.
