# REALGEN 001 — real autoregressive generation baseline

Date: 2026-08-21
Status: **`REALGEN_001_BASELINE_COMPLETE`**

## Scope and hard boundary

REALGEN 001 is an operational, end-to-end baseline for real greedy generation,
not a new optimization factor. It uses the local Qwen3-8B target and commits
unknown future tokens one at a time. It contains no oracle continuation,
speculative decoding, drafter, prompt lookup, Medusa, lookahead, or sampling.

This report deliberately distinguishes:

- **TARGET VERIFICATION M5:** prior oracle/known-future verifier evidence; and
- **REAL AUTOREGRESSIVE GENERATION M1:** the ordinary built-in MLX path that
  predicts, commits, and feeds each unknown next token through the BF16 KV
  cache.

M5 oracle-verification throughput is **not** real-chat generation throughput.

## Git and host gate

Git before the run was clean and coherent:

- branch: `research/stretch-015-divergence-attribution`;
- `HEAD` = `origin/research/stretch-015-divergence-attribution` =
  `871b2eac7dc997a0fc96e798af7bd66113401f87`;
- `origin...HEAD`: `0 0`;
- merge-base with `main`: `f345bcf0c98e8747531a56a7df14c95cc4f40efb`.

The passive sample immediately before launch was free memory **61%** and swap
**637.88 MB**, passing the unchanged `>=60%` / `<=5600 MB` gate. The runner's
own decisive pre-load sample was **62%** free memory and **637.88 MB** swap.
No purge, automatic/scripted process termination, pre-run `mx.clear_cache()`,
artificial allocation, swap manipulation, threshold change, or runner change
was used.

## Frozen runtime, M1 dispatch, tokenizer, and cleanup

- Apple M1 / 8 GB, `applegpu_g13g`; Qwen3-8B affine 3-bit/group64 BF16.
- Canonical launcher/prefix: `results-local/mlx/venv-mlx-lm-0.31.3`.
- Runtime: MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.
- Real generation geometry: M1, ordinary BF16 KV, greedy `argmax`, 128 tokens
  or natural EOS.
- Dynamic dispatch audit observed only the original built-in
  `QuantizedLinear.__call__`: M1 shapes K→N `4096→1024`, `4096→4096`,
  `4096→12288`, `12288→4096`, and LM head `4096→151936`. This confirms the
  ordinary built-in MLX M1 `qmv_fast` path.
- Stretch-037 S1_R8 was not injected: its exact identity guards
  `x.shape[-2] == 5`, so it is M5-only and ineligible at M1.
- `Qwen2Tokenizer` through mlx-lm `TokenizerWrapper`; base vocabulary 151643,
  effective model vocabulary 151936, config BOS 151643, EOS 151645
  (`<|im_end|>`). Normal Qwen3 chat template used with
  `add_generation_prompt=true`, `enable_thinking=false`; template SHA-256
  `87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5`.
- Cleanup was unchanged: `gc.collect() -> mx.clear_cache() -> gc.collect()`
  after each ten committed generated tokens. It is an operational stability
  translation, not a new promotion claim.

## Correctness, token counts, and per-prompt timing

The ordinary supported `mlx_lm.generate_step` greedy reference matched the
minimal direct M1 driver **exactly by complete generated-token-ID sequence for
all six prompts**. Exact prompt IDs, reference IDs, driver IDs, and each
per-token latency are preserved in the evidence summary.

