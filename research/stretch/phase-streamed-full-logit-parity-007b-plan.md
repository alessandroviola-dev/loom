# Stretch 007B — Phase-Streamed Full-Logit Parity — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Can the local Qwen3-8B 3-bit checkpoint execute from token IDs to final logits with a phase-streamed weight policy — embedding -> evict -> 36 transformer blocks one at a time -> final RMSNorm -> LM head — while matching a fully resident official Qwen3 control numerically?

## Motivation

Stretch 006 proved exact full 36-transformer-block streamed parity while keeping raw transformer-layer residency near one 84,427,264-byte layer at a time.

Stretch 007A recovered the complete non-layer layout:
- token embedding: 272,269,312 B
- final RMSNorm: 8,192 B
- separate LM head: 272,269,312 B
- no other non-layer tensors
- `tie_word_embeddings=false`.

The next missing model-weight stage is therefore full token-ID-to-logit execution. KV cache and autoregressive generation remain deliberately excluded.

## Frozen subject

Artifact directory:
`results-local/mlx/models/Qwen3-8B-3bit`

Weight file:
`model.safetensors`

Config:
- model type `qwen3`
- hidden size 4096
- 36 transformer layers
- vocab size 151936
- 32 attention heads
- 8 KV heads
- head dim 128
- RMSNorm epsilon 1e-6
- `tie_word_embeddings=false`
- quantization 3-bit / group size 64.

Environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

## Frozen provenance

Stretch 002 helper runner:
`scripts/stretch_single_layer_mlx_materialization_002.py`

Required blob:
`e7bd6bf4c61b44664c0c8421bf230b938509e4ef`.

Stretch 005 runner, whose layer materialization/eviction semantics are preserved:
`scripts/stretch_eight_layer_streamed_forward_scaling_005.py`

Required blob:
`8bbfff727a0131c48d4ba71edc8de485182b7fbe`.

The installed `mlx_lm.models.qwen3` implementation is used directly. Runtime records its source SHA-256.

The official `mlx_lm.utils.load_model` path is used for the fully resident control.

## Frozen input

No tokenizer is used yet.

Use deterministic valid vocabulary IDs:

`[[1, 42, 2048, 151935]]`

Shape:
- batch size 1
- sequence length 4.

All IDs satisfy `0 <= id < 151936`.

The same exact token tensor is used for resident and streamed paths.

## Resident control

Construct the exact official Qwen3 model using `mlx_lm.utils.load_model(model_dir, lazy=False, strict=True)`.

This path must:
- build the complete official Qwen3 model;
- use the frozen checkpoint quantization metadata;
- materialize all model parameters;
- execute the four token IDs with cache `None`;
- materialize full logits.

Record:
- active/cache memory before model load;
- active/cache after resident model materialization;
- resident raw-weight/materialized delta;
- resident load wall;
- resident forward wall;
- resident logits shape and max absolute magnitude.

Expected total tensor payload:
`3,583,928,320 B`.

Resident materialization gate:
observed active-memory delta must be within +/-64 MiB of the expected tensor payload. The tolerance is diagnostic accounting allowance; exact parity and streamed component gates remain primary.

After resident logits are materialized:
- retain only the resident logits needed for comparison;
- delete resident model/weight/config references and token tensor;
- run GC + `mx.clear_cache()`;
- record post-control active/cache.

## Phase-streamed path

Use a fresh identical token-ID tensor in the same MLX child process.

### Stage 1 — token embedding

Physical tensors from Stretch 007A:
- `model.embed_tokens.weight`
- `model.embed_tokens.scales`
- `model.embed_tokens.biases`

Expected payload:
**272,269,312 B**.

Construct a minimal wrapper containing `nn.Embedding(vocab_size, hidden_size)`, quantize it with the same frozen 3-bit/group-64 predicate semantics as the official loader, and load only the embedding tensors.

Then:
1. materialize embedding parameters;
2. perform the token lookup;
3. materialize the activation;
4. delete embedding module/weights;
5. GC + clear cache while preserving the activation.

Embedding gates:
- pre-materialization active delta <=32 MiB;
- materialized raw-weight delta 272,269,312 B +/-2 MiB;
- post-eviction cache <=4 MiB;
- post-eviction active movement relative to pre-stage <=4 MiB plus retained activation allowance.

### Stage 2 — 36 transformer blocks

Create the same causal attention mask semantics as official Qwen3 with cache `None`.

For layers 0..35, preserve Stretch 006/005 behavior:
- lazy-load only one layer;
- construct exact official Qwen3 `TransformerBlock`;
- quantize/load only that layer;
- materialize parameters;
- execute forward;
- materialize the new activation;
- evict that layer before loading the next.

