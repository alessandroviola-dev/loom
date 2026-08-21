# CAPABILITY 000D — Pi multi-turn loop admission with 512 prefill

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

Can the canonical Qwen3-8B 3-bit system complete an actual multi-turn Pi tool loop at context 4096 when the sole runtime change is `prefill_step_size=512`?

## Frozen subject

- Qwen3-8B full parameter count
- 3-bit affine/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- max output 2048
- enable_thinking=false
- full Pi tools: read/write/edit/bash
- same localhost bridge and isolated Pi configuration

Sole treatment relative to the failed CAPABILITY 000 smoke: `prefill_step_size=512`.

## Task

Use the same disposable `numbers.txt` task:

```
7
11
13
```

Agent must read it, compute 31, create `answer.txt` containing exactly `31`, verify it with a shell command, and finish exactly `DONE`.

## Telemetry

For every model turn record exact input token count, prefill segment sizes, prefill wall, generation wall/tokens, KV logical/capacity length, MLX active/peak/cache, system min-free/swap, Pi RSS, tool chosen/result size and final assistant text.

Preserve raw Pi events and request bodies.

## Gates

Hard abort only at free memory <5% or swap >5600 MB. No rescue, context reduction, KV quantization, prompt/tool compression, model change or hidden retry.

## Admission

Functional admission requires the full task to complete with correct file artifact and verification under the canonical local model with no provider fallback.

Strict admission additionally requires final text exactly `DONE`.

Classifications:

- `CAPABILITY_000D_PI_LOOP_PASS`
- `CAPABILITY_000D_PI_LOOP_FUNCTIONAL_PASS_STRICT_FAIL`
- `CAPABILITY_000D_PI_LOOP_RESOURCE_ABORT`
- `CAPABILITY_000D_PI_LOOP_INFRASTRUCTURE_FAIL`

If functional admission passes with no critical resource breach, CAPABILITY 001 may be considered for a separately reviewed run using the same 512 prefill setting.
