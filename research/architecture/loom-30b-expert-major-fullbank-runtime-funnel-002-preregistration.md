# LOOM 30B Expert-Major Full-Bank Runtime Funnel 002 — Preregistration

Date: 2026-08-26
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed
Protocol: `research/architecture/loom-integration-readiness-protocol-v1.md`

## Decision question

Can LOOM build/reuse a runtime-complete lossless expert-major routed bank, prove compile-time compatibility before integration, preserve exact runtime semantics, and deliver >=10% practical decode-wall improvement on Apple M1/8GB without material memory/swap regression?

Final outcomes only:
- `EXPERT_MAJOR_RUNTIME_GO`
- `EXPERT_MAJOR_RUNTIME_NO_GO`
- `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`

This is one compound funnel. Internal stages advance automatically only through frozen gates. No intermediate human/Git synchronization.

## Established facts

- Raw expert-major physical-I/O is accepted: `EXPERT_MAJOR_GO`, median packed/source access-wall ratio `0.595950`.
- Runtime Funnel 001 was INCONCLUSIVE before model forward because the retained 384-expert pack was position/trace-scoped and did not cover the selected runtime workload.
- The routed bank contains `48 × 128 = 6144` expert identities.
- Q4 expert payload size is `2,506,752 B`.
- Full routed-bank payload is exactly `15,401,484,288 B`.
- The 384-expert benchmark pack is not eligible as a runtime-complete provider artifact.

## Stage 0 — compile-time provider/consumer contract

No integration coding and no model forward.

1. Select the same deterministic canonical workload chosen by Runtime Funnel 001 unless it is mechanically unavailable:
   `LOOM_30B_MOE_REAL_RAW_CACHE_001` SOURCE control, P1 canonical sequence (`20260824T092553Z`).
2. Read only relevant source model metadata, existing expert-major pack/builder/manifest, canonical workload trace, and runtime access interface.
3. Emit machine-readable consumer requirements and provider capability JSON.
4. Verify source model exposes all `6144/6144` expert identities with the validated nine-component expert representation and expected `2,506,752 B` payload per expert.
5. Verify exact source model/revision, quantization/dtype semantics and mapping ABI.
6. Verify free disk before any build. Required free space: at least `20 GiB` on the destination volume.
7. Reuse an already complete compatible full-bank pack only if its manifest proves all `6144/6144` identities, source provenance and format compatibility. The existing 384-expert pack cannot satisfy this gate.

If source coverage, provenance, destination safety, or deterministic buildability cannot be proven: `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` and STOP.

## Stage 1 — build/reuse runtime-complete full expert-major bank

If a valid full-bank artifact is absent, build exactly one.

Frozen target:
- all `6144` experts;
- deterministic key order `(layer_id ascending, expert_id ascending)`;
- each expert payload contiguous;
- exact payload `2,506,752 B/expert`;
- total payload `15,401,484,288 B`;
- no compression or transformation beyond the already validated lossless expert-major representation;
- manifest entry for every expert: layer, expert, offset, size, source provenance/hash, packed hash;
- no persistent RAM cache.

Use/reuse the already validated packing semantics. Builder must be resumable/checkpointed at expert granularity so interruption does not require starting from zero.

After build:
- require file size/arithmetic consistency;
- require exactly `6144/6144` unique mapping entries;
- require zero missing/duplicate keys;
- verify every packed expert against its source payload hash/provenance; full verification is allowed because this is a one-time artifact acceptance stage;
- persist a root manifest/hash.

Any valid content/provenance mismatch => `EXPERT_MAJOR_RUNTIME_NO_GO` and STOP.
A new filesystem/environment ambiguity preventing safe completion => `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` and STOP.

## Stage 2 — mandatory static compatibility + adapter dry-run

Still no model forward.

1. Prove mechanically:
   `consumer_required_coverage ⊆ fullbank_available_coverage`.
2. Replay the complete retained access sequence needed by the selected workload through the candidate mapping without running expert math.
3. Every requested `(layer_id, expert_id)` must resolve exactly once to the full-bank manifest with expected size/hash/provenance.
4. No SOURCE fallback allowed.
5. Build the isolated treatment adapter only after the compatibility proof passes.
6. SOURCE and PACKED must implement the same observable expert-load interface. Only storage layout/backend changes.
7. Preserve routing, expert math, quantization, dtype, KV, non-routed weights, tokenizer/input, scheduling/synchronization and output computation.
8. No persistent expert cache; one routed expert logically live at a time.

Any missing/ambiguous access => `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` and STOP before model forward.

## Stage 3 — deterministic exactness

Use the same forced/frozen token sequence in SOURCE and PACKED.

Check exactly 3 consecutive decode positions through all 48 MoE layers.
Require at all positions:
- identical routed expert IDs/order;
- exact provider mapping/hash PASS;
- identical raw final-logit float32 SHA SOURCE vs PACKED;
- no fallback;
- no persistent expert cache;
- no unsafe memory pressure.

Valid semantic mismatch => `EXPERT_MAJOR_RUNTIME_NO_GO` and STOP.
Genuine instrumentation/environment ambiguity => `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` and STOP.

## Stage 4 — practical end-to-end runtime A/B

No artificial cold-cache controls.
Exactly 3 fresh-process matched pairs:
- Pair 1 `SOURCE -> PACKED`
- Pair 2 `PACKED -> SOURCE`
- Pair 3 `SOURCE -> PACKED`

Per arm:
- same local model, frozen input/token sequence and settings;
- prefill;
- one unmeasured decode warmup token;
- exactly 3 measured consecutive decode tokens;
- record per-token and aggregate wall, peak RSS, memory pressure, swap before/after/delta, routing and backend status;
- close process before next arm.

Validity:
- exactly 3 measured tokens/arm;
- complete timing;
- no fallback/exception;
- identical frozen sequence/settings;
- routed expert order consistent;
- no unsafe memory pressure.

Safety:
- no persistent expert cache;
- median PACKED peak RSS <= median SOURCE peak RSS + `128 MiB`;
- PACKED swap delta <= matched SOURCE swap delta + `64 MiB` in every pair;
- no unsafe memory-pressure event.

Decision statistic:
`median(packed_measured_decode_wall / source_measured_decode_wall)` across 3 pairs.

`EXPERT_MAJOR_RUNTIME_GO` iff:
- full-bank artifact acceptance PASS;
- static compatibility/dry-run PASS;
- exactness PASS;
- all runtime validity/safety PASS;
- median runtime ratio `<=0.90`;
- no fallback or persistent expert cache.

`EXPERT_MAJOR_RUNTIME_NO_GO` for valid artifact/exactness/safety failure or valid median ratio `>0.90`.

`EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` only for a genuine environment/instrumentation/resource ambiguity preventing a valid decision.

## Token/execution economy

Pi must use mechanical scripts for metadata/coverage/hash checks. Avoid broad repository exploration and re-derivation of settled evidence. Read `AGENTS.md`, this preregistration, Integration Readiness Protocol v1, and only directly relevant manifests/scripts/results.

No network/model download, no DFlash, no eviction experiments, no rescue repetitions, no project docs/Git edits.

Artifact build is one-time and resumable. Runtime model execution remains bounded to 3 exactness positions and 3 performance pairs. Stop immediately on unsafe memory pressure.

Evidence:
`results-local/research/30b-expert-major-fullbank-runtime-funnel-002/<UTC>/`
