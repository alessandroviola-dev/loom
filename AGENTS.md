# LOOM — Pi Agent Protocol

Version: 3.96
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

The locally runnable UOPT-003 UNLOCKED S40 profile serves loopback only:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

### FAST — archived and unavailable locally

The verified FAST GGUF was archived at:
`<external-archive>/archived-models/loom-deep-30b-fast.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Historical validated S32 median decode `5.596 tok/s`; WP4 operational snapshot `6.209 tok/s`. It is not selectable or a local rollback profile. The pinned `.loom/runtime/loom-llama-server` remains for UOPT-001 source rollback.

### UNLOCKED — UOPT-003 promoted S40 profile

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

UOPT-003 promotes S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`, retaining the UOPT-002 sidecar, patched runtime, LRU and asynchronous resolver unchanged. `scripts/loom-deep use unlocked-s32` retains the UOPT-002 S32 configuration as a managed same-runtime/sidecar rollback. The original UOPT-001 source rollback remains S32 / CPU-MoE / no-mmap / `-ub 2` and is unchanged.

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

`LOOM_CONTEXT_WEBUI_001` reuses that canonical global Pi2 core in a loopback-only gateway: public WebUI/API remains `127.0.0.1:18080`, while the UOPT-002 backend is private on `127.0.0.1:18081`. Set `LOOM_CONTEXT_WEBUI_GATEWAY=0` for direct backend rollback or `LOOM_CONTEXT_WEBUI_CI=0` for gateway passthrough; neither path uses `external archive`.

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

## UOPT-003 — COMPLETE / GO / LOCAL PROMOTION PENDING PERSISTENCE

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_003`

Durable result:
`research/integration/loom-unlocked-speed-optimization-003-result.md`

Outcome:
- S40 is the promoted normal `unlocked` residency; S32 is retained as managed `unlocked-s32` rollback;
- matched decode `6.660 -> 7.557 tok/s` (+13.46%); 1,155-token cold TTFT `161.676 -> 102.242 s` (-36.76%); cold prefill `7.147 -> 11.306 tok/s`;
- hit rate `81.745% -> 89.831%`, misses/sidecar reads `90,229 -> 50,260`;
- frozen `0/6`, `0/6`, `8/8` and loopback/API/WebUI/Pi2 verification passed;
- S48 failed with Metal GPU timeout; experimental frequency-aware policy was not promoted;
- model/sidecar/runtime hashes unchanged; experimental build/runtime removed; evidence remains local under `results-local/unlocked-speed-uopt-003/20260901T130729Z/`.

## UOPT-004 — COMPLETE / NO_GO

Durable result:
`research/integration/loom-unlocked-speed-optimization-004-result.md`

Expert-only `Q2_K` from BF16 reduced expert footprint by `23.636%` and passed frozen gates, but failed functional quality (`3/4`) and arithmetic (`414` vs expected `410`). Temporary artifacts were removed. Production S40 is unchanged.

## UOPT-005 — COMPLETE / NO_GO

Durable result:
`research/integration/loom-unlocked-speed-optimization-005-result.md`

BF16 source verification (`13/13`), HF→BF16 GGUF validation, imatrix completion, and Candidate A expert `IQ3_XXS` construction completed. Storage isolation identified external archive as the initial smoke bottleneck: decode `0.69 -> 9.63 tok/s`, prefill `0.24 -> 6.31 tok/s`, and TTFT `148.277 -> 5.605 s`. Candidate A passed frozen refusal `0/6`, degeneration `0/6`, and benign capability `8/8`, but failed functional quality (`3/4`) and arithmetic (`400` vs required `410`). B.1 Q3 `40–47` returned `400`; B.2 Q3 `36–47` and B.3 Q3 `32–47` returned `414`. The layer frontier found 37 and 39 causal (36/38 noncausal); 11 losslessly validated tensor splices exhausted causal set `{up37, down37, down39}` (all nonempty subsets `414`, empty `400`) without reaching `410`. Expert-by-expert selection was not pursued: it would require a new format/runtime (estimated 1–3 days) with unproven benefit. Production S40 is unchanged.

## LOOM_CONTEXT_WEBUI_001 — COMPLETE / KEEP / LOCAL VALIDATION

The UOPT-002 backend is privately loopback-bound on `127.0.0.1:18081`; the lightweight public `127.0.0.1:18080` gateway imports the canonical global Pi2 Context Intelligence core. Matched eligible-tool-evidence A/B preserved the selected output, reduced model-visible prompt tokens `2,386 -> 319`, and measured `0.737 ms` median static-health passthrough overhead. Gateway and CI bypasses passed; result evidence is local at `results-local/loom-context-webui-001-result.md`. No global Pi2 modification was required. This implementation is pending reviewed persistence.

## Current state

Treat the promoted UOPT-003 S40 UNLOCKED path as the sole locally runnable product profile, with the WebUI Context Intelligence gateway enabled by default. `unlocked-s32` is the managed UOPT-002 same-runtime/sidecar rollback; the UOPT-001 source UNLOCKED runtime remains the deeper local rollback baseline; FAST is externally archived and unavailable locally. UOPT-005 is closed NO_GO; production S40 must remain unchanged.
