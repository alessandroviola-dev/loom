# Stretch 038 — S1_R8 deferred cleanup scientific preregistration

Status: **Prepared after feasibility GO. Not yet authorized to run.**

## Question

On the frozen promoted M1 S1_R8 path, does deferring the existing explicit
final MLX/Python cleanup across exactly two M5 blocks improve target
throughput while retaining every frozen numerical, oracle, persistence and
resource gate?

## Only factor

- **CONTROL:** S1_R8, `block1 -> gc.collect(); mx.clear_cache(); gc.collect()
  -> block2 -> same cleanup`; exactly 2 cleanup calls / 10 accepted tokens.
- **TREATMENT:** identical S1_R8, `block1 -> no explicit cleanup -> block2 ->
  one same cleanup`; exactly 1 cleanup call / 10 accepted tokens.

No zero-cleanup run, third block, adaptive policy, threshold, qmv,
quantization, runtime, model, M5, H36, KV, oracle, or persistence change is
allowed.

## Frozen conditions and gates

Qwen3-8B affine 3-bit/group64 BF16, MLX/mlx-metal 0.31.2, mlx-lm 0.31.3,
transformers 5.12.1, full H36 raw-weight persistence (`3,583,928,320 B`), BF16
KV, M1 S1_R8 custom qmv, and zero target-time recompilations remain frozen.
Every constituent must have two M5 blocks and ten accepted oracle tokens;
prompt/all target logit gates, top-1, exact oracle sequence, generated
sequence, and full persistence must pass without tolerance changes.

Launch gate remains free memory >=60% and swap <=5600 MB; abort remains free
memory <5% or swap >5600 MB. No purge or rescue is allowed. Each treatment
constituent must record before block 1, after block 1/before block 2, after
block 2/before cleanup, and after cleanup: free memory, swap, MLX active,
peak, and cache where exposed.

## Design and result policy

Use a fresh source identity/evidence root and a balanced ABBA order:
`CONTROL -> TREATMENT -> TREATMENT -> CONTROL`. Warmup is separate and
excluded. Primary metric is pooled accepted oracle tokens / total target-block
wall. Record separate block compute, transition, final-cleanup and total
10-token walls.

- Any treatment numerical/oracle/top-1/sequence/persistence failure is a valid
  scientific FAIL; stop, no rescue.
- Resource/provenance/harness failure is INCOMPLETE; preserve it, no reuse.
- Promote the cadence only if all constituents pass, resources remain stable,
  final cleanup recovers, and pooled treatment improvement is >=5%.
- Otherwise retain the current one-cleanup-per-M5-block canonical schedule.

The feasibility result (`8.188963%` mean wall reduction, eight stable treatment
cycles) is motivation only and is not reused as scientific evidence.
