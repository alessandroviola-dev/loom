# Stretch 001 — Model Locator Note

Date: 2026-08-19
Status: **HARNESS LOCATOR ISSUE / NO STRETCH RESULT**

## Attempt

Run ID:
`20260819-153944`

Terminal classification:
`MODEL_NOT_FOUND`

Observed:
- model launch: none
- network/download: none
- disk free: 36.325 GiB before and after
- runner did not inspect any model weights.

## Diagnosis

The Stretch 001 default locator searched Hugging Face cache roots for a snapshot named for `mlx-community/Qwen3-8B-3bit`.

The verified Direct MLX benchmark does not use that cache layout. Its frozen runner explicitly uses:

`results-local/mlx/models/Qwen3-8B-3bit`

with primary weight:

`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Therefore the `MODEL_NOT_FOUND` result is a locator mismatch in the new Stretch harness, not evidence that the verified artifact is absent and not evidence against layer-addressable streaming.

## Resolution

Do not modify the frozen Stretch 001 runner. It already accepts an explicit `--model-dir` argument.

Rerun the same frozen experiment with:

```bash
python3 scripts/stretch_layer_streaming_feasibility_001.py \
  --model-dir results-local/mlx/models/Qwen3-8B-3bit
```

This preserves the preregistered Stage A/B logic and changes only artifact path resolution.

## Interpretation boundary

No scientific Stretch classification is assigned to run `20260819-153944`.

The next valid Stretch result requires successful Stage A access to the explicit verified local artifact.