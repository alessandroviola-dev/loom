# Stretch 009 — Four-Token KV Autoregressive Parity — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Can the phase-streamed Qwen3-8B path preserve resident-control numerical/token parity across a short repeated autoregressive loop while reusing the same 36 persistent ordinary BF16 KV caches and keeping raw weights phase-streamed?

## Frozen predecessor

Stretch 008 valid run `20260819-173553`:
`ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`.

Scientific runner blob:
`03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`.

Harness pipefix blob:
`8b2ce5902d3ed45c9120273fab415fe67a026d4a`.

Stretch 008 established exact prompt logits, generated-token equality, identical 36-layer KV state at offsets 4 and 5, and exact logits after one feedback token.

## Single scientific change

Autoregressive continuation depth:
- Stretch 008: exactly **1** generated/feedback token
- Stretch 009: exactly **4** generated/feedback tokens.

No other model/cache/quantization/prompt/generation policy changes are authorized.

## Frozen subject / environment

Model:
`results-local/mlx/models/Qwen3-8B-3bit`

Weight file:
`model.safetensors`

Frozen versions:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

Model/config:
- qwen3
- hidden size 4096
- 36 transformer layers
- vocab size 151936
- 32 attention heads
- 8 KV heads
- head dim 128
- RMSNorm eps 1e-6
- `tie_word_embeddings=false`
- 3-bit / group64 weights.

Frozen prompt token IDs:
`[[1, 42, 2048, 151935]]`.

Generation:
- deterministic argmax only
- exactly 4 generated tokens
- no tokenizer
- no sampling
- no cache quantization
- no prefetch/double buffering
- no speculative decoding.

## Cache policy

Use ordinary `mlx_lm.models.cache.KVCache` for all 36 layers.

Expected initial capacity behavior from the frozen mlx-lm implementation:
- KV allocation step = 256 positions
- prompt length 4 allocates the first block
- expected total KV bytes across 36 layers = **37,748,736 B**
- offsets after prefill = all 4
- offsets after feedback tokens = all 5, 6, 7, 8
- total allocated KV bytes should remain ~37,748,736 B throughout because offset 8 remains below the initial 256-position capacity.

No cache-capacity-boundary experiment is combined with Stretch 009.

## Resident control

Use the official fully resident Qwen3 model and official `make_prompt_cache`.

1. Run frozen 4-token prompt with cache.
2. Take argmax of the last prompt position -> token 1.
3. Feed token 1 through the same cache -> offset 5; obtain logits and token 2.
4. Feed token 2 -> offset 6; obtain logits and token 3.
5. Feed token 3 -> offset 7; obtain logits and token 4.
6. Feed token 4 -> offset 8; obtain final diagnostic logits/top-1.

Record resident logits, token sequence and cache snapshots at every step.

## Phase-streamed path

Create 36 persistent ordinary `KVCache()` objects once.

For prompt and each of the four feedback passes:
1. materialize quantized embedding -> compute -> evict weights;
2. for layer 0..35:
   - materialize exactly that layer's weights;
   - execute official Qwen3 `TransformerBlock` against that layer's persistent cache;
   - evict layer weights;
3. materialize final RMSNorm -> compute;
4. materialize LM head -> logits -> evict.

The streamed side computes its own argmax after every pass. For numerical comparison, the resident-selected token is the common feedback input at each step; streamed argmax must equal it before the next step is authorized by the analysis gate.

## Numerical gates

Prompt parity:
- compare complete prompt logits in float32
- threshold `1e-5 + 1e-5 * resident_max_abs`
- streamed prompt argmax token must equal resident token 1.

For each feedback step 1..4:
- compare complete `[1,1,vocab]` logits resident vs streamed in float32
- same threshold formula per step
- top-1 prediction equality required.

Generated token sequence:
- resident and streamed generated tokens 1..4 must be identical.

Any parity/token failure is a scientific failure for the frozen multi-token profile; do not repair/retry inside the run.

## Cache gates

For resident and streamed paths:
- cache count exactly 36
- after prompt: every offset exactly 4
- after feedback step `s`: every offset exactly `4+s` for s=1..4
- total cache bytes near 37,748,736 B within +/-1 MiB
- cache growth from prompt to each step must not exceed +1 MiB while below the 256-position boundary.

## Raw-weight residency gates

Preserve Stretch 008 stage sizes:
- embedding: 272,269,312 B +/-1 MiB
- transformer layer: 84,427,264 B +/-1 MiB
- final norm: 8,192 B +/-1 MiB accounting tolerance
- LM head: 272,269,312 B +/-1 MiB
- layer pre-eval delta <=32 MiB.

Persistent KV bytes are accounted separately from raw-weight-stage materialization.

## Timing / diagnostics

For prompt and each feedback token record:
- embedding materialize/forward wall
- sum of 36 layer materialize walls
- sum of 36 layer forward walls
- final norm materialize/forward wall
- LM-head materialize/forward wall
- total pass wall where practical.

Report per-feedback-token layer-materialization and layer-forward times and aggregate mean/median where available.

Phase/system telemetry:
- host launch gate: free >=60% for 3 samples; swap <=5600 MB
- runtime abort: free <5% or swap >5600 MB
- whole-run minimum free, peak swap, peak child RSS
- phase buckets diagnostic only because polling can miss short phases.

## Harness policy after Stretch 008 pipe incident

Do not emit verbose per-state JSON into an undrained captured pipe.

Frozen implementation requirement:
- child progress -> `child-state.json`
- child final scientific payload -> `child-final.json`
- child stdout/stderr -> file-backed handles or otherwise continuously drained
- parent polls state + host telemetry
- final payload is read from file after child exit.

This is a harness-safety implementation choice, not a new scientific factor.

## Classification

Primary PASS:
`FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`.

Primary PASS requires:
- all provenance/version/config gates
- resident full-model accounting gate
- prompt numerical/token parity
- four feedback numerical parity gates
- generated token sequence equality
- all cache count/offset/byte gates
- all streamed raw-weight-stage gates
- no host/runtime guardrail violation.

Setup/harness/telemetry failures must not be called model failures.

## Interpretation boundary

A PASS would establish short repeated deterministic autoregressive cache reuse with phase-streamed raw weights. It would still not establish:
- tokenizer/text prompt behavior
- sampling parity
- long-context/cache-capacity-boundary behavior
- long-run generation stability
- physical SSD bytes/token
- optimized tokens/second
- prefetch effectiveness.

## Decision after PASS

Only after a PASS should LOOM choose the next single-factor experiment: either tokenizer/text integration or a longer deterministic loop/per-token performance characterization. Prefetch, KV quantization and cache-capacity-boundary tests remain separate experiments.