# LOOM — Pi Agent Protocol

Version: 3.83
Mode: `ACCELERATED_MACRO_WORKPACKAGES / EVIDENCE_GATED`

Pi reads this file as persistent context. User-facing micro-checkpoints are retired for the current push.

## Roles / synchronization

Pi: local inspection/execution, implementation, bounded experimentation, local integration, durable `results-local/` evidence, autonomous continuation through internal gates inside an authorized macro work package.

ChatGPT: scientific direction, macro-package definition/review, canonical Git/GitHub persistence.

GitHub is canonical. Active clone:
`<repository-root>`.

Default rule: Pi must not commit/push/PR.

Narrow exception: at a completed macro-work-package boundary, ChatGPT may explicitly authorize one bounded persistence commit/push containing only reviewed package implementation/result/docs. This exception never includes `.loom/`, `results-local/`, personal/home-directory config, secrets, caches, model artifacts, generated databases, or unrelated working-tree changes. Pi must inspect and report the exact included file list before committing and must stop if unrelated or ambiguous changes cannot be separated safely.

## Operating rule

Inside an authorized macro work package:
- do not return after routine internal GO/NO_GO results;
- record failed experiments;
- revert regressions;
- continue to the next justified action;
- preserve frozen scientific gates;
- keep one known-good runnable baseline.

Return only when the macro deliverable is substantially complete or a genuine blocker requires user action, credentials, destructive/security-sensitive host changes, unavailable hardware/storage, or a project-direction choice not resolvable from existing goals/evidence.

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
10. Pi Git persistence is allowed only under the narrow explicit macro-boundary exception above.

## Canonical DEEP — WP1 validated

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Canonical serving binary:
`llama-server`
SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Canonical runtime profile: **S32**.
Rollback profile: S24.

Matched deterministic S24/S32 3x96-token A/B:
- S24 median decode `4.382 tok/s`, E2E `29.185 s`;
- S32 median decode `5.596 tok/s`, E2E `23.849 s`;
- S32/S24 decode `1.2768x`;
- S32/S24 E2E `0.8172`;
- byte-identical outputs.

S32 resource evidence:
- peak RSS `3914.6 MiB`;
- peak sampled swap `1651.88 MiB`;
- minimum sampled free memory `10%`;
- no crash/OOM/corruption/critical pressure indication.

Final S32 flags include:
`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`

Operational path:
- start: `scripts/loom-deep-server start`;
- status: `scripts/loom-deep-server status`;
- health: `scripts/loom-deep-server health`;
- stop: `scripts/loom-deep-server stop`;
- WebUI: `http://127.0.0.1:18080/`;
- API base: `http://127.0.0.1:18080/v1`.

Serving-path prompt/KV reuse is directly validated under bounded `--cache-ram 512`.

## WP1 — COMPLETE / GO

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Canonical result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Pi is configured against the local server and completed a real offline model request.

## WP2 — COMPLETE LOCALLY / GO — PERSISTENCE PENDING

Classification reported by the completed local macro package:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`.

Authoritative contract:
`research/integration/loom-context-intelligence-wp2.md`

Local final report:
`research/integration/loom-context-intelligence-wp2-result.md`

Local evidence:
`results-local/context-intelligence-wp2/20260830T133259Z/`

Reported validated outcome:
- deterministic Caveman packing/recovery implemented;
- Cavemem SQLite/FTS5 project memory implemented;
- Pi integration through `.pi/extensions/loom-context.ts` `before_provider_request` hook;
- no model-visible tools or extra LLMs;
- provider/model label safely renamed to `loom-local/loom-deep-30b-s32`;
- A/B/C all `6/7` objective successes; shared JSON-cap miss baseline-equivalent;
- combined heavy-context median provider-input reduction `23.24%`;
- no-op overhead `0%`;
- exact recovery `6/6`, SHA-verified;
- real Pi combined-path task passed;
- disable/rollback control passed;
- canonical S32 server remains healthy.

Permanent WP2 mechanisms:
- Caveman-derived deterministic context compression/packing/recovery;
- Cavemem-derived progressive local project memory/retrieval.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

WP2 implementation/result files are currently local and must be persisted through the explicit macro-boundary Git exception before WP3 begins. Do not begin WP3 until persistence and ChatGPT canonical review are complete.

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

WP1 is complete and canonical. WP2 is scientifically complete locally with GO but Git persistence is pending. Do not begin WP3 until WP2 files are safely persisted and reviewed.