| prompt | template tokens | output / EOS | prefill s (tok/s) | TTFT s | generation s (tok/s) | end-to-end s (tok/s) | cleanup s |
|---|---:|---:|---:|---:|---:|---:|---:|
| chat_01 | 44 | 108 / yes | 0.862805 (50.996) | 0.941177 | 8.123436 (13.294866) | 8.986241 (12.018373) | 0.629524 |
| chat_02 | 45 | 128 / no | 0.864547 (52.050) | 0.947422 | 9.706445 (13.187114) | 10.570992 (12.108608) | 0.746909 |
| code_01 | 57 | 128 / no | 0.853308 (66.799) | 0.931550 | 9.748159 (13.130684) | 10.601467 (12.073800) | 0.807203 |
| code_02 | 51 | 128 / no | 0.867829 (58.767) | 0.948506 | 9.675292 (13.229575) | 10.543120 (12.140619) | 0.801309 |
| reasoning_01 | 64 | 102 / yes | 0.866051 (73.899) | 0.943509 | 7.841881 (13.007083) | 8.707932 (11.713459) | 0.583857 |
| reasoning_02 | 51 | 128 / no | 0.857290 (59.490) | 0.936092 | 9.665580 (13.242868) | 10.522870 (12.163982) | 0.808345 |

Aggregate: **722** committed real generated tokens in **54.760794 s** gives
**13.184615 REAL generation tok/s**; end-to-end output is **12.046861 tok/s**
(59.932622 s). Total cleanup was **4.377148 s** across **68** cleanup events.
Flattened per-token forward latency (cleanup excluded) was min/p50/p95/max
**62.883 / 69.603 / 73.926 / 101.421 ms**.

## Resources and diagnostics

- Minimum free memory: **20%**; peak swap: **1591.19 MB**.
- MLX active memory was stable at **3,583,928,328 B**; observed peak was
  **3,826,575,836 B**. Final cache was **40,438,056 B**.
- Diagnostic process maximum RSS was **736,706,560 B**. RSS is diagnostic;
  system-wide free memory and swap are decisive.
- The initial model load/materialization (2.570621 s) and M1/BF16-KV warmup
  (9.686182 s; 108 tokens) were recorded but excluded from benchmark timing.

## M5 verifier versus M1 REALGEN

The retained Stretch-038 treatment is M5 oracle verification: 10 known tokens
in 0.7147628125 s, or **0.35738140625 s per M5 block** (13.990655117
oracle-verification tok/s). It does not predict five unknown future tokens and
is not a serving-rate substitute. The measured REALGEN result above is the
separate M1, unknown-future, BF16-KV rate.

## Speculative-decoding break-even arithmetic

No drafter was downloaded or tested. This is arithmetic only, using measured
`t_m1 = 54.7607935817 / 722 = 75.845974 ms/token` and retained verifier
`t_m5 = 357.381406 ms/block`. For a hypothetical M5 verification cycle with
mean accepted tokens `a` and draft wall `d`, rate is `a / (t_m5 + d)`.

| draft wall / M5 block | accepted needed to beat REALGEN M1 | rate at 5 accepted | accepted needed for 20 tok/s |
|---:|---:|---:|---:|
| 0 ms | 4.712 | 13.990655 tok/s | 7.148 |
| 5 ms | 4.778 | 13.797617 tok/s | 7.248 |
| 10 ms | 4.844 | 13.609834 tok/s | 7.348 |
| 20 ms | 4.976 | 13.249195 tok/s | 7.548 |

The existing M5 proposal is bounded at five accepted tokens. Even at zero draft
cost, reaching 20 tok/s would require 7.148 accepted tokens; the maximum
permitted draft wall at 20 tok/s for `a=5` is **-107.381 ms**, hence infeasible.
To merely exceed the measured REALGEN M1 rate at `a=5`, draft wall must be
strictly below **21.848 ms/block**. This does not authorize DRAFT 001.

## Evidence and checkpoint

- Complete machine evidence:
  `results-local/realgen/real-generation-baseline-001/20260821-081022/summary.json`.
- Run status:
  `results-local/realgen/real-generation-baseline-001/20260821-081022/run-status.json`.
- Classification: **`REALGEN_001_BASELINE_COMPLETE`**.
- Checkpoint: **`CHECKPOINT_REVIEW`**. Do not start DRAFT 001 automatically.
