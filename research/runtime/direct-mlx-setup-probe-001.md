# LOOM — Direct MLX Setup Probe 001 Result

Date: 2026-08-19
Run: `20260819-120748`
Status: **PASS**

## Frozen setup condition

Plan: `research/runtime/direct-mlx-setup-probe-001-plan.md`
Runner: `scripts/direct_mlx_setup_probe.py`

Reference machine:
- macOS / Darwin
- Apple Silicon arm64
- Apple M1 / 8 GB unified memory

Isolated environment:
- venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`

No LLM model weights were authorized or downloaded by this setup probe.

## Observed

- disk free before: **43.606 GiB**
- platform preflight: **PASS** (`Darwin arm64`, `uname=arm64`)
- venv creation: **PASS**
- pinned package install: **PASS**
- exact version lock: **PASS**
  - mlx 0.31.2
  - mlx-lm 0.31.3
  - transformers 5.12.1
- tiny local MLX computation: **PASS**
- disk free after: **43.138 GiB**
- setup disk delta: approximately **0.468 GiB**
- classification: **PASS**

Run directory:
`results-local/mlx/setup-probe-001/20260819-120748`

Summary:
`results-local/mlx/setup-probe-001/20260819-120748/setup-summary.json`

## Interpretation

> LOOM now has a reproducible isolated Direct MLX environment on the reference Apple M1 / 8 GB machine. This result validates only the runtime/package setup; it provides no evidence yet about an 8B model's memory safety, speed or quality.

## Next gate

Separately preregister acquisition plus direct-generation smoke for `mlx-community/Qwen3-8B-3bit`, including:
- immutable/verified model artifact evidence;
- disk accounting before/after acquisition;
- context/KV cap 4096;
- same free-memory <5% / swap >5600 MB safety abort;
- no production Pi changes;
- no Coding Benchmark until runtime/workload safety is established.
