# Stretch 033 candidate — M5 compiled Qwen3 MLP feasibility

Date: 2026-08-20  
Status: **NO-GO — diagnostic only; no Stretch 033 scientific runner, preregistration, preflight, or ABBA was created.**

## Mandatory Git audit before work

After `git fetch origin`, before any project modification:

```text
branch = research/stretch-015-divergence-attribution
status = clean
HEAD = 5f0d3003ffe8aad672fff219add157660ab9e5a4
origin/research/stretch-015-divergence-attribution = c73e2a89a3a9a8d3eb3637ed6c400bd9cff4b36a
origin...HEAD left/right = 0 / 6
merge-base(main, HEAD) = f345bcf0c98e8747531a56a7df14c95cc4f40efb
```

Thus the local branch had six unpushed commits and no remote-only commits. No pull, push, rebase, merge, PR, or main modification was performed.

## Scope and implementation

The factor is only an **outer** `mx.compile` around the real Qwen3 MLP expression at canonical M5:

```python
gate = quantized_matmul(x, gate_weight, gate_scales, gate_biases)
up = quantized_matmul(x, up_weight, up_scales, up_biases)
hidden = swiglu(gate, up)
out = quantized_matmul(hidden, down_weight, down_scales, down_biases)
```

CONTROL invokes this pure expression eagerly. TREATMENT invokes the same expression through MLX 0.31.2 `mx.compile(fun, inputs=layer0)`. `inputs=` explicitly captures the immutable real weight/scales/biases tree, so steady-state calls take only the unchanged BF16 M5 input. There is no manual qmatmul fusion, no row chunking, and no qmatmul parameter change.

An important local implementation fact: mlx-lm 0.31.3's `swiglu` is itself declared `@partial(mx.compile, shapeless=True)`. Therefore CONTROL is the uncompiled **outer MLP graph** used by the real Qwen3 implementation, while retaining its installed compiled SwiGLU helper; TREATMENT adds only the proposed outer MLP compile.

## Frozen diagnostic inputs

- Literal canonical launcher: `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`; child `sys.prefix` matched it.
- mlx/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`.
- Qwen3-8B 3-bit checkpoint SHA-256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`.
- Real layer-0 MLP payloads: gate/up `K=4096, N=12288`, packed U32 `12288×384`, BF16 scales/biases `12288×64`; down `K=12288, N=4096`, packed U32 `4096×1152`, BF16 scales/biases `4096×192`.
- Main probe: one reused BF16 `1×5×4096` input. Layers 0, 1, and 2 real MLP payloads were additionally retained only for the optional short depth probe; no model module or full model was built.

## Compile provenance and reuse

For layer 0, `mx.compile(...)` factory creation cost `0.000006834 s`; the first compiled invocation plus `mx.eval` cost `0.299160292 s`. Subsequent excluded compiled warmups had median `0.005603209 s`, so the first materialization contains an approximately `0.293557 s` one-time excess over steady execution.

The timed phase used the same compiled callable, same captured weight objects, and same `1×5×4096` BF16 input object throughout. It had 30 excluded warmups and 60 interleaved `EAGER → COMPILED → COMPILED → EAGER` cycles, yielding 120 synchronized samples per side. No deliberate cache purge occurred. MLX 0.31.2 exposes no public compile-count API; fixed shape/rank/dtype, one callable, separately measured first invocation, and no second compile-scale outlier are the available local evidence of reuse. The largest compiled timed sample was `2.436×` its median (`0.014407 s`), far below the `0.299160 s` first invocation.

## Exactness

Layer-0 eager and outer-compiled outputs both had shape `1×5×4096` and were bit-exact:

```text
exact_equal = true
max_abs_diff = 0.0
mean_abs_diff = 0.0
top1 = not applicable (MLP hidden-state output, not vocabulary logits)
```

The three-real-MLP sequence was likewise shape-equal and bit-exact. No scientific threshold was changed.

## Benchmark

Single real layer-0 MLP, milliseconds, 120 synchronized samples per side:

| Side | Median | p25 | p75 | Mean | Total wall |
|---|---:|---:|---:|---:|---:|
| Eager outer MLP | 5.9251 | 5.8339 | 6.0087 | 5.9519 | 0.714223 s |
| Outer compiled MLP | 5.9132 | 5.8471 | 5.9968 | 6.0181 | 0.722175 s |

`compiled/eager = 0.9979923`: a median difference of about `0.20%`, not a robust useful improvement.

Optional three-real-MLP depth probe (layers 0→1→2, 60 samples per side): eager median `16.7317 ms`, compiled median `16.7314 ms`, ratio `0.9999800`; it provides no accumulating graph-depth benefit. Its first invocation plus eval was `0.0278665 s` after the layer-0 compile had already warmed underlying runtime artifacts.

Diagnostic memory remained small relative to 8 GB: setup active `198,180,872 B`; single-MLP peak/active `199,065,608 / 198,492,168 B`; three-MLP peak/active `199,999,496 / 199,114,760 B`. This is compatibility telemetry only, not a full H36 residency claim.

## Diagnostic attribution

Standalone eager medians were gate qmatmul `2.3363 ms`, up qmatmul `2.3563 ms`, SwiGLU `0.3543 ms`, and down qmatmul `2.4449 ms`. Their separately synchronized sum exceeds the full eager MLP median, producing a negative descriptive residual (`-1.5667 ms`). This confirms that separate timing boundaries are not additive and does **not** identify an MLX internal kernel or establish that outer compile changed qmatmul scheduling. The evidence supports only: qmatmuls remained unmodified, and outer compilation did not yield a meaningful whole-MLP speedup.

## Estimated target-block effect

Applying the `0.2008%` single-MLP median fraction only to Stretch 028's diagnostic MLP time (`0.3265954 s/block`) estimates `0.0006557 s/block` saved: **0.1880%** of the valid Stretch 031 M5 median target-block wall (`0.3487060 s`). The arithmetic target-rate projection is `14.3577 tok/s` versus `14.3307 tok/s`; it is diagnostic only and far below the required plausible `>=5%` end-to-end upside.

## Decision

`STRETCH_033_COMPILED_MLP_FEASIBILITY_NO_GO`.

The output is exact and diagnostic memory is compatible, but the benefit is flat (<1%) for both one and three real MLPs, with a substantial first-invocation compilation cost. Do not create Stretch 033 scientific artifacts or ABBA. Keep the canonical M5 monolithic qmatmul path and select a new independently preregistered compute factor. Do not reinterpret this as a claim about newer MLX versions.

## Evidence

- Runner: `scripts/stretch_m5_compiled_mlp_033_feasibility.py`
- Parent summary: `results-local/stretch/m5-compiled-mlp-033-feasibility/20260820-190058/summary.json`
- Child evidence: `results-local/stretch/m5-compiled-mlp-033-feasibility/20260820-190058/child-summary.json`
