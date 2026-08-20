# LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution — Result

Status: **COMPLETE PASS**

Classification:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`

Valid run:
`20260820-160140`

Run directory:
`results-local/stretch/full-persistent-compute-kernel-attribution-024-fix2/20260820-160140`

Summary:
`results-local/stretch/full-persistent-compute-kernel-attribution-024-fix2/20260820-160140/summary.json`

## Preserved harness history

The earlier sequence `20260820-155313` remains frozen as **HARNESS / TELEMETRY DEFECT — NO SCIENTIFIC RESULT**. Its parent-side aggregation used child-local `args.num_hidden_layers` and terminated with:

`compute attribution incomplete: NameError: name 'args' is not defined`

It is not reused in the valid ABBA result.

Fix2 preserved the scientific design and changed only those parent-side geometry references to the already-frozen H36 geometry `len(HOTSET_LAYER_IDS)`.

## Frozen architecture

- Qwen3-8B 3-bit/group64
- MLX `0.31.2`
- mlx-lm `0.31.3`
- transformers `5.12.1`
- exact oracle target block `M=5`
- transformer residency `H36`
- all raw model weights persistent
- persistent raw model payload `3,583,928,320 B`
- ordinary BF16 KV
- exact inherited numerical/top-1/resource gates
- no deliberate cache purge
- no drafter/runtime/KV/quantization change.

CONTROL:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

PROFILED fix2:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled_fix2.py`
- blob `83f9e12dfa30445810ca4d39150dbcd151ad3e66`.

Balanced runner fix2:
- `scripts/stretch_full_persistent_compute_kernel_attribution_024_fix2.py`
- blob `de464c4fe5dca90c2fe110337f12e3f6424ea937`.

Balanced order:
`CONTROL -> PROFILED -> PROFILED -> CONTROL`.

## Valid result

All four constituent runs passed their inherited correctness/resource gates and the PROFILED attribution gates.

Instrumentation perturbation telemetry:
- CONTROL pooled target verification: `2.6093073645786875 token/s`
- PROFILED pooled target verification: `2.644128118583858 token/s`
- PROFILED/CONTROL rate ratio: `1.0133448264768887x`
- CONTROL median target-block wall: `1.8803645 s`
- PROFILED median target-block wall: `1.656948 s`.

The PROFILED/CONTROL throughput difference is **not** an optimization result. PROFILED inserts explicit `mx.eval` synchronization boundaries; its absolute rate is used only to check that profiling perturbation is bounded and host-state dependent.

Synchronized transformer compute per target block:
- total profiled transformer compute: `0.808182682027109 s`
- attention path: `0.22076561170009276 s`
- MLP path: `0.5874170703270162 s`
- MLP/attention ratio: `2.6608178049261344x`.

Mean synchronized component time per target block:
- `up_proj`: `0.1888043609020921 s` (~23.36% of profiled transformer compute)
- `gate_proj`: `0.18782552768243477 s` (~23.24%)
- attention: `0.1838260839964884 s` (~22.75%)
- `down_proj`: `0.17950852166783685 s` (~22.21%)
- input RMSNorm: `0.025495859891331445 s` (~3.15%)
- SwiGLU: `0.01459458990332981 s` (~1.81%)
- residual 1: `0.011443667812272906 s` (~1.42%)
- residual 2: `0.009162834185796479 s` (~1.13%)
- post-attention RMSNorm: `0.007521235985526194 s` (~0.93%).

Framework/cleanup attribution:
- mean per-layer cleanup summed over a target block: `0.9268928333333333 s`
- mean shared forward: `0.05525783333333333 s`
- mean residual unattributed: `0.09952548463955764 s`
- accounted share of PROFILED full wall: `0.947368373509772` (~94.74%).

The measured cleanup sum is approximately `1.1469x` the synchronized transformer-compute total. It is therefore the largest measured remaining target-side cost category under full-weight persistence.

Slowest profiled layer candidates in this run:
- layer 11: `0.036501791910268366 s`
- layer 3: `0.03557208327886959 s`
- layer 12: `0.033553207758814096 s`
- layer 19: `0.03239640302490443 s`
- layer 13: `0.03222312514359752 s`
- layer 21: `0.03217937428659449 s`
- layer 23: `0.0262430344397823 s`
- layer 10: `0.025614805325555306 s`.

Resource telemetry:
- CONTROL minimum observed free memory: `19%`
- PROFILED minimum observed free memory: `24%`
- CONTROL peak swap: `2394.75 MB`
- PROFILED peak swap: `2439.38 MB`
- disk free after: `~35.674 GiB`.

Do not interpret the higher PROFILED minimum-free percentage as lower intrinsic memory usage. Host state differs; the experiment's scientific output is attribution, not a claim that instrumentation improves memory or throughput.

## Canonical interpretation

1. Raw-weight residency is already closed by Stretch 023; Stretch 024 confirms that remaining wall is primarily framework cleanup plus actual transformer compute.
2. The largest measured category is the current **per-layer cleanup path** (`gc.collect()` / `mx.clear_cache()` around every persistent transformer layer), not any individual mathematical kernel.
3. Within actual transformer compute, MLP dominates attention by `~2.66x`, but gate/up/attention/down are individually close in size.
4. Because H36/full persistence no longer creates or evicts transformer weights per layer, the scientific next factor should test whether 36 per-layer cleanup cycles are still necessary.
5. Kernel/runtime work should follow only after cleanup/framework overhead is controlled; otherwise a major non-compute cost remains mixed into target wall.

## Decision

Freeze Stretch 024 as the bottleneck map for the canonical MLX 0.31.2 architecture.

Next experiment: Stretch 025 — controlled cleanup-schedule comparison under unchanged M5 + H36 + full-weight persistence. Compare canonical per-layer cleanup against one batched transformer-body cleanup per pass. Preserve exact correctness/resource gates and use a fresh balanced ABBA sequence.
