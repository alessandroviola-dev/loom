# LOOM 30B Noninteractive Frontend Recovery 001 — Result

Date: 2026-08-29
Classification: **`LOOM_30B_NONINTERACTIVE_FRONTEND_RECOVERY_GO`**

## Purpose

Mechanically establish the correct one-shot frontend for the frozen Apple MoE paging runtime and harden the local Stage1 harness against runaway subprocess output, without opening the model or running inference.

## Evidence

Canonical local evidence:
`results-local/research/30b-noninteractive-frontend-recovery-001/20260829T205441Z/report.json`

Source proof:
`results-local/research/30b-noninteractive-frontend-recovery-001/20260829T205441Z/source-confirmation-locations.txt`

Harness diff:
`results-local/research/30b-noninteractive-frontend-recovery-001/20260829T205441Z/harness-full.diff`

## Source diagnosis

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Confirmed from exact source:
- `tools/cli/cli.cpp:359-363`: `llama-cli` rejects `--no-conversation` and directs non-conversation use to `llama-completion`;
- `tools/cli/cli.cpp:449-500`: `llama-cli` contains the interactive `> ` / `readline` loop;
- `tools/completion/completion.cpp:46-50`: one-shot generation documents `-no-cnv`;
- `common/arg.cpp:1532-1542` plus completion control flow confirm non-conversation bounded generation exits rather than entering the interactive loop.

## Noninteractive frontend build

Built only the authorized target from the existing exact frozen checkout/build:

`cmake --build results-local/research/30b-apple-moe-paging-feasibility-001/20260829T130414Z/build --target llama-completion`

Source remained clean at the frozen commit.

`llama-completion` SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Existing `llama-cli` SHA remained unchanged:
`c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`

No-model help/argument parsing confirmed all required Stage1 scientific flags, including `-no-cnv`.

## Harness hardening

Recovered harness SHA256:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`

Mechanical changes:
- removed unbounded in-memory `chunks`, per-chunk `drain_events`, and full-file output decoding;
- subprocess output still streams directly to durable disk;
- fsync every 1 MiB and at completion;
- bounded/O(1) drain accounting plus 1 MiB analysis tail;
- hard per-profile output cap: 64 MiB;
- cap violation terminates child and persists `MECHANICAL_OUTPUT_RUNAWAY`;
- incremental telemetry and `finally` finalization retained.

The prior multi-gigabyte output path could materially contribute to the ~14 GiB swap observed in the invalid Stage1R runaway. That swap is not attributable to model residency.

## Synthetic-only validation

No GGUF was opened and no model inference occurred.

Passed:
- mixed stdout/stderr child: 2,097,152 bytes retained exactly, exit 0;
- nonzero child: same retained output, exit 7, evidence finalized;
- runaway child: terminated at the 64 MiB cap, retained bytes `67,108,864`, trigger byte `67,108,865`, exit `-15`, reason `MECHANICAL_OUTPUT_RUNAWAY`;
- parent peak RSS increase ~10.313 MiB;
- swap delta 0.0 MiB;
- profile, telemetry and final report survived;
- no lingering child process.

## Validated future command shape

Not executed during this recovery:

`llama-completion -m <verified-read-only-GGUF> -p <frozen-Stage1-prompt> -n 96 -c 1024 --temp 0 --moe-n-slots <8|16|24> --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -ub 1 -no-cnv`

## Conclusion

Recovery is GO. A fresh preregistered Stage1R2 may now repeat the original scientific workload with the exact same model/source hypothesis, changing only the mechanically corrected noninteractive frontend and bounded-output instrumentation.