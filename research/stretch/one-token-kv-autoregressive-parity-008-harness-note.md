# Stretch 008 — stdout pipe harness note

Date: 2026-08-19
Affected run: `20260819-171446`
Status: **HARNESS I/O STALL / NO SCIENTIFIC RESULT**

## Observed progress

The first Stretch 008 launch passed all scientific preflights and host-state gate, then completed:
- official resident control;
- streamed prompt prefill through all 36 layers;
- deterministic next-token selection;
- streamed feedback-token pass through layers 0..17.

Last persisted child state:
`stream_token_layer_17_complete`.

At that state:
- layer 17 raw-weight materialization delta: `84,427,264 B`;
- post-clear delta: `0 B`;
- total KV allocation: `37,748,736 B`;
- layer 0..17 cache offsets: 5;
- layer 18..35 cache offsets: 4;
- per-layer KV allocation: `1,048,576 B`;
- layer 17 materialization wall: `0.007072 s`;
- layer 17 forward wall: `0.005329 s`.

The persisted state then stopped advancing for many minutes, far beyond the observed per-layer compute times. No final parity/classification payload was produced.

## Demonstrated harness design defect

The frozen runner launches the MLX child with `stdout=subprocess.PIPE` and `stderr=subprocess.PIPE`, but the parent does not consume either pipe while the child is running. It calls `communicate()` only after the child exits.

Meanwhile every child `save(...)` call:
1. writes the current state to `child-state.json`;
2. emits the full state JSON again to stdout as `LOOM_CHILD_STATE=...` with `flush=True`.

Stretch 008 produces substantially more state events than earlier experiments because it contains resident work plus 36 streamed prompt layers plus 36 streamed feedback-token layers and persistent KV snapshots. The captured stdout pipe can therefore fill while the child is still running. Once full, the child blocks in the flushed stdout write even though model computation and `child-state.json` persistence up to that point succeeded.

The observed stall immediately after a persisted state is consistent with this mechanism and is classified as a harness I/O stall, not a model, KV, numerical-parity, or resource failure.

## Harness-only fix

Do not modify the frozen scientific runner blob:
`03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`.

Use wrapper:
`scripts/stretch_one_token_kv_autoregressive_parity_008_pipefix.py`.

The wrapper verifies the exact frozen runner blob and changes exactly one line inside `CHILD_CODE`:
- suppress per-state `LOOM_CHILD_STATE=...` stdout emission.

Preserved unchanged:
- every `child-state.json` state write;
- final `LOOM_CHILD_COMPLETE` stdout payload;
- model and version locks;
- prompt/token policy;
- resident control;
- all 36 KV caches and cache reuse;
- all raw-weight streaming stages;
- parity calculations and thresholds;
- cache size/offset gates;
- host/runtime guardrails;
- final result parsing/classification.

## Decision

Terminate the stalled first launch if it is still running. Treat it only as a harness incident with no primary scientific result. Rerun the same preregistered Stretch 008 experiment through the pipefix wrapper.
