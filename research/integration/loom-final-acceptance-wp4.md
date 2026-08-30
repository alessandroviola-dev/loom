# LOOM Final Integration + Acceptance — WP4

Date: 2026-08-30
Checkpoint: `LOOM_FINAL_ACCEPTANCE_WP4`
Status: AUTHORIZED

## Objective

Turn the validated LOOM research outputs into one final practical local product with two selectable DEEP profiles:

1. `fast` -> canonical `loom-deep-30b-s32`;
2. `unlocked` -> validated `loom-deep-30b-unlocked` from WP3-R2 Candidate A.

WP4 is integration/productization, not a new model-research sweep. Preserve every prior frozen result and do not reopen rejected WP3 adapter families.

## Frozen inputs

### FAST

Model: `Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Runtime: S32 on pinned `llama-server`.

Server SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Historical matched median decode: `5.596 tok/s`.

### UNLOCKED

Model: `Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

WP3-R2 persistence commit:
`1252fcfad73878981a1aa1844a484949a12d5ff4`

Frozen R2 result:
- explicit refusal `6/6 -> 0/6`;
- benign capability `8/8 -> 8/8`;
- no increased frozen degeneration;
- real Pi + WP2 request passed;
- loopback API/WebUI passed;
- rollback to FAST passed.

R2 caveat: materially slower and higher-swap than FAST; disposition drift remains explicit.

### Context Intelligence

WP2 Caveman + Cavemem is canonical and should work for both profiles through the `loom-local` provider path. Do not introduce another memory/compression/orchestration system.

## Product architecture

Only one 30B profile should be resident at a time on the 8 GiB host.

Provide one stable operator-facing profile manager. Preferred UX:

```text
scripts/loom-deep use fast
scripts/loom-deep use unlocked
scripts/loom-deep start
scripts/loom-deep stop
scripts/loom-deep status
scripts/loom-deep health
scripts/loom-deep current
```

Equivalent compact naming is acceptable only if it is clearer and documented.

Profile switching must:
- stop the currently managed LOOM DEEP server cleanly before starting another profile;
- never intentionally keep FAST and UNLOCKED 30B servers resident simultaneously;
- keep serving loopback-only;
- use one stable product endpoint where practical, preferably `127.0.0.1:18080`, so Pi/WP2/WebUI do not require endpoint rewiring for normal switching;
- expose the correct model alias for the active profile;
- preserve clean rollback to FAST.

The existing `scripts/loom-deep-server` interface may remain as compatibility/rollback, but the final documented UX should be the unified profile manager.

## Stable local artifact layout

The final product must not depend on timestamped experimental paths as its normal interface.

Use repository-local ignored `models/` for stable local model artifact paths, for example:

```text
models/loom-deep-30b-fast.gguf
models/loom-deep-30b-unlocked.gguf
```

Do not duplicate multi-GB model data merely to create these stable names.

Preferred order:
1. hard-link on the same filesystem when safe and verifiably supported;
2. otherwise move/rename the already-downloaded local artifact;
3. symbolic link only when its target is itself a stable retained local artifact;
4. copy only if no non-duplicating safe method exists and there is ample disk space.

For any move/link operation:
- verify source SHA256 first;
- verify final stable-path SHA256 after;
- preserve the only good copy until final verification succeeds;
- never delete an unrelated file;
- record exact final paths and hashes.

The `models/` directory and `*.gguf` remain excluded from Git.

## Stable configuration

Replace timestamp-specific product config references with stable local artifact paths.

FAST and UNLOCKED should share the same pinned runtime and validated S32-style runtime parameters unless evidence during WP4 shows a profile-specific setting is required for stability.

Keep FAST as the default profile.

UNLOCKED must remain explicitly selectable and must not silently replace FAST.

## Pi integration

Final Pi integration must expose both model labels under the local provider:

- `loom-local/loom-deep-30b-s32`;
- `loom-local/loom-deep-30b-unlocked`.

Normal profile switching should not require hand-editing Pi configuration each time.

Home-directory Pi configuration may be updated locally only as needed for final operation, with backup and no secrets committed.

WP2 Context Intelligence must be exercised with both profiles and remain independently disableable via its existing rollback.

## WebUI/API

For each profile, verify:
- `/health`;
- `/v1/models`;
- one OpenAI-compatible chat request;
- embedded WebUI HTML reachable on loopback;
- no public bind/interface exposure.

## Final acceptance sequence

Run a clean, deterministic end-to-end sequence from a stopped state.

Minimum sequence:

