# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — WP1 Runtime + Product Serving GO and fully persisted; WP2 Context Intelligence GO and persisted; WP3 Behavioral Transform is now authorized and active.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.85.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
Current WP3 contract: `research/integration/loom-behavioral-transform-wp3.md`.

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

Lifecycle:
`scripts/loom-deep-server start|status|health|stop`.

Lifecycle script persistence commit:
`75e210f4d46cb8b7955e46763e329f28f37b699e`.

Validated script SHA256:
`616752d8bf3da44b5ab5244f429c03b6be7e30c917f6aa6e8651a03f6ed1d939`.

## WP1 — COMPLETE / GO / FULLY PERSISTED

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

The validated S32 serving stack, `config/loom-deep-server.env`, and lifecycle script are all represented in the repository. No remaining WP1 persistence blocker.

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
- no accepted stale-memory error;
- real combined Pi task passed;
- server remained healthy.

Canonical Pi model label:
`loom-local/loom-deep-30b-s32`.

Rollback only Context Intelligence:
`LOOM_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32`

## Current — WP3 Behavioral Transform

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Status: **AUTHORIZED / ACTIVE**.

Authoritative contract:
`research/integration/loom-behavioral-transform-wp3.md`

Goal:
produce an actual model/adapter-level behavioral transform for canonical LOOM DEEP, with frozen behavior evaluation, capability preservation, resource measurement, exact provenance and a reversible runtime-loadable artifact.

Prompt-only jailbreak/system-prompt changes do not count.

### Method strategy

WP3 does not mandate installation of Heretic/Abliterix/Senbonzakura.

Preferred progression:
1. LOOM-native Heretic-style/projected single-direction low-rank adapter;
2. Abliterix-derived MoE-aware refinement only if measured evidence supports it;
3. Senbonzakura-derived multi-direction/subspace if a stable single direction remains insufficient;
4. clean alternative low-rank directional route if the upstream-oriented representations are mechanically incompatible.

Why:
- internal Heretic paper identifies streaming residual means and reversible low-rank edits as the transferable core for constrained hardware;
- Abliterix adds Qwen MoE-specific concepts but its documented production/reference path is Linux/CUDA and far above M1 8 GiB resources;
- Senbonzakura adds multi-direction editing but also assumes a much heavier full-precision transformation path upstream;
- current llama.cpp supports separate GGUF LoRA adapters, which is the preferred final artifact representation.

### Preferred architecture

`frozen contrast sets -> streamed residual statistics -> stable direction/subspace -> low-rank delta -> GGUF adapter -> canonical llama-server -> behavior/capability/resource A/B`

Preserve the canonical base GGUF. Avoid a resident full BF16/FP16 30B copy when selected-tensor/streaming methods can avoid it.

### Internal gates

Pi should autonomously:
- freeze external method commits/revisions used as references;
- audit canonical Qwen MoE tensor/adapter mapping;
- implement bounded residual extraction/streaming parity evidence;
- start with projected/single-direction attention-output rank-1/low-rank candidates;
- escalate to MoE-aware or multi-direction methods only if evidence justifies it;
- generate and load a GGUF-compatible adapter if feasible;
- compare base vs transformed under frozen behavior/capability/resource tests;
- preserve base S32 and WP2 rollback throughout.

Do not return after routine candidate NO_GO results.

### WP3 classification

`LOOM_BEHAVIORAL_TRANSFORM_WP3_GO` requires an actual runtime-loadable transform, material frozen behavior improvement, preserved capabilities, practically usable throughput/resources, a real Pi transformed-profile request, successful rollback and durable evidence.

Target primary behavior improvement: >=50% relative reduction when the baseline target/refusal rate is large enough for that statistic to be meaningful.

Target transformed decode: >=90% of canonical S32 median unless a smaller loss is justified by a substantially stronger behavior/capability Pareto result.

`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO` = valid bounded transform families do not give a useful Pareto result.

`LOOM_BEHAVIORAL_TRANSFORM_WP3_PHYSICAL_BLOCKED` = proven host/toolchain/representation constraint prevents all actual model-level transforms after the bounded method ladder.

## Later

WP4 — Final Integration + Acceptance remains planned and not authorized.

Pi should not commit/push during WP3 execution. At the macro boundary ChatGPT may explicitly authorize one reviewed bounded persistence commit under `AGENTS.md`.
