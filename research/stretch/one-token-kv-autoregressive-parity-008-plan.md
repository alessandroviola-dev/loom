# Stretch 008 — One-Token KV Autoregressive Parity — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Can LOOM preserve exact resident-vs-streamed behavior when introducing a real per-layer KV cache, selecting exactly one next token from a frozen prompt, and feeding that token back through the same persisted cache state?

## Motivation

Stretch 007B established exact full-logit parity from token IDs through embedding, all 36 transformer blocks, final RMSNorm and LM head while raw weights were phase-streamed. It intentionally excluded KV cache and autoregressive reuse.

Stretch 008 changes that boundary only: add the default mlx-lm Qwen3 KV-cache semantics and exactly one autoregressive feedback step.

## Frozen subject / environment

Artifact:
`results-local/mlx/models/Qwen3-8B-3bit`

Expected environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

Frozen model config:
- qwen3
- hidden size 4096
- 36 layers
- vocab size 151936
- 32 attention heads
- 8 KV heads
- head dim 128
- `tie_word_embeddings=false`
- 3-bit / group64.

Frozen weight layout:
- total 3,583,928,320 B
- embedding 272,269,312 B
- each transformer layer 84,427,264 B
- final RMSNorm 8,192 B
- LM head 272,269,312 B.

## Frozen provenance

Stretch 007B runner:
`scripts/stretch_phase_streamed_full_logit_parity_007b.py`

Required blob:
`b08c9b44ae062ee259ab6641575e44c4d7d753e6`.

Stretch 002 helper:
`scripts/stretch_single_layer_mlx_materialization_002.py`

Required blob:
`e7bd6bf4c61b44664c0c8421bf230b938509e4ef`.

Official mlx-lm v0.31.3 semantics verified from:
- `mlx_lm/models/qwen3.py`
- `mlx_lm/models/cache.py`
- `mlx_lm/models/base.py`.

Qwen3 has no custom `make_cache`; default `make_prompt_cache` therefore yields one ordinary `KVCache()` per transformer layer.

## Frozen prompt and token policy

Prompt token IDs remain exactly:
`[[1, 42, 2048, 151935]]`.

Prompt length: 4.

Next-token selection is deterministic:
`argmax(last_prompt_logits)`.

No sampling, temperature, top-p, top-k, tokenizer or text decoding.

Exactly one generated token is selected.

To test actual cache reuse rather than only cache population, that selected token is then fed back through both resident and streamed paths using the cache state created by the prompt prefill.

## KV-cache policy

Use default unquantized `mlx_lm.models.cache.KVCache` semantics.

One cache object per transformer layer: 36 total.

Official `KVCache.step = 256`, so the first update allocates capacity for 256 positions.

For this config, expected allocated cache payload per layer after first prefill:
- batch = 1
- KV heads = 8
- capacity = 256
- head dim = 128
- BF16 = 2 bytes
- separate key and value arrays.

Expected per-layer allocated KV bytes:
`2 * 1 * 8 * 256 * 128 * 2 = 1,048,576 B`.

Expected all-36-layer allocated KV bytes:
`37,748,736 B` (36 MiB).

Because prompt length 4 and post-token offset 5 are both below capacity 256, the second autoregressive step should not require another cache allocation block.

Cache-byte values are recorded and checked within +/-1 MiB total tolerance around 37,748,736 B after prompt and after the generated-token step.

## Resident official control

1. Load official full Qwen3 using `mlx_lm.utils.load_model(..., lazy=False, strict=True)`.
2. Create official prompt cache with `make_prompt_cache(resident_model)`.
3. Run the frozen 4-token prompt with that cache.
4. Materialize prompt logits.
5. Verify all 36 cache offsets equal 4.
6. Select exactly one next token using argmax of the final prompt-position logits.
7. Feed that token through the same resident model with the same cache objects.
8. Materialize post-token logits.
9. Verify all 36 cache offsets equal 5.
10. Record cache bytes after prefill and after feedback.
11. Retain only the prompt logits, selected token and post-token logits required for parity, then release resident model/cache before the streamed path.

## LOOM streamed path

Create 36 persistent `KVCache()` objects; these cache objects remain resident while transformer weights continue to stream one layer at a time.

### Prompt prefill

1. Phase-stream token embedding.
2. Build attention mask with the official `create_attention_mask(h, caches[0])` semantics.
3. For layers 0..35:
   - materialize exactly one layer;
   - execute the block with its corresponding persistent `caches[layer_id]`;
   - materialize output;
   - evict the layer weights;
   - keep only activation + all cache objects.
