# LOOM — Pi Agent Protocol

Version: 2.2
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is the persistent context for Pi. Do not require long prompts that restate it.

## Role split — local override

Pi owns only local technical execution:
- inspect relevant local code/runtime;
- write the minimum code required by the active work package;
- run tests/benchmarks;
- create local evidence under `results-local/`;
- diagnose and mechanically self-correct inside scope.

ChatGPT owns:
- scientific direction and experiment selection;
- Git/GitHub synchronization;
- `HANDOFF.md`, `ROADMAP.md`, research result documents and project-state administration.

Therefore Pi must NOT run Git operations, edit `HANDOFF.md`/`ROADMAP.md`, open PRs, merge, push, or create project documentation unless the work package explicitly overrides this rule.

## Token-efficiency rules

Use tokens for execution, not narration.

1. Read this file, then only files/evidence explicitly relevant to the work package.
2. Use targeted search (`rg`, exact paths); do not scan the whole repo without need.
3. Do not restate project history or the prompt.
4. Do not create notes, research dumps, changelogs or extra documentation.
5. Do not print full logs; preserve them locally and return only decisive evidence.
6. Do not refactor or change architecture outside the requested variable.
7. Distinguish measured fact, inference, hypothesis and unverified limit.
8. Mechanical failures may be diagnosed/fixed autonomously inside scope; do not broaden the scientific experiment as a rescue.
9. A failed preregistered treatment remains failed; no silent parameter changes.
10. Stop on scientific ambiguity, safety/destructive action, missing required artifact, or a gate that explicitly says STOP.

## Scientific loop

`OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`

Preserve one-factor experiments, deterministic inputs, exactness/parity gates, provenance and explicit failure classifications.

## Stable LOOM target context

Reference machine: Apple M1 / 8 GB unified memory.

Target model:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Canonical anatomy:
- 48 MoE layers; 128 routed experts/layer; top-k 8;
- full stored tensor payload: 16,220,499,968 B;
- resident non-routed backbone: 819,015,680 B;
- external routed bank: 15,401,484,288 B;
- one expert: 2,506,752 B;
- zero-cache expert payload: 962,592,768 B/token;
- BF16 KV: 98,304 B/token.

Proven invariants:
- external serial-expert math is bitwise exact;
- full 48-layer forward/logits are exact;
- only one routed expert needs to be live at a time;
- production-like lifecycle uses `GC_END_ONLY`; never add per-expert `gc.collect()` or per-expert RSS subprocesses to timed paths;
- on-disk expert-major `9 ranges -> 1 contiguous read` is lossless and materially faster when available;
- source-range access remains the general fallback for arbitrary un-packed experts;
- 4-GiB raw `GLOBAL_LRU` cache is `MEMORY_FAIL`: ~80.9% hits were real but swap grew +2.41 GiB and decode slowed. Do not reuse this design unless a future work package explicitly revisits it;
- persistent live-MLX expert cache is not currently promoted;
- full 14.344-GiB expert pack is not automatically authorized.

## DFlash stable context

