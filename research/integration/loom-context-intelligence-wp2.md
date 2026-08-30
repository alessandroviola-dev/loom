# LOOM Context Intelligence — WP2

Date: 2026-08-30
Status: **AUTHORIZED / ACTIVE**
Checkpoint: `LOOM_CONTEXT_INTELLIGENCE_WP2`

## Goal

Improve real Pi/LOOM efficiency on the canonical local 30B stack by implementing only the two user-approved context mechanisms:

1. **Caveman-derived deterministic context packing/compression**;
2. **Cavemem-derived progressive local project memory**.

WP2 is a macro work package. Internal engineering/research gates are evidence-based, but Pi must not return after routine internal GO/NO_GO results. Record bounded evidence, revert regressions, and continue until WP2 is complete or a genuine user-action blocker exists.

WP2 must not implement WP3 behavioral editing.

## Canonical runtime inherited from WP1

WP1 classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`.

Canonical DEEP runtime profile:
**S32**.

Rollback:
S24.

Canonical model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Canonical source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Canonical `llama-server` SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Validated S32 decode:
`5.596 tok/s` median in matched deterministic WP1 A/B.

Operational server:
`http://127.0.0.1:18080`

Serving-path prompt/KV reuse is already validated under bounded `--cache-ram 512`.

WP2 must preserve the WP1 runtime/server as a known-good rollback baseline and must not trade away the validated serving path merely to simplify context integration.

## User-approved scope

Permanent mechanisms only:
- Caveman-derived context intelligence;
- Cavemem-derived progressive project memory.

Do **not** install/integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

Small implementation ideas from other papers may be borrowed only when necessary to support Caveman/Cavemem with negligible permanent overhead.

Do not install Caveman or Cavemem wholesale as mandatory upstream dependencies unless direct inspection proves that doing so is lighter and cleaner than the LOOM-native implementation. Default is minimal LOOM-native reimplementation of the useful mechanisms.

## Architecture target

Desired flow:

```text
project/session evidence
        |
        +--> privacy filter / exact-source store
        |
        +--> Cavemem-style compact observations in local project DB
                    |
current query ------+--> cheap FTS/BM25 retrieval of compact candidates
                                |
current tool/context items -----+--> Caveman-style deterministic packer
                                             |
                                   typed compression + scoring
                                             |
                                   select under token budget
                                             |
                                   restore chronology
                                             |
                                   compact prompt + recovery handles
                                             |
                                   canonical localhost 30B
```

Exact detail remains recoverable outside the active prompt.

## Core invariants

1. **No extra LLM is used for compression, ranking, writing memory, or reranking by default.**
2. **No embedding model is required in v0.** Start with SQLite FTS5/BM25/lexical retrieval.
3. **Exact machine-critical values remain exact or byte-recoverable.** This includes code, commands, paths, URLs, hashes, versions, identifiers and benchmark numbers.
4. **Compression may reduce visibility but must not destroy recoverability.**
5. **Project technical memory is project-scoped by default.** Do not mix generic personal memory into LOOM technical state.
6. **Privacy filtering/redaction occurs before durable persistence.**
7. **Do not inject all stored memories at session start.** Memory is progressive disclosure, not transcript replay.
8. **Do not add a large permanent model-facing memory/tool schema.** Prefer host-side retrieval/packing and at most one compact retrieval entry point if Pi integration genuinely requires it.
9. **Errors/warnings/failing evidence receive deterministic preservation priority.**
10. **Selection may be relevance-based; presentation of selected evidence must restore original chronology.**

## Phase A — Integration audit + baseline

Before implementation:
- inspect Pi's actual provider/request/config/extension hooks;
- inspect existing LOOM scripts/configs/state/evidence conventions;
- identify where provider-bound context can be transformed with the lowest permanent overhead;
- preserve backups before Pi/config mutation;
- create a fresh WP2 evidence root under `results-local/context-intelligence-wp2/<timestamp>/`;
- freeze representative benchmark tasks/corpus before measuring candidates.

Mechanical naming cleanup is authorized here:
- current provider/model label `loom-local/loom-deep-30b-s24` is stale because WP1 promoted S32;
- if Pi's provider mechanism permits a safe rename, change the canonical label to `loom-local/loom-deep-30b-s32` while preserving the previous config backup and compatibility evidence;
- if another local artifact depends on the old label, preserve an alias rather than breaking the working WP1 integration.

