# LOOM Stretch 023 — M5/H36 Shared-Stage Persistence — Result

Status: **COMPLETE PASS after preregistered harness-only fix1**

Canonical scientific classification:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`

Valid scientific run:
`20260820-153308`

Run directory:
`results-local/stretch/m5-h36-shared-stage-persistence-023-fix1/20260820-153308`

Summary:
`results-local/stretch/m5-h36-shared-stage-persistence-023-fix1/20260820-153308/summary.json`

## Preserved harness defect

The first execution attempt, run `20260820-151540`, is retained separately as a harness defect with **no scientific result**:

`research/stretch/m5-h36-shared-stage-persistence-023-harness-defect-20260820-151540.md`

The original treatment helper failed before launching the scientific parent because `add_shared_persistence()` was applied to wrapper text instead of the generated M5/H36 runtime source. No result from that incomplete attempt is reused here.

Harness fix preregistration:
`research/stretch/m5-h36-shared-stage-persistence-023-harness-fix1.md`

## Frozen provenance

STREAMED control:
- `scripts/stretch_five_token_h36_hotset_variant_022.py`
- blob `9111dde483206a774a9fe5426522dab6e77cecca`.

PERSISTENT treatment, harness fix1:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

Balanced fix1 runner:
- `scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023_fix1.py`
- blob `dfa4c25b71108e258f4d311a65ae038b45be16dc`.

The broken helper and original runner remain preserved and are not overwritten.

## Frozen scientific design

Balanced order:
`STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`.

Scientific factor only:
- STREAMED: embedding, final RMSNorm and LM head reconstructed/materialized per pass;
- PERSISTENT: the same three shared stages materialized once and retained.

Unchanged:
- exact oracle block size `M=5`;
- H36 transformer hotset, layers `0..35`;
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1;
- ordinary BF16 KV;
- exact position-logit/top-1 gates;
- host/resource/I-O policy;
- no tokenizer, sampling, real drafter, prefetch, KV quantization, runtime upgrade, download or cache purge.

The one-time PERSISTENT shared setup remains excluded from the steady-state target rate and is reported separately as preregistered.

## Controlled result

All four fix1 constituent runs passed the inherited correctness, provenance and resource gates.

Target verification:
- STREAMED pooled rate: `2.2094465476329797 token/s`;
- PERSISTENT pooled rate: `3.532597336303855 token/s`;
- PERSISTENT/STREAMED ratio: `1.5988607373590418x`;
- controlled steady-state improvement: **~59.89%**.

Target block wall:
- STREAMED median: `2.2416415 s`;
- PERSISTENT median: `1.416072 s`;
- reduction: **~36.83%**.

Shared-stage attribution:
- PERSISTENT/STREAMED median shared-materialization ratio: `0.0001720537125220692x` (~99.9828% lower);
- PERSISTENT/STREAMED median shared-forward ratio: `0.7076299067105323x` (~29.24% lower);
- PERSISTENT/STREAMED mean full-pass process-read bytes/block ratio: `4.009422142033779e-05x` (~99.9960% lower);
- PERSISTENT/STREAMED shared-materialize process-read ratio: `0.0x`.

Raw-weight residency:
- STREAMED persistent raw weights: `3,039,381,504 B`;
- PERSISTENT persistent raw weights: `3,583,928,320 B`;
- full model raw weights are persistent in the treatment.

One-time full-persistence setup:
- mean shared setup wall: `0.3723145 s`;
- estimated break-even: `0.439246432072825` target blocks.

Resource telemetry:
- STREAMED minimum observed free memory: `21%`;
- PERSISTENT minimum observed free memory: `23%`;
- STREAMED peak observed swap: `2335.5 MB`;
- PERSISTENT peak observed swap: `2487.69 MB`.

Disk free after:
`~35.673 GiB`.

## Canonical interpretation

Full raw-weight persistence is a strong controlled win under the frozen M5/H36 architecture. Persisting embedding, final RMSNorm and LM head raises the balanced steady-state oracle target-verification rate by ~59.89% while preserving exactness and all inherited resource gates.

The effect aligns with removal of shared-stage rematerialization and process-read pressure. The one-time setup cost is small relative to the observed steady-state block-wall saving: the estimated break-even is below one M5 target block under this run.

The higher observed minimum-free percentage for PERSISTENT must **not** be interpreted as lower intrinsic RAM consumption; system-wide memory observations are host-state dependent. The causal conclusion comes from the balanced within-experiment performance comparison.

Absolute token/s values from other Stretch runs remain non-causal across experiments; only balanced within-experiment ratios are used for architecture decisions.

## Decision

1. Freeze **M=5 + H36 + full raw-weight persistence** as the best demonstrated target-side architecture under MLX 0.31.2.
2. Close the raw-weight residency axis: there are no remaining model weights to make persistent.
3. Preserve `20260820-151540` as a harness defect with no scientific result.
4. Move to an independent compute/kernel attribution experiment before changing runtime or integrating a real drafter.
5. A newer MLX version, if tested, must remain a separately preregistered environment factor and must not redefine the frozen 0.31.2 evidence.
