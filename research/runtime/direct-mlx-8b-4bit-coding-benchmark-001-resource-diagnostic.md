# LOOM — Direct MLX 8B 4-bit Coding Benchmark 001 Resource Diagnostic

Date: 2026-08-19
Run: `20260819-133144`
Status: **DIAGNOSTIC CLOSED — HOST-STATE SENSITIVITY PLAUSIBLE**

## Source run

Canonical result:
`research/runtime/direct-mlx-8b-4bit-coding-benchmark-001.md`

Frozen profile:
- `mlx-community/Qwen3-8B-4bit`
- Direct MLX pinned environment
- Coding Benchmark 01 v1.0.1
- one loaded model session
- `max_kv_size=4096`
- unquantized KV
- max 2048 generated tokens/task
- free-memory abort <5%
- swap abort >5600 MB

The run was already correctly classified `PARTIAL_RESOURCE_FAIL`.

## Persisted diagnostic evidence

Summary:
- classification `PARTIAL_RESOURCE_FAIL`
- failure reason `memory free 4% < 5%`
- generated task count `0`
- written tasks `0`
- artifact score `None`
- delivery-adjusted score `None`
- preflight: 56% free / 948.75 MB swap
- peak sampled child RSS: 459.453125 MB
- peak observed swap: 3028.25 MB
- minimum observed free memory: 4%
- child exit `-15` after parent termination
- wall 17.913 s
- no stdout/stderr content
- progress remained `phase=running`, `current_task=T01`, `completed=[]`
- no persisted T01 result.

Therefore no response completed before the guardrail abort and no quality inference is valid.

## Memory timeline

Observed samples:

| t (s) | free | swap MB | child RSS MB | phase |
|---:|---:|---:|---:|---|
| 0.002 | 55% | 948.75 | 0.03 | pre-progress |
| 1.030 | 58% | 948.75 | 80.73 | pre-progress |
| 2.047 | 54% | 948.75 | 459.45 | pre-progress |
| 3.070 | 13% | 1387.75 | 178.08 | pre-progress |
| 4.728 | 13% | 1875.44 | 191.92 | pre-progress |
| 5.856 | 18% | 2516.25 | 229.09 | T01 running |
| 6.881 | 22% | 3028.25 | 229.41 | T01 running |
| 7.898 | 20% | 2836.69 | 229.41 | T01 running |
| 8.934 | 20% | 2655.50 | 200.73 | T01 running |
| 10.023 | 16% | 2477.06 | 134.97 | T01 running |
| 11.043 | 14% | 2606.56 | 40.83 | T01 running |
| 12.069 | 12% | 2526.00 | 34.70 | T01 running |
| 13.087 | 11% | 2472.38 | 34.70 | T01 running |
| 14.109 | 11% | 2270.56 | 33.66 | T01 running |
| 15.175 | 9% | 2092.81 | 33.52 | T01 running |
| 16.199 | 6% | 1991.19 | 32.84 | T01 running |
| 17.403 | **4%** | 1977.56 | 29.91 | T01 running |

The maximum-swap sample occurred much earlier than the minimum-free sample. Swap was decreasing when free memory crossed the guardrail. The failure is therefore not a swap-threshold event.

## Comparison with successful runs

Successful standalone 4-bit T01 `20260819-132612`:
- preflight **74% free / 1395.25 MB swap**
- minimum free **6%**
- FULL_PASS.

Completed 3-bit full benchmark `20260819-125647`:
- preflight **75% free / 1339.00 MB swap**
- minimum free **14%**
- COMPLETE.

Failed 4-bit full benchmark `20260819-133144`:
- preflight **56% free / 948.75 MB swap**
- minimum free **4%**
- PARTIAL_RESOURCE_FAIL.

The 18–19 percentage-point free-memory preflight difference is a material uncontrolled host-state difference between the failed run and the two closest successful Direct MLX references. The evidence does not prove that host state caused the failure, but it makes host-state sensitivity a plausible explanation worth one controlled replication before changing the runtime profile.

## Mechanistic boundary

What the evidence supports:
- the exact original full-run condition failed genuinely during T01 processing;
- no T01 response completed;
- free memory, not swap, triggered the abort;
- the failed run began from substantially lower system free-memory state than the closest successful references.

What the evidence does **not** support:
- that 4-bit is globally impossible on 8 GB;
- that KV precision caused the failure;
- that model weights alone caused the failure;
- that the child RSS measures total unified-memory footprint;
- that a repeated run would necessarily pass.

## Decision

Authorize exactly one separately preregistered **host-state-controlled replication** before any KV-precision rescue.

The model/runtime/benchmark/safety condition remains unchanged. The only added launch eligibility condition is that system free memory must be at least 70% for three consecutive preflight samples before MLX starts.

This is not a retroactive reclassification of run `20260819-133144`; that run remains a valid `PARTIAL_RESOURCE_FAIL`.

If the controlled replication launches and again hits the <5% free-memory guardrail, close the 4-bit / unquantized-KV / 4096 full-session branch and do not repeat the same condition again.
