# CAPABILITY 000J — Full-sequence targeted reclamation result

Date: 2026-08-21
Classification: `CAPABILITY_000J_INFRASTRUCTURE_INCOMPLETE`

CONTROL: R1 completed; R2 hit the hard 4% free-memory gate; peak MLX 4194.45 MiB.

TREATMENT: after R1, detaching only the stale completed-response `prompt_cache` reduced active MLX from 3886.20 to 3634.20 MiB, recovering 252.00 MiB. Allocator cache rose from 231.07 to 483.07 MiB. R2 still reached the 4% free-memory gate. Observed treatment peak through the abort boundary was 4069.62 MiB; allocator cache reached about 712.95 MiB.

R1 response/tool behavior remained equivalent. No global cleanup was used.

Interpretation: the 000I targeted lifecycle correction remains valid and lowers live/peak MLX pressure, but it does not yet improve the system-free gate because released storage moves substantially into allocator cache. R2 did not complete and full actual-M/prefill/generation timing instrumentation was unavailable, so this run does not promote the treatment to the integrated bridge.

Next justified factor: isolate MLX allocator-cache reclamation after the proven request-local detach, while keeping model, context, BF16 KV, prompt/tool surface and prefill step 512 unchanged.