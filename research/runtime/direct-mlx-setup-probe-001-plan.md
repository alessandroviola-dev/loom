# LOOM — Direct MLX Setup Probe 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can LOOM establish a reproducible, isolated direct-MLX runtime on the reference Apple M1 / 8 GB machine before downloading any new model artifact?

## Motivation

The main llama.cpp 8B branch reached an operational boundary at context 4096:
- Qwen3-8B Q2_K is runnable but loses the frozen structured coding workload to the 4B control;
- Qwen3-8B Q3_K_M can pass an NP1/Q8_0-KV API smoke but fails the frozen memory guardrail during the first real coding task.

The main research branch therefore advances to Phase 5 — Direct MLX. The first action is environment validation only; no model download is authorized by this probe.

## Frozen software condition

Use an isolated venv under `results-local/mlx/`.

Pinned packages:
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`

Rationale:
- mlx-lm 0.31.3 is the current stable mlx-lm release selected for this phase;
- its package metadata requires MLX >=0.31.2, and 0.31.2 is pinned to avoid future dependency drift;
- transformers is pinned for reproducibility rather than left open-ended.

The exact installed dependency set must also be captured with `pip freeze`.

## Isolation

Venv path:
`results-local/mlx/venv-mlx-lm-0.31.3`

The probe must not alter production Pi, Ollama, llama.cpp source/build trees, or system Python packages.

## Procedure

1. Record disk free before.
2. Verify macOS and Apple Silicon architecture (`arm64`).
3. Create the isolated venv if absent.
4. Install the exact pinned packages into that venv.
5. Record Python version and complete `pip freeze`.
6. Verify imported package versions exactly:
   - mlx-lm 0.31.3
   - mlx 0.31.2
   - transformers 5.12.1
7. Run a tiny local MLX array computation with no model load and no network-dependent inference.
8. Run `python -m mlx --version` and `python -m mlx_lm --version` when supported; preserve stdout/stderr regardless.
9. Record disk free after.
10. Save all probe artifacts under `results-local/mlx/setup-probe-001/<runid>/`.

## No-download rule

This probe may download Python packages required to construct the isolated environment. It must **not** download any LLM weights or Hugging Face model snapshot.

## Success criteria

`PASS` requires:
- macOS arm64 preflight;
- venv creation/reuse succeeds;
- pip install exits 0;
- exact pinned package versions import successfully;
- tiny MLX computation returns the expected result;
- no model artifact is requested;
- summary artifacts are written successfully.

## Failure classification

- package resolution/install/import failure: `SETUP_FAIL`;
- wrong platform/architecture: `PLATFORM_FAIL`;
- version mismatch: `VERSION_FAIL`;
- harness/script defect: `INVALID_HARNESS` when clearly demonstrated.

Do not reinterpret a setup failure as evidence about Qwen3 model capability.

## Candidate after setup PASS

The first planned model candidate is `mlx-community/Qwen3-8B-3bit`, a direct MLX conversion of Qwen3-8B. It is selected as a practical 8B/3-bit profile, not as a bit-identical equivalent of GGUF `Q3_K_M`.

The model download/runtime smoke must be separately preregistered after setup PASS, with disk accounting and the existing 5% free-memory safety boundary.
