# LOOM Roadmap

Last updated: 2026-08-30
Current: WP1 Runtime + Product Serving GO and fully persisted. WP2 Context Intelligence GO and persisted. WP3 Behavioral Transform completed locally with valid NO_GO and awaits bounded persistence. WP4 is planned but not authorized.
Canonical context: `/AGENTS.md` v3.86.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.

## 1. Canonical product state

- `loom-deep`: Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging **S32** through persistent localhost `llama-server`.
- canonical Pi model label: `loom-local/loom-deep-30b-s32`.
- S24 remains validated runtime rollback.
- Caveman + Cavemem Context Intelligence is enabled by default for the local Pi provider and can be disabled independently.
- no behavioral adapter is promoted after WP3 NO_GO.

## 2. WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

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

Operational stack:
- embedded existing WebUI `http://127.0.0.1:18080/`;
- OpenAI-compatible API base `http://127.0.0.1:18080/v1`;
- localhost-only/offline;
- Pi verified against local server;
- serving-path stable-prefix reuse validated under `--cache-ram 512`;
- lifecycle helper `scripts/loom-deep-server` persisted in commit `75e210f4d46cb8b7955e46763e329f28f37b699e`.

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
- real combined Pi task passed;
- server remained healthy.

## 4. WP3 — Behavioral Transform — COMPLETE LOCALLY / NO_GO

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Local result:
`research/integration/loom-behavioral-transform-wp3-result.md`

Evidence:
`results-local/behavioral-transform-wp3/20260830T144523Z/`

Actual runtime-loadable GGUF LoRA transform families tested:
1. rank-1 directional;
2. MoE-router;
3. rank-4 subspace/multi-direction.

Frozen held-out refusal remained `6/6` for every tested candidate, producing `0%` target-behavior reduction. Therefore the frozen promotion gate failed and no adapter is promoted.

This is a scientific NO_GO, not a physical block: adapters were actually generated and loaded through canonical `llama-server`.

Base S32 + WP2 was restored, hash-verified, health-checked and rollback-tested on port 18080.

Do not relax the frozen behavior gate or substitute prompt-only behavior after this result.

Before WP4, persist the bounded reproducibility package: WP3 result, frozen eval specifications, and reusable small source/scripts/configs. Exclude generated adapters/models and `results-local/`.

## 5. WP4 — Final Integration + Acceptance — PLANNED / NOT AUTHORIZED

WP4 should assemble the strongest validated product state:
- S32 runtime/server/WebUI/API;
- validated serving-path prompt/KV reuse;
- Caveman + Cavemem;
- no behavioral adapter enabled because WP3 completed valid NO_GO.

WP4 may still classify GO when WP3 is explicitly retained as NO_GO, provided clean startup, API/WebUI/Pi, capability/resource, privacy, rollback, exact hashes/provenance and operational documentation all pass.
