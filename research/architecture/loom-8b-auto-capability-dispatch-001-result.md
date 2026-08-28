# LOOM 8B Auto Capability Dispatch 001 — Result

Date: 2026-08-28
Status: **NO_GO / INVALID FOR QUALITY OR PERFORMANCE**
Classification: **`LOOM_8B_AUTO_CAPABILITY_DISPATCH_NO_GO`**

## Result

The frozen end-to-end RAW8 vs AUTO8 checkpoint did not produce usable scientific evidence.

All `18/18` child conditions reached model inference but then ended as `MECHANICAL_FAILURE` while the experimental harness was building cleanup evidence. The reported exception was:

`TypeError: object of type 'int' has no len()`

Because the harness failed before persisting the generated outputs, selector decisions, timings and post-run evidence, **0/18 conditions satisfy the preregistered validity requirement**.

No correctness, utility, selector, latency or throughput conclusion may be drawn from this run.

## Provenance that did pass before each child

8B runtime/model:
- `mlx-community/Qwen3-8B-3bit@619ded3`;
- main weight SHA-256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- quantization `3-bit/group64`;
- MLX/mlx-metal `0.31.2`;
- mlx-lm `0.31.3`;
- transformers `5.12.1`;
- offline flags enabled.

Selector source SHA matched frozen v0:
`5ccaae77862ceb60700115487ea4db5e5bdcae330d8dcb7583d3186e6521887d`.

Failed experimental harness:
`scripts/loom_8b_auto_capability_dispatch_001.py`
SHA-256:
`a0346835bd927add1309ac800a9ae5c1fbffff25cb0f2307737186b526f9c460`.

Attributable local changed file: only that harness. No Git commit/push.

## Evidence

`results-local/research/8b-auto-capability-dispatch-001/20260828T164106Z/`

The evidence contains 18 per-condition mechanical-failure records and `summary.json`.

Unavailable due to failure:
- generated outputs;
- selector labels/walls;
- correctness/utility scores;
- TTFT/generation/end-to-end metrics;
- post-run memory evidence.

No inference processes remained after the run.

## Scientific interpretation

This is a **harness/instrumentation failure**, not evidence that Capability Selector v0, strict-output, verification-first or the 8B runtime failed.

The frozen GO gate failed immediately on the required `18/18` valid conditions. The original checkpoint remains closed `NO_GO`; it must not be silently repaired and reclassified.

No forbidden model tier, network, tool, retry, runtime mutation or integration was used.

## Authorized next action

Open a separate mechanical `FIX1` checkpoint.

Only the cleanup-evidence type handling at the observed traceback site may change. The failed harness must remain untouched for provenance; create a separate fix1 harness. Before any new model inference, prove the cleanup-evidence fix with local synthetic/no-model checks.

Prompts, selector rules/source, protocol strings, 8B runtime, execution order, output caps, scoring and GO gate remain unchanged.

If a second independent harness defect prevents valid evidence during FIX1, stop rather than opening another incremental patch in the same checkpoint.