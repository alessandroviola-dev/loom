# LOOM Stretch 023 — Harness Fix1 Amendment

Status: **READY / NOT YET RUN**

This amendment repairs a harness defect in the original Stretch 023 treatment implementation. It does **not** change the scientific question or comparison design.

## Preserved failed attempt

Original outer run:
`20260820-151540`

Canonical defect record:
`research/stretch/m5-h36-shared-stage-persistence-023-harness-defect-20260820-151540.md`

That attempt is permanently classified:
`HARNESS DEFECT / NO SCIENTIFIC RESULT`.

No constituent result from that incomplete ABBA sequence may be reused in the repaired comparison.

## Root-cause repair

Frozen broken treatment helper:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py`
- blob `8c263e7be15441581e481e6f41cbd16f87d4df4b`.

Frozen broken comparison runner:
- `scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023.py`
- blob `b8d69c218ee251662fc54a809ca6bf13a4a4e4da`.

The defect was transformation attachment level only: the frozen `add_shared_persistence()` callback was applied to the transformed Stretch 013 wrapper text before that wrapper had generated the final runtime source.

Fix1 changes only this attachment point:
- construct the exact frozen M5/H36 wrapper as before;
- inject the **unchanged frozen** `add_shared_persistence()` callback into that wrapper;
- invoke the callback only after the wrapper has generated the final runtime source;
- preserve all original treatment transformations, gates and measurements.

## Fixed sources

Harness-fixed treatment helper:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

Harness-fixed balanced runner:
- `scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023_fix1.py`
- blob `dfa4c25b71108e258f4d311a65ae038b45be16dc`.

The fix1 runner reuses the frozen original comparison logic and changes only:
1. the PERSISTENT helper path/blob;
2. the output root, so the failed attempt cannot be overwritten;
3. explicit harness-revision metadata/terminal identity.

## Scientific preregistration — unchanged

Question:
> With exact M=5 and all 36 transformer layers persistent, does keeping embedding + final RMSNorm + LM head persistent improve steady-state target verification versus rebuilding those shared stages each pass?

Frozen scientific factor:
- `STREAMED`: H36 transformers persistent; embedding, final RMSNorm and LM head streamed/materialized each pass;
- `PERSISTENT`: same H36 transformers plus those same three shared stages materialized once and retained.

Frozen balanced order:
`STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`.

Frozen environment/policy:
- Apple M1 / 8 GB;
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1;
- oracle block size M=5;
- 3 x 5-token target blocks / 15 accepted oracle tokens per constituent;
- H36 transformer residency;
- ordinary BF16 KV;
- exact numerical/top-1 gates;
- inherited host launch/runtime abort gates;
- inherited Darwin process-I/O instrumentation;
- no tokenizer, sampling, real drafter, KV quantization, prefetch or runtime upgrade;
- no cache purge;
- no automatic retry or fallback.

Shared payload and full raw-weight expectations remain:
- embedding `272,269,312 B`;
- final RMSNorm `8,192 B`;
- LM head `272,269,312 B`;
- shared total `544,546,816 B`;
- H36 transformer payload `3,039,381,504 B`;
- full persistent raw model `3,583,928,320 B`.

## Metrics and classifications — unchanged

Primary metric:
pooled steady-state accepted-token target rate over the two runs of each variant.

One-time PERSISTENT shared setup remains excluded from steady-state rate and reported separately, including estimated target-block break-even.

Primary PASS remains:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`.

Any constituent/provenance/resource/correctness failure remains:
`SHARED_STAGE_COMPARISON_INCOMPLETE`.

No winner may be inferred from partial data.

## Run policy

The repaired experiment must start a completely new four-run ABBA sequence. The valid STREAMED control from the failed attempt is not carried forward.

Stretch 023 still closes the raw-weight residency axis regardless of outcome.