Per-layer frozen gates remain:
- pre-eval active delta <=32 MiB;
- materialized delta 84,427,264 B +/-1 MiB;
- post-clear active delta within +/-4 MiB;
- post-clear cache <=4 MiB.

No KV cache.

### Stage 3 — final RMSNorm

Physical tensor:
`model.norm.weight`

Expected payload:
**8,192 B**.

Construct exact `nn.RMSNorm(4096, eps=1e-6)`, load only the final norm weight, materialize it, execute norm, preserve the output activation, then evict the module.

Gate:
- selected tensor payload exactly 8,192 B;
- post-clear cache <=4 MiB.

### Stage 4 — LM head / output projection

Physical tensors:
- `lm_head.weight`
- `lm_head.scales`
- `lm_head.biases`

Expected payload:
**272,269,312 B**.

Construct a minimal wrapper containing `nn.Linear(4096, 151936, bias=False)`, quantize it with the same frozen loader semantics, load only LM-head tensors, materialize parameters, project the final hidden activation to logits, materialize logits, and evict the LM-head module while preserving logits.

LM-head gates:
- pre-materialization active delta <=32 MiB;
- materialized raw-weight delta 272,269,312 B +/-2 MiB;
- post-eviction cache <=4 MiB.

## Numerical parity gate

Compare full resident and phase-streamed logits in float32.

Expected shape:
`[1, 4, 151936]`.

Record:
- max absolute difference
- mean absolute difference
- resident max absolute magnitude
- threshold `1e-5 + 1e-5 * resident_max_abs`.

Primary parity PASS requires:
`max_abs_diff <= threshold`.

Also record top-1 token ID per sequence position for resident and streamed paths; exact top-1 equality is diagnostic and expected if numerical parity passes.

## Weight-residency metrics

Report:
- resident complete-model materialized delta;
- embedding materialized delta;
- maximum transformer-layer materialized delta;
- LM-head materialized delta;
- maximum raw-weight stage across the streamed path;
- resident / maximum-streamed-stage ratio.

Structural expectation:
- resident raw model payload ~3.34 GiB;
- largest streamed raw-weight stage ~272.27 MB (embedding or LM head), not 3.58 GB simultaneously.

This expected ratio is descriptive; explicit component byte gates and parity determine PASS.

## Host/runtime safety

Launch gate:
- 3 samples
- each >=60% free memory
- swap <=5600 MB.

Runtime:
- free memory <5% => `PARTIAL_RESOURCE_FAIL`
- swap >5600 MB => `PARTIAL_RESOURCE_FAIL`
- missing required telemetry => `TELEMETRY_FAIL`.

No guardrail weakening.

## Primary PASS

`PHASE_STREAMED_FULL_LOGIT_PARITY_PASS` requires:
- source/version/config/provenance PASS;
- exact shared-component layout preflight;
- resident materialization within frozen broad accounting tolerance;
- embedding stage size gate PASS;
- all 36 transformer streamed gates PASS;
- final norm stage executes with exact selected payload;
- LM-head size gate PASS;
- final full-logit numerical parity PASS;
- no safety violation.

Diagnostic classifications include:
- `RESIDENT_CONTROL_SIZE_MISMATCH`
- `EMBEDDING_MATERIALIZATION_SIZE_MISMATCH`
- `STREAMED_MATERIALIZATION_SIZE_MISMATCH`
- `STREAMED_EVICTION_INCONCLUSIVE`
- `LM_HEAD_MATERIALIZATION_SIZE_MISMATCH`
- `NUMERICAL_PARITY_FAIL`
- `PARTIAL_RESOURCE_FAIL`
- `TELEMETRY_FAIL`
- `RUNTIME_FAIL`
- `PREFLIGHT_FAIL`.

Harness/runtime defects are not model failures.

## Explicit exclusions

Stretch 007B does NOT:
- tokenize text;
- create or retain KV cache;
- perform incremental decoding;
- generate a second token;
- implement prefetch/double buffering;
- benchmark model quality;
- claim usable generation throughput.

## Decision after result

If PASS:
- freeze full-logit parity and phase-residency result;
- proceed to the first autoregressive/KV experiment with one prompt and one generated token before attempting a longer generation loop.

If resource boundedness fails:
- inspect exact phase before changing residency policy.

If parity fails:
- diagnose the earliest component divergence before adding KV/generation.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_phase_streamed_full_logit_parity_007b.py
python3 scripts/stretch_phase_streamed_full_logit_parity_007b.py
```

No download is expected.