Do not confuse provider-label cleanup with runtime performance change.

## Phase B — Cavemem-derived progressive local memory

Implement the smallest project-local memory store that provides progressive disclosure.

Preferred local layout:

```text
.loom/
  memory.sqlite
  artifacts/
```

Equivalent project-local paths are allowed if they fit the repository better.

Minimum logical record fields:
- stable id;
- project scope;
- timestamp;
- kind;
- compact summary/observation;
- keywords/tags;
- importance/priority;
- source reference;
- exact-body/artifact reference where applicable;
- content hash;
- privacy/redaction class.

Start with SQLite + FTS5/BM25 if available in the existing local Python/SQLite toolchain.

Minimum operations:

```text
record(observation, source)
search(query, limit)
get(id)
timeline(...)
```

Only expose the minimum operation(s) Pi actually needs. Prefer host-side automatic persistence/retrieval over multiple permanent model tools.

Persist primarily:
- decisions;
- measured results;
- failed/reverted approaches;
- stable constraints;
- exact checkpoints/provenance;
- durable operational facts.

Do not treat every conversation turn as equally valuable memory.

Retrieval flow should be progressive:

```text
query
 -> compact top candidates
 -> select only relevant IDs/details
 -> exact body/evidence retrieval only when needed
```

No always-on semantic embeddings in v0. Add/test local embeddings only if the frozen lexical baseline demonstrably misses required evidence and the additional RAM/latency can be bounded; they are not required for WP2 GO.

## Phase C — Caveman-derived deterministic context packing

Implement a LOOM-native packer that treats context as a budgeted data structure.

Required candidate item metadata should include equivalent fields for:
- id;
- timestamp/order;
- token estimate;
- source type;
- text/compact representation;
- explicit priority;
- pinned state;
- error/warning state;
- recovery reference.

### Deterministic scoring

Use a local deterministic score inspired by Caveman:

```text
score = lexical/BM25 relevance
      + explicit priority
      + recency contribution
      + error/warning boost
      + overwhelming pin boost
```

Exact constants may be tuned only on frozen training/development examples and then frozen before final benchmark. Do not tune against final acceptance answers.

### Selection

1. score candidates;
2. select highest-value items that fit the configured prompt budget;
3. restore original chronological order among selected items;
4. emit compact context plus manifest/accounting;
5. ensure omitted/elided evidence has a stable recovery reference.

### Typed deterministic compression

Prioritize the formats LOOM/Pi actually encounters most. At minimum inspect feasibility/value for:
1. shell/log output;
2. repository/search results;
3. JSON/structured API output;
4. code/file reads;
5. diffs.

Compress structurally, not through free-form model summarization.

Preserve exact:
- error lines;
- identifiers;
- paths;
- commands;
- hashes/versions;
- benchmark values;
- changed diff lines;
- query-near evidence;
- schema/shape needed for interpretation.

Fold/remove only deterministically irrelevant/repeated structure.

Small/no-op inputs must bypass or nearly bypass the compressor when overhead would exceed savings.

### Recovery handles

Any omitted exact evidence must remain reachable through a stable local reference, for example an equivalent of:

```text
loom://artifact/<hash>
loom://artifact/<hash>#L400-L460
```

The URI spelling is not important; exact recoverability is.

Required accounting per packing operation:
- tokens/estimated tokens before;
- after;
- saved;
- selected/deferred counts;
- compression/packing wall ms;
- recovery refs emitted;
- recovery calls actually used.

## Phase D — Pi integration

Integrate the combined layer into Pi/local LOOM with minimum permanent context/schema overhead.

Preferred strategy:
- host-side/context-preparation hook or light wrapper around the existing Pi provider path;
- progressive memory retrieval before prompt construction only when useful;
- deterministic packer immediately before provider-bound context;
- exact recovery on demand.

Do not replace Pi with a new monolithic agent framework.

Do not advertise a large always-on set of memory/compression tools to the model.

The integration must preserve:
- the existing localhost-only `llama-server` path;
- streaming behavior where already working;
- validated prompt/KV reuse where compatible;
- Pi's ability to run with the context layer disabled as a rollback/control.

## Phase E — Frozen benchmark and promotion

Create a representative frozen LOOM/Pi benchmark from real project workload classes without using final expected answers to tune the system.

