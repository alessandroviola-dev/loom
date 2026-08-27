#!/usr/bin/env python3
"""Canonical no-cache SOURCE/PACKED expert backend for the 30B external-MoE path.

Full manifest/provenance validation is deliberately offline-only.  The hot
PACKED path consumes a small prevalidated runtime contract and never opens the
full validation manifest.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

LAYERS = 48
EXPERTS = 128
EXPERT_PAYLOAD_BYTES = 2_506_752
TOTAL_PAYLOAD_BYTES = 15_401_484_288
FORMAT = "LOOM_FULLBANK_EXPERT_MAJOR_V1"
ABI = "layer_id:int[0,47],expert_id:int[0,127]"
RUNTIME_CONTRACT_FORMAT = "LOOM_EXPERT_MAJOR_RUNTIME_CONTRACT_V1"
RUNTIME_CONTRACT_VERSION = 1
FORMULAIC_RESOLVER = "FORMULAIC_RESOLVER"
COMPACT_INDEX_RESOLVER = "COMPACT_INDEX_RESOLVER"


class ExpertBackendError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _hash_range(fd: int, offset: int, length: int) -> str:
    digest = hashlib.sha256()
    remaining, cursor = length, offset
    while remaining:
        chunk = os.pread(fd, min(1024 * 1024, remaining), cursor)
        if not chunk:
            raise ExpertBackendError("truncated payload range")
        digest.update(chunk)
        cursor += len(chunk)
        remaining -= len(chunk)
    return digest.hexdigest()


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("format") != FORMAT or manifest.get("format_version") != 1:
        raise ExpertBackendError("unsupported full-bank format")
    if manifest.get("artifact_scope") != "full-routed-bank" or manifest.get("mapping_abi") != ABI:
        raise ExpertBackendError("incompatible full-bank scope or ABI")
    if manifest.get("expert_payload_bytes") != EXPERT_PAYLOAD_BYTES or manifest.get("total_payload_bytes") != TOTAL_PAYLOAD_BYTES:
        raise ExpertBackendError("incompatible full-bank payload geometry")
    return manifest


def index_entries(manifest: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    rows = manifest.get("experts")
    expected = [(layer, expert) for layer in range(LAYERS) for expert in range(EXPERTS)]
    keys = [(row.get("layer"), row.get("expert_id")) for row in rows or []]
    if keys != expected:
        raise ExpertBackendError("manifest coverage/order is not exactly 6144 ascending identities")
    entries = {(int(row["layer"]), int(row["expert_id"])): row for row in rows}
    if len(entries) != LAYERS * EXPERTS:
        raise ExpertBackendError("ambiguous manifest identity")
    return entries


def validate_fullbank(
    manifest_path: Path,
    source_model: Path,
    expected_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    """Deterministically validate retained bytes, manifest geometry, and source provenance."""
    manifest_path, source_model = Path(manifest_path), Path(source_model)
    manifest = load_manifest(manifest_path)
    entries = index_entries(manifest)
    binary = manifest_path.parent / manifest["binary_file"]
    errors: list[str] = []
    manifest_sha = sha256_file(manifest_path)
    if expected_manifest_sha256 and manifest_sha != expected_manifest_sha256:
        errors.append("manifest_sha256")
    if not binary.is_file() or binary.stat().st_size != TOTAL_PAYLOAD_BYTES:
        errors.append("binary_size")
    for name, expected in (("config.json", manifest.get("config_sha256")), ("model.safetensors.index.json", manifest.get("index_sha256"))):
        path = source_model / name
        if not path.is_file() or sha256_file(path) != expected:
            errors.append(f"source_provenance:{name}")
    checked = source_checked = 0
    source_fds: dict[str, int] = {}
    packed_fd = None
    try:
        packed_fd = os.open(binary, os.O_RDONLY)
        for row in entries.values():
            layer, expert = row["layer"], row["expert_id"]
            if row.get("offset") != checked * EXPERT_PAYLOAD_BYTES or row.get("size") != EXPERT_PAYLOAD_BYTES:
                errors.append(f"entry_geometry:{layer}:{expert}")
                break
            components = row.get("components", [])
            if len(components) != 9:
                errors.append(f"component_count:{layer}:{expert}")
                break
            packed_hash = _hash_range(packed_fd, row["offset"], row["size"])
            if packed_hash != row.get("packed_sha256") or packed_hash != row.get("source_sha256"):
                errors.append(f"packed_hash:{layer}:{expert}")
                break
            for ordinal, component in enumerate(components):
                offset, length = component.get("packed_offset"), component.get("packed_length")
                if component.get("component_order") != ordinal or offset is None or length is None or offset + length > TOTAL_PAYLOAD_BYTES:
                    errors.append(f"component_geometry:{layer}:{expert}:{ordinal}")
                    break
                if _hash_range(packed_fd, offset, length) != component.get("sha256"):
                    errors.append(f"component_packed_hash:{layer}:{expert}:{ordinal}")
                    break
                shard = source_model / component["source_shard"]
                if not shard.is_file():
                    errors.append(f"source_shard:{component['source_shard']}")
                    break
                fd = source_fds.get(component["source_shard"])
                if fd is None:
                    fd = os.open(shard, os.O_RDONLY)
                    source_fds[component["source_shard"]] = fd
                if component.get("source_length") != length or _hash_range(fd, component["source_offset"], component["source_length"]) != component.get("sha256"):
                    errors.append(f"component_source_hash:{layer}:{expert}:{ordinal}")
                    break
                source_checked += 1
            if errors:
                break
            checked += 1
    finally:
        if packed_fd is not None:
            os.close(packed_fd)
        for fd in source_fds.values():
            os.close(fd)
    return {
        "pass": not errors,
        "errors": errors,
        "manifest_sha256": manifest_sha,
        "entries": len(entries),
        "unique_entries": len(entries),
        "binary_size_bytes": binary.stat().st_size if binary.exists() else None,
        "full_payload_hash_verification_entries": checked,
        "source_component_hash_verification_entries": source_checked,
        "artifact_path": str(binary),
        "manifest_path": str(manifest_path),
    }


def _fixed_layout_invariants(manifest: dict[str, Any], binary: Path) -> dict[str, Any]:
    """Check the preregistered affine layout condition; called offline only."""
    rows = manifest.get("experts") or []
    expected = [(layer, expert) for layer in range(LAYERS) for expert in range(EXPERTS)]
    observed = [(row.get("layer"), row.get("expert_id")) for row in rows]
    sizes = [row.get("size") for row in rows]
    offsets = [row.get("offset") for row in rows]
    affine = all(offset == index * EXPERT_PAYLOAD_BYTES for index, offset in enumerate(offsets))
    return {
        "exactly_6144_expert_records": len(rows) == LAYERS * EXPERTS,
        "lexicographic_48x128_identities": observed == expected,
        "constant_expert_payload_bytes": bool(sizes) and all(size == EXPERT_PAYLOAD_BYTES for size in sizes),
        "contiguous_affine_offsets_no_gaps_or_overlap": affine,
        "total_bank_size_exact": binary.is_file() and binary.stat().st_size == TOTAL_PAYLOAD_BYTES,
    }


def _write_json_and_digest(path: Path, value: dict[str, Any]) -> str:
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encoded)
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    path.with_suffix(path.suffix + ".sha256").write_text(digest + "\n")
    return digest


def derive_runtime_contract(
    manifest_path: Path,
    source_model: Path,
    contract_path: Path,
    expected_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    """Offline Stage-0 validation and frozen resolver selection.

    This is the only public operation which reads the validation manifest.
    The generated contract (and optional compact index) is all the runtime is
    permitted to consume.
    """
    manifest_path, source_model, contract_path = Path(manifest_path), Path(source_model), Path(contract_path)
    validation = validate_fullbank(manifest_path, source_model, expected_manifest_sha256)
    if not validation["pass"]:
        raise ExpertBackendError("offline full-bank validation failed: " + repr(validation["errors"]))
    manifest = load_manifest(manifest_path)
    binary = manifest_path.parent / manifest["binary_file"]
    invariants = _fixed_layout_invariants(manifest, binary)
    fixed_layout_pass = all(invariants.values())
    relative_binary = os.path.relpath(binary.resolve(), contract_path.parent.resolve())
    contract: dict[str, Any] = {
        "format": RUNTIME_CONTRACT_FORMAT,
        "format_version": RUNTIME_CONTRACT_VERSION,
        "source_model_identity": {
            "model": manifest["source_model"],
            "config_sha256": manifest["config_sha256"],
            "index_sha256": manifest["index_sha256"],
        },
        "bank_path_binding": {"relative_to_contract": relative_binary},
        "layers": LAYERS,
        "experts_per_layer": EXPERTS,
        "expert_payload_bytes": EXPERT_PAYLOAD_BYTES,
        "total_bank_size_bytes": TOTAL_PAYLOAD_BYTES,
        "base_offset_bytes": 0,
        "full_manifest_sha256": validation["manifest_sha256"],
        "fullbank_integrity_identity": {
            "validated_payload_entries": validation["full_payload_hash_verification_entries"],
            "validated_source_components": validation["source_component_hash_verification_entries"],
            "artifact_size_bytes": validation["binary_size_bytes"],
            "provenance_root": validation["manifest_sha256"],
        },
        "resolver_mode": FORMULAIC_RESOLVER if fixed_layout_pass else COMPACT_INDEX_RESOLVER,
    }
    index_path: Path | None = None
    if not fixed_layout_pass:
        index_path = contract_path.with_name("runtime-index.json")
        index = {
            "format": "LOOM_EXPERT_MAJOR_COMPACT_RUNTIME_INDEX_V1",
            "entries": [
                {"layer": row["layer"], "expert_id": row["expert_id"], "offset": row["offset"], "size": row["size"]}
                for row in manifest["experts"]
            ],
        }
        index_digest = _write_json_and_digest(index_path, index)
        contract["compact_index_binding"] = {
            "relative_to_contract": os.path.relpath(index_path.resolve(), contract_path.parent.resolve()),
            "sha256": index_digest,
        }
    contract_digest = _write_json_and_digest(contract_path, contract)
    return {
        "offline_validation": validation,
        "fixed_layout_invariants": invariants,
        "fixed_layout_pass": fixed_layout_pass,
        "resolver_mode": contract["resolver_mode"],
        "contract_path": str(contract_path),
        "contract_sha256": contract_digest,
        "index_path": str(index_path) if index_path else None,
    }


def load_runtime_contract(contract_path: Path) -> tuple[dict[str, Any], Path]:
    """Load only the minimal runtime contract; never call ``load_manifest`` here."""
    contract_path = Path(contract_path)
    raw = contract_path.read_bytes()
    digest_path = contract_path.with_suffix(contract_path.suffix + ".sha256")
    if not digest_path.is_file() or hashlib.sha256(raw).hexdigest() != digest_path.read_text().strip():
        raise ExpertBackendError("runtime contract digest mismatch")
    contract = json.loads(raw)
    required = {
        "format", "format_version", "source_model_identity", "bank_path_binding", "layers",
        "experts_per_layer", "expert_payload_bytes", "total_bank_size_bytes", "base_offset_bytes",
        "full_manifest_sha256", "fullbank_integrity_identity", "resolver_mode",
    }
    if not required <= set(contract) or contract.get("format") != RUNTIME_CONTRACT_FORMAT or contract.get("format_version") != RUNTIME_CONTRACT_VERSION:
        raise ExpertBackendError("incompatible runtime contract")
    if (contract["layers"], contract["experts_per_layer"], contract["expert_payload_bytes"], contract["total_bank_size_bytes"], contract["base_offset_bytes"]) != (LAYERS, EXPERTS, EXPERT_PAYLOAD_BYTES, TOTAL_PAYLOAD_BYTES, 0):
        raise ExpertBackendError("incompatible runtime contract geometry")
    if contract["resolver_mode"] not in (FORMULAIC_RESOLVER, COMPACT_INDEX_RESOLVER):
        raise ExpertBackendError("unsupported runtime resolver")
    binding = contract["bank_path_binding"].get("relative_to_contract")
    if not isinstance(binding, str) or Path(binding).is_absolute():
        raise ExpertBackendError("invalid bank path binding")
    binary = (contract_path.parent / binding).resolve()
    if not binary.is_file() or binary.stat().st_size != TOTAL_PAYLOAD_BYTES:
        raise ExpertBackendError("missing or incorrectly sized contract-bound packed artifact")
    return contract, binary


class SourceExpertBackend:
    """Unchanged SOURCE control exposed through the common backend interface."""
    name = "SOURCE"
    persistent_cache = False
    source_fallback = False

    def __init__(self, source_loader: Callable[..., tuple[Any, float, int]]):
        self._source_loader = source_loader
        self.requests = 0

    def load_weights(self, layer_id: int, expert_id: int, specs: Any) -> tuple[Any, float, int]:
        self.requests += 1
        return self._source_loader(layer_id, expert_id, specs)


class PackedExpertBackend:
    """One-pread-per-expert backend driven only by the prevalidated contract."""
    name = "PACKED"
    persistent_cache = False
    source_fallback = False

    def __init__(self, runtime_contract_path: Path, mx_module: Any, dtype_map: dict[str, Any], clock_ns: Callable[[], int]):
        self.runtime_contract_path = Path(runtime_contract_path)
        self.contract, self.binary = load_runtime_contract(self.runtime_contract_path)
        self.resolver_mode = self.contract["resolver_mode"]
        self.entries: dict[tuple[int, int], dict[str, int]] | None = None
        if self.resolver_mode == COMPACT_INDEX_RESOLVER:
            binding = self.contract.get("compact_index_binding", {})
            rel, expected = binding.get("relative_to_contract"), binding.get("sha256")
            if not isinstance(rel, str) or Path(rel).is_absolute() or not isinstance(expected, str):
                raise ExpertBackendError("missing compact runtime index binding")
            index_path = (self.runtime_contract_path.parent / rel).resolve()
            raw = index_path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ExpertBackendError("compact runtime index digest mismatch")
            index = json.loads(raw)
            rows = index.get("entries") if index.get("format") == "LOOM_EXPERT_MAJOR_COMPACT_RUNTIME_INDEX_V1" else None
            if not isinstance(rows, list):
                raise ExpertBackendError("invalid compact runtime index")
            entries = {(int(row["layer"]), int(row["expert_id"])): {"offset": int(row["offset"]), "size": int(row["size"])} for row in rows}
            if len(entries) != LAYERS * EXPERTS:
                raise ExpertBackendError("ambiguous compact runtime index")
            self.entries = entries
        self.mx, self.dtype_map, self.clock_ns = mx_module, dtype_map, clock_ns
        self.requests = self.fallback_count = 0
        # SPEED_FRONTIER_001 Stage 1: one process-lifetime descriptor; no payload retention.
        self._packed_fd: int | None = os.open(self.binary, os.O_RDONLY)

    def resolve_expert(self, layer_id: int, expert_id: int) -> dict[str, int]:
        layer, expert = int(layer_id), int(expert_id)
        if layer not in range(LAYERS) or expert not in range(EXPERTS):
            raise ExpertBackendError(f"unresolved packed identity {(layer, expert)}")
        if self.resolver_mode == FORMULAIC_RESOLVER:
            row = {"offset": (layer * EXPERTS + expert) * EXPERT_PAYLOAD_BYTES, "size": EXPERT_PAYLOAD_BYTES}
        else:
            assert self.entries is not None
            row = self.entries.get((layer, expert))
            if row is None:
                raise ExpertBackendError(f"unresolved packed identity {(layer, expert)}")
        if row["offset"] < 0 or row["size"] != EXPERT_PAYLOAD_BYTES or row["offset"] + row["size"] > TOTAL_PAYLOAD_BYTES:
            raise ExpertBackendError(f"invalid packed entry {(layer, expert)}")
        return row

    def load_weights(self, layer_id: int, expert_id: int, specs: Any) -> tuple[dict[str, Any], float, int]:
        started = self.clock_ns()
        row = self.resolve_expert(layer_id, expert_id)
        if self._packed_fd is None:
            raise ExpertBackendError("packed backend used after deterministic close")
        raw = os.pread(self._packed_fd, row["size"], row["offset"])
        if len(raw) != row["size"]:
            raise ExpertBackendError(f"truncated packed payload {(layer_id, expert_id)}")
        host: dict[str, Any] = {}
        cursor = 0
        for projection, component, record, count, _ in specs[layer_id]:
            part = memoryview(raw)[cursor:cursor + count]
            if len(part) != count:
                raise ExpertBackendError("packed component layout failure")
            host[f"{projection}.{component}"] = __import__("numpy").frombuffer(part, dtype=self.dtype_map[record["dtype"]]).reshape(record["shape"][1:])
            cursor += count
        if cursor != row["size"]:
            raise ExpertBackendError("packed component accounting failure")
        weights = {name: self.mx.array(array) for name, array in host.items()}
        self.mx.eval(*weights.values())
        self.requests += 1
        return weights, (self.clock_ns() - started) / 1e9, 1

    def close(self) -> None:
        """Deterministic process-lifetime PACKED descriptor teardown."""
        if self._packed_fd is not None:
            os.close(self._packed_fd)
            self._packed_fd = None

    def __del__(self) -> None:
        self.close()
