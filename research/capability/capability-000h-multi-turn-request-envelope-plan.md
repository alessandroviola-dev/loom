# CAPABILITY 000H — Multi-turn Request Envelope

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

Which captured later Pi request first becomes intrinsically unsafe on the canonical Qwen3-8B 3-bit / BF16 KV / step-512 runtime, and how much extra memory pressure is caused by sequential request history versus request size itself?

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- prefill_step_size 512
- same tokenizer/chat template/tool schemas
- no prompt/tool compression
- no cleanup treatment
- no model/runtime/representation changes

## Inputs

Recover the exact request bodies captured by CAPABILITY 000G. Use all available workload requests in order, including the final request associated with the resource-abort boundary. Do not reconstruct a request manually when an original captured body exists.

## Phase A — request anatomy

For each request record:

- exact input tokens
- messages by role
- system/user/assistant/tool token contribution where separable
- tool-result bytes/tokens introduced since prior request
- context headroom
- expected BF16 KV logical bytes and allocated capacity

## Phase B — fresh envelope

For every captured request Ri, use a separate fresh server/model process and execute Ri as the first request after model load.

Measure:

- completion/abort
- actual M segments
- prefill wall and tok/s
- generation tokens/wall/tok/s if generation is required
- KV logical/capacity
- peak/active/cache MLX
- minimum free memory
- peak swap

Each fresh run must satisfy the normal pre-load host gate: free >=60%, swap <=5600 MB. After process exit, passively wait until the host again satisfies the gate; CAPABILITY 000G established that natural recovery normally occurs within seconds. No purge or forced cleanup.

## Phase C — sequential envelope

Use one fresh server/model process. Execute the same captured request bodies in original order with no cleanup between requests. Stop at completion of the full series or the hard resource gate.

Record the same metrics per turn plus post-request active/cache state.

## Analysis

For each Ri compare fresh versus sequential:

- peak MLX delta
- minimum-free delta
- post-request active/cache delta
- prefill wall delta
- KV/capacity

Identify:

1. first request that fails when fresh, if any;
2. first request that passes fresh but fails sequentially, if any;
3. sequential overhead trend by turn;
4. request/token growth trend;
5. whether the observed abort boundary is primarily intrinsic request size, sequential allocator/state pressure, or system-host variability.

Do not label memory leak without retained-live-object evidence.

## Resource policy

Hard abort only at free <5% or swap >5600 MB after a run is admitted.

No rescue, retry, purge, mx.clear_cache, gc.collect, prompt change, tool change, context reduction, KV quantization, step change or model change.

## Evidence

Store under `results-local/capability/capability-000h/<run-id>/` with at least:

- summary.json
- request-anatomy.json
- fresh-runs.jsonl
- sequential-runs.jsonl
- comparisons.json
- memory-samples.jsonl
- copied/request references for exact captured bodies

## Classification

Use one:

- `CAPABILITY_000H_INTRINSIC_LATE_TURN_LIMIT`
- `CAPABILITY_000H_SEQUENTIAL_ACCUMULATION_LIMIT`
- `CAPABILITY_000H_ALL_CAPTURED_REQUESTS_SAFE`
- `CAPABILITY_000H_HOST_VARIABILITY_DOMINANT`
- `CAPABILITY_000H_INFRASTRUCTURE_INCOMPLETE`

This is attribution only. Do not implement a treatment.