# LOOM — Direct MLX 8B 3-bit Smoke 001 Result

Date: 2026-08-19
Run: `20260819-121656`
Status: **GENERATION PASS / SAFETY TELEMETRY INCOMPLETE — SWAP UNRESOLVED**

## Frozen condition

- isolated Direct MLX environment from Setup Probe 001
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- model `mlx-community/Qwen3-8B-3bit`
- pinned visible revision `619ded3`
- local/offline runtime after acquisition
- model quantization 3-bit / group size 64
- Qwen3 non-thinking chat template
- prompt `Reply only with OK.`
- max generation 16 tokens
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV (`kv_bits=None`)
- frozen safety thresholds: free memory <5% OR swap >5600 MB abort

## Acquisition and artifact verification

Observed:
- disk free before run: 43.032 GiB
- snapshot acquisition: PASS
- disk free after acquisition: 40.668 GiB
- model SHA256: PASS
- main weight size: 3.338 GiB
- quantization metadata: PASS `{'group_size': 64, 'bits': 3}`

No verified GGUF artifact was deleted or replaced.

## Runtime result

Observed direct-generation result:
- child exit code: 0
- assistant content: `OK.`
- prompt: 17 tokens @ 6.3732514376696985 tok/s
- generation: 3 tokens @ 24.62434191148197 tok/s
- MLX-reported peak memory: 3.6676508 GB
- finish reason: `stop`
- peak sampled process RSS: 443.875 MB
- minimum sampled system free memory: 25%
- disk free after runtime: 39.668 GiB

Process RSS is diagnostic only and does not represent total Apple unified/GPU memory use. MLX-reported peak memory and system-wide memory pressure are more relevant for this Direct MLX condition.

## Telemetry defect

The runner printed:

```text
Peak observed swap: None MB
```

This means the frozen swap guardrail was not demonstrably observable during this run. The preregistered plan required both free-memory and swap monitoring, so the console classification `FULL_PASS` is not accepted as a final safety validation until swap telemetry is resolved.

The approximately 1.000 GiB fall in free disk between post-acquisition and final snapshots is also left unattributed. It may reflect swap/APFS/runtime cache behavior, but no causal attribution is supported by this run.

## Canonical interpretation

> Direct MLX successfully loaded and generated with the verified Qwen3-8B 3-bit model at `max_kv_size=4096`, while sampled free memory remained far above the 5% threshold. However, swap telemetry was unavailable, so the two-channel LOOM safety gate was not fully validated.

Therefore classify this run as:

- model acquisition/artifact verification: **PASS**
- Direct MLX generation: **PASS**
- free-memory safety channel: **PASS**
- swap safety channel: **UNRESOLVED**
- overall safety qualification: **PENDING TELEMETRY DIAGNOSTIC**

Do not run Coding Benchmark T01 yet.

## Required next step

Run a read-only macOS swap-telemetry diagnostic. If the issue is a parser/harness defect, fix only telemetry collection and rerun the same smoke condition without changing model/runtime parameters or redownloading the model.
