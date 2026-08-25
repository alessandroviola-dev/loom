# LOOM DFlash BF16 Tap Drafter Probe 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`
Classification: `NO_MATERIAL_RECOVERY`
Gate: `COMPLETE`

## Purpose

Test a one-factor intervention on frozen state `P1_t01`: keep the already validated DFlash drafter completely unchanged and replace only the five target tap tensors supplied to it from local Q4 values to exact pinned-upstream BF16 values.

The question is whether the material Q4/BF16 target-state drift measured in `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001` is sufficient to recover DFlash proposal compatibility.

## Frozen state and invariants

State:
- `P1_t01`;
- context length: 43 tokens;
- prefix SHA-256: `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`;
- positions: `0..42`;
- anchor position: 42;
- anchor token: 271;
- target taps: `[1,12,23,34,45]` as 1-based post-block outputs;
- pinned BF16 target top1: `12050`.

Unchanged DFlash path:
- drafter weights and architecture;
- parameter mapping;
- publisher mask;
- anchor semantics;
- proposal code;
- tokenizer;
- scoring implementation.

Only the five supplied target tap tensors changed Q4 -> BF16 in the treatment.

## Expensive-artifact recovery and persistent cache

The first probe gate found that the completed BF16 control had retained only summary metrics; the exact raw BF16 tap tensors had existed transiently and were not persisted. Classification at that point was `BF16_TAP_ARTIFACT_MISSING`.

A mechanical re-extraction was authorized without changing the scientific treatment. To prevent repeated expensive downloads, the re-extraction introduced persistent external research storage under:

`<external-archive>/`

Persistent BF16 cache:

`<external-archive>/bf16-cache/`

Persistent probe artifacts:

`<external-archive>/artifacts/dflash-bf16-tap-drafter-probe-001/20260825T084409Z/`

Final cache state:
- routed expert entries retained: `3,470`;
- routed expert cache: ~31 GiB;
- dense cache: ~2.9 GiB;
- total retained BF16 cache: ~33 GiB;
- initial cache build: `3,470` misses / new entries;
- initial expert network payload: `32,747,028,480 B`;
- final re-extraction: `3,470` HDD cache hits;
- final re-extraction network payload: `0 B`;
- final re-extraction retries: `0`.

The external cache is mechanical infrastructure only and did not alter model math or the scientific treatment.

## BF16 artifact retention

Exact retained BF16 artifacts validate:
- taps dtype: float32;
- aggregate tap shape: `[5,43,2048]`;
- all five taps finite;
- hashes valid;
- BF16 target top1: `12050`.

Re-extraction parity PASS:
- deterministic;
- finite;
- no routed-expert leak;
- all required tap metrics match the completed BF16 control;
- final-hidden metrics match;
- final-logit metrics match;
- BF16 margin matches;
- top-5 overlap matches.

Therefore the persisted BF16 taps are a valid replay of the completed control rather than a new target state.

## Drafter probe measurements

### Q4-tap baseline

- proposal token: `1778`;
- proposal rank in pinned BF16 target distribution: `41641`;
- BF16-target top-5 compatibility: false;
- BF16-target top-10 compatibility: false;
- BF16-target top-50 compatibility: false;
- deterministic: PASS;
- finite: PASS.

This reproduces the expected frozen P1_t01 proposal baseline.

### BF16-tap treatment

- proposal token: `1778`;
- proposal rank in pinned BF16 target distribution: `41641`;
- BF16-target top-5 compatibility: false;
- BF16-target top-10 compatibility: false;
- BF16-target top-50 compatibility: false;
- deterministic: PASS;
- finite: PASS.

The treatment therefore produces no token-level or rank-level compatibility recovery.

### Drafter distribution movement

Q4-tap vs BF16-tap proposal-logit metrics:
- max abs: `2.72215`;
- mean abs: `0.343385`;
- RMSE: `0.432349`;
- relative-L2: `0.215100`;
- cosine: `0.977013`.

Thus the BF16 tap intervention materially changes the drafter logit distribution, but the change is not sufficient to alter the top proposal or improve its rank under the BF16 target distribution.

Mask parity remained bitwise equal and only the tap hashes changed between baseline and treatment.

## Output-support observation

Target token `12050` is absent from the drafter's mapped ~32k output support for this state/path. Its drafter rank/probability is therefore unavailable in both Q4-tap and BF16-tap conditions.

This is a distinct mechanistic issue from target-tap precision drift. For `P1_t01`, exact proposal of target token `12050` is not possible through the current mapped drafter output support regardless of whether the supplied target taps are Q4 or BF16.

This checkpoint does not establish how common that support limitation is across the frozen 63-state corpus. A broader static support-coverage audit is required before attributing the earlier 0/63 compatibility result to output-support coverage.

## Interpretation

Measured facts:
1. Q4 -> BF16 target taps materially move the DFlash proposal-logit distribution (`relative-L2 0.215100`, cosine `0.977013`).
2. The drafter proposal remains exactly `1778`.
3. The proposal remains rank `41641` in the BF16 target distribution.
4. Top-5/top-10/top-50 compatibility remains false.
5. Target token `12050` is not representable by the current mapped drafter output support.

Scientific conclusion:
- simple target-tap precision drift is not sufficient to explain or repair the catastrophic DFlash incompatibility on `P1_t01`;
- precision drift still affects drafter internals, but the one-factor BF16-tap intervention produces `NO_MATERIAL_RECOVERY`;
- output-support coverage is now a higher-leverage structural hypothesis and should be audited before any additional expensive BF16 sweeps.

No causal claim is made from this single state.

## Evidence

Local:
`results-local/research/dflash-bf16-tap-drafter-probe-001/20260825T084409Z/`

External retained artifacts:
`<external-archive>/artifacts/dflash-bf16-tap-drafter-probe-001/20260825T084409Z/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

## Next checkpoint

`LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`

Goal: statically audit the validated drafter output mapping against the complete frozen 63-state target-token reference without running BF16 forwards or DFlash E2E.

Required questions:
- for each of the 63 frozen target next tokens, is that exact target token representable by the drafter mapped output support?;
- overall representable count / 63 and unsupported count / 63;
- unsupported states grouped by frozen prefix/state ID;
- whether the previous drafter/target top1 compatibility failures occur in representable or structurally unrepresentable states;
- verify mapping provenance and uniqueness before interpretation.

Decision:
- large unsupported fraction -> output-support coverage becomes a major structural explanation for zero acceptance/compatibility and must be understood before DFlash salvage;
- most/all target tokens representable -> support limitation is local to P1_t01 or a minority of states and other training/interface/distribution hypotheses remain primary.

This audit should be static/cheap and must not trigger model downloads, BF16 target execution, or E2E decoding.
