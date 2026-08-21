# CAPABILITY 000H — Sequential accumulation limit

Date: 2026-08-21
Classification: `CAPABILITY_000H_SEQUENTIAL_ACCUMULATION_LIMIT`

## Question

Does the sustained Pi-loop resource failure come from intrinsically larger later requests or from memory retained between HTTP model requests?

## Exact captured trajectory

The CAPABILITY 000G workload contained six HTTP model POSTs; the earlier count of five referred to completed responses. Request 6 was the actual abort-boundary POST.

Input tokens:

- R1 1518
- R2 1573
- R3 1634
- R4 1682
- R5 1765
- R6 1820

All remain far below context 4096.

## Fresh-request envelope

Every request R1-R6 completed when executed as the first request of a fresh canonical model process with `prefill_step_size=512`.

Fresh peak MLX MB:

- R1 4069.62
- R2 4095.65
- R3 4095.65
- R4 4095.65
- R5 4095.65
- R6 4132.34

Fresh minimum free memory stayed between 7% and 10%. Therefore there is no intrinsic late-turn/request-size failure in the captured trajectory.

## Sequential result

R1 completed sequentially:

- peak MLX 4069.62 MB
- post active 3886.20 MB
- post cache 226.57 MB
- min free 7%

R2 then resource-aborted:

- observed peak MLX 4182.45 MB
- min free 4%
- hard gate triggered

Fresh R2 peak was 4095.65 MB, so sequential R2 carried +86.80 MB peak overhead.

More importantly, R2 began after R1 with MLX active at 3886.20 MB versus the fresh loaded-idle baseline of 3417.90 MB: **+468.30 MB retained active state at the request boundary**.

## Attribution

- Sequential retained MLX active/cache state: **PROVEN**.
- Intrinsic later request size/history as primary failure driver: **NOT SUPPORTED**; even R6 passes fresh.
- KV-capacity jumps as primary failure driver: **NOT SUPPORTED**.
- Host variability as primary driver: **NOT SUPPORTED**; admitted host states were comparable.

This does not by itself prove a memory leak. It proves request-boundary accumulation/live state sufficient to make R2 unsafe under the system-free gate.

## Decision

Do not reduce context, quantize KV, shrink tools/prompts, or switch to prefill step 256 yet.

The next experiment must identify the request-local object/tensor lifecycle responsible for the +468.30 MB active boundary state and test targeted release at response completion without global allocator cleanup.

Evidence:
`results-local/capability/capability-000h/20260821-164736/`
