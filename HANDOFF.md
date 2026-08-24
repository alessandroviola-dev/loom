# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — bounded BF16 control stopped before BF16 access because current Q4 replay no longer matches frozen P1_t01 taps; tap replay provenance diagnostic next
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_CONTROL_ADAPTER_PARITY_FAIL`
Next core checkpoint: `LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while preserving correctness, bounded memory and reproducible evidence.

Stable context lives in `/AGENTS.md`. Pi executes compact local WPs; ChatGPT owns Git/HANDOFF/ROADMAP and checkpoint administration.

## DFlash chain already proven

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Publisher target: `Qwen/Qwen3-30B-A3B`

Proven:
- target tap interface `[1,12,23,34,45]`;
- exact B7 wavefront target verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- corrected MLX/reference proposal parity 63/63.

First E2E remains rejected:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Do not optimize memory/performance while acceptance remains zero.

## Frozen target and compatibility history

Frozen continuation reference:
- 45/45 historical overlap;
- complete 63/63 token reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit on the frozen tap states:
- target replay/control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal ranks structurally far from target;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

This remains true for those frozen states. Its interpretation as live-target compatibility is now reopened because current Q4 no longer reconstructs the frozen P1_t01 taps bitwise.

## Target identity / BF16 preflight

Target identity audit:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

No material architecture/tokenizer/vocab/mapping mismatch was found. Material local delta remains MLX affine 4-bit (group 128).

BF16 preflight:
- pinned upstream control candidate available;
- full BF16 snapshot ~61.1 GB;
- full snapshot rejected due disk shortfall;
- bounded range/shard staging designed;
- no causal quantization claim yet.

## P1T01 bounded control — STOP before BF16

Checkpoint:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

Classification:
`CONTROL_ADAPTER_PARITY_FAIL`

Evidence:
`results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T161949Z/`

Result:
- frozen state `P1_t01`, context 43;
- adapter vs current Q4 oracle: bitwise parity PASS;
- current Q4 router/logits/greedy: PASS;
- deterministic/finite/no-leak PASS;
- current Q4 replay vs frozen P1_t01 taps: FAIL at all five taps `[1,12,23,34,45]`;
- first mismatch layer 1;
- BF16 weights not accessed;
- bytes fetched 0 B; peak dedicated disk 0 B.

Root observation:
The new adapter is not the immediate problem: it reproduces the current Q4 oracle. The problem is that the current Q4 oracle does not bitwise reproduce the earlier frozen tap artifact.

No BF16 comparison exists yet.

## Exact next step — Q4 tap replay drift diagnostic

Checkpoint:
`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001`

Goal: recover the exact provenance and replay contract of frozen `P1_t01` and localize the first reason its taps differ from current Q4.

Audit, without BF16:
1. exact frozen prefix token IDs, length, hash and state position;
2. whether `P1_t01` means the same target position in frozen and current paths;
3. tap contract: 1-based post-block outputs, dtype/shape/capture timing;
4. model/config/quantized weight provenance and hashes where available;
5. target/runtime/script provenance at freeze time vs current path where recoverable;
6. layer-by-layer current vs frozen hidden outputs to identify earliest mismatch;
7. router/logit/token controls to show downstream convergence/preservation.

Decision:
- proven prefix/position/capture/code mismatch -> repair only that mechanical variable and validate/refreeze affected tap states;
- identical replay provenance but deterministic hidden mismatch -> classify genuine Q4 hidden-state drift and localize earliest differing operation;
- do not resume BF16 control until tap replay integrity is restored or explicitly rebaselined under provenance.

Restrictions:
- no BF16 access;
- no DFlash proposals/E2E;
- no memory/performance remediation;
- no quantization-causality claim.

## Later order

1. Q4 tap replay drift diagnostic;
2. repair/refreeze current tap corpus if required;
3. rerun live compatibility check if frozen states changed materially;
4. resume bounded BF16 one-factor control only after Q4 tap replay integrity passes;
5. decide DFlash salvageability;
6. memory remediation only after useful acceptance.