# CAPABILITY 000C — bounded prefill-chunk frontier

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

Can smaller prefill chunks materially reduce peak memory for the unchanged 1504-token Pi request while preserving the same Qwen3-8B 3-bit model, BF16 KV, context 4096, tool surface and generated behavior?

## Frozen request and runtime

Reuse the exact captured CAPABILITY 000B Pi request. Do not change:

- request bytes/semantics;
- Qwen3-8B 3-bit affine/group64;
- BF16 KV;
- MLX/mlx-metal 0.31.2;
- mlx-lm 0.31.3;
- context 4096;
- max output 2048;
- enable_thinking=false;
- tool definitions: read/write/edit/bash.

Pi itself is not needed for the primary comparison; replay the exact captured request directly through the bridge so Pi RSS is removed as a nuisance variable.

## Sole factor

`prefill_step_size` / effective maximum prefill chunk size.

Evaluate, in descending order and with fresh equivalent request state:

- CONTROL: 2048 (observed effective first M=1430)
- 1024
- 512
- 256

Do not add smaller values unless separately authorized.

## Measurements

For every variant record:

- actual M sequence used by prefill;
- input tokens (must remain 1504);
- prefill wall;
- TTFT if available without changing workload;
- minimum system free memory;
- peak swap;
- MLX active/peak/cache;
- post-prefill active memory;
- transient peak above post-prefill active;
- resulting first generated token ID;
- resulting first complete assistant/tool-call output under a short frozen generation cap sufficient to capture the first tool call.

No cache purge between variants. If fresh process/model state is required for comparability, use the same documented initialization protocol for every variant.

## Correctness/admission

All variants must preserve:

- finite logits;
- correct KV advancement;
- same prompt tokenization;
- same first greedy token ID as CONTROL;
- preferably exact same first tool-call sequence. If token sequence differs, report it and do not silently label the variant equivalent.

Bit-exact logits are diagnostic, not required for this infrastructure feasibility unless naturally available.

## Resource safety

Hard abort per constituent if:

- free memory <5%; or
- swap >5600 MB.

No purge, artificial allocation, context reduction, KV quantization, tool removal, prompt shortening or model changes.

## Primary output

A frontier table:

`chunk size | M sequence | min free % | peak MLX MB | transient MB | prefill wall | wall penalty vs control | first-token/tool-call agreement`

The purpose is not to pick minimum RAM at any cost. Select the smallest memory treatment that restores practical headroom with an acceptable prefill-time penalty.

## Practical admission target

A candidate is worth integrating into CAPABILITY 000 only if it:

1. preserves first-token/tool-call behavior;
2. remains safely above the 5% abort floor;
3. improves minimum free-memory headroom materially over the 2048 control;
4. does not impose an obviously disproportionate prefill-time penalty.

Do not freeze a universal numeric speed threshold before seeing the frontier.

## Follow-up

If a chunk size provides clear memory headroom, run a separate integrated Pi smoke using that one frozen size. Do not launch CAPABILITY 001 directly from this diagnostic.

Pi implements/tests only. ChatGPT owns result review and repository synchronization.
