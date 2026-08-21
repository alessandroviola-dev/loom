# REALGEN 002 — M1 qmv_fast tuning feasibility

Date: 2026-08-21
Status: **`REALGEN_002_M1_QMV_FAST_NO_GO`**

## Question and boundary

Can a new process-local M1 `S1_R8` qmv kernel accelerate real M1 generation while remaining bit-exact? This is feasibility only. It does not reopen Stretch 037–041, does not use MLX 0.32, and does not test a drafter. REALGEN 001 remains the canonical serving baseline: **13.184615357 generation tok/s**, **12.046861457 end-to-end tok/s**, ordinary built-in M1 qmv_fast, BF16 KV.

## Git and host gate

Before work: branch `research/stretch-015-divergence-attribution`; HEAD and origin were `1c8e89e971a2710e3da8c77c903eb6c59c570620`; divergence `0 0`; clean tree; merge-base with `main` `f345bcf0c98e8747531a56a7df14c95cc4f40efb`.

The decisive pre-load sample was **73% free** and **1804.88 MB swap**, passing the unchanged >=60% / <=5600 MB gate. No purge, process termination, allocation, cache manipulation, gate modification, installed-MLX modification, or target-time JIT was used.

## Exact M1 dispatch and payloads

Pinned MLX source is v0.31.2 `68cf2fddd8de5edd8ab3d926391772b2e2cedad8`, on Apple M1 `applegpu_g13g` (gen13). The affine BF16 / 3-bit / group64 / transpose=true M=1 predicate `N % 8 == 0 && K % 512 == 0` resolves CONTROL to:

`affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0`

Canonical grid is `(1, N/8, 1)`, TG `[32,2,1]`: two SIMD groups, four rows/SIMD, eight rows/TG. The audit retained packed 3-bit (8 values/3 bytes), 16 activation values/lane, 512-K blocks, row + lane/4 scale/bias addressing, x scaling/sum order, float accumulation, `simd_sum`, BF16 store and output layout.

Actual M1 activations were captured at early/middle/late positions 0/4/9 of the frozen public REALGEN-001 `chat_02` replay, for q/k/v/o/gate/up/down at layers 0/18/35 plus LM head: 66 payloads total. Observed shape classes were `4096→4096`, `4096→1024`, `4096→12288`, `12288→4096`, and LM head `4096→151936`.

MLX 0.32 was not run. Provenance only: upstream split-K #3120 concerns small-M qmm, and `qmv_split_k` was removed before merge; this M1 path is qmv_fast.

## Clone admission

The distinct M1 `s2_r4` process-local canonical clone preserved all cited qmv_fast invariants. Against built-in CONTROL across all 66 actual payloads it was shape/BF16/bit exact with max and mean absolute difference **0**. Worst clone/control median ratio was **1.097680**, below 1.50. Clone admission passed.

## Sole treatment and isolated timings

TREATMENT was **M1_S1_R8**, a new M1-specific process-local implementation: one SIMD group/TG, eight rows/SIMD, eight rows/TG. It is not a claim that Stretch-037 M5 S1_R8 was promoted to M1. Five K/N specializations covered all projection classes including LM head; algorithm and geometry were unchanged by projection.

All 66 direct treatment-vs-built-in comparisons were shape/BF16/bit exact, with max and mean absolute difference **0**. Each cell below is the mean over layers 0/18/35 for the named real replay position; each underlying payload used 40 excluded warmups and 120 synchronized samples/side in `C -> T -> T -> C`. Values are CONTROL/TREATMENT median microseconds (ratio; saved µs). Per-payload medians/p25/p75 are in the evidence JSON.

