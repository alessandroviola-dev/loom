# LOOM — Pi Agent Protocol

Version: 3.88
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

## Canonical DEEP baseline — WP1 GO

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
- A/B/C objective success `6/7` each;
- combined heavy-context median provider-input reduction `23.24%`;
- no-op provider-input overhead `0%`;
- recovery `6/6`, `100%` SHA-verified;
- real Pi combined-path request passed;
- canonical provider/model label `loom-local/loom-deep-30b-s32`.

Rollback Context Intelligence:
`LOOM_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32`

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

## WP3 — COMPLETE / VALID NO_GO

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

The rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA families were actually constructed and served but left the original frozen refusal result at `6/6`. Those three bounded adapter families remain rejected. This NO_GO did not establish architectural impossibility.

## WP3-R2 — COMPLETE LOCALLY / GO — PERSISTENCE PENDING

Checkpoint:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2`

Classification:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO`.

Contract:
`research/integration/loom-behavioral-unlock-wp3-r2.md`

Local result:
`research/integration/loom-behavioral-unlock-wp3-r2-result.md`

Evidence:
`results-local/behavioral-unlock-wp3-r2/20260830T160845Z/`

### Selected Candidate A

Behavioral derivative:
`huihui-ai/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated`

GGUF source:
`mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF`

Selected quant:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

Local SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Validated R2 outcome:
- original frozen held-out explicit refusals improved from `6/6` baseline to `0/6` candidate, a `100%` relative reduction;
- frozen benign capability remained `8/8 -> 8/8`;
- no increased degeneration under the frozen evaluation;
- candidate served stably through loopback API and WebUI;
- one real Pi request through WP2 passed;
- exact model hash recorded;
- clean rollback to canonical S32 + WP2 passed and baseline is active again on port `18080`.

Important caveats:
- candidate fresh decode is roughly `55%` of the fresh canonical S32 baseline under the R2 comparison;
- swap pressure is materially higher;
- behavioral/disposition drift is explicitly retained in the R2 evidence and must not be hidden.

### Product interpretation

Do not replace canonical S32 silently.

The intended product structure is now two DEEP profiles:
- `loom-deep-30b-s32`: canonical fast/default profile;
- `loom-deep-30b-unlocked`: validated behavioral-unlock profile using Candidate A, selectable when behavioral openness is preferred over throughput/resource efficiency.

The unlocked GGUF remains a local model artifact and must not be committed to Git. Git should contain only provenance, hashes, small scripts/configuration, evaluation specifications and result documents.

## Current exact action

Persist the bounded WP3-R2 reproducibility/product-profile package under the macro-boundary exception, then review it before final product integration.

Include only small reusable R2 result/spec/source/config files required to reproduce or operate the selected unlocked profile. Exclude the downloaded ~13 GB GGUF, `results-local/`, caches, temporary environments, secrets, home-directory configuration and unrelated historical scripts.

## WP4 — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

WP4 should integrate both validated DEEP profiles, not discard either:
- fast/default S32 + WP2;
- behavioral-unlocked Candidate A + WP2.

Final acceptance must verify profile selection, clean rollback, API/WebUI/Pi, capability, performance, RAM/swap and exact provenance for both.

## Current state

WP1: GO and fully persisted.
WP2: GO and persisted.
WP3: valid NO_GO for three adapter families.
WP3-R2: GO locally; persistence pending.
WP4: not authorized until R2 persistence is reviewed.
