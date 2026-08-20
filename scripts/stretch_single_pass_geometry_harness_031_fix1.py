#!/usr/bin/env python3
"""Shared Stretch 031 Fix1 renderer and preflight.

This harness-only module reconstructs the generated runtime source without
starting the MLX model child.  It preserves every frozen transform and applies
the Stretch 031 geometry only after the inherited Stretch 017/H36 final-source
invariant has run.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.metadata as metadata
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SOURCE_027_PATH = Path("scripts/stretch_full_persistent_single_pass_cleanup_027.py")
SOURCE_027_BLOB = "6636456df5a773ac6062fdad66b7dc96abe8bd81"
TEN_TOKEN_ORACLE = "[1,374,264,4647,1483,304,279,1809,315,5994]"
CANONICAL_CHILD_PYTHON = Path("results-local/mlx/venv-mlx-lm-0.31.3/bin/python")
EXPECTED_RUNTIME = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}

VARIANTS = {
    "M5": {
        "block_size": 5,
        "block_count": 2,
        "classification": "SINGLE_PASS_M5_TEN_TOKEN_GEOMETRY_PASS",
        "terminal_title": "LOOM Stretch 031 — M5 Ten-Token H36 Full-Persistent Single-Pass Control",
        "summary_title": "Stretch 031 — M5 Ten-Token H36 Full-Persistent Single-Pass Control",
        "run_directory": "m5-ten-token-single-pass-control-031-fix1",
    },
    "M2": {
        "block_size": 2,
        "block_count": 5,
        "classification": "SINGLE_PASS_M2_TEN_TOKEN_GEOMETRY_PASS",
        "terminal_title": "LOOM Stretch 031 — M2 Ten-Token H36 Full-Persistent Single-Pass Treatment",
        "summary_title": "Stretch 031 — M2 Ten-Token H36 Full-Persistent Single-Pass Treatment",
        "run_directory": "m2-ten-token-single-pass-treatment-031-fix1",
    },
}


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo, capture_output=True,
        text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Stretch 031 Fix1 transform failed for {label}: expected 1 occurrence, found {count}")
    return source.replace(old, new, 1)


def replace_all(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f"Stretch 031 Fix1 transform failed for {label}: source text missing")
    return source.replace(old, new)


def add_geometry(source: str, variant: str) -> str:
    """Apply the only final-runtime differences for the named 10-token geometry."""
    cfg = VARIANTS[variant]
    source = replace_once(source, "ORACLE_BLOCK_SIZE = 5\n", f"ORACLE_BLOCK_SIZE = {cfg['block_size']}\n", "block size")
    source = replace_once(source, "ORACLE_BLOCK_COUNT = 3\n", f"ORACLE_BLOCK_COUNT = {cfg['block_count']}\n", "block count")
    source = replace_once(
        source,
        "ORACLE_SEQUENCE = [1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8]\n",
        f"ORACLE_SEQUENCE = {TEN_TOKEN_ORACLE}\n",
        "ten-token oracle prefix",
    )
    source = replace_once(source, "GENERATED_TOKENS = 15\n", "GENERATED_TOKENS = 10\n", "resident continuation")
    source = replace_all(source, "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS", cfg["classification"], "PASS classification")
    source = replace_all(
        source,
        "LOOM Stretch 027 — Five-Token H36 Full-Persistent Single-Pass-Cleanup Variant",
        cfg["terminal_title"],
        "terminal title",
    )
    # The failed original helper searched for a nonexistent Stretch 027 summary
    # title.  The actual generated source retains the inherited Stretch 013
    # summary identity, which is the exact failing literal observed by Fix1.
    source = replace_all(
        source,
        "Stretch 013 — Four-Token Oracle Block Verification",
        cfg["summary_title"],
        "inherited summary title",
    )
    source = replace_all(
        source,
        "five-token-h36-full-persistent-single-pass-cleanup-027",
        cfg["run_directory"],
        "run directory",
    )
    return source


def inherited_modules(repo: Path) -> tuple[Any, dict[str, Any], dict[str, Path]]:
    s027_path = repo / SOURCE_027_PATH
    observed027 = git_blob(s027_path, repo)
    if observed027 != SOURCE_027_BLOB:
        raise RuntimeError(f"Stretch 031 Fix1 provenance failure: Stretch027={observed027}")
    s027 = load_module(s027_path, "loom_stretch027_for_031_fix1")
    paths = {
        "s026": repo / s027.SOURCE_026_PATH,
        "s025": repo / s027.SOURCE_025_PATH,
        "fix1": repo / s027.SOURCE_FIX1_PATH,
        "broken": repo / s027.SOURCE_BROKEN_PATH,
        "h36": repo / s027.SOURCE_H36_PATH,
        "s017": repo / s027.SOURCE_017_PATH,
        "s013": repo / s027.SOURCE_013_PATH,
    }
    expected = {
        "s026": s027.SOURCE_026_BLOB,
        "s025": s027.SOURCE_025_BLOB,
        "fix1": s027.SOURCE_FIX1_BLOB,
        "broken": s027.SOURCE_BROKEN_BLOB,
        "h36": s027.SOURCE_H36_BLOB,
        "s017": s027.SOURCE_017_BLOB,
        "s013": s027.SOURCE_013_BLOB,
    }
    observed = {key: git_blob(path, repo) for key, path in paths.items()}
    if observed != expected:
        raise RuntimeError(f"Stretch 031 Fix1 inherited provenance failure: observed={observed} expected={expected}")
    modules = {
        "s026": load_module(paths["s026"], "loom_stretch026_for_031_fix1"),
        "s025": load_module(paths["s025"], "loom_stretch025_for_031_fix1"),
        "fix1": load_module(paths["fix1"], "loom_stretch023_fix1_for_031_fix1"),
        "broken": load_module(paths["broken"], "loom_stretch023_broken_for_031_fix1"),
        "h36": load_module(paths["h36"], "loom_stretch022_h36_for_031_fix1"),
        "s017": load_module(paths["s017"], "loom_stretch017_for_031_fix1"),
    }
    return s027, modules, paths


def inject_geometry_callback(wrapper: str, variant: str) -> tuple[str, dict[str, int]]:
    anchor = (
        "    missing = [fragment for fragment in required_fragments if fragment not in source]\n"
        "    if missing:\n"
        "        raise RuntimeError(f\"oracle transformed-source invariant failed; missing {missing}\")\n\n"
        "    if not is_child:\n"
    )
    replacement = anchor.replace(
        "    if not is_child:\n",
        f"    source = __stretch031_apply_geometry_{variant.lower()}(source)\n\n    if not is_child:\n",
    )
    if wrapper.count(anchor) != 1:
        raise RuntimeError("Stretch 031 Fix1 wrapper invariant failed: inherited post-preflight anchor missing")
    inherited_position = wrapper.index(anchor)
    wrapper = wrapper.replace(anchor, replacement, 1)
    callback = f"__stretch031_apply_geometry_{variant.lower()}(source)"
    callback_position = wrapper.index(callback)
    final_exec = '    exec(compile(source, str(source009), "exec"), transformed_globals)\n'
    if wrapper.count(final_exec) != 1:
        raise RuntimeError("Stretch 031 Fix1 wrapper invariant failed: final runtime execution anchor missing")
    final_exec_position = wrapper.index(final_exec)
    if not inherited_position < callback_position < final_exec_position:
        raise RuntimeError("Stretch 031 Fix1 wrapper callback phase invariant failed")
    return wrapper, {
        "inherited_m5_preflight_offset": inherited_position,
        "geometry_callback_offset": callback_position,
        "final_runtime_execution_offset": final_exec_position,
    }


def build_wrapper(repo: Path, variant: str) -> tuple[str, dict[str, Any], dict[str, Path], Any, dict[str, Any]]:
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant}")
    s027, modules, paths = inherited_modules(repo)
    wrapper = modules["h36"].transformed_013_wrapper(paths["s013"].read_text(encoding="utf-8"), modules["s017"])
    wrapper = modules["fix1"].inject_runtime_callback(wrapper)
    wrapper = modules["s025"].inject_cleanup_callback(wrapper)
    wrapper = modules["s026"].inject_shared_cleanup_callback(wrapper)
    wrapper = s027.inject_single_pass_callback(wrapper)
    wrapper, phase = inject_geometry_callback(wrapper, variant)
    required = [
        "__stretch023_add_shared_persistence(source)",
        "__stretch025_apply_batched_cleanup(source)",
        "__stretch026_apply_shared_batched_cleanup(source)",
        "__stretch027_apply_single_pass_cleanup(source)",
        f"__stretch031_apply_geometry_{variant.lower()}(source)",
        "oracle transformed-source invariant failed",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 031 Fix1 wrapper invariant failed: missing {missing}")
    return wrapper, phase, paths, s027, modules


def render_final_source(repo: Path, variant: str) -> tuple[str, dict[str, Any]]:
    """Execute only the wrapper's source-transform stage and capture final source.

    The final MLX runtime `exec` is replaced in memory with a collector.  No
    model, model child, resource telemetry, or scientific measurement starts.
    """
    wrapper, phase, paths, s027, modules = build_wrapper(repo, variant)
    final_exec = '    exec(compile(source, str(source009), "exec"), transformed_globals)\n'
    wrapper = wrapper.replace(final_exec, "    __stretch031_collect_final_source(source)\n", 1)
    trailer = '\nif __name__ == "__main__":\n    raise SystemExit(main())\n'
    if wrapper.count(trailer) != 1:
        raise RuntimeError("Stretch 031 Fix1 render invariant failed: wrapper main trailer missing")
    wrapper = wrapper.replace(trailer, "\n", 1)
    captured: list[str] = []
    namespace = {
        "__name__": "loom_stretch031_render_only",
        "__file__": str(paths["s013"]),
        "__package__": None,
        "__cached__": None,
        "__stretch031_collect_final_source": captured.append,
        "__stretch023_add_shared_persistence": modules["broken"].add_shared_persistence,
        "__stretch025_apply_batched_cleanup": modules["s025"].add_batched_cleanup,
        "__stretch026_apply_shared_batched_cleanup": modules["s026"].add_shared_batched_cleanup,
        "__stretch027_apply_single_pass_cleanup": s027.add_single_pass_cleanup,
        f"__stretch031_apply_geometry_{variant.lower()}": lambda source: add_geometry(source, variant),
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    namespace["main"]()
    if len(captured) != 1:
        raise RuntimeError(f"Stretch 031 Fix1 render failed: captured {len(captured)} final sources")
    source = captured[0]
    compile(source, str(repo / "scripts/stretch_four_token_kv_autoregressive_parity_009.py"), "exec")
    return source, phase


def source_facts(source: str, variant: str) -> dict[str, Any]:
    cfg = VARIANTS[variant]
    required = {
        "oracle_block_size": f"ORACLE_BLOCK_SIZE = {cfg['block_size']}",
        "oracle_block_count": f"ORACLE_BLOCK_COUNT = {cfg['block_count']}",
        "generated_tokens": "GENERATED_TOKENS = 10",
        "oracle_prefix": f"ORACLE_SEQUENCE = {TEN_TOKEN_ORACLE}",
        "h36": "HOTSET_LAYER_IDS = tuple(range(36))",
        "full_persistence": '"persistent_total_raw_weight_bytes": persistent_weight_bytes',
        "single_cleanup": '"policy": "single_cleanup_after_full_pass"',
        "runtime_lock": 'EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}',
        "classification": cfg["classification"],
    }
    missing = [name for name, fragment in required.items() if fragment not in source]
    forbidden = [
        fragment for fragment in [
            "ORACLE_BLOCK_SIZE = 4",
            "ORACLE_BLOCK_SIZE = 5" if variant == "M2" else "ORACLE_BLOCK_SIZE = 2",
            '"policy": "batched_once_after_36_layers"',
            "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        ] if fragment in source
    ]
    if missing or forbidden:
        raise RuntimeError(f"Stretch 031 Fix1 final-source invariant {variant} failed: missing={missing} forbidden={forbidden}")
    return {
        "variant": variant,
        "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "bytes": len(source.encode("utf-8")),
        "required_fragments": required,
        "missing": missing,
        "forbidden": forbidden,
    }


def normalize_geometry_only(source: str, from_variant: str, to_variant: str) -> str:
    left, right = VARIANTS[from_variant], VARIANTS[to_variant]
    replacements = [
        (f"ORACLE_BLOCK_SIZE = {left['block_size']}\n", f"ORACLE_BLOCK_SIZE = {right['block_size']}\n"),
        (f"ORACLE_BLOCK_COUNT = {left['block_count']}\n", f"ORACLE_BLOCK_COUNT = {right['block_count']}\n"),
        (left["classification"], right["classification"]),
        (left["terminal_title"], right["terminal_title"]),
        (left["summary_title"], right["summary_title"]),
        (left["run_directory"], right["run_directory"]),
    ]
    for old, new in replacements:
        source = replace_all(source, old, new, f"normalization {old!r}")
    return source


def child_interpreter_info(repo: Path) -> dict[str, Any]:
    path = repo / CANONICAL_CHILD_PYTHON
    if not path.is_file():
        raise RuntimeError(f"canonical MLX child interpreter missing: {path}")
    query = (
        "import importlib.metadata as m,json,sys; "
        "print(json.dumps({'executable':sys.executable,'prefix':sys.prefix,"
        "'versions':{k:m.version(k) for k in ('mlx','mlx-lm','transformers')}}))"
    )
    proc = subprocess.run([str(path), "-c", query], cwd=repo, text=True, capture_output=True, timeout=30, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"canonical child interpreter query failed: {proc.stderr.strip()}")
    info = json.loads(proc.stdout)
    if info.get("versions") != EXPECTED_RUNTIME:
        raise RuntimeError(f"canonical child runtime mismatch: {info.get('versions')} != {EXPECTED_RUNTIME}")
    return {"configured_path": str(path), "query": info}


def preflight(repo: Path, output_dir: Path | None = None) -> dict[str, Any]:
    sources: dict[str, str] = {}
    result: dict[str, Any] = {
        "experiment": "Stretch 031 Fix1 local generated-source preflight",
        "scientific_run": False,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "parent_interpreter": {"executable": sys.executable, "version": sys.version.split()[0]},
        "source_027_blob": git_blob(repo / SOURCE_027_PATH, repo),
        "variants": {},
    }
    for variant in ("M5", "M2"):
        source, phase = render_final_source(repo, variant)
        sources[variant] = source
        facts = source_facts(source, variant)
        result["variants"][variant] = {"facts": facts, "wrapper_phase": phase}
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            rendered = output_dir / f"rendered-{variant.lower()}-runtime.py"
            rendered.write_text(source, encoding="utf-8")
            result["variants"][variant]["rendered_source"] = str(rendered)
    result["child_interpreter"] = child_interpreter_info(repo)
    normalized_m5 = normalize_geometry_only(sources["M5"], "M5", "M2")
    if normalized_m5 != sources["M2"]:
        raise RuntimeError("Stretch 031 Fix1 single-factor invariant failed: normalized M5 source differs from M2")
    result["single_factor_diff"] = {
        "pass": True,
        "allowed_final_source_differences": [
            "ORACLE_BLOCK_SIZE 5 -> 2",
            "ORACLE_BLOCK_COUNT 2 -> 5",
            "variant classification/terminal title/summary title/run-directory identity",
        ],
        "same_oracle_prefix": TEN_TOKEN_ORACLE,
        "same_generated_tokens": 10,
    }
    result["classification"] = "STRETCH_031_FIX1_PREFLIGHT_PASS"
    if output_dir is not None:
        summary = output_dir / "preflight-summary.json"
        summary.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        result["summary"] = str(summary)
    return result


def default_preflight_dir(repo: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo / "results-local/stretch/single-pass-m2-m5-geometry-comparison-031-fix1/preflight" / stamp


def run_variant(variant: str, argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    repo = Path(__file__).resolve().parents[1]
    if argv and argv[0] in {"--preflight", "--render-only"}:
        out = default_preflight_dir(repo)
        result = preflight(repo, out)
        print(f"Classification: {result['classification']}")
        print(f"Variant requested: {variant}")
        print(f"Summary: {result['summary']}")
        return 0
    if argv and argv[0] != "--child":
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} [--preflight|--render-only|--child]")
    wrapper, _, paths, s027, modules = build_wrapper(repo, variant)
    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": modules["broken"].add_shared_persistence,
        "__stretch025_apply_batched_cleanup": modules["s025"].add_batched_cleanup,
        "__stretch026_apply_shared_batched_cleanup": modules["s026"].add_shared_batched_cleanup,
        "__stretch027_apply_single_pass_cleanup": s027.add_single_pass_cleanup,
        f"__stretch031_apply_geometry_{variant.lower()}": lambda source: add_geometry(source, variant),
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0
