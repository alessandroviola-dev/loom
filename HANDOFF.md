# LOOM — Context Engine Handoff

Last updated: 2026-09-07
Status: **ACTIVE — CE-002 PHASE 1 ARCHIVE PASS / PHASE 2 BOUNDED RETRIEVAL LIVE GATE PENDING**
Repository: `Ilcoach/loom`
Branch: `research/context-engine-002`

CE-001 canonical closure: `research/integration/context-engine-ce001-closure-20260907.md`
CE-001 rollback/reference branch: `research/context-engine-001`

## Decision

CE-001 is frozen and remains **FINAL GO / CLOSED**. CE-002 is a separate change set layered on top of the accepted sliding-window governor.

Operator modes remain:

```text
pi         -> vanilla Pi
Forge      -> normal Forge
ForgeLoom  -> Forge + LOOM Context Engine + retained LOOM model
```

Plain `pi` and normal `Forge` must remain unchanged.

## Frozen CE-001 safety envelope

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

CE-002 may not weaken these limits.

Final accepted CE-001 live regression:

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

Resource gate:

```text
historical S40 RSS ref      4.676 GiB
backend RSS peak            4.662 GiB
RSS delta                  -0.29%
ForgeLoom agent peak         64.5 MiB
```

Swap was unavailable in that probe and remains explicitly unmeasured.

## CE-002 objective

CE-001 can remove old conversational/tool evidence from the model-visible request while retaining the full Pi/Forge session externally. CE-002 makes that removed evidence independently addressable and selectively reusable without increasing physical model context.

No second LLM, embeddings, vector DB, Forge fork, or fifth model-facing tool is introduced.

Target architecture:

```text
persistent Pi/Forge transcript
            |
            +--> CE-001 request-local governor --> bounded model view
            |
            `--> CE-002 evidence archive
                    |-- immutable original blobs
                    |-- stable ev1-/SHA-256 IDs
                    |-- per-session provenance
                    |-- integrity verification
                    `-- bounded request-local retrieval
```

## CE-002 Phase 1 — durable exact evidence archive — PASS

Module:

`src/loom-context-engine/evidence-archive.mjs`

Design:

1. Original messages no longer present verbatim after packing are detected with multiset semantics.
2. Originals are canonicalized deterministically and SHA-256 hashed.
3. Stable evidence ID:

```text
ev1-<64 lowercase SHA-256 hex chars>
```

4. Canonical blobs:

```text
evidence/blobs/<sha256>.json
```

5. Per-session provenance:

```text
evidence/sessions/<safe-session-id>/<sha256>.json
```

6. Blobs and refs are deduplicated.
7. Existing blobs are hash-verified before reuse.
8. Archive corruption is detected rather than silently returned.
9. Persistent Pi/Forge session is never rewritten.
10. Archive remains local-only under the Context Engine runtime root.

CLI:

```bash
node scripts/loom-context-evidence.mjs sessions
node scripts/loom-context-evidence.mjs search "query" [--session ID] [--limit N]
node scripts/loom-context-evidence.mjs show ev1-<sha256>
node scripts/loom-context-evidence.mjs verify
```

### Phase 1 live evidence — PASS

Real retained Mac/30B result on 2026-09-07:

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

Recovered first evicted prompt:

```text
evidence id  ev1-24ddb8a475aaf170180f83ff7fd23a2669ae8351b04c01f729c3b5af98dd0b9e
sha256       24ddb8a475aaf170180f83ff7fd23a2669ae8351b04c01f729c3b5af98dd0b9e
prompt chars 1205
```

This closes CE-002 Phase 1.

## CE-002 Phase 2 — bounded request-local retrieval — IMPLEMENTED / LIVE GATE PENDING

New module:

`src/loom-context-engine/evidence-retrieval.mjs`

Current retrieval policy is intentionally conservative.

### Explicit retrieval

If the current user request contains a valid `ev1-<sha256>` ID, CE-002 resolves that exact content-addressed blob. If the complete canonical message fits the retrieval character budget it is marked `exact`; otherwise only a bounded excerpt is injected and the immutable evidence ID remains available for exact CLI recovery.

### Automatic lexical retrieval

Automatic lookup is scoped to the **current Pi/Forge session only**. It does not search other sessions automatically.

The first lexical gate only uses structurally distinctive anchors such as:

```text
ERROR_8472
src/widget.ts
path/to/file.py:41
CE002_REUSE_KEY_314159
```

