# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — CAPABILITY 001 baseline running next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000M_REAL_PI_REPRODUCIBLE_PASS`
Next: `CAPABILITY_001_BASELINE_RUN`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory, speed and capability.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- context 4096
- max assistant output 2048 for capability tasks
- `prefill_step_size=512`
- `enable_thinking=false`
- built-in M1 `qmv_fast`
- raw weights `3,583,928,320 B`

REALGEN 001: 13.184615357 tok/s real generation; 12.046861457 tok/s E2E.

## Bridge admission result

CAPABILITY 000H-000M isolated and fixed request-boundary memory pressure.

Promoted policy after every fully completed response:
1. ownership-check the finished `GenerationBatch.Response`;
2. detach only its stale `prompt_cache`;
3. call `mx.clear_cache()` exactly once.

CAPABILITY 000M real-Pi reproducibility:
- functional **3/3 = 100%**;
- strict **3/3 = 100%**;
- 6 model turns per attempt;
- no resource aborts;
- no telemetry errors;
- peak MLX 4116.06-4123.39 MiB;
- minimum free 9-11%;
- minimum post-clear free 16-19%;
- post-clear allocator cache 0.00 MiB;
- final `DONE` every attempt.

The stable bridge implementation is now published at:

`scripts/loom_pi_mlx_bridge.py`

commit:
`4d204471aedb9262ccaa3b86f29b0e344d0c2884`

The prior local line is preserved as backup branch `local/pre-sync-bridge-08412`; untracked experimental capability scripts remain untouched.

## CAPABILITY 001 — RUN READY

Frozen authority:
- `research/capability/capability-001-frozen-spec.md`
- `research/capability/capability-001-context-amendment.md`
- `research/capability/capability-001-runtime-admission.md`
- `research/capability/capability-001-run-manifest.md`

Suite: 12 practical agent tasks.
- C01-C06: existing Coding Benchmark 01 v1.0.1 T01-T06 unchanged
- G01: safe fast-forward synchronization
- G02: dirty-tree protection
- G03: divergence diagnosis
- E01: balanced-ratio causal interpretation
- E02: upper-bound/impossible-target reasoning

Primary result: passes / 12. Secondary: existing coding benchmark /100 plus critical failures, constraint violations, tool/protocol errors and resource diagnostics.

Every task uses a fresh Pi session and disposable workspace. Host admission before each task: free >=60% on two consecutive passive samples, swap <=5600 MB. No rescue/retry after scientific execution begins. Boundary reclamation remains frozen as part of the admitted runtime.

If canonical C01-C06 benchmark assets cannot be located exactly, stop as infrastructure incomplete rather than reconstructing them.

## Exact next step

Pi implements and executes the CAPABILITY 001 harness against the frozen 12-task suite and returns raw/scored evidence only. Pi does no Git/HANDOFF/ROADMAP work. ChatGPT reviews provenance and final scoring and synchronizes the result.

## Local-only warning

Most CAPABILITY 000A-000M experimental harness scripts and raw evidence remain local/untracked. Do not add or modify them during CAPABILITY 001 except for the new CAPABILITY 001 harness/evidence required by the benchmark.

## Later

1. CAPABILITY 001 frozen 12-task capability baseline
2. MEMORY-FRONTIER 001 real M1 RAM/tok/s partial-residency curve
3. async prefetch/buffering/direct range I/O
4. OUTCORE-BLOCK 001
5. scale toward 27B/32B
