# LOOM 30B Apple MoE Paging Stage 1R 001 — Preregistration

Date: 2026-08-29
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Recover the first scientifically valid Qwen3-30B-A3B Apple Metal MoE expert-paging generation measurement after Stage 1 closed as `LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO` for harness/instrumentation reasons.

Stage1R is not a new model/runtime hypothesis. It repeats the original frozen scientific workload using the exact verified artifact/runtime and the recovered, mechanically validated harness.

## Prior checkpoint status

Canonical Stage 1 result:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-result.md`

No valid S8/S16/S24 scientific measurement exists from Stage 1. Prior attempted executions are instrumentation-invalid and support no performance claim.

Harness recovery classification:
**`LOOM_30B_STAGE1_HARNESS_RECOVERY_GO`**

Recovery evidence:
`results-local/research/30b-stage1-harness-recovery-001/20260829T195240Z/`

## Frozen recovered harness

Local research runner:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`

Frozen SHA256:
`6857a7f7deeb6c8d88db81df4ce06e4ac2e571079971cebdd16718b625930ecf`

Frozen size:
- 446 lines
- 26,980 bytes

Before inference the runner SHA256 MUST match exactly. If it does not, STOP as mechanical invalidity. No runner edit is authorized inside Stage1R.

Recovered instrumentation properties already synthetic-tested:
- command/profile RUNNING state persisted before child launch;
- stdout/stderr continuously drained to durable evidence;
- telemetry persisted incrementally;
- COMPLETE/FAILED state finalized in `finally`;
- >2 MiB synthetic mixed stdout/stderr drain passed;
- nonzero child failure persistence passed;
- resume-to-pre-inference path passed.

## Frozen runtime

Source/runtime:
- repo `kisasexypantera94/llama.cpp`
- branch `moe-expert-residency`
- commit `41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
- Metal build only; no source patching
- reuse exact previously verified build

Expected binary SHA256:
`c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`

If source or binary provenance differs, STOP before inference.

## Frozen model artifact — local reuse only

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Existing verified local path:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Expected size:
`12,424,439,872` bytes

Expected SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Stage1R authorizes **no model download**. If the local artifact is absent or SHA/size mismatches, STOP mechanically before inference.

## Frozen inference workload

Prompt EXACTLY:
`Spiega in italiano, in circa 120 parole, perché un modello Mixture-of-Experts può avere molti parametri totali ma usarne solo una parte per ogni token. Descrivi anche il ruolo del router e un vantaggio pratico.`

Generation:
- deterministic temperature 0
- maximum 96 generated tokens
- context 1024
- `--moe-n-layers 48`
- `--no-mmap`
- `--no-warmup`
- expert tensor override exactly as required by the frozen PoC for CPU source weights (`--cpu-moe` in the validated command path)
- `-ub 1` for every profile
- one fresh process per measured profile
- no speculative decoding
- no prompt/RAG/tools/system capability injection

Required coherence check: output must be readable Italian and correctly state at minimum that only a subset of experts is selected/active per token and that a router/gating mechanism selects experts.

## Frozen slot sweep

Profiles in order:
1. `S8`: `--moe-n-slots 8`
2. `S16`: `--moe-n-slots 16`
3. `S24`: `--moe-n-slots 24`, conditionally

S8 and S16 are required unless a host-safety abort prevents continuation.

S24 may run only if S16 exits cleanly and all are true:
- no critical/red memory-pressure condition observed;
- peak swap <= 3.5 GiB during S16;
- no OOM/process kill;
- host remains responsive and at least 5% memory headroom is observed by the frozen harness telemetry.

Never test 32 slots.

Prior Stage 1 instrumentation-invalid attempts do not count as scientific profile trials. Inside Stage1R, once a profile yields a valid measured inference, no retry of that profile is authorized.

## Evidence durability requirement

Before each profile child launch, durable evidence must already contain:
- exact command;
- profile identifier;
- RUNNING state;
- model/binary/harness provenance;
- start timestamp.

During execution:
- subprocess output must be continuously drained and written to disk;
- host telemetry must be persisted incrementally.

On every exit/error path:
- profile state, exit/stop reason and retained evidence must be finalized even if inference fails.

If this durability mechanism itself fails, classify mechanically and STOP rather than retrying inference.

## Metrics/evidence

For every attempted valid Stage1R profile persist:
- exact command and harness/binary/model SHA;
- complete output text;
- exit/stop reason;
- model load/start wall;
- TTFT where observable;
- generated token count;
- generation tok/s from runtime timings;
- E2E wall;
- prompt/prefill rate where observable;
- expert paging/cache statistics if exposed;
- RSS/wired/compressed memory, swap and memory pressure before/during/after;
- storage read bytes/rate if observable without system mutation;
- cleanup proof and no lingering inference process.

Aggregate:
- best safe profile by measured generation tok/s;
- speedup ratio vs historical references `1.402 tok/s` and `1.229233 tok/s`;
- memory/swap cost across attempted profiles.

## Frozen classification

`LOOM_30B_APPLE_MOE_PAGING_STAGE1R_GO` only if all are true:
1. recovered harness SHA exactly matches `6857a7f7deeb6c8d88db81df4ce06e4ac2e571079971cebdd16718b625930ecf`;
2. exact model SHA/size verified;
3. exact frozen source/runtime/binary provenance verified;
4. at least one measured profile exits cleanly with coherent output;
5. best safe measured generation throughput >= `2.5 tok/s`;
6. no model-output corruption/NaN/repeated-token collapse;
7. no critical host memory-pressure/OOM event in the promoted best profile;
8. complete durable evidence retained;
9. zero source/runtime/package/system mutation.

If valid measurements exist but the scientific gate fails: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R_NO_GO`.

If instrumentation/artifact/runtime provenance prevents a valid test: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`.

A GO does not automatically replace canonical DEEP. It authorizes Stage 2 reproducibility + matched practical comparison + quality preservation.

## Boundaries

Forbidden:
- any model/GGUF download;
- changing/requantizing the model;
- changing the frozen harness;
- package-manager installs;
- source/runtime patching;
- slot counts other than 8/16/24;
- post-hoc flag tuning;
- retry of a scientifically valid measured profile;
- validator/guided-repair research;
- 8B/4B inference;
- Heretic/provider/UI/production integration;
- Git commit/push by Pi.

Use a fresh Stage1R evidence root under:
`results-local/research/30b-apple-moe-paging-stage1r-001/<timestamp>/`

The existing GGUF remains in the prior Stage1 artifact path and should be referenced/reused read-only rather than copied if the harness supports that without mutation.
