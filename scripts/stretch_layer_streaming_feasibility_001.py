#!/usr/bin/env python3
"""LOOM Stretch 001 — dense layer-streaming feasibility.

Header-only safetensors layer mapping plus exact selective disk I/O of one
transformer layer. No model launch, no MLX model construction, no download.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

MODEL_REPO = "mlx-community/Qwen3-8B-3bit"
MODEL_CACHE_NAME = "models--mlx-community--Qwen3-8B-3bit"
CHUNK_BYTES = 4 * 1024 * 1024
MAX_HEADER_BYTES = 256 * 1024 * 1024
LAYER_RE = re.compile(r"(?:^|\.)layers\.(\d+)\.")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], timeout: int = 20) -> dict:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": args,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "wall_seconds": round(time.perf_counter() - started, 3),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "command": args,
            "error": f"{type(exc).__name__}: {exc}",
            "wall_seconds": round(time.perf_counter() - started, 3),
        }


def parse_scaled_mb(value: str, unit: str) -> float:
    number = float(value.replace(",", "."))
    unit = unit.upper()
    if unit == "K":
        return number / 1024.0
    if unit == "M":
        return number
    if unit == "G":
        return number * 1024.0
    if unit == "T":
        return number * 1024.0 * 1024.0
    return number


def swap_used_mb() -> float | None:
    result = run(["sysctl", "-n", "vm.swapusage"], timeout=10)
    if result.get("exit_code") != 0:
        return None
    match = re.search(
        r"\bused\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*([KMGT])(?:B)?\b",
        result.get("stdout", ""),
        re.IGNORECASE,
    )
    if not match:
        return None
    return round(parse_scaled_mb(match.group(1), match.group(2)), 2)


def memory_free_percent() -> int | None:
    result = run(["memory_pressure"], timeout=15)
    text = result.get("stdout", "") + result.get("stderr", "")
    match = re.search(r"System-wide memory free percentage:\s*(\d+)%", text)
    return int(match.group(1)) if match else None


def host_sample() -> dict:
    return {
        "timestamp_utc": utc_now(),
        "memory_free_percent": memory_free_percent(),
        "swap_used_mb": swap_used_mb(),
    }


def disk_snapshot(path: Path) -> dict:
    usage = shutil.disk_usage(path)
    return {
        "free_bytes": usage.free,
        "free_gib": round(usage.free / (1024 ** 3), 3),
    }


def candidate_cache_roots() -> list[Path]:
    roots: list[Path] = []
    if os.environ.get("HF_HUB_CACHE"):
        roots.append(Path(os.environ["HF_HUB_CACHE"]).expanduser())
    if os.environ.get("HF_HOME"):
        roots.append(Path(os.environ["HF_HOME"]).expanduser() / "hub")
    roots.append(Path.home() / ".cache" / "huggingface" / "hub")

    dedup: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root.resolve()) if root.exists() else str(root)
        if key not in seen:
            seen.add(key)
            dedup.append(root)
    return dedup


def find_local_snapshot(explicit: Path | None) -> Path | None:
    if explicit is not None:
        explicit = explicit.expanduser().resolve()
        return explicit if explicit.is_dir() else None

    candidates: list[Path] = []
    for root in candidate_cache_roots():
        snapshots = root / MODEL_CACHE_NAME / "snapshots"
        if not snapshots.is_dir():
            continue
        for child in snapshots.iterdir():
            if child.is_dir() and (child / "config.json").is_file() and list(child.glob("*.safetensors")):
                candidates.append(child)

    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0].resolve()


def read_safetensors_header(path: Path) -> tuple[int, dict]:
    with path.open("rb") as handle:
        prefix = handle.read(8)
        if len(prefix) != 8:
            raise ValueError(f"{path}: missing safetensors 8-byte header length")
        header_len = struct.unpack("<Q", prefix)[0]
        if header_len <= 0 or header_len > MAX_HEADER_BYTES:
            raise ValueError(f"{path}: implausible safetensors header length {header_len}")
        header_bytes = handle.read(header_len)
        if len(header_bytes) != header_len:
            raise ValueError(f"{path}: truncated safetensors JSON header")
    try:
        header = json.loads(header_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid safetensors JSON header: {exc}") from exc
    if not isinstance(header, dict):
        raise ValueError(f"{path}: safetensors header is not an object")
    return header_len, header


def catalog_weights(model_dir: Path) -> tuple[list[dict], list[dict]]:
    shards = sorted(model_dir.glob("*.safetensors"))
    shard_records: list[dict] = []
    tensors: list[dict] = []

    for shard in shards:
        header_len, header = read_safetensors_header(shard)
        shard_records.append(
            {
                "path": str(shard),
                "name": shard.name,
                "file_bytes": shard.stat().st_size,
                "header_bytes": header_len,
            }
        )
        data_base = 8 + header_len
        for name, meta in header.items():
            if name == "__metadata__":
                continue
            if not isinstance(meta, dict):
                raise ValueError(f"{shard.name}:{name}: tensor metadata not an object")
            offsets = meta.get("data_offsets")
            if not isinstance(offsets, list) or len(offsets) != 2:
                raise ValueError(f"{shard.name}:{name}: invalid data_offsets")
            begin, end = offsets
            if not isinstance(begin, int) or not isinstance(end, int) or begin < 0 or end <= begin:
                raise ValueError(f"{shard.name}:{name}: invalid byte range {offsets!r}")
            absolute_begin = data_base + begin
            absolute_end = data_base + end
            if absolute_end > shard.stat().st_size:
                raise ValueError(f"{shard.name}:{name}: byte range exceeds file size")
            layer_match = LAYER_RE.search(name)
            layer_id = int(layer_match.group(1)) if layer_match else None
            tensors.append(
                {
                    "name": name,
                    "dtype": meta.get("dtype"),
                    "shape": meta.get("shape"),
                    "shard": str(shard),
                    "shard_name": shard.name,
                    "relative_begin": begin,
                    "relative_end": end,
                    "absolute_begin": absolute_begin,
                    "absolute_end": absolute_end,
                    "bytes": end - begin,
                    "layer_id": layer_id,
                }
            )

    return shard_records, tensors


def layer_summary(tensors: list[dict], expected_layers: int) -> tuple[dict[int, dict], dict]:
    layers: dict[int, dict] = {}
    non_layer_bytes = 0
    non_layer_tensors = 0

    for tensor in tensors:
        lid = tensor["layer_id"]
        if lid is None:
            non_layer_bytes += tensor["bytes"]
            non_layer_tensors += 1
            continue
        rec = layers.setdefault(lid, {"bytes": 0, "tensor_count": 0, "shards": set()})
        rec["bytes"] += tensor["bytes"]
        rec["tensor_count"] += 1
        rec["shards"].add(tensor["shard_name"])

    for rec in layers.values():
        rec["shard_count"] = len(rec["shards"])
        rec["shards"] = sorted(rec["shards"])

    discovered = sorted(layers)
    expected = list(range(expected_layers))
    mapping = {
        "expected_layer_ids": expected,
        "discovered_layer_ids": discovered,
        "missing_layer_ids": sorted(set(expected) - set(discovered)),
        "unexpected_layer_ids": sorted(set(discovered) - set(expected)),
        "non_layer_bytes": non_layer_bytes,
        "non_layer_tensors": non_layer_tensors,
    }
    return layers, mapping


def selective_read(tensors: list[dict], layer_id: int) -> dict:
    selected = [t for t in tensors if t["layer_id"] == layer_id]
    expected_bytes = sum(t["bytes"] for t in selected)
    hasher = hashlib.sha256()
    bytes_read = 0
    started = time.perf_counter()

    handles: dict[str, object] = {}
    try:
        for tensor in selected:
            shard_path = tensor["shard"]
            handle = handles.get(shard_path)
            if handle is None:
                handle = open(shard_path, "rb")
                handles[shard_path] = handle
            handle.seek(tensor["absolute_begin"])
            remaining = tensor["bytes"]
            while remaining:
                chunk = handle.read(min(CHUNK_BYTES, remaining))
                if not chunk:
                    raise IOError(f"unexpected EOF while reading {tensor['name']}")
                hasher.update(chunk)
                bytes_read += len(chunk)
                remaining -= len(chunk)
    finally:
        for handle in handles.values():
            try:
                handle.close()
            except Exception:
                pass

    wall = time.perf_counter() - started
    mib = bytes_read / (1024 ** 2)
    return {
        "layer_id": layer_id,
        "tensor_count": len(selected),
        "shard_count": len({t["shard"] for t in selected}),
        "expected_bytes": expected_bytes,
        "bytes_read": bytes_read,
        "wall_seconds": round(wall, 6),
        "effective_mib_per_second": round(mib / wall, 3) if wall > 0 else None,
        "sha256": hasher.hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=None)
    parser.add_argument("--probe-layer", type=int, default=None)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "layer-streaming-feasibility-001" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.json"

    summary: dict = {
        "experiment": "Stretch 001 — Dense Layer Streaming Feasibility",
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "model_repo": MODEL_REPO,
        "classification": None,
        "model_launch": False,
        "network_download": False,
        "disk_before": disk_snapshot(repo),
    }

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = disk_snapshot(repo)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Classification: {summary.get('classification')}")
        if summary.get("failure_reason"):
            print(f"Failure reason: {summary['failure_reason']}")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("LOOM Stretch 001 — Dense Layer Streaming Feasibility")
    print("Model launch: NONE")
    print("Network/download: NONE")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    model_dir = find_local_snapshot(args.model_dir)
    if model_dir is None:
        summary["classification"] = "MODEL_NOT_FOUND"
        summary["failure_reason"] = f"local cached snapshot not found for {MODEL_REPO}"
        return finish(2)

    summary["model_dir"] = str(model_dir)
    summary["snapshot_id"] = model_dir.name
    print(f"Model directory: {model_dir}")

    config_path = model_dir / "config.json"
    if not config_path.is_file():
        summary["classification"] = "LAYER_MAP_FAIL"
        summary["failure_reason"] = "config.json missing"
        return finish(3)

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        summary["classification"] = "LAYER_MAP_FAIL"
        summary["failure_reason"] = f"cannot parse config.json: {type(exc).__name__}: {exc}"
        return finish(3)

    expected_layers = config.get("num_hidden_layers")
    if not isinstance(expected_layers, int) or expected_layers <= 0:
        summary["classification"] = "LAYER_MAP_FAIL"
        summary["failure_reason"] = f"invalid num_hidden_layers: {expected_layers!r}"
        return finish(3)

    summary["config"] = {
        "model_type": config.get("model_type"),
        "architectures": config.get("architectures"),
        "hidden_size": config.get("hidden_size"),
        "intermediate_size": config.get("intermediate_size"),
        "num_attention_heads": config.get("num_attention_heads"),
        "num_key_value_heads": config.get("num_key_value_heads"),
        "num_hidden_layers": expected_layers,
        "vocab_size": config.get("vocab_size"),
        "quantization": config.get("quantization"),
    }
    print(f"Config num_hidden_layers: {expected_layers}")

    try:
        shards, tensors = catalog_weights(model_dir)
    except Exception as exc:
        summary["classification"] = "LAYER_MAP_FAIL"
        summary["failure_reason"] = f"safetensors catalog failure: {type(exc).__name__}: {exc}"
        return finish(3)

    if not shards or not tensors:
        summary["classification"] = "LAYER_MAP_FAIL"
        summary["failure_reason"] = "no safetensors weights discovered"
        return finish(3)

    layers, mapping = layer_summary(tensors, expected_layers)
    summary["safetensors_shards"] = shards
    summary["tensor_count"] = len(tensors)
    summary["total_tensor_bytes"] = sum(t["bytes"] for t in tensors)
    summary["mapping"] = mapping
    summary["per_layer"] = {str(k): v for k, v in sorted(layers.items())}

    print(f"Safetensors shards: {len(shards)}")
    print(f"Tensor count: {len(tensors)}")
    print(f"Total tensor bytes: {summary['total_tensor_bytes']}")
    print(f"Discovered layer IDs: {mapping['discovered_layer_ids']}")
    print(f"Missing layer IDs: {mapping['missing_layer_ids']}")
    print(f"Unexpected layer IDs: {mapping['unexpected_layer_ids']}")
    print(f"Non-layer/shared bytes: {mapping['non_layer_bytes']}")

    if mapping["missing_layer_ids"] or mapping["unexpected_layer_ids"]:
        summary["classification"] = "LAYER_MAP_FAIL"
        summary["failure_reason"] = "transformer layer IDs do not exactly match config"
        return finish(3)

    layer_bytes = [layers[i]["bytes"] for i in range(expected_layers)]
    stats = {
        "min_bytes": min(layer_bytes),
        "mean_bytes": round(mean(layer_bytes), 3),
        "median_bytes": median(layer_bytes),
        "max_bytes": max(layer_bytes),
        "total_layer_bytes": sum(layer_bytes),
    }
    summary["layer_byte_stats"] = stats
    print(
        "Layer bytes min/mean/median/max: "
        f"{stats['min_bytes']} / {stats['mean_bytes']} / {stats['median_bytes']} / {stats['max_bytes']}"
    )

    probe_layer = args.probe_layer if args.probe_layer is not None else expected_layers // 2
    if probe_layer not in layers:
        summary["classification"] = "SELECTIVE_IO_FAIL"
        summary["failure_reason"] = f"requested probe layer {probe_layer} not mapped"
        return finish(4)

    before = host_sample()
    summary["host_before_selective_io"] = before
    print(
        f"Selective I/O pre-state: free={before.get('memory_free_percent')}% "
        f"swap={before.get('swap_used_mb')} MB"
    )

    try:
        probe = selective_read(tensors, probe_layer)
    except Exception as exc:
        summary["classification"] = "SELECTIVE_IO_FAIL"
        summary["failure_reason"] = f"selective layer read failed: {type(exc).__name__}: {exc}"
        return finish(4)

    after = host_sample()
    summary["host_after_selective_io"] = after
    summary["selective_io"] = probe

    print(f"Probe layer: {probe_layer}")
    print(f"Probe tensors: {probe['tensor_count']} across {probe['shard_count']} shard(s)")
    print(f"Probe bytes: expected={probe['expected_bytes']} read={probe['bytes_read']}")
    print(f"Probe wall: {probe['wall_seconds']} s")
    print(f"Probe throughput: {probe['effective_mib_per_second']} MiB/s")
    print(f"Probe SHA256: {probe['sha256']}")
    print(
        f"Selective I/O post-state: free={after.get('memory_free_percent')}% "
        f"swap={after.get('swap_used_mb')} MB"
    )

    if probe["bytes_read"] != probe["expected_bytes"]:
        summary["classification"] = "SELECTIVE_IO_FAIL"
        summary["failure_reason"] = "selected layer byte count mismatch"
        return finish(4)

    if before.get("memory_free_percent") is None or before.get("swap_used_mb") is None or after.get("memory_free_percent") is None or after.get("swap_used_mb") is None:
        summary["classification"] = "TELEMETRY_PARTIAL"
        summary["failure_reason"] = "layer mapping and selective I/O passed but host telemetry was incomplete"
        return finish(5)

    summary["classification"] = "LAYER_ADDRESSABLE_IO_PASS"
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
