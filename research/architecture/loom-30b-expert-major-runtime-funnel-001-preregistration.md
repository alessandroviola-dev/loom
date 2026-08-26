# LOOM 30B Expert-Major Runtime Funnel 001 — Preregistration

Date: 2026-08-26
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Decision question

Does replacing only the external expert data-access backend with the proven lossless expert-major layout preserve exact runtime semantics and provide a useful practical end-to-end decode improvement on Apple M1/8GB without material memory/swap regression?

Final outcomes only:
- `EXPERT_MAJOR_RUNTIME_GO`
- `EXPERT_MAJOR_RUNTIME_NO_GO`
- `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`

This is one compound funnel. Internal stages advance automatically without intermediate Git/pull when their frozen gates pass.

## Established prior evidence

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002` = `EXPERT_MAJOR_GO`.

Three causally valid first-touch physical-I/O pairs produced packed/source wall ratios `0.602456`, `0.595950`, `0.581170`; median `0.595950`. All six arms passed physical coverage, exact payload/hash, read-structure, control, memory and swap gates. The raw data-access optimization is therefore established; this funnel tests deployment effect, not physical-I/O causality again.

## Stage 0 — isolated one-factor runtime integration

No model forward until the integration is mechanically validated.

1. Inspect the current exact external serial-expert runtime/harness and the retained expert-major pack/manifest.
2. Select the most recent existing deterministic exact-runtime workload that already supports final-logit capture and decode timing. Do not invent a new model/prompt if an existing canonical workload exists.
3. Create an isolated experimental adapter/workspace under this funnel's `results-local/` evidence directory. Do not edit project documentation, Git state, or the canonical SOURCE baseline path.
4. The only intended treatment factor is expert data-access layout/backend:
   - SOURCE arm uses the existing canonical nine-range expert reads;
   - PACKED arm maps the identical routed expert identity to the existing expert-major payload and returns identical expert bytes/tensors.
5. Routing, expert math, quantization, tensor dtypes, KV behavior, non-routed weights, tokenizer/input tokens, scheduling, synchronization semantics and output computation must remain unchanged.
6. Preserve the invariant that no persistent expert cache is introduced and one routed expert is logically live at a time.
7. Validate manifest coverage/mapping for every expert identity required by the selected canonical runtime workload before any model forward.

If a one-factor isolated integration cannot be established from the current runtime and retained pack: `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` and STOP.

## Stage 1 — deterministic exactness gate

Use the same frozen input/token sequence for SOURCE and PACKED. No network.

Run the minimum bounded exactness sequence that exercises the full 48-layer external-MoE decode path at three consecutive decode positions. Forced/frozen input tokens must be identical between arms; do not allow autoregressive divergence to alter later inputs.

Require all of:
- routed expert IDs/order identical at every layer/position;
- expert payload byte/hash mapping PASS;
- raw final-logit float32 SHA identical for SOURCE vs PACKED at all three checked decode positions;
- no exception/fallback to SOURCE inside PACKED arm;
- no persistent expert-cache introduction;
- no unsafe memory-pressure event.

If evidence is complete and any exactness requirement fails: `EXPERT_MAJOR_RUNTIME_NO_GO` and STOP.
If exactness cannot be validly measured because of a new environment/instrumentation ambiguity: `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` and STOP.

## Stage 2 — practical end-to-end decode performance/safety

This stage intentionally measures practical runtime behavior, not forced physical coldness. Do not use purge, reboot, RAM-fill, cache-thrash, swap eviction, `F_GLOBAL_NOCACHE`, or other artificial cache-state manipulation.

Use exactly three matched process-level pairs. Frozen arm order:
- Pair 1 `SOURCE -> PACKED`
- Pair 2 `PACKED -> SOURCE`
- Pair 3 `SOURCE -> PACKED`

For every arm:
1. start from a fresh runtime process;
2. use the exact same frozen model/input/token sequence and runtime settings;
3. perform one unmeasured decode warmup token after prefill;
4. measure exactly three consecutive decode tokens after warmup;
5. record per-token wall time and aggregate measured decode wall;
6. record peak RSS, memory-pressure state and swap before/after/delta;
7. record routed expert IDs/order and detect any backend fallback/error;
8. close the process before the next arm.

No model download/network access is allowed. Reuse only local retained model/artifacts.

### Performance validity gates

Every arm must have:
- exactly three measured decode tokens;
- identical frozen input/token sequence and runtime settings within pair;
- complete timing evidence;
- no backend fallback;
- no exception;
- no unsafe memory-pressure event;
- routed expert identity/order consistent with the frozen workload.

Any ambiguity invalidating the comparison => `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`.

### Safety gates

Across the three matched pairs:
- PACKED must not introduce a persistent expert cache;
- median PACKED peak RSS must be no more than `128 MiB` above median SOURCE peak RSS;
- PACKED swap delta in any matched pair must be no more than `64 MiB` above the matched SOURCE swap delta;
- no unsafe memory-pressure event in any PACKED arm.

A valid safety regression => `EXPERT_MAJOR_RUNTIME_NO_GO`.

## Frozen runtime performance decision

For each pair compute:

`runtime_ratio = packed_measured_decode_wall / source_measured_decode_wall`

Primary decision statistic: median of the three runtime ratios.

`EXPERT_MAJOR_RUNTIME_GO` only if:
- Stage 1 exactness PASS;
- all Stage 2 validity/safety gates PASS;
- median runtime ratio `<=0.90` (at least 10% practical measured decode-wall improvement);
- no persistent expert cache or fallback.

`EXPERT_MAJOR_RUNTIME_NO_GO` if evidence is valid but:
- exactness fails; or
- a safety gate fails; or
- median runtime ratio `>0.90`.

`EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` only for a genuine integration/environment/instrumentation ambiguity that prevents a valid decision.

No threshold relaxation after results begin.

## Hard bounds

- no network/model download;
- no DFlash;
- no new cache/eviction mechanism;
- no canonical project docs/Git edits by Pi;
- isolated experimental integration only;
- exactly three exactness decode positions maximum;
- exactly 3 matched performance pairs;
- one warmup + three measured decode tokens per performance arm;
- no rescue repetitions;
- total runtime execution wall cap `360 s`; if exceeded safely persist evidence and classify `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`;
- stop immediately on unsafe memory pressure.

## Evidence

`results-local/research/30b-expert-major-runtime-funnel-001/<UTC>/`

If final outcome is `EXPERT_MAJOR_RUNTIME_GO`, the expert-major backend is accepted as the selected runtime direction and may then be productionized/canonicalized in the repository with the funnel evidence as acceptance support.
