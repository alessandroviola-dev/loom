#!/usr/bin/env python3
"""LOOM Direct MLX Coding Benchmark 001.

Runs frozen Coding Benchmark 01 v1.0.1 against the verified Direct MLX
Qwen3-8B-3bit profile. The benchmark tree is copied to an isolated run tree.
One MLX child process loads the model once and executes T01-T06 sequentially
while the parent enforces LOOM system-memory and swap guardrails.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MODEL_REPO = "mlx-community/Qwen3-8B-3bit"
MODEL_SHA256 = "b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1"
ADAPTER_BLOB_SHA = "62abab57f6463c5813809b43d8f1e7bdfec5f304"
SCORER_BLOB_SHA = "754e9a6506968d2b191bff57997710591efe8133"
BENCHMARK_VERSION = "1.0.1"
MAX_KV_SIZE = 4096
MAX_TOKENS = 2048
MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
POLL_SECONDS = 1.0
OLLAMA_MODEL = "qwen3.5:4b-mlx"
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}

CHILD_CODE = r'''
import json
import sys
from pathlib import Path

import mlx.core as mx
from mlx_lm import load, stream_generate

model_path = Path(sys.argv[1])
input_path = Path(sys.argv[2])
results_dir = Path(sys.argv[3])
progress_path = Path(sys.argv[4])

tasks = json.loads(input_path.read_text(encoding="utf-8"))
results_dir.mkdir(parents=True, exist_ok=True)

mx.random.seed(0)
model, tokenizer = load(str(model_path))
completed = []

for index, task in enumerate(tasks, start=1):
    task_id = task["id"]
    progress_path.write_text(
        json.dumps({"phase": "running", "index": index, "current_task": task_id, "completed": completed}),
        encoding="utf-8",
    )
    prompt_text = Path(task["prompt_path"]).read_text(encoding="utf-8")
    messages = [{"role": "user", "content": prompt_text}]
    prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    parts = []
    last = None
    for response in stream_generate(
        model,
        tokenizer,
        prompt,
        max_tokens=2048,
        max_kv_size=4096,
    ):
        parts.append(response.text)
        last = response

    result = {
        "id": task_id,
        "text": "".join(parts),
        "prompt_tokens": getattr(last, "prompt_tokens", None) if last is not None else None,
        "prompt_tps": getattr(last, "prompt_tps", None) if last is not None else None,
        "generation_tokens": getattr(last, "generation_tokens", None) if last is not None else 0,
        "generation_tps": getattr(last, "generation_tps", None) if last is not None else None,
        "peak_memory_gb": getattr(last, "peak_memory", None) if last is not None else None,
        "finish_reason": getattr(last, "finish_reason", None) if last is not None else None,
        "max_kv_size": 4096,
        "kv_bits": None,
        "thinking": False,
    }
    (results_dir / f"{task_id}.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    completed.append(task_id)
    progress_path.write_text(
        json.dumps({"phase": "completed", "index": index, "current_task": task_id, "completed": completed}),
        encoding="utf-8",
    )

progress_path.write_text(
    json.dumps({"phase": "all_completed", "index": len(tasks), "current_task": None, "completed": completed}),
    encoding="utf-8",
)
print("LOOM_CHILD_COMPLETE=" + json.dumps({"completed": completed}), flush=True)
'''


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 60, env: dict | None = None) -> dict:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
        return {
            "command": cmd,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "wall_seconds": round(time.perf_counter() - started, 3),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
            "wall_seconds": round(time.perf_counter() - started, 3),
        }
    except OSError as exc:
        return {
            "command": cmd,
            "exit_code": None,
            "error": f"{type(exc).__name__}: {exc}",
            "wall_seconds": round(time.perf_counter() - started, 3),
        }


def git_blob(path: Path, cwd: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def disk_snapshot(path: Path) -> dict:
    usage = shutil.disk_usage(path)
    return {
        "free_bytes": usage.free,
        "free_gib": round(usage.free / (1024 ** 3), 3),
    }


def parse_scaled_mb(value: str, unit: str) -> float:
    n = float(value.replace(",", "."))
    unit = unit.upper()
    if unit == "K":
        return n / 1024.0
    if unit == "M":
        return n
    if unit == "G":
        return n * 1024.0
    if unit == "T":
        return n * 1024.0 * 1024.0
    return n


def swap_used_mb() -> float | None:
    proc = subprocess.run(
        ["sysctl", "-n", "vm.swapusage"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if proc.returncode != 0:
        return None
    match = re.search(
        r"\bused\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*([KMGT])(?:B)?\b",
        proc.stdout,
        re.IGNORECASE,
    )
    if not match:
        return None
    return round(parse_scaled_mb(match.group(1), match.group(2)), 2)


def memory_free_percent() -> tuple[int | None, str]:
    proc = subprocess.run(
        ["memory_pressure"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    text = proc.stdout + proc.stderr
    match = re.search(r"System-wide memory free percentage:\s*(\d+)%", text)
    if not match:
        return None, text.strip()
    return int(match.group(1)), f"System-wide memory free percentage: {match.group(1)}%"


def process_rss_mb(pid: int) -> float | None:
    proc = subprocess.run(
        ["ps", "-o", "rss=", "-p", str(pid)],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        return float(proc.stdout.strip().splitlines()[-1]) / 1024.0
    except ValueError:
        return None


def sample_process(pid: int, elapsed: float, progress: dict | None) -> dict:
    free_pct, pressure = memory_free_percent()
    return {
        "elapsed_seconds": round(elapsed, 3),
        "rss_mb": process_rss_mb(pid),
        "swap_used_mb": swap_used_mb(),
        "memory_free_percent": free_pct,
        "memory_pressure": pressure,
        "current_task": progress.get("current_task") if isinstance(progress, dict) else None,
        "phase": progress.get("phase") if isinstance(progress, dict) else None,
    }


def sample_failure(sample: dict) -> tuple[str | None, str | None]:
    free = sample.get("memory_free_percent")
    swap = sample.get("swap_used_mb")
    if free is None or swap is None:
        return None, "required memory/swap telemetry unavailable"
    if free < MIN_FREE_PERCENT:
        return f"memory free {free}% < {MIN_FREE_PERCENT}%", None
    if swap > MAX_SWAP_MB:
        return f"swap used {swap:.2f} MB > {MAX_SWAP_MB:.0f} MB", None
    return None, None


def terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def summarize_samples(samples: list[dict]) -> dict:
    rss = [x["rss_mb"] for x in samples if isinstance(x.get("rss_mb"), (int, float))]
    swap = [x["swap_used_mb"] for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    free = [x["memory_free_percent"] for x in samples if isinstance(x.get("memory_free_percent"), int)]
    return {
        "peak_rss_mb": max(rss) if rss else None,
        "peak_swap_used_mb": max(swap) if swap else None,
        "min_memory_free_percent": min(free) if free else None,
    }


def load_adapter(path: Path):
    spec = importlib.util.spec_from_file_location("loom_frozen_single_shot_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen adapter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight = model_dir / "model.safetensors"
    adapter_path = repo / "scripts" / "ollama_single_shot.py"
    frozen = repo / "benchmarks" / "coding" / "v1"
    scorer_path = frozen / "runner.py"
    manifest_path = frozen / "manifest.json"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = mlx_root / "coding-benchmark-001" / run_id
    working = run_dir / "benchmarks" / "coding" / "v1"
    prompt_dir = run_dir / "prompts"
    raw_dir = run_dir / "raw"
    task_results_dir = run_dir / "task-results"
    progress_path = run_dir / "progress.json"
    child_input_path = run_dir / "child-input.json"
    stdout_path = run_dir / "mlx-child-stdout.txt"
    stderr_path = run_dir / "mlx-child-stderr.txt"
    summary_path = run_dir / "benchmark-summary.json"

    prompt_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    task_results_dir.mkdir(parents=True, exist_ok=True)

    summary: dict = {
        "run_id": run_id,
        "experiment": "Direct MLX Coding Benchmark 001",
        "started_at_utc": utc_now(),
        "classification": None,
        "model": MODEL_REPO,
        "runtime": {
            "max_kv_size": MAX_KV_SIZE,
            "kv_bits": None,
            "max_tokens_per_task": MAX_TOKENS,
            "thinking": False,
            "single_loaded_model_session": True,
        },
        "guardrails": {
            "min_free_percent": MIN_FREE_PERCENT,
            "max_swap_mb": MAX_SWAP_MB,
        },
        "disk_before": disk_snapshot(repo),
        "tasks": [],
    }

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = disk_snapshot(repo)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        telemetry = summary.get("telemetry") or {}
        if telemetry:
            print(f"Peak process RSS: {telemetry.get('peak_rss_mb')} MB")
            print(f"Peak observed swap: {telemetry.get('peak_swap_used_mb')} MB")
            print(f"Minimum observed free memory: {telemetry.get('min_memory_free_percent')}%")
        if "artifact_score" in summary:
            print(f"Artifact score: {summary.get('artifact_score')}/100")
            print(f"Delivery-adjusted score: {summary.get('delivery_adjusted_score')}/100")
            print(f"Structured delivery: {summary.get('written_tasks')}/6")
        print(f"Classification: {summary['classification']}")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("LOOM Direct MLX Coding Benchmark 001")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)

    required_paths = [venv_py, weight, adapter_path, frozen, scorer_path, manifest_path]
    if any(not p.exists() for p in required_paths):
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "required environment/model/adapter/benchmark/scorer path missing"
        return finish(2)

    versions = run(
        [
            str(venv_py),
            "-c",
            "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))",
        ],
        cwd=repo,
        timeout=30,
    )
    try:
        observed_versions = json.loads(versions.get("stdout", "").strip())
    except (json.JSONDecodeError, AttributeError):
        observed_versions = {}
    summary["observed_versions"] = observed_versions
    if observed_versions != EXPECTED_VERSIONS:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {observed_versions!r}"
        return finish(2)
    print(f"Version lock: PASS {observed_versions}")

    observed_sha = sha256_file(weight)
    summary["model_sha256"] = observed_sha
    if observed_sha != MODEL_SHA256:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "model SHA mismatch"
        return finish(2)
    print("Model SHA256: PASS")

    adapter_blob = git_blob(adapter_path, repo)
    scorer_blob = git_blob(scorer_path, repo)
    summary["adapter_blob_sha"] = adapter_blob
    summary["scorer_blob_sha"] = scorer_blob
    if adapter_blob != ADAPTER_BLOB_SHA or scorer_blob != SCORER_BLOB_SHA:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"frozen blob mismatch: adapter={adapter_blob} scorer={scorer_blob}"
        return finish(2)
    print("Frozen adapter/scorer blobs: PASS")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"cannot read benchmark manifest: {type(exc).__name__}: {exc}"
        return finish(2)
    if manifest.get("version") != BENCHMARK_VERSION or len(manifest.get("tasks", [])) != 6:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"benchmark invariant mismatch: version={manifest.get('version')!r} tasks={len(manifest.get('tasks', []))}"
        return finish(2)
    summary["benchmark_version"] = manifest["version"]
    print(f"Frozen benchmark: PASS (version {manifest['version']}, 6 tasks)")

    if working.exists():
        summary["classification"] = "INVALID_HARNESS"
        summary["failure_reason"] = "isolated working tree already exists unexpectedly"
        return finish(2)
    shutil.copytree(frozen, working)

    try:
        adapter = load_adapter(adapter_path)
    except Exception as exc:
        summary["classification"] = "INVALID_HARNESS"
        summary["failure_reason"] = f"cannot load frozen adapter: {type(exc).__name__}: {exc}"
        return finish(2)

    child_tasks = []
    try:
        for task in adapter.TASKS:
            task_dir = working / task["path"]
            prompt = adapter.build_prompt(task_dir, task)
            prompt_path = prompt_dir / f"{task['id']}.txt"
            prompt_path.write_text(prompt, encoding="utf-8")
            child_tasks.append({"id": task["id"], "prompt_path": str(prompt_path)})
    except Exception as exc:
        summary["classification"] = "INVALID_HARNESS"
        summary["failure_reason"] = f"cannot build frozen benchmark prompts: {type(exc).__name__}: {exc}"
        return finish(2)

    if [x["id"] for x in child_tasks] != ["T01", "T02", "T03", "T04", "T05", "T06"]:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"adapter task order mismatch: {[x['id'] for x in child_tasks]!r}"
        return finish(2)

    child_input_path.write_text(json.dumps(child_tasks, indent=2) + "\n", encoding="utf-8")
    summary["prompt_chars"] = {
        x["id"]: Path(x["prompt_path"]).stat().st_size for x in child_tasks
    }
    print("Frozen prompts: PASS (T01-T06)")

    swap_pre = swap_used_mb()
    free_pre, _ = memory_free_percent()
    summary["preflight_system"] = {"swap_used_mb": swap_pre, "memory_free_percent": free_pre}
    if swap_pre is None or free_pre is None:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = "required memory/swap telemetry unavailable before launch"
        return finish(2)
    if free_pre < MIN_FREE_PERCENT or swap_pre > MAX_SWAP_MB:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"system outside safety boundary before launch: free={free_pre}% swap={swap_pre} MB"
        return finish(2)
    print(f"Safety preflight: PASS (free={free_pre}% swap={swap_pre:.2f} MB)")

    if shutil.which("ollama"):
        summary["ollama_stop"] = run(["ollama", "stop", OLLAMA_MODEL], cwd=repo, timeout=30)

    env = dict(os.environ)
    env.update(
        {
            "HF_HOME": str(mlx_root / "hf-home"),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "PYTHONUNBUFFERED": "1",
        }
    )

    cmd = [
        str(venv_py),
        "-c",
        CHILD_CODE,
        str(model_dir),
        str(child_input_path),
        str(task_results_dir),
        str(progress_path),
    ]
    summary["child_command"] = [
        str(venv_py),
        "-c",
        "<embedded frozen benchmark child code>",
        str(model_dir),
        str(child_input_path),
        str(task_results_dir),
        str(progress_path),
    ]

    samples: list[dict] = []
    guard_reason: str | None = None
    telemetry_reason: str | None = None
    last_progress_signature = None
    started = time.perf_counter()

    print("Launching T01-T06 in one Direct MLX session...", flush=True)
    with stdout_path.open("w", encoding="utf-8") as out_f, stderr_path.open("w", encoding="utf-8") as err_f:
        proc = subprocess.Popen(
            cmd,
            cwd=repo,
            stdout=out_f,
            stderr=err_f,
            text=True,
            env=env,
        )
        try:
            while proc.poll() is None:
                progress = read_json(progress_path)
                if isinstance(progress, dict):
                    signature = (progress.get("phase"), progress.get("index"), progress.get("current_task"), tuple(progress.get("completed") or []))
                    if signature != last_progress_signature:
                        phase = progress.get("phase")
                        task_id = progress.get("current_task")
                        index = progress.get("index")
                        if phase == "running" and task_id:
                            print(f"[{index}/6] {task_id} running...", flush=True)
                        elif phase == "completed" and task_id:
                            print(f"[{index}/6] {task_id} generation complete", flush=True)
                        elif phase == "all_completed":
                            print("All six generations complete", flush=True)
                        last_progress_signature = signature

                sample = sample_process(proc.pid, time.perf_counter() - started, progress)
                samples.append(sample)
                guard_reason, telemetry_reason = sample_failure(sample)
                if guard_reason or telemetry_reason:
                    terminate(proc)
                    break
                time.sleep(POLL_SECONDS)
        finally:
            if proc.poll() is None:
                terminate(proc)

    child_wall = round(time.perf_counter() - started, 3)
    child_exit = proc.returncode
    child_stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    child_stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    summary["child_result"] = {
        "exit_code": child_exit,
        "wall_seconds": child_wall,
        "guardrail_abort_reason": guard_reason,
        "telemetry_abort_reason": telemetry_reason,
        "stdout_tail": child_stdout[-4000:],
        "stderr_tail": child_stderr[-4000:],
    }
    summary["memory_samples"] = samples
    summary["telemetry"] = summarize_samples(samples)

    # Recover every fully persisted model result, even if a later task aborts.
    generated_results: dict[str, dict] = {}
    for task in adapter.TASKS:
        result_path = task_results_dir / f"{task['id']}.json"
        result = read_json(result_path)
        if isinstance(result, dict):
            generated_results[task["id"]] = result
            (raw_dir / f"{task['id']}-generation.json").write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    summary["generated_task_count"] = len(generated_results)

    if guard_reason:
        summary["classification"] = "PARTIAL_RESOURCE_FAIL"
        summary["failure_reason"] = guard_reason
    elif telemetry_reason:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = telemetry_reason
    elif child_exit != 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"Direct MLX child exited with code {child_exit}"
    elif len(generated_results) != 6:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"child exited without six persisted task results: {len(generated_results)}/6"

    # Apply the exact frozen adapter to every completed generation. Parser/delivery
    # failures are quality evidence and do not stop later scoring if all six generations completed.
    task_records = []
    written_by_id: dict[str, bool] = {}
    for task in adapter.TASKS:
        task_id = task["id"]
        result = generated_results.get(task_id)
        record: dict = {
            "id": task_id,
            "editable": task["editable"],
            "generation_completed": isinstance(result, dict),
        }
        if not isinstance(result, dict):
            record["adapter_status"] = "not_run"
            written_by_id[task_id] = False
            task_records.append(record)
            continue

        record["metrics"] = {
            "prompt_tokens": result.get("prompt_tokens"),
            "prompt_tps": result.get("prompt_tps"),
            "generation_tokens": result.get("generation_tokens"),
            "generation_tps": result.get("generation_tps"),
            "peak_memory_gb": result.get("peak_memory_gb"),
            "finish_reason": result.get("finish_reason"),
            "output_chars": len(result.get("text")) if isinstance(result.get("text"), str) else None,
        }
        try:
            files = adapter.extract_files({"response": result.get("text")}, task["editable"])
            task_dir = working / task["path"]
            for name, content in files.items():
                (task_dir / name).write_text(content, encoding="utf-8")
            record["adapter_status"] = "written"
            written_by_id[task_id] = True
        except Exception as exc:
            record["adapter_status"] = "failed"
            record["error"] = f"{type(exc).__name__}: {exc}"
            written_by_id[task_id] = False
        task_records.append(record)

    summary["tasks"] = task_records
    summary["written_tasks"] = sum(1 for x in task_records if x.get("adapter_status") == "written")

    if summary["classification"] is not None:
        return finish(1)

    score_env = dict(os.environ)
    score_env.update(
        {
            "LOOM_MODEL": MODEL_REPO,
            "LOOM_RUNTIME": "direct_mlx",
            "LOOM_BACKEND": "mlx",
            "LOOM_MODE": "single_shot",
            "LOOM_CONTEXT": str(MAX_KV_SIZE),
        }
    )
    score_result = run(
        [sys.executable, str(working / "runner.py"), "--benchmark-root", str(working)],
        cwd=working,
        timeout=180,
        env=score_env,
    )
    summary["scorer_execution"] = score_result
    if score_result.get("exit_code") != 0:
        summary["classification"] = "INVALID_HARNESS"
        summary["failure_reason"] = "frozen benchmark scorer failed"
        return finish(2)

    try:
        benchmark_result = json.loads(score_result.get("stdout", ""))
    except json.JSONDecodeError as exc:
        summary["classification"] = "INVALID_HARNESS"
        summary["failure_reason"] = f"cannot parse frozen scorer output: {exc}"
        return finish(2)

    summary["benchmark_result"] = benchmark_result
    summary["artifact_score"] = benchmark_result.get("score")
    delivery_adjusted = round(
        sum(
            item.get("points_earned", 0)
            for item in benchmark_result.get("tasks", [])
            if written_by_id.get(item.get("id")) is True
        ),
        2,
    )
    summary["delivery_adjusted_score"] = delivery_adjusted
    summary["classification"] = "COMPLETE"

    print("\n=== QUALITY RESULT ===")
    for record in task_records:
        metrics = record.get("metrics") or {}
        print(
            f"{record['id']}: delivery={record.get('adapter_status')} "
            f"prompt={metrics.get('prompt_tokens')} gen={metrics.get('generation_tokens')} "
            f"gen_tps={metrics.get('generation_tps')}"
        )
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
