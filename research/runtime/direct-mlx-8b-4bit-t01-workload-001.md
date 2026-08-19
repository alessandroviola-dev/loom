# LOOM — Direct MLX 8B 4-bit T01 Workload Safety 001 Result

Date: 2026-08-19
Run: `20260819-132612`
Status: **FULL_PASS — NARROW FREE-MEMORY MARGIN**

## Frozen condition

- model `mlx-community/Qwen3-8B-4bit`
- pinned revision `545dc4251c05440727734bcd94334791f6ab0192`
- local main weight SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64
- isolated Direct MLX environment: `mlx-lm==0.31.3`, `mlx==0.31.2`, `transformers==5.12.1`
- exact frozen Coding Benchmark 01 v1.0.1 T01 prompt built by adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- local/offline inference
- Qwen3 `enable_thinking=False`
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV
- max generation 2048 tokens
- seed 0
- one attempt; no retry, repair, salvage, re-prompt or test feedback
- safety abort: free memory <5% OR swap >5600 MB

## Preflight

Observed:
- disk free before: **35.354 GiB**
- validated template blob: PASS `e063fdaa11d7cee9bbbbf9ce0b8306e62855388e`
- 4-bit model/runtime transform: PASS
- version lock: PASS
- model SHA256: PASS
- frozen adapter blob: PASS
- frozen T01 prompt: PASS, 1300 chars
- safety preflight: **74% free / 1395.25 MB swap**

The initial shell typo `xcd` occurred before `git pull`; it did not affect the experiment because the shell was already in the repository and all runner preflights subsequently passed.

## Runtime result

- generation exit: 0
- output chars: 421
- prompt: 276 tokens @ **35.24217505693858 tok/s**
- generation: 101 tokens @ **13.92752874696274 tok/s**
- MLX-reported peak memory: **4.981664948 GB**
- finish reason: `stop`
- structured delivery: **written**
- peak sampled process RSS: **558.921875 MB**
- peak observed swap: **2470.31 MB**
- minimum observed free memory: **6%**
- disk free after: **35.354 GiB**
- classification: **FULL_PASS**

## Canonical interpretation

> The exact Qwen3-8B 4-bit Direct MLX profile completed the frozen real T01 coding workload at `max_kv_size=4096` with unquantized KV and respected both LOOM safety guardrails. The free-memory margin is narrow: the minimum observed value was 6%, only one percentage point above the 5% abort threshold.

This is a workload-safety PASS, not a full-session stability or aggregate quality result.

## Descriptive comparison with 3-bit T01

3-bit T01 run `20260819-124952` versus 4-bit T01 run `20260819-132612`:
- minimum free memory: 19% vs **6%**
- peak swap: 1643.12 MB vs **2470.31 MB**
- MLX peak memory: 3.959549116 GB vs **4.981664948 GB**
- prompt throughput: 57.1148 vs **35.2422 tok/s**
- generation throughput: 16.5166 vs **13.9275 tok/s**
- structured delivery: `written` vs **`written`**

These are profile-level observations only. They do not isolate a causal effect of quantization precision.

## Decision

The preregistered T01 gate passed, so the 4-bit profile is authorized for a separately preregistered full six-task Coding Benchmark 01 under the identical runtime and safety policy.

Because the T01 minimum free memory was only 6%, the full one-session benchmark is also a meaningful retained-memory/resource test. Do not reduce context, quantize KV, lower guardrails, or cold-restart between tasks inside that condition.
