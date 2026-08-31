# LOOM UNLOCKED Speed Optimization — UOPT-001 Result

Date: 2026-08-31  
Checkpoint: `LOOM_UNLOCKED_SPEED_UOPT_001`  
Classification: **`LOOM_UNLOCKED_SPEED_UOPT_001_PARTIAL_GO`**

## Retained product change

UNLOCKED alone uses physical microbatch `-ub 2`; FAST remains at its frozen `-ub 1` baseline. The model, runtime, endpoint, cache, loopback binding, slot count, and all other serving flags are unchanged.

Evidence: `results-local/unlocked-speed-uopt-001/20260831T131553Z/`.

## Matched UOPT results

The exact UNLOCKED GGUF (`734f...5744b7c`) and pinned server (`58ae...3ca08506`) were retained.

| Metric | S32 / ub1 UOPT baseline | S32 / ub2 retained candidate |
| --- | ---: | ---: |
| Fresh short decode median | 2.579 tok/s | 3.161 tok/s (product repeat; 3.046 in independent experimental repeat) |
| Short TTFT median | 19.525 s | 15.283 s |
| Short prompt median | 1.706 tok/s | 2.199 tok/s |
| ~413-token medium cold TTFT | 199.104 s | 184.700 s |
| ~1,150-token cold TTFT | 433.558 s | 393.983 s |
| ~1,150-token warm TTFT | 0.195 s | 0.190 s |

The long-cold comparison is conservative for the candidate because it reused the unavoidable common 18-token chat/system prefix; it still evaluated 1,133 prompt tokens versus the baseline's 1,150. Candidate prompt evaluation was 2.877 tok/s versus 2.654 tok/s. Cache reuse remained intact (`1,150/1` cached/evaluated on candidate reuse).

This is a reproducible interactive improvement: local matched decode increased about 22.6%, medium cold TTFT decreased about 7.2%, and the long cold path decreased about 9.1%, with no short or warm TTFT regression. It does **not** reach the co-primary >=5.0 tok/s target and the retained ~394 s long cold path remains far above FAST's historical ~184 s, so full GO is not justified.

## Frozen acceptance

With the product candidate:

- held-out explicit refusals: **0/6**;
- held-out degeneration: **0/6**;
- benign capability: **8/8**;
- API, WebUI, loopback-only listener and cache: PASS;
- real Pi + WP2 returned exactly `alpha beta gamma delta` and created a new packing record (`11 -> 12`);
- `scripts/test_loom_context.py`: PASS;
- FAST -> UNLOCKED and final UNLOCKED -> FAST lifecycle rollback: PASS.

The long Pi+WP2 request is expected to be slow because Pi/WP2 supplies a ~2.5k-token provider request on this host; it completed correctly under the extended local allowance. No cloud inference or public listener was used.

## Rejected frontier branches

- S24 reduced fresh decode to 2.321 tok/s; S40 left only 4% free-memory signal and used 2315.81 MiB swap before serving.
- `-ub 128` deterministically aborted because a microbatch required more than 32 unique experts; ub4 regressed warm-cache TTFT. ub2 was the only retained microbatch winner.
- `--mmap` had ~83.4 s readiness and produced Metal GPU command-buffer timeouts; it is rejected.
- no-CPU-MoE (2.386 tok/s), 8 CPU threads (2.674 tok/s), and forced Flash Attention did not improve the matched product result.
- The current fork master is `fda8528aa8c1d8ecb2a5cd2b6e85c43ef5425b6b`; audit found it has no `llama-moe-offloader` source, hence it is not a compatible bounded-residency replacement for this 8 GiB GGUF path.
- No exact-lineage alternate GGUF exists locally. Only ~5 GiB local storage was free, while a new eligible quantification requires retaining the 13.29 GB source plus a multi-GB output. No safe non-destructive quantization candidate could be constructed.

## Disposition

Retain the UB2 UNLOCKED setting as the best validated local profile, retain FAST as default, and leave the host at FAST + WP2. The remaining bottleneck is bounded expert paging/cold prefill on the 8 GiB M1; no tested safe current-runtime or compatible-new-runtime route approached 5 tok/s or FAST-like long-cold TTFT.
