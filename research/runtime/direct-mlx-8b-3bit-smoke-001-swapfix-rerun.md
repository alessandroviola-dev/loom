# LOOM — Direct MLX 8B 3-bit Smoke 001 Swap-Fix Rerun

Date: 2026-08-19
Run: `20260819-124440`
Status: **FULL_PASS — SAFETY VALIDATED**

## Scope

This rerun preserves the frozen Direct MLX 8B 3-bit Smoke 001 model/runtime/generation condition and changes only macOS swap telemetry parsing so locale decimal commas are observable.

Wrapper:
`scripts/direct_mlx_8b_3bit_smoke_001_swapfix.py`

Frozen base runner:
`scripts/direct_mlx_8b_3bit_smoke.py`

## Frozen model/runtime

- model: `mlx-community/Qwen3-8B-3bit`
- pinned visible revision: `619ded3`
- main weight SHA256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- main weight observed size: 3.338 GiB
- quantization metadata: 3-bit / group size 64
- isolated environment: `mlx-lm==0.31.3`, `mlx==0.31.2`, `transformers==5.12.1`
- local/offline inference
- Qwen3 chat template with `enable_thinking=False`
- prompt: `Reply only with OK.`
- direct `stream_generate`
- `max_kv_size=4096`
- KV unquantized
- maximum generation 16 tokens
- one attempt
- safety abort thresholds: free memory <5% OR swap >5600 MB

No model, context/KV cap, KV precision, prompt, generation policy or safety threshold changed relative to Smoke 001.

## Telemetry correction

The prior smoke could not parse this Mac's localized `vm.swapusage` output because decimal values use commas, for example `used = 1121,88M`.

The rerun wrapper changes only `swap_used_mb()` so both `.` and `,` decimal separators are accepted and comma is normalized before numeric conversion.

Preflight on the rerun:
- locale-safe swap parser: **1113.88 MB**
- parser preflight: **PASS**

## Observed result

- disk free before: **40.640 GiB**
- exact existing model reused
- existing model SHA256: **PASS**
- snapshot verification: **PASS**
- disk after acquisition/reuse: **40.640 GiB**
- model SHA256: **PASS**
- model weight size: **3.338 GiB**
- quantization metadata: **PASS** `{'group_size': 64, 'bits': 3}`
- direct generation exit: **0**
- assistant content: `OK.`
- prompt: **17 tokens @ 11.0758 tok/s**
- generation: **3 tokens @ 24.4160 tok/s**
- MLX-reported peak memory: **3.6676508 GB**
- finish reason: `stop`
- peak sampled process RSS: **494.8125 MB**
- peak observed swap: **1720.75 MB**
- minimum observed system free memory: **23%**
- disk free after: **40.639 GiB**
- classification: **FULL_PASS**

Process RSS remains diagnostic only; system-wide free memory and swap are the frozen safety channels.

## Canonical conclusion

> The verified `mlx-community/Qwen3-8B-3bit` Direct MLX profile can load and complete the frozen non-thinking smoke with `max_kv_size=4096` and unquantized KV on the Apple M1 / 8 GB reference machine while preserving both LOOM safety guardrails. Minimum observed free memory was 23% and peak observed swap was 1720.75 MB.

This is a smoke-level technical/safety result only. It does not yet establish workload stability, coding quality or Pi suitability.

## Next gate

Run a separately preregistered real Coding Benchmark T01 workload-safety probe under the same Direct MLX runtime/safety policy. Only if T01 is workload-safe may LOOM proceed to the full frozen Coding Benchmark quality comparison.
