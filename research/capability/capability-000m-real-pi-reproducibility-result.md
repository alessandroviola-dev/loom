# CAPABILITY 000M — real Pi boundary-reclamation reproducibility result

Date: 2026-08-21
Classification: `CAPABILITY_000M_REAL_PI_REPRODUCIBLE_PASS`

## Goal

Validate the promoted request-boundary reclamation mechanism in the actual Pi-integrated localhost bridge, not only captured-request replay.

The only runtime treatment promoted from CAPABILITY 000L was applied after each fully completed model response:

1. ownership-check the finished `GenerationBatch.Response`;
2. detach only that completed response's stale `prompt_cache`;
3. call `mx.clear_cache()` exactly once.

No model, context, KV, prompt, tool, quantization or prefill-step change was allowed.

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- max assistant output 2048
- `enable_thinking=false`
- `prefill_step_size=512`
- real Pi with `read`, `write`, `edit`, `bash`
- localhost-only `loom-mlx-local` provider

## Frozen task

Each independent attempt used a fresh disposable workspace containing exact `numbers.txt` bytes:

```text
7
11
13
```

Pi had to read the file, compute the sum, create `answer.txt` containing exactly `31`, verify it through the shell, preserve `numbers.txt`, and finish exactly `DONE`.

## Host admission

All three attempts met the frozen pre-load host gate on two consecutive passive samples:

| Attempt | Free sample 1 | Free sample 2 | Swap | Admitted |
|---|---:|---:|---:|---|
| 1 | 71% | 71% | 1370.88 MB | yes |
| 2 | 71% | 71% | 1377.69 MB | yes |
| 3 | 72% | 72% | 1527.38 MB | yes |

## Results

All three independent fresh-process/fresh-Pi attempts passed both functional and strict criteria.

| Attempt | Functional | Strict | Model turns | Tool sequence | Largest input | Max KV logical/capacity | Peak MLX | Min free | Peak swap | Boundary clears | Mean clear | Elapsed |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | PASS | PASS | 6 | read -> bash -> write -> bash -> bash | 1813 | 1812 / 2048 | 4123.39 MiB | 9% | 1513.69 MB | 6 | 2.003 ms | 152.087 s |
| 2 | PASS | PASS | 6 | read -> bash -> write -> bash -> bash | 1813 | 1812 / 2048 | 4123.39 MiB | 11% | 1612.69 MB | 6 | 2.478 ms | 152.217 s |
| 3 | PASS | PASS | 6 | read -> bash -> write -> bash -> bash | 1807 | 1806 / 2048 | 4116.06 MiB | 11% | 1580.75 MB | 6 | 2.596 ms | 151.924 s |

Primary reproducibility result:

- functional success: **3/3 = 100%**
- strict success: **3/3 = 100%**
- resource aborts: **0**
- telemetry errors: **0**

Every `answer.txt` contained exactly `31`; every `numbers.txt` integrity check passed; every final assistant response was exactly `DONE`.

## Boundary behavior

| Attempt | Minimum post-clear free | Max post-clear active | Max post-clear cache | Mean clear | Max clear |
|---|---:|---:|---:|---:|---:|
| 1 | 16% | 3706.20 MiB | 0.00 MiB | 2.003 ms | 2.335 ms |
| 2 | 19% | 3706.20 MiB | 0.00 MiB | 2.478 ms | 3.851 ms |
| 3 | 18% | 3706.20 MiB | 0.00 MiB | 2.596 ms | 4.291 ms |

The promoted mechanism therefore maintained zero sampled allocator cache after each boundary clear and preserved materially positive post-clear system headroom in all three real-agent attempts.

## Interpretation

CAPABILITY 000M closes bridge admission for the canonical Qwen3-8B 3-bit capability baseline.

The result supports all of the following:

- the local model can drive real Pi through a multi-turn tool workflow;
- the request-boundary ownership fix is valid in the integrated bridge;
- one boundary `mx.clear_cache()` is operationally low-cost at the measured scale;
- the combined mechanism is reproducible across three independently admitted attempts;
- no semantic rescue, provider retry, cloud/Ollama fallback or resource abort was needed.

This does **not** claim long-horizon memory behavior is solved for arbitrary conversations. It establishes sufficient reproducible headroom for the frozen CAPABILITY 001 suite.

## Evidence

Local raw evidence:

`results-local/capability/capability-000m/20260821-195821/`

Local implementation changed by Pi:

- `scripts/capability_000m_real_pi_boundary_reclamation.py`
- `scripts/loom_pi_mlx_bridge.py`

The bridge source remains local-only until explicitly synchronized from the user's worktree.
