# LOOM — Direct MLX 8B 4-bit Smoke 001 Result

Date: 2026-08-19
Run: `20260819-131009`
Status: **FULL_PASS**

## Frozen condition

- model `mlx-community/Qwen3-8B-4bit`
- pinned revision `545dc4251c05440727734bcd94334791f6ab0192`
- isolated Direct MLX environment:
  - `mlx-lm==0.31.3`
  - `mlx==0.31.2`
  - `transformers==5.12.1`
- local/offline inference after acquisition
- Qwen3 `enable_thinking=False`
- prompt `Reply only with OK.`
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV
- max 16 generated tokens
- seed 0
- locale-safe macOS swap telemetry
- safety abort: free memory <5% OR swap >5600 MB

## Acquisition / artifact verification

Observed:
- disk free before: **40.647 GiB**
- snapshot acquisition: PASS
- disk free after acquisition: **36.331 GiB**
- main weight SHA256: PASS
- observed main weight: **4.291 GiB**
- quantization metadata: PASS `{'group_size': 64, 'bits': 4}`

No verified 3-bit or GGUF artifact was deleted or replaced.

## Runtime / safety result

Preflight:
- free memory 75%
- swap 1261.50 MB

Generation:
- child exit 0
- assistant content `OK.`
- prompt 17 tokens @ **3.2971 tok/s**
- generation 3 tokens @ **20.8411 tok/s**
- MLX-reported peak memory **4.683327704 GB**
- finish `stop`

Telemetry:
- peak sampled process RSS **560.484375 MB**
- peak observed swap **2403.31 MB**
- minimum observed free memory **10%**
- disk free after runtime **35.329 GiB**

Classification: **FULL_PASS**.

## Canonical interpretation

> The exact Direct MLX Qwen3-8B 4-bit profile can load and complete the frozen 4096-KV smoke on the reference M1/8 GB machine without crossing LOOM's 5% free-memory or 5600 MB swap guardrails. The safety margin is materially narrower than the previously validated 3-bit smoke, so this result authorizes only the separately preregistered real T01 workload-safety gate, not the full coding benchmark or Pi integration.

Descriptive comparison to the safety-valid 3-bit smoke (`20260819-124440`):
- 3-bit min free 23% vs 4-bit 10%
- 3-bit peak swap 1720.75 MB vs 4-bit 2403.31 MB
- 3-bit generation 24.4160 tok/s vs 4-bit 20.8411 tok/s
- 3-bit MLX peak memory 3.6676508 GB vs 4-bit 4.683327704 GB

These are profile-level observations, not causal estimates of the effect of one additional quantization bit.

## Decision

Preregister exact Coding Benchmark T01 workload-safety using the same 4-bit runtime. Do not change KV cap, KV precision, prompt/parser, generation budget, or guardrails.