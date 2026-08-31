# LOOM — Pi Agent Protocol

Version: 3.93
Mode: `ACCELERATED_MACRO_WORKPACKAGES / EVIDENCE_GATED`

Pi reads this file as persistent context. User-facing micro-checkpoints are retired.

## Roles / synchronization

Pi: local inspection/execution, implementation, bounded experimentation, local integration, durable `results-local/` evidence, autonomous continuation through internal gates inside an authorized macro work package.

ChatGPT: scientific direction, macro-package definition/review, canonical Git/GitHub persistence.

GitHub is canonical. Active clone:
`<repository-root>`.

Current branch:
`research/unlocked-speed-001`.

Default rule: Pi must not commit/push/PR.

Narrow exception: at a completed macro-work-package boundary, ChatGPT may explicitly authorize one bounded persistence commit/push containing only reviewed package implementation/result/docs. Never include `.loom/`, `results-local/`, home-directory config, secrets, caches, model artifacts, generated databases, external repo checkouts/build artifacts, or unrelated working-tree changes.

## Operating rule

Inside an authorized macro work package:
- do not return after routine GO/NO_GO experiments;
- record failures and rejected candidates;
- fix/revert regressions;
- continue to the next justified action;
- preserve frozen scientific gates;
- keep known-good FAST and UNLOCKED rollback baselines.

## Core rules

1. evidence over narrative;
2. exact provenance for model/runtime/patch/derived artifacts;
3. no silent gate relaxation or false promotion;
4. deterministic tests before expensive runs where practical;
5. matched bounded A/B comparisons for performance claims;
6. no public internet exposure by default;
7. do not disable SIP/change host security settings;
8. do not delete unrelated user data;
9. project-local dependencies/environments are allowed when required and recorded;
10. never destructively mutate the hard-linked production GGUFs;
11. Pi Git persistence only under the explicit bounded exception above.

## Finished LOOM product — FINAL / GO / PERSISTED

Final product persistence commit:
`98949e77863c93a7d9dba266204a911ab85db09c`.

Operator UX:

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Both profiles serve loopback only:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

Only one 30B profile is resident at a time. FAST remains default.

### FAST

Alias/Pi label:
`loom-deep-30b-s32` / `loom-local/loom-deep-30b-s32`.

Model:
`models/loom-deep-30b-fast.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Historical validated S32 median decode `5.596 tok/s`; WP4 operational snapshot `6.209 tok/s`.

FAST retains `-ub 1`.

### UNLOCKED

Alias/Pi label:
`loom-deep-30b-unlocked` / `loom-local/loom-deep-30b-unlocked`.

Model:
`models/loom-deep-30b-unlocked.gguf`

Source model:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Frozen validated result:
- explicit refusals `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`.

Its behavioral/disposition drift remains explicit; openness is not a safety improvement.

### Runtime / Context Intelligence

Pinned final runtime link:
`.loom/runtime/loom-llama-server`

SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Pinned source lineage:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Base product flags include:
`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 --cache-ram 512`.

WP2 Caveman deterministic packing/recovery + Cavemem SQLite/FTS5 memory remains enabled for both profiles. Heavy-context provider-input reduction `23.24%` median; no-op overhead `0%`; exact recovery `6/6`.

Context Intelligence rollback:
`LOOM_CONTEXT_INTELLIGENCE=0`.

## Historical research state

WP1 Runtime/Product Serving: GO / persisted.

WP2 Context Intelligence: GO / persisted.

WP3 low-rank behavioral transform: valid NO_GO for rank-1 directional, MoE-router and rank-4 subspace families.

WP3-R2 full-model behavioral unlock: GO / persisted.

WP4 Final Integration/Acceptance: GO / persisted in `98949e77863c93a7d9dba266204a911ab85db09c`.

## UOPT-001 — COMPLETE / PARTIAL_GO / PERSISTED

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_001`

Persistence commit:
`93b5f44733d120a4e9c0f0b1fea6e58309f71ccd`.

Result:
`research/integration/loom-unlocked-speed-optimization-001-result.md`.

Retained product change:
- FAST remains `-ub 1`;
- UNLOCKED uses `-ub 2`.

Matched retained UOPT-001 metrics:
- fresh short decode `2.579 -> 3.161 tok/s` (product repeat; independent candidate repeat `3.046`);
- short TTFT `19.525 -> 15.283 s`;
- short prompt `1.706 -> 2.199 tok/s`;
- ~413-token cold TTFT `199.104 -> 184.700 s`;
- ~1,150-token cold TTFT `433.558 -> 393.983 s`;
- ~1,150-token warm TTFT `0.195 -> 0.190 s`.

Frozen `0/6`, `0/6`, `8/8`, API/WebUI/Pi+WP2/cache/loopback/FAST rollback all passed.

Rejected UOPT-001 directions include S24, S40 pressure, ub4/ub128, mmap (Metal timeout), no-CPU-MoE, thread forcing and Flash Attention. Current-runtime tuning did not approach 5 tok/s. Remaining bottleneck: expert paging / cold prefill.

Known-good UNLOCKED rollback baseline for all later work is now persisted UOPT-001 (`S32`, CPU-MoE, no-mmap, `-ub 2`).

## Current authorized macro — UOPT-002

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_002`

Contract:
`research/integration/loom-unlocked-speed-optimization-002.md`

Objective:
attack UNLOCKED expert paging / cold-prefill architecture while preserving exact behavior/capability and the finished product interfaces.

Co-primary full-GO targets:
1. matched fresh decode median **>= 5.0 tok/s**;
2. existing ~1,150-token cold TTFT **<= 184 s**; stretch **<120 s**.

A decode-only or TTFT-only win is not full GO.

Frozen gates remain:
- refusal `0/6`;
- held-out degeneration `0/6`;
- benign `8/8`;
- Qwen3 routed top-k semantics unchanged (no fewer-active-expert speed shortcut);
- loopback API/WebUI/Pi+WP2/cache;
- exact provenance/hashes;
- no crash/OOM/corruption;
- rollback to FAST and persisted UOPT-001 UNLOCKED.

Architectural ladder:
1. expert-granular I/O/paging attribution;
2. pinned bounded-expert-residency runtime audit/reproduction (`oversized-moe-runtime` / related page-aware approaches);
3. explicit router-driven sorted/merged expert prefetch;
4. quantify and mitigate GGUF page amplification without destructive/full-copy assumptions;
5. streamed expert cache/overlap with unchanged top-k;
6. exact-output speculative decode only as a justified fallback after paging/TTFT work.

External benchmark claims are hypotheses only. Pin exact revisions and reproduce locally.

Storage constraint: UOPT-001 observed only ~5 GiB free at that time. Re-measure. Do not create a second full 13.29 GB GGUF or mutate the hard-linked production model. If full relayout is storage-blocked, continue non-destructive architectural routes and return only if the whole macro truly requires user storage action.

Pi does not commit/push during UOPT-002. Evidence:
`results-local/unlocked-speed-uopt-002/<timestamp>/`.

Return only at UOPT-002 macro completion (`GO`, justified `PARTIAL_GO`) or a genuine contract-defined blocker.
