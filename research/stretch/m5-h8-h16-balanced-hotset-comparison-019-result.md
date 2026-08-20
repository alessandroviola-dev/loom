# LOOM Stretch 019 — M5 H8 vs H16 Balanced Hotset Comparison — Result

Date: 2026-08-20
Status: COMPLETE PASS
Classification: `M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`

## Run

Valid run:
`results-local/stretch/m5-h8-h16-balanced-hotset-comparison-019/20260820-132820`

Parent runner:
`scripts/stretch_m5_h8_h16_balanced_hotset_comparison_019.py`

Frozen parent runner blob:
`8ad0666624069d4852daed1188d634806b570ecc`

Frozen H8 source:
- `scripts/stretch_five_token_oracle_block_confirmation_017.py`
- blob `6171440736badf5150297f9c8945209fe49d0826`

Frozen H16 source:
- `scripts/stretch_five_token_h16_hotset_variant_019.py`
- blob `6a0bd001ad7a5a5bf5646b54a302f7fc372e4367`

Balanced order:
`H8 -> H16 -> H16 -> H8`.

No deliberate cache purge.

## Frozen scientific context

Preserved:
- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- exact M=5 oracle geometry
- resident sequential control
- ordinary BF16 KV
- streamed layers outside the persistent hotset
- shared-stage streaming
- exact numerical/top-1 gates
- Darwin process-I/O accounting
- host/resource safety gates
- no real drafter
- no runtime upgrade
- no threshold relaxation
- no deliberate cache purge.

Single scientific factor:
- persistent transformer hotset `H8 = layers 0..7`
- versus `H16 = layers 0..15`.

Every constituent run independently passed the inherited scientific gates and hotset provenance checks.

## Primary result

H8 pooled target-verification rate:
`1.6634679102900627 token/s`

H16 pooled target-verification rate:
`2.609454209167065 token/s`

H16/H8 target-rate ratio:
`1.568683226784969`

Therefore H16 improves the controlled pooled target-verification rate by approximately **56.87%**.

Observed higher pooled target rate: `H16`.

## Timing attribution

Median target-block wall:
- H8: `3.2671415 s`
- H16: `1.8776220000000001 s`

H16/H8 median block-wall ratio:
approximately `0.5747`, i.e. about **42.5% lower** wall time per M5 target block.

H16/H8 median materialization ratio:
`0.10130580024003226`

This corresponds to approximately **89.87% lower median materialization time**.

H16/H8 median forward ratio:
`0.8922774748455992`

This corresponds to approximately **10.77% lower median forward time**.

The much larger materialization reduction than forward reduction identifies residency/materialization as the dominant source of the H16 speedup.

## I/O attribution

H16/H8 mean full-pass process-read bytes/block ratio:
`0.04627184541030809`

Under the inherited Darwin process-I/O accounting, H16 therefore reduced full-pass process-read bytes/block by approximately **95.37%** relative to H8 in this balanced run.

This is diagnostic process accounting rather than forensic proof of physical SSD reads, but the direction and magnitude are consistent with the measured materialization improvement.

## Residency / memory

Persistent hotset:
- H8: `675,418,112 B`
- H16: `1,350,836,224 B`

Minimum observed free memory:
- H8: `20%`
- H16: `22%`

Do not interpret the higher H16 minimum-free sample as proof that H16 intrinsically uses less system memory. It only establishes that the H16 constituent runs remained within all inherited resource gates under the observed host states.

Disk free after:
`35.684 GiB`.

## Canonical interpretation

Stretch 019 confirms that increasing persistent transformer residency is a high-leverage speed axis for the exact M=5 streamed target path.

Under balanced host/cache ordering:
- H16 is materially faster than H8;
- the speedup is dominated by lower materialization and process-read cost, not a large change in pure forward compute;
- H16 remains scientifically valid and resource-safe under the inherited gates.

Canonical current exact profile:
- exact oracle block frontier: `M=5`
- preferred demonstrated residency point: `H16`
- controlled target-verification rate: `2.609454209167065 token/s`.

## Decision

1. Freeze H16 as the preferred demonstrated M=5 hotset point.
2. Keep M=5 fixed; do not reopen block-size scaling under MLX 0.31.2.
3. Continue the same single-factor residency curve with H24 before introducing prefetch, runtime upgrades, KV changes, or a real drafter.
4. Preserve all resource/parity gates unchanged.
5. If H24 fails a host/resource/correctness gate, preserve the failure and do not weaken the gate.

## Non-claims

- This remains an oracle target-verification upper bound, not end-to-end speculative decoding throughput.
- No real drafter cost, rejection, rollback, or acceptance-rate penalty is represented.
- The ~20 token/s usability target is unchanged.
- Process-read accounting is diagnostic and host/cache-state sensitive.
