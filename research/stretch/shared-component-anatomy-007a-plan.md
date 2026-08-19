# Stretch 007A — Shared Component Anatomy — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

What exactly comprises the verified 544,546,816-byte non-transformer-layer payload of the local Qwen3-8B 3-bit artifact, and what storage/config semantics must Stretch 007B preserve when adding embeddings, final norm and output projection?

## Motivation

Stretch 006 established full 36-transformer-block streamed parity with exact final activation parity and ~36x raw layer-weight residency reduction.

The remaining model-weight stage cannot be designed safely from assumptions. Before adding shared components, LOOM must recover the exact local artifact layout:
- token embedding tensors;
- final RMSNorm tensors;
- LM-head/output-projection tensors;
- any other non-layer tensors;
- `tie_word_embeddings` and relevant model config;
- quantization metadata;
- exact bytes per category.

## Frozen subject

Artifact directory:
`results-local/mlx/models/Qwen3-8B-3bit`

Weight file:
`model.safetensors`

Expected non-layer payload from Stretch 001:
**544,546,816 B**.

Frozen Stretch 001 helper source:
`scripts/stretch_layer_streaming_feasibility_001.py`

Required helper blob:
`890444928abd6cc24e7194317c92b36b50fd994b`.

## Method

Read-only, standard-library-only inspection.

1. Verify exact Stretch 001 helper blob.
2. Read local `config.json`.
3. Use the frozen safetensors header parser/catalog from Stretch 001.
4. Select only tensors with `layer_id == None`.
5. Record every non-layer tensor:
   - name
   - dtype
   - shape
   - byte payload
   - shard.
6. Group tensors deterministically by name:
   - `model.embed_tokens.*` -> `embedding`
   - `model.norm.*` -> `final_norm`
   - `lm_head.*` -> `lm_head`
   - everything else -> `other`.
7. Record config fields relevant to the next stage:
   - `model_type`
   - `vocab_size`
   - `hidden_size`
   - `num_hidden_layers`
   - `tie_word_embeddings`
   - `rms_norm_eps`
   - `quantization`.
8. Verify total non-layer bytes equal 544,546,816 B.
9. Save a JSON record under `results-local/stretch/shared-component-anatomy-007a/<runid>/summary.json`.

## Explicit exclusions

Stretch 007A does NOT:
- import MLX;
- materialize tensors;
- construct Qwen3 modules;
- run embedding lookup;
- run transformer computation;
- run final norm or LM head;
- create logits;
- create KV cache;
- generate tokens;
- download or modify model files.

## Classification

Primary PASS:
`SHARED_COMPONENT_ANATOMY_PASS` if:
- helper provenance matches;
- local config and safetensors are readable;
- non-layer total equals exactly 544,546,816 B;
- every non-layer tensor is captured and grouped.

`SHARED_COMPONENT_LAYOUT_MISMATCH` if the known total differs.

`PREFLIGHT_FAIL` for missing/corrupt required artifacts or helper-provenance mismatch.

The presence of tensors in the `other` group is not itself a failure; it is information that must be incorporated into Stretch 007B.

## Decision after PASS

Use the observed physical layout, not general Qwen assumptions, to preregister Stretch 007B:
- real token embedding input;
- all 36 transformer blocks streamed;
- final RMSNorm;
- real output projection according to local tie/head semantics;
- final-logit parity vs resident control;
- still no KV cache or autoregressive generation.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_shared_component_anatomy_007a.py
python3 scripts/stretch_shared_component_anatomy_007a.py
```

No model launch or download is expected.
