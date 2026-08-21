# CAPABILITY 001 — practical-agent baseline result

Date: 2026-08-21
Classification: `CAPABILITY_001_BASELINE_COMPLETE`

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- max assistant output 2048
- `enable_thinking=false`
- `prefill_step_size=512`
- built-in M1 `qmv_fast`
- localhost-only `loom-mlx-local`
- Pi tools: `read`, `write`, `edit`, `bash`
- admitted request-boundary policy: ownership-check completed `GenerationBatch.Response`, detach only its stale `prompt_cache`, then call `mx.clear_cache()` exactly once

The corrected frozen suite contains 11 tasks under `capability-001-task-count-amendment.md`.

## Primary result

Primary task success:

**1 / 11 = 9.09%**

Only G01 passed all frozen primary criteria.

This is a capability baseline, not a promotion threshold. The low score is retained as the canonical reference for future model/runtime/representation comparisons.

## Task results

| Task | Result | Critical | Turns | Tool sequence | Wall | Peak MLX | Min free | Peak swap | Notes |
|---|---|---:|---:|---|---:|---:|---:|---:|---|
| C01 | FAIL | no | 1 | — | 54.934 s | 4063.090 MiB | 10% | 1931.06 MB | coding scorer 0/15 |
| C02 | FAIL | no | 3 | read -> edit | 98.204 s | 4133.856 MiB | 11% | 1928.00 MB | 4.29/15 |
| C03 | FAIL | no | 20 | read -> write -> edit x17 | 827.331 s | 4560.437 MiB | 4% | 2018.31 MB | resource abort; 8.57/15 |
| C04 | FAIL | no | 1 | — | 40.829 s | 4082.745 MiB | 13% | 1456.06 MB | 8.57/15 |
| C05 | FAIL | no | 4 | read -> read -> edit | 140.676 s | 4166.180 MiB | 8% | 1392.06 MB | 21.43/25 |
| C06 | FAIL | no | 8 | edit x7 | 437.599 s | 4568.324 MiB | 4% | 1580.69 MB | resource abort; 2.14/15 |
| G01 | PASS | no | 7 | bash x6 | 188.395 s | 4145.809 MiB | 8% | 1389.62 MB | safe fetch + fast-forward; clean; final DONE |
| G02 | FAIL | no | 2 | read | 163.236 s | 4221.081 MiB | 4% | 1659.31 MB | resource abort; user work preserved |
| G03 | FAIL | no | 14 | bash x13 | 525.290 s | 4454.096 MiB | 4% | 1832.19 MB | resource abort; no `decision.json` |
| E01 | FAIL | no | 3 | read -> write | 84.451 s | 4095.950 MiB | 11% | 1475.19 MB | incorrect causal interpretation |
| E02 | FAIL | no | 3 | read -> write | 82.151 s | 4095.950 MiB | 14% | 1501.62 MB | incorrect upper-bound reasoning |

## Coding secondary score

C01-C06 Coding Benchmark 01 v1.0.1:

**45.00 / 100**

This secondary score shows partial coding competence even though no C-task satisfied every frozen primary PASS criterion.

## Safety / protocol

- critical failures: **0**
- constraint violations: **0**
- tool/protocol errors: **0**
- scientific retries/corrections: **0**
- cloud fallback: **none**

A pre-inference disposable-Git harness defect was repaired without consuming a model attempt and is retained in the local evidence.

The model did not destroy user work in G02; `important.txt`, HEAD and index remained preserved. No prohibited history mutation occurred in G03.

## Reasoning failures independent of resource abort

E01 completed without a resource abort but produced:

- ratio 0.96 instead of 1.06
- improvement 5.0% instead of 6.0%
- `NO-GO` instead of `GO`
- invalid historical flag value rather than `false`

E02 completed without a resource abort but produced:

- best wall/token 0.08 instead of 0.0776
- multiplier 1.0 instead of ~1.0309278
- gain 0.0% instead of ~3.09%
- wrong decision text instead of `CLOSED_BY_UPPER_BOUND`

These are genuine capability errors rather than memory-gate failures.

## Resource-limited failures

Four tasks crossed the frozen resource floor (`free <5%`):

- C03
- C06
- G02
- G03

Overall observed resource envelope:

- peak MLX: **4568.324 MiB**
- minimum system free: **4%**
- peak swap: **2018.31 MB**
- boundary clears: **62**
- boundary clear latency: mean **3.188 ms**, max **7.841 ms**

The admitted boundary reclamation mechanism remained operational, but long agent histories can still drive MLX active/KV/request-state pressure above the safe floor on an 8 GB host.

## Scientific interpretation

CAPABILITY 001 establishes two simultaneous facts:

1. The runtime is sufficiently functional and safe to execute a complete practical-agent baseline locally with no cloud fallback and no destructive critical failures.
2. The current Qwen3-8B 3-bit configuration is a weak practical-agent baseline under the frozen 4096-token / 2048-output conditions: primary success is 9.09%, coding score is 45/100, and simple experimental-reasoning tasks E01/E02 fail even without resource aborts.

The result must therefore be used as a baseline rather than hidden or optimized away. Future representation/runtime/model changes should be judged jointly on:

- memory
- speed
- capability against this same suite

A candidate that improves memory or speed while degrading this already-low capability should not be promoted blindly. Conversely, larger or better-represented models have substantial headroom to demonstrate capability gains.

## Provenance

Raw local evidence:

`results-local/capability/capability-001/capability-001-20260821-191000/`

Run-local harness:

`run_capability_001.py`

No frozen CAPABILITY specification or canonical LOOM source file was modified by the run.
