# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — WP1 Runtime + Product Serving is GO; WP2 Context Intelligence is GO and persisted. Canonical DEEP is S32 on localhost `llama-server` with Caveman+Cavemem enabled by default for the Pi local provider. Before WP3, one mechanical repository gap remains: persist the validated `scripts/loom-deep-server` lifecycle script, which is still local/untracked.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.84.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.

## Canonical DEEP

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

Serving-path prompt/KV reuse remains directly validated under `--cache-ram 512`.

## WP1 — COMPLETE / GO

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Validated lifecycle interface:
`scripts/loom-deep-server start|status|health|stop`.

Important persistence note: `config/loom-deep-server.env` is now in GitHub, but `scripts/loom-deep-server` is still an untracked local file and absent from GitHub. Persist only this validated script before WP3.

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

Persisted WP2 files include:
- `.pi/extensions/loom-context.ts`;
- `scripts/loom-context`;
- `scripts/test_loom_context.py`;
- `scripts/benchmark_context_intelligence_wp2.py`;
- `benchmarks/context-intelligence-wp2/frozen-cases.json`;
- `config/loom-deep-server.env`;
- `.gitignore` with `.loom/` exclusion;
- WP2 result document.

Canonical Context Intelligence architecture:
- Caveman deterministic host-side context packing/compression/recovery;
- Cavemem project-scoped SQLite/FTS5 memory and progressive retrieval;
- Pi hook runs at `before_provider_request` only for `loom-local`;
- no model-visible context tool, extra LLM, embeddings requirement, daemon or cloud path;
- fail-open behavior preserves WP1 provider operation if WP2 fails.

Validated WP2 benchmark:
- A/B/C objective success `6/7` each;
- shared miss was the frozen 16-token cap on a 40-hex answer, baseline-equivalent;
- combined heavy-context median provider-input reduction **23.24%**;
- small/no-op input overhead **0%**;
- recovery `6/6`, **100% SHA-verified**;
- no stale-memory accepted wrong answer;
- real local Pi combined-path task passed;
- server remained healthy.

Canonical Pi model label:
`loom-local/loom-deep-30b-s32`.

Rollback only Context Intelligence:
`LOOM_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32`

## Current exact action

Do not begin WP3 yet.

Persist only the already-validated local file:
`scripts/loom-deep-server`

Do not commit any of the many other untracked historical/research scripts shown in the local working tree. After that bounded persistence commit is verified, WP3 may be authorized.

## Later

WP3 — Behavioral Transform:
Abliterix-derived MoE-aware route first, then Heretic, Senbonzakura-style methods, then a clean LOOM-native equivalent if required by GGUF/llama.cpp/Apple Silicon constraints.

WP4 — Final Integration + Acceptance.
