# LOOM 30B Apple MoE Paging Stage 1R 001 — Result

Date: 2026-08-29
Classification: **`LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`**

## Summary

Stage1R did not produce a scientifically valid Apple MoE paging performance measurement. Exact harness/model/source/binary provenance was verified, but the frozen `llama-cli` frontend entered its interactive readline loop, emitted repeated `> ` prompts, and never produced a valid bounded one-shot completion. S16 and S24 were therefore not launched.

No throughput, TTFT, E2E, quality, or model-memory claim may be derived from this run.

## Evidence

Evidence root:
`results-local/research/30b-apple-moe-paging-stage1r-001/20260829T203413Z/`

Mechanical-stop audit:
`results-local/research/30b-apple-moe-paging-stage1r-001/20260829T203413Z/stage1r-external-mechanical-no-go.json`

## Provenance verified before inference

- harness SHA256: `6857a7f7deeb6c8d88db81df4ce06e4ac2e571079971cebdd16718b625930ecf`
- model size: `12,424,439,872` bytes
- model SHA256: `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`
- source commit: `41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
- `llama-cli` SHA256: `c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`
- Metal device: Apple M1

## S8 invalid attempt

Retained:
- exact command: `S8/command.json`
- streamed output: `S8/combined-output.txt`
- incremental telemetry: 616 samples, approximately `20:34:31Z` to `20:47:52Z`

Observed output file size: `4,554,688,520` bytes.

The retained output was dominated by repeated interactive `> ` prompts and contained no valid coherent Italian answer. The harness did not finalize the profile/report, so exit code, timings, generated token count and throughput are unavailable.

Telemetry observed during this mechanically invalid runaway included peak RSS ~1817.312 MiB, peak wired ~3654.578 MiB, peak compressed ~3465.25 MiB, peak swap ~13998.81 MiB, minimum reported headroom 21%, and no reported critical memory-pressure state. These values are **not** accepted as model-residency measurements because the frontend/harness was producing and retaining multi-gigabyte runaway output.

## Root cause

Inspection of the exact frozen source established that `llama-cli` is an interactive/conversational frontend. Its source explicitly rejects `--no-conversation`, directs non-conversation use to `llama-completion`, and contains the `> ` / `console::readline(...)` loop observed in the runaway.

Therefore this was a frontend-selection/instrumentation failure, not a scientific failure of Apple MoE expert paging.

## Consequence

Stage1R is closed mechanically. No profile was scientifically measured:
- S8: mechanically invalid
- S16: not launched
- S24: not launched

The next allowed step is a separately preregistered recovery using the exact same scientific workload with the exact frozen source/model but the non-interactive `llama-completion -no-cnv` frontend and bounded-output instrumentation.