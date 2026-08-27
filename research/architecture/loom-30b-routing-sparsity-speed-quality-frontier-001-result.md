# LOOM 30B Routing Sparsity Speed/Quality Frontier 001 — Result

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Checkpoint: `LOOM_30B_ROUTING_SPARSITY_SPEED_QUALITY_FRONTIER_001`
Final classification: `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`

## Result

Dynamic routing-mass truncation did not produce an acceptable speed/quality operating point on the canonical Qwen3-30B-A3B Q4 runtime.

Frozen teacher/reference baseline:
- canonical exact-Q4 commit `96958de`;
- sustained median `1.229233 tok/s`;
- top-8 routing semantics unchanged;
- fidelity oracle: 8 fixed prompts × 16 teacher-forced positions = 128 positions.

Evidence:
`results-local/research/30b-routing-sparsity-speed-quality-frontier-001/20260827T135848Z/`

## Frozen fidelity oracle

Saved under the evidence directory before any candidate result was observed:
- exact tokenized contexts;
- reference float32 logits;
- reference top-10 ranks;
- 128 total teacher-forced positions.

USABLE thresholds were frozen at:
- top-1 agreement >=90%;
- reference top-1 in candidate top-3 >=97%;
- mean KL(reference || candidate) <=0.10 nats;
- no NaN/Inf.

STRICT thresholds:
- top-1 >=95%;
- top-3 inclusion >=99%;
- mean KL <=0.05 nats.

## Candidate results

### tau = 0.95

- top-1 agreement: `100%`;
- top-3 inclusion: `100%`;
- mean KL: `0.004170`;
- tier: `STRICT`;
- retained experts/layer mean/min/max: `7.8757 / 6 / 8`;
- expert payload bytes/token: `947,630,592 B`;
- sustained throughput: `1.216703 tok/s`;
- gain vs exact baseline: `-1.02%`;
- peak RSS: `121,487,360 B`;
- swap: `0 MiB`;
- safety: PASS;
- eligible: NO — missed frozen >=10% speed-gain gate.

### tau = 0.90

- top-1 agreement: `96.875%`;
- top-3 inclusion: `100%`;
- mean KL: `0.048113`;
- tier: `STRICT`;
- retained experts/layer mean/min/max: `6.9440 / 5 / 8`;
- expert payload bytes/token: `835,531,776 B`;
- sustained throughput: `1.223280 tok/s`;
- gain vs exact baseline: `-0.48%`;
- peak RSS: `118,374,400 B`;
- swap: `0 MiB`;
- safety: PASS;
- eligible: NO — missed frozen >=10% speed-gain gate.

Residual expert file I/O at this quality-valid point remained `38.23%` of decode wall.

### tau = 0.80

- top-1 agreement: `92.188%`;
- top-3 inclusion: `100%`;
- mean KL: `0.113882`;
- fidelity: FAIL — KL exceeded USABLE gate;
- retained experts/layer mean/min/max: `5.7337 / 1 / 7`;
- sustained performance was not run after fidelity failure.

### tau = 0.70

- top-1 agreement: `87.5%`;
- top-3 inclusion: `98.438%`;
- mean KL: `0.331111`;
- fidelity: FAIL;
- retained experts/layer mean/min/max: `4.7430 / 1 / 6`;
- sustained performance was not run after fidelity failure.

## Decision

No tau was selected.

The two quality-valid variants (`0.95`, `0.90`) reduced too little expert work to improve throughput and both were slightly slower than the exact baseline. The more aggressive variants began violating the frozen fidelity gate before they could become eligible speed points.

Stage-6 one-ahead overlap was therefore skipped because there was no eligible Stage-5 sparsity selection. Stage 7 was not run for the same reason.

No tracked canonical backend/runtime file changed. The only new runner/evidence remained under `results-local/`.

## Interpretation

Qwen3-30B-A3B routing mass is sufficiently distributed across the original top-8 that dynamic cumulative-mass truncation cannot remove enough experts while preserving the frozen quality target.

Routing sparsity is therefore CLOSED as a speed direction for the current Q4 target under these fidelity gates. Do not retry adjacent tau values or fixed-top-k variants without a materially different hypothesis and new preregistration.

The dominant remaining speed lever is to reduce bytes per executed expert while preserving full top-8 routing. The next frontier is lower-bit expert payload quantization (Q3/Q2 where locally supported) with the same frozen Q4 teacher oracle and explicit speed/quality gates.
