# CAPABILITY 000G — Natural Host Recovery Result

Date: 2026-08-21
Classification: `CAPABILITY_000G_NATURAL_HOST_RECOVERY_PASS`

## Question

Does Apple M1 / macOS naturally recover host memory after the scientific Qwen3-8B process exits, or does LOOM leave a process/resource lifecycle problem behind?

## Result

Initial host state: 70% free, swap 1594.44 MB.

The bounded integrated workload executed 5 model requests, reached MLX peak 4212.45 MB and crossed the resource gate at 4% free. Peak swap was 2020 MB.

Normal SIGTERM teardown terminated Pi, bridge and server. No scientific parent/child process or localhost listener remained alive after teardown.

Natural recovery after scientific process exit:

- t=0 s: 6% free
- t=1 s: 5% free
- t=3 s: 70% free
- t=5 s: 71% free
- t=60 s: 71% free

First >=60% sample occurred at 3 s; two consecutive >=60% samples were reached by 5 s.

## Interpretation

The low post-run sample seen in CAPABILITY 000F was a transient macOS recovery state, not evidence of a surviving LOOM process or memory leak.

Scientific processes/listeners died normally and memory returned naturally within a few seconds. Swap recovery lagged but remained far below the 5600 MB hard limit.

A separate finding is now more important: even from a 70% pre-load host state, the integrated workload reached five model requests and eventually crossed the 5% free-memory floor. Therefore the remaining capability-bridge bottleneck is sustained multi-turn memory pressure, not process teardown.

## Decision

Close host-lifecycle attribution.

Do not change model representation, context, BF16 KV or prefill step based on teardown evidence.

Next isolate the real multi-turn request trajectory: recover the exact request bodies from the 000G workload and determine which later turn is intrinsically outside the safe envelope versus which cost is caused by sequential accumulation.