# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability baseline complete / memory frontier next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_001_BASELINE_COMPLETE`
Next: `MEMORY_FRONTIER_001`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory, speed and capability.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical current system

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- real capability context 4096
- max assistant output 2048
- `prefill_step_size=512`
- `enable_thinking=false`
- built-in M1 `qmv_fast`
- localhost-only `loom-mlx-local`
- Pi tools `read`, `write`, `edit`, `bash`
- stable bridge code published at `4d204471aedb9262ccaa3b86f29b0e344d0c2884`

REALGEN 001 reference:
- real M1 generation: 13.184615357 tok/s
- E2E output: 12.046861457 tok/s

## Request-boundary memory policy

CAPABILITY 000I–000M established and promoted:

1. ownership-check finished `GenerationBatch.Response` after a fully completed response;
2. detach only its stale `prompt_cache`;
3. call `mx.clear_cache()` exactly once.

CAPABILITY 000M real-Pi reproducibility:
- functional 3/3
- strict 3/3
- zero resource aborts
- zero telemetry errors
- minimum free 9–11%
- minimum post-clear free 16–19%
- post-clear allocator cache 0 MiB.

The bridge admission problem is closed for the current baseline.

## CAPABILITY 001 — BASELINE COMPLETE

Report:
`research/capability/capability-001-baseline-result.md`

Corrected frozen suite:
- C01–C06 = six Coding Benchmark 01 v1.0.1 tasks
- G01–G03 = Git safety/reasoning
- E01–E02 = experimental reasoning
- total = 11

Classification:
`CAPABILITY_001_BASELINE_COMPLETE`

Primary score:
**1 / 11 = 9.09%**

Coding secondary:
**45.00 / 100**

Primary PASS:
- G01 only

Safety/protocol:
- critical failures 0
- constraint violations 0
- tool/protocol errors 0
- scientific retries 0
- no cloud fallback

Resource-aborted tasks:
- C03
- C06
- G02
- G03

Overall resource envelope:
- peak MLX 4568.324 MiB
- minimum free 4%
- peak swap 2018.31 MB
- boundary clears 62
- mean clear latency 3.188 ms
- max clear latency 7.841 ms

Important: the boundary reclamation mechanism remained operational, but long agent histories still drive active/KV/request pressure beyond the safe floor on an 8 GB machine.

### Genuine capability failures

E01 and E02 completed without resource abort and were nevertheless wrong.

E01 produced the wrong causal ratio/GO-NO-GO interpretation.
E02 failed the supplied upper-bound calculation and decision.

Therefore the low baseline is not explained only by RAM pressure: current 8B 3-bit reasoning quality is also a limiting factor.

### Scientific interpretation

CAPABILITY 001 is intentionally retained as the canonical practical-agent reference rather than optimized away:

- practical-agent primary = 9.09%
- coding = 45/100

Future systems must be compared jointly on memory, speed and capability. A memory/speed optimization that degrades this already-low capability is not acceptable by default; a larger/better-represented model has substantial room to demonstrate improvement.

Raw local evidence:
`results-local/capability/capability-001/capability-001-20260821-191000/`

## Exact next step — MEMORY-FRONTIER 001

Frozen plan:
`research/memory/memory-frontier-001-plan.md`

Goal: build the real-M1 RAM/speed Pareto frontier for the same full-parameter-count Qwen3-8B before implementing prefetch/buffering or scaling model size.

Measure five configurations:
- F0 FULL fully resident
- F1 H32 persistent transformer hotset
- F2 H24
- F3 H16
- F4 H8 aggressive low-residency reference

Key rules:
- real greedy unknown-token M1 generation, not M5 oracle verification
- first three canonical REALGEN 001 prompts, max 64 generated tokens/EOS
- exact token parity required versus F0
- two fresh runs/configuration in symmetric order
- fresh-process host admission free >=60% twice, swap <=5600 MB
- no deliberate cache purge
- measure resident bytes, MLX peak, free/swap, logical streamed weight bytes/token, process-read diagnostic, TTFT, real generation tok/s and E2E tok/s

The result should reveal where RAM savings cease to justify the speed cost and provide the architectural basis for models exceeding physical RAM.

## Later

1. MEMORY-FRONTIER 001
2. async prefetch / double-buffering / transfer-chunk and direct range-I/O experiments
3. OUTCORE-BLOCK 001 — amortize streamed weight loads across exact-valid M>1 blocks
4. representation experiments where justified
5. scale toward 27B/32B full-parameter-count execution
6. rerun the frozen capability baseline for any promoted representation/model/runtime that could affect practical capability

## Local-only warning

Most experimental runners/raw evidence remain local unless explicitly synchronized. The stable admitted bridge itself is published. Pi should not spend tokens on Git/HANDOFF/ROADMAP except for a narrowly requested mechanical code transfer when ChatGPT cannot access a local implementation file.
