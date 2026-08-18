#!/usr/bin/env python3
"""LOOM llama.cpp Phase 4 setup probe.

Clones/fetches a pinned official llama.cpp commit into results-local, configures
an Apple Silicon Metal Release build, builds llama-cli and llama-bench, and
records machine/toolchain/build metadata. No model is downloaded.

Important pinned-source detail: at the selected llama.cpp commit, tools/cli is
added only when LLAMA_BUILD_SERVER=ON. We therefore keep server support enabled
while disabling the embedded Web UI.

Standard library only.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PINNED_REPO = "https://github.com/ggml-org/llama.cpp.git"
PINNED_COMMIT = "60addddf3c567c43ec3caf70fc953fba3572d96f"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path, timeout: int = 60) -> dict:
    try:
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": args,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": args, "error": f"{type(exc).__name__}: {exc}"}


def cmd_version(cmd: list[str], cwd: Path) -> str:
    result = run(cmd, cwd)
    return (result.get("stdout", "") + result.get("stderr", "")).strip()


def find_cache_value(cache: Path, key: str) -> str | None:
    if not cache.exists():
        return None
    prefix = f"{key}:"
    for line in cache.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix) and "=" in line:
            return line.split("=", 1)[1].strip()
    return None


def finish_failure(summary: dict, out_dir: Path, reason: str, headline: str, detail: str = "") -> int:
    summary["success"] = False
    summary["failure_reason"] = reason
    summary["finished_at_utc"] = utc_now()
    path = out_dir / "setup-summary.json"
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("LOOM llama.cpp Phase 4 setup probe")
    print(headline)
    if detail:
        print(detail)
    print(f"Summary: {path}")
    return 1


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    required = ["git", "cmake", "xcrun", "clang", "sysctl"]
    missing = [name for name in required if shutil.which(name) is None]

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = repo_root / "results-local" / "llama-cpp"
    source = root / f"source-{PINNED_COMMIT[:12]}"
    build = source / "build-loom-metal"
    out_dir = root / "setup" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    summary: dict = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "experiment": "llama.cpp Phase 4 setup probe",
        "probe_revision": 2,
        "official_repo": PINNED_REPO,
        "pinned_commit": PINNED_COMMIT,
        "repo_root": str(repo_root),
        "source_dir": str(source),
        "build_dir": str(build),
        "missing_prerequisites": missing,
        "system": {
            "sw_vers": cmd_version(["sw_vers"], repo_root),
            "hardware": cmd_version(["system_profiler", "SPHardwareDataType"], repo_root),
            "hw_memsize": cmd_version(["sysctl", "-n", "hw.memsize"], repo_root),
            "logicalcpu": cmd_version(["sysctl", "-n", "hw.logicalcpu"], repo_root),
        },
        "toolchain": {
            "git": cmd_version(["git", "--version"], repo_root),
            "cmake": cmd_version(["cmake", "--version"], repo_root) if shutil.which("cmake") else "",
            "clang": cmd_version(["clang", "--version"], repo_root) if shutil.which("clang") else "",
            "xcode": cmd_version(["xcrun", "xcodebuild", "-version"], repo_root) if shutil.which("xcrun") else "",
            "xcode_select": cmd_version(["xcode-select", "-p"], repo_root) if shutil.which("xcode-select") else "",
        },
        "steps": {},
    }

    if missing:
        return finish_failure(
            summary,
            out_dir,
            f"missing prerequisites: {', '.join(missing)}",
            f"Prerequisites: FAIL — missing {', '.join(missing)}",
        )

    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        clone = run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", PINNED_REPO, str(source)],
            repo_root,
            timeout=300,
        )
        summary["steps"]["clone"] = clone
        if clone.get("exit_code") != 0:
            return finish_failure(summary, out_dir, "git clone failed", "Clone: FAIL", clone.get("stderr", "").strip())

    fetch = run(["git", "fetch", "origin", PINNED_COMMIT, "--depth", "1"], source, timeout=300)
    summary["steps"]["fetch"] = fetch
    if fetch.get("exit_code") != 0:
        return finish_failure(
            summary,
            out_dir,
            "git fetch pinned commit failed",
            "Fetch pinned commit: FAIL",
            fetch.get("stderr", "").strip(),
        )

    checkout = run(["git", "checkout", "--detach", PINNED_COMMIT], source, timeout=60)
    summary["steps"]["checkout"] = checkout
    source_sha = run(["git", "rev-parse", "HEAD"], source).get("stdout", "").strip()
    summary["source_commit_actual"] = source_sha

    configure_cmd = [
        "cmake",
        "-S", ".",
        "-B", str(build),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DGGML_METAL=ON",
        "-DGGML_METAL_EMBED_LIBRARY=ON",
        "-DLLAMA_BUILD_TESTS=OFF",
        "-DLLAMA_BUILD_SERVER=ON",
        "-DLLAMA_BUILD_UI=OFF",
        "-DLLAMA_BUILD_COMMON=ON",
        "-DLLAMA_BUILD_TOOLS=ON",
    ]
    configure = run(configure_cmd, source, timeout=300)
    summary["steps"]["configure"] = configure

    jobs_text = run(["sysctl", "-n", "hw.logicalcpu"], repo_root).get("stdout", "").strip()
    jobs = jobs_text if jobs_text.isdigit() else "4"
    build_cmd = [
        "cmake",
        "--build", str(build),
        "--config", "Release",
        "-j", jobs,
        "--target", "llama-cli", "llama-bench",
    ]
    build_result = run(build_cmd, source, timeout=900)
    summary["steps"]["build"] = build_result

    cli = build / "bin" / "llama-cli"
    bench = build / "bin" / "llama-bench"
    cache = build / "CMakeCache.txt"
    cache_keys = [
        "GGML_METAL",
        "GGML_METAL_EMBED_LIBRARY",
        "LLAMA_BUILD_COMMON",
        "LLAMA_BUILD_TOOLS",
        "LLAMA_BUILD_SERVER",
        "LLAMA_BUILD_UI",
    ]
    cache_values = {key: find_cache_value(cache, key) for key in cache_keys}

    summary["build_verification"] = {
        "llama_cli_exists": cli.exists(),
        "llama_bench_exists": bench.exists(),
        "cmake_cache_exists": cache.exists(),
        **cache_values,
        "llama_cli_version": cmd_version([str(cli), "--version"], source) if cli.exists() else "",
        "llama_bench_help_ok": run([str(bench), "--help"], source, timeout=30).get("exit_code") == 0 if bench.exists() else False,
    }

    success = (
        checkout.get("exit_code") == 0
        and source_sha == PINNED_COMMIT
        and configure.get("exit_code") == 0
        and build_result.get("exit_code") == 0
        and cli.exists()
        and bench.exists()
        and cache_values["GGML_METAL"] == "ON"
        and cache_values["LLAMA_BUILD_SERVER"] == "ON"
        and cache_values["LLAMA_BUILD_UI"] == "OFF"
    )

    summary["success"] = success
    if not success:
        summary["failure_reason"] = "one or more setup verification checks failed"
    summary["finished_at_utc"] = utc_now()
    path = out_dir / "setup-summary.json"
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("LOOM llama.cpp Phase 4 setup probe")
    print(f"Pinned commit: {PINNED_COMMIT}")
    print(f"Actual commit: {source_sha or 'N/A'}")
    print("Prerequisites: PASS")
    print(f"Configure: {'PASS' if configure.get('exit_code') == 0 else 'FAIL'}")
    print(f"Build: {'PASS' if build_result.get('exit_code') == 0 else 'FAIL'}")
    print(f"llama-cli: {'PASS' if cli.exists() else 'FAIL'}")
    print(f"llama-bench: {'PASS' if bench.exists() else 'FAIL'}")
    for key in cache_keys:
        print(f"{key}: {cache_values[key]}")
    print(f"Success: {success}")

    if configure.get("exit_code") != 0 and configure.get("stderr", "").strip():
        print("--- configure stderr ---")
        print(configure["stderr"].strip())
    if build_result.get("exit_code") != 0 and build_result.get("stderr", "").strip():
        print("--- build stderr ---")
        print(build_result["stderr"].strip())

    print(f"Source: {source}")
    print(f"Build: {build}")
    print(f"Summary: {path}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
