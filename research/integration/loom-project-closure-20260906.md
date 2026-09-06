# LOOM Project Closure — 2026-09-06

Status: **FINAL / CLOSED / ARCHIVED**

## Closure decision

LOOM is concluded by owner decision.

The project demonstrated that a 30B-class local model could be made substantially more usable on an 8 GB Apple Silicon M1 through careful runtime, storage, expert-residency, and sidecar work. However, after the final speed investigations, the retained model still did not provide sufficient practical intelligence/capability for the intended workloads.

The remaining problem is therefore not primarily throughput. Additional speed engineering would optimize a model that still does not satisfy the core capability requirement.

No further LOOM optimization work is authorized.

## Final retained product

UNLOCKED UOPT-003 S40 remains the final stable local profile.

Key matched results:

- decode `7.557 tok/s`
- 1,155-token cold prefill `11.306 tok/s`
- 1,155-token cold TTFT `102.242 s`
- expert hit rate `89.831%`
- frozen refusal `0/6`
- held-out degeneration `0/6`
- benign capability `8/8`

The final product remains loopback-only and recoverable through the documented `scripts/loom-deep` operator interface.

## Research conclusions

1. **Lossless expert-major layout was high leverage.** UOPT-002 materially reduced routed-expert miss I/O while preserving model math.
2. **Residency tuning was high leverage.** UOPT-003 S40 improved both decode and cold TTFT without altering weights.
3. **Lower-bit routed-expert quantization crossed the quality boundary.** UOPT-004 and UOPT-005 reduced footprint but repeatedly failed the frozen functional arithmetic reference.
4. **Selective IQ3 refinement was exhaustively informative at practical granularity.** Layer and tensor frontiers converged to outputs `400` or `414`, never the required `410`; going expert-by-expert would require a new multi-day format/runtime research branch with unproven value.
5. **Storage placement matters critically.** A temporary external archive sidecar made Candidate A appear pathologically slow; moving only the sidecar internal changed decode `0.69 -> 9.63 tok/s` and TTFT `148.277 -> 5.605 s`, isolating external storage as the bottleneck.
6. **Draftless speculative decoding did not engage.** UOPT-006 `ngram-simple` and `ngram-mod` both produced `0 drafted / 0 accepted` tokens and no meaningful speedup.
7. **The final stopping criterion was product capability, not lack of additional optimization ideas.** Further runtime research was intentionally discontinued because it would not address the model's practical intelligence ceiling.

## Git / artifact policy at closure

Git contains durable source, configuration, patches, and research documentation only.

The following remain intentionally outside Git:

- `.loom/`
- `results-local/`
- model GGUFs
- expert sidecars
- temporary candidates
- caches/temp files
- external external archive staging/archive data
- unrelated untracked scripts

## Future reopen

If LOOM is ever reopened, do not automatically continue the speed frontier. First reassess the model target and required practical capability. A stronger base model or substantially different hardware/runtime premise should be considered before further optimization of the current 30B profile.

Until such an explicit reopen, treat the repository as historical/read-only.
