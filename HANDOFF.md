# LOOM — Context Engine Handoff

Last updated: 2026-09-07
Status: **CE-001 FINAL GO / CLOSED**
Repository: `Ilcoach/loom`
Branch: `research/context-engine-001`

Canonical closure record: `research/integration/context-engine-ce001-closure-20260907.md`

## Decision

CE-001 is accepted and closed.

LOOM keeps the retained local 30B UNLOCKED model at physical `n_ctx=4096`, while ForgeLoom retains the full Pi/Forge session externally and exposes only a bounded request-local working window to the model.

Operator modes remain:

```text
pi         -> vanilla Pi
Forge      -> normal Forge
ForgeLoom  -> Forge + LOOM Context Engine + retained LOOM model
```

Plain `pi` and normal `Forge` remain unchanged.

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

Final gateway invariant:

```text
guarded input + reserved output <= 3600 < 4096
```

Layer A (governor) is the normal flow-control mechanism. Layer B (gateway hard guard) remains fail-closed protection and must not normally be reached.

## Final acceptance evidence

### One-shot real smoke — PASS

```text
final input               926
output reserve            256
projected total          1214
headroom to 4096         2882
Pi threshold compactions    0
Pi overflow compactions     0
```

### 12-turn persistent-session stress — PASS

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

This proved the central CE-001 invariant: persistent history can exceed the physical context while the model-visible request stays bounded.

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

The first implementation produced one genuine gateway hard-guard block (`finalInputTokens=2857`, `guardInputTokens=2889`) and was correctly held at NO-GO.

Root cause: structurally large active coding turns retained too much completed tool history and large historical `toolCall.arguments`.

The corrected governor now compacts nested tool-call arguments, compacts completed call/result exchanges coherently, and as a last resort removes the oldest completed assistant tool-call plus matching tool-result group as one unit. The current user request is not truncated and the persistent Pi/Forge transcript is not mutated.

### Exact failed-transcript replay — PASS

The same real RPC transcript that previously generated the block was replayed through the corrected governor:

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

### Live corrected tool-heavy regression — PASS

```text
provider attempts              5
governor reductions            4
max raw estimate            9971
max visible estimate        1199
max exact final input        1972
max projected total          2260
min headroom to 4096         1836
hard-guard blocks               0
Pi actual compactions           0
Pi overflow events               0
```

This is the final live proof of the active-turn fix.

### Resource regression gate — PASS

Historical retained S40 backend-RSS reference: `4.676 GiB`.

```text
allowed RSS (+15%)          5.377 GiB
backend RSS before          1.752 GiB
backend RSS peak            4.662 GiB
backend RSS after           4.653 GiB
RSS delta vs reference      -0.29%
ForgeLoom agent peak RSS    64.5 MiB
```

No material RSS regression was observed. Swap telemetry was unavailable in this run and is recorded as an unmeasured quantity, not assumed to be zero.

## Frozen retained product

Do not mutate as part of CE-001 closure:

- model: `models/loom-deep-30b-unlocked.gguf`
- model SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- profile: UOPT-003 S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`
- sidecar: `models/unlocked-expert-major-v1.bin`
- sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- patched runtime: `.loom/runtime/loom-uopt002/llama-server`
- runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- physical context: `4096`

Historical UOPT performance remains frozen:

- decode `7.557 tok/s`
- 1,155-token cold prefill `11.306 tok/s`
- 1,155-token cold TTFT `102.242 s`
- refusal `0/6`
- degeneration `0/6`
- benign `8/8`

## CE-001 implementation files

- `src/loom-context-engine/core.mjs`
- `src/loom-context-engine/index.ts`
- `scripts/install-forge-loom.sh`
- `scripts/loom-context-webui-gateway.mjs`
- `scripts/verify-context-engine.sh`
- `scripts/smoke-context-engine.sh`
- `scripts/stress-context-engine.sh`
- `scripts/realistic-context-engine-benchmark.py`
- `scripts/recover-realistic-context-engine-benchmark.py`
- `scripts/replay-context-engine-rpc.mjs`
- `scripts/live-tool-heavy-context-engine.sh`
- `scripts/resource-context-engine.sh`
- `test/context-engine-core.test.mjs`

## Known semantic limitation

CE-001 retains the full session externally, but evidence evicted from the current model-visible working window is not yet independently addressable/retrievable by the model. Files can be re-read from disk, but arbitrary old conversational/tool evidence has no durable evidence ID/archive yet.

This limitation is intentionally deferred to CE-002+.

## Next work package — CE-002

CE-002 may now begin as a separate change set. Do not reopen or mutate CE-001 unless a regression of its accepted invariant is demonstrated.

Primary CE-002 direction:

1. durable external archive for evicted evidence;
2. stable evidence IDs and hashes;
3. exact recovery of old evidence on demand;
4. compact durable task state / provenance;
5. lightweight lexical retrieval first (for example SQLite FTS/BM25);
6. no second LLM, embeddings or vector DB unless later evidence demonstrates a need.

The CE-001 branch is now a rollback/reference checkpoint for the working sliding-window governor.
