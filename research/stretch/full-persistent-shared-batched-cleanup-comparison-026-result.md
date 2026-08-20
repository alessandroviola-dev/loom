# Stretch 026 — Full-Persistent Shared-Stage Batched Cleanup — Result

Date: 2026-08-20
Run: `20260820-162951`
Classification: `FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`

## Question

With the successful Stretch 025 transformer cleanup schedule already frozen at one cleanup per 36-layer body, does consolidating the three persistent shared-stage cleanup points (embedding, final RMSNorm, LM head) into one cleanup after LM head improve exact M5 target verification?

## Frozen architecture

- Qwen3-8B 3-bit/group64
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- M=5 exact oracle target block
- H36 transformer residency
- all raw model weights persistent: `3,583,928,320 B`
- ordinary BF16 KV
- transformer cleanup once per body in both variants
- exact numerical/top-1, I/O and resource gates unchanged
- no deliberate cache purge

## Balanced order

`BATCHED -> SHARED_BATCHED -> SHARED_BATCHED -> BATCHED`

Sources:
- BATCHED baseline: `scripts/stretch_full_persistent_batched_cleanup_025.py`
  - blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`
- SHARED_BATCHED treatment: `scripts/stretch_full_persistent_shared_batched_cleanup_026.py`
  - blob `6926e1b1b9a851f23d88ba6b1f1023e13336098a`
- balanced runner: `scripts/stretch_full_persistent_shared_batched_cleanup_comparison_026.py`
  - blob `e958bde5d8a239ffa5fd192922e0693854d478e0`

## Controlled result

- BATCHED pooled target verification: `11.1287398593995 token/s`
- SHARED_BATCHED pooled target verification: `12.69867607836099 token/s`
- SHARED_BATCHED/BATCHED rate ratio: `1.1410704391329174x`
- controlled rate gain: **+14.1070%**

Target block wall:
- BATCHED median: `0.4502915 s`
- SHARED_BATCHED median: `0.399913 s`
- wall ratio: `0.8881202509929678x`
- controlled median wall reduction: **11.1880%**

Cleanup telemetry:
- BATCHED mean transformer-body cleanup: `0.05014766666666667 s/block`
- SHARED_BATCHED mean transformer-body cleanup: `0.047733333333333336 s/block`
- SHARED_BATCHED mean one-per-shared-path cleanup: `0.031349 s/block`

Resource telemetry:
- BATCHED minimum observed free memory: `19%`
- SHARED_BATCHED minimum observed free memory: `25%`
- BATCHED peak swap: `2422.94 MB`
- SHARED_BATCHED peak swap: `2465.75 MB`
- disk free after run: ~`35.655 GiB`

The free-memory difference is host-state telemetry and is not evidence that SHARED_BATCHED intrinsically consumes less RAM. Both variants remained well inside the frozen swap/resource limits.

## Interpretation

The result confirms that cleanup scheduling remained a material framework cost even after Stretch 025. Consolidating embedding/norm/head cleanup from three calls to one produced a further controlled **+14.11%** target-rate gain while preserving all inherited gates.

Canonical target-side schedule is now:

- M5 exact block
- H36 transformer residency
- full raw-weight persistence
- one cleanup after the transformer body
- one cleanup after the complete shared path (after LM head)

The raw-weight residency axis remains closed. The framework-cleanup axis is not yet fully closed because two cleanup points remain per pass. A final controlled consolidation from two cleanup points to one end-of-pass cleanup is justified before returning to MLP/attention/kernel work.

Absolute token/s values from separate experiments must not be compared causally. The scientific evidence here is the within-run balanced ratio `1.1410704391329174x`.
