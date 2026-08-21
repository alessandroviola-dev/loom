# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_001_FROZEN_SUITE_CORRECTED_TO_11`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2. REALGEN 001 = 13.184615357 tok/s real generation and 12.046861457 tok/s E2E.

The admitted bridge uses `prefill_step_size=512` and, after every fully completed model response, ownership-checks the finished response, detaches only its stale `prompt_cache`, then calls `mx.clear_cache()` exactly once.

Stable bridge source is published at code-sync commit `4d204471aedb9262ccaa3b86f29b0e344d0c2884`.

## A — Capability baseline — ACTIVE

### CAPABILITY 000M — REAL PI REPRODUCIBLE PASS

Three independent real-Pi attempts passed functionally and strictly 3/3 with no resource aborts or telemetry errors. Minimum system free was 9–11%, minimum post-clear free 16–19%, and post-clear allocator cache remained 0.00 MiB.

The bridge is admitted for the capability baseline.

### CAPABILITY 001 — PRE-RUN AUDIT CORRECTION

The first CAPABILITY 001 invocation ran no model tasks. Its mandatory frozen-suite audit found a clerical inconsistency:

- frozen spec declared 12 tasks;
- actually defined identities are C01–C06, G01–G03, E01–E02;
- total = **11 tasks**.

No twelfth task exists in the inspected canonical benchmark assets.

Audit classification: `CAPABILITY_001_INFRASTRUCTURE_INCOMPLETE`
Issue: `FROZEN_TASK_COUNT_MISMATCH`

This is protocol/infrastructure evidence only; it contains no model-quality result.

Report:
`research/capability/capability-001-pre-run-suite-audit-result.md`

### CAPABILITY 001 — CORRECTED FROZEN BASELINE READY

Task-count amendment:
`research/capability/capability-001-task-count-amendment.md`

The amendment changes only the clerical count/denominator:

- canonical suite = **11 tasks**;
- C01–C06 = 6 coding;
- G01–G03 = 3 Git safety;
- E01–E02 = 2 experimental reasoning;
- primary metric = passes / 11.

No task prompt, fixture, expected result, scorer, runtime condition, tool surface or resource rule changes. Do not invent a twelfth task.

Run conditions remain:

- Qwen3-8B full parameter count, 3-bit/group64;
- BF16 KV;
- context 4096;
- max output 2048;
- step 512;
- localhost-only provider;
- tools read/write/edit/bash;
- request-boundary detach + one `mx.clear_cache()`;
- fresh isolated process/session/workspace per task;
- host free >=60% on two passive samples and swap <=5600 MB before task load;
- no retry/rescue.

Classification after all 11 tasks execute/scorable: `CAPABILITY_001_BASELINE_COMPLETE`. There is no quality promotion threshold; the measured score is the baseline.

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

1. CAPABILITY 001 — corrected 11-task baseline
2. MEMORY-FRONTIER 001
3. prefetch/buffering/range-I/O
4. OUTCORE-BLOCK 001
5. scale toward 27B/32B

## Local-only implementation warning

Recent experiment harness scripts/evidence remain local unless explicitly synchronized. The stable bridge source is already published.
