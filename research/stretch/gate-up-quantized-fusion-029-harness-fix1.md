# LOOM Stretch 029 — Harness Fix1

Status: **HARNESS FIX1 READY — SCIENTIFIC DESIGN UNCHANGED**

Date: 2026-08-20

## Preserved failed sequence

Run:
`results-local/stretch/gate-up-quantized-fusion-comparison-029/20260820-170503`

Classification:
`GATE_UP_QUANTIZED_FUSION_COMPARISON_INCOMPLETE`

Scientific result:
**NONE**.

Defect record:
`research/stretch/gate-up-quantized-fusion-029-harness-defect-20260820-170503.md`

## Root cause

The original helper injected:

```python
source = __stretch029_apply_gate_up_fusion(source)
```

into the transformed wrapper, but then immediately required the intermediate wrapper text to already contain:

```text
single_quantized_matmul_gate_up
```

That string is generated only when the callback executes later against the final runtime source. The original preflight therefore failed before the FUSED treatment launched.

## Frozen original files

Original FUSED helper:
`scripts/stretch_gate_up_quantized_fusion_029.py`

Blob:
`c37ff6313106807c1e2e5070b7fb8f19e97abea6`

Original balanced runner:
`scripts/stretch_gate_up_quantized_fusion_comparison_029.py`

Blob:
`8d89665b5d3061891a53f1734e19331aa1a4fb34`

## Fix1 files

Harness-fixed FUSED helper:
`scripts/stretch_gate_up_quantized_fusion_029_fix1.py`

Blob:
`93d985a526f4433b10fec39fbaf5807059807821`

Harness-fixed balanced runner:
`scripts/stretch_gate_up_quantized_fusion_comparison_029_fix1.py`

Blob:
`3e8c32292763c10d2acea234152d0ff835fe985d`

## Exact harness-only change

Fix1 imports and reuses the original frozen `add_gate_up_fusion()` callback unchanged.

The wrapper preflight now validates only facts that can exist before callback execution:
- M=5 wrapper geometry;
- H36 wrapper geometry;
- Stretch 027 single-pass callback;
- Stretch 029 fusion callback invocation;
- inherited confirmation classification and swap gate.

It no longer requires post-callback generated runtime text to exist before the callback has executed.

Fix1 separately verifies that the frozen original helper source still defines:
- `FusedGateUpMLP`;
- `mx.quantized_matmul(`;
- the `single_quantized_matmul_gate_up` provenance policy;
- the Stretch 029 callback machinery.

The balanced Fix1 runner reuses the original runner logic and changes only:
- FUSED helper path/blob -> Fix1;
- result root -> `gate-up-quantized-fusion-comparison-029-fix1`;
- harness revision/title metadata.

## Scientific design remains frozen

Unchanged:
- CONTROL = Stretch 027 SINGLE_PASS blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`;
- M=5;
- H36;
- full raw-weight persistence;
- one final cleanup/pass;
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2;
- mlx-lm 0.31.3;
- transformers 5.12.1;
- ordinary BF16 KV;
- gate+up fused packed representation;
- one fused `mx.quantized_matmul` per layer;
- no per-forward concatenation;
- SwiGLU/down_proj unchanged;
- exact numerical/top1/acceptance gates;
- resource/I-O policy;
- no cache purge;
- balanced order `CONTROL -> FUSED -> FUSED -> CONTROL`;
- no automatic retry/rescue.

Valid FUSED numerical/top1/acceptance failure remains:
`GATE_UP_QUANTIZED_FUSION_NUMERICAL_PARITY_FAIL`.

Complete exact ABBA success remains:
`GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS`.

Harness/resource/provenance failure remains:
`GATE_UP_QUANTIZED_FUSION_COMPARISON_INCOMPLETE`.

## Rerun policy

Run a completely fresh ABBA through the Fix1 runner. Do not reuse attempt 1 CONTROL from `20260820-170503`.

If the first FUSED reaches the inherited numerical gates and fails them, that is the valid scientific result and the sequence stops without rescue.
