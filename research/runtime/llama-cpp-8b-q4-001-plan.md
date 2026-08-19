# LOOM — llama.cpp 8B Q4 Capability 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — DISK PREFLIGHT PASS / RUNNER READY**

## Research question

Can the reference Apple M1 / 8 GB machine run an official 8B-class Q4_K_M GGUF usefully with the pinned llama.cpp Metal build at context 4096, and what are the resulting throughput and memory-pressure tradeoffs?

This is the first Phase 4 experiment directly aligned with LOOM's **Big models. Small machines.** objective.

## Frozen runtime

- Machine: Apple M1, 8 GB unified memory
- llama.cpp source commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- Existing canonical Metal build under `results-local/llama-cpp/source-60addddf3c56/build-loom-metal`
- `GGML_METAL=ON`
- embedded Metal library enabled

## Frozen model artifact

Official repository:
- `Qwen/Qwen3-8B-GGUF`

File:
- `Qwen3-8B-Q4_K_M.gguf`

Quantization:
- `Q4_K_M`

Published remote size:
- `5,027,783,488` bytes (about 5.03 GB decimal / 4.68 GiB)

Expected SHA256:
- `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`

The runner must verify the complete SHA256 before inference.

## Why the sequence differs from the 4B control

The validated 4B control reported:
- model file 2.326 GiB;
- Metal device approximately 5460 MiB free;
- recommended Metal max working set 5726.63 MB;
- pp512 230.85 t/s;
- tg128 22.33 t/s;
- peak process RSS 1914.91 MB;
- minimum memory-free percentage 22%.

The 8B Q4 artifact is much closer to the observed Metal working-set frontier. Therefore Capability 001 uses a staged sequence instead of jumping directly to the full benchmark.

## Storage guardrail

Before running the new 8B runner, manually record:

```bash
df -h /
du -sh results-local/models results-local/llama-cpp 2>/dev/null
```

The runner independently records disk free before and after the experiment.

For a fresh 8B download, require **at least 12 GiB free** before starting. This leaves room for the approximately 4.68 GiB model, temporary/resumable download state, swap growth and normal macOS operation.

Do not silently delete the verified 4B model or prior results to satisfy this guard.

### Disk preflight — PASS

Observed on the reference Mac before the 8B run:

```text
Filesystem        Size    Used   Avail Capacity  Mounted on
/dev/disk3s1s1   228Gi    12Gi    56Gi    18%   /

2.3G  results-local/models
415M  results-local/llama-cpp
```

Classification:
- free disk: **56 GiB**
- required minimum: **12 GiB**
- model storage currently: **2.3 GiB**
- llama.cpp source/build/results currently: **415 MiB**
- storage gate: **PASS**

No cleanup is required before Capability 001.

## Stage A — context-4096 launch smoke

After verified download:

1. stop the canonical Ollama model if available;
2. launch `llama-cli` using the 8B GGUF;
3. request maximum Metal offload (`-ngl -1`);
4. force `--ctx-size 4096`;
5. use a tiny deterministic prompt and generate only 8 tokens;
6. capture stdout/stderr, wall time, process RSS, swap and memory pressure.

Stage A is successful only if:
- process exits cleanly;
- no timeout;
- Metal evidence exists;
- context 4096 is accepted;
- output is non-empty;
- memory guardrails are not breached.

## Runtime memory guardrails

During Stage A and Stage B:
- sample process RSS and swap approximately once per second;
- sample memory-pressure free percentage;
- abort the active child process if observed free memory falls below **5%**;
- abort if observed swap usage exceeds **5600 MB**;
- classify a guardrail abort explicitly; do not retry automatically with altered parameters.

These thresholds are experiment-safety controls, not claims about macOS hard limits.

## Stage B — throughput benchmark

Stage B runs only after Stage A succeeds.

Use `llama-bench` with:
- same verified model;
- `-ngl -1`;
- flash attention `auto`;
- prompt processing 512 tokens;
- text generation 128 tokens;
- 3 repetitions;
- JSON output.

Capture:
- pp512 average/stddev t/s;
- tg128 average/stddev t/s;
- backend/device evidence;
- effective `n_gpu_layers`;
- wall time;
- peak RSS;
- peak swap;
- minimum memory-free percentage.

The benchmark workload intentionally matches the validated 4B runtime control for descriptive scaling comparison.

## Success classification

### FULL_PASS
- artifact hash PASS;
- Stage A context-4096 smoke PASS;
- Stage B benchmark PASS;
- Metal evidence present;
- no memory guardrail breach.

### LAUNCH_PASS_BENCH_FAIL
- Stage A succeeds at context 4096;
- Stage B fails or hits a guardrail.

This still proves basic 8B launchability but not useful benchmark stability.

### FAIL
- hash mismatch;
- Stage A cannot load/execute cleanly at frozen settings;
- or a memory guardrail is breached during Stage A.

No same-run rescue by reducing context, quantization or GPU layers is permitted. Any fallback is a separately preregistered condition.

## Runner

Canonical runner:
- `scripts/llama_cpp_8b_q4.py`

The runner preserves the preregistered staged sequence, model hash, context, offload request, disk gate and memory guardrails. It also records disk free after the run.

## Non-claims

- Do not call Qwen3 8B Q4 higher quality merely because it has more parameters.
- Do not infer that llama.cpp is globally faster/slower than MLX from different model families.
- Do not infer VRAM as distinct physical memory on Apple unified memory.
- Do not interpret RSS alone as total physical footprint.

## Next decision

If FULL_PASS:
- quantify 4B -> 8B throughput/memory scaling;
- then test an 8B Q3 variant and/or move toward ~9B Q3/Q2 according to observed headroom.

If Stage A passes but Stage B does not:
- investigate a separately frozen partial-offload or lower-quantization condition.

If Stage A fails materially at Q4_K_M:
- move directly to a separately preregistered 8B Q3 condition rather than repeatedly tuning this run.
