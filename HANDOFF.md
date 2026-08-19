# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal phase has characterized the current 8B frontier at context 4096. Qwen3 8B Q2 is technically runnable but inferior on the frozen structured coding workload; Qwen3 8B Q3_K_M is API-smoke viable with NP1 + Q8_0 KV but fails the frozen 5% free-memory guardrail during the first real coding task. The main branch now moves to Phase 5 Direct MLX.
Checkpoint: `DIRECT_MLX_SETUP_PROBE_001_READY`

## Mission

Study practical local LLM/agent execution on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.
Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

Reference stack:
- Apple M1, 8 GB unified memory
- Ollama 0.32.14
- Pi 0.84.2
- Qwen Code 0.21.13
- canonical Ollama model `qwen3.5:4b-mlx`
- canonical experimental context 4096 unless separately preregistered

## Production Pi constraint

Production Pi contains real auth, sessions and customizations. LOOM must never reset/replace production Pi configuration. Controlled experiments use isolated/run-local configuration. No new runtime/model profile is exposed to Pi until technical, workload-safety and quality gates are passed.

## Storage hygiene

Reuse verified artifacts and never silently delete models or canonical results. Free disk is a standard metric.
Latest confirmed after Coding Quality Compare 002: **43.643 GiB free**. Verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 GGUF artifacts are retained.

# Frozen baseline / prior results

## Coding Baseline 001 — Ollama/MLX qwen3.5:4b-mlx
Run `20260818-203156`, context 4096:
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt 186.46 tok/s
- generation 16.01 tok/s

## Pi Agentic Coding Benchmark 001
Run `20260818-214848`:
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6
- provider usage 20,209 tokens

# Phase 4 — llama.cpp — MAIN BRANCH CHARACTERIZED

Pinned source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

4B Runtime Control 001:
- Qwen3-4B Q4_K_M, 2.326 GiB
- pp512 230.85 t/s ±0.12
- tg128 22.33 t/s ±0.02
- minimum free memory 22%

8B Q4 Capability 001:
- context 4096 / forced `-ngl -1`
- minimum free memory 1%
- VALID FAIL

## 8B Q2

Qwen3-8B Q2_K:
- Stage B FULL_PASS: pp512 103.00 t/s ±0.67; tg128 13.72 t/s ±0.34; minimum free 8%
- llama-server smoke FULL_PASS: API `OK`; minimum free 6%
- Coding Quality Compare 001: Q2 delivery 0/100 vs 4B Q4 34.29/100
- diagnostic: transport/API/JSON healthy but structured delivery degraded; repeated literal `filename` handling

Boundary:
> Q2 is technically runnable/API-servable but is not a practical upgrade for the frozen structured coding workload.

## 8B Q3 rescue sequence

Q3 forced `-ngl -1` Capability 001:
- minimum free memory 1%
- VALID FAIL

Auto-Fit Server Smoke 001:
- auto server parallelism produced `n_slots=4`
- minimum free memory 4%
- VALID FAIL

Auto-Fit NP1 Server Smoke 001:
- `n_slots=1` verified
- minimum free memory still 4%
- VALID FAIL

Auto-Fit NP1 Q8 KV Server Smoke 001 — run `20260819-113658`:
- Qwen3-8B Q3_K_M
- context 4096
- `-np 1`
- FA auto
- `--fit on --fit-target 1024 --fit-ctx 4096`
- `-ctk q8_0 -ctv q8_0`
- no forced `-ngl -1`
- readiness 8.756 s
- API `OK`
- minimum free memory 6%
- FULL_PASS

This established API-smoke viability only.

## Coding Quality Compare 002 — PARTIAL / RESOURCE FAIL

Run `20260819-114848`.
Common Q3/4B runtime:
```text
-c 4096
-np 1
-fa auto
--fit on
--fit-target 1024
--fit-ctx 4096
-ctk q8_0
-ctv q8_0
no forced -ngl -1
```

Q3:
- server ready 7.360 s
- T01 entered real request processing
- exact abort: `memory free 4% < 5%`
- peak observed swap 2290.88 MB
- minimum free memory 4%
- no HTTP response captured because the runner terminated the server at the safety threshold
- profile `PARTIAL_OR_RESOURCE_FAIL`

Persisted memory timeline around T01:
```text
7.3 s   free 6%
8.4 s   free 5%
9.7 s   free 5%
11.9 s  free 5%
13.1 s  free 5%
14.3 s  free 5%
15.4 s  free 5%
16.7 s  free 7%
18.3 s  free 5%
20.3 s  free 4% -> guardrail
```

4B under the same runtime:
- COMPLETE
- minimum free memory 15%
- delivery-adjusted 25.72/100

Canonical conclusion:
> The exact Qwen3-8B Q3_K_M + llama.cpp + NP1 + Q8_0-KV profile is **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096 under the frozen 5% free-memory boundary. Compare 002 does not establish intrinsic Q3-vs-4B quality because Q3 did not complete.

Records:
- `research/runtime/llama-cpp-coding-quality-compare-002.md`
- `research/runtime/llama-cpp-coding-quality-compare-002-diagnostic.md`

Do not expose this Q3 llama.cpp profile to Pi. Do not lower the guardrail or reinterpret printed `4B_HIGHER` as a valid quality ordering.

# Phase 5 — Direct MLX — ACTIVE

## Current checkpoint — Setup Probe 001

Checkpoint: `DIRECT_MLX_SETUP_PROBE_001_READY`
Plan: `research/runtime/direct-mlx-setup-probe-001-plan.md`
Runner: `scripts/direct_mlx_setup_probe.py`

Goal:
> Establish a reproducible isolated direct-MLX environment before any new model download.

Frozen environment:
- venv: `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- macOS arm64 required
- complete `pip freeze` captured
- tiny local MLX array computation required
- **no LLM model weights downloaded by this probe**

Candidate after setup PASS:
- `mlx-community/Qwen3-8B-3bit`
- practical Qwen3 8B / 3-bit direct-MLX profile
- not bit-identical or causally equivalent to GGUF `Q3_K_M`
- model acquisition and runtime smoke require a separate preregistration with disk accounting and the same memory safety boundary

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_setup_probe.py
python3 scripts/direct_mlx_setup_probe.py
```

Preserve output through `Summary:`.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
