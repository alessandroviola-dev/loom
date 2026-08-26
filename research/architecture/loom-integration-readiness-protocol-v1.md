# LOOM Integration Readiness Protocol v1

Date: 2026-08-26
Status: ACTIVE

## Purpose

Prevent expensive integration attempts from discovering artifact/runtime incompatibilities that could have been rejected mechanically before coding or model execution.

This protocol applies before any new backend, cache, layout, quantization path, speculative path, or runtime artifact is integrated into the canonical LOOM execution path.

## 1. Producer artifact contract

Every produced artifact must declare machine-readable metadata for:
- artifact type and format version;
- source model/revision;
- scope: full-model, full-routed-bank, workload-scoped, trace-scoped, position-scoped, etc.;
- coverage universe and covered identities;
- tensor/byte layout, dtype and quantization semantics;
- mapping key/ABI (for MoE: layer + expert identity);
- payload sizes/offsets/ranges;
- integrity hashes/provenance root;
- whether fallback is required for uncovered accesses;
- construction script/version.

Scope must never be inferred from file name or prior experiment context.

## 2. Consumer runtime contract

Before integration coding, freeze the consumer requirements:
- exact canonical workload ID;
- phases required: prefill/warmup/decode/etc.;
- positions/tokens required;
- required identities/access sequence when retained traces make them knowable;
- expected mapping ABI;
- exactness oracle;
- fallback policy;
- memory/cache invariants;
- benchmark and safety requirements.

## 3. Compile-time compatibility gate — mandatory

No integration coding and no model forward until an offline mechanical checker proves:

`consumer_required_coverage ⊆ provider_available_coverage`

and validates:
- format/version compatibility;
- source model/revision identity;
- ABI/key compatibility;
- sizes/offsets/ranges consistency;
- expected dtype/quantization semantics;
- no required fallback when the experiment forbids fallback;
- integrity metadata availability.

The checker must emit a compact PASS/FAIL JSON with exact missing identities/reasons.

FAIL here is an architecture/artifact-readiness result; do not spend tokens implementing an adapter that cannot work.

## 4. Static adapter dry-run — mandatory

After compile-time compatibility PASS, but before model forward:
- instantiate the adapter in isolation;
- replay the retained/frozen access sequence using metadata or bounded payload checks;
- resolve every requested access to exactly one provider entry;
- verify expected byte/tensor size, mapping identity and hash provenance;
- verify zero hidden SOURCE fallback;
- verify no persistent cache is introduced unless explicitly part of treatment.

Any unresolved access => STOP before model execution.

## 5. Artifact class separation

Benchmark artifacts and runtime artifacts are distinct classes.

A trace/position-scoped pack may validate a storage mechanism or physical-I/O hypothesis but must not be promoted implicitly to a general runtime backend.

For a general expert-major runtime backend, preferred acceptance artifact is a **full routed-bank pack** covering all `48 × 128 = 6144` expert identities, unless a deliberately workload-scoped runtime is the stated product.

## 6. Integration coding gate

Only after Sections 3–4 PASS may Pi write an isolated adapter.

The adapter must define an explicit backend interface. For external MoE expert storage the conceptual contract is:

`resolve_expert(layer_id, expert_id) -> exact expert payload/tensor`

SOURCE and treatment backends must implement the same observable semantics. Routing, expert math, dtypes, quantization, KV, scheduling and output computation are not allowed to change unless separately preregistered.

## 7. Model execution gate

Only after static compatibility and adapter dry-run PASS may any model forward occur.

Execution order:
1. deterministic exactness;
2. safety/memory;
3. performance.

A failure at an earlier gate prevents later expensive stages.

## 8. Token / investigation economy

Pi should spend reasoning tokens on unresolved scientific questions, not discoverable metadata facts.

Before coding:
- read `AGENTS.md` plus only explicitly relevant manifests/scripts/results;
- prefer `rg`, JSON/Python validators and manifest comparison over broad repository reading;
- do not re-derive settled facts;
- do not recursively inspect unrelated history;
- convert compatibility checks into small deterministic scripts;
- persist and reuse validators/builders after first creation.

A known compatibility FAIL must terminate immediately with a compact reason.

## 9. Build-once reuse

If the needed provider artifact is missing, the next compound funnel may include a deterministic artifact-build stage, but only after:
- source inputs are proven available;
- output size is calculated;
- free disk/safety budget passes;
- format/build script is frozen;
- resumability/checkpointing is available for materially expensive builds;
- final manifest must pass complete coverage and hash/provenance validation before integration continues.

## 10. Required preregistration questions

Every integration funnel must answer before execution:
1. What exact artifact does the consumer require?
2. What exact artifact do we currently have?
3. Does a mechanical compatibility proof already PASS?
4. If not, is the funnel authorized to build the missing artifact, or must it stop?
5. What static dry-run proves every access resolves before model forward?
6. What exactness oracle decides semantic parity?
7. What resource and performance thresholds decide adoption?

If any answer is missing, the funnel is not ready to run.
