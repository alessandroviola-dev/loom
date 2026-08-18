# LOOM — llama.cpp 4B Runtime Control 001

Date: 2026-08-18 / 2026-08-19 local rollover
Status: **PASS / CANONICAL 4B RUNTIME CONTROL**
Run id: `20260818-235812`

## Configuration

- Reference machine: Apple M1, 8 GB unified memory
- llama.cpp pinned commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- Metal build: canonical Phase 4 setup build
- Model repo: `Qwen/Qwen3-4B-GGUF`
- Model file: `Qwen3-4B-Q4_K_M.gguf`
- Quantization: `Q4_K_M`
- Verified SHA256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- Observed model size: **2.326 GiB**
- GPU layers: `-1` (maximum/default full-offload request for this test)
- Flash attention: `auto`
- Prompt-processing test: 512 tokens
- Text-generation test: 128 tokens
- Repetitions: 3

## Device / backend validation

`llama-bench --list-devices` reported:

- `MTL0: Apple M1 (5461 MiB, 5460 MiB free)`
- `BLAS: Accelerate`
- unified memory: `true`
- embedded Metal library loaded successfully
- recommended Metal max working set: **5726.63 MB**

The benchmark rows reported backend `MTL,BLAS`, and runtime logs contained Metal initialization evidence.

## Results

- Benchmark: **PASS**
- Prompt processing `pp512`: **230.85 t/s ± 0.12**
- Text generation `tg128`: **22.33 t/s ± 0.02**
- Metal evidence: **True**
- Peak process RSS: **1914.91 MB**
- Peak observed swap: **1097.19 MB**
- Minimum observed free memory: **22%**
- Overall success: **True**

Local result directory:
- `results-local/llama-cpp/4b-control/20260818-235812`

Local summary:
- `results-local/llama-cpp/4b-control/20260818-235812/control-summary.json`

## Interpretation

This completes the purpose of the 4B runtime control:

1. official GGUF download and SHA256 verification work;
2. the pinned llama.cpp build loads and executes the model successfully;
3. Metal is active on the Apple M1;
4. throughput telemetry is parsable and stable across repetitions;
5. RSS/swap/memory-pressure telemetry works under live inference.

This result is **not** a clean runtime-performance comparison against the existing Ollama/MLX `qwen3.5:4b-mlx` baseline because the model family/version and quantization differ. The numerical throughput values may be shown side-by-side descriptively, but no claim that llama.cpp is intrinsically faster should be made from this control alone.

## Phase 4 consequence

The runtime measurement path is validated. Proceed to the preregistered main capability test:

- `Qwen/Qwen3-8B-GGUF`
- `Qwen3-8B-Q4_K_M.gguf`
- context 4096 initial smoke
- maximum practical Metal offload first
- then throughput measurement if the smoke is stable.

Because the 8B Q4 artifact is materially larger and close to the Metal working-set frontier on the 8 GB reference machine, free disk and memory guardrails must be checked before launch.
