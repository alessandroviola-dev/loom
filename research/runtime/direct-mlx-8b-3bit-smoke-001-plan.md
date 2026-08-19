# LOOM — Direct MLX 8B 3-bit Smoke 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can a Qwen3 8B model in native MLX 3-bit format load and complete a deterministic direct-generation smoke on the Apple M1 / 8 GB reference machine while preserving the frozen LOOM memory safety boundary?

## Runtime

Use the already validated isolated environment from Direct MLX Setup Probe 001:
- venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`

No production Pi configuration is touched.

## Model artifact

Candidate:
- repository: `mlx-community/Qwen3-8B-3bit`
- pinned visible Hugging Face revision: `619ded3`
- base family: Qwen3-8B
- MLX quantization: 3 bits, group size 64
- main weight file: `model.safetensors`
- published main-weight size: approximately 3.58 GB
- required SHA256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`

Local destination:
`results-local/mlx/models/Qwen3-8B-3bit`

The runner downloads the snapshot directly into this controlled destination. Runtime inference then uses the local path with Hugging Face offline mode enabled.

No existing GGUF model is deleted or replaced.

## Storage policy

1. Record free disk before acquisition.
2. Require at least 8 GiB free before starting a first acquisition attempt.
3. Download/reuse only the exact candidate snapshot.
4. Verify `model.safetensors` SHA256 after acquisition.
5. Record local model directory size and free disk after acquisition/runtime.
6. Never delete a mismatching or partial artifact automatically; classify and stop.

## Direct-generation policy

This experiment deliberately uses the direct MLX generation API rather than `mlx_lm.server`.

Frozen generation condition:
- local model path only / offline during inference;
- user message: `Reply only with OK.`
- Qwen3 chat template with `enable_thinking=False`;
- maximum generated tokens: 16;
- deterministic/default greedy generation path (no quality claim from this smoke);
- `max_kv_size=4096`;
- **no KV quantization** (`kv_bits=None`) in this first Direct MLX condition;
- one generation attempt only;
- no retry/rescue in the same run.

`max_kv_size=4096` is the Direct MLX operational context/KV cap. It is not claimed to be memory-allocation-equivalent to llama.cpp's fixed server context implementation.

## Telemetry

Record:
- disk free before/acquisition-after/final;
- model file SHA and size;
- config quantization bits/group size;
- child process wall time;
- peak child RSS;
- peak swap used;
- minimum system free-memory percentage;
- MLX-reported peak memory when available;
- prompt token count / prompt tok/s;
- generation token count / generation tok/s;
- finish reason;
- generated text;
- stdout/stderr and full memory samples.

## Frozen safety guardrails

Abort the model process when either becomes true:
- system free memory < **5%**;
- swap used > **5600 MB**.

These are the same LOOM safety thresholds used in Phase 4.

Process RSS is diagnostic only; system-wide free memory and swap drive safety decisions.

## Classification

`FULL_PASS` requires all of:
- validated setup venv exists;
- exact snapshot acquisition/reuse succeeds;
- main weight SHA matches;
- config confirms 3-bit / group-size 64;
- runtime uses local model offline;
- generation process exits 0;
- no guardrail abort;
- non-empty generated text;
- generation stats are captured.

Other classifications:
- `PREFLIGHT_FAIL`: setup environment or disk precondition missing;
- `DOWNLOAD_FAIL`: snapshot acquisition fails;
- `HASH_FAIL`: main weight SHA mismatch;
- `MODEL_METADATA_FAIL`: quantization metadata differs from frozen candidate;
- `RESOURCE_FAIL`: frozen memory/swap guardrail fires;
- `RUNTIME_FAIL`: model load/generation fails without a guardrail breach;
- `INVALID_HARNESS`: clearly demonstrated runner defect.

## Decision after result

If `FULL_PASS`:
1. freeze model/runtime telemetry;
2. run a separately preregistered real-workload safety probe using frozen Coding Benchmark T01 under the same direct-MLX context/KV policy;
3. only if workload-safe proceed to a full quality comparison and then possible Pi integration.

If `RESOURCE_FAIL`:
- do not lower the 5% guardrail;
- do not alter context inside this failed condition;
- a KV-quantized Direct MLX rescue (`kv_bits=8`) may be considered only as a separately preregistered experiment.

If hash/download/runtime fails, diagnose the exact mechanism before changing model/runtime conditions.
