# REALGEN 001 — real autoregressive generation baseline

Date: 2026-08-21
Status: **`REALGEN_001_NOT_STARTED_HOST_NOT_READY`**

## Scope and hard boundary

REALGEN 001 is an operational, end-to-end baseline for real greedy generation,
not a new optimization factor.  It uses the exact local Qwen3-8B target, with
unknown future tokens generated and committed one at a time.  It contains no
oracle continuation, speculative decoding, drafter, prompt lookup, Medusa,
lookahead, or sampling.

This report deliberately distinguishes:

- **TARGET VERIFICATION M5:** the previously validated oracle/known-future
  target-verification configuration; and
- **REAL AUTOREGRESSIVE GENERATION M1:** the required ordinary built-in MLX
  path which predicts one unknown next token, commits it, updates BF16 KV for
  subsequent predictions, and repeats.

M5 oracle-verification throughput is **not** real-chat generation throughput.
No M5 figure is presented as a serving rate, and no historical ratio is
multiplied to invent a REALGEN result.

## Host gate result

The pre-launch sample recorded in
`results-local/realgen/real-generation-baseline-001/20260821-075158/run-status.json`
was:

| gate | observed | required | result |
|---|---:|---:|---|
| free system memory | 54% | >=60% | fail |
| swap used | 669.88 MB | <=5600 MB | pass |

No model was loaded by the runner, no prompt was benchmarked, and no generation
or reference-correctness attempt was consumed.  No cache purge, memory
manipulation, automatic process kill, or retry was performed.  The result is
therefore exactly **`REALGEN_001_NOT_STARTED_HOST_NOT_READY`**, not a
correctness or performance result.

## Frozen research baseline retained

The prior validated verifier configuration remains preserved without claiming
that it directly emits five unknown future tokens:

- Qwen3-8B, affine 3-bit/group64, BF16;
- Apple M1 / 8 GB, `applegpu_g13g`;
- MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1;
- H36, full raw-weight persistence, ordinary BF16 KV;
- M5 target verification;
- M1-specific S1_R8 only at its validated source identity;
- one exact cleanup event per two M5 verifier blocks:
  `gc.collect() -> mx.clear_cache() -> gc.collect()`.

The valid Stretch-038 S1_R8/two-M5 verifier treatment recorded a 10-token
constituent wall of 1.429525625 s (13.990655117 oracle-verification tok/s).
That evidence is retained only as **M5 verification** evidence.

## M1 dispatch and legality audit

The audit is source-identity based and required no model execution:

1. The exact Stretch-037 injection (`scripts/stretch_m1_qmv_fast_runtime_037.py`,
   blob `a65776177b8e988939d1a95a821469e0a9c41f83`) has the literal eligibility
   guard `x_value.shape[-2] == 5`.  Therefore **S1_R8 is ineligible at M1**.
   It is not installed, modified, tuned, or promoted in REALGEN 001.
2. For affine BF16/group64/3-bit Qwen3 M1 projection inputs, existing
   Stretch-035 source evidence maps the transformer q/k/v/o/gate/up/down
   `QuantizedLinear` operations to built-in MLX qmv_fast on M1/gen13.  The
   built-in M1 path is the only path the new driver uses.
3. Qwen3 attention retains its ordinary source path: q/k/v projections,
   q/k RMSNorm and layout, RoPE at the cache offset, `KVCache.update_and_fetch`,
   built-in causal GQA SDPA, output projection, residual and MLP.  The M1
   cache is the ordinary MLX-LM BF16 prompt cache.
4. The untied quantized LM head remains ordinary built-in `QuantizedLinear`
   / `mx.quantized_matmul`; it is not an S1_R8 shape and remains built-in.
5. The operational cleanup schedule in the driver is conservative and explicit:
   one identical `gc.collect() -> mx.clear_cache() -> gc.collect()` event after
   each ten committed generated tokens.  This translates the promoted
   one-event/two-M5 verifier operation for baseline stability; it is **not** a
   new scientific cadence or optimization claim.

## Tokenizer and chat-template identity

The prepared driver uses the local target tokenizer and normal chat template,
not arbitrary token IDs.  Static identity:

- tokenizer class: `Qwen2Tokenizer` through mlx-lm `TokenizerWrapper`;
- base vocabulary: 151643; model-config effective vocabulary: 151936;
- config BOS ID: 151643 (`<|endoftext|>`); tokenizer `bos_token` is null;
- EOS ID: 151645 (`<|im_end|>`);
- chat template: `tokenizer_config.json` normal Qwen3 chat template,
  SHA-256 `87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5`,
  `add_generation_prompt=true`, `enable_thinking=false`;
- SHA-256: `tokenizer.json` `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`;
  `tokenizer_config.json` `253153d0738ceb4c668d2eff957714dd2bea0b56de772a9fdccd96cbf517e6a0`;
  `special_tokens_map.json` `76862e765266b85aa9459767e33cbaf13970f327a0e88d1c65846c2ddd3a1ecd`.

The harness freezes six public, non-sensitive prompts: two ordinary assistant,
two coding/software, and two reasoning/technical prompts. Their exact text,
post-template token IDs/counts, reference IDs, and benchmark IDs are emitted
only after a host-ready execution. None has been timed yet.

## Prepared reference/correctness and metrics protocol

For every frozen prompt the driver will first run ordinary supported
`mlx_lm.generate_step` with greedy `argmax`, then compare its complete generated
ID sequence to the minimal direct M1 loop exactly. A mismatch is
`REALGEN_BASELINE_CORRECTNESS_FAIL` and stops the phase. The planned length is
128 generated tokens unless EOS occurs naturally; EOS is recorded and actual
committed output tokens are used in all aggregates.

Model loading, materialization, and separate M1/BF16-KV warmup are excluded
from benchmark timing but recorded. Per prompt the future host-ready run will
record prefill wall/rate, TTFT, generation-only and end-to-end walls, tok/s,
per-token latency distribution, EOS, cleanup wall, free memory, swap, MLX
active/peak/cache, and diagnostic RSS. No deliberate purge will occur between
prompts.

## Speculative-decoding readiness

REALGEN M1 wall/token and its real baseline rate do not exist yet, so the
requested complete break-even table is intentionally **deferred** rather than
fabricated. The retained M5 verifier datum is 0.7147628125 s per two-block
constituent / 0.35738140625 s per M5 block under Stretch-038 treatment. It is
not substituted for the missing M1 number.

After a successful baseline, the table will use, explicitly:

- `t_m1`: measured REALGEN M1 generation wall/token;
- `t_m5`: valid M5 verifier wall/block with its cleanup semantics stated;
- maximum draft wall at 20 tok/s: `accepted/20 - t_m5`;
- required mean accepted tokens: `20 * (t_m5 + draft_wall)`;
- several zero-to-positive draft-cost scenarios, bounded by the M5 proposal
  geometry rather than assumed feasible.

No draft model was downloaded or tested. The next separately authorized DRAFT
001 may consider `mlx-community/Qwen3-0.6B-4bit`, but must independently verify
tokenizer identity, vocab IDs, chat-template compatibility, speed, and RAM
footprint before use.

## Resume condition

Wait for a natural host state satisfying free memory >=60% and swap <=5600 MB.
Then rerun exactly:

```bash
results-local/mlx/venv-mlx-lm-0.31.3/bin/python scripts/loom_real_generation_baseline_001.py
```

Do not rerun Stretch 037–041.
