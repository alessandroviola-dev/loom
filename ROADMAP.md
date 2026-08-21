# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_001_BASELINE_COMPLETE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2.

REALGEN 001:
- 13.184615357 tok/s real M1 generation
- 12.046861457 tok/s E2E

Admitted Pi runtime:
- context 4096
- max assistant output 2048
- `prefill_step_size=512`
- localhost-only provider
- tools read/write/edit/bash
- after each fully completed response: ownership-check finished response, detach only stale completed-response `prompt_cache`, then one `mx.clear_cache()`

Stable bridge source is published at `4d204471aedb9262ccaa3b86f29b0e344d0c2884`.

## A — Capability baseline — COMPLETE

### CAPABILITY 000M — real-Pi admission PASS

Three independent real-Pi attempts passed 3/3 functionally and strictly, with no resource aborts or telemetry errors. This admitted the current bridge/runtime to capability testing.

### CAPABILITY 001 — BASELINE COMPLETE

Report:
`research/capability/capability-001-baseline-result.md`

Corrected frozen suite: 11 tasks.

Primary practical-agent success:
**1 / 11 = 9.09%**

Coding Benchmark 01 secondary score:
**45.00 / 100**

Primary PASS:
- G01 safe fast-forward synchronization

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

Overall observed resource envelope:
- peak MLX 4568.324 MiB
- minimum system free 4%
- peak swap 2018.31 MB
- 62 request-boundary clears
- mean clear latency 3.188 ms; max 7.841 ms

The admitted boundary reclamation remains useful but does not eliminate long-history pressure on an 8 GB host.

E01 and E02 also failed without resource aborts, demonstrating genuine reasoning limitations in the current Qwen3-8B 3-bit baseline. Therefore the low practical-agent result is not a pure memory artifact.

This score is now the canonical capability reference for future comparisons. Do not optimize it away or rerun selectively to obtain a preferred score.

## B — MEMORY-FRONTIER 001 — NEXT

Frozen plan:
`research/memory/memory-frontier-001-plan.md`

Goal: measure a **real greedy M1** Pareto curve between persistent model residency, unified-memory headroom, weight-streaming I/O and real generation speed.

Configurations:
- F0 FULL fully resident
- F1 H32 transformer hotset
- F2 H24
- F3 H16
- F4 H8 aggressive low-residency reference

This experiment reuses proven Stretch hotset/streaming implementation where valid, but old M5 oracle token/s values are not accepted as the new speed metric.

Requirements:
- exact real-M1 token parity against F0 for every partial-residency point
- first three canonical REALGEN 001 prompts
- greedy generation, max 64 tokens/EOS
- two fresh runs/configuration in symmetric order `F0 -> F4 -> F3 -> F2 -> F1 -> F1 -> F2 -> F3 -> F4 -> F0`
- fresh-process host admission free >=60% twice and swap <=5600 MB
- no deliberate macOS cache purge
- hard resource floor free <5% / swap >5600 MB

Measure:
- resident raw-weight bytes / fraction
- MLX load and peak footprint
- system free/swap
- TTFT
- real generation tok/s
- E2E output tok/s
- direct logical streamed-weight bytes/generated token
- process-read bytes/token only as a diagnostic, not claimed physical SSD traffic
- exact output token IDs/EOS

The objective is a RAM↔speed frontier, not a single preselected winner. Descriptive speed bands:
- >=10 tok/s: interactive candidate
- 5–<10: usable experimental
- 1–<5: slow reference
- <1: impractical reference

This frontier is the system-design bridge toward models whose weights exceed comfortable physical RAM.

## C — Hide streamed-weight cost

After MEMORY-FRONTIER 001, use the measured Pareto point(s) to isolate, one factor at a time:

1. asynchronous prefetch
2. double/triple buffering
3. transfer/super-layer chunk sizing
4. direct safetensors range I/O / mmap / pread
5. macOS page-cache behavior
6. resident-hotset selection if the real-M1 frontier reveals a different useful point than the older M5 verifier curve

Do not begin these treatments inside MEMORY-FRONTIER 001.

## D — Amortize I/O across tokens

OUTCORE-BLOCK 001 revisits exact-valid M>1 blocks specifically for out-of-core execution, where one streamed weight load may serve multiple candidate token positions.

Measure SSD/logical bytes per accepted token, wall/block, prefetch overlap and resident memory. Do not confuse the existing M5 oracle verifier rate with end-to-end agent throughput.

## E — Representation and capability

Potential later factors include:
- mixed/selective precision
- compressed cold weights
- quantized KV
- out-of-core storage formats

Full parameter count remains a major project condition.

Any promoted representation/model/runtime that can affect model behavior must be compared against CAPABILITY 001:
- practical-agent primary 9.09%
- Coding Benchmark 45/100

A candidate is not promoted solely because it fits or is faster.

## F — Scale beyond 8B

1. establish the real-M1 RAM/speed frontier on the well-characterized 8B
2. reduce/hide the cost of partial residency
3. transfer the architecture to models exceeding comfortable physical RAM
4. first major scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
5. optimize toward genuinely usable speed and measure capability against the frozen baseline

## Immediate order

1. MEMORY-FRONTIER 001 — real M1 RAM/speed Pareto curve
2. prefetch/buffering/range-I/O based on measured bottleneck
3. OUTCORE-BLOCK 001
4. representation work where justified by evidence
5. scale toward 27B/32B
6. rerun frozen capability baseline for promoted behavior-affecting candidates

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates; use narrow mechanical code transfer only when a stable local implementation must be published and ChatGPT cannot read the uncommitted file.
