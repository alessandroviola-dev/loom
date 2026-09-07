#!/usr/bin/env python3
"""Recover score and safety evidence from the latest completed CE-001 realistic run.

Use when all frozen coding tasks reached agent_end but the harness exited before
final scoring/summary (for example because final get_state telemetry timed out).
No model inference is performed.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".loom" / "runtime" / "loom-deep"
RUNS_ROOT = STATE / "ce001-realistic"
SOURCE = ROOT / "benchmarks" / "coding" / "v1"
GATEWAY_ACCOUNTING = STATE / "context-webui-ci" / "accounting.jsonl"
BACKEND_LOG = STATE / "llama-server.log"
ENGINE_ROOT = Path.home() / ".pi" / "agent" / "loom-context-engine"

TASKS = [
    ("T01", "tasks/t01_generation", {"solution.py"}),
    ("T02", "tasks/t02_debugging", {"buggy.py"}),
    ("T03", "tasks/t03_comprehension", {"answer.json"}),
    ("T04", "tasks/t04_refactor", {"solution.py"}),
    ("T05", "tasks/t05_multifile", {"order.py"}),
    ("T06", "tasks/t06_constraints", {"solution.py"}),
]


def fail(message: str) -> None:
    raise SystemExit(f"CE-001 RECOVERY FAIL: {message}")


def ignored(rel: str) -> bool:
    return (
        "__pycache__/" in rel
        or "/.ruff_cache/" in f"/{rel}"
        or rel.startswith(".ruff_cache/")
        or rel.endswith(".pyc")
        or rel == ".DS_Store"
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not root.exists():
        return out
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if ignored(rel):
            continue
        out[rel] = digest(path)
    return out


def parse_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(errors="replace").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def parse_epoch(value: object) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def stats(values: list[float]) -> dict[str, object]:
    if not values:
        return {"count": 0}
    ordered = sorted(values)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    return {
        "count": len(values),
        "min": min(values),
        "median": round(median, 3),
        "max": max(values),
    }


def latest_recoverable_run() -> Path:
    if not RUNS_ROOT.exists():
        fail(f"no realistic run directory: {RUNS_ROOT}")
    candidates = sorted((p for p in RUNS_ROOT.iterdir() if p.is_dir()), key=lambda p: p.name, reverse=True)
    for run in candidates:
        bench = run / "benchmarks" / "coding" / "v1"
        rpc = run / "rpc.jsonl"
        if bench.exists() and rpc.exists():
            return run
    fail("no recoverable realistic run found")
    raise AssertionError


run = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else latest_recoverable_run()
bench = run / "benchmarks" / "coding" / "v1"
rpc_log = run / "rpc.jsonl"
summary_path = run / "recovered-summary.json"
if not bench.exists() or not rpc_log.exists():
    fail(f"run lacks benchmark/RPC evidence: {run}")

rpc_rows = parse_jsonl(rpc_log)
accepted_tasks = {
    row.get("id")
    for row in rpc_rows
    if row.get("type") == "response"
    and row.get("success") is True
    and isinstance(row.get("id"), str)
    and row.get("id", "").startswith("task-t")
}
agent_ends = sum(1 for row in rpc_rows if row.get("type") == "agent_end")
assistant_calls = sum(
    1
    for row in rpc_rows
    if row.get("type") == "message_start"
    and isinstance(row.get("message"), dict)
    and row["message"].get("role") == "assistant"
)
if len(accepted_tasks) < 6 or agent_ends < 6:
    fail(f"run did not complete all six tasks: accepted={len(accepted_tasks)}, agent_end={agent_ends}")
if assistant_calls <= 0:
    fail("could not infer provider-call count from RPC log")

# Persisted benchmark copy may only differ from the frozen source in each task's
# explicitly editable file. Transient workspace caches are intentionally ignored.
scope_violations: list[dict[str, object]] = []
for task_id, task_path, allowed in TASKS:
    before = snapshot(SOURCE / task_path)
    after = snapshot(bench / task_path)
    changed = {name for name in set(before) | set(after) if before.get(name) != after.get(name)}
    outside = sorted(name for name in changed if name not in allowed)
    if outside:
        scope_violations.append({"task": task_id, "files": outside})

# Objective frozen v1.0.1 score. This is pure local Python; no LLM call.
env = dict(**__import__("os").environ)
env.update({
    "LOOM_MODEL": "loom-deep-30b-unlocked",
    "LOOM_RUNTIME": "ForgeLoom/CE-001",
    "LOOM_BACKEND": "llama.cpp-patched-UOPT-003",
    "LOOM_MODE": "agentic-persistent-session-recovered",
    "LOOM_CONTEXT": "4096 physical; CE-001 1600/1200 working; 2800 input; 3600 safe-total",
})
score_proc = subprocess.run(
    [sys.executable, str(bench / "runner.py"), "--benchmark-root", str(bench)],
    cwd=bench,
    env=env,
    capture_output=True,
    text=True,
    timeout=180,
)
if score_proc.returncode != 0:
    fail(f"benchmark runner failed: {score_proc.stderr[-1200:]}")
try:
    benchmark = json.loads(score_proc.stdout)
except Exception as exc:
    fail(f"benchmark runner returned invalid JSON: {exc}")

# Governor rows have timestamps, so this slice is exact to the run window.
try:
    run_start = datetime.strptime(run.name, "%Y%m%d-%H%M%S").timestamp()
except ValueError:
    run_start = rpc_log.stat().st_ctime
run_end = rpc_log.stat().st_mtime + 120.0
engine_rows: list[dict] = []
if ENGINE_ROOT.exists():
    for path in ENGINE_ROOT.glob("*/accounting.jsonl"):
        for row in parse_jsonl(path):
            epoch = parse_epoch(row.get("timestamp"))
            if epoch is not None and run_start - 2 <= epoch <= run_end:
                engine_rows.append(row)
governors = [row for row in engine_rows if row.get("event") == "context_governor"]
changed_governors = [row for row in governors if row.get("changed") is True]
pi_actual = [row for row in engine_rows if row.get("event") == "pi_compaction_after"]
pi_overflow = [
    row for row in engine_rows
    if row.get("event") in {"pi_compaction_before", "pi_compaction_after"}
    and row.get("reason") == "overflow"
]
if not governors:
    fail("no governor evidence found for recovered run")

# Gateway rows have no timestamps in CE-001. One chat accounting row is emitted
# per provider call, so the current run is reconstructed from the tail using the
# assistant message_start count from its RPC log. This is safe only while no newer
# ForgeLoom inference has been run after the failed benchmark.
gateway_all = [
    row for row in parse_jsonl(GATEWAY_ACCOUNTING)
    if row.get("path") in {"/v1/chat/completions", "/chat/completions"}
]
if len(gateway_all) < assistant_calls:
    fail(f"gateway accounting has fewer rows ({len(gateway_all)}) than RPC provider calls ({assistant_calls})")
gateway_rows = gateway_all[-assistant_calls:]
blocks = [row for row in gateway_rows if row.get("guardBlocked") is True or row.get("event") in {"hard_guard_block", "hard_guard_unavailable"}]
guards = [row for row in gateway_rows if row.get("guardChecked") is True]
if len(guards) != assistant_calls:
    fail(f"not every recovered provider call has exact guard evidence: {len(guards)}/{assistant_calls}")
if blocks:
    fail(f"recovered run contains {len(blocks)} gateway block/unavailable rows")
if pi_actual:
    fail(f"Pi performed {len(pi_actual)} actual compactions")
if pi_overflow:
    fail(f"Pi overflow activity observed: {len(pi_overflow)}")

# Recover backend throughput by matching the same number of most recent provider
# calls. Peak RSS and swap-before were process-local samples and cannot be rebuilt.
prompt_rates: list[float] = []
decode_rates: list[float] = []
if BACKEND_LOG.exists():
    text = BACKEND_LOG.read_text(errors="replace")
    prompt_rates = [float(x) for x in re.findall(r"prompt eval time[^\n]*?\(([0-9.]+) tokens per second\)", text, flags=re.I)][-assistant_calls:]
    decode_rates = [float(x) for x in re.findall(r"(?<!prompt )eval time[^\n]*?\(([0-9.]+) tokens per second\)", text, flags=re.I)][-assistant_calls:]

persistent_lower_bound = max((int(row.get("messageCountBefore", 0) or 0) for row in governors), default=0)
summary = {
    "recovered_from": str(run),
    "recovery_note": "Final get_state timed out after all six agent_end events; no model inference was repeated.",
    "benchmark": benchmark,
    "rpc": {
        "accepted_tasks": len(accepted_tasks),
        "agent_end_events": agent_ends,
        "provider_calls": assistant_calls,
        "persistent_message_count_lower_bound": persistent_lower_bound,
    },
    "scope": {
        "persisted_copy_violations": scope_violations,
        "transient_cache_policy": ".ruff_cache/__pycache__ ignored",
    },
    "governor": {
        "calls": len(governors),
        "compactions": len(changed_governors),
        "max_before_estimate": max(int(row.get("beforeTokens", 0) or 0) for row in governors),
        "max_after_estimate": max(int(row.get("afterTokens", 0) or 0) for row in governors),
        "max_turns_dropped": max(int(row.get("turnsDropped", 0) or 0) for row in governors),
    },
    "gateway": {
        "reconstruction": f"tail {assistant_calls} chat accounting rows matched to RPC assistant message_start count",
        "checked_requests": len(guards),
        "blocks": len(blocks),
        "max_final_input": max(int(row.get("finalInputTokens", 0) or 0) for row in guards),
        "max_projected_total": max(int(row.get("projectedTotalTokens", 0) or 0) for row in guards),
        "min_headroom_to_4096": min(4096 - int(row.get("projectedTotalTokens", 0) or 0) for row in guards),
    },
    "pi": {"actual_compactions": len(pi_actual), "overflow_events": len(pi_overflow)},
    "timings": {"prompt_eval_tok_s": stats(prompt_rates), "decode_tok_s": stats(decode_rates)},
    "memory": {"peak_rss": "unrecoverable after harness exit", "swap_before": "unrecoverable after harness exit"},
}
summary_path.write_text(json.dumps(summary, indent=2) + "\n")

print("CE-001 realistic benchmark RECOVERED")
print(f"  run                      : {run}")
print(f"  score                    : {benchmark.get('score')} / {benchmark.get('max_score')}")
for task in benchmark.get("tasks", []):
    print(f"  {task.get('id')}                       : {task.get('tests_passed')}/{task.get('tests_total')} tests; {task.get('points_earned')}/{task.get('points_available')} pts")
print(f"  RPC accepted tasks       : {len(accepted_tasks)}")
print(f"  RPC agent_end events     : {agent_ends}")
print(f"  provider calls           : {assistant_calls}")
print(f"  persistent msg lower bd  : {persistent_lower_bound}")
print(f"  governor calls           : {len(governors)}")
print(f"  governor compactions     : {len(changed_governors)}")
print(f"  max raw estimate         : {summary['governor']['max_before_estimate']}")
print(f"  max visible estimate     : {summary['governor']['max_after_estimate']}")
print(f"  max exact final input    : {summary['gateway']['max_final_input']}")
print(f"  max projected total      : {summary['gateway']['max_projected_total']}")
print(f"  min headroom to 4096     : {summary['gateway']['min_headroom_to_4096']}")
print(f"  hard-guard blocks        : {len(blocks)}")
print(f"  Pi actual compactions    : {len(pi_actual)}")
print(f"  Pi overflow events       : {len(pi_overflow)}")
print(f"  persisted scope issues   : {len(scope_violations)}")
print(f"  prompt eval tok/s        : {summary['timings']['prompt_eval_tok_s']}")
print(f"  decode tok/s             : {summary['timings']['decode_tok_s']}")
print("  peak RSS / swap-before   : unavailable from crashed harness")
print(f"  recovered summary        : {summary_path}")

if scope_violations:
    fail(f"persisted benchmark copy contains out-of-scope edits: {scope_violations}")
print("CE-001 RECOVERY PASS: objective score and safety evidence recovered without rerunning ForgeLoom")
