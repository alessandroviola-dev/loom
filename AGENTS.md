# LOOM — Pi Agent Protocol

Version: 3.85
Mode: `ACCELERATED_MACRO_WORKPACKAGES / EVIDENCE_GATED`

Pi reads this file as persistent context. User-facing micro-checkpoints are retired for the current push.

## Roles / synchronization

Pi: local inspection/execution, implementation, bounded experimentation, local integration, durable `results-local/` evidence, autonomous continuation through internal gates inside an authorized macro work package.

ChatGPT: scientific direction, macro-package definition/review, canonical Git/GitHub persistence.

GitHub is canonical. Active clone:
`<repository-root>`.

Default rule: Pi must not commit/push/PR.

Narrow exception: at a completed macro-work-package boundary, ChatGPT may explicitly authorize one bounded persistence commit/push containing only reviewed package implementation/result/docs. Never include `.loom/`, `results-local/`, personal/home-directory config, secrets, caches, model artifacts, generated databases, or unrelated working-tree changes.

## Operating rule

Inside an authorized macro work package:
- do not return after routine internal GO/NO_GO results;
- record failed experiments;
- revert regressions;
- continue to the next justified action;
- preserve frozen scientific gates;
- keep one known-good runnable baseline.

Do not begin a later macro package until it is explicitly authorized.

## Core rules

1. evidence over narrative;
2. exact provenance for model/runtime/derived artifacts;
3. no silent gate relaxation or false promotion;
4. deterministic tests before expensive runs where practical;
5. bounded A/B comparisons for performance claims;
6. no public internet exposure by default;
7. do not disable SIP/change host security settings;
8. do not delete unrelated user data;
9. project-local dependencies/environments are allowed when required and recorded;
10. Pi Git persistence only under the explicit bounded exception above.

## Canonical DEEP runtime — WP1 GO

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Canonical `llama-server` SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Canonical runtime profile: **S32**. Rollback: S24.

Validated matched S24/S32 3x96-token A/B:
- S24 median decode `4.382 tok/s`, E2E `29.185 s`;
- S32 median decode `5.596 tok/s`, E2E `23.849 s`;
- decode ratio `1.2768x`;
- E2E ratio `0.8172`;
- byte-identical outputs.

Operational target:
- `scripts/loom-deep-server start|status|health|stop`;
- WebUI `http://127.0.0.1:18080/`;
- API base `http://127.0.0.1:18080/v1`.

WP1 result:
`research/integration/loom-runtime-productization-wp1-result.md`

Lifecycle script persistence commit:
`75e210f4d46cb8b7955e46763e329f28f37b699e`

Validated lifecycle script SHA256:
`616752d8bf3da44b5ab5244f429c03b6be7e30c917f6aa6e8651a03f6ed1d939`

## WP2 — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`.

Implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`

Contract:
`research/integration/loom-context-intelligence-wp2.md`

Result:
`research/integration/loom-context-intelligence-wp2-result.md`

Evidence:
`results-local/context-intelligence-wp2/20260830T133259Z/`

Canonical permanent layer:
- Caveman-derived deterministic context packing/compression/recovery;
- Cavemem-derived progressive project memory via SQLite/FTS5;
- Pi integration at `.pi/extensions/loom-context.ts` using `before_provider_request` for `loom-local` only;
- no extra LLM, embedding model, daemon, or model-visible tool schema;
- fail-open rollback path preserved.

Validated final benchmark:
- A/B/C objective success `6/7` each; shared JSON cap miss baseline-equivalent;
- combined heavy-context median provider-input reduction `23.24%`;
- no-op provider-input overhead `0%`;
- recovery `6/6`, `100%` SHA-verified;
- real Pi combined-path request passed;
- canonical provider/model label `loom-local/loom-deep-30b-s32`.

Rollback Context Intelligence:
`LOOM_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32`

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

## Current checkpoint — WP3 Behavioral Transform

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Status: **AUTHORIZED / ACTIVE**.

Authoritative contract:
`research/integration/loom-behavioral-transform-wp3.md`

Goal:
produce and validate an **actual model/adapter-level behavioral transform** for canonical LOOM DEEP while preserving capability, runtime usability, and rollback.

Prompt-only jailbreak/system-prompt behavior does not satisfy WP3.

### WP3 method priority

Use method families as engineering references, not mandatory dependencies:

1. **LOOM-native low-rank directional adapter** using the Heretic/projected-abliteration core as the lowest-cost production candidate;
2. **Abliterix-derived MoE-aware refinement** when measured evidence justifies expert/router/layer-specific treatment;
3. **Senbonzakura-derived multi-direction/subspace** if a stable single direction remains materially insufficient;
4. another clean low-rank directional equivalent only if upstream-oriented routes are mechanically incompatible.

Current external reality:
- Abliterix has MoE/Qwen A3B methods but documents Linux/CUDA as its production environment and large MoE reference runs far beyond the M1 8 GiB budget;
- Heretic's transferable core is streamed residual means + directional low-rank editing, while its bitsandbytes/NF4 path is not mandatory for LOOM;
- Senbonzakura adds multi-direction refusal-subspace editing but its upstream full-precision editing path is also not a natural M1-8GiB production route;
- llama.cpp supports separate GGUF LoRA adapters and server-side LoRA loading, which is the preferred final artifact path.

Do not port/install these frameworks wholesale merely to satisfy naming. Prefer a clean LOOM-native implementation using documented mathematical ideas and exact provenance. Avoid copying AGPL implementation code without explicit license review.

### WP3 architecture target

Preferred path:

`frozen contrast sets -> streamed residual statistics -> stable direction/subspace -> low-rank delta -> GGUF-compatible adapter -> canonical llama-server -> frozen behavior/preservation/resource A/B`

Preserve the canonical quantized GGUF as base. Do not require a resident BF16/FP16 30B copy if a tensor-streamed/adapter route can avoid it.

Start cheap:
- streaming residual mean;
- mean/projected mean direction;
- attention output projection first;
- rank 1 first;
- small bounded strength/layer sweep;
- only escalate to MoE-specific or multi-direction methods when measured evidence supports it.

Do not begin with broad Optuna/TPE search.

### WP3 execution

Pi may:
- inspect current upstream method repos/docs and freeze exact reference commits;
- create project-local temporary environments;
- minimally instrument an isolated llama.cpp/runtime analysis path if needed for residual extraction;
- inspect/dequantize only selected GGUF tensors needed to construct a low-rank delta;
- generate PEFT-like or direct GGUF-compatible LoRA/adapter artifacts;
- test server loading with adapter;
- run bounded frozen behavioral/capability/resource evaluations;
- revert failed candidates and continue through the method ladder.

Pi must preserve:
- base S32 server/runtime rollback;
- WP2 Context Intelligence rollback;
- base model hash and artifact.

### WP3 promotion

`LOOM_BEHAVIORAL_TRANSFORM_WP3_GO` requires:
- actual adapter/model-level transform;
- exact provenance/hashes;
- runtime-loadable transformed profile;
- material improvement on frozen target-behavior evaluation, target >=50% relative reduction when baseline rate supports that statistic;
- no material broken/degenerate-output increase;
- capability non-inferior within frozen tolerance;
- target >=90% of canonical S32 decode unless a smaller loss is justified by a substantially better behavior/capability Pareto result;
- safe RAM/swap;
- real Pi request through transformed profile;
- successful disable/rollback;
- durable evidence.

`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO` = bounded valid methods do not produce a useful Pareto improvement.

`LOOM_BEHAVIORAL_TRANSFORM_WP3_PHYSICAL_BLOCKED` = actual transform cannot be produced/evaluated because of proven host/toolchain/representation constraints after the bounded method ladder is exhausted.

Do not return after routine candidate failures.

## WP4 — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Assemble the best validated WP1-WP3 outputs and run end-to-end final acceptance.

## Current state

WP1: GO and fully persisted.
WP2: GO and persisted.
WP3: authorized and active.
WP4: not authorized.
