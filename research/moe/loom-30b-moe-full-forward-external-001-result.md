# LOOM 30B MoE Full Forward External 001 — Result

Date: 2026-08-24
Classification: `LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL`
Run: `results-local/moe/full-forward-external-001/20260824T073551Z/`

The first complete Qwen3-30B-A3B target forward on the M1 8 GB reference machine traversed embedding, all 48 decoder layers, final norm and LM head while the complete non-expert backbone remained resident and routed experts stayed external.

Correctness was exact: CONTROL and SERIAL_SELECTED_EXPERT both completed 48/48 layers; router IDs and weights were bitwise identical at all layers; hidden states were bitwise identical for 48/48 layers; final hidden state and logits had zero error; logits argmax and top-10 ranking matched exactly.

Capacity represented: 16,220,499,968 B total model payload = 819,015,680 B resident backbone + 15,401,484,288 B externally represented routed bank. Treatment read 962,592,768 B useful expert payload for the one-position F1 forward. Maximum logical routed-expert residency was 2,506,752 B and final routed-expert residency was 0 B. Ownership/release gate passed.

Memory: treatment peak MLX 821,640,984 B; peak RSS 311,197,696 B as reported by the run. Swap increased from 1,096.19 to 1,227.19 MiB (+131 MiB), so the run remains CONDITIONAL on memory-pressure behavior despite completing successfully. CONTROL peak MLX/RSS was 1,140,015,936 / 815,742,976 B.

Timing: F1 full-forward wall time 20.333756 s. Explicit stage totals were attention/shared 0.148352 s, expert reads 1.486196 s, decode/view 0.002486 s, MLX reconstruction 0.160427 s, expert compute 0.340194 s and aggregation 0.043012 s. These explicit categories sum to only about 2.18 s, leaving roughly 18 s of wall time unattributed. Per-layer wall P50/P90/P95/max was 0.420643 / 0.429449 / 0.434578 / 0.446881 s. This unattributed overhead is now the primary immediate runtime blocker and must be localized before generation speed is interpreted.

Real multi-position routing traces already show overlap. F4 had 1,086 unique expert instances over 1,536 naive selections and potential union accounting of 680,583,168 B/position. F8 had 1,547 unique instances over 3,072 selections and 484,743,168 B/position, a 49.64% reduction versus the F1 962,592,768 B baseline. This is real target routing overlap, but it is not yet enough by itself to meet the previously established 58.47% storage-only traffic reduction needed for a 5 tok/s envelope, and no cache/DFlash speedup is inferred from it.

Decision: full-capacity end-to-end external-expert execution is proven. Do not build the full expert-major pack yet. Do not promote autoregressive generation speed from this checkpoint. Next core checkpoint: `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001`, focused on explaining the ~18 s uninstrumented wall-time gap, followed by routing/cache and DFlash work once the baseline runtime cost is understood.
