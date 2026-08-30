# LOOM 30B Acceleration Paging/I/O Instrumentation Design 001 — Preregistration

Date: 2026-08-30
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Design, but do not yet implement, the minimum source-level measurement instrumentation required for a later canonical S24 paging/I/O attribution experiment.

This checkpoint exists because `LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_001` completed `NO_GO`: no already-installed non-mutating external observation method validated a high-value per-process read observable in the current session.

This checkpoint must not open the GGUF, run inference, modify source, rebuild binaries, install packages, or change system/security settings.

Its only scientific output is a frozen instrumentation specification suitable for a later separately preregistered implementation/build checkpoint.

## Frozen source and runtime context

Pinned source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Relevant frozen files:
- `src/llama-moe-offloader.h`
- `src/llama-moe-offloader.cpp`
- exact call sites that construct/start/stop the `llama_moe_offloader`, if needed only to prove where a final statistics emission can occur without changing runtime semantics.

Canonical frontend remains:
`llama-completion -no-cnv`

Canonical frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Canonical DEEP profile remains S24.

Canonical decode baseline remains approximately `4.39–4.40 tok/s`.

## Source facts already established

The pinned source currently establishes:

1. `moe_layer` already contains `total_hits` and `total_misses`.
2. `resolve(...)` increments those counters while resolving selected experts against the bounded LRU slots.
3. An expert miss creates one `moe_pread_task` for each bound expert pool.
4. `pread_pool(...)` performs ordinary `pread(...)` calls until the full expert-pool stride has been transferred.
5. Multiple `pread_pool(...)` tasks can execute concurrently through `dispatch_apply`.
6. The sidecar signals completion only after `resolve(...)` returns.
7. Existing hit/miss counters are not exposed by the inspected public interface.

The design must preserve these semantics and must not introduce any acceleration behavior.

## Design questions

Using source inspection only, produce a frozen answer to each question:

1. Which exact source locations must be instrumented to expose useful paging statistics with minimum code change?
2. Which metrics can be collected directly and unambiguously?
3. Which counters require atomic updates because `pread_pool(...)` tasks may execute concurrently?
4. Which timing statistic measures syscall/task work and which timing statistic measures sidecar `resolve(...)` wall time?
5. Where can one final structured summary be emitted after paging activity has stopped, without printing per-token/per-read hot-path logs?
6. Which fields must be reported per layer versus globally?
7. How will the later research wrapper parse the summary deterministically?
8. What measurement overhead could the instrumentation itself add, and how must that overhead be validated before attribution results are accepted?
9. Which quantities remain interpretations rather than direct measurements even after instrumentation?

## Preferred minimal metric set

The design should attempt to specify the following direct counters only if the source inspection proves clean semantics.

### Existing residency counters

Per layer:
- `total_hits`;
- `total_misses`.

Derived later, not stored as a new source counter:
- hit rate = hits / (hits + misses), when denominator is non-zero.

### Read-task counters

Per layer:
- logical `pread_pool(...)` task count;
- actual `pread(...)` syscall count;
- bytes successfully returned by `pread(...)`.

The specification must distinguish logical pool-read tasks from physical syscall count because one pool read may require more than one syscall.

### Read timing

If timing can be implemented minimally using an already-available standard monotonic clock abstraction, specify:
- cumulative wall duration spent inside each `pread_pool(...)` invocation, accumulated across tasks;
- cumulative `resolve(...)` wall duration measured on the sidecar thread.

These two timing quantities have different semantics and must never be conflated.

Because pool-read tasks may run in parallel, summed per-task read duration is **not** equivalent to process wall time or GPU stall time.

### Structural metadata

Per layer or summary as appropriate:
- layer index;
- configured slot count;
- expert count;
- bound pool count.

This permits later consistency checks between misses and logical read tasks.

## Concurrency requirement

Any counter updated from `pread_pool(...)` must be designed race-free under concurrent `dispatch_apply` execution.

The design must explicitly state which fields require atomic accumulation and which remain single-sidecar-thread fields.

Do not add locks to the hot path unless source inspection proves atomics insufficient for the frozen metric set.

## Output contract

The design must define one machine-parseable final summary format emitted only after paging activity has stopped.

Preferred property:
- one stable prefix such as `LOOM_MOE_IO_STATS`;
- one record per layer plus an optional aggregate record;
- fixed field names;
- integer counters/timing values in base units;
- no dependence on locale;
- no per-read or per-token logging.

