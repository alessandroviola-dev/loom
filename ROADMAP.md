# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000L_FULL_SEQUENCE_BOUNDARY_RECLAMATION_PASS`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2. REALGEN 001 = 13.184615357 tok/s real generation and 12.046861457 tok/s E2E.

## A — Capability baseline — ACTIVE

### 000C — prefill frontier

`prefill_step_size=512` dominates canonical 2048 on the exact Pi prefill and remains the active integrated-agent candidate.

### 000H — sequential accumulation

All captured R1-R6 requests pass fresh. A critical sequential run showed R2 failure because R1 left +468.30 MiB active request-boundary MLX state.

### 000I — targeted request-local reclamation PASS

The stale completed `GenerationBatch.Response.prompt_cache` retains finished-request KV. Ownership-checked detach recovers 252.00 MiB active MLX and preserves model/tool behavior.

### 000K — allocator-cache reclamation PASS

After the stale-response detach, one `mx.clear_cache()` reclaims 486.23 MiB allocator cache, raises R2 minimum free from 5% to 11%, costs 3.900 ms at the measured boundary and preserves semantics. Non-canonical ~0.01 s prefill measurements from 000K are not promoted.

### 000L — FULL-SEQUENCE BOUNDARY RECLAMATION PASS

Report: `research/capability/capability-000l-full-sequence-boundary-reclamation-result.md`.

Exact R1-R6 all complete with the combined treatment:
- after every completed response, detach only that stale completed-response `prompt_cache`;
- call `mx.clear_cache()` exactly once.

Treatment vs control in the same full sequence:
- peak MLX: **4132.64 vs 4230.45 MiB**;
- minimum free: **10% vs 5%**;
- peak reduction: **97.81 MiB**;
- worst-case free-memory gain: **+5 pp**;
- semantic/tool equivalence: PASS for R1-R6;
- no `gc.collect()`.

Allocator cache returns to **0.00 MiB** after every treatment boundary and before R2-R6. Cache-clear latency: mean **2.651 ms**, median **2.291 ms**, max **4.237 ms**.

The control also completed R1-R6 in this particular run, confirming resource-gate variability. Therefore 000L validates the treatment mechanism and headroom benefit, but does not itself establish real-agent reliability.

### 000M — NEXT

Frozen plan: `research/capability/capability-000m-real-pi-boundary-reclamation-reproducibility-plan.md`.

Integrate the exact 000L boundary treatment into the real Pi-localhost bridge for the experiment only, then run the frozen numbers.txt task in **three independent fresh attempts**.

Frozen:
- Qwen3-8B 3-bit full parameter count;
- BF16 KV;
- context 4096;
- step 512;
- full Pi tools;
- no model/prompt/tool/KV/context changes.

Each attempt:
- fresh server/model process;
- fresh Pi session/workspace;
- host admission free >=60% on two consecutive passive samples, swap <=5600 MB;
- no inference preflight in the scientific process;
- no retry/rescue;
- boundary detach + one `mx.clear_cache()` after every completed response.

Promotion rule: **3/3 functional PASS** is required before CAPABILITY 001. Strict final text `DONE` is secondary.

### CAPABILITY 001 — BLOCKED pending 000M

Frozen 12-task coding + Git safety + experimental-reasoning baseline. Run only after 000M demonstrates 3/3 real-Pi functional reliability.

## B — RAM/speed frontier

After CAPABILITY 001, run MEMORY-FRONTIER 001 with controlled partial residency and measure resident bytes, MLX peak, system free/swap, SSD bytes/token, real tok/s, TTFT and correctness.

## C — Hide SSD cost

Then isolate async prefetch, double/triple buffering, transfer chunk sizing, direct safetensors range I/O, macOS page-cache behavior and resident-hotset selection.

## D — Amortize I/O across tokens

OUTCORE-BLOCK 001 revisits M>1 for out-of-core execution where one weight load can serve multiple positions.

## E — Representation without shrinking parameter count

Later candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core storage formats. Judge each by memory + speed + capability.

## F — Scale beyond 8B

1. solve architecture on well-characterized 8B;
2. transfer to models exceeding comfortable physical RAM;
3. reach 27B/32B-class full-parameter generation on M1 8 GB without OOM;
4. optimize toward interactive speed.

## Immediate order

1. CAPABILITY 000M — real Pi boundary-reclamation reproducibility
2. CAPABILITY 001 if and only if 000M = 3/3 functional PASS
3. MEMORY-FRONTIER 001
4. prefetch/buffering/range-I/O
5. OUTCORE-BLOCK 001
6. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/` unless explicitly synchronized.
