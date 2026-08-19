# LOOM — Direct MLX 8B 3-bit T01 Workload Safety 001

Date: 2026-08-19
Run: `20260819-124952`
Status: **FULL_PASS — REAL T01 WORKLOAD SAFETY**

## Frozen condition

- isolated Direct MLX environment
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- model `mlx-community/Qwen3-8B-3bit`
- verified local `model.safetensors` SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit / group size 64
- local/offline inference
- Qwen3 chat template with `enable_thinking=False`
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV
- `mx.random.seed(0)`
- max generation 2048 tokens
- frozen free-memory abort below 5%
- frozen swap abort above 5600 MB
- locale-safe swap telemetry

Frozen benchmark provenance:
- Coding Benchmark 01 v1.0.1
- T01 only
- frozen adapter `scripts/ollama_single_shot.py`
- adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- exact adapter `build_prompt()` envelope
- no test feedback
- one attempt
- no retry / repair / salvage / re-prompt

## Observed

- disk free before: 40.634 GiB
- version lock: PASS
- model SHA256: PASS
- frozen adapter blob: PASS
- frozen T01 prompt: PASS, 1300 chars
- safety preflight: PASS at 75% free / 1266.38 MB swap
- T01 child exit: 0
- output length: 372 chars
- prompt: 276 tokens @ 57.1148 tok/s
- generation: 86 tokens @ 16.5166 tok/s
- MLX-reported peak memory: 3.959549116 GB
- finish reason: `stop`
- structured delivery: `written`
- peak sampled process RSS: 403.25 MB
- peak observed swap: **1643.12 MB**
- minimum observed free memory: **19%**
- classification: **FULL_PASS**
- disk free after: 40.633 GiB

Run directory:
`results-local/mlx/8b-3bit-t01-workload-001/20260819-124952`

Summary:
`results-local/mlx/8b-3bit-t01-workload-001/20260819-124952/t01-workload-summary.json`

## Interpretation

> The verified Direct MLX Qwen3-8B 3-bit profile completed the exact frozen Coding Benchmark T01 request at `max_kv_size=4096` with unquantized KV while remaining comfortably inside both LOOM safety guardrails. It also satisfied the frozen structured-delivery envelope for T01.

This is the exact real-workload gate where the Q3/llama.cpp profile previously crossed the 5% free-memory boundary and aborted. Direct MLX therefore establishes materially stronger workload-safety evidence for this 8B-class profile on the reference M1/8 GB machine.

This record does **not** yet claim full coding quality. T01 tests were intentionally not run by this safety probe. Correctness and aggregate delivery quality are resolved by the separately preregistered full Coding Benchmark 01.

## Decision

Authorize the full Direct MLX Coding Benchmark 01 under the same runtime/safety policy. Do not change model, KV precision, KV cap, prompt envelope, parser, scorer, safety thresholds, or retry policy.
