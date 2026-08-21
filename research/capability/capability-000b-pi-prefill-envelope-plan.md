# CAPABILITY 000B — Pi prefill envelope

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

Why does the canonical Qwen3-8B 3-bit + local MLX bridge + Pi stack cross the hard memory floor during the first real Pi prefill even though the model is single-instanced and Pi itself is small?

## Frozen subject

Keep unchanged:

- Qwen3-8B full parameter count;
- affine 3-bit/group64 weights;
- BF16 KV;
- MLX/mlx-metal 0.31.2;
- mlx-lm 0.31.3;
- normal Qwen3 chat template;
- `enable_thinking=false`;
- Pi local provider through the admitted localhost bridge;
- context 4096;
- max output 2048;
- Pi tools read/write/edit/bash;
- hard abort: free memory <5% OR swap >5600 MB.

Do not lower context, quantize KV, change weights, remove tools, shorten Pi prompts, purge caches, or change model/runtime in this experiment.

## Required measurements

### 1. Capture exact first Pi request without model execution

Intercept/log the first request Pi would send to the localhost bridge for the CAPABILITY 000 smoke workspace. Preserve exact:

- system/developer/user/tool messages;
- tool schemas;
- message count;
- byte size;
- request JSON;
- model/provider fields.

The capture path must return a controlled non-model response or otherwise stop before inference so that request capture itself cannot consume the benchmark.

### 2. Token accounting

Using the exact canonical tokenizer/chat template, calculate:

- total templated input tokens;
- tokens attributable to system/agent instructions where separable;
- user/task tokens;
- tool-schema tokens;
- other protocol/tool envelope tokens;
- remaining headroom to 4096.

Do not estimate from characters when exact tokenizer accounting is possible.

### 3. Direct replay of exact Pi payload

Replay the captured Pi request directly against the same bridge/model without spawning Pi. This isolates model/prefill cost from Pi process overhead.

Record at high enough frequency to catch the peak:

- system free-memory percentage;
- swap;
- MLX active memory;
- MLX peak memory;
- MLX cache memory;
- bridge/server RSS;
- request token count;
- prefill wall if completed.

Sampling interval should be <=100 ms during prefill if practical without materially perturbing the workload.

### 4. Prefill allocation attribution

Inspect the local MLX/mlx-lm path and report, without changing it:

- whether KV is allocated to actual sequence length or context capacity;
- whether prompt prefill uses qmm or another path different from M1 generation;
- material temporary tensors/attention masks/logits allocations that scale with prompt length;
- whether full-vocabulary logits are retained for every prompt position or only the required position;
- any obvious high-water temporary allocation that can explain the abort.

Source inspection is evidence; do not patch the runtime yet.

### 5. Controlled token-length envelope, only if exact Pi replay completes safely

If and only if the exact Pi replay remains above the hard resource floor, create direct non-Pi requests at several naturally truncated prefixes of the exact captured payload to map prefill memory versus token count. Do not alter semantic content except by prefix truncation for diagnostics.

Suggested diagnostic token targets where representable: ~512, 1024, 1536, 2048, exact-Pi length.

This is not a capability test. It is a memory scaling map.

## Classification

- `CAPABILITY_000B_PREFILL_ENVELOPE_COMPLETE` — exact Pi request captured/tokenized and direct replay/prefill memory mechanism sufficiently characterized.
- `CAPABILITY_000B_EXACT_REPLAY_RESOURCE_ABORT` — exact direct replay crosses the hard floor; preserve peak evidence and stop.
- `CAPABILITY_000B_DIAGNOSTIC_INCOMPLETE` — infrastructure prevents trustworthy capture/attribution.

## Decision boundary

Do not select a remedy inside CAPABILITY 000B. The result will determine whether the next factor should target:

- prefill temporary-memory behavior;
- KV/context capacity;
- Pi prompt/tool-envelope size;
- or another identified allocation.

Pi implements/runs only. ChatGPT reviews and handles Git/HANDOFF/ROADMAP afterward.
