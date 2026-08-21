# CAPABILITY 000E — Fresh vs Sequential Turn Attribution

Date: 2026-08-21
Status: COMPLETE
Classification: `CAPABILITY_000E_NO_REPRODUCTION`

## Question

Determine whether CAPABILITY 000D Fix2 failed because the second exact Pi request (~1576 tokens) is intrinsically too large for the canonical Qwen3-8B 3-bit runtime, or because request 1 leaves enough residual state to make request 2 fail sequentially.

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- `prefill_step_size=512`
- exact captured request bodies from CAPABILITY 000D Fix2
- R1: 1521 canonical input tokens
- R2: 1576 canonical input tokens

No cleanup treatment, prompt modification, KV quantization, context reduction or model change was applied.

## Result

### Fresh R2

R2 was executed as the first request after a fresh model/server load.

- completed: yes
- M segments: `512,512,512,39`
- peak MLX: **4095.65 MB**
- post-request active MLX: **3922.20 MB**
- post-request cache: **4.79 MB**
- minimum free memory: **6%**
- peak swap: **2108.94 MB**

Therefore R2 is **not intrinsically above the executable envelope** under the observed host state.

### Sequential R1 -> R2

Both requests completed in the same fresh process without cleanup between them.

Loaded-idle baseline:

- active MLX: **3417.90 MB**
- cache MLX: **0 MB**
- bridge RSS: **24.94 MB**
- free memory: **30%**
- swap: **1981.50 MB**

After R1, a stable residual was observed:

- active MLX: **3886.20 MB** = **+468.30 MB** over loaded idle
- allocator cache: **229.07 MB**
- bridge RSS: lower than loaded-idle by 13.49 MB

R2 nevertheless completed.

Sequential R2 peak MLX: **4194.45 MB**.
Fresh R2 peak MLX: **4095.65 MB**.
Sequential peak delta: **+98.80 MB** (~2.4% of fresh R2 peak).

Sequential R2 ended with:

- active MLX: **3922.20 MB**
- cache MLX: **2.96 MB**
- observed free memory at B8: **12%**
- swap: **1971.19 MB**

## Object/reference lifetime audit

- `CompletionRequest`: weak reference dead; no persistent request object found.
- 180 `BatchKVCache` objects: all weak references dead; no request KV retained.
- one `PromptProcessingBatch` remained live through a `BatchGenerator` reference; its KV objects were not retained.
- one generic `Response` object was found by passive GC inspection; turn attribution unresolved.
- telemetry retained scalars only.
- prompt-cache sequences/bytes: zero.

This is **not evidence of a memory leak**.

## Interpretation

The specific failure from CAPABILITY 000D Fix2 did not reproduce in either controlled path:

1. exact R2 succeeds when fresh;
2. exact R1 then exact R2 also succeeds without cleanup.

R1 does leave persistent active MLX state and allocator cache, and the sequential R2 peak is ~98.8 MB above the fresh-R2 peak, so inter-request state is real. However it was insufficient to reproduce the hard resource abort.

The large differences in system `memory_pressure`/free-memory observations across otherwise similar MLX states indicate that host/system state materially affects the <5% free-memory gate. Therefore the Fix2 abort should not be reclassified as an intrinsic 1576-token or step-512 limit.

## Decision

Do **not** move immediately to step 256, KV quantization, prompt/tool compression or context reduction on the basis of Fix2 alone.

Next experiment should test the actual integrated Pi loop with the 512 treatment under a preregistered, reproducible passive host launch state and a fresh scientific server process not contaminated by preflight inference. Repeated runs should establish whether the bridge is operationally reliable or merely host-state-sensitive.

Raw evidence remains local at:
`results-local/capability/capability-000e/20260821-000e-attribution-final/`.
