# LOOM 30B Acceleration Paging/I/O Attribution Preflight 001 — Result

Date: 2026-08-30
Classification: **`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_NO_GO`**

## Summary

The frozen non-mutating instrumentation preflight completed validly but did not identify an already-installed macOS observation method usable in the current session that could recover a high-value per-process read observable from the deterministic synthetic `os.pread` probe.

This is a scientific `NO_GO`, not a mechanical failure.

The result does not imply that expert paging is or is not a decode bottleneck. It establishes only that the desired attribution cannot be performed with the tested non-mutating observation methods under the current session constraints.

No GGUF/model artifact was opened and no inference occurred.

## Evidence

Evidence root:
`results-local/research/30b-accel-paging-io-attribution-preflight-001/20260830T111709Z/`

## Provenance

- pinned source commit and clean status verified;
- canonical frontend SHA256 verified: `38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`;
- no GGUF/model artifact opened;
- no inference;
- no source/runtime/package/security mutation;
- no install or rebuild;
- no Git action by Pi.

## Frozen synthetic read probe

The deterministic Python `os.pread` probe executed:
- 5 reads;
- offsets `0`, `4096`, `16384`, `32768`, `49152`;
- aggregate requested/returned bytes `15,872`.

Probe SHA256:
`0ee66ce40e5865c6288a9ea259b02d7e46d58d3086ca4cc99dd6253c623e095d`

Deterministic parser SHA256:
`46e996b911b177a0695b8d70edd816b7b606ec1c3c5fef5bb37bf5ff0883797c`

All synthetic probe executions completed successfully.

## Observation-method result

The tested native tracing candidates were unavailable for usable per-process read observation in the current research session.

No tracer emitted read observations for the frozen probe. Retained raw evidence was deterministically parsed as zero records / zero observed bytes, so no high-value observable was validated against synthetic ground truth.

## Gate evaluation

PASS:
- provenance;
- no GGUF/model access;
- no mutation;
- durable raw evidence and deterministic parsing;
- measurement semantics/limitations;
- cleanup.

FAIL:
- usable non-mutating tracer;
- validated target isolation for a usable tracer;
- high-value observable validated against synthetic ground truth;
- selected observation method for later inference attribution.

Final classification:
**`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_NO_GO`**.

## Scientific interpretation

No direct claim is supported about:
- expert hit/miss rate;
- expert bytes read per token;
- paging read duration;
- storage-wait contribution to decode wall time;
- prefetch/overlap benefit.

A model inference attribution run must not proceed without a separately preregistered measurement strategy.

## Exact next step

Preregister a source-level instrumentation strategy before authorizing any measurement patch or rebuild.

The strategy must define, without opening the GGUF or modifying source:
- exact frozen source locations to instrument;
- exact counters/timers and their semantics;
- concurrency requirements for counters updated by parallel read tasks;
- structured durable output format;
- provenance rules for the instrumented binary;
- overhead-validation policy before instrumented measurements are used scientifically;
- which later attribution quantities can and cannot be claimed.

No expert-prefetch/overlap implementation is authorized by this result.
