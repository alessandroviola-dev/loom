# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / real Pi boundary-reclamation reproducibility
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000L_FULL_SEQUENCE_BOUNDARY_RECLAMATION_PASS`
Next: `CAPABILITY_000M_REAL_PI_BOUNDARY_RECLAMATION_REPRODUCIBILITY`

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
- `prefill_step_size=512`
- built-in M1 `qmv_fast`
- raw weights `3,583,928,320 B`

REALGEN 001: 13.184615357 tok/s real generation; 12.046861457 tok/s E2E. REALGEN 002 custom M1 qmv transfer exact but -9.178832%; closed.

## Capability findings

### 000C — prefill frontier

Step 512 dominates canonical 2048 on the exact Pi prefill in both memory and speed while remaining bit-exact. Step 256 saves more peak memory but is slower and not bit-exact.

### 000D–000G — bridge and host lifecycle

A genuine Pi tool turn works. Later failures are not caused by intrinsic ~1500–1800-token request size. Scientific-process teardown is healthy and macOS naturally recovers >=60% free within ~3–5 s.

### 000H — sequential accumulation limit

All exact captured R1-R6 requests pass fresh. Sequential R2 fails in the critical run because R1 leaves +468.30 MiB MLX active request-boundary state. Later prompt size, KV-capacity jumps and host variability are not primary causes.

### 000I — targeted request-local reclamation PASS

`ResponseGenerator._generate` retains a completed `GenerationBatch.Response`; its `prompt_cache` keeps finished-request KVCache objects alive after HTTP completion.

Ownership-checked detach of only the stale completed response's `prompt_cache`:
- recovers 252.00 MiB MLX active;
- lowers R2 peak by ~98.5 MiB;
- preserves response/tool behavior.

Released storage largely moves into MLX allocator cache.

### 000J — detach-only insufficient

Full-sequence detach-only validation did not extend the safe sequence in that run because allocator cache remained charged against system memory. After R1 detach, active fell 3886.20 -> 3634.20 MiB while allocator cache rose ~231 -> 483 MiB and later ~713 MiB during R2.

### 000K — allocator-cache reclamation PASS

Report: `research/capability/capability-000k-allocator-cache-reclamation-result.md`.

After the proven stale-response detach, one `mx.clear_cache()`:
- reclaims 486.23 MiB allocator cache;
- raises R2 minimum free from 5% to 11% (+6 pp);
- costs 3.900 ms in the measured boundary;
- preserves R1/R2 semantics and tool calls;
- leaves intrinsic R2 MLX peak essentially unchanged.

The reported ~0.01 s prefill timings in 000K are non-canonical and are not promoted as performance evidence.

### 000L — FULL-SEQUENCE BOUNDARY RECLAMATION PASS

Report: `research/capability/capability-000l-full-sequence-boundary-reclamation-result.md`.

Exact R1-R6: 1518, 1573, 1634, 1682, 1765, 1820 tokens.

Both control and treatment happened to complete R1-R6 in this run, so 000L is not itself a reliability study. The treatment nonetheless shows a clear full-sequence memory advantage.

Overall:
- CONTROL peak MLX **4230.45 MiB**, minimum free **5%**;
- TREATMENT peak MLX **4132.64 MiB**, minimum free **10%**;
- peak reduction **97.81 MiB**;
- worst-case free-memory gain **+5 pp**;
- semantic/tool equivalence PASS on R1-R6;
- no `gc.collect()`.

Treatment after every completed response:
1. verify ownership of the finished `GenerationBatch.Response`;
2. detach only its stale `prompt_cache`;
3. call `mx.clear_cache()` exactly once.

Boundary allocator cache is 0.00 MiB before R2-R6 and after every clear. Clear latency over R1-R6: mean **2.651 ms**, median **2.291 ms**, max **4.237 ms**.

Post-clear active residual over 3417.90 MiB loaded-idle:
- R1 +216.30 MiB
- R2-R5 +252.30 MiB
- R6 +288.30 MiB

Residual is mostly bounded over the six-request sequence, with a modest increase at R6. No long-horizon leak claim is justified yet.

## Exact next step

Run **CAPABILITY 000M — real Pi boundary-reclamation reproducibility** from:
`research/capability/capability-000m-real-pi-boundary-reclamation-reproducibility-plan.md`.

Promote the combined boundary mechanism into the actual Pi-integrated localhost bridge for the test only:
- after every fully completed model response, ownership-check and detach only that completed response's stale `prompt_cache`;
- call `mx.clear_cache()` exactly once;
- no other runtime/model/context/KV/prompt/tool/prefill changes.

Run exactly three independently admitted fresh-process/fresh-Pi attempts of the frozen numbers.txt task. Host gate before each attempt: free >=60% for two consecutive passive samples, swap <=5600 MB. Wait passively for natural recovery between attempts; no purge or host manipulation.

Only **3/3 functional PASS** admits the boundary-reclamation bridge into CAPABILITY 001. Strict final text `DONE` is tracked separately.

Do not automatically run CAPABILITY 001 after 000M; ChatGPT reviews first.

## Local-only implementation warning

Recent CAPABILITY scripts/evidence remain local unless explicitly synchronized, including CAPABILITY 000A–000L scripts and raw `results-local/capability/...` evidence. Do not assume those local files exist on GitHub until explicitly published.

## Later

1. CAPABILITY 000M real Pi reproducibility with boundary reclamation
2. CAPABILITY 001 frozen 12-task capability baseline if 000M is 3/3 functional PASS
3. MEMORY-FRONTIER 001 real M1 RAM/tok/s partial-residency curve
4. async prefetch/buffering/direct range I/O
5. OUTCORE-BLOCK 001
6. scale toward 27B/32B
