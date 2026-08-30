# LOOM — Active Handoff

Last updated: 2026-08-30
Status: WP1 Runtime + Product Serving GO and fully persisted; WP2 Context Intelligence GO and persisted; WP3 Behavioral Transform completed locally with valid NO_GO and awaits bounded persistence. WP4 is not authorized.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.86.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.

## Canonical product state

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Server binary SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`.

Runtime: **S32**. Rollback: S24.

Validated S32 performance:
- median decode `5.596 tok/s` vs S24 `4.382 tok/s`;
- median E2E `23.849 s` vs S24 `29.185 s`;
- decode ratio `1.2768x`;
- byte-identical matched outputs;
- peak RSS `3914.6 MiB`;
- peak sampled swap `1651.88 MiB`.

Operational endpoints:
- WebUI `http://127.0.0.1:18080/`;
- API base `http://127.0.0.1:18080/v1`;
- health `http://127.0.0.1:18080/health`.

Lifecycle:
`scripts/loom-deep-server start|status|health|stop`.

Lifecycle persistence commit:
`75e210f4d46cb8b7955e46763e329f28f37b699e`.

## WP1 — COMPLETE / GO / FULLY PERSISTED

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Canonical S32 serving stack, config and lifecycle script are represented in Git.

## WP2 — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`

Implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`

Contract:
`research/integration/loom-context-intelligence-wp2.md`

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

Validated WP2 benchmark:
- A/B/C objective success `6/7` each;
- combined heavy-context provider-input reduction **23.24%** median;
- no-op provider-input overhead **0%**;
- exact recovery **6/6, 100% SHA-verified**;
- real combined Pi task passed;
- server remained healthy.

Canonical Pi model label:
`loom-local/loom-deep-30b-s32`.

Rollback only Context Intelligence:
`LOOM_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32`

## WP3 — COMPLETE LOCALLY / NO_GO — PERSISTENCE PENDING

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Contract:
`research/integration/loom-behavioral-transform-wp3.md`

Local final report:
`research/integration/loom-behavioral-transform-wp3-result.md`

Evidence:
`results-local/behavioral-transform-wp3/20260830T144523Z/`

Reported tested transform families:
1. rank-1 directional GGUF LoRA;
2. MoE-router GGUF LoRA;
3. rank-4 subspace/multi-direction GGUF LoRA.

All were actually constructed and loaded through canonical `llama-server`, so WP3 is **not** physical/toolchain blocked.

Frozen behavior result:
- held-out refusal baseline/candidates remained `6/6`;
- target-behavior reduction `0%`;
- behavior promotion gate failed for all bounded routes;
- no adapter is promoted.

Rollback/result integrity:
- base S32 + WP2 restored;
- base hashes verified;
- `127.0.0.1:18080` health passed;
- rollback tested;
- WP4 not started.

Do not weaken the frozen behavior gate after seeing this result and do not substitute prompt-only behavior.

## Current exact action

Persist the bounded WP3 research package before WP4:
- final WP3 result document;
- frozen behavioral/capability evaluation specs needed to reproduce the classification;
- reusable small WP3 source/scripts/configs that generated/evaluated the tested adapters.

Do not commit:
- generated GGUF/LoRA adapter binaries;
- full/model artifacts;
- `results-local/`;
- caches/temp environments;
- home-directory config/secrets;
- unrelated historical untracked scripts.

After that persistence commit is reviewed, WP4 may be authorized.

## WP4 — PLANNED / NOT AUTHORIZED

WP4 final product candidate is the best validated state:
- S32 runtime/server/WebUI/API;
- serving prompt/KV reuse;
- Caveman + Cavemem enabled;
- no WP3 adapter enabled because WP3 is valid NO_GO.

WP4 may classify GO with a documented WP3 NO_GO if all final product acceptance gates pass.
