#!/usr/bin/env python3
"""LOOM Stretch 016 — quantized-linear M-boundary mapping.

Maps the first M in 1..16 where the actual frozen layer-0 quantized projections
stop reproducing the M=1 first-row output. No runtime/model/quantization change.
"""
from __future__ import annotations

import importlib.util
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SOURCE_015_BLOB = "933c366220625e845e788b2ab1521ae78d9e7d15"
SOURCE_002_BLOB = "e7bd6bf4c61b44664c0c8421bf230b938509e4ef"
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
EXPECTED_QUANTIZATION = {"group_size": 64, "bits": 3}
EXPECTED_LAYER_BYTES = 84_427_264
EXPECTED_LAYER_TENSORS = 25
EXPECTED_EMBED_BYTES = 272_269_312
HOST_GATE_FREE_PERCENT = 60
HOST_GATE_SAMPLES = 3
MAX_SWAP_MB = 5600.0
M_VALUES = list(range(1, 17))
ORACLE_SEQUENCE_16 = [1, 374, 264, 4647, 1483, 304, 279, 1809, 315, 5994, 320, 1654, 23740, 285, 8, 311]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def child_main(argv: list[str]) -> int:
    import gc

    import mlx.core as mx
    import mlx.nn as nn
    from mlx_lm.models import qwen3

    model_dir = Path(argv[0])
    weight_path = Path(argv[1])
    config_path = Path(argv[2])
    output_path = Path(argv[3])

    config = json.loads(config_path.read_text(encoding="utf-8"))
    args = qwen3.ModelArgs.from_dict(config)
    quant = config["quantization"]

    def select_weights(prefix: str, strip_prefix: str = "") -> dict:
        all_weights = mx.load(str(weight_path))
        selected = {}
        for name, value in all_weights.items():
            if name.startswith(prefix):
                local_name = name[len(strip_prefix):] if strip_prefix else name
                selected[local_name] = value
        del all_weights
        gc.collect()
        return selected

    def selected_bytes(selected: dict) -> int:
        return sum(int(v.nbytes) for v in selected.values())

    def quantize_and_load(module, selected: dict):
        def class_predicate(path, leaf):
            return hasattr(leaf, "to_quantized") and f"{path}.scales" in selected

        nn.quantize(
            module,
            group_size=quant["group_size"],
            bits=quant["bits"],
            mode=quant.get("mode", "affine"),
            class_predicate=class_predicate,
        )
        module.load_weights(list(selected.items()), strict=True)
        module.eval()
        return module

    class EmbeddingStage(nn.Module):
        def __init__(self):
            super().__init__()
            self.embed_tokens = nn.Embedding(args.vocab_size, args.hidden_size)

        def __call__(self, ids):
            return self.embed_tokens(ids)

    def build_block(layer_id: int):
        marker = f"model.layers.{layer_id}."
        selected = select_weights(marker, marker)
        if len(selected) != EXPECTED_LAYER_TENSORS:
            raise RuntimeError(
                f"layer {layer_id} tensor count {len(selected)} != {EXPECTED_LAYER_TENSORS}"
            )
        if selected_bytes(selected) != EXPECTED_LAYER_BYTES:
            raise RuntimeError(
                f"layer {layer_id} selected bytes {selected_bytes(selected)} != {EXPECTED_LAYER_BYTES}"
            )
        block = qwen3.TransformerBlock(args)
        quantize_and_load(block, selected)
        mx.eval(block.parameters())
        return block, selected

    def first_row_vector(arr):
        view = arr[:, 0:1, ...]
        out = (view + mx.zeros_like(view)).astype(mx.float32).reshape(-1)
        mx.eval(out)
        return out

    def diff_metrics(reference, candidate) -> dict:
        diff = mx.abs(reference - candidate)
        mx.eval(diff)
        max_abs = float(mx.max(diff).item())
        mean_abs = float(mx.mean(diff).item())
        return {
            "exact": max_abs == 0.0,
            "max_abs_diff": max_abs,
            "mean_abs_diff": mean_abs,
            "elements": int(reference.size),
        }

    started = time.perf_counter()

    embed_selected = select_weights("model.embed_tokens.", "model.")
    if selected_bytes(embed_selected) != EXPECTED_EMBED_BYTES:
        raise RuntimeError(
            f"embedding bytes {selected_bytes(embed_selected)} != {EXPECTED_EMBED_BYTES}"
        )
    embed_stage = EmbeddingStage()
    quantize_and_load(embed_stage, embed_selected)
    mx.eval(embed_stage.parameters())
    ids = mx.array([ORACLE_SEQUENCE_16], dtype=mx.int32)
    embedded = embed_stage(ids)
    mx.eval(embedded)
    del ids, embed_stage, embed_selected
    gc.collect()
    mx.clear_cache()

    block, block_selected = build_block(0)

    # Construct each probe once; slicing changes M but never changes first-row bits.
    hidden_probe16 = block.input_layernorm(embedded)
    mx.eval(hidden_probe16)

    intermediate_total = len(M_VALUES) * args.intermediate_size
    down_probe16 = (
        ((mx.arange(intermediate_total, dtype=mx.int32) % 257).astype(mx.float32) - 128.0)
        / 64.0
    ).reshape(1, len(M_VALUES), args.intermediate_size).astype(mx.bfloat16)
    mx.eval(down_probe16)

    modules = {
        "q_proj": (block.self_attn.q_proj, hidden_probe16),
        "k_proj": (block.self_attn.k_proj, hidden_probe16),
        "v_proj": (block.self_attn.v_proj, hidden_probe16),
        "o_proj": (block.self_attn.o_proj, hidden_probe16),
        "gate_proj": (block.mlp.gate_proj, hidden_probe16),
        "up_proj": (block.mlp.up_proj, hidden_probe16),
        "down_proj": (block.mlp.down_proj, down_probe16),
    }

    projection_results = {}
    for name, (module, probe) in modules.items():
        reference_out = module(probe[:, :1, :])
        reference = first_row_vector(reference_out)
        del reference_out

        rows = []
        first_divergent_m = None
        first_divergence = None
        largest_exact_m_before_divergence = 1

        for m in M_VALUES:
            out = module(probe[:, :m, :])
            candidate = first_row_vector(out)
            metrics = diff_metrics(reference, candidate)
            row = {"m": m, **metrics}
            rows.append(row)
            if metrics["exact"] and first_divergent_m is None:
                largest_exact_m_before_divergence = m
            if not metrics["exact"] and first_divergent_m is None:
                first_divergent_m = m
                first_divergence = row
            del out, candidate

        projection_results[name] = {
            "largest_exact_m_before_divergence": largest_exact_m_before_divergence,
            "first_divergent_m": first_divergent_m,
            "first_divergence": first_divergence,
            "rows": rows,
        }

    mapped = [
        name
        for name in ("gate_proj", "up_proj", "down_proj")
        if projection_results[name]["first_divergent_m"] is not None
    ]
    classification = (
        "QUANTIZED_LINEAR_M_BOUNDARY_MAPPED"
        if mapped
        else "QUANTIZED_LINEAR_M_BOUNDARY_NOT_FOUND_1_TO_16"
    )

    final = {
        "experiment": "Stretch 016 — QuantizedLinear M-Boundary Mapping",
        "classification": classification,
        "m_values": M_VALUES,
        "quantization": quant,
        "layer": 0,
        "oracle_sequence_16": ORACLE_SEQUENCE_16,
        "projection_results": projection_results,
        "mapped_mlp_projections": mapped,
        "peak_mlx_memory_bytes": int(mx.get_peak_memory()),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }
    output_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Classification: {classification}")
    for name, result in projection_results.items():
        print(
            f"{name}: largest_exact_before_divergence="
            f"{result['largest_exact_m_before_divergence']} "
            f"first_divergent_m={result['first_divergent_m']}"
        )
        if result["first_divergence"] is not None:
            d = result["first_divergence"]
            print(
                f"  first divergence: M={d['m']} max_abs={d['max_abs_diff']} "
                f"mean_abs={d['mean_abs_diff']}"
            )
    print(f"Peak MLX memory: {final['peak_mlx_memory_bytes']} B")
    print(f"Child summary: {output_path}")

    del block, block_selected, embedded, hidden_probe16, down_probe16
    gc.collect()
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        return child_main(sys.argv[2:])

    repo = Path(__file__).resolve().parents[1]
    source015 = repo / "scripts" / "stretch_eight_token_divergence_attribution_015.py"
    source002 = repo / "scripts" / "stretch_single_layer_mlx_materialization_002.py"
    observed015 = git_blob(source015, repo)
    observed002 = git_blob(source002, repo)

    print("LOOM Stretch 016 — QuantizedLinear M-Boundary Mapping")
    print(f"Stretch 015 runner blob: {observed015}")
    print(f"Stretch 002 helper blob: {observed002}")
    if observed015 != SOURCE_015_BLOB or observed002 != SOURCE_002_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Scientific question: map exact M=1..16 shape-dependence boundary")
    print("Frozen runtime/model/quantization: UNCHANGED")
    print("MLX upgrade / strict mode / threshold relaxation: NONE")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        print(
            f"PREFLIGHT_FAIL: requires Darwin arm64, got {platform.system()} {platform.machine()}",
            file=sys.stderr,
        )
        return 2

    helpers = load_module(source002, "loom_stretch002_helpers_016")
    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight = model_dir / "model.safetensors"
    config_path = model_dir / "config.json"

    required = [source015, source002, venv_py, weight, config_path]
    if not all(p.is_file() for p in required):
        print("PREFLIGHT_FAIL: required frozen path missing", file=sys.stderr)
        return 2

    versions_result = helpers.run(
        [
            str(venv_py),
            "-c",
            "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))",
        ],
        cwd=repo,
        timeout=30,
    )
    try:
        versions = json.loads(versions_result.get("stdout", "").strip())
    except Exception:
        versions = {}
    if versions != EXPECTED_VERSIONS:
        print(f"PREFLIGHT_FAIL: version lock mismatch {versions!r}", file=sys.stderr)
        return 2
    print(f"Version lock: PASS {versions}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    expected_config = {
        "model_type": "qwen3",
        "hidden_size": 4096,
        "num_hidden_layers": 36,
        "vocab_size": 151936,
        "num_attention_heads": 32,
        "num_key_value_heads": 8,
        "head_dim": 128,
        "rms_norm_eps": 1e-6,
        "tie_word_embeddings": False,
    }
    observed_config = {k: config.get(k) for k in expected_config}
    if observed_config != expected_config or config.get("quantization") != EXPECTED_QUANTIZATION:
        print(
            f"PREFLIGHT_FAIL: model config/quantization mismatch "
            f"{observed_config!r} {config.get('quantization')!r}",
            file=sys.stderr,
        )
        return 2
    print(
        f"Model config/quantization: PASS {observed_config} "
        f"quantization={EXPECTED_QUANTIZATION}"
    )

    names, layer_bytes = helpers.selected_layer_from_header(weight, 0)
    if len(names) != EXPECTED_LAYER_TENSORS or layer_bytes != EXPECTED_LAYER_BYTES:
        print("PREFLIGHT_FAIL: layer-0 provenance mismatch", file=sys.stderr)
        return 2
    print("Layer-0 provenance: PASS")

    for index in range(HOST_GATE_SAMPLES):
        sample = helpers.system_sample()
        free = sample.get("memory_free_percent")
        swap = sample.get("swap_used_mb")
        print(f"Host sample {index + 1}/{HOST_GATE_SAMPLES}: free={free}% swap={swap} MB")
        if free is None or swap is None:
            print("TELEMETRY_FAIL: required host telemetry unavailable", file=sys.stderr)
            return 3
        if free < HOST_GATE_FREE_PERCENT or swap > MAX_SWAP_MB:
            print(
                f"HOST_STATE_NOT_READY: free={free}% swap={swap} MB",
                file=sys.stderr,
            )
            return 3
        if index + 1 < HOST_GATE_SAMPLES:
            time.sleep(0.5)
    print("Host-state gate: PASS")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = (
        repo
        / "results-local"
        / "stretch"
        / "quantized-linear-m-boundary-mapping-016"
        / run_id
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    child_summary = run_dir / "child-summary.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"

    disk_before = helpers.disk_snapshot(repo)
    cmd = [
        str(venv_py),
        str(Path(__file__).resolve()),
        "--child",
        str(model_dir),
        str(weight),
        str(config_path),
        str(child_summary),
    ]
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open(
        "w", encoding="utf-8"
    ) as err:
        proc = subprocess.run(cmd, cwd=repo, stdout=out, stderr=err, check=False)

    child_stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    child_stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    if child_stdout:
        print(child_stdout, end="" if child_stdout.endswith("\n") else "\n")
    if proc.returncode != 0 or not child_summary.is_file():
        print(f"CHILD_FAIL: returncode={proc.returncode}", file=sys.stderr)
        if child_stderr:
            print(child_stderr, file=sys.stderr)
        return 4

    child = json.loads(child_summary.read_text(encoding="utf-8"))
    summary = {
        "experiment": "Stretch 016 — QuantizedLinear M-Boundary Mapping",
        "run_id": run_id,
        "started_finished_at_utc": utc_now(),
        "classification": child.get("classification"),
        "source_015_blob": observed015,
        "source_002_blob": observed002,
        "versions": versions,
        "model_config": observed_config,
        "quantization": config.get("quantization"),
        "m_values": M_VALUES,
        "child": child,
        "disk_before": disk_before,
        "disk_after": helpers.disk_snapshot(repo),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Classification: {summary['classification']}")
    print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
