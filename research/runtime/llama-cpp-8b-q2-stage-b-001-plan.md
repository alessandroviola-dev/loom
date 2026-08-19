# LOOM — llama.cpp 8B Q2 Stage B 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Purpose

Complete the throughput portion of the Qwen3-8B Q2_K capability experiment without rerunning `llama-cli` Stage A.

Stage A launch/memory evidence is inherited from Capability 003 run `20260819-103347`, recorded in `research/runtime/llama-cpp-8b-q2-003-recovered-stage-a.md`.

This continuation exists because Capability 003 completed inference and exited cleanly but its inherited harness incorrectly required captured stdout/stderr, while the CLI wrote visible terminal/TTY output outside those pipes.

## Frozen runtime/model condition

- Apple M1, 8 GB unified memory
- llama.cpp source commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- existing Release/Metal build
- model `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q2_K.gguf`
- expected SHA256 `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`
- quantization `Q2_K`
- requested GPU layers `-ngl -1`
- flash attention `auto`

## Stage A prerequisite

Do not rerun Stage A. Require the recorded Capability 003 evidence:
- exit code 0;
- no timeout;
- no guardrail abort;
- exact `-c 4096` command evidence;
- exact `-ngl -1` command evidence;
- single-turn evidence;
- same-run Metal device preflight evidence;
- minimum observed free memory 10%.

## Stage B workload

Run `llama-bench` exactly with:
- prompt processing: 512 tokens;
- generation: 128 tokens;
- repetitions: 3;
- JSON output;
- `-ngl -1`;
- `-fa auto`.

This workload matches the successful 4B Runtime Control 001 shape for descriptive throughput scaling.

## Guardrails

Preserve the established Q2/Q4/Q3 safety thresholds:
- abort child if observed free memory falls below 5%;
- abort child if swap exceeds 5600 MB;
- no retry with altered parameters in the same run.

## Required telemetry

Record:
- exact model SHA256;
- disk free before/after;
- `llama-bench --list-devices`;
- pp512 average/stddev t/s;
- tg128 average/stddev t/s;
- backend information;
- effective `n_gpu_layers` from benchmark JSON where available;
- wall time;
- peak process RSS;
- peak swap;
- minimum memory-free percentage;
- guardrail state.

## Classification

### FULL_PASS
- exact model hash PASS;
- benchmark exits 0;
- JSON parses;
- positive pp512 and tg128 throughput rows exist;
- Metal evidence exists;
- no timeout or guardrail breach.

### BENCH_FAIL
- Stage A recovered launch evidence remains valid, but Stage B fails, times out or breaches a guardrail.

No inference should be made about model quality from throughput alone.

## Decision after run

If FULL_PASS:
- freeze Q2 8B as a technically runnable profile;
- compare throughput/memory with 4B Q4;
- test actual quality/usefulness and Pi compatibility before calling it a practical upgrade.

If BENCH_FAIL:
- stop repeated Q2 harness repair;
- move to a separately preregistered memory/offload strategy or broader runtime comparison.
