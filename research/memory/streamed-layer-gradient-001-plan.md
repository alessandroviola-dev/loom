# STREAMED-LAYER-GRADIENT 001 — frozen plan

Date: 2026-08-22
Status: FROZEN / RUN PENDING

## Goal

Measure the low-overhead real-M1 marginal cost of streaming 1, 2 or 4 transformer layers when all shared stages are already persistent.

The question is whether the residual slowdown after SHARED-STAGE-RESIDENCY 001 is approximately additive per streamed transformer layer or dominated by a fixed/nonlinear orchestration effect.

This is a characterization experiment, not an optimization treatment.

## Why now

SHARED-STAGE-RESIDENCY 001 proved that making embedding/final norm/LM head persistent improves F1 generation by 36.66%, from 2.532 to 3.459 tok/s, while preserving exact token parity.

The treatment still reaches only 25.75% of F0 throughput. Its only intentional model-residency difference versus F0 is that layers 32..35 remain streamed each token.

Earlier invasive tracing suggested approximately 50–58 ms/token around each streamed layer, but tracing materially perturbed throughput. A low-overhead causal gradient is therefore required before choosing the first transformer-stream optimization.

## Frozen model/runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1 where inherited
- thinking disabled
- greedy real M1 unknown-token generation
- no drafter/speculation/oracle/cloud/Ollama

Canonical raw weight anatomy:
- total: 3,583,928,320 B
- each transformer layer: 84,427,264 B
- shared embedding + final norm + LM head: 544,546,816 B

## Shared-stage rule

For every arm:
- embedding persistent
- final norm persistent
- LM head persistent
- materialized once before prompt execution

No arm may stream a shared stage.

## Gradient arms

### S0 — zero streamed transformer layers

All transformer layers 0..35 persistent.
All shared stages persistent.
Equivalent model residency to F0 FULL.

Expected persistent raw bytes: 3,583,928,320 B.
Expected streamed transformer bytes/token: 0.

### S1 — one streamed transformer layer

Layers 0..34 persistent.
Layer 35 streamed through the proven current transformer streaming path.
Shared stages persistent.

Expected persistent raw bytes: 3,499,501,056 B.
Expected streamed bytes/token: 84,427,264 B.

### S2 — two streamed transformer layers

Layers 0..33 persistent.
Layers 34..35 streamed identically.
Shared stages persistent.

Expected persistent raw bytes: 3,415,073,792 B.
Expected streamed bytes/token: 168,854,528 B.

### S4 — four streamed transformer layers

Layers 0..31 persistent.
Layers 32..35 streamed identically.
Shared stages persistent.

Expected persistent raw bytes: 3,246,219,264 B.
Expected streamed bytes/token: 337,709,056 B.

S4 is the SHARED-STAGE-RESIDENCY 001 treatment configuration.

## One-factor discipline

Across S0/S1/S2/S4, change only the number of transformer layers using the exact proven streaming lifecycle.

Do not change:
- shared-stage residency
- model math
- quantization
- KV format
- tokenizer/chat template
- decoding
- streaming source/format
- per-layer loader
- cleanup policy
- prefetch/threading/buffering
- chunking/range I/O/mmap/pread
- page-cache policy
- M>1 execution

## Implementation audit

Before science verify actual persistent/streamed tensors for every arm and exact logical byte accounting.

The streamed layers in S1/S2/S4 must use the same code path and lifecycle. No streamed transformer layer may remain accidentally cached across generated tokens.

Store `implementation-audit.json`.

## Exact parity preflight

Separate non-scientific processes using the first canonical REALGEN 001 prompt.

Generate at least 16 greedy unknown tokens or EOS and require exact token IDs versus S0 for S1, S2 and S4.

A genuine divergence invalidates that point.

## Scientific workload

Use exactly the first three canonical REALGEN 001 prompts, unchanged, normal chat template, thinking false, greedy generation, max 64 generated tokens or EOS.

## Balanced run order

Two fresh constituent runs per arm in symmetric order:

`S0 -> S4 -> S2 -> S1 -> S1 -> S2 -> S4 -> S0`

Each process must independently satisfy host admission.

## Host admission

Before each process:
- system free >=60% on two consecutive passive samples
- swap <=5600 MB

Wait naturally. No purge, unrelated process kills, swap manipulation, artificial allocation/free or deliberate page-cache flush.

## Resource abort

After inference starts, abort if free <5% or swap >5600 MB. No rescue/retry.

## Low-overhead measurements

Do not reuse invasive STREAMING-ATTRIBUTION tracing.

Use identical low-overhead hooks for all arms to record:
- generated tokens
- generation wall
- real generation tok/s
- E2E tok/s
- TTFT
- exact token IDs/EOS
- MLX active after load
- peak MLX active and active+cache where available
- minimum system free
- peak swap
- process RSS diagnostic
- logical streamed bytes/token
- process-read bytes/token diagnostic

Do not add extra `mx.eval()` or `mx.synchronize()` solely for timing.

## Primary analysis

For each arm pool its two valid constituents.

Report wall time per generated token and throughput.

Fit/descriptively examine relation between:
- number of streamed transformer layers: 0,1,2,4
- logical streamed bytes/token
- incremental wall/token relative to S0

Calculate marginal penalty:
- S1 vs S0
- S2 vs S1
- S4 vs S2

Express both:
- additional ms/token per additional streamed layer
- additional ms/token per 84,427,264 B streamed layer equivalent

Do not claim strict linearity from four points unless residuals are small and monotonic behavior supports it.

## Interpretation classes

Choose one:

`STREAM_LAYER_COST_APPROX_ADDITIVE`
if incremental wall cost per streamed layer is reasonably stable and monotonic.

`STREAM_LAYER_COST_FIXED_OR_NONLINEAR`
if the first streamed layer carries a large fixed cost or marginal penalties materially differ/non-monotonic.

`STREAM_LAYER_COST_UNRESOLVED`
if host variability or measurement quality prevents interpretation.

This classification describes system-level cost only; it does not identify SSD/materialization/kernel internals.

## Why this matters

If cost is approximately additive per streamed layer, future optimization must reduce or amortize the per-layer lifecycle itself; simple residency reshuffling cannot scale to 27B/32B.

If a large fixed/nonlinear cost dominates, batching/chunking/scheduling may offer a different route.

## Classification

`STREAMED_LAYER_GRADIENT_001_COMPLETE` if all four arms have two valid runs and exact correctness status.

`STREAMED_LAYER_GRADIENT_001_PARTIAL` if S0 plus at least two streamed arms are valid.

`STREAMED_LAYER_GRADIENT_001_INFRASTRUCTURE_INCOMPLETE` only for harness/implementation failure.

## Evidence

Store under:
`results-local/memory/streamed-layer-gradient-001/<run-id>/`

At minimum:
- summary.json
- implementation-audit.json
- parity.json
- host-admission.jsonl
- gradient.json
- runs/

## Pi role

Pi implements/adapts the local runner and executes measurements only. No Git/HANDOFF/ROADMAP and no next experiment.
