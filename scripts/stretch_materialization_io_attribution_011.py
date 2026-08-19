#!/usr/bin/env python3
"""LOOM Stretch 011 — instrumentation-only materialization I/O attribution.

Reuses the exact frozen Stretch 010 transformed scientific workload and adds
Darwin proc_pid_rusage(RUSAGE_INFO_V2) snapshots around weight selection and
materialization. No model/cache/generation/safety policy changes.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_009_BLOB = "3e0780850bb65f9dccf07946f89597fa2e4d17e1"
SOURCE_010_BLOB = "ff3dc83abc6388113fca15594eef6b3ec00ebe50"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_exact(text: str, old: str, new: str, expected_count: int, label: str) -> str:
    observed = text.count(old)
    if observed != expected_count:
        raise RuntimeError(
            f"instrumentation transform failed for {label}: expected {expected_count} occurrence(s), found {observed}"
        )
    return text.replace(old, new)


def add_io_instrumentation(source: str) -> str:
    # Rename the inherited 010 experiment only; scientific workload stays exact.
    source = replace_exact(
        source,
        'print("LOOM Stretch 010 — Sixteen-Token Autoregressive Stability")',
        'print("LOOM Stretch 011 — Materialization I/O Attribution")',
        1,
        "terminal title",
    )
    source = replace_exact(
        source,
        '"experiment": "Stretch 010 — Sixteen-Token Autoregressive Stability",',
        '"experiment": "Stretch 011 — Materialization I/O Attribution",',
        1,
        "summary title",
    )
    source = replace_exact(
        source,
        '"sixteen-token-autoregressive-stability-010"',
        '"materialization-io-attribution-011"',
        1,
        "run directory",
    )

    source = replace_exact(
        source,
        "import gc\n",
        "import gc\nimport ctypes\nimport os\n",
        1,
        "ctypes/os imports",
    )

    source = replace_exact(
        source,
        '    quant = config["quantization"]\n\n    def mem() -> dict:\n',
        '''    quant = config["quantization"]\n\n    class RUsageInfoV2(ctypes.Structure):\n        _fields_ = [\n            ("ri_uuid", ctypes.c_uint8 * 16),\n            ("ri_user_time", ctypes.c_uint64),\n            ("ri_system_time", ctypes.c_uint64),\n            ("ri_pkg_idle_wkups", ctypes.c_uint64),\n            ("ri_interrupt_wkups", ctypes.c_uint64),\n            ("ri_pageins", ctypes.c_uint64),\n            ("ri_wired_size", ctypes.c_uint64),\n            ("ri_resident_size", ctypes.c_uint64),\n            ("ri_phys_footprint", ctypes.c_uint64),\n            ("ri_proc_start_abstime", ctypes.c_uint64),\n            ("ri_proc_exit_abstime", ctypes.c_uint64),\n            ("ri_child_user_time", ctypes.c_uint64),\n            ("ri_child_system_time", ctypes.c_uint64),\n            ("ri_child_pkg_idle_wkups", ctypes.c_uint64),\n            ("ri_child_interrupt_wkups", ctypes.c_uint64),\n            ("ri_child_pageins", ctypes.c_uint64),\n            ("ri_child_elapsed_abstime", ctypes.c_uint64),\n            ("ri_diskio_bytesread", ctypes.c_uint64),\n            ("ri_diskio_byteswritten", ctypes.c_uint64),\n        ]\n\n    try:\n        _libproc = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)\n        _proc_pid_rusage = _libproc.proc_pid_rusage\n        _proc_pid_rusage.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]\n        _proc_pid_rusage.restype = ctypes.c_int\n    except Exception as exc:\n        raise RuntimeError(f"proc_pid_rusage telemetry unavailable: {type(exc).__name__}: {exc}")\n\n    def rusage_snapshot() -> dict:\n        info = RUsageInfoV2()\n        rc = _proc_pid_rusage(os.getpid(), 2, ctypes.byref(info))\n        if rc != 0:\n            err = ctypes.get_errno()\n            raise RuntimeError(f"proc_pid_rusage telemetry unavailable: rc={rc} errno={err}")\n        return {\n            "pageins": int(info.ri_pageins),\n            "resident_size": int(info.ri_resident_size),\n            "phys_footprint": int(info.ri_phys_footprint),\n            "disk_read_bytes": int(info.ri_diskio_bytesread),\n            "disk_written_bytes": int(info.ri_diskio_byteswritten),\n        }\n\n    def rusage_delta(before: dict, after: dict) -> dict:\n        return {key: int(after[key]) - int(before[key]) for key in before}\n\n    def mem() -> dict:\n''',
        1,
        "Darwin rusage helper",
    )

    source = replace_exact(
        source,
        '        stage_records: dict[str, dict] = {}\n\n        # Embedding.\n',
        '        stage_records: dict[str, dict] = {}\n        pass_io_start = rusage_snapshot()\n\n        # Embedding.\n',
        1,
        "pass I/O start",
    )

    # Embedding selection/materialization instrumentation.
    source = replace_exact(
        source,
        '        embed_pre_active = int(mx.get_active_memory())\n        embed_selected = select_weights("model.embed_tokens.", "model.")\n',
        '        embed_pre_active = int(mx.get_active_memory())\n        embed_io_before_select = rusage_snapshot()\n        embed_selected = select_weights("model.embed_tokens.", "model.")\n        embed_io_after_select = rusage_snapshot()\n',
        1,
        "embedding select I/O",
    )
    source = replace_exact(
        source,
        '        mx.eval(embed_stage.parameters())\n        embed_materialize_wall = time.perf_counter() - started\n',
        '        mx.eval(embed_stage.parameters())\n        embed_materialize_wall = time.perf_counter() - started\n        embed_io_after_materialize = rusage_snapshot()\n',
        1,
        "embedding materialize I/O",
    )
    source = replace_exact(
        source,
        '        save_state(f"stream_{label}_embedding_complete", stage=stage_records["embedding"], cache=cache_snapshot(caches))\n',
        '        stage_records["embedding"]["io_select_delta"] = rusage_delta(embed_io_before_select, embed_io_after_select)\n        stage_records["embedding"]["io_materialize_delta"] = rusage_delta(embed_io_after_select, embed_io_after_materialize)\n        save_state(f"stream_{label}_embedding_complete", stage=stage_records["embedding"], cache=cache_snapshot(caches))\n',
        1,
        "embedding I/O record",
    )

    # Per-transformer-layer selection/materialization instrumentation.
    source = replace_exact(
        source,
        '            pre_active = int(mx.get_active_memory())\n            pre_cache = cache_snapshot(caches)\n            block, selected = build_block(layer_id)\n            pre_eval_active = int(mx.get_active_memory())\n',
        '            pre_active = int(mx.get_active_memory())\n            pre_cache = cache_snapshot(caches)\n            io_before_build = rusage_snapshot()\n            block, selected = build_block(layer_id)\n            io_after_build = rusage_snapshot()\n            pre_eval_active = int(mx.get_active_memory())\n',
        1,
        "layer build I/O",
    )
    source = replace_exact(
        source,
        '            mx.eval(block.parameters())\n            materialize_wall = time.perf_counter() - started\n',
        '            mx.eval(block.parameters())\n            materialize_wall = time.perf_counter() - started\n            io_after_materialize = rusage_snapshot()\n',
        1,
        "layer materialize I/O",
    )
    source = replace_exact(
        source,
        '            cycles.append(cycle)\n',
        '            cycle["io_build_delta"] = rusage_delta(io_before_build, io_after_build)\n            cycle["io_materialize_delta"] = rusage_delta(io_after_build, io_after_materialize)\n            cycles.append(cycle)\n',
        1,
        "layer I/O record",
    )

    # Final norm selection/materialization instrumentation.
    source = replace_exact(
        source,
        '        norm_pre_active = int(mx.get_active_memory())\n        norm_selected = select_weights("model.norm.", "model.")\n',
        '        norm_pre_active = int(mx.get_active_memory())\n        norm_io_before_select = rusage_snapshot()\n        norm_selected = select_weights("model.norm.", "model.")\n        norm_io_after_select = rusage_snapshot()\n',
        1,
        "norm select I/O",
    )
    source = replace_exact(
        source,
        '        mx.eval(norm_stage.parameters())\n        norm_materialize_wall = time.perf_counter() - started\n',
        '        mx.eval(norm_stage.parameters())\n        norm_materialize_wall = time.perf_counter() - started\n        norm_io_after_materialize = rusage_snapshot()\n',
        1,
        "norm materialize I/O",
    )
    source = replace_exact(
        source,
        '        save_state(f"stream_{label}_norm_complete", stage=stage_records["norm"], cache=cache_snapshot(caches))\n',
        '        stage_records["norm"]["io_select_delta"] = rusage_delta(norm_io_before_select, norm_io_after_select)\n        stage_records["norm"]["io_materialize_delta"] = rusage_delta(norm_io_after_select, norm_io_after_materialize)\n        save_state(f"stream_{label}_norm_complete", stage=stage_records["norm"], cache=cache_snapshot(caches))\n',
        1,
        "norm I/O record",
    )

    # LM-head selection/materialization instrumentation.
    source = replace_exact(
        source,
        '        head_pre_active = int(mx.get_active_memory())\n        head_selected = select_weights("lm_head.")\n',
        '        head_pre_active = int(mx.get_active_memory())\n        head_io_before_select = rusage_snapshot()\n        head_selected = select_weights("lm_head.")\n        head_io_after_select = rusage_snapshot()\n',
        1,
        "head select I/O",
    )
    source = replace_exact(
        source,
        '        mx.eval(head_stage.parameters())\n        head_materialize_wall = time.perf_counter() - started\n',
        '        mx.eval(head_stage.parameters())\n        head_materialize_wall = time.perf_counter() - started\n        head_io_after_materialize = rusage_snapshot()\n',
        1,
        "head materialize I/O",
    )
    source = replace_exact(
        source,
        '        save_state(f"stream_{label}_head_complete", stage=stage_records["head"], cache=cache_snapshot(caches))\n',
        '        stage_records["head"]["io_select_delta"] = rusage_delta(head_io_before_select, head_io_after_select)\n        stage_records["head"]["io_materialize_delta"] = rusage_delta(head_io_after_select, head_io_after_materialize)\n        save_state(f"stream_{label}_head_complete", stage=stage_records["head"], cache=cache_snapshot(caches))\n',
        1,
        "head I/O record",
    )

    source = replace_exact(
        source,
        '        return logits, {\n',
        '        pass_io_end = rusage_snapshot()\n        return logits, {\n',
        1,
        "pass I/O end",
    )
    source = replace_exact(
        source,
        '            "total_pass_wall_seconds": round(time.perf_counter() - pass_started, 6),\n',
        '            "total_pass_wall_seconds": round(time.perf_counter() - pass_started, 6),\n            "io_start": pass_io_start,\n            "io_end": pass_io_end,\n            "io_delta": rusage_delta(pass_io_start, pass_io_end),\n',
        1,
        "pass I/O summary",
    )

    # Classify a libproc/API failure separately from the scientific workload.
    source = replace_exact(
        source,
        '''    if proc.returncode != 0:\n        summary["classification"] = "RUNTIME_FAIL"\n        summary["failure_reason"] = f"child exited {proc.returncode}; final={child!r}; state={helpers.read_json(state_path)!r}"\n        return finish(6)\n''',
        '''    if proc.returncode != 0:\n        child_error = child.get("error", "") if isinstance(child, dict) else ""\n        if "proc_pid_rusage telemetry unavailable" in child_error:\n            summary["classification"] = "IO_TELEMETRY_PREFLIGHT_FAIL"\n        else:\n            summary["classification"] = "RUNTIME_FAIL"\n        summary["failure_reason"] = f"child exited {proc.returncode}; final={child!r}; state={helpers.read_json(state_path)!r}"\n        return finish(6)\n''',
        1,
        "I/O telemetry failure classification",
    )

    # Promote per-layer/pass I/O deltas into a compact token-level attribution summary.
    source = replace_exact(
        source,
        '    summary["classification"] = "SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS"\n',
        '''    try:\n        token_passes = [record["pass"] for record in child["stream"]["tokens"]]\n        materialize_disk_reads = [\n            sum(int(cycle["io_materialize_delta"]["disk_read_bytes"]) for cycle in record["cycles"])\n            for record in token_passes\n        ]\n        materialize_pageins = [\n            sum(int(cycle["io_materialize_delta"]["pageins"]) for cycle in record["cycles"])\n            for record in token_passes\n        ]\n        build_disk_reads = [\n            sum(int(cycle["io_build_delta"]["disk_read_bytes"]) for cycle in record["cycles"])\n            for record in token_passes\n        ]\n        build_pageins = [\n            sum(int(cycle["io_build_delta"]["pageins"]) for cycle in record["cycles"])\n            for record in token_passes\n        ]\n        full_pass_disk_reads = [int(record["io_delta"]["disk_read_bytes"]) for record in token_passes]\n        full_pass_pageins = [int(record["io_delta"]["pageins"]) for record in token_passes]\n        if not all(len(record.get("cycles", [])) == 36 for record in token_passes):\n            raise RuntimeError("incomplete layer I/O records")\n\n        def pearson(xs, ys):\n            if len(xs) != len(ys) or len(xs) < 2:\n                return None\n            mxv = statistics.mean(xs)\n            myv = statistics.mean(ys)\n            num = sum((x - mxv) * (y - myv) for x, y in zip(xs, ys))\n            dx = sum((x - mxv) ** 2 for x in xs)\n            dy = sum((y - myv) ** 2 for y in ys)\n            if dx <= 0 or dy <= 0:\n                return None\n            return num / ((dx * dy) ** 0.5)\n\n        summary["io_attribution"] = {\n            "darwin_api": "proc_pid_rusage/RUSAGE_INFO_V2",\n            "materialize_disk_read_bytes": materialize_disk_reads,\n            "materialize_pageins": materialize_pageins,\n            "build_select_disk_read_bytes": build_disk_reads,\n            "build_select_pageins": build_pageins,\n            "full_pass_disk_read_bytes": full_pass_disk_reads,\n            "full_pass_pageins": full_pass_pageins,\n            "early_tokens_1_4": {\n                "mean_materialize_seconds": statistics.mean(materialize_times[:4]),\n                "mean_materialize_disk_read_bytes": statistics.mean(materialize_disk_reads[:4]),\n                "mean_materialize_pageins": statistics.mean(materialize_pageins[:4]),\n                "mean_full_pass_disk_read_bytes": statistics.mean(full_pass_disk_reads[:4]),\n            },\n            "late_tokens_8_16": {\n                "mean_materialize_seconds": statistics.mean(materialize_times[7:16]),\n                "mean_materialize_disk_read_bytes": statistics.mean(materialize_disk_reads[7:16]),\n                "mean_materialize_pageins": statistics.mean(materialize_pageins[7:16]),\n                "mean_full_pass_disk_read_bytes": statistics.mean(full_pass_disk_reads[7:16]),\n            },\n            "materialize_time_vs_disk_read_pearson": pearson(materialize_times, materialize_disk_reads),\n            "materialize_time_vs_pageins_pearson": pearson(materialize_times, materialize_pageins),\n        }\n    except Exception as exc:\n        summary["classification"] = "TELEMETRY_FAIL"\n        summary["failure_reason"] = f"incomplete materialization I/O attribution: {type(exc).__name__}: {exc}"\n        return finish(11)\n\n    summary["classification"] = "MATERIALIZATION_IO_ATTRIBUTION_PASS"\n''',
        1,
        "token-level I/O attribution",
    )

    source = replace_exact(
        source,
        '        print(f"Minimum observed free memory: {summary[\'telemetry\'].get(\'min_memory_free_percent\')}%")\n',
        '''        if summary.get("io_attribution"):\n            ioa = summary["io_attribution"]\n            print(f"Materialize disk-read bytes/token: {ioa.get('materialize_disk_read_bytes')}")\n            print(f"Materialize pageins/token: {ioa.get('materialize_pageins')}")\n            print(f"Build/select disk-read bytes/token: {ioa.get('build_select_disk_read_bytes')}")\n            print(f"Full-pass disk-read bytes/token: {ioa.get('full_pass_disk_read_bytes')}")\n            print(f"Early token I/O means: {ioa.get('early_tokens_1_4')}")\n            print(f"Late token I/O means: {ioa.get('late_tokens_8_16')}")\n            print(f"Materialize-time/disk-read Pearson: {ioa.get('materialize_time_vs_disk_read_pearson')}")\n            print(f"Materialize-time/pageins Pearson: {ioa.get('materialize_time_vs_pageins_pearson')}")\n        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")\n''',
        1,
        "I/O attribution display",
    )

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source009 = repo / "scripts" / "stretch_four_token_kv_autoregressive_parity_009.py"
    source010 = repo / "scripts" / "stretch_sixteen_token_autoregressive_stability_010.py"
    observed009 = git_blob(source009, repo)
    observed010 = git_blob(source010, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 011 — Materialization I/O Attribution frozen instrumentation")
        print(f"Stretch 009 source blob: {observed009}")
        print(f"Stretch 010 transform blob: {observed010}")
    if observed009 != SOURCE_009_BLOB or observed010 != SOURCE_010_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    if not is_child:
        print("Source provenance: PASS")

    transform010 = load_module(source010, "loom_stretch010_transform")
    source = transform010.transformed_source(source009.read_text(encoding="utf-8"))
    source = add_io_instrumentation(source)

    required_fragments = [
        'GENERATED_TOKENS = 16',
        'MATERIALIZATION_IO_ATTRIBUTION_PASS',
        'proc_pid_rusage',
        'ri_diskio_bytesread',
        'io_materialize_delta',
        'stdout=out_handle',
        'stderr=err_handle',
        'MIN_FREE_PERCENT = 5',
        'MAX_SWAP_MB = 5600.0',
    ]
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise RuntimeError(f"instrumented-source invariant failed; missing {missing}")

    if not is_child:
        print("Frozen Stretch 010 workload transform: PASS")
        print("Scientific workload: UNCHANGED")
        print("New instrumentation: Darwin proc_pid_rusage V2 around weight selection/materialization")
        print("OS cache purge: NONE")
        print("Model/KV/parity/safety gates: UNCHANGED")

    transformed_globals = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
    }
    exec(compile(source, str(source009), "exec"), transformed_globals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
