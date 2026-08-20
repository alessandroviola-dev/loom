#!/usr/bin/env python3
"""LOOM Stretch 024 — profiled M5/H36/full-persistent target.

Instrumentation-only transform of the canonical Stretch 023 fix1 treatment.
The model, weights, M=5 oracle geometry, H36/full-weight residency, KV, parity,
I/O and resource gates remain frozen. Target transformer blocks are decomposed
with explicit MLX evaluation boundaries so component wall time can be measured.
Those boundaries deliberately perturb scheduling; this helper is for attribution,
not for claiming canonical uninstrumented throughput.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_FIX1_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py")
SOURCE_FIX1_BLOB = "120ad7be2f275559898bf636ca8e8fe039a56c60"
SOURCE_BROKEN_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py")
SOURCE_BROKEN_BLOB = "8c263e7be15441581e481e6f41cbd16f87d4df4b"
SOURCE_H36_PATH = Path("scripts/stretch_five_token_h36_hotset_variant_022.py")
SOURCE_H36_BLOB = "9111dde483206a774a9fe5426522dab6e77cecca"
SOURCE_017_PATH = Path("scripts/stretch_five_token_oracle_block_confirmation_017.py")
SOURCE_017_BLOB = "6171440736badf5150297f9c8945209fe49d0826"
SOURCE_013_PATH = Path("scripts/stretch_four_token_oracle_block_verification_013.py")
SOURCE_013_BLOB = "deeb0339294162f38cd4522d2890b6a0c728f96e"


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


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 024 attribution transform failed for {label}: "
            f"expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def inject_second_runtime_callback(wrapper_source: str) -> str:
    anchor = "    source = __stretch023_add_shared_persistence(source)\n"
    count = wrapper_source.count(anchor)
    if count != 1:
        raise RuntimeError(f"Stretch 024 wrapper callback anchor count={count}")
    return wrapper_source.replace(
        anchor,
        anchor + "    source = __stretch024_add_compute_attribution(source)\n",
        1,
    )


def add_compute_attribution(source: str) -> str:
    """Instrument the final generated full-persistent runtime only."""
    source = source.replace(
        "LOOM Stretch 023 — Five-Token H36 Full-Weight Persistent Variant",
        "LOOM Stretch 024 — Full-Persistent Compute Attribution PROFILED",
    )
    source = source.replace(
        "Stretch 023 — Five-Token H36 Full-Weight Persistent Variant",
        "Stretch 024 — Full-Persistent Compute Attribution PROFILED",
    )
    source = source.replace(
        "five-token-h36-full-persistent-023-full",
        "full-persistent-compute-attribution-024-profiled",
    )

    build_anchor = '''    def build_block(layer_id: int):\n        if layer_id in persistent_blocks:\n            return persistent_blocks[layer_id], None\n'''
    profiled_build = '''    _loom_profile_label = None\n    _loom_component_profiles = []\n\n    class ProfiledTransformerBlock(qwen3.TransformerBlock):\n        def __init__(self, block_args, layer_id):\n            super().__init__(block_args)\n            self._loom_layer_id = int(layer_id)\n\n        def __call__(self, x, mask=None, cache=None):\n            # Prompt remains on the canonical unprofiled path. Only the three\n            # M=5 oracle target blocks receive explicit evaluation boundaries.\n            if not str(_loom_profile_label or "").startswith("oracle_block_"):\n                return super().__call__(x, mask, cache)\n\n            rec = {\n                "pass_label": str(_loom_profile_label),\n                "layer_id": self._loom_layer_id,\n            }\n\n            def timed(name, fn):\n                started = time.perf_counter()\n                value = fn()\n                mx.eval(value)\n                rec[name] = time.perf_counter() - started\n                return value\n\n            n1 = timed("input_norm_seconds", lambda: self.input_layernorm(x))\n            attn = timed("attention_seconds", lambda: self.self_attn(n1, mask, cache))\n            h = timed("residual_1_seconds", lambda: x + attn)\n            n2 = timed("post_attention_norm_seconds", lambda: self.post_attention_layernorm(h))\n            gate = timed("gate_proj_seconds", lambda: self.mlp.gate_proj(n2))\n            up = timed("up_proj_seconds", lambda: self.mlp.up_proj(n2))\n            activated = timed("swiglu_seconds", lambda: qwen3.swiglu(gate, up))\n            down = timed("down_proj_seconds", lambda: self.mlp.down_proj(activated))\n            out = timed("residual_2_seconds", lambda: h + down)\n            rec["profiled_component_total_seconds"] = sum(\n                float(v) for k, v in rec.items() if k.endswith("_seconds")\n            )\n            _loom_component_profiles.append(rec)\n            return out\n\n    def build_block(layer_id: int):\n        if layer_id in persistent_blocks:\n            return persistent_blocks[layer_id], None\n'''
    source = replace_once(source, build_anchor, profiled_build, "profiled block class")
    source = replace_once(
        source,
        "        block = qwen3.TransformerBlock(args)\n",
        "        block = ProfiledTransformerBlock(args, layer_id)\n",
        "profiled block construction",
    )

    source = replace_once(
        source,
        '''    def run_streamed_pass(ids, caches, label: str):\n        pass_started = time.perf_counter()\n''',
        '''    def run_streamed_pass(ids, caches, label: str):\n        nonlocal _loom_profile_label\n        _loom_profile_label = label\n        pass_started = time.perf_counter()\n''',
        "profile label",
    )

    source = replace_once(
        source,
        '''            pre_active = int(mx.get_active_memory())\n            pre_cache = cache_snapshot(caches)\n            io_before_build = rusage_snapshot()\n            block, selected = build_block(layer_id)\n            io_after_build = rusage_snapshot()\n''',
        '''            pre_active = int(mx.get_active_memory())\n            pre_cache = cache_snapshot(caches)\n            io_before_build = rusage_snapshot()\n            build_wall_started = time.perf_counter()\n            block, selected = build_block(layer_id)\n            build_wall = time.perf_counter() - build_wall_started\n            io_after_build = rusage_snapshot()\n''',
        "layer build wall",
    )
    source = replace_once(
        source,
        '''            old_h = h\n            h = out\n            del old_h, block, selected\n            gc.collect()\n            mx.clear_cache()\n            gc.collect()\n            post_clear_active = int(mx.get_active_memory())\n''',
        '''            old_h = h\n            h = out\n            cleanup_started = time.perf_counter()\n            del old_h, block, selected\n            gc.collect()\n            mx.clear_cache()\n            gc.collect()\n            cleanup_wall = time.perf_counter() - cleanup_started\n            post_clear_active = int(mx.get_active_memory())\n''',
        "layer cleanup wall",
    )
    source = replace_once(
        source,
        '''                "materialize_wall_seconds": round(materialize_wall, 6),\n                "forward_wall_seconds": round(forward_wall, 6),\n''',
        '''                "materialize_wall_seconds": round(materialize_wall, 6),\n                "forward_wall_seconds": round(forward_wall, 6),\n                "build_reuse_wall_seconds": round(build_wall, 6),\n                "cleanup_wall_seconds": round(cleanup_wall, 6),\n''',
        "cycle attribution walls",
    )

    source = replace_once(
        source,
        '        "shared_persistence": shared_persistence_record,\n',
        '        "shared_persistence": shared_persistence_record,\n        "component_profiles": _loom_component_profiles,\n',
        "child profile payload",
    )
    source = replace_once(
        source,
        '        "resident", "stream", "hotset", "shared_persistence", "oracle_sequence_provenance",\n',
        '        "resident", "stream", "hotset", "shared_persistence", "component_profiles", "oracle_sequence_provenance",\n',
        "parent profile promotion",
    )

    classification_anchor = '    summary["classification"] = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"\n'
    attribution = '''    try:\n        component_names = [\n            "input_norm_seconds",\n            "attention_seconds",\n            "residual_1_seconds",\n            "post_attention_norm_seconds",\n            "gate_proj_seconds",\n            "up_proj_seconds",\n            "swiglu_seconds",\n            "down_proj_seconds",\n            "residual_2_seconds",\n        ]\n        profiles = [\n            p for p in child.get("component_profiles", [])\n            if str(p.get("pass_label", "")).startswith("oracle_block_")\n        ]\n        expected_profile_count = ORACLE_BLOCK_COUNT * args.num_hidden_layers\n        if len(profiles) != expected_profile_count:\n            raise RuntimeError(\n                f"expected {expected_profile_count} target layer profiles, got {len(profiles)}"\n            )\n\n        block_totals = []\n        layer_accum = {layer_id: [] for layer_id in range(args.num_hidden_layers)}\n        for block_index in range(1, ORACLE_BLOCK_COUNT + 1):\n            label = f"oracle_block_{block_index}"\n            rows = [p for p in profiles if p.get("pass_label") == label]\n            ids = sorted(int(p.get("layer_id", -1)) for p in rows)\n            if ids != list(range(args.num_hidden_layers)):\n                raise RuntimeError(f"{label}: invalid profiled layer ids {ids}")\n            totals = {name: sum(float(p[name]) for p in rows) for name in component_names}\n            totals["attention_path_seconds"] = (\n                totals["input_norm_seconds"]\n                + totals["attention_seconds"]\n                + totals["residual_1_seconds"]\n            )\n            totals["mlp_path_seconds"] = (\n                totals["post_attention_norm_seconds"]\n                + totals["gate_proj_seconds"]\n                + totals["up_proj_seconds"]\n                + totals["swiglu_seconds"]\n                + totals["down_proj_seconds"]\n                + totals["residual_2_seconds"]\n            )\n            totals["profiled_transformer_compute_seconds"] = (\n                totals["attention_path_seconds"] + totals["mlp_path_seconds"]\n            )\n            totals["block"] = block_index\n            block_totals.append(totals)\n            for p in rows:\n                layer_accum[int(p["layer_id"])].append(\n                    sum(float(p[name]) for name in component_names)\n                )\n\n        component_means = {\n            name: statistics.mean(float(row[name]) for row in block_totals)\n            for name in component_names\n        }\n        layer_means = [\n            {"layer_id": layer_id, "mean_profiled_compute_seconds": statistics.mean(values)}\n            for layer_id, values in layer_accum.items()\n        ]\n        layer_means.sort(key=lambda row: row["mean_profiled_compute_seconds"], reverse=True)\n        summary["compute_attribution"] = {\n            "instrumentation": "explicit mx.eval boundary after each profiled component",\n            "throughput_comparability": "PROFILED wall is intentionally perturbed; use balanced control for perturbation",\n            "profiled_target_layer_records": len(profiles),\n            "component_names": component_names,\n            "block_totals": block_totals,\n            "mean_component_seconds_per_target_block": component_means,\n            "mean_attention_path_seconds_per_target_block": statistics.mean(\n                row["attention_path_seconds"] for row in block_totals\n            ),\n            "mean_mlp_path_seconds_per_target_block": statistics.mean(\n                row["mlp_path_seconds"] for row in block_totals\n            ),\n            "mean_profiled_transformer_compute_seconds_per_target_block": statistics.mean(\n                row["profiled_transformer_compute_seconds"] for row in block_totals\n            ),\n            "slowest_layers_by_mean_profiled_compute": layer_means[:8],\n        }\n    except Exception as exc:\n        summary["classification"] = "COMPUTE_ATTRIBUTION_TELEMETRY_FAIL"\n        summary["failure_reason"] = f"compute attribution incomplete: {type(exc).__name__}: {exc}"\n        return finish(12)\n\n    summary["classification"] = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"\n'''
    source = replace_once(source, classification_anchor, attribution, "compute attribution summary")

    source = replace_once(
        source,
        '        print(f"Minimum observed free memory: {summary[\'telemetry\'].get(\'min_memory_free_percent\')}%")\n',
        '''        if summary.get("compute_attribution"):\n            ca = summary["compute_attribution"]\n            print(f"Profiled transformer compute/block: {ca.get('mean_profiled_transformer_compute_seconds_per_target_block')} s")\n            print(f"Profiled attention path/block: {ca.get('mean_attention_path_seconds_per_target_block')} s")\n            print(f"Profiled MLP path/block: {ca.get('mean_mlp_path_seconds_per_target_block')} s")\n            print(f"Mean component seconds/block: {ca.get('mean_component_seconds_per_target_block')}")\n            print(f"Slowest profiled layers: {ca.get('slowest_layers_by_mean_profiled_compute')}")\n        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")\n''',
        "compute attribution display",
    )

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    paths = {
        "fix1": repo / SOURCE_FIX1_PATH,
        "broken": repo / SOURCE_BROKEN_PATH,
        "h36": repo / SOURCE_H36_PATH,
        "s017": repo / SOURCE_017_PATH,
        "s013": repo / SOURCE_013_PATH,
    }
    observed = {key: git_blob(path, repo) for key, path in paths.items()}
    expected = {
        "fix1": SOURCE_FIX1_BLOB,
        "broken": SOURCE_BROKEN_BLOB,
        "h36": SOURCE_H36_BLOB,
        "s017": SOURCE_017_BLOB,
        "s013": SOURCE_013_BLOB,
    }

    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"
    if not is_child:
        print("LOOM Stretch 024 — Full-Persistent Compute Attribution PROFILED")
        for key in ["fix1", "broken", "h36", "s017", "s013"]:
            print(f"{key} blob: {observed[key]}")
    if observed != expected:
        print(f"Source provenance: FAIL observed={observed} expected={expected}", file=sys.stderr)
        return 2
    if not is_child:
        print("Source provenance: PASS")
        print("Scientific architecture: M=5 + H36 + full raw-weight persistence UNCHANGED")
        print("Instrumentation factor: explicit target-component evaluation boundaries ONLY")
        print("Profiled throughput is not a canonical speed result")

    fix1 = load_module(paths["fix1"], "loom_stretch023_fix1_for_024")
    broken = load_module(paths["broken"], "loom_stretch023_broken_for_024")
    h36 = load_module(paths["h36"], "loom_stretch022_h36_for_024")
    s017 = load_module(paths["s017"], "loom_stretch017_for_024")

    wrapper = h36.transformed_013_wrapper(paths["s013"].read_text(encoding="utf-8"), s017)
    wrapper = fix1.inject_runtime_callback(wrapper)
    wrapper = inject_second_runtime_callback(wrapper)

    required = [
        "__stretch023_add_shared_persistence(source)",
        "__stretch024_add_compute_attribution(source)",
        "ORACLE_BLOCK_SIZE = 5",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 024 wrapper invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
        "__stretch024_add_compute_attribution": add_compute_attribution,
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
