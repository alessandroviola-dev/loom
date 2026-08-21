# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability baseline / CAPABILITY 001 ready
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

## Canonical baseline

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

REALGEN 001: 13.184615357 tok/s real generation; 12.046861457 tok/s E2E. REALGEN 002 custom M1 qmv transfer exact but -9.178832%; closed.

## Capability bridge findings

### 000C — prefill frontier

Step 512 dominates canonical 2048 on the exact Pi prefill in both memory and speed while remaining bit-exact. Step 256 saves more peak memory but is slower and not bit-exact.

### 000D–000G — bridge and host lifecycle

A genuine Pi tool turn works. Later failures are not caused by intrinsic ~1500–1800-token request size. Scientific-process teardown is healthy and macOS naturally recovers >=60% free within ~3–5 s.

### 000H — sequential accumulation limit

All exact captured R1-R6 requests pass fresh. A critical sequential run showed R2 failure because R1 left +468.30 MiB MLX active request-boundary state. Later prompt size, KV-capacity jumps and host variability were not primary causes.

### 000I — targeted request-local reclamation PASS

`ResponseGenerator._generate` can retain a completed `GenerationBatch.Response`; its `prompt_cache` keeps finished-request KVCache objects alive after HTTP completion.

Ownership-checked detach of only the stale completed response's `prompt_cache`:
- recovers 252.00 MiB MLX active;
- lowers R2 peak by ~98.5 MiB;
- preserves response/tool behavior.

Released storage largely moves into MLX allocator cache.

### 000K — allocator-cache reclamation PASS

After the stale-response detach, one `mx.clear_cache()`:
- reclaims 486.23 MiB allocator cache;
- raises R2 minimum free from 5% to 11%;
- costs 3.900 ms in the measured boundary;
- preserves semantics.

Non-canonical ~0.01 s prefill timings from 000K are not accepted as performance evidence.

### 000L — full-sequence boundary reclamation PASS

Exact captured R1-R6 all complete with the combined boundary treatment.

Treatment vs control:
- peak MLX 4132.64 vs 4230.45 MiB;
- minimum free 10% vs 5%;
- semantic/tool equivalence PASS;
- boundary cache clears average 2.651 ms, max 4.237 ms;
- allocator cache returns to 0.00 MiB after each clear.

The control also passed in that particular run, so 000L validated mechanism/headroom rather than reliability.

### 000M — REAL PI REPRODUCIBLE PASS

Report: `research/capability/capability-000m-real-pi-reproducibility-result.md`.

The 000L boundary policy was promoted into the actual localhost Pi bridge:

1. after each fully completed model response, ownership-check the finished `GenerationBatch.Response`;
2. detach only its stale `prompt_cache`;
3. call `mx.clear_cache()` exactly once.

Three independently admitted fresh-process/fresh-Pi attempts of the frozen numbers task all passed:

- functional **3/3 = 100%**;
- strict final `DONE` **3/3 = 100%**;
- 6 model turns per attempt;
- tool sequence `read -> bash -> write -> bash -> bash`;
- largest input 1807–1813 tokens;
- max KV about 1806–1812 / 2048;
- peak MLX 4116.06–4123.39 MiB;
- minimum free 9–11%;
- resource aborts 0;
- telemetry errors 0;
- every `answer.txt` = `31`;
- every `numbers.txt` integrity check PASS;
- minimum post-clear free 16–19%;
- max post-clear allocator cache 0.00 MiB;
- mean clear latency 2.003–2.596 ms.

Classification: `CAPABILITY_000M_REAL_PI_REPRODUCIBLE_PASS`.

This satisfies the frozen promotion rule. The canonical bridge is admitted to CAPABILITY 001.

Raw local evidence:
`results-local/capability/capability-000m/20260821-195821/`

## CAPABILITY 001 — READY

Frozen documents:

- `research/capability/capability-001-agentic-baseline-plan.md`
- `research/capability/capability-001-frozen-spec.md`
- `research/capability/capability-001-context-amendment.md`
- `research/capability/capability-001-runtime-admission.md`

Frozen suite: 12 tasks.

- C01–C06: existing Coding Benchmark 01 v1.0.1 tasks unchanged
- G01: safe fast-forward synchronization
- G02: dirty-tree protection
- G03: divergence diagnosis
- E01: balanced-ratio causal interpretation
- E02: upper-bound/impossible-target reasoning

Primary score: passes / 12. There is no quality promotion threshold; completion produces `CAPABILITY_001_BASELINE_COMPLETE` if all tasks are scorable.

Each task must use a fresh isolated Pi session and disposable workspace. No human rescue/retry. Local provider only. Boundary reclamation remains frozen as part of the admitted runtime.

## Exact next step

Before running CAPABILITY 001, publish the now-promoted local bridge source mechanically because `scripts/loom_pi_mlx_bridge.py` was modified by Pi and ChatGPT cannot read uncommitted files on the user's Mac.

This is a code-only synchronization exception: no HANDOFF/ROADMAP/report work by Pi.

Then run CAPABILITY 001 exactly from the frozen specification. Pi implements/executes the harness and returns raw results only; ChatGPT reviews/scorers/provenance and synchronizes project documentation.

## Local-only implementation warning

Most CAPABILITY 000A–000M harness scripts and raw evidence remain local unless explicitly synchronized. The stable bridge source must now be published before the capability baseline so the admitted runtime is reproducible from Git.

## Later

1. mechanically publish promoted `scripts/loom_pi_mlx_bridge.py`
2. CAPABILITY 001 frozen 12-task capability baseline
3. MEMORY-FRONTIER 001 real M1 RAM/tok/s partial-residency curve
4. async prefetch/buffering/direct range I/O
5. OUTCORE-BLOCK 001
6. scale toward 27B/32B
