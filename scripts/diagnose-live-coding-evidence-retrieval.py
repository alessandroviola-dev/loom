#!/usr/bin/env python3
"""Offline diagnostic for the latest CE-002 coding-retrieval run."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".loom" / "runtime" / "loom-deep"
RUN_ROOT = STATE / "ce002-live-coding-retrieval"
GATEWAY = STATE / "context-webui-ci" / "accounting.jsonl"
ERROR = "ERROR_CE002_271828"
TARGET = "src/retry_policy.py"
EXTRA = "diagnostics/ERROR_CE002_271828.json"
EXPECTED = [5, 13, 29, 61]


def load_jsonl(path: Path) -> list[dict]:
    out = []
    if not path.exists():
        return out
    for line in path.read_text(errors="replace").splitlines():
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, dict):
            out.append(value)
    return out


def latest_run() -> Path:
    runs = sorted(p for p in RUN_ROOT.glob("*") if (p / "workspace").is_dir())
    if not runs:
        raise SystemExit("CE-002 DIAG FAIL: no coding-retrieval run found")
    return runs[-1]


def workspace_files(workspace: Path) -> list[str]:
    files = []
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(workspace).as_posix()
        if "__pycache__" in path.parts or rel.endswith(".pyc") or rel.startswith(".ruff_cache/") or rel == ".DS_Store":
            continue
        files.append(rel)
    return sorted(files)


def check_target(workspace: Path):
    target = workspace / TARGET
    if not target.exists():
        return None, False, "target missing"
    try:
        spec = importlib.util.spec_from_file_location("ce002_diag_retry_policy", target)
        if spec is None or spec.loader is None:
            return None, False, "import spec unavailable"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fn = getattr(module, "retry_delay", None)
        if not callable(fn):
            return None, False, "retry_delay missing"
        actual = [fn(i) for i in range(1, 5)]
        bad_ok = True
        for bad in (0, 5):
            try:
                fn(bad)
            except ValueError:
                pass
            else:
                bad_ok = False
        return actual, actual == EXPECTED and bad_ok, None
    except Exception as exc:
        return None, False, f"{type(exc).__name__}: {exc}"


def main() -> None:
    run = latest_run()
    workspace = run / "workspace"
    files = workspace_files(workspace)
    allowed = {"README.md", TARGET}
    unexpected = sorted(set(files) - allowed)
    actual, contract_ok, target_error = check_target(workspace)

    extra_path = workspace / EXTRA
    extra_excerpt = ""
    if extra_path.exists():
        extra_excerpt = extra_path.read_text(errors="replace")[:1600]

    rpc_rows = load_jsonl(run / "rpc.jsonl")
    needle = EXTRA
    provenance = []
    for row in rpc_rows:
        rendered = json.dumps(row, ensure_ascii=False)
        if needle in rendered:
            provenance.append(rendered[:1800])

    accounting = []
    for path in (run / "engine-runtime").glob("*/accounting.jsonl"):
        accounting.extend(load_jsonl(path))
    retrievals = [r for r in accounting if r.get("event") == "evidence_retrieval"]
    final_retrieval = retrievals[-1] if retrievals else {}
    ids = [x for x in (final_retrieval.get("evidenceIds") or []) if isinstance(x, str)]
    visible = int(final_retrieval.get("finalVisibleTokens", 0) or 0)

    matched = False
    blobs = run / "engine-runtime" / "evidence" / "blobs"
    for evidence_id in ids:
        if not evidence_id.startswith("ev1-"):
            continue
        blob_path = blobs / f"{evidence_id[4:]}.json"
        if not blob_path.exists():
            continue
        try:
            blob = json.loads(blob_path.read_text())
        except Exception:
            continue
        text = json.dumps(blob.get("message"), sort_keys=True)
        if ERROR in text and "attempt 1 -> 5 seconds" in text and "attempt 4 -> 61 seconds" in text:
            matched = True
            break

    threshold = [r for r in accounting if r.get("event") == "pi_compaction_after" and r.get("reason") == "threshold"]
    overflow = [r for r in accounting if r.get("event") in {"pi_compaction_before", "pi_compaction_after"} and r.get("reason") == "overflow"]
    archive_errors = [r for r in accounting if r.get("event") == "evidence_archive_error"]
    retrieval_errors = [r for r in accounting if r.get("event") == "evidence_retrieval_error"]

    governors = [r for r in accounting if r.get("event") == "context_governor"]
    attempts = len(governors)
    gateway_candidates = [
        r for r in load_jsonl(GATEWAY)
        if r.get("guardChecked") is True
        or r.get("guardBlocked") is True
        or r.get("event") in {"hard_guard_block", "hard_guard_unavailable"}
    ]
    run_gateway = gateway_candidates[-attempts:] if attempts and len(gateway_candidates) >= attempts else []
    blocked = [r for r in run_gateway if r.get("guardBlocked") is True or r.get("event") in {"hard_guard_block", "hard_guard_unavailable"}]
    checked = [r for r in run_gateway if r.get("guardChecked") is True]
    max_input = max((int(r.get("finalInputTokens", 0) or 0) for r in checked), default=0)
    max_total = max((int(r.get("projectedTotalTokens", 0) or 0) for r in checked), default=0)

    retrieval_ok = bool(retrievals) and bool(ids) and matched and 0 < visible <= 1200 and not archive_errors and not retrieval_errors
    safety_ok = attempts >= 4 and len(checked) == attempts and not blocked and max_input <= 2800 and max_total <= 3600 and not threshold and not overflow
    scope_ok = not unexpected
    full_gate = retrieval_ok and safety_ok and contract_ok and scope_ok

    print("CE-002 coding retrieval diagnostic")
    print(f"  run                       : {run}")
    print(f"  workspace files           : {files}")
    print(f"  unexpected files          : {unexpected}")
    print(f"  hidden expected delays    : {EXPECTED}")
    print(f"  actual delays             : {actual}")
    print(f"  coding contract           : {'PASS' if contract_ok else 'FAIL'}")
    if target_error:
        print(f"  target error              : {target_error}")
    print(f"  retrieval applications    : {len(retrievals)}")
    print(f"  final evidence ids        : {ids}")
    print(f"  evidence matches old CI   : {matched}")
    print(f"  retrieval visible tokens  : {visible}")
    print(f"  provider attempts         : {attempts}")
    print(f"  max exact final input     : {max_input}")
    print(f"  max projected total       : {max_total}")
    print(f"  hard-guard blocks         : {len(blocked)}")
    print(f"  Pi threshold compactions  : {len(threshold)}")
    print(f"  Pi overflow events        : {len(overflow)}")
    print(f"  retrieval/safety          : {'PASS' if retrieval_ok and safety_ok else 'FAIL'}")
    print(f"  scope discipline          : {'PASS' if scope_ok else 'FAIL'}")
    print(f"  RPC refs to extra file    : {len(provenance)}")
    if extra_excerpt:
        print("\nextra file excerpt:")
        print(extra_excerpt)
    if provenance:
        print("\nRPC provenance excerpts:")
        for item in provenance[-4:]:
            print(item)
    print(f"\nCE-002 realistic coding gate: {'PASS' if full_gate else 'FAIL'}")


if __name__ == "__main__":
    main()
