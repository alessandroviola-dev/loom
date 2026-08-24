# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_CONTROL_ADAPTER_PARITY_FAIL`
Strategic next: `LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical long-lived context is in `/AGENTS.md`.

## Proven DFlash chain

- target tap interface `[1,12,23,34,45]` established;
- exact B7 wavefront verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- corrected MLX/reference proposal parity 63/63.

First E2E:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Memory/performance remediation remains deferred while acceptance is zero.

## Frozen-state compatibility history

Frozen target continuation:
- independent-oracle historical overlap 45/45;
- complete 63/63 target token reference;
- deterministic/finite;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit on frozen target-tap states:
- target token replay/control 63/63 PASS;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal target ranks structurally distant;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

Important: this verdict remains valid for the frozen states but is no longer sufficient as a live-target statement until target-tap replay provenance is restored.

## Target identity / BF16 preflight

Identity audit:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

No material non-quantization architecture/tokenizer/vocab/mapping mismatch was found. Local material delta is MLX affine 4-bit, group 128.

Unquantized-control preflight:
- pinned upstream BF16 control candidate identified;
- 16 shards, ~61.1 GB total;
- full snapshot rejected because it exceeds available/staging disk budget;
- bounded range/shard control designed;
- BF16 reader/math adapter required.

## P1_t01 range control — STOP at adapter gate

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`
classified `CONTROL_ADAPTER_PARITY_FAIL`.

Gate A result:
- adapter vs current Q4 oracle: bitwise parity PASS;
- current Q4 router/logits/greedy and deterministic rerun: PASS;
- current Q4 vs frozen `P1_t01` taps: FAIL at all 5 DFlash taps;
- first mismatch: layer 1;
- finite/no-leak PASS;
- BF16 access 0 B; peak dedicated disk 0 B.

Therefore BF16/quantization has not been tested yet.

## Next — Q4 tap replay drift diagnostic

Checkpoint:
`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001`

Purpose:
Before any BF16 access, determine why the same nominal `P1_t01` Q4 state no longer reconstructs the frozen taps while downstream router/logit/greedy behavior remains correct.

Audit:
1. exact frozen/current prefix token IDs, lengths and hashes;
2. state-position semantics and off-by-one possibilities;
3. exact tap capture semantics/timing/dtype/shape;
4. model/config/quantized weight provenance and hashes where available;
5. freeze-time vs current target/runtime/script provenance;
6. layer-by-layer current-vs-frozen hidden comparison to find the earliest mismatch;
7. router/logit/token controls.

Decision:
- prefix/position/capture/code mismatch proven -> repair only that variable, then revalidate/refreeze the affected tap corpus;
- exact replay provenance matches but hidden states deterministically differ -> classify genuine Q4 hidden-state drift and localize earliest differing operation;
- if the refrozen/current tap corpus changes materially, rerun the compatibility audit before returning to BF16;
- only after Q4 tap replay integrity is restored may the bounded BF16 one-factor control resume.

Restrictions:
- no BF16 weight access;
- no DFlash proposal/full-E2E run;
- no memory/performance remediation;
- no causal quantization claim.

## Later order

1. Q4 tap replay drift diagnostic;
2. repair/refreeze tap corpus if necessary;
3. rerun compatibility on current/live-consistent taps if needed;
4. resume bounded BF16 control;
5. determine DFlash salvageability;
6. memory remediation only after nonzero useful acceptance;
7. full E2E economics/capability/context if DFlash becomes viable;
8. otherwise return to the next high-leverage LOOM architecture/I/O branch.

## Token-efficient Pi workflow

Root `/AGENTS.md` is persistent context. Pi prompts carry only the active delta. Pi executes local work; ChatGPT owns Git/HANDOFF/ROADMAP.