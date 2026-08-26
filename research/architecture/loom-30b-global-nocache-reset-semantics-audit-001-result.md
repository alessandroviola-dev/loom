# LOOM 30B — Global Nocache Reset Semantics Audit 001

Date: 2026-08-26
Checkpoint: `LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001`
Classification: `GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED`
Evidence: `results-local/research/30b-global-nocache-reset-semantics-audit-001/20260826T135941Z/`

## Result

The reset failure from `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001` was a runner interpretation bug, not a failed kernel control transition.

Local interface:
- `F_GLOBAL_NOCACHE = 55` from local `sys/fcntl.h`;
- old runner: Python 3.13 `fcntl.fcntl(fd, 55, argument)` on a fresh `O_RDONLY` FD;
- old success predicate incorrectly required `returned == 0` for both set and reset.

Established local semantics:
- set argument `1` from state 0: raw return `0`, `errno=0`, transition `0 -> 1`;
- reset argument `0` from state 1: raw return `1`, `errno=0`, transition `1 -> 0`;
- therefore reset return `1` is successful and reports the preceding state.

No passive `F_GET_GLOBAL_NOCACHE` query exists locally. Reversible transactional verification on distinct empty files produced `[0,1,0,1,0,1]` under native C, historical Python `fcntl`, and a fixed-ABI C/ctypes wrapper. No payload read was required (`0 B`).

## Frozen future control protocol

Use a fixed-ABI native helper that clears/captures `errno` around `fcntl(fd, 55, value)`.

1. SET before payload: argument `1`; require raw return `0`, `errno=0`, no exception.
2. RESET after payload: argument `0`; require raw return `1`, `errno=0`, no exception.
3. Verify restoration transactionally: SET `1` must return `0`; immediate RESET `0` must return `1`; `errno=0` throughout.
4. Any deviation: persist control/FD evidence, restore captured state if known, close FD, fail closed, and reject the timing repetition.

## Interpretation

The earlier T1 coldness observation (`95.3113%` conservative physical coverage) remains strong positive evidence. However validation 001 remains an overall protocol FAIL because it terminated after T1 and did not complete the preregistered 3/3 trials. It is not retroactively reclassified.

Next checkpoint: `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002`, repeating the same packed-only 3-trial coldness validation with only the control-return semantics/predicate repaired.