The design must freeze exact field names before any later implementation.

Example shape only, not yet authoritative:

`LOOM_MOE_IO_STATS layer=<n> slots=<n> experts=<n> pools=<n> hits=<n> misses=<n> read_tasks=<n> pread_calls=<n> pread_bytes=<n> pread_task_ns=<n> resolve_calls=<n> resolve_ns=<n>`

The design checkpoint must decide whether this shape is source-correct and freeze the final version.

## Emission point requirement

Source inspection must identify one exact lifecycle point where:
- sidecar updates have stopped;
- all pending backend work relevant to the paging handler is synchronized as required by existing code;
- layer state still exists;
- statistics can be emitted once;
- no inference semantics are changed.

If no such point can be identified confidently, the design is `NO_GO` and must not invent one.

## Scientific semantics to freeze

A later instrumented run may directly support claims about:
- observed expert cache hits/misses;
- logical expert-pool read task count;
- actual `pread` syscall count;
- bytes returned by those calls;
- measured instrumented read-task duration;
- measured instrumented sidecar resolve duration.

A later instrumented run must **not** automatically claim from those counters alone:
- exact GPU idle/stall time;
- exact storage-device service time;
- causal speedup from prefetch;
- fully non-overlapped I/O time;
- performance of an uninstrumented binary.

Those require separate interpretation or comparison gates.

## Overhead-validation policy to design

The design must include a later validation procedure comparing canonical and instrumented binaries under identical canonical S24 conditions before accepting instrumentation measurements scientifically.

At minimum freeze:
- identical model/prompt/profile/generation conditions;
- fresh-process comparison;
- direct generation tok/s and E2E capture;
- memory/swap capture;
- a maximum acceptable instrumentation perturbation threshold selected before the implementation run.

This design checkpoint must recommend and justify a conservative threshold, but must not run the comparison.

If instrumentation overhead exceeds the later frozen threshold, the instrumented run may remain diagnostic but must not support precise attribution claims.

## Evidence root

Fresh root:
`results-local/research/30b-accel-paging-io-instrumentation-design-001/<timestamp>/`

Persist:
- exact source commit/clean status;
- inspected source paths and relevant line/function references;
- proposed minimal field additions;
- concurrency classification for every field;
- exact timing semantics;
- exact final output schema;
- exact emission lifecycle point;
- later parser contract;
- overhead-validation recommendation;
- explicit non-claims;
- final GO/NO_GO classification.

## GO gate

Classification `LOOM_30B_ACCEL_PAGING_IO_INSTRUMENTATION_DESIGN_GO` only if all are true:

1. exact pinned source provenance is verified;
2. no GGUF/model artifact is opened and no inference occurs;
3. no source/binary/package/security mutation occurs;
4. exact minimal source locations for instrumentation are identified;
5. direct metric semantics are unambiguous;
6. concurrency-safe update requirements are specified;
7. one final non-hot-path emission point is identified confidently;
8. a deterministic machine-parseable output schema is frozen;
9. an overhead-validation policy for the later instrumented binary is frozen;
10. direct claims and forbidden interpretations are explicitly separated;
11. complete durable evidence is retained.

If source inspection proves the desired direct measurements cannot be exposed minimally and unambiguously:
`LOOM_30B_ACCEL_PAGING_IO_INSTRUMENTATION_DESIGN_NO_GO`.

If provenance/evidence capture fails before a valid design determination:
`LOOM_30B_ACCEL_PAGING_IO_INSTRUMENTATION_DESIGN_MECHANICAL_NO_GO`.

## After GO

Preregister a separate **instrumentation implementation/build** checkpoint that:
- applies only the frozen measurement patch;
- produces a separate instrumented binary with exact provenance/hash;
- performs no model inference unless separately authorized;
- validates source diff scope and build reproducibility.

Only after that implementation/build checkpoint passes may LOOM preregister instrumented canonical S24 overhead calibration and paging/I/O attribution.

No expert-prefetch/overlap implementation is authorized by this design checkpoint.

## Boundaries

Forbidden:
- opening the 30B GGUF;
- model inference;
- source edit/patch;
- binary build/rebuild;
- package installation;
- runtime mutation;
- dynamic interposition;
- security-setting change;
- model download/copy/requantization;
- changing canonical S24 parameters;
- expert-prefetch/overlap implementation;
- production/provider/UI work;
- Pi Git commit/push.
