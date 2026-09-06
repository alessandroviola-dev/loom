# LOOM — Final Handoff

Last updated: 2026-09-06
Status: **PROJECT CLOSED / ARCHIVED**
Repository: `Ilcoach/loom`
Final research branch: `research/unlocked-speed-001`

## Final decision

LOOM is concluded. The project succeeded at making the local 30B UNLOCKED model materially faster and operationally usable, but the model's practical intelligence/capability remained below what was required for the intended workloads. Further speed optimization was therefore stopped by product decision, not by an unresolved runtime defect.

There is no active next action.

## Final retained product

The retained local product is **UOPT-003 S40 UNLOCKED**.

Operator UX:

```text
scripts/loom-deep use unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable loopback endpoint:

```text
http://127.0.0.1:18080/
```

Final retained artifacts:

- source GGUF `models/loom-deep-30b-unlocked.gguf`
- source SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- expert-major sidecar `models/unlocked-expert-major-v1.bin`
- sidecar SHA256 `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- patched runtime `.loom/runtime/loom-uopt002/llama-server`
- runtime SHA256 `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- default profile: S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`
- managed rollback: `unlocked-s32`

Matched UOPT-003 result:

- decode `6.660 -> 7.557 tok/s` (+13.46%)
- 1,155-token cold prefill `7.147 -> 11.306 tok/s`
- 1,155-token cold TTFT `161.676 -> 102.242 s` (-36.76%)
- expert hit rate `81.745% -> 89.831%`
- misses `90,229 -> 50,260`
- frozen gates remained refusal `0/6`, degeneration `0/6`, benign `8/8`

## Optimization closure

### UOPT-001 — PARTIAL_GO
Retained low-risk runtime tuning and rollback baseline.

### UOPT-002 — GO
Lossless expert-major sidecar + patched runtime reduced expert-miss I/O and materially improved decode/cold TTFT.

### UOPT-003 — GO
S40 residency was the stable winner and remains the final product profile.

### UOPT-004 — NO_GO
Expert-only Q2_K reduced expert footprint by `23.636%` but failed functional arithmetic quality (`414` vs `410`).

### UOPT-005 — NO_GO
Global and selective IQ3_XXS exploration exhausted layer and tensor frontiers without recovering the required arithmetic reference. Candidate outputs converged to `400` or `414`, never `410`. Expert-by-expert search was rejected as a new multi-day format/runtime project with unproven value.

### UOPT-006 — NO_GO
Draftless speculative decoding was tested on production S40:

- `ngram-simple`: greedy parity PASS, decode `+0.52%`, drafted `0`, accepted `0`
- `ngram-mod`: greedy parity PASS, decode `-0.45%`, drafted `0`, accepted `0`
- acceptance N/A (`0/0`)
- RSS ~`4.676 GiB`
- no meaningful swap growth or stability issue

No UOPT-006 phase 2 was justified.

## Storage / archive

The external external archive volume is archive/staging only and is not required for normal inference. FAST remains externally archived and unavailable as a local profile.

Local experiment evidence under `results-local/`, `.loom/` runtimes, model files, caches, and external-drive artifacts remain intentionally outside Git.

## Closure rule

Do not resume LOOM optimization, create a new UOPT work package, mutate the retained S40 production profile, or perform new model downloads/builds unless the owner explicitly reopens the project.

If LOOM is reopened in the future, start from this document and the final closure record in `research/integration/loom-project-closure-20260906.md` rather than from stale historical roadmap items.
