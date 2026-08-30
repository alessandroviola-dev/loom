# LOOM — Pi Agent Protocol

Version: 3.82
Mode: `ACCELERATED_MACRO_WORKPACKAGES / EVIDENCE_GATED`

Pi reads this file as persistent context. User-facing micro-checkpoints are retired for the current push.

## Roles / synchronization

Pi: local inspection/execution, implementation, bounded experimentation, local integration, durable `results-local/` evidence, autonomous continuation through internal gates inside an authorized macro work package.

ChatGPT: scientific direction, macro-package definition/review, canonical Git/GitHub persistence.

GitHub is canonical. Active clone:
`<repository-root>`.

Pi must not commit/push/PR.

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
10. Pi does not commit/push.

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

Pi is already configured against the local server and completed a real offline model request.

Current provider/model label `loom-local/loom-deep-30b-s24` is stale naming only. WP2 is authorized to rename it safely to `loom-local/loom-deep-30b-s32` or preserve a compatibility alias after backing up config.

## Current checkpoint — WP2 Context Intelligence

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Status: **AUTHORIZED / ACTIVE**.

Authoritative contract:
`research/integration/loom-context-intelligence-wp2.md`

Permanent mechanisms only:
- **Caveman-derived deterministic context compression/packing/recovery**;
- **Cavemem-derived progressive local project memory/retrieval**.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

### WP2 architecture rules

Cavemem:
- project-scoped local memory;
- compact observations in SQLite/FTS5-first storage;
- cheap lexical/BM25 retrieval first;
- exact bodies/evidence only on demand;
- decisions/results/failures/constraints/checkpoints prioritized over raw transcript;
- privacy/redaction before durable write;
- no mandatory embeddings in v0.

Caveman:
- deterministic local scoring/selection under token budget;
- typed compression for real LOOM/Pi output classes;
- preserve exact machine-critical values;
- errors/warnings receive priority;
- selection by value, then restore chronology for presentation;
- every omitted exact item remains recoverable by stable local handle;
- small/no-op contexts must bypass compression when overhead would outweigh savings.

Integration:
- no extra LLM for compression/ranking/memory by default;
- no new monolithic agent framework;
- avoid large permanent model-facing tool schemas;
- prefer host-side retrieval/context preparation immediately before provider calls;
- preserve the WP1 S32 server/runtime and a disable/rollback path.

### WP2 benchmark

Final frozen comparison arms:
- A: current WP1 baseline;
- B: Caveman packer/compression only;
- C: Caveman + Cavemem progressive retrieval.

Required workload mix includes context-heavy logs/search/JSON/code/diffs, earlier-project-decision recovery, and small/already concise negative cases.

GO requires, among the full contract gates:
- non-inferior objective task success;
- exact recovery/provenance;
- safe project memory/privacy behavior;
- target >=20% median provider-input reduction on context-heavy cases;
- target <=5% provider-input overhead on small/no-op cases with no correctness regression;
- packing/retrieval cost small relative to saved prefill/E2E;
- safe RAM/swap with canonical S32;
- no accepted wrong result caused by stale/incorrect memory;
- real Pi local-model task through the combined path;
- WP2 layer remains disableable for rollback.

Do not return after individual compressor/retrieval failures. Revert/disable net-negative subfeatures and continue according to the WP2 stopping rule.

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

WP1 is complete. WP2 is now the only authorized active macro package. Do not begin WP3.
