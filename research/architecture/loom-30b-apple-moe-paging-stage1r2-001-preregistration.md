# LOOM 30B Apple MoE Paging Stage 1R2 001 — Preregistration

Date: 2026-08-29
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Obtain the first scientifically valid Qwen3-30B-A3B generation measurement on the base M1 8 GiB host with Apple Metal MoE expert paging after Stage1 and Stage1R closed mechanically.

Stage1R2 preserves the original model/runtime/scientific workload. The only authorized recovery delta is mechanical: use the correct noninteractive `llama-completion -no-cnv` frontend and the already synthetic-validated bounded-output harness.

## Prior checkpoint status

Stage1 result:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-result.md`
Classification: `LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`.

Stage1R result:
`research/architecture/loom-30b-apple-moe-paging-stage1r-001-result.md`
Classification: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`.

Noninteractive frontend recovery result:
`research/architecture/loom-30b-noninteractive-frontend-recovery-001-result.md`
Classification: `LOOM_30B_NONINTERACTIVE_FRONTEND_RECOVERY_GO`.

No valid S8/S16/S24 scientific measurement exists from the prior mechanical attempts. They support no performance claim.

## Frozen recovered harness

Runner:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`

Required SHA256 before inference:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`

No runner edit is authorized during Stage1R2. If SHA differs, STOP mechanically before inference.

Instrumentation freeze:
- stdout/stderr streamed directly to durable disk;
- bounded/O(1) drain accounting plus bounded analysis tail;
- fsync every 1 MiB and at completion;
- hard per-profile subprocess-output cap: `64 MiB` (`67,108,864` bytes);
- exceeding the cap terminates the child and records `MECHANICAL_OUTPUT_RUNAWAY`;
- telemetry persists incrementally;
- profile/report finalization occurs in `finally`.

## Frozen runtime/source

Repository: `kisasexypantera94/llama.cpp`
Branch: `moe-expert-residency`
Commit exactly:
`41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Source must be clean at the frozen commit. No source patching.

## Frozen noninteractive binary

Use `llama-completion`, not `llama-cli`.

Required `llama-completion` SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

The binary must come from the existing frozen source/build provenance established by `LOOM_30B_NONINTERACTIVE_FRONTEND_RECOVERY_GO`.

If the binary is absent or SHA differs, STOP mechanically. No rebuild is authorized inside Stage1R2.

## Frozen model artifact — local reuse only

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Existing local path:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Required size:
`12,424,439,872` bytes

Required SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

No download, copy, requantization, or model substitution is authorized. Reuse/reference the existing verified artifact read-only.

## Frozen inference workload

Prompt EXACTLY:
`Spiega in italiano, in circa 120 parole, perché un modello Mixture-of-Experts può avere molti parametri totali ma usarne solo una parte per ogni token. Descrivi anche il ruolo del router e un vantaggio pratico.`

Common command shape:
`llama-completion -m <verified-GGUF> -p <exact-prompt> -n 96 -c 1024 --temp 0 --moe-n-slots <S> --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -ub 1 -no-cnv`

Frozen generation settings:
- deterministic temperature 0;
- maximum 96 generated tokens;
- context 1024;
- `--moe-n-layers 48`;
- `--no-mmap`;
- `--no-warmup`;
- `--cpu-moe`;
- `-ub 1`;
- `-no-cnv`;
- no speculative decoding;
- no prompt/RAG/tools/system capability injection;
- one fresh `llama-completion` process per measured profile.

Required coherence guard: output must be readable Italian and correctly state at minimum that only a subset of experts is active/selected per token and that a router/gating mechanism selects experts.

## Frozen slot sweep

Profiles in order:
1. S8: `--moe-n-slots 8`
2. S16: `--moe-n-slots 16`
3. S24: `--moe-n-slots 24`, conditionally

S8 and S16 are required unless host safety or mechanical invalidity prevents continuation.

S24 may run only if S16 exits cleanly and all are true:
- no critical/red memory-pressure condition observed;
- peak swap <= 3.5 GiB during S16;
- no OOM/process kill;
- host remains responsive;
- at least 5% memory headroom is observed by frozen telemetry.

Never test S32.

## Durable evidence requirements

Use a fresh evidence root:
`results-local/research/30b-apple-moe-paging-stage1r2-001/<timestamp>/`

Before every profile child launch persist:
- exact command;
- profile identifier;
- RUNNING state;
- harness/model/binary/source provenance;
- start timestamp.

During execution persist continuously/incrementally:
- combined subprocess output;
- output byte count;
- host telemetry.

On every exit/error path finalize:
- profile state;
- exit/stop reason;
- retained telemetry/output metadata;
- aggregate/report state.

If durability itself fails, STOP mechanically and do not retry the profile.

If the 64 MiB output cap triggers, classify the attempt as `MECHANICAL_OUTPUT_RUNAWAY`, terminate the child, persist evidence and STOP Stage1R2 without retry.

## Metrics

For every valid attempted profile retain:
- exact command and harness/binary/model SHA;
- complete bounded output;
- exit/stop reason;
- load/start wall where observable;
- TTFT where observable;
- generated token count;
- generation tok/s from runtime timings;
- E2E wall;
- prompt/prefill rate where observable;
- expert paging/cache statistics if exposed;
- RSS/wired/compressed memory;
- swap and memory pressure before/during/after;
- storage read bytes/rate if observable without system mutation;
- cleanup proof and no lingering inference process.

Aggregate:
- best safe profile by generation tok/s;
- speedup ratio vs historical `1.402 tok/s` compact practical DEEP reference;
- speedup ratio vs historical `1.229233 tok/s` exact-Q4 production reference;
- memory/swap cost across attempted profiles.

Prior Stage1R ~14 GiB swap is excluded from model comparison because that run was an interactive/output-memory runaway.

## Frozen classification

`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO` only if all are true:
1. harness SHA exactly matches `4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`;
2. exact model SHA/size verified;
3. exact source commit/cleanliness verified;
4. exact `llama-completion` SHA verified;
5. at least one measured profile exits cleanly with coherent output;
6. best safe measured generation throughput >= `2.5 tok/s`;
7. no output corruption/NaN/repeated-token collapse;
8. no critical host memory-pressure/OOM event in the promoted profile;
9. no output-runaway cap event;
10. complete durable evidence retained;
11. zero package/source/runtime/system mutation.

If valid scientific measurements exist but the throughput/coherence/safety gate fails: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_NO_GO`.

If instrumentation/artifact/runtime/frontend provenance prevents a valid test: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_MECHANICAL_NO_GO`.

A GO does not automatically replace canonical DEEP. It authorizes Stage 2 reproducibility + matched practical comparison + quality preservation.

## Boundaries

Forbidden:
- any model/GGUF download;
- copying/requantizing/changing model;
- changing the frozen harness;
- rebuilding binaries;
- package-manager installs;
- source/runtime patching;
- use of `llama-cli`;
- omission of `-no-cnv`;
- slot counts other than 8/16/24;
- post-hoc flag tuning;
- retry of a scientifically valid measured profile;
- validator/guided-repair work;
- 8B/4B inference;
- Heretic/provider/UI/production integration;
- Git commit/push by Pi.