| projection | early | middle | late |
|---|---:|---:|---:|
| q | 614.95/630.99 (1.0261; -16.03) | 628.94/646.87 (1.0285; -17.94) | 633.74/653.72 (1.0315; -19.98) |
| k | 463.51/486.12 (1.0488; -22.62) | 462.15/483.06 (1.0452; -20.91) | 404.83/422.68 (1.0441; -17.85) |
| v | 441.52/461.11 (1.0444; -19.59) | 466.93/494.38 (1.0588; -27.45) | 495.67/520.67 (1.0505; -25.01) |
| o | 675.86/702.12 (1.0388; -26.26) | 602.10/621.32 (1.0319; -19.22) | 628.28/652.57 (1.0387; -24.29) |
| gate | 1099.01/1079.81 (0.9825; +19.21) | 1091.01/1070.90 (0.9816; +20.10) | 1091.06/1068.19 (0.9790; +22.87) |
| up | 1060.33/1036.58 (0.9776; +23.76) | 1031.63/1007.09 (0.9762; +24.54) | 1018.80/992.87 (0.9745; +25.93) |
| down | 1055.30/1054.13 (0.9989; +1.17) | 1007.24/993.94 (0.9868; +13.30) | 1062.01/1059.35 (0.9975; +2.66) |
| LM head | 5331.96/5260.83 (0.9867; +71.12) | 5326.13/5289.81 (0.9932; +36.31) | 5271.06/5272.52 (1.0003; -1.46) |

The MLP classes improve, but q/k/v/o regress; LM-head evidence is near flat. The direct actual-payload arithmetic estimate is **-3729.997 µs/token** over 36 transformer layers (LM head excluded), already a projected slowdown; it is superseded by representative replay evidence.

Factory cost was 0.68 ms for the five treatment specializations (canonical clone factory 4.57 ms). Separately measured first-dispatch/JIT-plus-materialization costs were 2.60–21.36 ms per treatment shape (clone: 1.86–6.14 ms); all were outside replay timing, and target-time recompilations were zero.

## Ten-token full M1 replay

One frozen public `chat_02` prompt and existing REALGEN-001 generated IDs `[334, 19641, 12, 8304, 9680, 369, 264, 43354, 42700, 8821]` were replayed with independent BF16 KV states. Both sides retained full raw weights (`lazy=False`, materialized), identical model/runtime/KV/cleanup, and `gc.collect() -> mx.clear_cache() -> gc.collect()` after ten committed tokens.

All ten positions had exact logits, equal top-1, the fixed exact replay sequence, and equal cache offsets. No sampling or oracle acceptance claim was used.

After excluded C/T warmups, the balanced target schedule `C -> T -> T -> C` measured:

- CONTROL wall: **0.779169 s** median; **12.834182 tok/s** equivalent.
- M1_S1_R8 wall: **0.857916 s** median; **11.656154 tok/s** equivalent.
- Treatment/control wall ratio: **1.101065**.
- Balanced throughput change: **-9.178832%** (slower), versus the required +5%.

The full implementation-path treatment includes its required process-local QuantizedLinear dispatch and therefore is the causal feasibility result; isolated MLP-kernel improvements do not overcome the complete M1 path.

## Resources and decision

Final diagnostic state: 25% free memory, 2111.75 MB swap, MLX active/peak/cache `3,594,430,472 / 3,775,277,456 / 40,861,884 B`, and RSS diagnostic 1,772,044,288 B. This remained above the <5% / >5600 MB runtime abort thresholds and added no persistent model-weight expansion.

**NO-GO.** Although clone admission, bit exactness, replay correctness, resource safety, and zero target-time recompilation passed, the complete balanced M1 replay was 9.18% slower and cannot meet the >=5% upside gate. Do not create REALGEN 003 or run the six-prompt comparison. Retain built-in MLX 0.31.2 M1 qmv_fast as REALGEN serving CONTROL.

## Evidence

- Harness: `scripts/loom_realgen_m1_qmv_tuning_002_feasibility.py`
- Complete evidence: `results-local/realgen/m1-qmv-tuning-002-feasibility/20260821-083048/summary.json`
- A first run at `20260821-082613` is preserved as an excluded harness-label defect: it reported the MLX dtype display string rather than dtype identity, despite already measuring exact zero-difference outputs. The corrected harness uses `dtype == mx.bfloat16`. The intermediate `082720` no-go is preserved; final `083048` adds separately measured first-dispatch/JIT telemetry before excluded warmups and is the authoritative result.