1. verify Git/provenance and both model hashes;
2. verify stable local model paths;
3. start/use FAST;
4. verify health/API/WebUI;
5. real Pi + WP2 request on FAST;
6. representative deterministic capability/performance/resource sample on FAST;
7. switch FAST -> UNLOCKED using only final product UX;
8. verify FAST process is no longer resident;
9. verify health/API/WebUI for UNLOCKED;
10. real Pi + WP2 request on UNLOCKED;
11. rerun the unchanged six frozen WP3 held-out behavior cases and eight benign capability cases, or the exact existing deterministic evaluator, to ensure final integrated UNLOCKED still reproduces the R2 behavior/capability result;
12. record deterministic matched/representative decode, prefill, E2E, RSS, swap and memory-pressure measurements for UNLOCKED;
13. switch UNLOCKED -> FAST through final product UX;
14. verify UNLOCKED process is no longer resident;
15. reverify FAST health/API and exact base hash;
16. verify Context Intelligence disable rollback;
17. leave the machine in the documented default final state: FAST + WP2, unless a safer clean stopped state is explicitly justified in the final report.

Do not run both 30B profiles concurrently merely for benchmarking.

## Performance/resource acceptance

FAST must remain within ordinary run-to-run tolerance of the validated S32 product; investigate any material unexplained regression before promotion.

UNLOCKED does not need to match FAST throughput because WP3-R2 already accepted the strong-behavior tradeoff, but WP4 must confirm it remains stable and practically runnable with its caveat visible.

Any OOM, crash, corrupted output, sustained critical memory pressure, or inability to switch back to FAST is a blocker until repaired/reverted.

## Behavior/capability acceptance

Do not modify the existing frozen behavior/capability benchmark after seeing outputs.

Final UNLOCKED integration should reproduce the selected R2 profile rather than silently substitute another artifact.

Required target:
- held-out explicit refusal remains at or near the validated `0/6`; any regression to more than `1/6` requires investigation and cannot be silently accepted;
- frozen benign capability remains `8/8` or within the already frozen tolerance with no critical capability regression;
- no material new degeneration.

Disposition/safety drift from the abliterated model must remain documented rather than reclassified as capability improvement.

## Prompt/KV cache

Confirm the final FAST serving path still has the validated prompt/KV reuse behavior under the canonical cache configuration. Confirm UNLOCKED serving is compatible with the same cache mechanism if used in the final profile. Do not invent a new caching layer in WP4.

## Documentation

Create a concise durable operator document, preferred path:
`docs/LOOM_OPERATIONS.md`

It should contain:
- what FAST and UNLOCKED are;
- exact simple commands to select/start/stop/status/health;
- Pi commands/model labels;
- WebUI/API endpoint;
- expected tradeoff: FAST performance vs UNLOCKED behavioral openness/resource cost;
- local model hashes;
- rollback instructions;
- note that model artifacts are local and not stored in Git.

Also produce:
`research/integration/loom-final-acceptance-wp4-result.md`

Archive local evidence under:
`results-local/final-acceptance-wp4/<timestamp>/`

## Archival closure

The still-local `research/integration/loom-behavioral-transform-wp3-result.md` may be included in the eventual bounded WP4 persistence package as historical negative research evidence. Do not sweep in the many unrelated historical untracked scripts.

## WP4 classifications

### `LOOM_FINAL_ACCEPTANCE_WP4_GO`

Requires all of:
- two stable selectable profiles;
- stable non-timestamp product model paths without unnecessary model duplication;
- FAST default and clean FAST <-> UNLOCKED switching;
- one 30B resident at a time;
- API/WebUI healthy for both;
- Pi + WP2 real request for both;
- UNLOCKED final frozen behavior/capability reproduction;
- FAST performance remains healthy;
- UNLOCKED performance/resources recorded and practically stable;
- prompt/KV cache path remains valid;
- exact hashes/provenance;
- clean rollback to FAST + WP2;
- durable operations documentation and result/evidence.

### `LOOM_FINAL_ACCEPTANCE_WP4_NO_GO`

Use only if integration defects remain after bounded corrective iterations and prevent a trustworthy two-profile product.

### `LOOM_FINAL_ACCEPTANCE_WP4_BLOCKED`

Use only for a genuine user-action/physical/storage/security/toolchain blocker that cannot be resolved safely inside the current authorization.

## Execution rules

- Work autonomously through routine integration defects; fix/retest/revert internally.
- Do not return after minor failures.
- Preserve known-good FAST throughout.
- Do not redownload a 13 GB model if the verified local artifact already exists.
- Do not perform destructive cleanup of unrelated historical files.
- Do not disable SIP or host security controls.
- Do not expose the server publicly.
- Do not purchase compute/services or require new credentials.
- Do not commit/push during WP4 execution. Return one bounded final report; persistence happens after review.
