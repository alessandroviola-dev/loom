# LOOM — Pi Agent Protocol

Version: 3.26
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git/push/PR/edit project docs unless explicitly authorized.

After every **significant scientific checkpoint**, ChatGPT updates canonical project state on GitHub and the user pulls before the next Pi WP. Significant checkpoints include classification change, accepted/invalid/unresolved experiment, frozen baseline change, branch-direction change, or selection of a new next checkpoint.

Rules:
1. one-factor experiments; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. treatment comparison invalid if more than intended factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID or UNRESOLVED evidence;
7. do not advance from stale AGENTS/HANDOFF/ROADMAP;
8. instrumentation required by a gate must persist successfully before a timed result can be accepted;
9. a failed frozen method must not be silently modified and rerun under the same checkpoint;
10. control/API return values must not be inferred from convention when scientific validity depends on them; establish local semantics explicitly.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Mission / stable 30B target

Mission: **Big models. Small machines.** Practical ~27B/32B local AI on Apple M1/8GB.
Q4 target: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable facts:
- 48 MoE layers, 128 experts/layer, top-k 8;
- payload `16,220,499,968 B`;
- resident non-routed `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- Q4 expert `2,506,752 B`;
- BF16 KV `98,304 B/token`;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- raw 4-GiB global LRU rejected.

## DFlash — CLOSED AS ACTIVE PATH

Final: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`.
Report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.
Do not reopen absent a new independent mechanism.

## Core serving/I/O — BOTTLENECK IDENTIFIED

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` = `SERVING_IO_BOTTLENECK_IDENTIFIED`.
External expert data-access is dominant:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- 384 expert reads, `962,592,768 B` payload;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority candidate remains lossless expert-major contiguous storage, but no speedup claim is accepted until physical-I/O causality is valid.

## Expert-major A/B 001 — INVALID

`LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_001` = `EXPERT_MAJOR_PHYSICAL_IO_INVALID`.
Observed but not accepted: source p50 `1.097739 s`, packed p50 `0.382613 s`, apparent ratio `0.348547`, reads/pass `3456 -> 384`, exact payload equality PASS.
Reason: packed conservative physical coverage only `50.0644%`.

## Coverage/cold-protocol history

Coverage audit identified macOS page-cache contamination. Frozen cold timing rule: every accepted timed repetition must independently show `>=80%` conservative physical coverage.

Fresh-inode byte-copy protocol is rejected: three valid 160,432,128-B trials produced only `21.7537%`, `21.6914%`, `20.8250%` coverage with payload/hash PASS and zero swap.

Instrumentation persistence repair is PASS and no longer a blocker.

Measurement strategy redesign selected direct existing-packed reads using `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0`, with per-trial physical coverage as validity authority.

## Global-nocache cold-I/O validation 001 — FAIL, WITH POSITIVE COLDNESS SIGNAL

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001` = `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`.
Report: `research/architecture/loom-30b-expert-major-global-nocache-cold-io-validation-001-result.md`.
Evidence: `results-local/research/30b-expert-major-global-nocache-cold-io-validation-001/20260826T134143Z/`.

T1 only:
- conservative physical coverage `95.3113%`;
- wall `0.246744 s`;
- raw physical `153,010,000 B`;
- conservative physical `152,910,000 B`;
- payload/hash PASS;
- control set PASS;
- swap delta `0 B`;
- minimum free memory `59%`.

The coldness sub-gate passed strongly (`95.3113% >= 80%`). However the post-trial `F_GLOBAL_NOCACHE` reset returned `1` and the runner classified reset as failure. The frozen protocol therefore failed closed; T2/T3 were not run.

Interpretation:
- this does **not** reject the direct global-nocache cold-read mechanism;
- it provides the strongest cold-read evidence so far;
- the current blocker is exact set/reset API/runner semantics, not physical coverage;
- do not reinterpret return value `1` without explicit local semantics evidence;
- do not rerun the 160-MiB validation until reset semantics are resolved.

## Current checkpoint

`LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001`

Goal: establish exact local semantics and safe restoration behavior for `F_GLOBAL_NOCACHE` before another cold-I/O trial.

Requirements:
1. no model forward/network/DFlash/source-vs-packed A/B/full 160-MiB read;
2. inspect the exact runner call path, constants, return-value handling and any available local/system interface semantics;
3. determine what set return values and reset return values mean on this Mac/runtime;
4. capture errno/exception information where applicable;
5. determine whether post-call control state can be queried or verified directly; if not, define the smallest safe behavioral verification;
6. a tiny <=16 MiB read probe is allowed only if needed to distinguish reset semantics/state;
7. persist all set/reset call inputs, raw returns, errors, verification evidence and final restoration status;
8. do not change the coldness threshold or claim performance;
9. select exactly one fail-safe control protocol for the next validation if semantics are resolved.

Classifications:
- `GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED`
- `GLOBAL_NOCACHE_RESET_SEMANTICS_UNRESOLVED`

Only after `GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED` may a separately preregistered global-nocache cold-I/O validation retry be considered.
