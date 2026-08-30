# LOOM — Pi Agent Protocol

Version: 3.86
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

## WP3 — COMPLETE LOCALLY / NO_GO — PERSISTENCE PENDING

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Reported classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Authoritative contract:
`research/integration/loom-behavioral-transform-wp3.md`

Local result:
`research/integration/loom-behavioral-transform-wp3-result.md`

Local evidence:
`results-local/behavioral-transform-wp3/20260830T144523Z/`

Reported bounded outcome:
- actual GGUF LoRA adapters were produced and loaded through the canonical `llama-server` path;
- rank-1 directional route tested;
- MoE-router route tested;
- rank-4 subspace/multi-direction route tested;
- frozen held-out refusal result remained `6/6` for all tested transformed candidates;
- relative target-behavior reduction therefore remained `0%`, failing the frozen behavior promotion gate;
- no transform is promoted;
- base S32 + WP2 was restored, hash-verified, health-checked, and rollback-tested on `127.0.0.1:18080`;
- WP4 was not started.

Interpretation:
WP3 is a valid scientific NO_GO, not a physical/toolchain block. The project demonstrated that real runtime-loadable transforms can be created on this host, but the bounded validated method families did not produce a useful behavioral improvement under the frozen evaluation.

Do not weaken or replace the frozen WP3 behavior gate after seeing this result. Do not relabel prompt-only behavior as a model transform. Do not promote any WP3 adapter.

Before WP4 begins, persist only the bounded reusable WP3 source/spec/result files through the explicit macro-boundary exception. Exclude generated adapter/model artifacts and `results-local/` evidence from Git.

## WP4 — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

WP4 must assemble the best validated product state:
- WP1 S32 runtime/server/WebUI/API;
- validated serving-path prompt/KV reuse;
- WP2 Caveman + Cavemem;
- **no behavioral adapter enabled**, because WP3 completed valid NO_GO;
- exact WP3 NO_GO retained as research evidence rather than silently retried or relabeled.

WP4 acceptance may still be GO when WP3 is valid NO_GO, provided final product operation/capability/resource/provenance gates pass and the absence of a promoted behavioral transform is explicit.

## Current state

WP1: GO and fully persisted.
WP2: GO and persisted.
WP3: scientifically complete locally with NO_GO; bounded Git persistence pending.
WP4: not authorized.
