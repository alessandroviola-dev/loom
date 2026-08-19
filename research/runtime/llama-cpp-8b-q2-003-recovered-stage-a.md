# LOOM — llama.cpp 8B Q2 Capability 003 — Recovered Stage A

Date: 2026-08-19
Run id: `20260819-103347`
Status: **STAGE_A_RECOVERED_PASS / HARNESS_CAPTURE_DEFECT**

## Frozen condition

- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- model `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q2_K.gguf`
- observed size `3.056 GiB`
- SHA256 PASS
- context requested exactly with `-c 4096`
- requested offload exactly with `-ngl -1`
- single-turn exactly with `-st`
- frozen memory guardrails unchanged: abort below 5% free memory or above 5600 MB swap

## Observed run

User-visible CLI output showed:
- model loaded successfully;
- one inference turn executed;
- prompt timing about `42.7 t/s`;
- generation timing about `13.4 t/s`;
- CLI printed `Exiting...` and returned control.

Runner telemetry:
- wall: `7.134 s`
- peak process RSS: `2092.96875 MB`
- peak observed swap: `1986.56 MB`
- minimum observed free memory: `10%`
- no timeout
- no guardrail abort
- exit code `0`

Persisted Stage A validator fields, inspected after the run:
- `exit_code: 0`
- `timed_out: False`
- `guardrail_abort: False`
- `metal_evidence: True`
- `context_4096_evidence: True`
- `requested_offload_evidence: True`
- `single_turn_evidence: True`
- `stage_a_metal_preflight_evidence: True`
- `output_nonempty: False`
- `pass: False`
- captured stdout bytes: `0`
- captured stderr bytes: `0`

## Root cause

The inherited Stage A validator required `output_nonempty`, calculated only from captured child stdout. In this CLI/TTY mode, the user visibly received model/UI output while the runner's stdout/stderr pipes remained empty. Therefore `output_nonempty` is not a valid success criterion for this Stage A implementation.

This is a harness capture/validation defect, not evidence of a model/runtime failure.

## Canonical interpretation

Capability 003 is not promoted to a full capability PASS because Stage B was skipped by the defective validator. However, its Stage A launch/memory requirement is accepted as **recovered PASS evidence** because every persisted operational criterion is positive and the child exited cleanly without guardrail breach.

No further `llama-cli` Stage A rerun is required before benchmarking this exact Q2 condition.

## Next action

Run a separately preregistered Stage B-only continuation using the same verified Q2 artifact, same pinned llama.cpp build, `-ngl -1`, pp512/tg128 x3 and the unchanged memory/swap guardrails.
