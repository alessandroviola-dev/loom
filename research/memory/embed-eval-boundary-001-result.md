# EMBED-EVAL-BOUNDARY 001 — Result

Date: 2026-08-22
Classification: `EMBED_EVAL_BOUNDARY_001_COMPLETE`
Interpretation: `EMBED_EVAL_NO_GO`

## Frozen comparison

Both arms used the cleanup-consolidated S1 baseline:
- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- transformer layers 0..34 persistent
- layer 35 streamed
- embedding/final norm/LM head persistent
- persistent raw weights: 3,499,501,056 B
- logical streamed traffic: 84,427,264 B/token

CONTROL retained the explicit post-embedding `mx.eval(h)`.

TREATMENT removed/deferred only that explicit post-embedding eval. First-block eval, norm eval, head eval, cleanup topology, residency, streamed-layer lifecycle and I/O were otherwise unchanged.

## Correctness

- CONTROL parity: PASS
- TREATMENT parity: PASS
- all four scientific constituents matched canonical S0 token IDs exactly
- no resource aborts

## Pooled result

| Arm | Gen tok/s | Wall/token | E2E tok/s | Median TTFT | Peak MLX | Min free | Peak swap |
|---|---:|---:|---:|---:|---:|---:|---:|
| CONTROL | 7.069 | 141.462 ms | 6.198 | 1.230 s | 3,537,250,032 B | 20% | 2269.44 MB |
| TREATMENT | 6.833 | 146.359 ms | 6.001 | 1.297 s | 3,537,250,032 B | 13% | 2283.94 MB |

Treatment vs control:
- generation ratio: 0.966543
- generation change: **-3.346%**
- E2E change: **-3.178%**
- wall/token delta: **+4.897 ms**
- TTFT change: **+5.475%**
- peak MLX delta: 0 B
- minimum-free delta: -7 pp
- peak swap delta: +14.50 MB
- process-read diagnostic delta: +320,704 B/token

## Decision

Removing/defering the explicit post-embedding `mx.eval(h)` is a NO-GO on the current S1 path. It preserved exact model output but regressed contemporaneous throughput and TTFT.

Therefore the post-embedding eval remains frozen in the current experimental runtime. No mechanism-level claim is made about why removal regressed performance.

Context only: this treatment removed none of the previously modeled residual fixed activation term; measured wall/token instead increased by 4.897 ms.

Physical SSD traffic remains unproven.

Raw local evidence:
`results-local/memory/embed-eval-boundary-001/20260822-173925/`
