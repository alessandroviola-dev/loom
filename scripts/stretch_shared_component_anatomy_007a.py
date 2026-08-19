#!/usr/bin/env python3
"""LOOM Stretch 007A — read-only shared/non-layer component anatomy.

No MLX import, model construction, tensor materialization, network, or generation.
Uses the frozen Stretch 001 safetensors header catalog to enumerate every
non-transformer-layer tensor in the local Qwen3-8B-3bit artifact.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_001_BLOB = "890444928abd6cc24e7194317c92b36b50fd994b"
EXPECTED_NON_LAYER_BYTES = 544_546_816
EXPECTED_MODEL_TYPE = "qwen3"
EXPECTED_HIDDEN_SIZE = 4096
EXPECTED_NUM_LAYERS = 36


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("loom_stretch001_helpers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import Stretch 001 helper module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def group_for(name: str) -> str:
    if name.startswith("model.embed_tokens."):
        return "embedding"
    if name.startswith("model.norm."):
        return "final_norm"
    if name.startswith("lm_head."):
        return "lm_head"
    return "other"


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    helper_path = repo / "scripts" / "stretch_layer_streaming_feasibility_001.py"
    model_dir = repo / "results-local" / "mlx" / "models" / "Qwen3-8B-3bit"
    config_path = model_dir / "config.json"
    weight_path = model_dir / "model.safetensors"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "shared-component-anatomy-007a" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.json"

    print("LOOM Stretch 007A — Shared Component Anatomy")
    print("MLX/model launch: NONE")
    print("Tensor materialization: NONE")
    print("Network/download: NONE")

    observed_helper_blob = git_blob(helper_path, repo)
    print(f"Stretch 001 helper blob: {observed_helper_blob}")
    if observed_helper_blob != SOURCE_001_BLOB:
        print(f"Classification: PREFLIGHT_FAIL")
        print(f"Failure reason: Stretch 001 helper blob mismatch; expected {SOURCE_001_BLOB}")
        return 2
    print("Source provenance: PASS")

    if not config_path.is_file() or not weight_path.is_file():
        print("Classification: PREFLIGHT_FAIL")
        print(
            "Failure reason: required local config/weight missing: "
            f"config={config_path.is_file()} weight={weight_path.is_file()}"
        )
        return 2

    helpers = load_module(helper_path)
    disk_before = helpers.disk_snapshot(repo)
    print(f"Disk free before: {disk_before['free_gib']:.3f} GiB")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("Classification: PREFLIGHT_FAIL")
        print(f"Failure reason: config parse failed: {type(exc).__name__}: {exc}")
        return 2

    config_view = {
        "model_type": config.get("model_type"),
        "vocab_size": config.get("vocab_size"),
        "hidden_size": config.get("hidden_size"),
        "num_hidden_layers": config.get("num_hidden_layers"),
        "tie_word_embeddings": config.get("tie_word_embeddings"),
        "rms_norm_eps": config.get("rms_norm_eps"),
        "quantization": config.get("quantization"),
    }
    print("Config: " + json.dumps(config_view, ensure_ascii=False, sort_keys=True))

    if (
        config_view["model_type"] != EXPECTED_MODEL_TYPE
        or config_view["hidden_size"] != EXPECTED_HIDDEN_SIZE
        or config_view["num_hidden_layers"] != EXPECTED_NUM_LAYERS
    ):
        print("Classification: PREFLIGHT_FAIL")
        print("Failure reason: frozen model identity/config mismatch")
        return 2

    try:
        shards, tensors = helpers.catalog_weights(model_dir)
    except Exception as exc:
        print("Classification: PREFLIGHT_FAIL")
        print(f"Failure reason: safetensors catalog failed: {type(exc).__name__}: {exc}")
        return 2

    non_layer = [dict(t) for t in tensors if t.get("layer_id") is None]
    non_layer.sort(key=lambda item: item["name"])

    groups: dict[str, dict] = {}
    for tensor in non_layer:
        group = group_for(tensor["name"])
        tensor["group"] = group
        record = groups.setdefault(group, {"tensor_count": 0, "bytes": 0, "names": []})
        record["tensor_count"] += 1
        record["bytes"] += int(tensor["bytes"])
        record["names"].append(tensor["name"])

    total_non_layer = sum(int(t["bytes"]) for t in non_layer)
    total_all = sum(int(t["bytes"]) for t in tensors)
    layer_total = total_all - total_non_layer

    print(f"Safetensors shards: {len(shards)}")
    print(f"All tensors: {len(tensors)}")
    print(f"Non-layer tensors: {len(non_layer)}")
    print(f"Non-layer bytes: {total_non_layer}")
    print(f"Transformer-layer bytes: {layer_total}")
    print(f"Total tensor bytes: {total_all}")

    for group in ("embedding", "final_norm", "lm_head", "other"):
        record = groups.get(group, {"tensor_count": 0, "bytes": 0, "names": []})
        print(
            f"Group {group}: tensors={record['tensor_count']} bytes={record['bytes']}"
        )

    print("Non-layer tensor catalog:")
    for tensor in non_layer:
        print(
            "  "
            + json.dumps(
                {
                    "name": tensor["name"],
                    "group": tensor["group"],
                    "dtype": tensor.get("dtype"),
                    "shape": tensor.get("shape"),
                    "bytes": tensor["bytes"],
                    "shard": tensor.get("shard_name"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )

    disk_after = helpers.disk_snapshot(repo)
    classification = (
        "SHARED_COMPONENT_ANATOMY_PASS"
        if total_non_layer == EXPECTED_NON_LAYER_BYTES
        else "SHARED_COMPONENT_LAYOUT_MISMATCH"
    )

    summary = {
        "experiment": "Stretch 007A — Shared Component Anatomy",
        "run_id": run_id,
        "started_and_finished_at_utc": utc_now(),
        "classification": classification,
        "source_001_blob": observed_helper_blob,
        "model_dir": str(model_dir),
        "weight_sha256": sha256_file(weight_path),
        "config": config_view,
        "shards": shards,
        "tensor_count_all": len(tensors),
        "tensor_count_non_layer": len(non_layer),
        "total_tensor_bytes": total_all,
        "transformer_layer_bytes": layer_total,
        "non_layer_bytes": total_non_layer,
        "expected_non_layer_bytes": EXPECTED_NON_LAYER_BYTES,
        "groups": groups,
        "non_layer_tensors": [
            {
                "name": t["name"],
                "group": t["group"],
                "dtype": t.get("dtype"),
                "shape": t.get("shape"),
                "bytes": t["bytes"],
                "shard_name": t.get("shard_name"),
            }
            for t in non_layer
        ],
        "disk_before": disk_before,
        "disk_after": disk_after,
        "mlx_imported": False,
        "model_launched": False,
        "tensor_materialized": False,
        "network_download": False,
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Classification: {classification}")
    if classification != "SHARED_COMPONENT_ANATOMY_PASS":
        print(
            f"Failure reason: non-layer total {total_non_layer} B != expected {EXPECTED_NON_LAYER_BYTES} B"
        )
    print(f"Disk free after: {disk_after['free_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0 if classification == "SHARED_COMPONENT_ANATOMY_PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
