# LOOM — Context Engine Handoff

Last updated: 2026-09-07
Status: **ACTIVE — CE-002 PHASE 1 EVIDENCE ARCHIVE / OFFLINE VALIDATION**
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

Swap was unavailable in that probe and remains an explicitly unmeasured quantity.

## CE-002 objective

CE-001 can remove old conversational/tool evidence from the model-visible request while retaining the full Pi/Forge session externally. The missing capability is independent addressability and recovery of evidence no longer visible verbatim to the model.

CE-002 will add this without increasing model context and without introducing another model.

Target architecture:

```text
persistent Pi/Forge transcript
            |
            +--> CE-001 request-local governor --> bounded model view
            |
            `--> CE-002 evidence archive
                    |-- exact original blobs
                    |-- stable evidence IDs / SHA-256
                    |-- session provenance refs
                    |-- integrity verification
                    `-- lightweight lexical lookup / exact recovery
```

## CE-002 Phase 1 — current implementation

New module:

`src/loom-context-engine/evidence-archive.mjs`

Design:

1. Original messages that are no longer present **verbatim** after `packMessages()` are identified with multiset semantics.
2. The original message is canonicalized deterministically and SHA-256 hashed.
3. Stable evidence ID format:

```text
ev1-<64 lowercase SHA-256 hex chars>
```

4. Exact original evidence is stored content-addressed under the Context Engine runtime root:

```text
evidence/blobs/<sha256>.json
```

5. Per-session provenance is stored separately:

```text
evidence/sessions/<safe-session-id>/<sha256>.json
```

6. Duplicate evidence reuses the same blob and session reference rather than appending duplicate records.
7. Files are local-only and written with restrictive permissions where the platform supports them.
8. Existing blobs are hash-verified before reuse.
9. The persistent Pi/Forge transcript is not mutated.
10. The provider-visible request is unchanged relative to CE-001; Phase 1 archive metadata is not injected into the model context.

The Pi extension now archives evidence only when the CE-001 governor actually changes the imminent model view. Archive failures are explicitly recorded as `evidence_archive_error` accounting events and do not silently alter the provider request.

Context-governor accounting additionally records:

```text
evidenceCandidates
evidenceBlobsCreated
evidenceSessionRefsCreated
evidenceDeduped
```

## Local evidence CLI

New CLI:

`scripts/loom-context-evidence.mjs`

Commands:

```bash
node scripts/loom-context-evidence.mjs sessions
node scripts/loom-context-evidence.mjs search "query" [--session ID] [--limit N]
node scripts/loom-context-evidence.mjs show ev1-<sha256>
node scripts/loom-context-evidence.mjs verify
```

`show` returns the exact archived message envelope. `verify` checks blob filenames, evidence IDs, hashes, and session-ref/blob consistency. `search` is intentionally simple local lexical retrieval in Phase 1; there is no embedding model or vector database.

## Phase 1 acceptance gates

Before any retained-30B test:

1. canonical hash is stable across object-key ordering;
2. dropped and transformed originals are detected correctly, including duplicate-message multiset cases;
3. blobs are content-addressed and deduplicated;
4. session references are deduplicated;
5. exact recovery reproduces the original message object;
6. lexical lookup finds a unique archived marker;
7. archive verification detects metadata/hash corruption;
8. CE-001 governor unit tests remain unchanged and passing;
9. syntax/repository invariant CI passes on `research/context-engine-002`.

Only after those pass should the extension be reinstalled and a short live archive/recovery test be run.

## Explicitly deferred

Not in the first CE-002 increment:

- automatic injection of retrieved evidence into the model request;
- new model-facing memory/retrieval tools;
- embeddings;
- vector DB;
- second LLM;
- remote/network archive;
- semantic summarization as the canonical source of evidence.

Exact original evidence remains canonical. Any later summaries/indexes must point back to immutable evidence IDs/hashes.

## Frozen retained product

Do not change during CE-002:

- model: `models/loom-deep-30b-unlocked.gguf`
- model SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- profile: UOPT-003 S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`
- sidecar: `models/unlocked-expert-major-v1.bin`
- sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- physical `n_ctx=4096`

## Immediate next action

Run CE-002 static/unit CI, fix any archive-integrity defects, then add one short live test that proves:

- a real ForgeLoom context reduction creates archive evidence;
- at least one archived item can be recovered exactly by evidence ID;
- archive verification passes;
- CE-001 safety envelope still reports zero hard-guard blocks and zero Pi overflow/threshold compactions.
