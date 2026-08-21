# CAPABILITY 000I — Request-local state reclamation

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Background

CAPABILITY 000H proved a sequential-only failure:

- every captured R1-R6 request passes fresh;
- R1 passes sequentially;
- R2 fails sequentially at 4% free;
- R2 fresh peak 4095.65 MB;
- R2 sequential observed peak 4182.45 MB;
- after R1, MLX active is 3886.20 MB versus 3417.90 MB loaded-idle: +468.30 MB request-boundary active state;
- post-R1 MLX allocator cache is ~226.57 MB.

Later request size, context length and host variability are not supported as primary causes.

## Question

Which request-local server object/tensor lifecycle owns the retained active MLX state after a completed response, and can that exact stale state be released at response completion without changing model, prompt, KV representation, inference output or global allocator policy?

## Phase A — attribution before treatment

Inspect the actual MLX-LM server lifecycle used by LOOM. Trace ownership after exact captured R1 completes, including:

- API handler/request lifecycle;
- response/stream generator;
- BatchGenerator;
- PromptProcessingBatch;
- pending/finished request queues;
- request KV/cache objects;
- logits/output arrays;
- instrumentation closures.

Use weakrefs/object graphs and metadata-only tensor byte accounting where safe. Do not invoke GC or allocator cleanup.

A treatment is allowed only if a precise stale owner/reference or intended-but-missing lifecycle transition is identified. Otherwise stop as attribution incomplete.

## Phase B — one targeted treatment

CONTROL: exact R1 -> exact R2 sequentially with canonical natural server behavior.

TREATMENT: same fresh process and exact R1 -> R2 sequence, with one targeted request-local lifecycle release immediately after R1 HTTP response completion.

The treatment may only close/remove/drop the specific completed-request owner proven in Phase A, preferably through the runtime's intended lifecycle API. It must not clear global model state or allocator cache.

Forbidden treatment mechanisms:

- `mx.clear_cache()`;
- `gc.collect()`;
- model reload;
- process restart between R1/R2;
- KV quantization;
- prefill step change;
- context/prompt/tool reduction;
- global cache purge;
- unrelated object deletion.

## Frozen configuration

Qwen3-8B full parameter count, affine 3-bit/group64, BF16 KV, MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, context 4096, `prefill_step_size=512`, same tokenizer/chat template/tool schema and exact captured CAPABILITY 000H R1/R2 bodies.

## Required measurements

For CONTROL and TREATMENT record:

- host pre-load admission state;
- loaded-idle MLX active/cache;
- R1 peak and output/tool call;
- immediately post-R1 active/cache;
- active/cache after request-local finalization point;
- residual active/cache over loaded idle;
- R2 peak/min-free/swap;
- R2 completion;
- exact/semantic R1 and R2 response agreement;
- object weakref/liveness before and after targeted finalization.

Primary metrics:

1. request-boundary active memory recovered;
2. sequential R2 peak reduction;
3. R2 resource-gate outcome;
4. output equivalence.

## Promotion condition

A targeted lifecycle release is useful if it:

- is source/object-lifecycle justified;
- materially reduces post-R1 active memory;
- allows R2 to complete with >=5% free under comparable host admission;
- preserves model outputs/tool-call behavior;
- does not use global cleanup or alter model representation.

## Classifications

- `CAPABILITY_000I_TARGETED_RECLAMATION_PASS`
- `CAPABILITY_000I_TARGETED_RECLAMATION_NO_GO`
- `CAPABILITY_000I_ATTRIBUTION_INCOMPLETE`
- `CAPABILITY_000I_INFRASTRUCTURE_INCOMPLETE`

Do not proceed to CAPABILITY 001 or another memory treatment in the same run.