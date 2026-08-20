# Stretch 038 — S1_R8 deferred cleanup cadence feasibility

Date: 2026-08-20  
Status: **GO for preregistration only; no scientific ABBA was run.**

## Scope and frozen path

The promoted Stretch 037 path was retained: Qwen3-8B, affine 3-bit/group64,
BF16, MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1, M5, H36,
full raw-weight persistence, BF16 KV, and process-local M1-specific S1_R8
custom qmv. No qmv source, specialization, quantization, model, oracle or
resource threshold changed. The rendered treatment source compiles and uses
one child/model-load process. It runs the inherited control warmup followed by
an interleaved feasibility schedule of four CONTROL and eight TREATMENT cycles.

Evidence: `results-local/stretch/s1r8-deferred-cleanup-038-feasibility/20260820-222911/summary.json`.

### Preserved harness-only attempts

The distinct generated-harness revisions at `20260820-222529`, `222610`,
`222714`, and `222805` stopped on, respectively, a pre-child import path,
cleanup-control scope, warmup-result ordering, and localized swap-telemetry
parsing. They are retained in the evidence root. None reached a treatment
diagnostic cycle; none is scientific evidence or was reused. The final source
revision was committed/pushed and source-compiled before the complete run.

## Exact cleanup audit

The current final cleanup is the `shared_stage_cleanup` in the rendered
Stretch-037 S1_R8 target's `run_streamed_pass()`, after the persistent LM-head
forward/evaluation and before the pass returns its logits. The code is exactly:

```python
gc.collect()
mx.clear_cache()
gc.collect()
```

Its policy is `single_cleanup_after_full_pass`. Stretch 027 removed the former
post-transformer-body cleanup, leaving this one final full-pass cleanup.
Therefore the actual promoted cadence is **one cleanup per M5 target block**,
not one cleanup per 10-token/two-block constituent:

| Unit | Explicit final cleanup calls |
|---|---:|
| M5 target block | 1 |
| 10 accepted tokens | 2 |
| Stretch-037 constituent (two M5 blocks) | 2 |

The fresh Stretch-037 S1_R8 ABBA telemetry recorded individual target cleanup
walls of `0.043282`, `0.051428`, `0.046600`, and `0.040986 s`: mean
`0.045574 s/block`, or its reported pooled `0.00911480 s/token`.

The cleanup's explicit effects are Python garbage collection and the public
MLX cache-clear call. It is after temporary activation/logit references have
been deleted by the pass caller. It does **not** remove the persistent H36
block/shared-weight dictionaries: the successful one-load run retained
`3,583,928,320 B` of raw weights. It does not construct, replace or call a
kernel factory, Metal command API, or model-weight mutation API. MLX does not
expose a public command-state/kernel-invalidation counter; the source proves
no direct such operation and Stretch 037 established zero target-time custom
kernel recompilations. Active-memory telemetry around this cleanup was zero
or returned to its stable baseline; cache telemetry is recorded below.

This audit makes the requested cadence factor real and available.

## Feasibility definitions

- **CONTROL:** S1_R8; block 1 -> final cleanup -> block 2 -> final cleanup:
  2 cleanup calls / 10 accepted tokens.
- **TREATMENT:** identical S1_R8; block 1 -> no explicit cleanup -> block 2
  -> one final cleanup: 1 cleanup call / 10 accepted tokens.

The inherited exact CONTROL is a separate warmup. Timed feasibility cycles
were interleaved `C, T, T, C, T, T, C, T, T, C, T, T`; this deliberately is
not a scientific ABBA.

## Correctness and persistence

The inherited warmup passed all original gates. Every timed cycle (4 CONTROL,
8 TREATMENT) passed prompt and all ten target logit checks with max and mean
absolute difference `0`, top-1 equality, exact oracle acceptance (`10/10`),
and generated-sequence equality. The final cleanup executed in every cycle.
Full raw-weight persistence remained `3,583,928,320 B`.

## Resource trajectory

All eight treatment cycles completed; no abort gate fired. Across treatment
cycles 2/3/5/6/8/9/11/12, the four snapshots were stable:

| Point | Free memory | Swap MB | MLX active B | MLX peak B | MLX cache B |
|---|---:|---:|---:|---:|---:|
| before block 1 | 24–25% | 1849.06 | 3,665,291,272 | 3,671,402,528 | 0 |
| after block 1, before block 2 | 24–25% | 1849.06 | 3,665,291,272 | 3,671,402,528 | 3,513,120 |
| after block 2, before final cleanup | 24–25% | 1849.06 | 3,666,913,308 | 3,671,402,528 | 1,891,084 |
| after final cleanup | 24–25% | 1849.06 | 3,665,291,272 | 3,671,402,528 | 2,867,748–2,868,260 |

Thus the final cleanup recovered active memory to the exact pre-block stable
value and cache to a stable post-cleanup band. The temporary cache increase
before block 2 was not cumulative across the eight cycles. Minimum free
memory was `24%`; peak swap was `1849.06 MB` (well inside the `<5%` / `>5600
MB` abort gates).

## Timing

Means across the timed cycles:

| Metric | CONTROL (n=4) | TREATMENT (n=8) |
|---|---:|---:|
| block-1 compute wall | 0.286230 s | 0.287470 s |
| no-cleanup transition | 0.000000105 s | 0.000000146 s |
| block-2 compute wall | 0.291833 s | 0.297485 s |
| final-cleanup wall/cycle | 0.126737 s | 0.062129 s |
| total 10-token wall | 0.704799 s | 0.647084 s |
| derived target tok/s | 14.188437 | 15.453956 |

Treatment/control wall ratio is `0.91811037`; measured wall improvement is
**8.188963%**. The one-call reduction lowers cleanup wall by `0.064607 s` per
10-token cycle (`50.98%` of CONTROL cleanup wall). This is a feasibility
measurement, not a replacement for Stretch 037's validated 15.0026817294
tok/s or a scientific effect estimate.

## Decision

`STRETCH_038_CLEANUP_CADENCE_FEASIBILITY_GO`.

All GO conditions are satisfied: strict correctness, eight stable treatment
cycles, final cleanup recovery, gain >=5%, compatible host resources, and
unchanged S1_R8 numerical gates. Do **not** run an ABBA from this result. The
next permitted action is the separate preregistered scientific comparison in
`s1r8-deferred-cleanup-038-preregistration.md`.
