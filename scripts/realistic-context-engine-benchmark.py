#!/usr/bin/env python3
"""Run the frozen LOOM coding benchmark through one persistent ForgeLoom RPC session.

The canonical benchmark prompts are sent byte-for-byte unchanged. A stable staging
workspace is reused between tasks so Pi/Forge keeps one session while each task
still sees only its own fixture files. Canonical benchmark files are never edited.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import selectors
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmarks" / "coding" / "v1"
STATE = ROOT / ".loom" / "runtime" / "loom-deep"
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
RUN_DIR = STATE / "ce001-realistic" / STAMP
BENCH = RUN_DIR / "benchmarks" / "coding" / "v1"
WORK = RUN_DIR / "workspace"
RPC_LOG = RUN_DIR / "rpc.jsonl"
STDERR_LOG = RUN_DIR / "stderr.txt"
SUMMARY = RUN_DIR / "summary.json"
BACKEND_LOG = STATE / "llama-server.log"
GATEWAY_ACCOUNTING = STATE / "context-webui-ci" / "accounting.jsonl"
ENGINE_ROOT = Path(os.environ.get("LOOM_CONTEXT_RUNTIME_DIR", str(Path.home() / ".pi" / "agent" / "loom-context-engine"))).expanduser()
TASK_TIMEOUT = int(os.environ.get("LOOM_CE001_REALISTIC_TASK_TIMEOUT", "900"))

TASKS = [
    ("T01", "tasks/t01_generation", {"solution.py"}),
    ("T02", "tasks/t02_debugging", {"buggy.py"}),
    ("T03", "tasks/t03_comprehension", {"answer.json"}),
    ("T04", "tasks/t04_refactor", {"solution.py"}),
    ("T05", "tasks/t05_multifile", {"order.py"}),
    ("T06", "tasks/t06_constraints", {"solution.py"}),
]


def fail(msg: str) -> None:
    raise SystemExit(f"CE-001 REALISTIC FAIL: {msg}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if "__pycache__/" in rel or rel.endswith(".pyc") or rel == ".DS_Store":
            continue
        result[rel] = sha(path)
    return result


def changed_files(before: dict[str, str], after: dict[str, str]) -> set[str]:
    return {name for name in set(before) | set(after) if before.get(name) != after.get(name)}


def clean_dir(path: Path) -> None:
    if path.exists():
        for child in path.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        path.mkdir(parents=True)


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", errors="replace") as handle:
        return sum(1 for _ in handle)


def read_jsonl_since(path: Path, start_line: int) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(errors="replace").splitlines()[start_line:]:
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def timestamp_epoch(value: object) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def engine_rows_since(start_epoch: float) -> list[dict]:
    rows: list[dict] = []
    if not ENGINE_ROOT.exists():
        return rows
    for path in ENGINE_ROOT.glob("*/accounting.jsonl"):
        try:
            for line in path.read_text(errors="replace").splitlines():
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                epoch = timestamp_epoch(row.get("timestamp"))
                if epoch is not None and epoch >= start_epoch - 1.0:
                    rows.append(row)
        except OSError:
            pass
    return rows


def rss_kb(pid: int | None) -> int:
    if not pid:
        return 0
    proc = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True)
    try:
        return int(proc.stdout.strip() or 0)
    except ValueError:
        return 0


def read_pid(path: Path) -> int | None:
    try:
        return int(path.read_text().strip())
    except Exception:
        return None


def swap_snapshot() -> dict[str, object]:
    proc = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True)
    raw = proc.stdout.strip() if proc.returncode == 0 else "unavailable"
    match = re.search(r"used\s*=\s*([0-9.]+)([MG])", raw)
    used_mb = None
    if match:
        value = float(match.group(1))
        used_mb = value * (1024 if match.group(2) == "G" else 1)
    return {"raw": raw, "used_mb": used_mb}


def parse_backend_timings(text: str) -> dict[str, object]:
    prompt = [float(x) for x in re.findall(r"prompt eval time[^\n]*?\(([0-9.]+) tokens per second\)", text, flags=re.I)]
    decode = [float(x) for x in re.findall(r"(?<!prompt )eval time[^\n]*?\(([0-9.]+) tokens per second\)", text, flags=re.I)]
    def stats(values: list[float]) -> dict[str, object]:
        if not values:
            return {"count": 0}
        ordered = sorted(values)
        mid = len(ordered) // 2
        median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
        return {"count": len(values), "min": min(values), "median": round(median, 3), "max": max(values)}
    return {"prompt_eval_tok_s": stats(prompt), "decode_tok_s": stats(decode)}


if not SOURCE.exists():
    fail(f"benchmark source missing: {SOURCE}")
if shutil.which("ForgeLoom") is None:
    fail("ForgeLoom not found; run scripts/install-forge-loom.sh")

RUN_DIR.mkdir(parents=True, exist_ok=False)
shutil.copytree(SOURCE, BENCH)
WORK.mkdir(parents=True)

# Ensure live CE profile is valid before spending model work.
verify = subprocess.run(["bash", str(ROOT / "scripts" / "verify-context-engine.sh")], cwd=ROOT)
if verify.returncode != 0:
    fail("preflight verification failed")

start_epoch = time.time()
gateway_before = line_count(GATEWAY_ACCOUNTING)
backend_offset = BACKEND_LOG.stat().st_size if BACKEND_LOG.exists() else 0
swap_before = swap_snapshot()
backend_pid = read_pid(STATE / "llama-server-backend.pid")
peak_backend_rss = rss_kb(backend_pid)
peak_agent_rss = 0

stderr_handle = STDERR_LOG.open("w")
proc = subprocess.Popen(
    ["ForgeLoom", "--no-session", "--mode", "rpc"],
    cwd=WORK,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=stderr_handle,
    text=True,
    bufsize=1,
)
if proc.stdin is None or proc.stdout is None:
    proc.kill()
    fail("could not open ForgeLoom RPC pipes")

selector = selectors.DefaultSelector()
selector.register(proc.stdout, selectors.EVENT_READ)
rpc_log_handle = RPC_LOG.open("w")

def send(payload: dict) -> None:
    proc.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
    proc.stdin.flush()


def read_event(timeout_deadline: float) -> dict | None:
    global peak_agent_rss, peak_backend_rss
    while time.time() < timeout_deadline:
        peak_agent_rss = max(peak_agent_rss, rss_kb(proc.pid))
        peak_backend_rss = max(peak_backend_rss, rss_kb(backend_pid))
        events = selector.select(timeout=0.5)
        if proc.poll() is not None and not events:
            fail(f"ForgeLoom RPC exited early with status {proc.returncode}; inspect {STDERR_LOG}")
        for key, _ in events:
            line = key.fileobj.readline()
            if not line:
                continue
            rpc_log_handle.write(line)
            rpc_log_handle.flush()
            try:
                value = json.loads(line)
            except Exception:
                continue
            if isinstance(value, dict):
                return value
    fail("RPC event timeout")
    return None


def wait_response(request_id: str, timeout: int = 60) -> dict:
    deadline = time.time() + timeout
    while True:
        event = read_event(deadline)
        if event and event.get("type") == "response" and event.get("id") == request_id:
            return event

send({"id": "init", "type": "get_state"})
init = wait_response("init")
if not init.get("success"):
    proc.terminate()
    fail("RPC get_state failed")

turn_results: list[dict[str, object]] = []
violations: list[dict[str, object]] = []

try:
    for task_id, task_path, allowed in TASKS:
        task_dir = BENCH / task_path
        prompt_path = task_dir / "prompt.md"
        if not prompt_path.exists():
            fail(f"missing frozen prompt: {prompt_path}")

        clean_dir(WORK)
        for item in task_dir.iterdir():
            destination = WORK / item.name
            if item.is_dir():
                shutil.copytree(item, destination)
            else:
                shutil.copy2(item, destination)

        before = snapshot(WORK)
        prompt = prompt_path.read_text()
        request_id = f"task-{task_id.lower()}"
        turn_started = time.perf_counter()
        first_text_delta: float | None = None
        accepted = False
        send({"id": request_id, "type": "prompt", "message": prompt})
        deadline = time.time() + TASK_TIMEOUT

        while True:
            event = read_event(deadline)
            if event is None:
                continue
            if event.get("type") == "response" and event.get("id") == request_id:
                if not event.get("success"):
                    fail(f"{task_id} prompt rejected: {event}")
                accepted = True
            if event.get("type") == "message_update":
                delta = event.get("assistantMessageEvent") or {}
                if delta.get("type") == "text_delta" and first_text_delta is None:
                    first_text_delta = time.perf_counter()
            if event.get("type") == "agent_end":
                break

        duration = time.perf_counter() - turn_started
        if not accepted:
            fail(f"{task_id} ended without prompt acceptance response")

        after = snapshot(WORK)
        changed = changed_files(before, after)
        outside = sorted(name for name in changed if name not in allowed)
        if outside:
            violations.append({"task": task_id, "files": outside})

        for name in allowed:
            source_file = WORK / name
            destination = task_dir / name
            if source_file.exists() and source_file.is_file():
                shutil.copy2(source_file, destination)
            elif destination.exists():
                destination.unlink()

        turn_results.append({
            "task": task_id,
            "duration_s": round(duration, 3),
            "client_ttft_s": round(first_text_delta - turn_started, 3) if first_text_delta is not None else None,
            "changed_files": sorted(changed),
            "allowed_files": sorted(allowed),
            "out_of_scope_files": outside,
        })
        print(f"CE-001 REALISTIC INFO: {task_id} completed in {duration:.1f}s; changed={sorted(changed)}")

    send({"id": "final-state", "type": "get_state"})
    final_state = wait_response("final-state")
finally:
    try:
        proc.terminate()
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
    rpc_log_handle.close()
    stderr_handle.close()

swap_after = swap_snapshot()

# Objective frozen v1.0.1 score against the isolated edited benchmark copy.
env = os.environ.copy()
env.update({
    "LOOM_MODEL": "loom-deep-30b-unlocked",
    "LOOM_RUNTIME": "ForgeLoom/CE-001",
    "LOOM_BACKEND": "llama.cpp-patched-UOPT-003",
    "LOOM_MODE": "agentic-persistent-session",
    "LOOM_CONTEXT": "4096 physical; CE-001 1600/1200 working; 2800 input; 3600 safe-total",
})
score_proc = subprocess.run(
    [sys.executable, str(BENCH / "runner.py"), "--benchmark-root", str(BENCH)],
    cwd=BENCH,
    env=env,
    capture_output=True,
    text=True,
    timeout=180,
)
if score_proc.returncode != 0:
    fail(f"benchmark runner failed: {score_proc.stderr[-1000:]}")
try:
    benchmark_result = json.loads(score_proc.stdout)
except json.JSONDecodeError:
    fail("benchmark runner returned invalid JSON")

# Safety/accounting evidence from the exact gateway and request-local governor.
gateway_rows = read_jsonl_since(GATEWAY_ACCOUNTING, gateway_before)
engine_rows = engine_rows_since(start_epoch)
guards = [r for r in gateway_rows if r.get("guardChecked") is True]
blocks = [r for r in gateway_rows if r.get("event") in {"hard_guard_block", "hard_guard_unavailable"} or r.get("guardBlocked") is True]
governors = [r for r in engine_rows if r.get("event") == "context_governor"]
changed_governors = [r for r in governors if r.get("changed") is True]
pi_actual = [r for r in engine_rows if r.get("event") == "pi_compaction_after"]
pi_overflow = [r for r in engine_rows if r.get("event") in {"pi_compaction_before", "pi_compaction_after"} and r.get("reason") == "overflow"]

if not guards:
    fail("no exact gateway guard rows captured")
if blocks:
    fail(f"gateway hard guard blocked {len(blocks)} realistic requests")
if pi_actual:
    fail(f"Pi performed {len(pi_actual)} actual compactions")
if pi_overflow:
    fail(f"Pi overflow compaction activity observed: {len(pi_overflow)}")

backend_tail = ""
if BACKEND_LOG.exists():
    with BACKEND_LOG.open("rb") as handle:
        handle.seek(min(backend_offset, BACKEND_LOG.stat().st_size))
        backend_tail = handle.read().decode(errors="replace")
timings = parse_backend_timings(backend_tail)

state_data = (final_state.get("data") or {}) if isinstance(final_state, dict) else {}
summary = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "benchmark": benchmark_result,
    "tasks": turn_results,
    "out_of_scope_violations": violations,
    "persistent_message_count": state_data.get("messageCount"),
    "governor": {
        "calls": len(governors),
        "compactions": len(changed_governors),
        "max_before_estimate": max((int(r.get("beforeTokens", 0) or 0) for r in governors), default=0),
        "max_after_estimate": max((int(r.get("afterTokens", 0) or 0) for r in governors), default=0),
        "max_turns_dropped": max((int(r.get("turnsDropped", 0) or 0) for r in governors), default=0),
    },
    "gateway": {
        "checked_requests": len(guards),
        "blocks": len(blocks),
        "max_final_input": max(int(r.get("finalInputTokens", 0) or 0) for r in guards),
        "max_projected_total": max(int(r.get("projectedTotalTokens", 0) or 0) for r in guards),
        "min_headroom_to_4096": min(4096 - int(r.get("projectedTotalTokens", 0) or 0) for r in guards),
    },
    "pi": {
        "actual_compactions": len(pi_actual),
        "overflow_events": len(pi_overflow),
    },
    "memory": {
        "swap_before": swap_before,
        "swap_after": swap_after,
        "peak_backend_rss_mb_sampled": round(peak_backend_rss / 1024, 1),
        "peak_agent_rss_mb_sampled": round(peak_agent_rss / 1024, 1),
    },
    "timings": timings,
}
SUMMARY.write_text(json.dumps(summary, indent=2) + "\n")

print("CE-001 realistic coding benchmark: COMPLETE")
print(f"  score                    : {benchmark_result.get('score')} / {benchmark_result.get('max_score')}")
print(f"  persistent messages      : {summary['persistent_message_count']}")
print(f"  governor calls           : {summary['governor']['calls']}")
print(f"  governor compactions     : {summary['governor']['compactions']}")
print(f"  max visible estimate     : {summary['governor']['max_after_estimate']}")
print(f"  exact gateway requests   : {summary['gateway']['checked_requests']}")
print(f"  max exact final input    : {summary['gateway']['max_final_input']}")
print(f"  max projected total      : {summary['gateway']['max_projected_total']}")
print(f"  min headroom to 4096     : {summary['gateway']['min_headroom_to_4096']}")
print(f"  hard-guard blocks        : {summary['gateway']['blocks']}")
print(f"  Pi actual compactions    : {summary['pi']['actual_compactions']}")
print(f"  Pi overflow events       : {summary['pi']['overflow_events']}")
print(f"  out-of-scope edits       : {len(violations)}")
print(f"  sampled backend RSS MB   : {summary['memory']['peak_backend_rss_mb_sampled']}")
print(f"  sampled agent RSS MB     : {summary['memory']['peak_agent_rss_mb_sampled']}")
print(f"  swap before              : {swap_before['raw']}")
print(f"  swap after               : {swap_after['raw']}")
print(f"  prompt eval tok/s        : {timings['prompt_eval_tok_s']}")
print(f"  decode tok/s             : {timings['decode_tok_s']}")
print(f"  summary                  : {SUMMARY}")
print(f"  rpc log                  : {RPC_LOG}")
print(f"  stderr                   : {STDERR_LOG}")

if violations:
    fail(f"agent modified files outside frozen task scope: {violations}")
print("CE-001 REALISTIC PASS: session survived, scope held, exact guard stayed safe, and objective benchmark score was recorded")
