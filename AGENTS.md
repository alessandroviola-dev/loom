# LOOM — Pi Agent Protocol

Version: 3.84
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

S32 resources:
- peak RSS `3914.6 MiB`;
- peak sampled swap `1651.88 MiB`;
- minimum sampled free memory `10%`;
- no crash/OOM/corruption/critical pressure indication.

Final flags include:
`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`

Operational target:
- `scripts/loom-deep-server start|status|health|stop`;
- WebUI `http://127.0.0.1:18080/`;
- API base `http://127.0.0.1:18080/v1`.

WP1 result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

## WP2 — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`.

Canonical implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`

Contract:
`research/integration/loom-context-intelligence-wp2.md`

Canonical result:
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
- recovery verification `6/6`, `100%` SHA-verified;
- no accepted wrong result from stale/incorrect memory;
- real Pi local-model combined-path request passed;
- canonical provider/model label is now `loom-local/loom-deep-30b-s32`;
- S32 server remained healthy.

Rollback:
`LOOM_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32`

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

## Repository persistence audit — OPEN MECHANICAL ITEM

The WP2 commit is reviewed and persisted. However, the validated WP1 lifecycle script `scripts/loom-deep-server` is still present only as an untracked local file and is absent from GitHub.

Before WP3 begins, persist **only** the exact validated `scripts/loom-deep-server` file through an explicitly authorized bounded commit. Do not sweep in the many unrelated/historical untracked scripts.

`config/loom-deep-server.env` is already persisted by the WP2 commit.

## Later macro packages

### WP3 — Behavioral Transform — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Technical search priority:
1. Abliterix-derived MoE-aware methodology adapted to LOOM;
2. Heretic;
3. Senbonzakura-style multi-direction methods;
4. clean LOOM-native equivalent when upstream tooling is incompatible.

Select by fit to GGUF/llama.cpp/Apple Silicon. Prefer a small reversible/runtime-loadable adapter when technically valid. Prompt-only behavior does not satisfy WP3.

### WP4 — Final Integration + Acceptance — PLANNED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Assemble the best validated outputs from WP1-WP3 and run end-to-end acceptance.

## Current state

WP1: GO.
WP2: GO and persisted.
Current action: persist the single missing validated WP1 lifecycle script. Do not begin WP3 yet.