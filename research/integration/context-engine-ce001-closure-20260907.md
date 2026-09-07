# CE-001 Context Engine — Closure

Date: 2026-09-07
Status: **FINAL GO / CLOSED**
Branch: `research/context-engine-001`

## Decision

CE-001 is accepted and closed.

The retained LOOM 30B UNLOCKED model continues to run with physical `n_ctx=4096`, while ForgeLoom keeps the persistent Pi/Forge session externally and exposes only a bounded request-local working window to the model.

The final CE-001 acceptance evidence demonstrates that long raw session history can exceed the physical model context while every provider-visible request remains safely bounded, without Pi threshold/overflow compaction and without relying on the gateway hard guard as normal flow control.

## Frozen operating envelope

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

Gateway invariant:

```text
guarded input + reserved output <= 3600 < 4096
```

## Acceptance evidence

### One-shot smoke — PASS

```text
final input               926
output reserve            256
projected total          1214
headroom to 4096         2882
Pi threshold compactions    0
Pi overflow compactions     0
```

### 12-turn synthetic persistent-session stress — PASS

```text
RPC turns completed         12
persistent message count    24
max raw history estimate  5777
max visible estimate      1430
governor compactions         9
max exact final input     2343
max projected total       2631
min headroom to 4096      1465
hard-guard blocks            0
Pi threshold compactions     0
Pi overflow compactions      0
```

This directly proved the target architecture: raw retained session history exceeded 4096-equivalent working history while the model-visible request stayed bounded.

### Frozen realistic coding benchmark — completed

Objective model-quality score:

```text
60.0 / 100
T01  15.00 / 15
T02   4.29 / 15
T03   8.57 / 15
T04   8.57 / 15
T05  21.43 / 25
T06   2.14 / 15
```

The original CE-001 implementation exposed one genuine gateway hard-guard block during this workload:

```text
final input       2857
guarded input     2889
output reserve     256
projected total   3145
input ceiling     2800
hard-guard blocks    1
```

The physical limit remained protected, but this was correctly treated as CE-001 NO-GO because Layer A had failed to bound a structurally large active coding turn.

Root cause: historical `toolCall.arguments` and repeated completed tool exchanges inside one active user turn were not bounded strongly enough.

## Active-turn fix

The governor now:

1. drops oldest complete user turns first;
2. preserves the current user request;
3. compacts oversized tool-result text;
4. compacts stale assistant narration/thinking;
5. compacts large nested historical `toolCall.arguments`;
6. compacts completed call/result exchanges coherently;
7. preserves call/result IDs and sequencing;
8. performs a more aggressive completed-exchange pass when needed;
9. as a final fallback, removes the oldest **completed** assistant tool-call plus matching tool-result group as one unit until the target is met;
10. never mutates the persistent Pi/Forge transcript.

### Exact realistic transcript replay — PASS

The same RPC transcript that previously generated the hard-guard block was replayed offline through the corrected governor:

```text
provider attempts           24
max raw estimate          8557
max replay visible        1196
governor reductions         20
tool-arg compactions        59
emergency passes            11
target misses (>1200)        0
high-water misses (>1600)    0
```

### Live tool-heavy regression — PASS

Real corrected ForgeLoom session:

```text
provider attempts              5
governor reductions            4
max raw estimate            9971
max visible estimate        1199
emergency passes               5
max exact final input        1972
max projected total          2260
min headroom to 4096         1836
hard-guard blocks               0
Pi actual compactions           0
Pi overflow events               0
```

This is the final live proof that the active-turn fix works on the retained 30B runtime.

## Resource regression gate — PASS

Historical retained S40 reference: `4.676 GiB` backend RSS.

Final CE-001 resource probe:

```text
historical S40 RSS ref      4.676 GiB
allowed RSS (+15%)          5.377 GiB
backend RSS before          1.752 GiB
backend RSS peak            4.662 GiB
backend RSS after           4.653 GiB
RSS delta vs reference      -0.29%
ForgeLoom agent peak RSS    64.5 MiB
```

No material backend-RSS regression was observed. Swap telemetry was unavailable in this run; this is recorded as a measurement limitation, not inferred as zero swap growth.

## Retained product

Do not mutate as part of CE-001 closure:

- model: `models/loom-deep-30b-unlocked.gguf`
- model SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- UOPT-003 S40 profile
- sidecar: `models/unlocked-expert-major-v1.bin`
- sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- patched runtime: `.loom/runtime/loom-uopt002/llama-server`
- runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- physical context: `4096`

Operator modes remain:

```text
pi         -> vanilla Pi
Forge      -> normal Forge
ForgeLoom  -> Forge + LOOM Context Engine + retained LOOM model
```

Plain `pi` and normal `Forge` remain unchanged.

## Known semantic limitation

CE-001 preserves the full session externally but does not yet provide independent retrieval of evidence evicted from the current model-visible window. The model can re-read files from disk, but arbitrary old conversational/tool evidence that is outside the request-local working set is not yet an addressable archive.

This is intentionally deferred.

## Next work package

CE-002 may now begin as a separate change set.

Primary target:

- durable external evidence archive for evicted context;
- stable evidence IDs/hashes;
- exact recovery of old evidence on demand;
- compact task state / provenance;
- lightweight lexical retrieval first (BM25/SQLite FTS or equivalent);
- no second LLM, embeddings, or vector DB unless later evidence demonstrates a need.

Do not reopen CE-001 unless a regression in its accepted invariant is demonstrated.
