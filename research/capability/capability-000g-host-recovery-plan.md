# CAPABILITY 000G — scientific process teardown / natural host recovery

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

After a real Qwen3-8B + Pi scientific attempt, does normal termination of the scientific server/model process return the Apple M1 / 8 GB host to the passive launch-ready state (`free >=60%`) within a bounded interval, or does process/resource lifecycle remain incomplete?

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- `prefill_step_size=512`
- localhost bridge
- no model/runtime/representation change

## Pre-load admission

Require before the model is loaded:
- system free memory >=60%
- swap <=5600 MB

If not met naturally, classify host-not-ready and stop. Do not purge, kill unrelated user processes, manipulate swap, or allocate/free artificial memory.

## Workload

Use one fresh scientific server/model process. Execute exactly one bounded workload sufficient to materialize the model and exercise real generation/tool-path memory. Reusing the frozen numbers.txt Pi task through the first two model turns is acceptable; stop as soon as the workload finishes or hits the existing <5% free / >5600 MB swap gate.

The workload result itself is secondary. The primary experiment starts at process termination.

## Teardown

Terminate the scientific server through its normal harness lifecycle, not `kill -9`.

Record:
- parent PID
- server PID
- Pi PID
- all known child PIDs/process tree
- localhost listener PID/port
- process exit codes
- exact termination timestamps

After termination, prove whether each scientific PID is dead and whether the server listening socket is gone.

Do not call `mx.clear_cache`, `gc.collect`, purge, or other cleanup treatment inside the scientific process before exit.

## Passive recovery sampling

After the final scientific process has exited, sample host state at approximately:

- t=0 s
- 1 s
- 3 s
- 5 s
- 10 s
- 20 s
- 30 s
- 45 s
- 60 s

Stop early only if free memory >=60% for two consecutive scheduled samples and all scientific PIDs/listeners are confirmed dead.

For every sample record:
- system free memory % (`memory_pressure` or established canonical metric)
- PhysMem used/unused/wired/compressor
- swap used/capacity
- scientific PID liveness
- process tree / relevant Python/Node processes
- listener state
- top memory processes diagnostically if available

Do not mutate host state to improve recovery.

## Classification

Use one:

- `CAPABILITY_000G_NATURAL_HOST_RECOVERY_PASS` — all scientific processes/listeners die and host returns to >=60% free within the bounded passive interval.
- `CAPABILITY_000G_PROCESS_LIFECYCLE_INCOMPLETE` — one or more scientific server/model/child processes or listener remain alive after normal teardown.
- `CAPABILITY_000G_OS_RECOVERY_SLOW_OR_INCOMPLETE` — all scientific processes/listeners are dead but host remains below 60% at 60 s.
- `CAPABILITY_000G_HOST_NOT_READY` — initial pre-load gate cannot be met naturally.
- `CAPABILITY_000G_INFRASTRUCTURE_INCOMPLETE` — harness cannot establish valid process/recovery evidence.

## Interpretation

Do not call delayed recovery a memory leak without process/object evidence.

If natural recovery passes, the next CAPABILITY 000F rerun may add only a passive wait-until-gate step between attempts; this is host admission control, not a model-memory treatment.

If process lifecycle is incomplete, repair teardown before rerunning capability.

No chunk-size, prompt, KV, context, precision, or model change is allowed in 000G.
