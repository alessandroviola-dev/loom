# CAPABILITY 000L — Full-sequence boundary reclamation result

Date: 2026-08-21
Branch: `research/stretch-015-divergence-attribution`
Classification: `CAPABILITY_000L_FULL_SEQUENCE_BOUNDARY_RECLAMATION_PASS`

## Question

Can the combined completed-request boundary policy — ownership-checked detach of the stale `GenerationBatch.Response.prompt_cache`, followed by exactly one `mx.clear_cache()` — keep the exact captured R1->R6 sequence safe without changing model, context, KV precision, tools, prompt, prefill step or semantics?

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- `prefill_step_size=512`
- same tokenizer/chat template/tool surface and localhost bridge semantics

Exact requests:
- R1 1518 tokens
- R2 1573
- R3 1634
- R4 1682
- R5 1765
- R6 1820

## Result

Both control and treatment completed R1-R6 in this run. The control therefore did not reproduce the earlier R2 abort, confirming that the <5% system-free gate has some host/run variability. The treatment nonetheless produced a consistent and material memory-headroom advantage across the full sequence.

Overall:
- CONTROL peak MLX: **4230.45 MiB**
- CONTROL minimum free: **5%**
- TREATMENT peak MLX: **4132.64 MiB**
- TREATMENT minimum free: **10%**
- peak reduction: **97.81 MiB**
- worst-case free-memory improvement: **+5 percentage points**
- first failure: NONE in either arm
- semantic/tool equivalence: PASS for R1-R6
- `gc.collect()`: not used

Per turn:

| Request | Control peak MiB | Treatment peak MiB | Control min free | Treatment min free |
|---|---:|---:|---:|---:|
| R1 | 4069.62 | 4069.62 | 10% | 14% |
| R2 | 4194.45 | 4095.95 | 5% | 12% |
| R3 | 4194.45 | 4095.95 | 6% | 12% |
| R4 | 4194.45 | 4095.95 | 7% | 13% |
| R5 | 4194.45 | 4095.95 | 7% | 12% |
| R6 | 4230.45 | 4132.64 | 5% | 10% |

## Boundary behavior under treatment

After each completed response, the stale request-local `prompt_cache` was detached with ownership verification, then `mx.clear_cache()` was called exactly once.

| R | Post-response active/cache MiB | Post-detach active/cache MiB | Post-clear active/cache MiB | Free after clear | Clear latency |
|---|---|---|---|---:|---:|
| R1 | 3886.20 / 234.23 | 3634.20 / 486.23 | 3634.20 / 0.00 | 22% | 4.237 ms |
| R2 | 3922.20 / 4.65 | 3670.20 / 256.65 | 3670.20 / 0.00 | 18% | 1.825 ms |
| R3 | 3922.20 / 4.49 | 3670.20 / 256.49 | 3670.20 / 0.00 | 19% | 2.637 ms |
| R4 | 3922.20 / 2.96 | 3670.20 / 254.96 | 3670.20 / 0.00 | 21% | 1.855 ms |
| R5 | 3958.20 / 271.74 | 3670.20 / 559.74 | 3670.20 / 0.00 | 19% | 3.404 ms |
| R6 | 3994.20 / 2.96 | 3706.20 / 290.96 | 3706.20 / 0.00 | 17% | 1.945 ms |

Allocator cache was **0.00 MiB before R2-R6 and after every treatment clear**. During requests it could grow to roughly 559-689 MiB, but the completed-request boundary policy returned it to zero each time.

Cache-clear latency:
- mean **2.651 ms**
- median **2.291 ms**
- max **4.237 ms**

## Residual active state

Loaded-idle active: **3417.90 MiB**.

Post-clear residual active over loaded-idle:
- R1 +216.30 MiB
- R2 +252.30 MiB
- R3 +252.30 MiB
- R4 +252.30 MiB
- R5 +252.30 MiB
- R6 +288.30 MiB

The residual is mostly stable R2-R5 and rises modestly at R6. It is not yet proven to be a long-horizon leak; the six-request sequence remains safe with 10% worst-case free memory.

## Semantic safety

Exact parsed response text, finish reason, tool name and tool arguments matched control for all R1-R6. No semantic discrepancy was observed.

## Interpretation

The combined boundary mechanism is now promoted from a two-turn candidate to a **full captured-sequence validated treatment**:

1. request-local stale KV ownership is explicitly detached;
2. resulting allocator cache is returned to the system with one `mx.clear_cache()`;
3. allocator cache remains bounded at zero between requests;
4. full R1-R6 completes;
5. worst-case system free improves from 5% to 10% in this run;
6. treatment overhead is only a few milliseconds per completed request;
7. semantics are unchanged.

The non-reproducing control failure means 000L alone is not a reliability study. The next step is real Pi end-to-end reproducibility using the exact combined boundary mechanism.

## Evidence

Local evidence:
`results-local/capability/capability-000l/20260821-194156/`

Local implementation:
`scripts/capability_000l_full_sequence_boundary_reclamation.py`

These local files are not assumed to be present on GitHub until explicitly synchronized.
