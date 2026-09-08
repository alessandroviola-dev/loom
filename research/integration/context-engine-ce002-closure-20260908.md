# LOOM Context Engine — CE-002 closure

Date: 2026-09-08
Branch: `research/context-engine-002`
Status: **CE-002 FINAL GO / CLOSED (archive + bounded retrieval)**

## Scope

CE-002 extends the frozen CE-001 request-local governor with a durable local evidence archive and bounded request-local retrieval. It does not change the retained model, physical `n_ctx=4096`, CE-001 safety envelope, plain `pi`, or normal `Forge`.

Operator isolation is now explicit:

```text
pi         -> vanilla Pi; LOOM Context Engine not loaded
Forge      -> normal Forge; LOOM Context Engine not loaded
ForgeLoom  -> Forge + explicitly loaded LOOM Context Engine + retained LOOM 30B
```

The extension is installed outside Pi's globally auto-discovered `extensions/` directory and is loaded only by the `ForgeLoom` launcher via `--extension`.

## Accepted CE-002 evidence

### Phase 1 — durable exact archive — PASS

Real retained Mac/30B run:

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

The first evicted prompt was recovered exactly by stable `ev1-<sha256>` evidence ID.

### Phase 2 — bounded archive-to-model retrieval — PASS

Real retained Mac/30B synthetic recall run:

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

The final prompt did not contain the secret `ORCHID_7391`; CE-002 retrieved the archived evidence and the model returned the correct value without a fifth model-facing tool.

### Lightweight coding retrieval — CE-002 function PASS / model scope FAIL

The heavy multi-turn coding gate was retired on the 8 GB Mac after it caused severe memory/swap pressure. A replacement lite gate pre-seeded one immutable evidence blob offline and sent exactly one real coding request to the retained 30B.

Offline diagnosis of the real lite run:

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

- CE-002 retrieved the correct archived external-CI contract.
- The retained 30B correctly applied the retrieved values to `src/retry_policy.py`.
- The model also created `verify.py` despite the instruction to edit only the target file. This is a model/tool-discipline failure, not an archive/retrieval failure.
- The strict realistic coding scope gate therefore remains **not passed**; it is not relabelled as PASS.
- This scope failure is non-blocking for CE-002 closure because the CE-002 objective is archive + retrieval correctness, already demonstrated independently and in the coding workflow.

The lite diagnostic reported `guarded provider calls = 0` because it could not recover the gateway accounting rows after the run. Therefore that lite run is **not** used as fresh proof of CE-001 provider-envelope safety. CE-001 safety remains supported by the already accepted CE-001 live gates and the earlier CE-002 Phase 1/Phase 2 guarded runs.

## Retrieval behavior frozen at closure

- immutable content-addressed evidence blobs (`ev1-<sha256>`)
- per-session provenance
- integrity verification
- exact explicit retrieval by known evidence ID
- conservative automatic lexical retrieval scoped to the current session
- distinctive anchors only (paths, error IDs, structured keys)
- bounded request-local injection
- default retrieval budget: 560 characters / 2 items
- provider-visible CE working target remains `<=1200` estimated message tokens
- historical evidence is treated as data, never as authoritative instructions
- persistent Pi/Forge transcript is not rewritten
- no second LLM, embeddings, vector DB, or fifth model-facing tool

## Frozen CE-001 envelope

```text
physical context       4096
safe total             3600
final input ceiling    2800
maximum output          800
working high-water     1600
working target         1200
legacy count margin      32
```

CE-002 does not weaken these limits.

## Hardware validation policy

For the 8 GB Mac, long/endurance live 30B gates are retired. Future validation should use:

1. unit/static tests first;
2. deterministic offline fixtures/replay where possible;
3. at most one short live 30B request per acceptance probe;
4. no automatic live retries;
5. provider-call and wall-clock caps;
6. automatic backend shutdown on exit;
7. no concurrent Forge/Astra live gate execution.

## Deferred work

Possible future CE-003+ work includes compact durable task state, better deterministic ranking/indexing, and exact recovery ergonomics. Any future cloud/frontier-model experiment must be a separate opt-in product/calibration; the current CE thresholds are designed for the retained local 4096-context model and must not be applied unchanged to frontier models with very large context windows.

## Disposition

**CE-002 FINAL GO / CLOSED for archive + bounded retrieval.**

Do not reopen CE-002 because the retained 30B created `verify.py`; that behavior belongs to model/tool-discipline evaluation. Reopen only for a demonstrated archive/retrieval/integrity regression.
