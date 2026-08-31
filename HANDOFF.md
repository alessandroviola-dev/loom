# LOOM — Active Handoff

Last updated: 2026-08-31
Status: LOOM final product GO/persisted; **UOPT-001 UNLOCKED speed optimization authorized and active**.
Repository: `Ilcoach/loom`
Branch: `research/unlocked-speed-001`
Pi context: `/AGENTS.md` v3.91.
Active contract: `research/integration/loom-unlocked-speed-optimization-001.md`.

## Finished product baseline

Final product persistence commit:
`98949e77863c93a7d9dba266204a911ab85db09c`.

Operator UX:

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Normal endpoint:
`127.0.0.1:18080` loopback only.

### FAST / default

Label:
`loom-local/loom-deep-30b-s32`

Model:
`models/loom-deep-30b-fast.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Historical S32 matched decode: `5.596 tok/s`; WP4 operational snapshot: `6.209 tok/s`.

### UNLOCKED / optimization baseline

Label:
`loom-local/loom-deep-30b-unlocked`

Model:
`models/loom-deep-30b-unlocked.gguf`

SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

WP4 operational baseline:
- decode `2.963 tok/s`;
- prefill `1.673 tok/s`;
- RSS `4.13->4.16 GiB`;
- swap `1667->1708 MiB`.

Frozen behavior/capability baseline:
- explicit refusal `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`.

Final runtime flags include:
`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`.

WP2 Caveman + Cavemem remains required for final integration and has independent `LOOM_CONTEXT_INTELLIGENCE=0` rollback.

## Current macro — UOPT-001

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_001`

Objective:
maximize UNLOCKED throughput on Apple M1 8 GiB while preserving the finished product and frozen behavior/capability gates.

Primary target:
**>= 5.0 tok/s matched fresh decode median**.

Stretch target:
exceed FAST historical `5.596 tok/s` if feasible.

Optimization order:
1. current exact-model runtime frontier (slots/residency/mmap/placement/batch and relevant Metal/thread knobs);
2. newer evidence-backed MoE residency/paging runtimes, including audit of recent bounded-residency approaches;
3. if runtime alone is insufficient, a small exact-lineage quantization frontier of the validated Huihui derivative;
4. combine only independently validated winners.

Do not trade away `0/6`, `8/8`, `0/6` to gain speed.

Evidence root:
`results-local/unlocked-speed-uopt-001/<timestamp>/`.

Pi does not commit/push during execution. Return only at UOPT completion or a genuine user-action blocker.