Exact-target candidate:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`

Static invariant:
- BF16 safetensors 1,362,042,120 B (~1.2685 GiB), 680,813,824 learned weight elements;
- 5 draft layers, H=2048, block=8 / proposals=7;
- exact target taps `[1,12,23,34,45]`, concatenated to 10,240 then fused to 2048;
- static M1/8-GB fit is plausible; current LOOM/MLX requires a custom port.

Target-interface invariant:
- `LOOM_DFLASH_TARGET_INTERFACE_001_PASS`;
- taps are 1-based post-block outputs (`layers[i-1]`);
- prefill `[1,28,2048]`, decode `[1,1,2048]`, float32;
- router/logits/tokens remain bitwise exact;
- MLX peak delta +18,612,224 B; swap delta 0; no expert leak.

Wavefront invariant:
- `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`;
- canonical `q_len=1` attention is sequential per position while seven positions advance layer-by-layer;
- each unique expert is loaded once per layer and reused across assigned positions;
- layer hidden/KV/router/final logits/token decisions are bitwise exact vs sequential teacher forcing;
- B7 uses 1,205 unique `(layer,expert)` instances = 431,519,451 B useful expert bytes/verified position;
- wall 10.8152 s sequential vs 6.5430 s wavefront = 1.653x;
- peak MLX 985,002,536 B; peak RSS 1,003,978,752 B; swap delta 0; no expert leak.

Drafter-port invariant:
- `LOOM_DFLASH_DRAFTER_PORT_001_PASS`;
- all 680,813,824 learned BF16 params mapped = 1,361,627,648 B, 60 learned + 2 mapping tensors, no missing/extra learned weights;
- independent reference is a NumPy translation of publisher source because publisher Torch/Speculators runtime is unavailable locally;
- fusion max abs 1.38e-05; draft-layer max abs 0.0515–0.1442; final-logit max/mean 0.01956 / 0.003045;
- MLX resident 1,362,053,632 B; peak 2,289,441,196 B; swap delta 0.

Drafter-decision-stability invariant:
- `LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001_PASS`;
- 9 frozen real target-tap states from P1/P2/P3 at positions 1/16/32;
- 63/63 mapped proposal decisions matched the then-current independent NumPy translation across 7-step rollouts;
- deterministic rerun PASS; no NaN/Inf;
- 7-proposal wall P50/mean 0.08437 / 0.09067 s;
- MLX resident 1,362,053,640 B; peak 2,305,009,460 B; RSS 1,449,148,416 B; swap delta 0.

Important: that stability result predates the publisher anchor/block mask correction below. It proves MLX/reference agreement for the old semantics, not publisher-contract correctness after the mask repair.

DFlash first E2E invariant:
- `LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`;
- P1/P2/P3 completed, 96 committed output tokens, ordinary-greedy token parity PASS;
- target KV/router/logits bitwise PASS; deterministic rerun PASS; zero routed-expert leak;
- acceptance 0/96 cycles: mean/P50 0.0, rate 0%;
- verifier calls/output token 1.96875; useful expert bytes/output token 3,098,293,248 B;
- control 0.7735 tok/s vs DFlash 0.1544 tok/s = 0.1996x;
- MLX peak 3,148,206,740 B; RSS 1,259,044,864 B; swap delta +737.43 MiB.

This is a dual failure: zero acceptance is the first blocker; memory pressure is separate. Do not optimize memory while acceptance remains zero.

Acceptance-alignment invariant:
- `LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE`;
- 3 deterministic P1 cycles C=43–45 inspected;
- first concrete semantic mismatch: publisher anchor/block attention mask was absent in `Drafter.propose`;
- publisher contract recovered: base positions `< anchor`, causal same-block synthetic attention, slots 1–7 map via `d2t`, `sample_from_anchor=False`, post-block taps `[1,12,23,34,45]`, no draft-KV carry;
- target correction/bonus logic was already aligned;
- only the drafter mask was mechanically repaired;
- repaired short probe still accepted 0/21 proposals with prefixes `[0,0,0]`;
- no simple k-1/k/k+1 proposal shift exists.

Masked-reference invariant:
- `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`;
- independent publisher-semantics reference implements the corrected anchor/block mask separately from the MLX path;
- explicit independent 8×13 anchor/block mask assertion PASS;
- same 9 frozen P1/P2/P3 states at positions 1/16/32;
- 63/63 mapped proposal-token decisions match across full seven-step autoregressive rollouts; first mismatch none;
- deterministic rerun PASS; no NaN/Inf;
- final-logit max-abs distribution max/mean 0.0166407 / 0.0109135;
- final-logit mean-abs distribution max/mean 0.00175031 / 0.00120281;
- top1/top2 margin mean MLX/reference 0.55770 / 0.55726; max absolute margin error 0.00708771;
- frozen-target accepted-prefix observation is `[0,0,0,0,0,0,0,0,0]` for both MLX and independent reference.

Interpretation:
- the corrected MLX drafter is now validated against an independent publisher-semantics reference;
- the missing mask is no longer an unresolved implementation explanation for the observed zero frozen-prefix acceptance;
- target/drafter compatibility is now the next scientific question;
- the local `Qwen3-30B-A3B-MLX-4bit` target is a hypothesis to audit, not an established cause;
- do not attribute incompatibility specifically to 4-bit quantization without isolating that variable.

Target-compatibility audit precondition invariant:
- `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` attempted Gate A and classified `ENGINE_OR_DATA_BLOCKED`;
- target replay and compatibility scoring were not run;
- immutable frozen continuation decisions available: 45/63;
- `P1_t32`, `P2_t32`, `P3_t32` each lack six of the seven required continuation tokens;
- drafter/target parity, ranks, top-k, logprobs, margins and accepted prefixes are therefore not measurable yet;
- evidence: `results-local/research/dflash-target-compatibility-audit-001/20260824T144106Z/` (`precondition.json`, `provenance.json`);
- do not fabricate the missing historical decisions by running the same current replay/scoring path; that would make Gate A circular.

Next checkpoint:
`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001`

First search only relevant pre-existing local evidence for an independently captured/provenanced seven-token continuation corpus. If none exists, explicitly create a NEW rebaselined 63-token target-continuation reference with an independent already-validated target oracle path, not the later compatibility scorer/replay path. Preserve the same nine frozen prefixes. The rebaseline must reproduce all 45 already-available historical frozen decisions exactly (`45/45`) before the 18 missing decisions can be accepted as new reference data. Require deterministic rerun, finite outputs, exact provenance and a content hash. Newly generated continuation tokens must be labeled as rebaselined reference data, not historical frozen observations.

Only after that freeze passes may `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` be rerun.

Do not rerun full E2E or optimize memory/performance yet.

For volatile project state, read `HANDOFF.md` only when explicitly needed. Do not edit it.

## Work-package contract

A normal prompt may now be only:

```text
LOOM WP <id>
Goal: ...
Inputs: exact files/evidence to inspect
Change: single allowed variable / code scope
Gates: correctness + performance/memory criteria
Evidence: output directory/files
Return: requested key metrics only
STOP
```

Everything not changed by the work package inherits this file.

## Default evidence rules

- Original model files are immutable.
- Experimental scripts may be local under `scripts/`.
- Raw benchmark evidence stays local under `results-local/<area>/<checkpoint>/<UTC-RUN-ID>/`.
- Record real UTC run ID and enough provenance to reproduce the test.
- Do not manufacture measurements or infer unmeasured physical I/O.

## Default concise return

Unless the work package requests different fields, return only:

```text
Checkpoint: <id>
Classification: <PASS/CONDITIONAL/FAIL-specific>
Key metrics: <only decisive values>
Parity/tests: <PASS/FAIL>
Memory/safety: <decisive values>
Evidence: <directory>
Files: <created/modified>
Blocker: <only if present>
STOP
```

Local LOOM restrictions prevail where stricter than general agent protocols.
