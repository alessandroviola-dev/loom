# STREAMING-ATTRIBUTION 001 — F1 real-M1 streamed-weight wall-time attribution

Date: 2026-08-22
Status: FROZEN / RUN PENDING

## Goal

Explain the large real-generation slowdown measured at MEMORY-FRONTIER 001 F1 (H32) before choosing an optimization treatment.

MEMORY-FRONTIER 001 measured:
- F0 FULL: 13.433 real generation tok/s;
- F1 H32: 2.527 tok/s;
- F1 peak-MLX saving: 864,774,144 B;
- F1 logical streamed traffic: 896,041,120 B/generated token;
- F1 process-read diagnostic: ~26.5 MB/generated token;
- exact token parity PASS.

The gap between logical streaming traffic and process-read diagnostics means the slowdown must not be labeled physical SSD bandwidth cost without attribution.

## Scientific question

For exact real-M1 F1 H32 generation, how is per-token wall time divided among:

1. streaming-source/range access and host-side decoding/slicing;
2. creation/reconstruction of quantized MLX tensors/parameter structures;
3. `mx.eval` / materialization / device synchronization attributable to newly streamed tensors;
4. forward compute using the streamed stages;
5. other orchestration/cleanup overhead;
6. persistent-stage model compute.

The experiment is diagnostic. It changes no model math and promotes no optimization.

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1 where inherited
- F1 H32 residency from MEMORY-FRONTIER 001
- transformer layers 0..31 persistent
- layers 32..35 streamed via the same proven path
- shared embed/final-norm/LM-head treatment exactly as F1
- greedy real M1 unknown-token generation
- normal Qwen chat template
- thinking disabled
- no drafter/speculation/oracle

No residency change is allowed.

## Workload

Use the exact first canonical REALGEN 001 prompt only, unchanged, to keep instrumentation overhead bounded.

Generate 32 unknown greedy tokens or EOS if earlier.

Before timed attribution, run a separate short exact-parity preflight against the existing F1/F0 token sequence. Instrumentation must not change generated token IDs.

## Host admission

Before each scientific process:
- system free >=60% on two consecutive passive samples;
- swap <=5600 MB;
- passive recovery only;
- no purge/cache flush/process killing/swap manipulation.

## Measurement strategy

Instrumentation must be fail-open and as low-overhead as practical. Use monotonic high-resolution timers. Do not insert global `mx.synchronize()` calls merely to make categories convenient unless a synchronization already exists at the same semantic boundary; extra synchronization would alter the system being measured.

Where MLX is asynchronous, distinguish:
- host enqueue/setup wall;
- synchronization/materialization wall at existing required boundaries.

Do not claim device-kernel duration from host timing unless directly measured by a valid installed profiler.

### Required boundaries

For every generated token and every streamed stage/group where feasible, capture:

- source access begin/end;
- tensor/parameter reconstruction begin/end;
- required materialization/evaluation begin/end;
- streamed-stage forward begin/end;
- cleanup/release begin/end;
- logical bytes handled;
- process-read delta around source-access window as diagnostic;
- MLX active/cache before and after stage group where nonintrusive.

Also measure total token wall and residual unclassified wall.

## Attribution categories

Report at minimum:

- `SOURCE_ACCESS_HOST_WALL`
- `TENSOR_RECONSTRUCTION_HOST_WALL`
- `MATERIALIZATION_SYNC_WALL`
- `STREAMED_FORWARD_WALL`
- `CLEANUP_ORCHESTRATION_WALL`
- `OTHER_UNCLASSIFIED_WALL`

If persistent-stage compute can be separately measured without changing execution semantics, report it as `PERSISTENT_FORWARD_WALL`; otherwise keep it inside residual and state that limitation.

No category may double-count time. If overlapping/asynchronous intervals prevent additive attribution, report overlapping intervals separately and do not force percentages to sum to 100%.

## Repetition

Run two fresh scientific F1 attribution processes after parity preflight.

Each run: same one prompt, 32 generated tokens/EOS.

Do not compare against a differently instrumented F0 for causal percentages. F0 may be measured once with only the same outer/token timer as a sanity reference, but the scientific target is decomposition of F1.

## Required outputs

Per run report:
- generated tokens and exact IDs;
- total generation wall and tok/s;
- per-token wall distribution;
- total/median/p95 per attribution category;
- category share of token wall only where non-overlapping/additive;
- logical streamed bytes/token;
- process-read bytes/token diagnostic;
- MLX peak active and minimum free;
- instrumentation overhead estimate if measurable.

Also report stage-level hotspots: which streamed stage/layer/shared stage consumes the most attributed wall.

## Bottleneck classification

Choose one evidence-based primary classification:

- `SOURCE_ACCESS_DOMINANT`
- `TENSOR_RECONSTRUCTION_DOMINANT`
- `MATERIALIZATION_SYNC_DOMINANT`
- `STREAMED_FORWARD_COMPUTE_DOMINANT`
- `MIXED_NO_SINGLE_DOMINANT`
- `ATTRIBUTION_UNRESOLVED`

A category is dominant only if it is the largest reproducible non-overlapping contributor and materially exceeds alternatives. Do not classify based on logical bytes alone.

## Classification

Use `STREAMING_ATTRIBUTION_001_COMPLETE` if both F1 runs are valid, exact parity is preserved, and enough attribution is measured to identify or explicitly rule out a dominant category.

Use `STREAMING_ATTRIBUTION_001_PARTIAL` if generation is valid but substantial wall remains unresolved.

Use `STREAMING_ATTRIBUTION_001_INFRASTRUCTURE_INCOMPLETE` only if instrumentation/harness prevents interpretable measurement.

## Forbidden

Do not implement or test:
- async prefetch;
- double/triple buffering;
- new chunk sizing;
- direct range-I/O redesign;
- mmap/pread redesign;
- compression/quantization changes;
- M>1 blocks;
- residency changes;
- capability reruns.

This experiment only measures.

## Evidence

Store raw evidence under:
`results-local/memory/streaming-attribution-001/<run-id>/`

At minimum:
- `summary.json`
- `parity.json`
- `attribution.json`
- `stage-hotspots.json`
- `host-admission.jsonl`
- `runs/`

## Pi boundary

Pi may inspect/adapt local instrumentation and run tests. Pi must not perform Git/HANDOFF/ROADMAP work and must not propose the next experiment.
