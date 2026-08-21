# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — agentic bridge stabilization
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Last completed experiment: `CAPABILITY_000C_PREFILL_FRONTIER_COMPLETE`
Next experiment: `CAPABILITY_000D_PI_LOOP_ADMISSION`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

**Big models. Small machines.**

LOOM aims to run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Success requires memory fit, useful speed and retained capability.

## Operating split

Pi: local code, runtime inspection, tests, concise raw evidence.

ChatGPT: research direction, experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and checkpoint continuity.

## Canonical model/runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- Apple M1 / 8 GB
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- ordinary built-in M1 `qmv_fast`
- raw persistent weights `3,583,928,320 B`

REALGEN 001 remains the user-facing baseline:

- real generation **13.184615357 tok/s**
- end-to-end output **12.046861457 tok/s**
- exact greedy reference agreement on all six frozen prompts
- MLX peak `3,826,575,836 B`

REALGEN 002 M1_S1_R8 transfer was exact but **-9.178832%** throughput; closed.

## Capability bridge

CAPABILITY 000 proved the canonical Qwen3-8B can drive Pi: a genuine model-generated `read(numbers.txt)` tool call was observed. The integrated smoke then crossed the <5% free-memory floor.

### CAPABILITY 000A — complete

- exactly one model instance
- no model duplication
- Pi RSS ~45.55 MB
- model materialization was the largest static jump
- direct small requests survived
- real Pi prefill caused the dynamic cliff

### CAPABILITY 000B — complete

Exact first Pi request:

- total input **1504 tokens**
- system 608 / user 65 / tools 814 / other 17
- context headroom 2592 / 4096
- BF16 KV logical 1504 / capacity 1536
- current prefill segmentation `[1430,70,3]` at `prefill_step_size=2048`
- full-sequence logits not materially retained; final logits `[1,1,151936]`
- exact replay peak MLX **4180.1 MB**
- prefill wall **20.61 s**
- ~216 MiB persistent KV capacity
- ~546 MiB transient first-prefill peak

Attribution: weights and KV PROVEN; qmm/prefill temporaries and long system/tool prompt STRONGLY SUPPORTED; full-sequence logits and Pi RSS NOT SUPPORTED as the cliff cause.

### CAPABILITY 000C — complete

Report: `research/capability/capability-000c-prefill-frontier-result.md`.

Exact 1504-token request, one-factor `prefill_step_size` frontier:

- 2048 control: 27.91 s, 53.88 tok/s, 4180.1 MB peak
- 512: **23.74 s, 63.36 tok/s, 4089.8 MB peak, bit-exact**
- 256: 28.24 s, 53.26 tok/s, **3980.7 MB peak**, top1 same but not bit-exact
- Pareto frontier: **512, 256**

Relative to 2048, step 512 reduces prefill wall ~14.94%, raises effective prefill throughput ~17.59%, lowers peak MLX by 90.3 MB and lowers the measured transient by 90.3 MB, while preserving bit-exact final logits.

Decision: `512` is the operational candidate. It is not yet promoted to the full capability benchmark until an actual multi-turn Pi tool loop completes safely.

## Exact next step

Run `CAPABILITY 000D — Pi multi-turn loop admission with 512 prefill` from:
`research/capability/capability-000d-pi-loop-admission-plan.md`.

Use the same disposable numbers task and full Pi tool surface. Record every model turn's input length, prefill segmentation/wall, generation, KV state, MLX peak, system free/swap and tool result. Hard abort remains free <5% or swap >5600 MB.

Do not change context 4096, max output 2048, BF16 KV, 3-bit representation, system/tool semantics or model.

If 000D functionally completes, review the resource trajectory and then authorize the frozen 12-task CAPABILITY 001 suite under the same 512 prefill setting.

## Later

1. CAPABILITY 001 baseline
2. MEMORY-FRONTIER 001 partial-residency RAM/tok/s curve
3. async prefetch / buffering / direct range I/O
4. M>1 out-of-core weight-I/O amortization
5. scale toward 27B/32B
