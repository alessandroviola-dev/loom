# LOOM Stretch 021 — M5 H24 vs H32 Balanced Hotset Comparison — Preregistration

Status: **READY / FROZEN BEFORE RUN**

## Question

Under the frozen exact `M=5` target-verification path, does increasing persistent transformer residency from 24 to 32 layers improve controlled target-verification throughput while preserving numerical correctness and the existing 8 GB resource gates?

## Frozen baseline

Model/runtime:
- Qwen3-8B 3-bit/group64
- MLX 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- Apple M1 / 8 GB reference system.

Target path:
- exact oracle block size `M=5`
- three 5-token target traversals over the frozen first-15 oracle sequence
- ordinary BF16 KV
- resident sequential control
- exact numerical parity and top-1 gates
- shared stages remain streamed
- inherited Darwin process-I/O attribution
- inherited host/resource gates
- no real drafter
- no tokenizer/sampling change
- no KV quantization
- no prefetch/double buffering
- no runtime upgrade
- no deliberate cache purge
- no threshold relaxation.

Frozen H24 source:
- `scripts/stretch_five_token_h24_hotset_variant_020.py`
- blob `09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`
- persistent transformer layers `0..23`.

Frozen H32 helper:
- `scripts/stretch_five_token_h32_hotset_variant_021.py`
- blob `b6b39dfb095b905ed659d52903309783efc02be7`
- persistent transformer layers `0..31`.

Balanced comparison runner:
- `scripts/stretch_m5_h24_h32_balanced_hotset_comparison_021.py`
- blob `fa52f21a7ae02a4fcae6c73416ad2ef63cc0ae45`.

## Single scientific factor

Persistent transformer residency only:
- H24: layers `0..23`
- H32: layers `0..31`.

No other scientific factor may change within Stretch 021.

## Expected raw-weight geometry

Per frozen transformer layer:
`84,427,264 B`.

H24:
- persistent hotset: `2,026,254,336 B`
- nominal hybrid raw-weight budget with the previously observed maximum shared stage `272,269,312 B`: `2,298,523,648 B`.

H32:
- persistent hotset: `2,701,672,448 B`
- nominal hybrid raw-weight budget with the same shared-stage size: `2,973,941,760 B` (~2.77 GiB).

The hybrid values are raw-weight accounting, **not** total system RAM consumption. System-wide free memory and swap gates remain decisive.

## Balanced execution order

`H24 -> H32 -> H32 -> H24`

No deliberate cache purge or cache-state manipulation is allowed between attempts.

The ABBA order is intended to reduce simple first/last-run host-cache ordering bias; it does not make Darwin process-I/O accounting forensic.

## Constituent-run requirements

Every one of the four constituent runs must independently:
1. exit successfully;
2. reach inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`;
3. expose exact expected hotset IDs;
4. retain `M=5`;
5. accept all 15 frozen oracle tokens;
6. satisfy inherited numerical/top-1/KV/I-O/host/resource gates.

Expected hotset provenance:
- H24 = exactly `[0, ..., 23]`
- H32 = exactly `[0, ..., 31]`.

If any constituent run fails, abort the comparison as:
`HOTSET_COMPARISON_INCOMPLETE`.

No winner may be inferred from a partial sequence. No automatic rescue/rerun, gate weakening, or replacement variant is allowed.

## Primary PASS classification

`M5_H24_H32_BALANCED_HOTSET_COMPARISON_PASS`

This classification requires all four constituent runs to satisfy the requirements above and the aggregate comparison to complete.

## Primary comparison outputs

For H24 and H32 separately, aggregate:
- pooled accepted-token target-verification token/s
- median target-block full-pass wall
- median materialization wall
- median forward wall
- mean process-read bytes per full target block
- mean materialization process-read bytes per block
- process-read bytes per accepted token
- persistent hotset bytes
- hybrid raw-weight budget
- minimum observed system free-memory percentage
- peak observed swap.

Report H32/H24 ratios for:
- pooled target rate
- median block wall
- median materialization wall
- median forward wall
- full-pass process-read bytes/block
- materialization process-read bytes/block
- hotset bytes.

## Decision rule

If H32 passes and materially increases controlled pooled target rate while retaining acceptable resource headroom:
- freeze H32 as the best demonstrated residency point;
- consider H36 only as a new, separately preregistered ceiling experiment.

If H32 is flat/slower despite passing:
- stop increasing residency at H32;
- retain the faster controlled point;
- move to another independent speed axis such as prefetch/double buffering.

If H32 fails an inherited resource/correctness gate:
- preserve the failure as the boundary result;
- do not weaken gates;
- do not attempt H36 as an unchanged continuation.

## Non-claims

Stretch 021 does not establish:
- real speculative decoding speed;
- draft-model acceptance/cost;
- rejection/rollback behavior;
- interactive usability;
- a causal comparison against historical absolute rates from separate Stretch runs.

The oracle target rate remains an upper-bound target-side measurement.

## Exact run commands

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_h32_hotset_variant_021.py
python3 -m py_compile scripts/stretch_m5_h24_h32_balanced_hotset_comparison_021.py
python3 scripts/stretch_m5_h24_h32_balanced_hotset_comparison_021.py
```

No download is expected.
