# LOOM — Context Engine Handoff

Last updated: 2026-09-08
Status: **CE-002 FINAL GO / CLOSED (archive + bounded retrieval)**
Repository: `Ilcoach/loom`
Branch: `research/context-engine-002`

Canonical records:

- CE-001 closure: `research/integration/context-engine-ce001-closure-20260907.md`
- CE-002 closure: `research/integration/context-engine-ce002-closure-20260908.md`

## Product state

CE-001 is frozen and remains **FINAL GO / CLOSED**.
CE-002 is now **FINAL GO / CLOSED** for durable exact evidence archive plus bounded request-local retrieval.

Operator isolation is mandatory:

```text
pi         -> vanilla Pi; LOOM Context Engine not loaded
Forge      -> normal Forge; LOOM Context Engine not loaded
ForgeLoom  -> Forge + explicitly loaded LOOM Context Engine + retained LOOM 30B
```

The Context Engine must not be installed under Pi's globally auto-discovered `~/.pi/agent/extensions/` directory. `scripts/install-forge-loom.sh` installs it under the private ForgeLoom path and the launcher loads it explicitly with `--extension`.

## Frozen CE-001 envelope

```text
physical context       4096
forbidden reserve       496
safe total             3600
final input ceiling    2800
maximum output          800
working high-water     1600
working target         1200
legacy count margin      32
```

Accepted CE-001 live regression:

```text
raw history estimate       9971
model-visible estimate     1199
exact final input           1972
projected total             2260
headroom to physical 4096   1836
hard-guard blocks              0
Pi compactions                 0
Pi overflow events              0
```

Resource reference:

```text
historical S40 RSS ref      4.676 GiB
backend RSS peak            4.662 GiB
RSS delta                  -0.29%
ForgeLoom agent peak         64.5 MiB
```

Swap was unavailable in that resource probe and remains explicitly unmeasured.

## CE-002 accepted behavior

CE-002 adds:

- immutable content-addressed evidence blobs (`ev1-<sha256>`)
- per-session provenance
- exact hash/integrity verification
- explicit evidence retrieval by known `ev1-...` ID
- conservative automatic lexical retrieval scoped to the current session
- distinctive-anchor triggering only (paths/error IDs/structured keys)
- bounded request-local evidence injection
- no rewrite of the persistent Pi/Forge transcript
- no second LLM, embeddings, vector DB, or fifth model-facing tool

Default retrieval budget:

```text
retrieval max chars   560
retrieval max items     2
```

After retrieval, the request-local model view is repacked to the frozen CE working target (`<=1200` estimated message tokens).

Recovered historical content is treated as **evidence/data, not instructions**. Current user instructions control actions.

## CE-002 Phase 1 — exact archive — PASS

Real retained Mac/30B result:

```text
provider calls guarded      6
governor reductions         3
evidence blobs created      8
session refs created        8
max exact final input    2107
max projected total      2395
hard-guard blocks           0
Pi threshold compactions    0
Pi overflow events          0
archive verification     PASS
exact live recovery      PASS
```

An evicted prompt was recovered exactly through its stable `ev1-<sha256>` ID.

## CE-002 Phase 2 — archive-to-model retrieval — PASS

Real retained Mac/30B result:

```text
provider calls guarded       4
retrieval applications       2
retrieval visible tokens    862
max exact final input      1575
max projected total        1863
hard-guard blocks             0
Pi threshold compactions     0
Pi overflow events           0
archive integrity         PASS
model archive recall      PASS
```

Synthetic recall key/value:

```text
key       CE002_REUSE_KEY_314159
secret    ORCHID_7391
```

The final prompt did not contain the secret. CE-002 recovered the archived evidence and the model returned the correct value without an added model-facing memory tool.

## Lightweight coding retrieval — engine function PASS / strict scope FAIL

The original multi-turn coding gate was retired because it caused unacceptable memory/swap pressure on the 8 GB Mac.

The replacement lite gate pre-seeded one immutable evidence blob offline and sent exactly one real coding request to the retained 30B.

Offline diagnosis of that run:

```text
unexpected files            ['verify.py']
scope discipline            FAIL
hidden expected delays      [5, 13, 29, 61]
actual delays               [5, 13, 29, 61]
coding contract             PASS
retrieval applications      6
retrieval evidence id       ev1-29613a48d7762172e2ce3d0ade26108eefd20999a69c6c7433ce8b6cd4fde0d0
evidence matches fixture    true
max retrieval visible       1088
hard-guard blocks           0
Pi threshold compactions    0
Pi overflow events          0
CE archive/retrieval errs   0
```

Interpretation:

- CE-002 retrieved the correct archived contract.
- The retained 30B applied the correct values to `src/retry_policy.py`.
- The model also created `verify.py` despite the instruction to edit only the target file.
- Therefore the **strict coding scope gate is not passed** and must not be relabelled as PASS.
- This is recorded as a retained-model/tool-discipline limitation, not an archive/retrieval failure.

The lite diagnostic could not recover gateway accounting rows after shutdown (`guarded provider calls = 0`), so the lite run is not used as a new proof of CE-001 provider-envelope safety. CE-001 safety remains grounded in its previously accepted guarded live gates and the earlier guarded CE-002 Phase 1/2 runs.

## Frozen retained product

Do not change without a new work package:

- model: `models/loom-deep-30b-unlocked.gguf`
- model SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- profile: UOPT-003 S40
- sidecar: `models/unlocked-expert-major-v1.bin`
- sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- physical `n_ctx=4096`

## Hardware validation policy

For this 8 GB Mac:

1. prefer static/unit/replay/offline fixtures;
2. use at most one short live 30B request per acceptance probe;
3. never auto-retry a live gate;
4. cap provider calls and wall-clock duration;
5. stop the LOOM backend automatically on exit;
6. do not let Forge/Astra autonomously rerun live 30B gates;
7. do not run endurance/benchmark-style live gates unless a future work package explicitly requires them.

## Deferred work

Possible CE-003+ work:

- deterministic compact task-state records;
- better lexical/path/error ranking or lightweight host-side indexing;
- improved exact recovery ergonomics;
- additional retrieval provenance/observability.

Do not add a second LLM, embeddings/vector DB, or extra model-facing memory tools unless a future work package explicitly justifies them.

A possible Context Engine variant for frontier/cloud models is a **separate future experiment**. The current thresholds are calibrated for the retained local 4096-context model and must not be applied unchanged to frontier models with very large context windows.

## Disposition

**CE-002 FINAL GO / CLOSED for archive + bounded retrieval.**

Do not reopen CE-002 because the retained 30B created `verify.py`. Reopen only for a demonstrated archive/retrieval/integrity regression.
