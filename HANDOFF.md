# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — expert-major is accepted/canonical. Exact-Q4 speed frontier advanced to median `1.229233 tok/s`; remaining dominant bottleneck is expert file I/O. Persistent-FD delta is accepted locally and awaits review/commit before routing-sparsity work.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_POST_CANONICAL_SPEED_FRONTIER_001_SPEED_FRONTIER_ADVANCED_AWAITING_CODE_REVIEW`
Pi context: `/AGENTS.md` v3.39.

## Settled expert-major phase

Physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median first-touch PACKED/SOURCE ratio `0.595950` = `40.405%` lower expert-access wall.

Full-bank runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Accepted three-pair median ratio `0.794284` = `20.5716%` lower decode wall. Exactness/RSS/swap/fallback/cache PASS.

Canonicalization:
`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002 = EXPERT_MAJOR_CANONICALIZATION_GO` with `FORMULAIC_RESOLVER`.

Canonical code committed before speed frontier:
`scripts/loom_30b_moe_expert_major_backend_001.py`
Commit `36414d7`.

Do not reopen expert-major validation absent regression/new target.

## Post-Canonical Speed Frontier 001 — ADVANCED

Result:
`research/architecture/loom-30b-post-canonical-speed-frontier-001-result.md`
Evidence:
`results-local/research/30b-post-canonical-speed-frontier-001/20260827T131329Z/`

Stage-0 exact sustained baseline:
`1.063941 tok/s`.

Wall attribution:
1. expert file I/O `13.415820 s` / `44.61%`;
2. expert compute `7.971682 s` / `26.50%`;
3. non-expert/backbone `4.432324 s` / `14.74%`;
4. materialization/synchronization `3.462511 s` / `11.51%`;
5. routing `0.794527 s` / `2.64%`.

Stage decisions:
- persistent PACKED process-lifetime fd: exact/safe, `+8.65%`, RETAINED;
- sync collapse: `-30.38%`, reverted;
- bounded allocation/copy reduction: `+3.60%` but RSS +151,879,680 B > +32 MiB, reverted;
- bounded one-ahead overlap: `+8.45%` but RSS +162,676,736 B > +32 MiB, reverted.

Final exact 3×32-token sustained throughput:
- `1.115874`;
- `1.229233`;
- `1.254611 tok/s`;
median `1.229233 tok/s`.

p50 token wall `0.825660 s`; p95 `1.217692 s`.
Peak RSS `404,340,736 B`; swap delta `0`; safety PASS.
Final three-position exactness PASS.
Final local backend SHA-256 `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Interpretation: exact-Q4 speed is now I/O-limited. Each top-8 token reads `962,592,768 B` of routed expert payload; `5 tok/s` would imply roughly `4.81 GB/s` expert payload bandwidth before other work.

## Immediate action — persist accepted persistent-FD delta

The retained Stage-1 modification is currently local/uncommitted in:
`scripts/loom_30b_moe_expert_major_backend_001.py`.

Before next independent Pi run:
1. capture/review exact diff and file SHA;
2. verify only process-lifetime PACKED fd + deterministic close was retained;
3. reject hidden cache/fallback/fd leak or accidental extra Stage 2–4 code;
4. if review PASS, commit/push;
5. pull canonical docs afterward.

Do not execute Routing Sparsity Frontier 001 until this persistence step is complete.

## Next — Routing Sparsity Speed/Quality Frontier 001

Preregistration:
`research/architecture/loom-30b-routing-sparsity-speed-quality-frontier-001-preregistration.md`.

Goal: trade only a frozen bounded amount of model fidelity for speed by reducing the number of top-8 routed experts actually executed according to cumulative routing mass.

Frozen variants: `tau=0.95`, `0.90`, `0.80`, `0.70` only.

Fidelity set is frozen before variant results: 8 prompts ×16 teacher-forced positions = 128 positions using exact Q4 teacher logits.

USABLE gate:
- top1 agreement >=90%;
- reference top1 in candidate top3 >=97%;
- mean KL <=0.10 nats;
- no NaN/Inf.

STRICT gate:
- top1 >=95%;
- top3 inclusion >=99%;
- KL <=0.05.

Only quality-valid/safe variants >=10% faster than exact median `1.229233 tok/s` are eligible. Select fastest; tie within 2% favors fidelity/higher tau.

After selection, one raw-payload one-ahead overlap repair is allowed only if residual I/O >=20% and it stays within +32 MiB RSS.

If still materially below 5 tok/s afterward, next frontier is lower-bit expert payload quantization (Q3/Q2/mixed) with a separate quality gate.

After current 30B speed work is frozen: run Qwen3-30B-A3B vs Qwen3.8-27B vs Qwen3.8-Flash-Next bake-off on speed, memory, quality/intelligence and steerability/refusal behavior.
