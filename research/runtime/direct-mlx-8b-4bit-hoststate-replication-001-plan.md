# LOOM — Direct MLX 8B 4-bit Host-State Controlled Replication 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Does the previously failed Direct MLX Qwen3-8B 4-bit full Coding Benchmark 01 remain outside LOOM's safety boundary when launched from a host free-memory state comparable to the successful Direct MLX references?

This is a **host-state-controlled replication**, not a runtime rescue.

## Motivation

Original 4-bit full benchmark run `20260819-133144`:
- preflight free memory 56%
- guardrail abort at 4% during T01
- no completed task result.

Successful 4-bit standalone T01 `20260819-132612`:
- preflight free memory 74%
- minimum free 6%
- FULL_PASS.

Completed 3-bit full benchmark `20260819-125647`:
- preflight free memory 75%
- minimum free 14%
- COMPLETE.

The lower initial host free-memory state in the failed run is a material uncontrolled difference. One controlled replication is justified before changing KV precision or any model/runtime parameter.

## Frozen model/runtime/benchmark condition

Reuse exactly:
`scripts/direct_mlx_8b_4bit_coding_benchmark_001.py`

Required Git blob:
`541e23ef5a824a29f3f67e162e48228b2ccabb14`

Therefore retain without modification:
- model `mlx-community/Qwen3-8B-4bit`
- verified 4-bit artifact and SHA
- pinned Direct MLX environment
- Coding Benchmark 01 v1.0.1 T01–T06
- exact adapter/scorer blobs
- exact prompts/parser/scorer
- one loaded model process for all six tasks
- local/offline inference
- `enable_thinking=False`
- `max_kv_size=4096`
- unquantized KV
- max 2048 generated tokens/task
- seed 0
- no retries/repair/salvage/test feedback
- runtime abort free memory <5% OR swap >5600 MB.

## New prospective host-state launch gate

Before launching the frozen benchmark runner, sample `memory_pressure` once per second.

MLX may start only if **three consecutive samples are each >=70% system-wide free memory**.

No memory purge, cache purge, swap purge, process killing, or automated system manipulation is performed by the runner.

If the three-sample requirement is not met immediately:
- classification: `HOST_STATE_NOT_READY`
- do not launch MLX
- do not classify model/runtime capability.

The user may later retry the wrapper after naturally freeing host resources; attempts that never launch MLX are not model repetitions.

The existing 5600 MB swap guardrail remains unchanged. No additional prelaunch swap threshold is introduced because the failed run began with lower swap than the successful references; free-memory state is the specific controlled variable.

## Replication identity / provenance

Wrapper:
`scripts/direct_mlx_8b_4bit_hoststate_replication_001.py`

The wrapper must:
1. verify the exact frozen full-runner blob;
2. record the three prelaunch free-memory samples and current swap/disk state under `results-local/mlx/8b-4bit-hoststate-replication-001/`;
3. if eligible, replace itself with the frozen full benchmark process via `os.execv`, so the wrapper does not remain resident during MLX execution;
4. make no source/runtime transformation.

The benchmark's own output directory remains the canonical 4-bit benchmark directory. The host-state preflight record and terminal timestamps establish the replication provenance.

## Interpretation

If host state is not ready:
- no MLX launch;
- no capability result.

If MLX launches and the frozen benchmark again hits a resource guardrail:
- classify the controlled replication as resource fail;
- close the 4-bit / unquantized-KV / 4096 full-session branch;
- do not repeat the same profile again.

If MLX launches and completes:
- freeze the COMPLETE result;
- apply the already-preregistered quality gate from the original 4-bit benchmark plan:
  - delivery-adjusted >27.86/100
  - structured delivery >2/6
- only if both improve may the profile become eligible for a later isolated Pi validation.

A completed controlled replication does not erase the original `PARTIAL_RESOURCE_FAIL`; both results remain canonical evidence of host-state sensitivity.

## Prohibited changes

Do not:
- lower the 5% free-memory guardrail;
- change the 5600 MB swap guardrail;
- change `max_kv_size`;
- quantize KV;
- alter prompts/parser/scorer;
- cold-restart between tasks;
- retry an individual task;
- automate memory purging.
