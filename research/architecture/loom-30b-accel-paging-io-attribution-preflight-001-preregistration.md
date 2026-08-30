# LOOM 30B Acceleration Paging/I/O Attribution Preflight 001 — Preregistration

Date: 2026-08-30
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Prepare a non-mutating, no-GGUF instrumentation path for the next canonical S24 decode attribution experiment.

The goal is to determine whether the existing pinned Apple MoE paging runtime can be observed externally well enough to measure expert-paging I/O without patching or rebuilding the runtime.

This checkpoint is an instrumentation preflight only. It must not produce or imply a decode-performance claim.

## Why this preflight is required

Pinned-source inspection already establishes the mechanism:

- `llama_moe_offloader::resolve(...)` records LRU hits/misses internally;
- each miss creates one `pread_pool(...)` task per bound expert pool;
- `pread_pool(...)` performs synchronous `pread(...)` calls until one expert-pool stride is fully read;
- multiple read tasks may be issued through `dispatch_apply`;
- the sidecar signals the Metal event only after `resolve(...)` finishes.

The current header contains `total_hits` and `total_misses` counters, but the inspected implementation does not expose a public reporting interface for those counters.

Therefore the next scientific run must not assume that exact hit/miss or `pread` timing is observable without first proving an instrumentation method.

Pinned source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Relevant frozen files:
- `src/llama-moe-offloader.h`
- `src/llama-moe-offloader.cpp`

No source modification is authorized in this preflight.

## Canonical DEEP context

Model remains:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Frontend remains:
`llama-completion -no-cnv`

Frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Canonical profile remains S24.

**The GGUF must not be opened in this preflight.**

## Preflight questions

Answer, with durable evidence:

1. Which already-installed macOS/native tools can observe file-read activity for one target process without modifying that process?
2. Can at least one available method distinguish or measure `pread`/read operations with usable count, byte and/or timing information?
3. Can the method be scoped to a single child PID or otherwise isolate the target process reliably?
4. Does the method require privilege escalation, interactive approval, SIP changes, package installation, source patching, binary rebuilding, dynamic-library injection or other mutation?
5. Can its output be captured durably and parsed deterministically by a research wrapper?
6. Can the chosen method be validated against a synthetic process whose exact read count, byte count and offsets are known in advance?
7. Which exact observable(s) can safely be used in the later attribution run, and which desired quantities remain unavailable?

## Candidate instrumentation inventory

Inspect only what is already installed. Candidate tools may include, but are not limited to:

- `fs_usage`;
- `dtrace`;
- `dtruss`;
- `xctrace`;
- `sample`;
- `spindump`;
- `iostat`;
- `/usr/bin/time -l`;
- `vm_stat`;
- Activity Monitor-compatible command-line system telemetry already present on macOS.

This list is exploratory, not an authorization to install anything or modify host security settings.

Do not assume a candidate is usable merely because its executable exists.

## Synthetic read probe

A small local synthetic probe is authorized, provided it:

- creates only temporary files under the fresh evidence root;
- uses a deterministic known sequence of ordinary `pread` operations;
- does not open the GGUF or any model artifact;
- does not compile native code unless an already-existing interpreter/runtime can express the probe directly;
- does not require package installation;
- does not require source/runtime mutation;
- is deleted or retained only inside evidence according to the wrapper's normal bounded cleanup policy.

Preferred implementation is a short Python standard-library process using `os.open`, `os.pread`, and deterministic offsets/sizes.

Freeze a synthetic pattern before tracing, for example:
- fixed temporary file size;
- fixed number of reads;
- fixed byte size per read;
- fixed offsets;
- known aggregate requested bytes.

The exact synthetic pattern and its SHA/hashable script contents must be persisted before executing candidate tracers.

## Validation requirements

A candidate tracing method is considered **usable for the later attribution run** only if all are true:

1. it is available on the host without installation;
2. it can execute non-interactively under the current research session, or its required privilege state is already available without changing system/security configuration;
3. it can be scoped sufficiently to isolate the synthetic probe;
4. its raw output can be persisted;
5. a deterministic parser can recover the observable(s) claimed from the raw output;
6. the recovered synthetic values agree with the frozen known pattern within the explicitly applicable semantics of the tool;
7. running the tracer does not modify source, runtime, binary, model, package state or system security configuration.

If a tool exposes only approximate/system-wide throughput, document that limitation; do not promote it to exact per-expert I/O evidence.

## Desired later-run observables

Priority order:

A. direct per-process `pread` count and requested/completed bytes;
B. direct per-`pread` or aggregate syscall wall duration;
C. file offsets/sizes sufficient to distinguish expert-pool reads from unrelated reads;
D. temporal correlation between paging reads and decode token production;
E. process-level read throughput;
F. only if directly observable without mutation: expert hit/miss counts.

No post-hoc inference may convert an unavailable observable into a direct measurement claim.

Static source-derived quantities such as expert-pool stride may be used later only if separately recorded as source-derived, not measured.

## Evidence root

Fresh root:
`results-local/research/30b-accel-paging-io-attribution-preflight-001/<timestamp>/`

Persist:
- host/OS identity;
- exact pinned source/runtime provenance;
- inventory of candidate instrumentation commands and versions/help output where useful;
- privilege/non-interactive usability result for each candidate actually tested;
- frozen synthetic probe source/hash and known expected read pattern;
- exact tracer commands;
- complete bounded raw tracer output;
- deterministic parser or parsing procedure;
- recovered synthetic observables;
- comparison against expected values;
- explicit limitations;
- selected single instrumentation method for the later inference attribution run, if any;
- cleanup proof;
- statement confirming GGUF/model artifact was never opened.

## GO gate

Classification `LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_GO` only if all are true:

1. pinned source/runtime provenance is verified;
2. no GGUF/model artifact is opened;
3. no source/runtime/binary/package/security-setting mutation occurs;
4. at least one already-installed non-mutating method is demonstrated on the frozen synthetic probe;
5. that method isolates the target probe sufficiently for later inference attribution;
6. raw output is durable and deterministically parseable;
7. at least one high-value observable from A-C is validated against the synthetic ground truth;
8. exact measurement semantics and unavailable quantities are documented;
9. one instrumentation method is selected and frozen for preregistration of the actual inference attribution run;
10. complete durable evidence is retained.

If the host can be inspected validly but no non-mutating method can provide a high-value observable from A-C:
`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_NO_GO`.

If provenance, tooling execution or evidence capture fails mechanically before a valid determination:
`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_MECHANICAL_NO_GO`.

## Interpretation

A GO means only that LOOM has a validated, non-mutating observation method suitable for a separately preregistered S24 inference attribution run.

It does not establish:
- how many expert misses occur during decode;
- how many bytes are read per token;
- how much decode wall time is I/O-bound;
- whether prefetch/overlap will improve throughput;
- any new tok/s result.

A NO_GO is scientifically useful: it establishes that exact attribution requires a different instrumentation strategy, which must then be separately preregistered before any runtime patch or rebuild.

## Boundaries

Forbidden:
- opening the 30B GGUF or running model inference;
- source patching;
- binary rebuild;
- dynamic-library injection/interposition;
- package installation;
- SIP/security-setting modification;
- reboot;
- model download/copy/requantization;
- runtime mutation;
- expert-prefetch/overlap implementation;
- changing canonical S24 parameters;
- production/provider/UI work;
- Pi Git commit/push.
