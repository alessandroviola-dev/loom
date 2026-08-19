# Stretch 006 — Transform Harness Note

Date: 2026-08-19
Status: **HARNESS TRANSFORM FAILURE / NO SCIENTIFIC RESULT**

## Launch

The first attempted launch of `Stretch 006 — Full 36-Layer Streamed Body Parity` stopped inside the frozen transform wrapper before the transformed Stretch 005 runner was executed.

Observed preflight:
- Stretch 005 source blob: `8bbfff727a0131c48d4ba71edc8de485182b7fbe`
- source provenance: PASS
- failure: `transform invariant failed for experiment labels: expected 2 occurrence(s), found 1`

No MLX child process, transformer block, model weight materialization, resident control, streamed path, parity comparison, or resource experiment was executed.

Therefore this launch is **not** a model/runtime/resource/parity failure and provides no evidence for or against 36-layer streaming.

## Demonstrated harness defect

The wrapper used one global replacement invariant for the experiment label. The label occurs in distinct semantic contexts (`print(...)` and the summary `"experiment"` field), making the combined textual invariant brittle after earlier transforms.

The fix changes only transform bookkeeping:
- replace the console label with its own exact one-occurrence invariant;
- replace the summary experiment label with its own exact one-occurrence invariant.

Scientific design is unchanged:
- exact Stretch 005 source blob remains frozen;
- layer chain remains `0..35`;
- deterministic input unchanged;
- official Qwen3 block/quantization unchanged;
- resident and streamed computation unchanged;
- resident tolerance remains +/-36 MiB;
- per-layer streamed gates unchanged;
- numerical parity formula unchanged;
- host/runtime safety unchanged.

Corrected runner blob:
`ab5d74b37111b7ceae6e5c00a47c10f1e1086ca6`

## Decision

Rerun the same preregistered Stretch 006 experiment with the corrected transform wrapper. Treat the first launch only as a harness preflight defect.