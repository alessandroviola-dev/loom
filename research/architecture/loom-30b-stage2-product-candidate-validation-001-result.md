# LOOM 30B Stage2 Product-Candidate Validation 001 — Result

Date: 2026-08-30
Classification: **`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`**

## Summary

Stage2 validated Apple Metal MoE paging S24 as the better current `loom-deep` product candidate versus the historical custom-MLX 30B under the preregistered different-checkpoint product-utility contract.

The result does **not** establish same-checkpoint runtime-only superiority because the compared checkpoints differ. It does establish sufficient reproducibility, practical quality, speed, E2E latency and host safety to promote the Apple candidate as canonical DEEP.

## Evidence

Evidence root:
`results-local/research/30b-stage2-product-candidate-validation-001/20260830T094500Z/`

A no-inference output-extraction reconciliation was applied to retained Apple raw logs and recorded in `output-extraction-reconciliation.json`; no model rerun occurred.

## Block A — S24 reproducibility

Candidate N, three fresh S24 processes:

| Run | Generation tok/s | E2E | Peak swap |
|---|---:|---:|---:|
| 1 | 4.38 | 38.546 s | 1549.69 MiB |
| 2 | 4.39 | 37.834 s | 1533.69 MiB |
| 3 | 4.39 | 37.621 s | 1525.69 MiB |

Median generation throughput: **4.39 tok/s**.

Reproducibility gate: PASS.
- 3/3 clean coherent runs;
- median >=4.0 tok/s;
- no individual run <3.5 tok/s;
- no critical memory pressure/OOM/corruption/output-runaway;
- every run remained below 3.5 GiB peak swap.

## Block B — matched practical suite

| Task | Historical H | H tok/s | Apple N | N tok/s |
|---|---:|---:|---:|---:|
| T1 arithmetic exact JSON | FAIL | 1.42 | FAIL | 3.52 |
| T2 structured extraction | PASS | 1.46 | PASS | 3.39 |
| T3 ordered transformation | FAIL | 1.39 | PASS | 4.56 |
| T4 logical entailment | FAIL | 1.13 | PASS | 3.73 |
| T5 Python utility | PASS | 1.44 | PASS | 4.97 |
| T6 constrained summary | 3/3 | 1.44 | 3/3 | 3.71 |
| T7 concise explanation | 3/3 | 1.48 | 2/3 | 4.47 |

Aggregates:
- objective T1–T5: H **2/5**, N **4/5**;
- rubric T6–T7: H **6/6**, N **5/6**;
- median generation: H **1.437 tok/s**, N **3.730 tok/s**;
- pooled generation: H **1.444 tok/s**, N **4.059 tok/s**;
- pooled throughput ratio N/H: **2.81x**;
- median E2E: H **65.909 s**, N **26.380 s**;
- median E2E ratio N/H: **0.40x**;
- peak matched-suite swap: **1501.69 MiB** for both candidates;
- no critical pressure, OOM, corruption or output-runaway.

T1 failed for both candidates and therefore does not distinguish product quality. N materially outperformed H on T3 and T4 while matching T2 and T5. H retained a one-point advantage on the T6–T7 rubric total because N scored 2/3 on T7.

## Gate evaluation

1. exact provenance / no unauthorized mutation — PASS;
2. N Block A reproducibility — PASS;
3. 7/7 matched tasks valid for both candidates — PASS;
4. N objective >=4/5 and no more than one PASS below H — PASS (`4/5` vs `2/5`);
5. N rubric no more than one point below H — PASS (`5/6` vs `6/6`);
6. N matched generation throughput >=2.0x H — PASS (`2.81x` pooled);
7. N median E2E <=0.80x H — PASS (`0.40x`);
8. no critical memory/OOM/corruption/runaway — PASS;
9. N peak swap <=3.5 GiB — PASS;
10. complete durable evidence — PASS.

Final classification:
**`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`**.

## Product decision

Promote the Apple Metal MoE paging candidate to canonical `loom-deep` on product-utility grounds:

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Profile:
S24 (`--moe-n-slots 24`).

Runtime:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
with `llama-completion -no-cnv`.

Historical custom MLX remains retained as a historical comparison/fallback artifact but is no longer the preferred DEEP product candidate.

This promotion must not be described as same-checkpoint runtime-only superiority because Stage2 comparability established different checkpoints.

## Next step

Open the separate 30B acceleration funnel.

Primary architectural reference: mini-SGLang concepts independently adapted for Apple Silicon:
- persistent process / stable-prefix caching;
- KV/prompt reuse;
- chunked prefill;
- overlap scheduling;
- expert/I/O prefetch.

Start with a bounded persistent/cache feasibility audit before altering the now-promoted runtime. Then use measured attribution to choose the first direct decode-throughput intervention. Goal sequence: secure 5+ tok/s, then investigate 6–9 tok/s without unacceptable quality or memory cost.