4. Apply final RMSNorm.
5. Phase-stream LM head and obtain full prompt logits.
6. Verify all cache offsets are 4.
7. Select next token via the same deterministic argmax.

### Generated-token feedback

Use the **resident-selected token** as the fixed continuation input for the numerical post-token comparison. The streamed-selected token is separately required to equal it for PASS.

1. Phase-stream embedding for that one token.
2. Build attention mask using cache offset 4. Official semantics yield no explicit mask for N=1.
3. Run layers 0..35 one at a time using the same persistent streamed caches.
4. Each layer cache advances from offset 4 to 5.
5. Apply final RMSNorm.
6. Phase-stream LM head and obtain post-token logits `[1,1,151936]`.
7. Verify all cache offsets equal 5.

## Weight-residency gates

Preserve Stretch 007B weight layout and gates:
- embedding materialization near 272,269,312 B;
- each transformer layer near 84,427,264 B;
- final norm exactly 8,192 B;
- LM head near 272,269,312 B;
- maximum phase-streamed raw-weight stage near 272,269,312 B.

Per-layer post-clear residual active/cache rules are interpreted with the KV cache excluded from the layer-local weight delta baseline: persistent KV memory is allowed and expected to remain across cycles. The runner therefore samples each layer relative to the current cache-resident pre-layer state rather than requiring global active memory to return to zero.

## Numerical gates

### Prompt-with-cache parity

Compare resident vs streamed full prompt logits in float32.

Threshold:
`1e-5 + 1e-5 * resident_prompt_max_abs`.

PASS requires max absolute difference <= threshold.

### Generated token

Resident and streamed argmax next-token IDs must be identical.

### Post-token cache-reuse parity

Feed the resident-selected token through both persisted cache states.

Compare complete resident vs streamed post-token logits `[1,1,151936]` in float32.

Threshold:
`1e-5 + 1e-5 * resident_post_token_max_abs`.

PASS requires max absolute difference <= threshold.

Also record top-1 token IDs from post-token logits as diagnostic.

## Cache gates

After prompt prefill:
- exactly 36 caches;
- every cache offset == 4;
- total allocated `nbytes` within +/-1 MiB of 37,748,736 B.

After generated-token feedback:
- every cache offset == 5;
- total allocated `nbytes` remains within +/-1 MiB of 37,748,736 B;
- cache allocation growth from prompt to post-token <=1 MiB total.

Resident and streamed paths must satisfy the same cache-offset gates.

## Resource / safety

Host launch gate unchanged:
- 3 samples
- each >=60% free memory
- swap <=5600 MB.

Runtime guardrail unchanged:
- free memory <5% => `PARTIAL_RESOURCE_FAIL`
- swap >5600 MB => `PARTIAL_RESOURCE_FAIL`.

Disk recorded before/after. No download.

Whole-run telemetry includes the fully resident control; phase-scoped telemetry is diagnostic where polling captures it and is not required for PASS.

## Primary PASS

`ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS` requires:
- provenance/version/config/layout preflights PASS;
- resident prompt cache offsets 4 and post-token offsets 5;
- streamed prompt cache offsets 4 and post-token offsets 5;
- cache byte gates PASS;
- prompt full-logit parity PASS;
- resident/streamed selected next token identical;
- post-token full-logit parity PASS;
- weight-stage materialization gates PASS;
- no runtime safety violation.

## Interpretation boundary

A PASS would establish the first genuine autoregressive cache-reuse step for LOOM's streamed runtime: a prompt is prefetched, a next token is selected, that token is fed back through the model using persistent per-layer KV state, and the resulting logits match the fully resident official control.

A PASS still does not establish usable multi-token generation throughput. It excludes:
- tokenizer/text prompt;
- sampling;
- multiple generated tokens;
- cache quantization;
- prefetch/double buffering;
- long-context behavior.

## Decision after result

If PASS:
- freeze result;
- next extend the same frozen loop to a short deterministic multi-token argmax sequence before optimization.

If token or post-token parity fails:
- diagnose earliest divergence, especially cache offset/RoPE/mask semantics, before changing cache type or quantization.

If resource fail occurs only during the resident control, distinguish that from streamed-path feasibility and do not weaken guardrails.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_one_token_kv_autoregressive_parity_008.py
python3 scripts/stretch_one_token_kv_autoregressive_parity_008.py
```

No download is expected.
