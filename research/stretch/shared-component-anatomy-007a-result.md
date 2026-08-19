# Stretch 007A — Shared Component Anatomy — Result

Date: 2026-08-19
Run: `20260819-165247`
Classification: **SHARED_COMPONENT_ANATOMY_PASS**

## Subject

Local artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Read-only inspection only. No MLX import, tensor materialization, model construction, network access or generation occurred.

Frozen Stretch 001 helper blob:
`890444928abd6cc24e7194317c92b36b50fd994b`.

Source provenance: PASS.

## Config

Observed local config:
- model type: `qwen3`
- hidden size: 4096
- transformer layers: 36
- vocab size: 151936
- RMSNorm epsilon: 1e-6
- `tie_word_embeddings`: **false**
- quantization: 3-bit / group size 64.

The embedding and output projection are therefore physically distinct in this artifact.

## Tensor accounting

Safetensors shards: 1

All tensors: 907

Transformer-layer payload:
**3,039,381,504 B**

Non-layer payload:
**544,546,816 B**

Total tensor payload:
**3,583,928,320 B**

The observed non-layer total exactly matches the value frozen by Stretch 001.

## Shared/non-layer decomposition

### Token embedding

Group total:
**272,269,312 B**

Tensors:
- `model.embed_tokens.weight`: U32, shape `[151936, 384]`, 233,373,696 B
- `model.embed_tokens.scales`: BF16, shape `[151936, 64]`, 19,447,808 B
- `model.embed_tokens.biases`: BF16, shape `[151936, 64]`, 19,447,808 B

### Final RMSNorm

Group total:
**8,192 B**

Tensor:
- `model.norm.weight`: BF16, shape `[4096]`, 8,192 B

### LM head / output projection

Group total:
**272,269,312 B**

Tensors:
- `lm_head.weight`: U32, shape `[151936, 384]`, 233,373,696 B
- `lm_head.scales`: BF16, shape `[151936, 64]`, 19,447,808 B
- `lm_head.biases`: BF16, shape `[151936, 64]`, 19,447,808 B

### Other

No other non-layer tensors were present.

## Canonical interpretation

The remaining 544,546,816-byte model payload is fully explained by two separate quantized ~272.27 MB vocabulary projections plus an 8 KB final RMSNorm.

Because `tie_word_embeddings=false`, the input embedding and LM head cannot be treated as the same physical weight tensor. However, they are used at opposite ends of the forward path. This makes a **phase-streamed shared-component policy** testable:

1. materialize token embedding and produce the initial activation;
2. evict embedding weights;
3. stream transformer layers 0..35 one at a time;
4. apply the tiny final RMSNorm;
5. materialize the separate LM head only for final logit projection;
6. evict the LM head.

Under that policy the largest raw-weight stage should be one quantized embedding/head payload (~272.27 MB), not the full 544.55 MB shared payload plus the 36-layer body simultaneously.

This anatomy result does not itself prove that the phase-streamed pipeline preserves logits. That is the next experiment.

## Decision

Proceed to Stretch 007B — Phase-Streamed Full-Logit Parity:
- deterministic valid token IDs as input;
- official fully resident Qwen3 model as numerical control;
- phase-streamed embedding -> 36 transformer blocks -> final RMSNorm -> LM head;
- exact final-logit parity comparison;
- no KV cache or autoregressive generation yet.
