# LOOM 30B Expert-Major Global Nocache Cold-I/O Validation 001 — Result

Date: 2026-08-26
Classification: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
Evidence: `results-local/research/30b-expert-major-global-nocache-cold-io-validation-001/20260826T134143Z/`

## Frozen protocol

Packed-only validation on the first 64 packed experts (`160,432,128 B/trial`), direct read of the existing packed payload with a fresh read-only FD and `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0` before any payload read. Frozen PASS required all 3/3 trials to satisfy >=80% conservative physical coverage plus payload, instrumentation, control set/reset and safety gates.

## Result

Trial 1:
- conservative physical coverage: `95.3113%`;
- wall: `0.246744 s`;
- raw physical bytes: `153,010,000 B`;
- conservative physical bytes: `152,910,000 B`;
- payload/hash: PASS;
- control set: PASS;
- swap delta: `0 B`;
- minimum free memory: `59%`.

The frozen physical-coverage gate was exceeded strongly on T1, providing positive evidence that direct-existing-packed `F_GLOBAL_NOCACHE` can produce a genuinely physical read under this workload.

However the post-trial `F_GLOBAL_NOCACHE` reset step returned `1` and was classified as reset failure by the runner. Per preregistration, the experiment failed closed and T2/T3 were not executed.

## Interpretation

This is a protocol FAIL, not evidence that the cold-read mechanism failed. The coldness sub-gate passed on the only executed trial (`95.3113% >= 80%`). The unresolved blocker is the exact API/runner semantics of setting and resetting `F_GLOBAL_NOCACHE`.

Do not reinterpret return value `1` as success or failure without a dedicated semantics audit. Do not rerun the 160-MiB validation until reset semantics and post-call state are established independently.

## Next

`LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001`

Audit the exact local API/runner behavior for `F_GLOBAL_NOCACHE` set/reset with no performance benchmark. Establish the meaning of return values, errno/exception behavior, whether reset actually changes the control state, and a fail-safe way to verify restoration. Use no model forward/network/DFlash/full payload benchmark; only a tiny control-state probe if needed.
