# LOOM 30B Apple MoE Paging Stage 1 001 — Result

Date: 2026-08-29
Classification: **LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO**

## Summary

Stage 1 did not produce any scientifically valid S8/S16/S24 inference measurement. The model/runtime therefore did **not** scientifically fail. The checkpoint closed mechanically because the harness/instrumentation path invalidated the attempted execution evidence.

## Frozen artifact/runtime provenance retained

- Model: `Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
- Model size: `12,424,439,872` bytes
- Model SHA256: `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`
- Runtime source: `kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
- Binary SHA256: `c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`

No second model/download, package install, runtime/source patch, or Git action by Pi occurred.

## Mechanical invalid attempt 1 — stdio pipe backpressure

The first S8 attempt is classified:

`MECHANICAL_INVALID_ATTEMPT_STDIO_PIPE_BACKPRESSURE`

Diagnostics showed:
- stdin `/dev/null`;
- stdout/stderr both attached to a 65536-byte pipe;
- live stack dominated by `console::readline -> fflush -> __sflush -> _swrite -> __write_nocancel`;
- the harness did not continuously drain subprocess output.

The attempt was manually terminated only after confirming the instrumentation failure. Elapsed wall, TTFT and throughput from this attempt are invalid and support no model-performance claim.

Retained local evidence includes:
- `attempts/S8-mechanical-invalid-attempt-stdio-pipe-backpressure.json`
- `attempts/post-stdio-correction-execution-integrity.json`

## Mechanical invalid attempt 2 — evidence persistence gap

After a minimum stdio-drain correction, the launcher still did not retain the required completed profile output, telemetry, profile JSON or aggregate result. No S8/S16/S24 scientific measurement could be reconstructed.

Pi correctly stopped rather than launching an unregistered further inference retry.

## Harness recovery

A separate no-model checkpoint completed:

**`LOOM_30B_STAGE1_HARNESS_RECOVERY_GO`**

Evidence:
`results-local/research/30b-stage1-harness-recovery-001/20260829T195240Z/`

Concrete diagnosis: profile output, telemetry and final state were retained only after `process.wait()`, reader join and post-run work. Live evidence was RAM-only until then, so interruption/error after child launch could leave no durable profile evidence.

Recovered behavior:
- command/profile RUNNING state persisted before launch;
- combined subprocess output streamed directly to disk;
- telemetry persisted incrementally;
- COMPLETE/FAILED evidence finalized in `finally`.

Synthetic recovery tests passed:
- clean child exit 0 with `2,097,152` bytes retained;
- stdout marker bytes `1,048,576`;
- stderr marker bytes `1,048,576`;
- 256 drain events;
- telemetry persisted during execution;
- nonzero child exit 7 retained full output/profile/telemetry/report;
- resume path detected an existing verified artifact and stopped immediately before model inference;
- no `llama-cli` inference was launched during recovery.

Recovered local harness freeze:
- path `scripts/loom_30b_apple_moe_paging_stage1_001.py`
- SHA256 `6857a7f7deeb6c8d88db81df4ce06e4ac2e571079971cebdd16718b625930ecf`
- 446 lines
- 26,980 bytes
- file remains a local untracked research runner; exact content was captured with `git diff --no-index -- /dev/null ...` before continuation.

## Scientific interpretation

No valid generation throughput, TTFT, E2E, output-coherence, paging/cache, memory/swap or safety-gate result exists for S8, S16 or S24.

Therefore:
- no speedup claim vs `1.402 tok/s` or `1.229233 tok/s` is supported;
- no conclusion about Apple MoE expert paging performance on the base M1 8 GiB host is supported;
- a fresh preregistered recovery run may reuse the exact verified artifact/runtime and the frozen recovered harness, because the prior attempts failed mechanically before yielding a valid scientific measurement.
