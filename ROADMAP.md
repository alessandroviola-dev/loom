# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000D_FIX1_PREFLIGHT_FAIL_NO_SCIENCE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models.

Every major direction is judged on:
1. memory
2. speed
3. capability

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2.

REALGEN 001:
- real generation **13.184615357 tok/s**
- end-to-end **12.046861457 tok/s**
- raw weights **3,583,928,320 B**
- MLX peak **3,826,575,836 B**

REALGEN 002 custom M1 qmv transfer: exact but **-9.178832%**; closed.

Pure full-model layer streaming is already known to save RAM and destroy throughput. It is not the endpoint.

## A — Capability baseline — ACTIVE

Goal: benchmark the practical intelligence of the current Qwen3-8B through Pi before future representation changes.

### CAPABILITY 000–000B

The local MLX bridge works and a genuine Qwen-generated Pi tool call was observed. There is one model instance, no duplication. The first real Pi request is ~1500 tokens and the main dynamic pressure comes from large prefill qmm/transient allocation plus BF16 KV, not Pi RSS or full-sequence logits.

### CAPABILITY 000C — COMPLETE

`prefill_step_size=512` dominates canonical 2048 on the exact 1504-token Pi prefill:

- 512: **23.74 s**, **63.36 tok/s**, **4089.8 MB peak**, bit-exact
- 2048: **27.91 s**, **53.88 tok/s**, **4180.1 MB peak**, bit-exact

This makes 512 the admitted integrated-agent candidate, not yet a universal runtime default.

### CAPABILITY 000D — HARNESS FAILURE / NO SCIENCE

First integrated Pi-loop attempt failed before prefill/tool execution because instrumentation assumed `.shape` on a list.

Root cause:
`AttributeError: 'list' object has no attribute 'shape'`
at `scripts/capability_000d_pi_loop.py`, `watched_prompt`, line 114.

No evidence against 512 was produced.

### CAPABILITY 000D Fix1 — PREFLIGHT FAILURE / NO SCIENCE

Fix1 repaired the original list-shape issue with list-safe prompt observation and exception-contained callbacks. The canonical model successfully executed a tiny local preflight request and returned `OK.`.

However the harness failed to produce a completed turn-metrics record, so the scientific numbers.txt Pi-loop run was not started.

The punctuation difference `OK.` vs `OK` is not itself a harness-science failure. Preflight should test infrastructure health, not exact instruction-following. The remaining blocker is reliable non-fatal telemetry lifecycle closure.

Report:
`research/capability/capability-000d-fix1-preflight-failure.md`.

### CAPABILITY 000D Fix2 — NEXT

Minimal harness repair only:

1. preserve `prefill_step_size=512`;
2. preserve model, 3-bit weights, BF16 KV, context 4096, Pi tools and prompts;
3. keep list-safe prompt instrumentation;
4. make telemetry observational and non-fatal;
5. require preflight to produce a valid local-model response and complete request/turn records; exact punctuation is not a preflight gate;
6. then rerun the original frozen numbers.txt Pi loop exactly once.

If the real loop passes, proceed to CAPABILITY 001. If the model actually runs and hits the resource floor, that is valid scientific evidence.

### CAPABILITY 001 — BLOCKED pending successful 000D admission

Frozen 12-task suite: coding + Git safety + experiment/result reasoning.

This becomes the capability reference for future representation changes.

## B — RAM/speed frontier

After CAPABILITY 001, run MEMORY-FRONTIER 001 on real M1 generation with controlled partial residency.

Measure together:
- resident bytes
- MLX peak
- system free/swap
- SSD bytes/token
- real tok/s
- TTFT
- correctness

Output: RAM <-> tok/s Pareto curve.

## C — Hide SSD cost

Then test one factor at a time:
1. asynchronous prefetch
2. double/triple buffering
3. transfer/super-layer chunk sizing
4. direct safetensors range I/O / mmap / pread
5. macOS page-cache behavior
6. resident-hotset selection

## D — Amortize I/O across tokens

OUTCORE-BLOCK 001 will revisit M>1 execution specifically for out-of-core models, where one weight load may serve several token positions.

## E — Representation without shrinking parameter count

Potential later factors:
- mixed/selective precision
- compressed cold weights
- quantized KV
- storage formats designed for out-of-core execution

Judge every representation by `memory + speed + capability`.

## F — Scale beyond 8B

1. solve architecture on the well-characterized 8B
2. apply it to a model whose weights exceed comfortable physical RAM
3. first major checkpoint: **27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM**
4. then optimize speed toward interactivity

## Immediate order

1. CAPABILITY 000D Fix2 — minimal telemetry repair + identical Pi-loop rerun
2. CAPABILITY 001
3. MEMORY-FRONTIER 001
4. prefetch/buffering/range-I/O work
5. OUTCORE-BLOCK 001
6. scale toward 27B/32B

## Local-only implementation warning

Several recent CAPABILITY scripts/evidence currently exist only in the local worktree under `<repository-root>` and `results-local/`. HANDOFF.md lists the known paths. A new chat should not assume those scripts have been committed to GitHub until they are explicitly synchronized.

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
