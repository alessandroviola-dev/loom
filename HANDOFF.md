# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_030_MLX_0312_0320_RUNTIME_COMPARISON_FIX3_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate scientific PASS gate.

## Research rules

- One scientific factor at a time.
- Preserve PASS, scientific FAIL and harness/setup defects.
- No post-hoc gate weakening, hidden rescue ladders or automatic retries.
- Runtime abort where inherited: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- No deliberate macOS cache purge to manufacture host state.
- Balanced within-experiment ratios are causal evidence; absolute cross-experiment throughput is host/cache-state dependent.
- Runtime/model upgrades are separately preregistered and never rewrite historical evidence.
- Update HANDOFF and ROADMAP after meaningful checkpoints.

## Frozen model / historical runtime

Model: `results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Qwen3 geometry:
- hidden 4096
- 36 layers
- vocab 151936
- 32 attention heads / 8 KV heads / head dim 128
- RMSNorm eps 1e-6
- untied embedding/head
- 3-bit/group64 affine quantization.

Historical canonical runtime through Stretch 029:
- mlx 0.31.2
- mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- Python 3.13.0.

Canonical MLX venv/interpreter:
`results-local/mlx/venv-mlx-lm-0.31.3/bin/python`

Raw weights:
- total `3,583,928,320 B`
- transformer body `3,039,381,504 B`
- each layer `84,427,264 B` / 25 tensors
- embedding `272,269,312 B`
- final RMSNorm `8,192 B`
- LM head `272,269,312 B`.

Ordinary BF16 KV remains frozen.

## Canonical Stretch evidence

### Stretch 001–017 — exact block frontier

Established layer-addressable I/O, streamed/full parity, persistent BF16 KV, persistent hotsets and oracle verification.

MLX 0.31.2 exactness frontier:
- M8 valid numerical-parity FAIL;
- q/k/v/o exact through M9, first divergence M10;
- gate/up/down exact through M5, first divergence M6;
- M5 exact end-to-end over 15 oracle tokens.

Decision: M5 is maximum demonstrated exact oracle block under MLX 0.31.2.

### Stretch 018 — M4/M5 cost — COMPLETE PASS

- M5/M4 `1.09795340695x` (~+9.80%).

### Stretch 019–022 — transformer residency — COMPLETE

Controlled gains:
- H8 -> H16 ~+56.87%
- H16 -> H24 ~+34.86%
- H24 -> H32 ~+11.45%
- H32 -> H36 ~+10.50%.

Decision: H36 is the physical transformer-residency ceiling.

### Stretch 023 — full raw-weight persistence — COMPLETE PASS

Valid Fix1 `20260820-153308`:
- PERSISTENT/STREAMED `1.5988607374x` (~+59.89%).

Decision: freeze M5 + H36 + full persistence.

### Stretch 024 — compute/framework attribution — COMPLETE PASS

Valid Fix2 `20260820-160140`:
- transformer compute `0.8081826820 s/block`
- attention `0.2207656117 s/block`
- MLP `0.5874170703 s/block`
- old per-layer cleanup `0.9268928333 s/block`.

Decision: cleanup/framework first.

### Stretch 025–027 — cleanup schedule — COMPLETE

025:
- BATCHED/CONTROL `3.8627785715x` (~+286.28%).

026:
- SHARED_BATCHED/BATCHED `1.1410704391x` (~+14.11%).

027 valid `20260820-163715`:
- SINGLE_PASS/SHARED_BATCHED `1.0867142144x` (~+8.67%)
- pooled `12.7306853225 token/s`
- median block `0.396305 s`.

Decision: freeze **M5 + H36 + full persistence + one final cleanup/pass**.

Canonical Stretch 027 workload:
`scripts/stretch_full_persistent_single_pass_cleanup_027.py`
blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`.

### Stretch 028 — compute re-attribution — COMPLETE PASS

Valid `20260820-164802`:
- transformer compute `0.4496960012 s/block`
- attention path `0.1231006118 s/block`
- MLP path `0.3265953895 s/block`
- MLP/attention `2.6530769000x`
- up/attention/gate/down each ~0.095–0.099 s/block.

Decision: true transformer compute is primary target.

### Stretch 029 — gate+up fusion — COMPLETE PASS / NOT PROMOTED

Initial `20260820-170503`: harness defect / no science.

Valid Fix1 ABBA `20260820-171714`:
- CONTROL `13.2286272786 token/s`
- FUSED `12.3523991241 token/s`
- FUSED/CONTROL `0.9337627302x` (~6.62% slower)
- FUSED exact at M5
- FUSED median wall ~8.62% higher.

Decision: do not promote; fusion path closed under MLX 0.31.2. Stretch 027 remains preferred 0.31.2 architecture.

Canonical result:
`research/stretch/gate-up-quantized-fusion-029-result.md`

## Stretch 030 — coherent MLX 0.31.2 vs 0.32.0 — FIX3 READY

