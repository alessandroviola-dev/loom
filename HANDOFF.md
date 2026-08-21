# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — CAPABILITY 001 corrected frozen baseline ready
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_001_FROZEN_SUITE_CORRECTED_TO_11`
Next: `CAPABILITY_001_BASELINE_RUN`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory, speed and capability.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical admitted runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- context 4096
- max assistant output 2048 for capability tasks
- `prefill_step_size=512`
- `enable_thinking=false`
- built-in M1 `qmv_fast`
- localhost-only `loom-mlx-local`
- Pi tools `read`, `write`, `edit`, `bash`

REALGEN 001 practical reference: 13.184615357 tok/s real generation; 12.046861457 tok/s E2E.

The stable promoted bridge source is published on this branch; its code-only sync commit is `4d204471aedb9262ccaa3b86f29b0e344d0c2884`.

## Capability bridge result

### CAPABILITY 000M — REAL PI REPRODUCIBLE PASS

Report: `research/capability/capability-000m-real-pi-reproducibility-result.md`.

The admitted boundary policy after each fully completed model response is:

1. ownership-check the finished `GenerationBatch.Response`;
2. detach only its stale completed-response `prompt_cache`;
3. call `mx.clear_cache()` exactly once.

Three independent fresh-process/fresh-Pi attempts of the frozen numbers task all passed:

- functional 3/3 = 100%;
- strict final `DONE` 3/3 = 100%;
- 6 model turns each;
- no resource aborts;
- no telemetry errors;
- peak MLX about 4116–4123 MiB;
- minimum free 9–11%;
- minimum post-clear free 16–19%;
- post-clear allocator cache 0.00 MiB;
- correct `answer.txt=31` and preserved `numbers.txt` in every attempt.

The bridge admission gate is closed successfully.

## CAPABILITY 001 — corrected frozen suite READY

Authoritative documents:

- `research/capability/capability-001-agentic-baseline-plan.md`
- `research/capability/capability-001-frozen-spec.md`
- `research/capability/capability-001-context-amendment.md`
- `research/capability/capability-001-runtime-admission.md`
- `research/capability/capability-001-task-count-amendment.md`

### Pre-run audit

The first CAPABILITY 001 invocation performed only the mandatory frozen-suite audit and stopped before any model task.

Classification: `CAPABILITY_001_INFRASTRUCTURE_INCOMPLETE`
Issue: `FROZEN_TASK_COUNT_MISMATCH`

The frozen spec declared 12 tasks, but the authoritative identities actually defined are:

- C01–C06 = 6 coding tasks;
- G01–G03 = 3 Git-safety tasks;
- E01–E02 = 2 experimental-reasoning tasks.

Total = **11**, not 12.

Sources inspected included the frozen CAPABILITY documents and Coding Benchmark 01 v1 manifest/README/validation assets. No twelfth task exists. No model task ran and no scientific task attempt was consumed.

Audit report:
`research/capability/capability-001-pre-run-suite-audit-result.md`

Raw local audit evidence:
`results-local/capability/capability-001/capability-001-audit-20260821-205727/`

### Frozen correction

`research/capability/capability-001-task-count-amendment.md` overrides only the clerical count/denominator:

- canonical frozen task count = **11**;
- identities = C01–C06, G01–G03, E01–E02;
- primary metric = passes / 11.

No task prompt, fixture, expected output, scorer, model/runtime setting, tool surface, resource gate or isolation rule changes.

Do not invent a twelfth task.

### Benchmark execution

Each task uses:

- fresh model/server process;
- fresh bridge and Pi session;
- disposable workspace;
- empty conversation history;
- host admission free >=60% on two consecutive passive samples and swap <=5600 MB;
- no inference preflight in the scientific process;
- no retry/rescue;
- resource abort only at free <5% or swap >5600 MB;
- admitted request-boundary reclamation unchanged.

Primary score: passes / 11. There is no quality threshold; if all 11 tasks execute/scorable, classification is `CAPABILITY_001_BASELINE_COMPLETE` regardless of score.

## Exact next step

Run CAPABILITY 001 on the corrected 11-task frozen suite. Pi implements/executes the harness and returns raw results only. ChatGPT reviews scoring/provenance and synchronizes the repository.

Do not alter the frozen task set or runtime during the run.

## Local-only implementation warning

Most CAPABILITY 000A–000M experiment harness scripts and raw evidence remain local unless explicitly synchronized. The promoted stable bridge itself is published.

## Later

1. CAPABILITY 001 corrected 11-task baseline
2. MEMORY-FRONTIER 001 real M1 RAM/tok/s partial-residency curve
3. async prefetch/buffering/direct range I/O
4. OUTCORE-BLOCK 001
5. scale toward 27B/32B
