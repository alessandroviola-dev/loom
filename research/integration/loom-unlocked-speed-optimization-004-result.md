# LOOM_UNLOCKED_SPEED_UOPT_004_NO_GO

Date: 2026-09-03

Branch: `research/unlocked-speed-001`

Classification: **NO_GO**

## Result

UOPT-004 evaluated expert-only `Q2_K` quantization derived from BF16. The expert
footprint decreased by **23.636%** and all frozen gates passed. The candidate did
not meet quality acceptance: functional evaluation was **3/4 (FAIL)** and the
arithmetic result was **414** versus the expected **410**. It is therefore
rejected.

| Check | Result |
| --- | --- |
| Expert representation | BF16 → expert-only `Q2_K` |
| Expert footprint | **-23.636%** |
| Frozen gates | **PASS** |
| Functional | **3/4 — FAIL** |
| Arithmetic | **414 vs expected 410 — FAIL** |
| Decision | **NO_GO** |

Temporary candidate artifacts were removed after the decision. The promoted
UOPT-003 S40 production profile is unchanged.