Scientific question:
Does changing only the coherent macOS MLX runtime pair (`mlx` + `mlx-metal`) from 0.31.2 to 0.32.0 preserve frozen M5 correctness and improve target-verification cost?

Scientific factor:
- CONTROL: mlx 0.31.2 + mlx-metal 0.31.2
- TREATMENT: mlx 0.32.0 + mlx-metal 0.32.0.

Frozen besides runtime:
- Qwen3-8B 3-bit/group64
- M5
- H36
- full persistence
- one final cleanup/pass
- mlx-lm 0.31.3
- transformers 5.12.1
- NumPy 2.5.2
- safetensors 0.8.0
- Python 3.13.0
- BF16 KV
- oracle/numerical/top-1/acceptance gates
- resource/I-O policy
- no cache purge.

### Environment Setup Fix1 — VALID / PRESERVED

Original shell-Python setup failed before science because shell `python3` was not the canonical LOOM venv. Scientific result NONE.

Setup Fix1 then passed and must **not** be rerun.

CONTROL venv:
`results-local/mlx/venv-mlx-lm-0.31.3`
- mlx 0.31.2
- mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- numpy 2.5.2
- safetensors 0.8.0.

TREATMENT clone:
`.venvs/stretch030-mlx0320-fix1`
- mlx 0.32.0
- mlx-metal 0.32.0
- tracked non-runtime package versions identical.

Setup utility:
`scripts/stretch_mlx_0320_env_setup_030_fix1.py`
blob `dfcc05aa6f730756056a75d5bf867bbd717ac31f`.

### Runner Fix1 defect — NO SCIENCE

Fix1 stopped before Attempt 1 because its invariant required nonexistent `MLX_0320_RUNTIME_NUMERICAL_PARITY_FAIL`; the frozen class is `MLX_0320_RUNTIME_EXACTNESS_FAIL`.

Preserved:
`research/stretch/mlx-0312-0320-runtime-comparison-030-runner-defect-20260820-1738.md`.

### Runner Fix2 defect — NO SCIENCE

Fix2 also stopped before Attempt 1 at environment provenance.

Observed CONTROL executable became framework Python with MLX packages MISSING, despite the canonical venv path being selected.

Root cause:
- Fix2 used `(repo / CONTROL_VENV / "bin/python").resolve()`;
- on macOS the venv `bin/python` is a symlink;
- resolving it before execution dereferenced to `/Library/Frameworks/Python.framework/...` and lost venv identity.

The same issue existed in the portable inner-child path via `Path(sys.executable).resolve()` and was identified before any child launch.

Preserved defect:
`research/stretch/mlx-0312-0320-runtime-comparison-030-runner-defect-fix2-20260820-1745.md`.

### Portable workload Fix1

`scripts/stretch_runtime_portable_single_pass_030_fix1.py`
blob `44251a524c77a379f43445444fa8a2643f1bfbdf`.

Harness-only behavior:
- retains the previous two-version portable preflight (`mlx` only 0.31.2 or 0.32.0; mlx-lm/Transformers fixed);
- changes inner child path from `Path(sys.executable).resolve()` to `Path(sys.executable)`;
- preserves the selected venv through the child process boundary;
- scientific Stretch 027 workload unchanged.

### Balanced runner Fix3

`scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix3.py`
blob `108aed0e7e66fafe9b3213e33a57c34f9e0602d2`.

Harness-only changes over Fix2:
- common workload -> portable Fix1 blob above;
- CONTROL path uses `repo / CONTROL_VENV / "bin/python"` without `.resolve()`;
- TREATMENT keeps `.venvs/stretch030-mlx0320-fix1/bin/python`;
- child runtime provenance remains mandatory;
- fresh result root `mlx-0312-0320-runtime-comparison-030-fix3`.

Fix3 preregistration:
`research/stretch/mlx-0312-0320-runtime-comparison-030-harness-fix3.md`.

Balanced order remains:
`MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`.

Outcome policy:
- first genuine MLX0320 numerical/top-1/oracle failure => `MLX_0320_RUNTIME_EXACTNESS_FAIL`, valid scientific FAIL, stop/no rescue;
- complete exact ABBA => `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`;
- environment/harness/resource/runtime-provenance issue => `MLX_0312_0320_RUNTIME_COMPARISON_INCOMPLETE`.

## Exact next step

Do not rerun setup. Do not run runner Fix1 or Fix2.

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_runtime_portable_single_pass_030_fix1.py
python3 -m py_compile scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix3.py
python3 scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix3.py
```

## After Stretch 030

- If 0.32.0 is exact + faster: freeze 030, then separately remap M exactness boundary under 0.32.0.
- If exact + flat/slower: retain 0.31.2 and choose another compute factor.
- If exactness FAIL: preserve it; no mixed-package rescue.
- Real drafter integration remains separate; current rates are oracle-verification upper bounds.

## Other track

Amplify remains queued behind Stretch:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`.
