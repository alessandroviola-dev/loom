# LOOM — Pi Agent Protocol

Version: 3.87
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

## WP3 — COMPLETE LOCALLY / VALID NO_GO

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Reported classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Contract:
`research/integration/loom-behavioral-transform-wp3.md`

Local result:
`research/integration/loom-behavioral-transform-wp3-result.md`

Local evidence:
`results-local/behavioral-transform-wp3/20260830T144523Z/`

Valid bounded outcome:
- real GGUF LoRA candidates built and loaded through canonical `llama-server`;
- rank-1 directional route tested;
- MoE-router route tested;
- rank-4 subspace/multi-direction route tested;
- original frozen held-out refusal remained `6/6` for all candidates;
- target-behavior reduction `0%`;
- no WP3 adapter promoted;
- base S32 + WP2 restored and rollback-tested.

Interpretation:
WP3 falsified those three bounded adapter families. It did **not** prove the Qwen3-30B-A3B architecture cannot be behaviorally unlocked.

Do not alter the original WP3 frozen evaluation after the result. R2 must retain direct comparability to it.

## Current checkpoint — WP3-R2 Behavioral Unlock

Checkpoint:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2`

Status: **AUTHORIZED / ACTIVE**.

Authoritative contract:
`research/integration/loom-behavioral-unlock-wp3-r2.md`

User direction:
continue research toward an actually behaviorally unlocked local model rather than moving to WP4 with the WP3 NO_GO state.

### R2 materially different routes

1. **Exact-base external abliterated replacement candidate**
   - upstream behavioral derivative: `huihui-ai/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated`;
   - declared base: `Qwen/Qwen3-30B-A3B-Instruct-2507`;
   - GGUF quant source: `mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF`;
   - first candidate: `Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`, published around 13.3 GB, architecture `qwen3moe`.

2. **Native llama.cpp activation/control-vector steering**
   - use `cvector-generator` on GGUF;
   - runtime supports `--control-vector`, `--control-vector-scaled`, and `--control-vector-layer-range`;
   - this changes activations during inference and is materially different from the failed WP3 LoRA weight edits.

3. **Evidence-backed external Qwen3-A3B derivatives** only if A/B fail, with exact local verification before any promotion.

4. **External-compute escalation** only after local routes are exhausted and only after returning to user with a specific justified plan; do not purchase/require credentials autonomously.

### R2 invariants

- preserve original canonical base GGUF/hash;
- preserve S32 and WP2 rollback;
- do not trust third-party `abliterated` labels without local frozen evaluation;
- original WP3 held-out behavior set remains unchanged and directly reused;
- candidate may add capability/drift controls, but may not rewrite the old behavior gate;
- no prompt-only success claim;
- no public exposure;
- do not start WP4.

### R2 GO target

`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO` requires:
- actual model-level or activation-level intervention;
- >=50% relative reduction against the original frozen `6/6` behavior baseline, preferably <=1/6 for a strong candidate;
- practical capability non-inferior on frozen controls;
- exact provenance/hashes;
- stable local serving with throughput/RAM/swap recorded;
- localhost API and one real Pi request through WP2 where applicable;
- clean rollback to canonical S32 + WP2.

Do not stop after a routine candidate failure. Follow the R2 contract through the replacement/control-vector ladder.

## WP4 — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

WP4 remains blocked until WP3-R2 completes or returns a genuine external-compute/user-action blocker.

## Current state

WP1: GO and fully persisted.
WP2: GO and persisted.
WP3: valid NO_GO for three adapter families.
WP3-R2: authorized and active with materially different routes.
WP4: not authorized.
