# LOOM — Pi Agent Protocol

Version: 3.89
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
- fix or revert regressions;
- continue to the next justified action;
- preserve frozen scientific gates;
- keep one known-good runnable baseline.

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

## WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

Canonical FAST model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Pinned source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Canonical `llama-server` SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Runtime: S32. Rollback: S24.

Validated matched S24/S32:
- S24 median decode `4.382 tok/s`, E2E `29.185 s`;
- S32 median decode `5.596 tok/s`, E2E `23.849 s`;
- byte-identical outputs.

Current compatibility lifecycle:
`scripts/loom-deep-server start|status|health|stop`.

Lifecycle persistence commit:
`75e210f4d46cb8b7955e46763e329f28f37b699e`.

## WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`.

Implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`.

Canonical layer:
- Caveman-derived deterministic host-side packing/compression/recovery;
- Cavemem-derived SQLite/FTS5 project memory;
- Pi `before_provider_request` integration for `loom-local`;
- no extra LLM, embedding requirement, daemon or model-visible tool schema;
- heavy-context provider-input reduction `23.24%` median;
- no-op overhead `0%`;
- exact recovery `6/6`, SHA-verified.

Rollback:
`LOOM_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32`

Do not add LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

## WP3 — Behavioral Transform — COMPLETE / VALID NO_GO

Classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA candidates were built and served but all retained the original frozen held-out refusal result at `6/6`. Those three adapter families remain rejected. This did not establish architecture-level impossibility.

The local historical result `research/integration/loom-behavioral-transform-wp3-result.md` may be archived with the eventual WP4 persistence package; do not sweep in unrelated historical scripts.

## WP3-R2 — Behavioral Unlock — COMPLETE / GO / PERSISTED

Classification:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO`.

Persistence commit:
`1252fcfad73878981a1aa1844a484949a12d5ff4`.

Selected UNLOCKED model:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

Source:
`mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF`

Local SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Validated outcome:
- frozen explicit refusals `6/6 -> 0/6`;
- benign capability `8/8 -> 8/8`;
- no increased frozen degeneration;
- loopback API/WebUI passed;
- real Pi + WP2 request passed;
- clean rollback to FAST + WP2 passed.

Tradeoff:
- about `55%` of fresh FAST decode under R2 comparison;
- materially higher swap pressure;
- disposition/behavior drift remains explicit.

Product decision: retain both profiles. Do not silently replace FAST with UNLOCKED.

## Current checkpoint — WP4 Final Integration + Acceptance

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Status: **AUTHORIZED / ACTIVE**.

Authoritative contract:
`research/integration/loom-final-acceptance-wp4.md`

### Final product target

Two selectable DEEP profiles:

1. `loom-deep-30b-s32` — FAST/default;
2. `loom-deep-30b-unlocked` — behaviorally unlocked, slower/more resource-intensive.

Only one 30B profile should be resident at a time on this 8 GiB host.

Preferred operator UX:

```text
scripts/loom-deep use fast
scripts/loom-deep use unlocked
scripts/loom-deep start
scripts/loom-deep stop
scripts/loom-deep status
scripts/loom-deep health
scripts/loom-deep current
```

Equivalent compact UX is acceptable if clearer and fully documented.

Normal switching should use one stable loopback serving endpoint where practical, preferably `127.0.0.1:18080`, so Pi/WP2/WebUI do not need manual endpoint rewiring.

### Stable local model artifacts

Final product operation must not depend on timestamped experimental paths.

Use ignored repository-local `models/` stable paths. Do not duplicate multi-GB data just to create aliases. Prefer safe verified hard-links on the same filesystem, otherwise move/rename; verify SHA256 before and after and preserve a good copy until validation succeeds.

Both GGUFs remain local and excluded from Git.

### WP4 acceptance

WP4 must verify end-to-end:
- stable model paths/hashes;
- FAST default;
- FAST -> UNLOCKED -> FAST switching through final UX;
- no intentional concurrent FAST+UNLOCKED 30B residency;
- loopback API/WebUI for both;
- real Pi + WP2 request for both;
- final UNLOCKED recheck against unchanged frozen six held-out + eight benign cases;
- FAST performance health;
- UNLOCKED decode/prefill/E2E/RSS/swap/memory-pressure evidence;
- prompt/KV cache compatibility;
- Context Intelligence disable rollback;
- clean final rollback to FAST + WP2;
- durable operator documentation `docs/LOOM_OPERATIONS.md`;
- final result `research/integration/loom-final-acceptance-wp4-result.md`;
- evidence under `results-local/final-acceptance-wp4/<timestamp>/`.

Pi may update local `~/.pi/agent/models.json` with backup as needed so both labels are usable without manual edits. Never commit home configuration or secrets.

Do not redownload a verified local 13 GB model unnecessarily.

Do not commit/push during WP4 execution. Return one final bounded report for review.

## Current state

WP1: GO / persisted.
WP2: GO / persisted.
WP3: valid NO_GO for three adapter families.
WP3-R2: GO / persisted.
WP4: authorized and active.
