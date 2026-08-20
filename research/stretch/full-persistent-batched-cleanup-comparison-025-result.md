# LOOM Stretch 025 — Full-Persistent Batched Transformer Cleanup — Result

Status: **COMPLETE PASS**

Run: `20260820-161317`

Classification:
`FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`

Run directory:
`results-local/stretch/full-persistent-batched-cleanup-comparison-025/20260820-161317`

## Frozen comparison

Balanced order:
`CONTROL -> BATCHED -> BATCHED -> CONTROL`

CONTROL:
- canonical M5/H36/full-weight-persistent Stretch 023 Fix1 path;
- transformer cleanup `gc.collect() -> mx.clear_cache() -> gc.collect()` after each of 36 transformer layers.

BATCHED:
- identical architecture/workload;
- removes all 36 per-layer transformer cleanup sequences;
- executes the same cleanup sequence exactly once after the 36-layer transformer body;
- shared-stage cleanup remains unchanged.

Frozen sources:
- CONTROL blob `120ad7be2f275559898bf636ca8e8fe039a56c60`;
- BATCHED blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`;
- balanced runner blob `5fa702d7236888a55b33031c832ce12c79c0e55a`.

Model/runtime/M5/H36/full persistence/KV/parity/I-O/resource gates were unchanged.

## Controlled performance result

- CONTROL pooled target-verification rate: `2.761599662127487 token/s`;
- BATCHED pooled target-verification rate: `10.667447997968917 token/s`;
- BATCHED/CONTROL rate ratio: `3.8627785715149265x`;
- controlled rate gain: **~+286.28%**.

Target-block wall:
- CONTROL median: `1.5667445 s`;
- BATCHED median: `0.464723 s`;
- BATCHED/CONTROL median wall ratio: `0.2966169659443515x`;
- median block wall reduction: **~70.34%**.

BATCHED one-per-body cleanup:
- mean cleanup wall: `0.060996 s` per target block.

## Resource telemetry

CONTROL:
- minimum observed free memory `17%`;
- peak swap `2484.94 MB`.

BATCHED:
- minimum observed free memory `23%`;
- peak swap `2535.12 MB`.

Disk free after run:
`35.668 GiB`.

Higher observed pooled rate:
`BATCHED`.

As always, a higher minimum-free percentage in one variant is host-state telemetry and is not evidence that the variant intrinsically consumes less RAM. Peak swap remained far below the inherited `5600 MB` abort threshold.

## Scientific interpretation

Stretch 024 measured mean per-target-block per-layer cleanup wall near `0.926893 s` on the explicitly profiled path. Stretch 025 now demonstrates causally that the cleanup schedule was a dominant framework bottleneck: changing only transformer cleanup from 36 times per pass to once per transformer body increased the balanced target-verification rate by `3.8628x` while preserving all inherited correctness/resource gates.

This is not a kernel improvement and does not change model arithmetic. It removes redundant framework cleanup work around already-persistent transformer modules.

Canonical operational architecture under frozen MLX 0.31.2 is therefore updated to:

**M5 + H36 + full raw-weight persistence + one transformer cleanup per body.**

This profile demonstrates `10.6674 token/s` within Stretch 025's balanced experiment, more than half of the project's approximate `20 token/s` interactive promotion target.

Do not compare this absolute `10.6674 token/s` causally against absolute values from separate experiments. The causal evidence is the within-Stretch-025 BATCHED/CONTROL ratio `3.8627785715x`.

## Next decision

Shared stages still retain their inherited cleanup schedule:
- embedding cleanup;
- final RMSNorm cleanup;
- LM-head cleanup;

in addition to the single transformer-body cleanup.

The next independent factor is therefore shared-stage cleanup consolidation while leaving the successful one-per-transformer-body cleanup untouched.

Stretch 026 should compare:
`BATCHED -> SHARED_BATCHED -> SHARED_BATCHED -> BATCHED`,
where SHARED_BATCHED changes only the three shared-stage cleanup sequences into one cleanup after LM head.