Include both context-heavy and negative/no-op cases. Reuse existing durable LOOM evidence where possible instead of manufacturing only compressor-friendly samples.

Minimum comparison arms:

```text
A. current WP1 Pi/runtime baseline, no WP2 layer
B. Caveman packer/compression only
C. Caveman + Cavemem progressive retrieval
```

If useful for diagnosis, Cavemem-only may be measured internally, but it is not required as a separate promotion arm.

Representative workload classes should include:
- verbose logs/errors;
- large repository/search output;
- structured JSON/API evidence;
- code/file inspection;
- diffs;
- long-running project question requiring recovery of an earlier decision/result;
- small/already concise/no-op context.

Freeze objective task success criteria before final evaluation.

### Required metrics

Measure where directly available:
- provider/server prompt input tokens or closest direct runtime count;
- prompt/prefill wall;
- E2E wall;
- decode tok/s to ensure the context layer does not alter runtime semantics;
- host packing/retrieval wall ms;
- peak RSS/swap delta attributable to WP2 components;
- correct task/answer success;
- correct recovery of prior decision/evidence;
- stale-memory errors;
- missed relevant evidence;
- recovery calls;
- exact-source verification rate;
- tokens before/after packing;
- permanent prompt/tool-schema overhead.

### WP2 promotion gate

`LOOM_CONTEXT_INTELLIGENCE_WP2_GO` requires all of the following:

1. Caveman-derived deterministic packer is operational and reversible through exact recovery references;
2. Cavemem-derived local project memory is operational with progressive retrieval and source provenance;
3. privacy/redaction boundary occurs before durable memory writes;
4. final benchmark quality/task success is non-inferior to baseline on the frozen objective criteria;
5. context-heavy benchmark cases show a material aggregate provider-input reduction; target at least **20% median reduction** versus baseline unless direct token accounting proves a more appropriate equivalent metric;
6. small/already concise/no-op cases do not show a material aggregate regression; target <= **5% provider-input overhead** and no correctness regression;
7. packing/retrieval CPU latency is small relative to the saved prefill/E2E time on the canonical M1 host, and no permanent heavy background service is required;
8. WP2 memory/RAM/swap overhead remains safe with the canonical S32 server;
9. no stale/incorrect retrieved memory causes an accepted wrong result in the frozen final benchmark;
10. Pi can complete at least one real local-model task using the final combined WP2 path and can also run with the layer disabled as rollback;
11. complete durable evidence and exact hashes/config provenance are retained.

If an individual compressor, retrieval strategy or memory feature is net-negative, revert/disable that subfeature and continue with the remaining evidence-backed design. WP2 GO does not require every attempted compressor or optional feature to survive.

`LOOM_CONTEXT_INTELLIGENCE_WP2_NO_GO` applies only if no combined Caveman/Cavemem implementation can deliver safe net-positive context intelligence without harming baseline task utility or operational stability.

## Stopping rule

Do not endlessly optimize context heuristics.

After:
- the required typed compressor families have been evaluated;
- one deterministic packer design is frozen;
- lexical progressive memory is benchmarked;
- up to two materially different corrective iterations have been tried for any failing quality/token gate;

select the best validated configuration and finish WP2 rather than continuing broad parameter search.

## Final operating result

Leave WP2 either:
- enabled by default only if the final benchmark proves net-positive; or
- installed but optional/off by default if some workloads benefit while global default promotion is not justified.

Do not delete the WP1 no-context baseline/rollback path.

## Return policy

Do not return after routine internal sub-results.

Return only when:
1. WP2 is complete; or
2. a genuine blocker requires user action/credentials/destructive or security-sensitive changes/unavailable hardware or storage.

Final report must include:
- classification;
- final Caveman/Cavemem architecture;
- exact integration point with Pi;
- provider/model id after any naming cleanup;
- memory DB/artifact paths;
- context budget/policy;
- typed compressors retained/disabled;
- recovery mechanism;
- baseline vs packer-only vs combined benchmark table;
- task-quality results;
- provider input/prefill/E2E changes;
- packing/retrieval overhead;
- RAM/swap impact;
- privacy/redaction behavior;
- source/artifact/config hashes;
- changed files;
- evidence roots;
- important reverted/negative cases;
- rollback/disable procedure;
- genuine remaining blocker, if any.

Pi must not commit or push.
