#!/usr/bin/env python3
"""LOOM Direct MLX Setup Probe 001.

Creates/reuses an isolated MLX environment and validates exact pinned package
versions plus a tiny local MLX computation. No model weights are requested.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MLX_LM_VERSION = "0.31.3"
MLX_VERSION = "0.31.2"
TRANSFORMERS_VERSION = "5.12.1"
VENV_NAME = f"venv-mlx-lm-{MLX_LM_VERSION}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], cwd: Path, timeout: int = 300, env: dict[str, str] | None = None) -> dict:
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
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "exit_code": None,
            "stdout": exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            "stderr": exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or ""),
            "timed_out": True,
        }


def disk_free_gib(path: Path) -> float:
    return round(shutil.disk_usage(path).free / (1024 ** 3), 3)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    mlx_root = repo_root / "results-local" / "mlx"
    venv = mlx_root / VENV_NAME
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = mlx_root / "setup-probe-001" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "setup-summary.json"

    print("LOOM Direct MLX Setup Probe 001")
    disk_before = disk_free_gib(repo_root)
    print(f"Disk free before: {disk_before:.3f} GiB")

    uname = run(["uname", "-m"], repo_root, timeout=30)
    host = {
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "uname_m": uname.get("stdout", "").strip(),
        "python": sys.version,
        "python_executable": sys.executable,
    }

    summary: dict = {
        "run_id": run_id,
        "experiment": "Direct MLX Setup Probe 001",
        "started_at_utc": utc_now(),
        "classification": None,
        "host": host,
        "pinned": {
            "mlx-lm": MLX_LM_VERSION,
            "mlx": MLX_VERSION,
            "transformers": TRANSFORMERS_VERSION,
        },
        "venv": str(venv),
        "disk_before_gib": disk_before,
        "model_download_authorized": False,
    }

    arm64 = host["platform_system"] == "Darwin" and host["platform_machine"] == "arm64" and host["uname_m"] == "arm64"
    print(f"Platform preflight: {'PASS' if arm64 else 'FAIL'} ({host['platform_system']} {host['platform_machine']}, uname={host['uname_m']})")
    if not arm64:
        summary["classification"] = "PLATFORM_FAIL"
        summary["failure_reason"] = "Direct MLX reference probe requires macOS arm64"
        summary["disk_after_gib"] = disk_free_gib(repo_root)
        summary["finished_at_utc"] = utc_now()
        write_json(summary_path, summary)
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 1

    if not venv.exists():
        print("Creating isolated venv...", flush=True)
        create = run([sys.executable, "-m", "venv", str(venv)], repo_root, timeout=180)
        summary["venv_create"] = create
        if create.get("exit_code") != 0:
            summary["classification"] = "SETUP_FAIL"
            summary["failure_reason"] = "venv creation failed"
            summary["disk_after_gib"] = disk_free_gib(repo_root)
            summary["finished_at_utc"] = utc_now()
            write_json(summary_path, summary)
            print("Venv creation: FAIL")
            print(f"Summary: {summary_path}")
            return 1
        print("Venv creation: PASS")
    else:
        summary["venv_create"] = {"needed": False, "reused": True}
        print("Venv: PRESENT / REUSE")

    py = venv / "bin" / "python"
    if not py.exists():
        summary["classification"] = "SETUP_FAIL"
        summary["failure_reason"] = "venv python missing"
        summary["disk_after_gib"] = disk_free_gib(repo_root)
        summary["finished_at_utc"] = utc_now()
        write_json(summary_path, summary)
        print("Venv Python: FAIL")
        print(f"Summary: {summary_path}")
        return 1

    pins = [
        f"mlx=={MLX_VERSION}",
        f"mlx-lm=={MLX_LM_VERSION}",
        f"transformers=={TRANSFORMERS_VERSION}",
    ]
    print("Installing/verifying pinned MLX packages...", flush=True)
    install = run(
        [str(py), "-m", "pip", "install", "--disable-pip-version-check", "--no-input", *pins],
        repo_root,
        timeout=1200,
    )
    summary["pip_install"] = install
    (out_dir / "pip-install-stdout.txt").write_text(install.get("stdout", ""), encoding="utf-8")
    (out_dir / "pip-install-stderr.txt").write_text(install.get("stderr", ""), encoding="utf-8")
    if install.get("exit_code") != 0:
        summary["classification"] = "SETUP_FAIL"
        summary["failure_reason"] = "pinned package installation failed"
        summary["disk_after_gib"] = disk_free_gib(repo_root)
        summary["finished_at_utc"] = utc_now()
        write_json(summary_path, summary)
        print("Pinned package install: FAIL")
        print(f"Summary: {summary_path}")
        return 1
    print("Pinned package install: PASS")

    offline_env = dict(os.environ)
    offline_env["HF_HUB_OFFLINE"] = "1"
    offline_env["TRANSFORMERS_OFFLINE"] = "1"

    version_code = (
        "import importlib.metadata as m, json; "
        "print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))"
    )
    versions = run([str(py), "-c", version_code], repo_root, timeout=60, env=offline_env)
    summary["version_probe"] = versions
    observed: dict = {}
    if versions.get("exit_code") == 0:
        try:
            observed = json.loads(versions.get("stdout", "").strip())
        except json.JSONDecodeError:
            observed = {}
    summary["observed_versions"] = observed
    exact_versions = observed == {
        "mlx": MLX_VERSION,
        "mlx-lm": MLX_LM_VERSION,
        "transformers": TRANSFORMERS_VERSION,
    }
    print(f"Version lock: {'PASS' if exact_versions else 'FAIL'} {observed}")
    if not exact_versions:
        summary["classification"] = "VERSION_FAIL"
        summary["failure_reason"] = "installed package versions do not match frozen pins"
        summary["disk_after_gib"] = disk_free_gib(repo_root)
        summary["finished_at_utc"] = utc_now()
        write_json(summary_path, summary)
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 1

    compute_code = (
        "import json, mlx.core as mx; "
        "x=mx.array([1,2,3]); y=x*2; mx.eval(y); "
        "print(json.dumps({'result':y.tolist(),'default_device':str(mx.default_device())}))"
    )
    compute = run([str(py), "-c", compute_code], repo_root, timeout=60, env=offline_env)
    summary["mlx_compute"] = compute
    compute_ok = False
    if compute.get("exit_code") == 0:
        try:
            payload = json.loads(compute.get("stdout", "").strip())
            summary["mlx_compute_payload"] = payload
            compute_ok = payload.get("result") == [2, 4, 6]
        except json.JSONDecodeError:
            pass
    print(f"MLX local compute: {'PASS' if compute_ok else 'FAIL'}")
    if not compute_ok:
        summary["classification"] = "SETUP_FAIL"
        summary["failure_reason"] = "MLX local compute/import probe failed"
        summary["disk_after_gib"] = disk_free_gib(repo_root)
        summary["finished_at_utc"] = utc_now()
        write_json(summary_path, summary)
        print(f"Summary: {summary_path}")
        return 1

    mlx_cli = run([str(py), "-m", "mlx", "--version"], repo_root, timeout=60, env=offline_env)
    mlx_lm_cli = run([str(py), "-m", "mlx_lm", "--version"], repo_root, timeout=60, env=offline_env)
    summary["mlx_cli_version"] = mlx_cli
    summary["mlx_lm_cli_version"] = mlx_lm_cli

    freeze = run([str(py), "-m", "pip", "freeze"], repo_root, timeout=120, env=offline_env)
    summary["pip_freeze_exit_code"] = freeze.get("exit_code")
    (out_dir / "pip-freeze.txt").write_text(freeze.get("stdout", ""), encoding="utf-8")
    (out_dir / "pip-freeze-stderr.txt").write_text(freeze.get("stderr", ""), encoding="utf-8")

    disk_after = disk_free_gib(repo_root)
    summary["disk_after_gib"] = disk_after
    summary["classification"] = "PASS"
    summary["finished_at_utc"] = utc_now()
    write_json(summary_path, summary)

    print(f"Disk free after: {disk_after:.3f} GiB")
    print("Classification: PASS")
    print(f"Run directory: {out_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
