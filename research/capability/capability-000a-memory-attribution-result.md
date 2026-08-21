# CAPABILITY 000A — integrated-agent memory attribution

Date: 2026-08-21
Status: COMPLETE
Classification: `CAPABILITY_000A_MEMORY_ATTRIBUTION_COMPLETE`

## Purpose

Attribute the memory failure seen when the canonical LOOM Qwen3-8B 3-bit model is used as the reasoning model behind Pi through the local MLX bridge.

## Canonical result

- Model instances: **1**.
- Duplicate model: **no**.
- Pi itself is small relative to the model: measured Pi RSS at S5 was **45.55 MB**.
- The largest memory transition is model materialization, S1 -> S2: system free memory **67% -> 30%** and swap **1272.44 -> 2100.62 MB**.
- The model remains usable for direct requests after loading.
- Direct minimal request S3 reached 18 context tokens with 20% free memory.
- Direct tool-schema request S4 reached 366 context tokens with 17% free memory.
- Starting Pi alone did not materially worsen system pressure: S5 was 18% free with Pi RSS 45.55 MB.
- The run aborted during the first real Pi prefill before S6 completed because the hard free-memory floor (<5%) was reached.

## Stage table

| Stage | free % | swap MB | bridge RSS MB | Pi RSS MB | MLX active MB | MLX cache MB | context tokens |
|---|---:|---:|---:|---:|---:|---:|---|
| S0 host baseline | 66 | 1272.44 | — | — | — | — | — |
| S1 bridge listening | 67 | 1272.44 | 24.50 | — | — | — | — |
| S2 model loaded/idle | 30 | 2100.62 | 14.23 | — | 3583.93 | 0.00 | 0 |
| S3 direct simple request | 20 | 1812.62 | 14.98 | — | 3659.74 | 3.31 | 18 |
| S4 direct tool-schema request | 17 | 1796.62 | 10.28 | — | 3737.59 | 3.32 | 366 |
| S5 Pi started | 18 | 1796.62 | 10.28 | 45.55 | 3737.59 | 3.32 | 366 |
| S6 Pi first model response | — | — | — | — | — | — | aborted during Pi prefill |
| S7 first tool result | — | — | — | — | — | — | not reached |
| S8 second model call | — | — | — | — | — | — | not reached |

## BF16 KV arithmetic

For Qwen3-8B with 36 layers, 8 KV heads, head dimension 128, K+V and BF16:

- **147,456 bytes/token**;
- **288 MiB @ 2048 tokens**;
- **432 MiB @ 3072 tokens**;
- **576 MiB @ 4096 tokens**.

## Interpretation

The failure is not caused by a second model copy or by Pi process RSS. The dominant static cost is the canonical 3.58 GB model materialization. The unresolved dynamic failure occurs during the first real Pi prefill. The next experiment must measure the exact Pi request size and prefill peak/temporary-memory behavior before changing context length, KV representation or model quantization.

Local raw evidence:
`results-local/capability/capability-000a/20260821-140547/`

## Next step

Run `CAPABILITY 000B — Pi prefill envelope` without changing Qwen3-8B weights, BF16 KV, context=4096 or the Pi tool surface. Capture the exact first Pi request without executing it, tokenize it, then reproduce the same payload directly through the bridge while measuring prefill peak memory and temporary allocations.
