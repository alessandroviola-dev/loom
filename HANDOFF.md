# LOOM — Active Handoff

Last updated: 2026-08-31
Status: LOOM final product GO/persisted; UOPT-001 PARTIAL_GO/persisted; **UOPT-002 architectural UNLOCKED speed optimization authorized and active**.
Repository: `Ilcoach/loom`
Branch: `research/unlocked-speed-001`
Pi context: `/AGENTS.md` v3.93.
Active contract: `research/integration/loom-unlocked-speed-optimization-002.md`.

## Finished product baseline

Final product persistence commit:
`98949e77863c93a7d9dba266204a911ab85db09c`.

Operator UX:
```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Loopback endpoint: `127.0.0.1:18080`.

### FAST / default
- model `models/loom-deep-30b-fast.gguf`;
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- historical matched decode `5.596 tok/s`;
- FAST `-ub 1`.

### UNLOCKED
- model `models/loom-deep-30b-unlocked.gguf`;
- SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- frozen refusal `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`.

## UOPT-001 — COMPLETE / PARTIAL_GO / PERSISTED

Commit:
`93b5f44733d120a4e9c0f0b1fea6e58309f71ccd`.

Retained change: UNLOCKED `-ub 2`, FAST remains `-ub 1`.

Matched retained metrics:
- decode `2.579 -> 3.161 tok/s`;
- short TTFT `19.525 -> 15.283 s`;
- ~413-token cold TTFT `199.104 -> 184.700 s`;
- ~1,150-token cold TTFT `433.558 -> 393.983 s`;
- ~1,150-token warm TTFT `0.195 -> 0.190 s`.

All frozen behavior/capability/integration gates passed. Current-runtime tuning was exhausted without reaching 5 tok/s. Remaining bottleneck is expert paging / cold prefill.

Known-good UNLOCKED rollback baseline: persisted UOPT-001 S32/CPU-MoE/no-mmap/ub2.

## UOPT-002 — ACTIVE

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_002`

Objective:
attack expert paging and cold-prefill architecture rather than continue broad flag tuning.

Full-GO targets:
- matched fresh decode >= `5.0 tok/s`;
- ~1,150-token cold TTFT <= `184 s`;
- stretch cold TTFT < `120 s`.

Frozen gates:
- `0/6` refusal;
- `0/6` held-out degeneration;
- `8/8` benign;
- routed top-k semantics unchanged;
- API/WebUI/Pi+WP2/cache/loopback;
- exact provenance;
- FAST + UOPT-001 rollback.

Research order:
1. expert-granular I/O/paging attribution;
2. bounded expert residency runtime reproduction;
3. router-driven explicit/merged prefetch;
4. GGUF page-amplification mitigation without destructive production-model changes;
5. streamed expert cache/compute overlap;
6. exact-output speculative decode only if paging work improves TTFT but decode remains below target.

UOPT-001 observed ~5 GiB free disk. Re-measure at execution. Do not create a second full 13.29 GB GGUF if space is insufficient and never mutate the hard-linked stable models.

Evidence:
`results-local/unlocked-speed-uopt-002/<timestamp>/`.

Pi does not commit/push during execution and returns only at macro completion or genuine user-action blocker.
