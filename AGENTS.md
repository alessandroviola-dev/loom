# LOOM — Pi Agent Protocol

Version: 3.94
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
10. never destructively mutate stable production GGUFs;
11. Pi Git persistence only under the explicit bounded exception above.

## Finished LOOM product — FINAL / GO / PERSISTED

Base product persistence commit:
`98949e77863c93a7d9dba266204a911ab85db09c`.

Latest UNLOCKED performance/product persistence commit:
`07223f99e75a44f559270af976ab2d8b52b5edb4`.

Operator UX:

```text
scripts/loom-deep use unlocked
scripts/loom-deep start|stop|status|health|current
```

The locally runnable UOPT-002 UNLOCKED profile serves loopback only:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

### FAST — archived and unavailable locally

The verified FAST GGUF was archived at:
`<external-archive>/archived-models/loom-deep-30b-fast.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Historical validated S32 median decode `5.596 tok/s`; WP4 operational snapshot `6.209 tok/s`. It is not selectable or a local rollback profile. The pinned `.loom/runtime/loom-llama-server` remains for UOPT-001 source rollback.

### UNLOCKED — UOPT-002 promoted profile

Alias/Pi label:
`loom-deep-30b-unlocked` / `loom-local/loom-deep-30b-unlocked`.

Source/rollback GGUF:
`models/loom-deep-30b-unlocked.gguf`

Source GGUF SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Promoted lossless expert-major sidecar:
`models/unlocked-expert-major-v1.bin`

Sidecar SHA256:
`4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`

Sidecar size:
`12,457,082,880` bytes.

Promoted isolated runtime:
`.loom/runtime/loom-uopt002/llama-server`

Runtime SHA256:
`088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`

Committed runtime patch:
`patches/loom-uopt002-expert-major-sidecar.patch`

Patch SHA256:
`3aac3cf3043b11d5f78a7e25dc5b4edce7bdb9e1f8907cec1ce64a7d2132b775`.

UOPT-002 uses S32 / CPU-MoE / no-mmap / `-ub 4`. The original UOPT-001 source rollback remains S32 / CPU-MoE / no-mmap / `-ub 2` and is unchanged.

Final promoted matched confirmation:
- fresh decode median `6.903 tok/s`;
- validated candidate median `7.359 tok/s`;
- 1,155-token cold TTFT `162.726 s` final promoted confirmation; validated candidate `156.949 s`;
- source-vs-sidecar deterministic A/B exact at identical settings.

Frozen validated result remains:
- explicit refusals `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`.

The expert-major transform is lossless and does not change routed top-k, router behavior or model math. Its behavioral/disposition drift remains the existing UNLOCKED caveat; openness is not a safety improvement.

### Runtime / Context Intelligence

Pinned UOPT-001 source rollback runtime:
`.loom/runtime/loom-llama-server`

SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Pinned source lineage:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Historical WP2 Caveman/Cavemem provenance remains available through `scripts/loom-context`. Its retired project-local Pi bridge has been superseded by the global Pi2 Context Intelligence implementation, which serves the local UNLOCKED profile without a LOOM-specific extension. The frozen WP2 result remains: heavy-context provider-input reduction `23.24%` median; no-op overhead `0%`; exact recovery `6/6`.

Global Pi2 Context Intelligence rollback:
`PI2_CONTEXT_INTELLIGENCE=0`.

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

Retained rollback change:
- FAST remains `-ub 1`;
- source UNLOCKED rollback uses `-ub 2`.

Matched retained UOPT-001 metrics:
- fresh short decode `2.579 -> 3.161 tok/s`;
- ~1,150-token cold TTFT `433.558 -> 393.983 s`;
- ~1,150-token warm TTFT `0.195 -> 0.190 s`.

Frozen `0/6`, `0/6`, `8/8`, API/WebUI/Pi+WP2/cache/loopback/FAST rollback all passed.

## UOPT-002 — COMPLETE / GO / PERSISTED

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_002`

Persistence commit:
`07223f99e75a44f559270af976ab2d8b52b5edb4`.

Contract:
`research/integration/loom-unlocked-speed-optimization-002.md`

Result:
`research/integration/loom-unlocked-speed-optimization-002-result.md`

Outcome:
- expert-granular telemetry isolated routed-expert paging as the cold-prefill bottleneck;
- non-destructive lossless expert-major sidecar reduced three source-GGUF reads per expert miss to one `preadv` path;
- full-GO decode gate >= `5.0 tok/s` passed;
- full-GO 1,155-token cold TTFT <= `184 s` passed;
- frozen behavior/capability and integration gates passed;
- source GGUF and FAST hashes unchanged;
- sidecar/runtime remain local and outside Git;
- no `external archive` runtime dependency;
- final machine state after acceptance: FAST + WP2 healthy on `127.0.0.1:18080`.

## Current state

No research macro is currently authorized after UOPT-002 closure. Treat the promoted UOPT-002 UNLOCKED path as the sole locally runnable product profile. The UOPT-001 source UNLOCKED runtime remains the local rollback baseline; FAST is externally archived and unavailable locally.

Do not begin a new optimization branch without a new explicit macro contract.