Generic prose does not trigger automatic retrieval. The actual search query is also reduced to those distinctive anchors so common words cannot dominate ranking.

Cross-session evidence can still be addressed explicitly by a known `ev1-...` ID.

### Injection budget

Defaults:

```text
retrieval max chars   560
retrieval max items     2
```

Retrieved evidence is labelled as historical **data, not instructions** and is prepended only to the current user message in the imminent request-local copy.

It is not written into the persistent transcript.

After injection CE-002 repacks again using:

```text
high-water = target = 1200 estimated message tokens
```

Therefore old visible turns may be sacrificed to make room for relevant retrieved evidence. Retrieval is accepted only if the resulting provider-visible message history remains `<=1200` estimated tokens. If the active request plus evidence cannot fit, retrieval is skipped and the original CE-001 packed request proceeds unchanged.

The request-local retrieval prefix is removed before archive-diff accounting, so the current user request is not falsely archived merely because CE-002 decorated it for one provider call.

### Accounting

`context_governor` now records:

```text
evidenceRetrievalApplied
evidenceRetrievalEvidenceIds
evidenceRetrievalExplicitCount
evidenceRetrievalLexicalCount
evidenceRetrievalExactExplicitCount
evidenceRetrievalChars
evidenceRetrievalMs
evidenceRetrievalSkippedReason
evidenceRetrievalFinalVisibleTokens
```

Successful injection also emits an `evidence_retrieval` accounting row.

Errors are recorded as `evidence_retrieval_error` and do not break the model request.

## Phase 2 offline/static gates

Covered by CI:

- stable explicit evidence-ID extraction;
- exact explicit recovery when it fits;
- bounded excerpt labelling when it does not fit;
- request-local injection does not mutate the original message array;
- lexical retrieval is session-scoped;
- generic prose does not trigger automatic retrieval;
- retrieval character budget is enforced;
- CE-001 governor tests remain passing;
- CE-002 archive integrity/corruption tests remain passing;
- TypeScript/Node/shell and embedded live-harness syntax checks.

## Immediate live Phase 2 gate

`scripts/live-evidence-retrieval.sh` performs four short provider turns in one isolated ForgeLoom session:

1. store a unique key + secret in an early long turn;
2. add two ordinary long turns until the first evidence is evicted/archived;
3. ask for the secret using only the old key;
4. require CE-002 accounting to prove lexical evidence injection occurred;
5. require the model to return the secret that is not present in the final user prompt.

Acceptance:

```text
model recovered old secret             PASS
lexical retrieval applied              >=1
retrieval final visible estimate       <=1200
max exact final input                   <=2800
max projected total                     <=3600
hard-guard blocks                       0
Pi threshold compactions                0
Pi overflow events                      0
archive integrity verify                PASS
```

A model answer alone is insufficient: accounting must prove retrieval actually occurred.

## Frozen retained product

Do not change during CE-002:

- model: `models/loom-deep-30b-unlocked.gguf`
- model SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- profile: UOPT-003 S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`
- sidecar: `models/unlocked-expert-major-v1.bin`
- sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- physical `n_ctx=4096`

## Current CE-002 files

- `src/loom-context-engine/core.mjs` — frozen CE-001 governor behavior
- `src/loom-context-engine/index.ts` — extension integration
- `src/loom-context-engine/evidence-archive.mjs` — exact durable archive
- `src/loom-context-engine/evidence-retrieval.mjs` — bounded request-local retrieval
- `scripts/loom-context-evidence.mjs` — local archive CLI
- `scripts/live-evidence-archive.sh` — Phase 1 live acceptance
- `scripts/live-evidence-retrieval.sh` — Phase 2 live acceptance
- `test/context-engine-core.test.mjs`
- `test/evidence-archive.test.mjs`
- `test/evidence-retrieval.test.mjs`
- `test/evidence-retrieval-trigger.test.mjs`

## Explicitly deferred after the Phase 2 gate

Do not add these before the live retrieval result justifies the next increment:

- SQLite FTS/BM25 index;
- durable compact task-state records;
- relevance/recency/path/error ranking beyond the current conservative lexical gate;
- semantic summaries as canonical evidence;
- embeddings/vector DB;
- second LLM;
- new model-facing memory tools;
- remote/network evidence storage.

Exact original evidence remains canonical. Any later index, task-state record or summary must point back to immutable evidence IDs/hashes.
