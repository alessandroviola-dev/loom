# LOOM_UNLOCKED_SPEED_UOPT_005_CANDIDATE_A_NO_GO

Date: 2026-09-03

Branch: `research/unlocked-speed-001`

Classification: **Candidate A NO_GO; Candidate B next**

## Completed preparation

- BF16 source verification: **13/13** verified.
- HF→BF16 GGUF conversion: validated.
- Imatrix: completed.
- Candidate A: expert `IQ3_XXS` constructed.

## Storage isolation finding

Candidate A's initial performance pathology was caused by its sidecar being on
external archive. Storage isolation removed that bottleneck:

| Metric | external archive sidecar | Isolated storage |
| --- | ---: | ---: |
| Decode | 0.69 tok/s | **9.63 tok/s** |
| Prefill | 0.24 tok/s | **6.31 tok/s** |
| TTFT | 148.277 s | **5.605 s** |

external archive is therefore identified as the bottleneck, not a candidate-model
performance result.

## Candidate A quality and decision

| Gate | Result |
| --- | --- |
| Explicit refusal | **0/6 — PASS** |
| Held-out degeneration | **0/6 — PASS** |
| Benign capability | **8/8 — PASS** |
| Functional | **3/4 — FAIL** |
| Arithmetic | **400 vs expected 410 — FAIL** |
| Decision | **NO_GO** |

Candidate A is rejected for quality. The next bounded step is Candidate B:
mixed Q3/IQ3 expert quantization selected by layer sensitivity. The promoted
UOPT-003 S40 production profile remains unchanged.
