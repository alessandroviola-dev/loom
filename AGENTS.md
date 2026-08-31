# LOOM — Pi Agent Protocol

Version: 3.92
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

Narrow exception: at a completed macro-work-package boundary, ChatGPT may explicitly authorize one bounded persistence commit/push containing only reviewed package implementation/result/docs. Never include `.loom/`, `results-local/`, home-directory config, secrets, caches, model artifacts, generated databases, external repo checkouts, or unrelated working-tree changes.

## Operating rule

Inside an authorized macro work package:
- do not return after routine GO/NO_GO experiments;
- record failed experiments;
- fix/revert regressions;
- continue to the next justified action;
- preserve frozen scientific gates;
- keep known-good FAST and UNLOCKED rollback baselines.

## Core rules

1. evidence over narrative;
2. exact provenance for model/runtime/derived artifacts;
3. no silent gate relaxation or false promotion;
4. deterministic tests before expensive runs where practical;
5. matched bounded A/B comparisons for performance claims;
6. no public internet exposure by default;
7. do not disable SIP/change host security settings;
8. do not delete unrelated user data;
9. project-local dependencies/environments are allowed when required and recorded;
10. Pi Git persistence only under the explicit bounded exception above.

## Finished LOOM product — FINAL / GO / PERSISTED

Final product persistence commit:
`98949e77863c93a7d9dba266204a911ab85db09c`.

Operator UX:

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Both profiles serve on loopback only:
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

Historical validated S32 median decode: `5.596 tok/s`; WP4 operational snapshot: `6.209 tok/s`.

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

WP4 operational snapshot:
- decode `2.963 tok/s`;
- prefill `1.673 tok/s`;
- RSS about `4.13->4.16 GiB`;
- swap `1667->1708 MiB`;
- free-memory signal `8->9%`.

WP4 also measured a severe cold-prefix latency signal on the `1,149`-token cache test: UNLOCKED cold prompt evaluation `~373.774 s` versus FAST `~184.269 s`; after prefix reuse UNLOCKED reuse E2E fell to `~0.242 s`. Therefore cold prompt/TTFT latency is a real product bottleneck, not merely subjective perception.

Its behavioral/disposition drift remains explicit; openness is not a safety improvement.

### Runtime / Context Intelligence

Pinned final runtime link:
`.loom/runtime/loom-llama-server`

SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Pinned source lineage:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Current final flags include:
`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`.

WP2 Caveman deterministic packing/recovery + Cavemem SQLite/FTS5 project memory remains enabled for both profiles. Heavy-context provider-input reduction `23.24%` median; no-op overhead `0%`; exact recovery `6/6`.

Context Intelligence rollback:
`LOOM_CONTEXT_INTELLIGENCE=0`.

WP4 verified FAST -> UNLOCKED -> FAST switching, WebUI/API/Pi+WP2, cache reuse, frozen UNLOCKED reproduction and final FAST rollback.

## Historical research state

WP1 Runtime/Product Serving: GO / persisted.

WP2 Context Intelligence: GO / persisted.

WP3 low-rank behavioral transform: valid NO_GO for rank-1 directional, MoE-router and rank-4 subspace families.

WP3-R2 full-model behavioral unlock: GO / persisted.

WP4 Final Integration/Acceptance: GO / persisted in `98949e77863c93a7d9dba266204a911ab85db09c`.

## Current authorized macro — UOPT-001

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_001`

Contract:
`research/integration/loom-unlocked-speed-optimization-001.md`

Objective:
maximize **interactive UNLOCKED performance** on this Apple M1 8 GiB host without losing its frozen behavioral/capability result or finished LOOM interfaces.

Co-primary promotion targets:
1. **>= 5.0 tok/s matched fresh decode median**;
2. **materially reduce initial response latency / TTFT**, explicitly separating service startup, cold prompt/prefill, first-token latency, warm/cache-reuse latency and steady-state decode.

A candidate that reaches `5.0 tok/s` but leaves avoidable multi-minute first-token waits is not a full GO.

Latency guidance:
- no short-prompt TTFT regression;
- materially improve medium/long cold TTFT versus measured UOPT baseline;
- for the existing ~`1,149`-token cold path, at minimum approach/beat current FAST cold prompt latency (~`184 s`) if physically achievable;
- stretch target: below `120 s` for that long cold path while preserving all gates;
- lower is better; continue through justified optimization rather than stopping at the first threshold.

Stretch decode target:
exceed FAST historical `5.596 tok/s` if possible without gate regression.

Optimization ladder:
1. exact-current-model runtime/slot/residency/mmap/placement frontier, measuring startup + TTFT + prefill + decode independently;
2. newer evidence-backed llama.cpp / bounded MoE residency implementations, including audit of recent `oversized-moe-runtime`-style approaches and their cold-prefill implications;
3. only if needed, a small exact-lineage quantization frontier of the validated Huihui derivative;
4. combine only independently validated winners.

External benchmark claims are hypotheses only. Pin exact upstream revisions and reproduce locally before promotion.

Promotion must preserve unchanged UNLOCKED frozen gates:
- explicit refusal `0/6`;
- benign `8/8`;
- held-out degeneration `0/6`;
- API/WebUI/Pi+WP2/cache;
- loopback-only serving;
- exact provenance/hashes;
- clean rollback to current FAST and current validated UNLOCKED.

Pi does not commit/push during UOPT-001 execution. Evidence goes under:
`results-local/unlocked-speed-uopt-001/<timestamp>/`.

Return only at UOPT macro completion (`GO`, justified `PARTIAL_GO`) or a genuine user-action blocker defined by the contract.
