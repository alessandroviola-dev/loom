#!/usr/bin/env python3
"""Bounded P1_t01 pinned-upstream BF16 versus local-4bit target control.

Gate A first executes the new adapter with the immutable local Q4 tensors and
compares it against both the frozen P1_t01 captures and the validated target
oracle.  No upstream request is made unless that gate passes.  Gate B uses
HTTP byte ranges only: safetensors headers are catalogued from the pinned
objects and every staged tensor is capped by a dedicated 12-GiB store.
"""
from __future__ import annotations

import gc
import hashlib
import http.client
import json
import os
import platform
import re
import resource
import shutil
import ssl
import struct
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import certifi
import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten
from mlx_lm.models.activations import swiglu
from mlx_lm.models.base import create_attention_mask, scaled_dot_product_attention

import loom_30b_moe_dflash_target_interface_001 as oracle
import loom_30b_moe_first_greedy_generation_001 as target

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "results-local/moe/models/Qwen3-30B-A3B-MLX-4bit"
TRACE = ROOT / "results-local/moe/routing-cache-trace-001/20260824T090555Z/generations.json"
CORPUS = ROOT / "results-local/research/dflash-masked-reference-parity-001/20260824T142830Z"
FROZEN = CORPUS / "corpus/P1_t01.npz"
PREFLIGHT = ROOT / "results-local/research/dflash-unquantized-control-preflight-001/20260824T160413Z"
MANIFEST = PREFLIGHT / "upstream-manifest.json"
INDEX = PREFLIGHT / "source-index.json"
OUTROOT = ROOT / "results-local/research/dflash-unquantized-target-p1t01-range-control-001"
REUSE_RUN = OUTROOT / "20260824T173131Z"
REUSE_GATE_A_OUTPUT = REUSE_RUN / "gate-a-q4-output.npz"
REUSE_GATE_A_PARITY = REUSE_RUN / "gate-a-adapter-parity.json"
REUSE_DENSE = REUSE_RUN / "control-cache/dense"
CAP_BYTES = 12 * 1024**3
TOP_K = 8
TAPS = (1, 12, 23, 34, 45)
BF16_EXPERT_BYTES = 9_437_184
Q4_ESTIMATED_UNIQUE_EXPERTS = 3_536
Q4_ESTIMATED_EXPERT_BYTES = 33_369_882_624
BF16_THEORETICAL_LAYER_EXPERTS = 48 * 128
REQUEST_TIMEOUT_SECONDS = 180
REQUEST_MAX_ATTEMPTS = 3
COALESCE_GAP_BYTES = 64 * 1024
# Selected by TRANSPORT_MICROBENCHMARK_PASS (20260824T212313Z); Gate B is not launched here.
MAX_COALESCED_RANGE_BYTES = 64 * 1024 * 1024
TRANSPORT_PREFLIGHT_SAMPLES = 3
TRANSPORT_GATE_B_LIMIT_SECONDS = 2 * 60 * 60


def utc_id(): return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
def utc_now(): return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def dump(path, value): Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
def atomic_dump(path, value):
    path = Path(path); tmp = path.with_name(f".{path.name}.{os.getpid()}.part")
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    try:
        with tmp.open("xb") as f:
            f.write(encoded); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
    finally:
        tmp.unlink(missing_ok=True)
def fsha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def raw_sha(value): return hashlib.sha256(np.ascontiguousarray(np.asarray(value)).tobytes()).hexdigest()
def bf_host(value): return np.asarray(value.astype(mx.float32))
def finite(value): return bool(np.isfinite(np.asarray(value)).all())
def top5(value): return [int(x) for x in np.argsort(np.asarray(value))[-5:][::-1]]
def margin(value):
    x = np.asarray(value).reshape(-1); two = np.partition(x, -2)[-2:]
    return float(two.max() - two.min())
def metric(a, b):
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64); d = a - b
    an = float(np.linalg.norm(a.ravel())); bn = float(np.linalg.norm(b.ravel())); dn = float(np.linalg.norm(d.ravel()))
    return {"max_abs": float(np.abs(d).max()), "mean_abs": float(np.abs(d).mean()), "rmse": float(np.sqrt(np.mean(d * d))), "relative_L2": dn / max(bn, 1e-30), "cosine": float(np.vdot(a.ravel(), b.ravel()) / max(an * bn, 1e-30))}
def memory():
    return {"mlx_active_bytes": int(mx.get_active_memory()), "mlx_peak_bytes": int(mx.get_peak_memory()), "mlx_cache_bytes": int(mx.get_cache_memory()), "ru_maxrss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)}


def staged_tensor_metadata(path):
    path = Path(path)
    with path.open("rb") as f:
        preamble = f.read(8)
        if len(preamble) != 8: raise RuntimeError(f"truncated staged tensor preamble: {path}")
        header_bytes = struct.unpack("<Q", preamble)[0]
        encoded = f.read(header_bytes)
        if len(encoded) != header_bytes: raise RuntimeError(f"truncated staged tensor header: {path}")
        header = json.loads(encoded)
    spec = header.get("x")
    if set(header) != {"x"} or spec is None or spec.get("dtype") != "BF16" or spec.get("data_offsets", [None])[0] != 0:
        raise RuntimeError(f"invalid staged BF16 tensor contract: {path}")
    payload_bytes = int(spec["data_offsets"][1])
    expected_file_bytes = 8 + header_bytes + payload_bytes
    if path.stat().st_size != expected_file_bytes: raise RuntimeError(f"truncated staged tensor payload: {path}")
    return {"path": str(path), "file_bytes": expected_file_bytes, "payload_bytes": payload_bytes, "shape": spec["shape"], "sha256": fsha(path)}


def validate_reused_evidence():
    old_provenance = json.loads((REUSE_RUN / "provenance.json").read_text())
    parity = json.loads(REUSE_GATE_A_PARITY.read_text())
    if not all(parity["gates"].values()): raise RuntimeError("REUSED_GATE_A_NOT_PASS")
    provenance_checks = {
        "checkpoint": old_provenance["checkpoint"] == "LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001",
        "runtime_mlx_0_31_2": old_provenance["runtime"]["mlx_version"] == "0.31.2",
        "manifest_sha256": old_provenance["inputs"]["preflight_manifest_sha256"] == fsha(MANIFEST),
        "frozen_sha256": old_provenance["inputs"]["frozen_p1_t01_sha256"] == fsha(FROZEN),
        "trace_sha256": old_provenance["inputs"]["trace_sha256"] == fsha(TRACE),
        "gate_a_output_present": REUSE_GATE_A_OUTPUT.is_file(),
        "gate_a_parity_present": REUSE_GATE_A_PARITY.is_file(),
    }
    if not all(provenance_checks.values()): raise RuntimeError(f"REUSED_EVIDENCE_PROVENANCE_FAIL: {provenance_checks}")
    files = sorted(REUSE_DENSE.glob("*.safetensors"))
    rows = [staged_tensor_metadata(path) for path in files]
    payload_bytes = sum(x["payload_bytes"] for x in rows)
    disk_bytes = sum(x["file_bytes"] for x in rows)
    manifest_rows = [{"filename": Path(x["path"]).name, "file_bytes": x["file_bytes"], "payload_bytes": x["payload_bytes"], "sha256": x["sha256"]} for x in rows]
    manifest_sha256 = raw_sha(json.dumps(manifest_rows, sort_keys=True).encode())
    expected_dense = json.loads(MANIFEST.read_text())["bf16_structural_accounting"]["non_routed_bytes"]
    if len(rows) != 435 or payload_bytes != expected_dense:
        raise RuntimeError(f"REUSED_DENSE_CACHE_RECONCILIATION_FAIL: count={len(rows)} payload={payload_bytes}")
    return {"provenance_checks": provenance_checks, "gate_a_output_sha256": fsha(REUSE_GATE_A_OUTPUT), "gate_a_parity_sha256": fsha(REUSE_GATE_A_PARITY), "dense_tensor_count": len(rows), "dense_payload_bytes": payload_bytes, "dense_disk_bytes": disk_bytes, "dense_file_manifest_sha256": manifest_sha256, "dense_files": manifest_rows}


def dry_accounting(validation):
    q4 = np.load(REUSE_GATE_A_OUTPUT, allow_pickle=False)
    per_layer = [len(set(np.asarray(q4[f"router_ids_{layer}"]).reshape(-1).tolist())) for layer in range(target.LAYERS)]
    unique_pairs = sum(per_layer)
    del q4
    if unique_pairs != Q4_ESTIMATED_UNIQUE_EXPERTS or min(per_layer) != 58 or max(per_layer) != 89:
        raise RuntimeError(f"Q4_ROUTING_ACCOUNTING_DRIFT: total={unique_pairs} min={min(per_layer)} max={max(per_layer)}")
    theoretical_expert_bytes = BF16_THEORETICAL_LAYER_EXPERTS * BF16_EXPERT_BYTES
    staging_peak_estimate = BF16_EXPERT_BYTES + 4096
    combined_peak_estimate = validation["dense_disk_bytes"] + staging_peak_estimate
    retains_all_experts = False
    permitted = not retains_all_experts and combined_peak_estimate <= CAP_BYTES
    return {
        "q4_estimated_unique_expert_count": unique_pairs,
        "q4_estimated_expert_bytes": unique_pairs * BF16_EXPERT_BYTES,
        "q4_unique_experts_per_layer_min": min(per_layer),
        "q4_unique_experts_per_layer_max": max(per_layer),
        "q4_unique_experts_per_layer_mean": float(np.mean(per_layer)),
        "bf16_theoretical_upper_bound_unique_layer_experts": BF16_THEORETICAL_LAYER_EXPERTS,
        "bf16_theoretical_expert_upper_bytes": theoretical_expert_bytes,
        "dense_payload_bytes_reused": validation["dense_payload_bytes"],
        "dense_cache_disk_bytes_reused": validation["dense_disk_bytes"],
        "one_expert_staging_peak_estimate_bytes": staging_peak_estimate,
        "cache_staging_combined_peak_estimate_bytes": combined_peak_estimate,
        "dedicated_disk_cap_bytes": CAP_BYTES,
        "retains_all_expert_payloads": retains_all_experts,
        "one_bf16_expert_weight_set_logically_live": True,
        "dedicated_cache_staging_within_12_gib": permitted,
    }


def p1_tokens():
    trace = json.loads(TRACE.read_text())
    row = next(x for x in trace["runs"] if x["prompt_id"] == "P1")
    ids = list(map(int, row["prompt_token_ids"]))
    if len(ids) != 43: raise RuntimeError(f"P1_t01 geometry changed: {len(ids)} != 43")
    return ids


def q4_forward_adapter(backbone, sources, token_ids, capture_taps=True):
    """New reader/math adapter in local-Q4 mode: exact canonical Q4 operations."""
    x = backbone.embed_tokens(mx.array([token_ids], dtype=mx.int32)); mx.eval(x)
    cache = [target.BF16KVCache() for _ in range(target.LAYERS)]
    mask = create_attention_mask(x, cache[0]); taps, routers = {}, []
    logical_live = max_live = 0
    for layer_no, layer in enumerate(backbone.layers):
        h = x + oracle.attention_with_bf16_cache(layer.self_attn, layer.input_layernorm(x), mask, cache[layer_no])
        z = layer.post_attention_layernorm(h); mx.eval(h, z)
        router_logits, selected, weights = target.route(layer.external_moe.gate, z); mx.eval(router_logits, selected, weights)
        routers.append({"layer": layer_no, "logits": np.asarray(router_logits).copy(), "ids": np.asarray(selected).astype(np.int32, copy=True), "weights": np.asarray(weights).copy()})
        positions = []
        for position in range(z.shape[1]):
            serial = []
            for expert_id in routers[-1]["ids"][0, position].tolist():
                w, _, _, _ = target.read_one_expert(layer_no, int(expert_id), sources)
                logical_live += target.EXPERT_BYTES; max_live = max(max_live, logical_live)
                y = target.direct_expert(z[:, position:position + 1, :], w); mx.eval(y)
                detached = mx.array(np.array(y)); mx.eval(detached); serial.append(detached)
                del w, y; logical_live -= target.EXPERT_BYTES
            stacked = mx.stack(serial, axis=-2); mixed = (stacked * weights[:, position:position + 1, :, None]).sum(axis=-2)
            mx.eval(mixed); positions.append(mixed); del stacked, serial, mixed
        moe = mx.concatenate(positions, axis=1); x = h + moe; mx.eval(x)
        if capture_taps and layer_no + 1 in TAPS: taps[layer_no + 1] = np.asarray(x).astype(np.float32, copy=True)
        del positions, moe, h, z, router_logits, selected, weights
        mx.clear_cache()
    norm = backbone.norm(x); mx.eval(norm); logits = backbone.lm_head(norm); mx.eval(logits)
    result = {"taps": taps, "routers": routers, "final_hidden": np.asarray(norm).astype(np.float32, copy=True), "logits": np.asarray(logits).copy(), "final_live": logical_live, "max_live": max_live}
    del x, norm, logits, cache
    return result


def q4_gate(out, token_ids):
    cfg = json.loads((MODEL / "config.json").read_text())
    records = target.bb.inventory(target.bb.headers()); included = [x for x in records if x["category"] != "routed_expert"]
    if len(included) != 919 or sum(x["stored_bytes"] for x in included) != target.BACKBONE_BYTES: raise RuntimeError("local backbone inventory gate failed")
    sources = target.catalog(records); mx.clear_cache(); mx.reset_peak_memory()
    backbone = target.load_backbone(cfg, included); ownership_before = target.ownership(backbone)
    primary = q4_forward_adapter(backbone, sources, token_ids)
    canonical_cache = [target.BF16KVCache() for _ in range(target.LAYERS)]
    canonical = oracle.external_forward(backbone, sources, token_ids, canonical_cache, "P1_T01_GATE_A_CANONICAL", capture_taps=True)
    canonical_taps = {key: np.asarray(value).astype(np.float32, copy=True) for key, value in canonical["taps"].items()}
    rerun = q4_forward_adapter(backbone, sources, token_ids)
    frozen = np.load(FROZEN, allow_pickle=False)["taps"]
    tap_rows, router_rows = [], []
    for idx, layer_id in enumerate(TAPS):
        a, b, f = primary["taps"][layer_id], canonical_taps[layer_id], frozen[idx:idx + 1]
        tap_rows.append({"layer": layer_id, "frozen_bitwise": bool(np.array_equal(a, f, equal_nan=True)), "canonical_bitwise": bool(np.array_equal(a, b, equal_nan=True)), "rerun_bitwise": bool(np.array_equal(a, rerun["taps"][layer_id], equal_nan=True)), "primary_sha256": raw_sha(a), "frozen_sha256": raw_sha(f)})
    for p, c, r in zip(primary["routers"], canonical["router_digests"], rerun["routers"]):
        router_rows.append({"layer": p["layer"], "canonical_router_logits_bitwise": raw_sha(p["logits"]) == c["sha256"], "rerun_router_logits_bitwise": bool(np.array_equal(p["logits"], r["logits"], equal_nan=True)), "rerun_ids_bitwise": bool(np.array_equal(p["ids"], r["ids"])), "rerun_weights_bitwise": bool(np.array_equal(p["weights"], r["weights"], equal_nan=True))})
    logit_bitwise = bool(np.array_equal(primary["logits"], canonical["logits"], equal_nan=True))
    rerun_logit_bitwise = bool(np.array_equal(primary["logits"], rerun["logits"], equal_nan=True))
    greedy = int(np.argmax(primary["logits"][0, -1])); canonical_greedy = int(np.argmax(canonical["logits"][0, -1]))
    ownership_after = target.ownership(backbone)
    gates = {"runtime_mlx_0_31_2": mx.__version__ == "0.31.2", "frozen_4bit_taps_bitwise": all(x["frozen_bitwise"] for x in tap_rows), "canonical_taps_bitwise": all(x["canonical_bitwise"] for x in tap_rows), "router_decisions_bitwise": all(x["canonical_router_logits_bitwise"] for x in router_rows), "final_logits_bitwise": logit_bitwise, "greedy_token_parity": greedy == canonical_greedy, "greedy_token_12050": greedy == 12050, "deterministic_rerun": all(x["rerun_bitwise"] for x in tap_rows) and all(x["rerun_router_logits_bitwise"] and x["rerun_ids_bitwise"] and x["rerun_weights_bitwise"] for x in router_rows) and rerun_logit_bitwise, "no_nan_inf": finite(primary["logits"]) and finite(primary["final_hidden"]) and all(finite(x["logits"]) and finite(x["weights"]) for x in primary["routers"]), "no_routed_expert_leak": ownership_before["pass"] and ownership_after["pass"] and primary["final_live"] == 0 and canonical["final_logical_expert_live_bytes"] == 0 and rerun["final_live"] == 0}
    report = {"gates": gates, "tap_rows": tap_rows, "router_rows": router_rows, "final_logits": {"canonical_bitwise": logit_bitwise, "rerun_bitwise": rerun_logit_bitwise}, "greedy": {"adapter": greedy, "canonical": canonical_greedy}, "memory": memory(), "ownership_before": ownership_before, "ownership_after": ownership_after}
    dump(out / "gate-a-adapter-parity.json", report)
    # Persist only host comparison tensors so Gate B never co-resides a Q4 and
    # BF16 backbone merely to produce the paired metrics.
    np.savez(out / "gate-a-q4-output.npz", taps=np.stack([primary["taps"][x] for x in TAPS]), final_hidden=primary["final_hidden"], logits=primary["logits"], max_live=np.array(primary["max_live"], dtype=np.int64), **{f"router_logits_{x['layer']}": x["logits"] for x in primary["routers"]}, **{f"router_ids_{x['layer']}": x["ids"] for x in primary["routers"]}, **{f"router_weights_{x['layer']}": x["weights"] for x in primary["routers"]})
    del primary, canonical, rerun, canonical_taps, backbone, canonical_cache
    gc.collect(); mx.clear_cache()
    return gates


class BFLinear(nn.Module):
    def __init__(self): super().__init__()
    def __call__(self, x): return mx.matmul(x, self.weight.T)
class BFEmbedding(nn.Module):
    def __init__(self): super().__init__()
    def __call__(self, x): return self.weight[x]
class BFAttention(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.n_heads = cfg["num_attention_heads"]; self.n_kv_heads = cfg["num_key_value_heads"]; self.scale = cfg["head_dim"] ** -.5
        self.q_proj, self.k_proj, self.v_proj, self.o_proj = BFLinear(), BFLinear(), BFLinear(), BFLinear()
        self.q_norm = nn.RMSNorm(cfg["head_dim"], eps=cfg["rms_norm_eps"]); self.k_norm = nn.RMSNorm(cfg["head_dim"], eps=cfg["rms_norm_eps"])
        self.rope = nn.RoPE(cfg["head_dim"], traditional=False, base=cfg["rope_theta"])
class BFExternalMoe(nn.Module):
    def __init__(self): super().__init__(); self.gate = BFLinear()
class BFLayer(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.self_attn = BFAttention(cfg); self.input_layernorm = nn.RMSNorm(2048, eps=cfg["rms_norm_eps"]); self.post_attention_layernorm = nn.RMSNorm(2048, eps=cfg["rms_norm_eps"]); self.external_moe = BFExternalMoe()
class BFBackbone(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.embed_tokens = BFEmbedding(); self.layers = [BFLayer(cfg) for _ in range(cfg["num_hidden_layers"])]; self.norm = nn.RMSNorm(2048, eps=cfg["rms_norm_eps"]); self.lm_head = BFLinear()


class NetworkCapAbort(RuntimeError):
    """Raised before a range dispatch would exceed its configured hard budget."""
    def __init__(self, row):
        self.row = row
        super().__init__(
            "NETWORK_CAP_ABORT "
            f"current_network_bytes={row['current_network_bytes']} "
            f"current_network_requests={row['current_network_requests']} "
            f"proposed_network_bytes={row['proposed_network_bytes']} "
            f"proposed_network_requests={row['proposed_network_requests']} "
            f"network_byte_cap={row['network_byte_cap']} "
            f"network_request_cap={row['network_request_cap']}"
        )


class RangeStore:
    """Pinned, pooled range reader with one-expert staging and atomic progress."""
    def __init__(self, root, dense_root, manifest, index, dense_validation, progress_path=None,
                 network_byte_cap=None, network_request_cap=None, network_ledger_path=None):
        self.root, self.dense_root, self.manifest, self.index = Path(root), Path(dense_root), manifest, index
        self.progress_path = Path(progress_path) if progress_path else None
        self.root.mkdir(parents=True, exist_ok=False)
        self.expert_root = self.root / "expert"; self.expert_root.mkdir()
        self.dense_validation = {x["filename"]: x for x in dense_validation["dense_files"]}
        self.bytes_fetched = self.expert_bytes_fetched = self.network_bytes_received = 0
        self.expert_tensor_payload_bytes_fetched = 0
        self.network_byte_cap = self._validate_cap(network_byte_cap, "network_byte_cap")
        self.network_request_cap = self._validate_cap(network_request_cap, "network_request_cap")
        self.network_ledger_path = Path(network_ledger_path) if network_ledger_path else (self.progress_path.with_name("network-ledger.json") if self.progress_path else None)
        self.network_accounted_bytes = 0
        self.network_accounted_requests = 0
        self.network_cap_abort_count = 0
        self.network_ledger_events = []
        self._load_network_ledger()
        self.peak_staging_bytes = 0; self.peak_bytes = dense_validation["dense_disk_bytes"]
        self.fetches = []; self.network_events = []; self.network_retries = self.network_failures = self.exhausted_failures = 0
        self.dense_cache_hits = self.dense_payload_bytes_reused = 0; self.unique_layer_experts_fetched = set()
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.weights = {x["filename"]: x for x in manifest["artifacts"]["weights"]}
        self.weight_map = index["weight_map"]; self.headers = {}
        self.connections = {}; self.resolved_urls = {}; self.connection_new_count = 0
        self.connection_reuse_count = 0; self.redirect_count = 0; self.http_request_count = self.network_accounted_requests
        self.coalesced_range_count = 0; self.coalesced_tensor_count = 0
        self.started_monotonic = time.monotonic(); self.started_utc = utc_now(); self.last_successful_fetch_timestamp = None
        self.current_layer = None; self.current_layer_required = set(); self.current_layer_completed = set()
        self.cumulative_expert_layer_pairs_completed = 0
        self._write_network_ledger()
        self.write_progress("initialized")
    @staticmethod
    def _validate_cap(value, name):
        if value is None: return None
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer or None")
        return value
    def _load_network_ledger(self):
        if not self.network_ledger_path or not self.network_ledger_path.is_file(): return
        row = json.loads(self.network_ledger_path.read_text())
        if row.get("ledger_version") != 1:
            raise RuntimeError("NETWORK_LEDGER_VERSION_MISMATCH")
        if row.get("network_byte_cap") != self.network_byte_cap or row.get("network_request_cap") != self.network_request_cap:
            raise RuntimeError("NETWORK_LEDGER_CAP_CONFIGURATION_MISMATCH")
        self.network_accounted_bytes = int(row["network_accounted_bytes"])
        self.network_accounted_requests = int(row["network_accounted_requests"])
        self.network_cap_abort_count = int(row.get("network_cap_abort_count", 0))
        self.network_ledger_events = list(row.get("events", []))
        if self.network_accounted_bytes < 0 or self.network_accounted_requests < 0:
            raise RuntimeError("NETWORK_LEDGER_NEGATIVE_COUNTER")
    def _write_network_ledger(self):
        if not self.network_ledger_path: return
        atomic_dump(self.network_ledger_path, {
            "ledger_version": 1,
            "network_byte_cap": self.network_byte_cap,
            "network_request_cap": self.network_request_cap,
            "network_accounted_bytes": self.network_accounted_bytes,
            "network_accounted_requests": self.network_accounted_requests,
            "network_cap_abort_count": self.network_cap_abort_count,
            "events": self.network_ledger_events,
        })
    def _reserve_network_dispatch(self, shard, start, length, purpose, attempt, redirect):
        """Atomically charge the maximum planned range cost before HTTP dispatch."""
        proposed_bytes, proposed_requests = int(length), 1
        abort = {
            "event": "NETWORK_CAP_ABORT",
            "current_network_bytes": self.network_accounted_bytes,
            "current_network_requests": self.network_accounted_requests,
            "proposed_network_bytes": proposed_bytes,
            "proposed_network_requests": proposed_requests,
            "network_byte_cap": self.network_byte_cap,
            "network_request_cap": self.network_request_cap,
        }
        byte_exceeded = self.network_byte_cap is not None and self.network_accounted_bytes + proposed_bytes > self.network_byte_cap
        request_exceeded = self.network_request_cap is not None and self.network_accounted_requests + proposed_requests > self.network_request_cap
        if byte_exceeded or request_exceeded:
            abort["byte_cap_exceeded"] = byte_exceeded; abort["request_cap_exceeded"] = request_exceeded
            self.network_cap_abort_count += 1; self.network_ledger_events.append(abort)
            self.network_events.append(abort.copy()); self._write_network_ledger(); self.write_progress("NETWORK_CAP_ABORT")
            raise NetworkCapAbort(abort)
        row = {"event": "network_dispatch_reserved", "shard": shard, "start": start, "length": length,
               "purpose": purpose, "attempt": attempt, "redirect": redirect,
               "accounted_network_bytes": proposed_bytes, "accounted_network_requests": proposed_requests}
        self.network_accounted_bytes += proposed_bytes; self.network_accounted_requests += proposed_requests
        self.http_request_count = self.network_accounted_requests
        self.network_ledger_events.append(row); self._write_network_ledger()
    def record_cache_hit(self, cache_key):
        """Record a validated cache hit without charging the network ledger."""
        self.network_events.append({"event": "cache_hit", "cache_key": cache_key,
                                    "network_accounted_bytes": 0, "network_accounted_requests": 0})
        self._write_network_ledger()
    def close(self):
        for connection in self.connections.values():
            try: connection.close()
            except Exception: pass
        self.connections.clear()
    def staging_used(self): return sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file())
    def observe(self):
        staging = self.staging_used(); self.peak_staging_bytes = max(self.peak_staging_bytes, staging)
        combined = sum(x["file_bytes"] for x in self.dense_validation.values()) + staging
        self.peak_bytes = max(self.peak_bytes, combined)
        if combined > CAP_BYTES: raise RuntimeError(f"CONTROL_CACHE_CAP_EXCEEDED: {combined} > {CAP_BYTES}")
    def write_progress(self, state):
        if not self.progress_path: return
        atomic_dump(self.progress_path, {
            "checkpoint": "LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001",
            "state": state, "updated_utc": utc_now(), "started_utc": self.started_utc,
            "elapsed_seconds": time.monotonic() - self.started_monotonic,
            "current_layer_1_based": None if self.current_layer is None else self.current_layer + 1,
            "layers_total": target.LAYERS,
            "unique_experts_required_current_layer": len(self.current_layer_required),
            "unique_experts_completed_current_layer": len(self.current_layer_completed),
            "cumulative_expert_layer_pairs_completed": self.cumulative_expert_layer_pairs_completed,
            "cumulative_payload_bytes_fetched": self.expert_tensor_payload_bytes_fetched,
            "cumulative_network_payload_bytes_fetched": self.expert_bytes_fetched,
            "http_request_count": self.http_request_count,
            "network_accounted_bytes": self.network_accounted_bytes,
            "network_accounted_requests": self.network_accounted_requests,
            "network_byte_cap": self.network_byte_cap,
            "network_request_cap": self.network_request_cap,
            "network_cap_abort_count": self.network_cap_abort_count,
            "successful_range_request_count": len(self.fetches),
            "connection_reuse_count_observable": self.connection_reuse_count,
            "connection_new_count": self.connection_new_count,
            "retry_count": self.network_retries,
            "last_successful_fetch_timestamp": self.last_successful_fetch_timestamp,
        })
    def set_layer(self, layer, required):
        self.current_layer = layer; self.current_layer_required = set(required); self.current_layer_completed = set()
        self.write_progress("layer_in_progress")
    def complete_expert(self, layer, expert_id):
        if layer != self.current_layer: raise RuntimeError("progress layer mismatch")
        if expert_id not in self.current_layer_required: raise RuntimeError("progress expert not required")
        if expert_id in self.current_layer_completed: raise RuntimeError("duplicate completed expert")
        self.current_layer_completed.add(expert_id); self.cumulative_expert_layer_pairs_completed += 1
        self.write_progress("layer_in_progress")
    def url(self, shard): return f"https://huggingface.co/Qwen/Qwen3-30B-A3B/resolve/{self.manifest['resolved_revision']}/{shard}"
    def _connection(self, parsed):
        if parsed.scheme != "https": raise RuntimeError(f"non-HTTPS redirect rejected: {parsed.geturl()}")
        host, port = parsed.hostname, parsed.port or 443
        key = (parsed.scheme, host, port)
        connection = self.connections.get(key)
        reused_candidate = connection is not None and connection.sock is not None
        if connection is None:
            connection = http.client.HTTPSConnection(host, port, timeout=REQUEST_TIMEOUT_SECONDS, context=self.ssl_context)
            self.connections[key] = connection; self.connection_new_count += 1
        return connection, reused_candidate
    def _raw_get(self, url, start, length, purpose, attempt, redirect):
        parsed = urlsplit(url)
        if not parsed.hostname: raise RuntimeError(f"invalid redirect URL: {url}")
        connection, reused_candidate = self._connection(parsed)
        path = (parsed.path or "/") + (f"?{parsed.query}" if parsed.query else "")
        try:
            self._reserve_network_dispatch(parsed.path, start, length, purpose, attempt, redirect)
            connection.request("GET", path, headers={"Range": f"bytes={start}-{start + length - 1}", "User-Agent": "LOOM-range-control/001", "Accept-Encoding": "identity", "Connection": "keep-alive"})
            response = connection.getresponse(); body = response.read()
            headers = {key.lower(): value for key, value in response.getheaders()}; status = response.status
            if reused_candidate: self.connection_reuse_count += 1
            if headers.get("connection", "").lower() == "close": connection.close()
            return status, headers, body
        except Exception:
            connection.close()
            raise
    def request(self, shard, start, length, purpose, tensor_names=()):
        if length <= 0: raise ValueError("nonpositive range")
        expected_prefix = f"bytes {start}-{start + length - 1}/"
        last_error = None
        for attempt in range(1, REQUEST_MAX_ATTEMPTS + 1):
            try:
                request_started = time.monotonic()
                url = self.resolved_urls.get(shard, self.url(shard)); redirects = 0
                while True:
                    status, headers, body = self._raw_get(url, start, length, purpose, attempt, redirects)
                    if status in (301, 302, 303, 307, 308):
                        location = headers.get("location")
                        if not location or redirects >= 5: raise RuntimeError(f"redirect contract status={status} location={location!r}")
                        url = urljoin(url, location); redirects += 1; self.redirect_count += 1
                        continue
                    break
                # Cache only the resolved object URL: a later expired signature falls back to the pinned resolver.
                if url != self.url(shard): self.resolved_urls[shard] = url
                cr = headers.get("content-range"); etag = headers.get("etag") or headers.get("x-linked-etag")
                self.network_bytes_received += len(body)
                expected_total = self.weights[shard]["bytes"]
                if status != 206 or cr is None or not cr.startswith(expected_prefix) or len(body) != length or not cr.endswith(f"/{expected_total}"):
                    raise RuntimeError(f"range contract status={status} content_range={cr!r} bytes={len(body)} expected={length}/{expected_total}")
                normalized_etag = etag.strip().removeprefix("W/").strip('"') if etag else None
                # CDN/Xet ETags are opaque object identifiers, not necessarily the Hub's
                # published full-file SHA-256.  Sparse ranges cannot recompute that full
                # hash; retain the pinned revision, expected full-object SHA-256 and total
                # byte contract, and record rather than misclassify an opaque ETag.
                etag_sha256_match = None if not normalized_etag or len(normalized_etag) != 64 or not all(c in "0123456789abcdef" for c in normalized_etag.lower()) else normalized_etag.lower() == self.weights[shard]["sha256"]
                self.bytes_fetched += len(body)
                if purpose in ("ephemeral_expert", "transport_benchmark"):
                    self.expert_bytes_fetched += len(body)
                self.last_successful_fetch_timestamp = utc_now()
                row = {"shard": shard, "start": start, "length": length, "purpose": purpose, "tensor_names": list(tensor_names), "content_range": cr, "etag": etag, "etag_sha256_matches_pinned_full_object": etag_sha256_match, "object_sha256": self.weights[shard]["sha256"], "attempt": attempt, "redirects": redirects, "elapsed_seconds": time.monotonic() - request_started}
                self.fetches.append(row); self.network_events.append({**row, "outcome": "success"})
                self.write_progress("network_fetch_complete")
                return body
            except NetworkCapAbort:
                # A cap decision is final for this pending range: it is not a transport retry.
                raise
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"; self.network_failures += 1
                self.network_events.append({"shard": shard, "start": start, "length": length, "purpose": purpose, "tensor_names": list(tensor_names), "attempt": attempt, "outcome": "failure", "error": last_error})
                # Expired signed URLs must be re-resolved at the pinned revision on the next attempt.
                self.resolved_urls.pop(shard, None)
                self.write_progress("network_fetch_retry")
                if attempt < REQUEST_MAX_ATTEMPTS:
                    self.network_retries += 1; time.sleep(min(2 ** (attempt - 1), 4))
        self.exhausted_failures += 1; self.write_progress("network_fetch_failed")
        raise RuntimeError(f"NETWORK_RANGE_FETCH_FAIL: shard={shard} start={start} length={length} attempts={REQUEST_MAX_ATTEMPTS} last={last_error}")
    def catalog(self):
        for shard in sorted(self.weights):
            first = self.request(shard, 0, 8, "safetensors_preamble")
            n = struct.unpack("<Q", first)[0]
            if n <= 0 or n > 32 * 1024 * 1024: raise RuntimeError(f"implausible header {shard}: {n}")
            h = json.loads(self.request(shard, 8, n, "safetensors_header").decode())
            self.headers[shard] = (8 + n, h)
        if set(self.weight_map.values()) != set(self.weights): raise RuntimeError("pinned index/shard manifest mismatch")
    def specs(self, names):
        rows = []
        for name in names:
            shard = self.weight_map[name]; base, header = self.headers[shard]; spec = header.get(name)
            if spec is None or spec.get("dtype") != "BF16": raise RuntimeError(f"missing/non-BF16 tensor {name}")
            start, end = map(int, spec["data_offsets"]); length = end - start
            rows.append({"name": name, "shard": shard, "start": base + start, "length": length, "shape": spec["shape"]})
        return rows
    def coalesced_plan(self, names, max_range_bytes=MAX_COALESCED_RANGE_BYTES):
        grouped = {}
        for row in self.specs(names): grouped.setdefault(row["shard"], []).append(row)
        plan = []
        for shard, rows in grouped.items():
            span = None
            for row in sorted(rows, key=lambda x: x["start"]):
                end = row["start"] + row["length"]
                if span is None or row["start"] > span["end"] + COALESCE_GAP_BYTES or end - span["start"] > max_range_bytes:
                    if span: plan.append(span)
                    span = {"shard": shard, "start": row["start"], "end": end, "rows": [row]}
                else:
                    span["end"] = max(span["end"], end); span["rows"].append(row)
            if span: plan.append(span)
        return plan
    def fetch_plan(self, plan, purpose):
        """Fetch planned enclosing ranges and return only exact local tensor slices."""
        payloads = {}
        for span in plan:
            body = self.request(span["shard"], span["start"], span["end"] - span["start"], purpose, [x["name"] for x in span["rows"]])
            for row in span["rows"]:
                lo = row["start"] - span["start"]; payload = body[lo:lo + row["length"]]
                if len(payload) != row["length"]: raise RuntimeError(f"local coalesced slice failure: {row['name']}")
                payloads[row["name"]] = payload
        return payloads
    def fetch_names(self, names, purpose, max_range_bytes=MAX_COALESCED_RANGE_BYTES):
        plan = self.coalesced_plan(names, max_range_bytes)
        self.coalesced_range_count += len(plan); self.coalesced_tensor_count += len(names)
        payloads = self.fetch_plan(plan, purpose)
        rows = self.specs(names)
        if purpose in ("ephemeral_expert", "transport_benchmark"):
            self.expert_tensor_payload_bytes_fetched += sum(x["length"] for x in rows)
            self.write_progress("tensor_payload_accounted")
        return rows, payloads, plan
    def tensor(self, name, persistent):
        shard = self.weight_map[name]; base, header = self.headers[shard]; spec = header.get(name)
        if spec is None or spec.get("dtype") != "BF16": raise RuntimeError(f"missing/non-BF16 tensor {name}")
        start, end = map(int, spec["data_offsets"]); length = end - start
        safe = {"x": {"dtype": "BF16", "shape": spec["shape"], "data_offsets": [0, length]}}
        encoded = json.dumps(safe, separators=(",", ":")).encode()
        key = hashlib.sha256(f"{name}:{base + start}:{length}".encode()).hexdigest()[:16]
        path = (self.dense_root if persistent else self.expert_root) / f"{key}.safetensors"
        if persistent:
            cached = self.dense_validation.get(path.name)
            if cached is None or not path.is_file() or path.stat().st_size != cached["file_bytes"] or fsha(path) != cached["sha256"]: raise RuntimeError(f"REUSED_DENSE_CACHE_HASH_FAIL: {name} {path}")
            self.dense_cache_hits += 1; self.dense_payload_bytes_reused += length
        else:
            _, payloads, _ = self.fetch_names([name], "ephemeral_expert"); payload = payloads[name]
            self._write_tensor(path, encoded, payload); del payload; self.observe()
        arr = mx.load(str(path))["x"]; mx.eval(arr)
        if list(arr.shape) != list(spec["shape"]): raise RuntimeError(f"staged tensor shape mismatch: {name}")
        return arr, path, {"name": name, "shard": shard, "payload_offset": base + start, "payload_bytes": length, "shape": spec["shape"], "object_sha256": self.weights[shard]["sha256"], "cache_reused": persistent}
    def _write_tensor(self, path, encoded, payload):
        tmp = path.with_name(f".{path.name}.{os.getpid()}.part")
        try:
            with tmp.open("xb") as f:
                f.write(struct.pack("<Q", len(encoded))); f.write(encoded); f.write(payload); f.flush(); os.fsync(f.fileno())
            os.replace(tmp, path)
        finally: tmp.unlink(missing_ok=True)
    def tensors(self, names):
        rows, payloads, _ = self.fetch_names(names, "ephemeral_expert"); arrays, paths, records = {}, [], []
        try:
            for row in rows:
                length = row["length"]; safe = {"x": {"dtype": "BF16", "shape": row["shape"], "data_offsets": [0, length]}}
                encoded = json.dumps(safe, separators=(",", ":")).encode(); name = row["name"]
                key = hashlib.sha256(f"{name}:{row['start']}:{length}".encode()).hexdigest()[:16]; path = self.expert_root / f"{key}.safetensors"
                self._write_tensor(path, encoded, payloads[name]); paths.append(path)
                arr = mx.load(str(path))["x"]; mx.eval(arr)
                if list(arr.shape) != list(row["shape"]): raise RuntimeError(f"staged tensor shape mismatch: {name}")
                arrays[name] = arr
                records.append({"name": name, "shard": row["shard"], "payload_offset": row["start"], "payload_bytes": length, "shape": row["shape"], "object_sha256": self.weights[row["shard"]]["sha256"], "cache_reused": False})
            self.observe(); return arrays, paths, records
        except Exception:
            for path in paths: path.unlink(missing_ok=True)
            raise

def bf_path(backbone, name):
    if name == "model.embed_tokens.weight": return backbone.embed_tokens, "weight"
    if name == "model.norm.weight": return backbone.norm, "weight"
    if name == "lm_head.weight": return backbone.lm_head, "weight"
    m = re.match(r"model\.layers\.(\d+)\.(.*)", name)
    if not m: raise KeyError(name)
    layer, rest = backbone.layers[int(m.group(1))], m.group(2)
    if rest.startswith("self_attn."):
        tail = rest[len("self_attn."):]; part, key = tail.rsplit(".", 1); return getattr(layer.self_attn, part), key
    if rest.startswith("input_layernorm.") or rest.startswith("post_attention_layernorm."): return getattr(layer, rest.rsplit(".", 1)[0]), "weight"
    if rest.startswith("mlp.gate."): return layer.external_moe.gate, "weight"
    raise KeyError(name)


def dense_names(index):
    return sorted(name for name in index["weight_map"] if ".mlp.experts." not in name)

def load_bf_backbone(store, cfg, index):
    names = dense_names(index)
    if len(names) != 435: raise RuntimeError(f"upstream dense tensor count changed: {len(names)}")
    backbone = BFBackbone(cfg); records = []
    for name in names:
        a, _, record = store.tensor(name, persistent=True); module, key = bf_path(backbone, name); setattr(module, key, a); records.append(record); del a
    gc.collect(); mx.clear_cache(); gc.collect()
    expected = store.manifest["bf16_structural_accounting"]["non_routed_bytes"]
    if sum(x["payload_bytes"] for x in records) != expected: raise RuntimeError("BF16 dense byte reconciliation failed")
    return backbone, records


def bf_expert(store, layer, expert_id):
    names = [f"model.layers.{layer}.mlp.experts.{expert_id}.{proj}.weight" for proj in target.PROJS]
    loaded, paths, rows = store.tensors(names)
    arrays = {proj: loaded[name] for proj, name in zip(target.PROJS, names)}
    if sum(x["payload_bytes"] for x in rows) != 9_437_184: raise RuntimeError("BF16 expert byte reconciliation failed")
    return arrays, paths, rows

def bf_direct(x, weights): return mx.matmul(swiglu(mx.matmul(x, weights["gate_proj"].T), mx.matmul(x, weights["up_proj"].T)), weights["down_proj"].T)


def bf_forward_paired(store, backbone, token_ids):
    """Run primary/rerun layer-paired; fetch each union expert once per layer."""
    streams = []
    for _ in range(2):
        x = backbone.embed_tokens(mx.array([token_ids], dtype=mx.int32)); mx.eval(x)
        cache = [target.BF16KVCache() for _ in range(target.LAYERS)]
        streams.append({"x": x, "cache": cache, "taps": {}, "routers": []})
    mask = create_attention_mask(streams[0]["x"], streams[0]["cache"][0])
    expert_rows = []; logical_live = max_live = 0; layer_accounting = []
    for layer_no, layer in enumerate(backbone.layers):
        routed = []
        for stream in streams:
            x = stream["x"]
            h = x + oracle.attention_with_bf16_cache(layer.self_attn, layer.input_layernorm(x), mask, stream["cache"][layer_no])
            z = layer.post_attention_layernorm(h); mx.eval(h, z)
            router_logits, selected, weights = target.route(layer.external_moe.gate, z); mx.eval(router_logits, selected, weights)
            ids = np.asarray(selected).astype(np.int32, copy=True); ws = bf_host(weights).copy()
            stream["routers"].append({"layer": layer_no, "logits": bf_host(router_logits).copy(), "ids": ids, "weights": ws})
            routed.append({"h": h, "z": z, "router_logits": router_logits, "selected": selected, "weights": weights, "ids": ids})
        assignments = {}
        for stream_no, route in enumerate(routed):
            for position in range(route["ids"].shape[1]):
                for rank, expert_id in enumerate(route["ids"][0, position].tolist()):
                    assignments.setdefault(int(expert_id), []).append((stream_no, position, rank))
        union_ids = sorted(assignments)
        store.set_layer(layer_no, union_ids)
        serial = [[([None] * TOP_K) for _ in range(route["ids"].shape[1])] for route in routed]
        for expert_id in union_ids:
            w, paths, rows = bf_expert(store, layer_no, expert_id)
            store.unique_layer_experts_fetched.add((layer_no, expert_id)); logical_live += BF16_EXPERT_BYTES; max_live = max(max_live, logical_live)
            try:
                for stream_no, position, rank in assignments[expert_id]:
                    y = bf_direct(routed[stream_no]["z"][:, position:position + 1, :], w); mx.eval(y)
                    detached = mx.array(bf_host(y), dtype=mx.bfloat16); mx.eval(detached)
                    serial[stream_no][position][rank] = detached; del y
                expert_rows.extend(rows)
            finally:
                del w
                for path in paths: path.unlink(missing_ok=True)
                store.observe(); logical_live -= BF16_EXPERT_BYTES
            store.complete_expert(layer_no, expert_id)
        for stream_no, stream in enumerate(streams):
            positions = []
            for position, outputs in enumerate(serial[stream_no]):
                if any(value is None for value in outputs): raise RuntimeError("serial expert assignment incomplete")
                stacked = mx.stack(outputs, axis=-2)
                mixed = (stacked * routed[stream_no]["weights"][:, position:position + 1, :, None]).sum(axis=-2); mx.eval(mixed)
                positions.append(mixed); del stacked, outputs, mixed
            moe = mx.concatenate(positions, axis=1); stream["x"] = routed[stream_no]["h"] + moe; mx.eval(stream["x"])
            if layer_no + 1 in TAPS: stream["taps"][layer_no + 1] = bf_host(stream["x"]).copy()
            del positions, moe
        layer_accounting.append({"layer": layer_no, "primary_unique_experts": len(set(routed[0]["ids"].reshape(-1).tolist())), "rerun_unique_experts": len(set(routed[1]["ids"].reshape(-1).tolist())), "union_unique_experts_fetched": len(union_ids)})
        del serial, assignments, union_ids
        for route in routed:
            del route["h"], route["z"], route["router_logits"], route["selected"], route["weights"]
        del routed
        mx.clear_cache()
    results = []
    for stream in streams:
        norm = backbone.norm(stream["x"]); mx.eval(norm); logits = backbone.lm_head(norm); mx.eval(logits)
        results.append({"taps": stream["taps"], "routers": stream["routers"], "final_hidden": bf_host(norm).copy(), "logits": bf_host(logits).copy(), "final_live": logical_live, "max_live": max_live})
        del norm, logits, stream["x"], stream["cache"]
    return results[0], results[1], {"expert_rows": expert_rows, "layers": layer_accounting}


def first_router_difference(q4, bf):
    for a, b in zip(q4["routers"], bf["routers"]):
        for position in range(a["ids"].shape[1]):
            if not np.array_equal(a["ids"][0, position], b["ids"][0, position]):
                return {"position_1_based": position + 1, "layer_0_based": a["layer"], "q4_topk_ids": a["ids"][0, position].tolist(), "bf16_topk_ids": b["ids"][0, position].tolist(), "q4_topk_weights": a["weights"][0, position].astype(float).tolist(), "bf16_topk_weights": b["weights"][0, position].astype(float).tolist()}
    return None


def routing_transport_plan(store, max_range_bytes):
    """Plan only the frozen Q4-routed experts, keeping layer boundaries intact."""
    q4 = np.load(REUSE_GATE_A_OUTPUT, allow_pickle=False)
    spans, exact_bytes, tensor_count = [], 0, 0
    for layer in range(target.LAYERS):
        ids = sorted(set(np.asarray(q4[f"router_ids_{layer}"]).reshape(-1).tolist()))
        names = [f"model.layers.{layer}.mlp.experts.{expert_id}.{proj}.weight" for expert_id in ids for proj in target.PROJS]
        rows = store.specs(names); plan = store.coalesced_plan(names, max_range_bytes)
        exact_bytes += sum(x["length"] for x in rows); tensor_count += len(rows)
        for span in plan: spans.append({**span, "layer_0_based": layer})
    del q4
    if exact_bytes != Q4_ESTIMATED_EXPERT_BYTES or tensor_count != Q4_ESTIMATED_UNIQUE_EXPERTS * len(target.PROJS):
        raise RuntimeError(f"TRANSPORT_PLAN_ACCOUNTING_DRIFT: bytes={exact_bytes} tensors={tensor_count}")
    return {"spans": spans, "exact_tensor_payload_bytes": exact_bytes, "tensor_count": tensor_count, "network_bytes": sum(x["end"] - x["start"] for x in spans), "request_count": len(spans)}


def representative_transport_groups(plan128):
    """Choose four largest actual contiguous groups across distinct shards/layer bands."""
    ranked = sorted(plan128["spans"], key=lambda x: (x["end"] - x["start"], len(x["rows"])), reverse=True)
    selected, used_shards, used_bands = [], set(), set()
    for span in ranked:
        shard, band = span["shard"], span["layer_0_based"] // 12
        if shard in used_shards or band in used_bands: continue
        selected.append(span); used_shards.add(shard); used_bands.add(band)
        if len(selected) == 4: break
    if len(selected) < 3:
        for span in ranked:
            if span in selected: continue
            selected.append(span)
            if len(selected) == 3: break
    if len(selected) < 3: raise RuntimeError("TRANSPORT_MICROBENCHMARK_INSUFFICIENT_REPRESENTATIVE_GROUPS")
    return selected


def transport_microbenchmark(store, requested_candidate_mib=None):
    """No-forward, sequential pooled HTTPS measurement of coalescing ceilings."""
    all_candidates = (16, 32, 64, 128)
    candidates = all_candidates if requested_candidate_mib is None else (requested_candidate_mib,)
    if any(x not in all_candidates for x in candidates): raise RuntimeError(f"invalid transport microbenchmark candidate: {candidates}")
    candidate_bytes = {mib: mib * 1024 * 1024 for mib in all_candidates}
    plans = {mib: routing_transport_plan(store, size) for mib, size in candidate_bytes.items()}
    anchors = representative_transport_groups(plans[128])
    results = []
    for mib in candidates:
        max_bytes = candidate_bytes[mib]; sample_exact = sample_network = 0; sample_requests = 0; latencies = []; elapsed = 0.0
        reused_before, retries_before, fetched_before = store.connection_reuse_count, store.network_retries, len(store.fetches)
        group_rows = []
        for anchor in anchors:
            names = [row["name"] for row in anchor["rows"]]
            plan = store.coalesced_plan(names, max_bytes)
            started = time.monotonic(); payloads = store.fetch_plan(plan, "transport_microbenchmark"); duration = time.monotonic() - started
            rows = store.specs(names); exact = sum(x["length"] for x in rows); network = sum(x["end"] - x["start"] for x in plan)
            if len(payloads) != len(rows) or sum(len(payloads[x["name"]]) for x in rows) != exact:
                raise RuntimeError("TRANSPORT_MICROBENCHMARK_EXACT_SLICE_FAIL")
            sample_exact += exact; sample_network += network; sample_requests += len(plan); elapsed += duration
            latencies.extend(x["elapsed_seconds"] for x in store.fetches[fetched_before:] if x["purpose"] == "transport_microbenchmark")
            fetched_before = len(store.fetches)
            group_rows.append({"layer_0_based": anchor["layer_0_based"], "shard": anchor["shard"], "tensor_count": len(rows), "exact_tensor_payload_bytes": exact, "network_bytes": network, "overfetch_bytes": network - exact, "http_request_count": len(plan), "elapsed_seconds": duration})
            del payloads
        plan = plans[mib]; network_bps = sample_network / max(elapsed, 1e-9); exact_bps = sample_exact / max(elapsed, 1e-9)
        projected_seconds = plan["network_bytes"] / network_bps
        peak_response = max((x["end"] - x["start"] for x in plan["spans"]), default=0)
        peak_disk = sum(x["file_bytes"] for x in store.dense_validation.values()) + BF16_EXPERT_BYTES + 4096
        result = {"max_coalesced_range_mib": mib, "max_coalesced_range_bytes": max_bytes, "representative_groups": group_rows, "benchmark": {"exact_tensor_payload_bytes_required": sample_exact, "network_bytes_actually_fetched": sample_network, "overfetch_bytes": sample_network - sample_exact, "overfetch_ratio": (sample_network - sample_exact) / max(sample_exact, 1), "http_request_count": sample_requests, "mean_request_latency_seconds": float(np.mean(latencies)), "effective_exact_payload_MB_per_second": exact_bps / 1_000_000, "effective_network_MB_per_second": network_bps / 1_000_000, "retries": store.network_retries - retries_before, "connection_reuse_count_observable": store.connection_reuse_count - reused_before, "exact_tensor_extraction_verified": True}, "projection_frozen_q4_routing_plan": {"exact_tensor_payload_bytes": plan["exact_tensor_payload_bytes"], "network_bytes_including_overfetch": plan["network_bytes"], "overfetch_bytes": plan["network_bytes"] - plan["exact_tensor_payload_bytes"], "overfetch_ratio": (plan["network_bytes"] - plan["exact_tensor_payload_bytes"]) / max(plan["exact_tensor_payload_bytes"], 1), "expert_http_request_count": plan["request_count"], "http_request_count_including_32_header_requests": plan["request_count"] + 32, "projected_wall_seconds": projected_seconds, "projected_wall_hours": projected_seconds / 3600}, "resource_estimate": {"peak_temporary_raw_response_memory_bytes": peak_response, "peak_temporary_disk_bytes_one_staged_expert": BF16_EXPERT_BYTES + 4096, "peak_dedicated_disk_bytes_dense_plus_one_expert": peak_disk, "within_12_gib_dedicated_disk": peak_disk <= CAP_BYTES, "one_routed_expert_logically_live": True}}
        result["selection_eligible"] = result["resource_estimate"]["within_12_gib_dedicated_disk"] and result["resource_estimate"]["one_routed_expert_logically_live"] and result["benchmark"]["exact_tensor_extraction_verified"] and projected_seconds <= TRANSPORT_GATE_B_LIMIT_SECONDS
        results.append(result)
    eligible = [x for x in results if x["selection_eligible"]]
    selected = min(eligible, key=lambda x: x["projection_frozen_q4_routing_plan"]["projected_wall_seconds"]) if eligible else None
    store.write_progress("transport_microbenchmark_complete")
    classification = ("TRANSPORT_MICROBENCHMARK_PARTIAL" if requested_candidate_mib is not None else ("TRANSPORT_MICROBENCHMARK_PASS" if selected else "TRANSPORT_COALESCING_LIMIT_REACHED"))
    return {"checkpoint": "LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001", "classification": classification, "scope": "MECHANICAL_TRANSPORT_ONLY_NO_FORWARD_NO_GATE_B", "requested_candidate_mib": requested_candidate_mib, "persistent_https_connection_pool": True, "gap_rule_bytes": COALESCE_GAP_BYTES, "concurrency": "NOT_USED", "representative_anchor_groups_from_128_mib_plan": [{"layer_0_based": x["layer_0_based"], "shard": x["shard"], "tensor_count": len(x["rows"]), "network_bytes": x["end"] - x["start"]} for x in anchors], "candidates": results, "selected_transport_settings": None if selected is None else {"max_coalesced_range_bytes": selected["max_coalesced_range_bytes"], "max_coalesced_range_mib": selected["max_coalesced_range_mib"], "projected_wall_seconds": selected["projection_frozen_q4_routing_plan"]["projected_wall_seconds"], "projected_wall_hours": selected["projection_frozen_q4_routing_plan"]["projected_wall_hours"]}, "gate_b_launched": False}


def transport_preflight(store):
    """Measure pooled/coalesced expert transport before the full Gate-B execution."""
    q4 = np.load(REUSE_GATE_A_OUTPUT, allow_pickle=False)
    planned_spans = planned_payload_bytes = planned_tensor_count = 0
    samples, sampled_shards = [], set()
    for layer in range(target.LAYERS):
        for expert_id in sorted(set(np.asarray(q4[f"router_ids_{layer}"]).reshape(-1).tolist())):
            names = [f"model.layers.{layer}.mlp.experts.{expert_id}.{proj}.weight" for proj in target.PROJS]
            plan = store.coalesced_plan(names)
            planned_spans += len(plan); planned_payload_bytes += sum(x["length"] for x in store.specs(names)); planned_tensor_count += len(names)
            if len(samples) < TRANSPORT_PREFLIGHT_SAMPLES and not ({x["shard"] for x in plan} & sampled_shards):
                samples.append({"layer_0_based": layer, "expert_id": expert_id, "names": names, "plan": plan})
                sampled_shards.update(x["shard"] for x in plan)
    del q4
    if planned_payload_bytes != Q4_ESTIMATED_EXPERT_BYTES or planned_tensor_count != Q4_ESTIMATED_UNIQUE_EXPERTS * 3:
        raise RuntimeError(f"TRANSPORT_PLAN_ACCOUNTING_DRIFT: bytes={planned_payload_bytes} tensors={planned_tensor_count}")
    if not samples: raise RuntimeError("TRANSPORT_PREFLIGHT_NO_REPRESENTATIVE_EXPERT")
    measurements = []
    for sample in samples:
        before = len(store.fetches); started = time.monotonic()
        rows, payloads, plan = store.fetch_names(sample["names"], "transport_benchmark")
        elapsed = time.monotonic() - started; payload_bytes = sum(len(x) for x in payloads.values())
        if payload_bytes != BF16_EXPERT_BYTES or sum(x["length"] for x in rows) != BF16_EXPERT_BYTES:
            raise RuntimeError("TRANSPORT_PREFLIGHT_EXPERT_BYTE_RECONCILIATION_FAIL")
        measurements.append({"layer_0_based": sample["layer_0_based"], "expert_id": sample["expert_id"], "shards": sorted({x["shard"] for x in plan}), "coalesced_range_count": len(plan), "tensor_payload_bytes": payload_bytes, "network_payload_bytes": sum(x["length"] for x in store.fetches[before:]), "elapsed_seconds": elapsed, "request_latencies_seconds": [x["elapsed_seconds"] for x in store.fetches[before:]]})
        del payloads
    sampled_payload = sum(x["tensor_payload_bytes"] for x in measurements); sampled_elapsed = sum(x["elapsed_seconds"] for x in measurements)
    effective_bps = sampled_payload / max(sampled_elapsed, 1e-9)
    request_latencies = [x for measurement in measurements for x in measurement["request_latencies_seconds"]]
    projected_seconds = Q4_ESTIMATED_EXPERT_BYTES / effective_bps
    report = {"classification": "TRANSPORT_PREFLIGHT_PASS" if projected_seconds <= TRANSPORT_GATE_B_LIMIT_SECONDS else "TRANSPORT_PREFLIGHT_TOO_SLOW", "transport": "persistent_https_connection_pool_with_pinned_resolved_object_reuse", "coalescing": {"gap_bytes": COALESCE_GAP_BYTES, "max_range_bytes": MAX_COALESCED_RANGE_BYTES, "expert_tensor_count": planned_tensor_count, "expert_range_count_after_coalescing": planned_spans, "projected_gate_b_http_request_count_including_32_header_requests": planned_spans + 32}, "benchmark": {"sample_count": len(measurements), "measurements": measurements, "sampled_exact_tensor_payload_bytes": sampled_payload, "sampled_elapsed_seconds": sampled_elapsed, "effective_payload_MB_per_second": effective_bps / 1_000_000, "mean_request_latency_seconds": float(np.mean(request_latencies)), "connection_reuse_count_observable": store.connection_reuse_count, "retry_count": store.network_retries}, "projection": {"expert_payload_bytes": Q4_ESTIMATED_EXPERT_BYTES, "expert_payload_gib": Q4_ESTIMATED_EXPERT_BYTES / 1024**3, "projected_expert_fetch_seconds": projected_seconds, "projected_expert_fetch_hours": projected_seconds / 3600, "gate_b_transport_wall_time_limit_seconds": TRANSPORT_GATE_B_LIMIT_SECONDS, "within_two_hour_gate": projected_seconds <= TRANSPORT_GATE_B_LIMIT_SECONDS}}
    store.write_progress("transport_preflight_complete")
    return report


def bf_gate(out, token_ids, validation, transport_microbenchmark_only=False, transport_microbenchmark_candidate_mib=None):
    manifest, index = json.loads(MANIFEST.read_text()), json.loads(INDEX.read_text())
    store = RangeStore(out / "control-staging", REUSE_DENSE, manifest, index, validation, out / "progress.json")
    try:
        store.catalog()
        if transport_microbenchmark_only:
            microbenchmark = transport_microbenchmark(store, transport_microbenchmark_candidate_mib)
            dump(out / "transport-microbenchmark.json", microbenchmark)
            dump(out / "range-fetches.json", store.fetches); dump(out / "network-events.json", store.network_events)
            store.close()
            return {"transport_microbenchmark_only": True, "transport_microbenchmark": microbenchmark}
        # The user-authorized 64-MiB selection is frozen by the completed
        # microbenchmark.  Do not run another transport preflight here.
        transport = {"classification": "FROZEN_TRANSPORT_SELECTION_REUSED", "source": str(OUTROOT / "20260824T212313Z/transport-microbenchmark-aggregate.json"), "max_coalesced_range_bytes": MAX_COALESCED_RANGE_BYTES, "persistent_https_connection_pool": True, "concurrency": "NOT_USED", "coalescing_gap_bytes": COALESCE_GAP_BYTES, "gate_b_launch_authorized": True}
        dump(out / "transport-selection.json", transport)
        store.write_progress("frozen_transport_selection_reused")
        cfg = json.loads((PREFLIGHT / "source-config.json").read_text())
        backbone, dense = load_bf_backbone(store, cfg, index)
        if store.dense_cache_hits != 435 or store.dense_payload_bytes_reused != manifest["bf16_structural_accounting"]["non_routed_bytes"]:
            raise RuntimeError("DENSE_CACHE_REUSE_GATE_FAIL")
        before = memory(); primary, rerun, paired = bf_forward_paired(store, backbone, token_ids); after = memory()
        deterministic = all(np.array_equal(primary["taps"][x], rerun["taps"][x], equal_nan=True) for x in TAPS) and np.array_equal(primary["final_hidden"], rerun["final_hidden"], equal_nan=True) and np.array_equal(primary["logits"], rerun["logits"], equal_nan=True) and all(np.array_equal(a["logits"], b["logits"], equal_nan=True) and np.array_equal(a["ids"], b["ids"]) and np.array_equal(a["weights"], b["weights"], equal_nan=True) for a, b in zip(primary["routers"], rerun["routers"]))
        q4_saved = np.load(REUSE_GATE_A_OUTPUT, allow_pickle=False)
        q4 = {"taps": {lid: q4_saved["taps"][i] for i, lid in enumerate(TAPS)}, "final_hidden": q4_saved["final_hidden"], "logits": q4_saved["logits"], "max_live": int(q4_saved["max_live"]), "routers": [{"layer": layer, "logits": q4_saved[f"router_logits_{layer}"], "ids": q4_saved[f"router_ids_{layer}"], "weights": q4_saved[f"router_weights_{layer}"]} for layer in range(target.LAYERS)]}
        tap_metrics = [{"layer": lid, **metric(primary["taps"][lid][:, -1:, :], q4["taps"][lid][:, -1:, :])} for lid in TAPS]
        hidden_metrics, logit_metrics = metric(primary["final_hidden"][:, -1:, :], q4["final_hidden"][:, -1:, :]), metric(primary["logits"][:, -1:, :], q4["logits"][:, -1:, :])
        q4_last, bf_last = q4["logits"][0, -1], primary["logits"][0, -1]
        router = first_router_difference(q4, primary)
        router_comparison = [{"layer": a["layer"], "topk_ids_equal_all_positions": bool(np.array_equal(a["ids"], b["ids"])), "topk_weight_metrics": metric(a["weights"], b["weights"])} for a, b in zip(q4["routers"], primary["routers"])]
        finite_ok = finite(primary["logits"]) and finite(primary["final_hidden"]) and all(finite(x["logits"]) and finite(x["weights"]) for x in primary["routers"])
        leak_ok = primary["final_live"] == 0 and rerun["final_live"] == 0
        network = {"request_timeout_seconds": REQUEST_TIMEOUT_SECONDS, "max_attempts": REQUEST_MAX_ATTEMPTS, "retries": store.network_retries, "failed_attempts": store.network_failures, "exhausted_failures": store.exhausted_failures, "http_request_count": store.http_request_count, "connection_reuse_count_observable": store.connection_reuse_count, "connection_new_count": store.connection_new_count, "redirect_count": store.redirect_count}
        report = {"pinned_bf16_provenance": {"repository": manifest["source"]["repository"], "revision": manifest["resolved_revision"], "manifest_sha256": fsha(MANIFEST), "index_sha256": fsha(INDEX), "objects": store.weights}, "transport_preflight": transport, "download": {"exact_downloaded_bytes": store.bytes_fetched, "network_bytes_received": store.network_bytes_received, "expert_bytes_fetched": store.expert_bytes_fetched, "expert_tensor_payload_bytes_fetched": store.expert_tensor_payload_bytes_fetched, "dense_payload_bytes_reused": store.dense_payload_bytes_reused, "dense_cache_disk_bytes_reused": validation["dense_disk_bytes"], "dense_cache_hits": store.dense_cache_hits, "peak_staging_bytes": store.peak_staging_bytes, "peak_dedicated_disk_bytes": store.peak_bytes, "cap_bytes": CAP_BYTES, "range_fetch_count": len(store.fetches), "coalesced_range_count": store.coalesced_range_count, "coalesced_tensor_count": store.coalesced_tensor_count, "network": network}, "dense_tensor_records": dense, "unique_bf16_layer_experts_fetched": len(store.unique_layer_experts_fetched), "expert_tensor_count_fetched": len(paired["expert_rows"]), "paired_layer_accounting": paired["layers"], "first_router_divergence": router, "router_comparison_full_prefix": router_comparison, "tap_metrics_final_position": tap_metrics, "final_hidden_metrics": hidden_metrics, "logit_metrics": logit_metrics, "top1": {"q4": int(np.argmax(q4_last)), "bf16": int(np.argmax(bf_last)), "equal": int(np.argmax(q4_last)) == int(np.argmax(bf_last))}, "top1_top2_margin": {"q4": margin(q4_last), "bf16": margin(bf_last), "delta_bf16_minus_q4": margin(bf_last) - margin(q4_last)}, "top5": {"q4": top5(q4_last), "bf16": top5(bf_last), "overlap": len(set(top5(q4_last)) & set(top5(bf_last)))}, "deterministic_rerun": deterministic, "no_nan_inf": finite_ok, "no_routed_expert_leak": leak_ok, "memory": {"before": before, "after": after, "bf16_max_logical_live_bytes": primary["max_live"], "q4_max_logical_live_bytes": q4["max_live"]}, "causal_status": "NOT_CAUSAL: a single pinned-upstream P1_t01 paired state measures target-output drift only; the BF16 reader/math implementation and one-state scope preclude a quantization-causality claim."}
        dump(out / "bf16-control.json", report); dump(out / "range-fetches.json", store.fetches); dump(out / "network-events.json", store.network_events)
        del primary, rerun, q4, q4_saved, backbone
        gc.collect(); mx.clear_cache(); store.write_progress("gate_b_complete"); store.close()
        return report
    except Exception:
        dump(out / "range-fetches.json", store.fetches); dump(out / "network-events.json", store.network_events)
        dump(out / "gate-b-interrupted.json", {"unique_bf16_layer_experts_fetched": len(store.unique_layer_experts_fetched), "expert_bytes_fetched": store.expert_bytes_fetched, "expert_tensor_payload_bytes_fetched": store.expert_tensor_payload_bytes_fetched, "dense_payload_bytes_reused": store.dense_payload_bytes_reused, "network_retries": store.network_retries, "network_failed_attempts": store.network_failures, "network_exhausted_failures": store.exhausted_failures, "http_request_count": store.http_request_count, "connection_reuse_count_observable": store.connection_reuse_count, "peak_staging_bytes": store.peak_staging_bytes, "peak_cache_staging_bytes": store.peak_bytes, "last_successful_fetch_timestamp": store.last_successful_fetch_timestamp})
        store.write_progress("gate_b_interrupted"); store.close()
        raise


def main():
    out = OUTROOT / utc_id(); out.mkdir(parents=True, exist_ok=False)
    token_ids = p1_tokens()
    provenance = {"checkpoint": "LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001", "run_id_utc": out.name, "runtime": {"python_executable": sys.executable, "python_version": sys.version, "platform": platform.platform(), "mlx_version": mx.__version__}, "script": str(Path(__file__)), "script_sha256": fsha(__file__), "inputs": {"frozen_p1_t01": str(FROZEN), "frozen_p1_t01_sha256": fsha(FROZEN), "trace": str(TRACE), "trace_sha256": fsha(TRACE), "preflight_manifest": str(MANIFEST), "preflight_manifest_sha256": fsha(MANIFEST), "reused_gate_a_output": str(REUSE_GATE_A_OUTPUT), "reused_gate_a_parity": str(REUSE_GATE_A_PARITY), "reused_dense_cache": str(REUSE_DENSE)}, "p1_token_count": len(token_ids), "gate_a_execution": "NOT_RERUN_REUSED_PROVEN_PASS", "gate_b_io_schedule": "layer -> union unique expert -> all assigned positions in paired streams", "prohibitions_observed": ["no DFlash proposals", "no full E2E", "no model/mapping/acceptance changes", "no full upstream snapshot", "no memory/performance remediation", "no quantization-causality claim", "no Git"]}
    dump(out / "provenance.json", provenance)
    if mx.__version__ != "0.31.2": raise RuntimeError(f"PINNED_RUNTIME_FAIL: MLX {mx.__version__}")
    validation = validate_reused_evidence(); dump(out / "reuse-validation.json", validation)
    accounting = dry_accounting(validation); dump(out / "dry-accounting.json", accounting)
    if not accounting["dedicated_cache_staging_within_12_gib"] or accounting["retains_all_expert_payloads"]:
        dump(out / "summary.json", {"checkpoint": provenance["checkpoint"], "classification": "CONTROL_CACHE_DRY_ACCOUNTING_STOP", "dry_accounting": accounting, "bf16_accessed": False, "gate": "STOP", "evidence_directory": str(out)})
        print(json.dumps({"classification": "CONTROL_CACHE_DRY_ACCOUNTING_STOP", "evidence": str(out)}, indent=2)); return
    if "--dry-run" in sys.argv[1:]:
        dump(out / "summary.json", {"checkpoint": provenance["checkpoint"], "classification": "GATE_B_DRY_ACCOUNTING_PASS", "dry_accounting": accounting, "bf16_accessed": False, "gate": "DRY_RUN_COMPLETE", "evidence_directory": str(out)})
        print(json.dumps({"classification": "GATE_B_DRY_ACCOUNTING_PASS", "evidence": str(out)}, indent=2)); return
    gates = json.loads(REUSE_GATE_A_PARITY.read_text())["gates"]
    candidate_flags = [x for x in sys.argv[1:] if x.startswith("--transport-microbenchmark-candidate=")]
    if len(candidate_flags) > 1: raise RuntimeError("multiple transport microbenchmark candidate flags")
    candidate_mib = None if not candidate_flags else int(candidate_flags[0].split("=", 1)[1])
    try:
        bf = bf_gate(out, token_ids, validation, transport_microbenchmark_only="--transport-microbenchmark" in sys.argv[1:], transport_microbenchmark_candidate_mib=candidate_mib)
    except Exception as exc:
        classification = "NETWORK_RANGE_FETCH_FAIL" if "NETWORK_RANGE_FETCH_FAIL" in str(exc) else "GATE_B_MECHANICAL_EXECUTION_FAIL"
        interrupted = json.loads((out / "gate-b-interrupted.json").read_text()) if (out / "gate-b-interrupted.json").exists() else None
        dump(out / "summary.json", {"checkpoint": provenance["checkpoint"], "classification": classification, "error": f"{type(exc).__name__}: {exc}", "adapter_parity": gates, "dry_accounting": accounting, "gate_b_interrupted": interrupted, "gate": "STOP", "evidence_directory": str(out)})
        print(json.dumps({"classification": classification, "error": str(exc), "evidence": str(out)}, indent=2)); return
    if bf.get("transport_microbenchmark_only"):
        micro = bf["transport_microbenchmark"]
        dump(out / "summary.json", {"checkpoint": provenance["checkpoint"], "classification": micro["classification"], "adapter_parity": gates, "transport_microbenchmark": micro, "gate_b_launched": False, "gate": "STOP", "evidence_directory": str(out)})
        print(json.dumps({"classification": micro["classification"], "evidence": str(out)}, indent=2)); return
    if bf.get("transport_preflight_stop"):
        dump(out / "summary.json", {"checkpoint": provenance["checkpoint"], "classification": "TRANSPORT_PREFLIGHT_TOO_SLOW", "adapter_parity": gates, "dry_accounting": accounting, "transport_preflight": bf["transport_preflight"], "gate": "STOP", "evidence_directory": str(out)})
        print(json.dumps({"classification": "TRANSPORT_PREFLIGHT_TOO_SLOW", "evidence": str(out)}, indent=2)); return
    classification = "LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS" if bf["deterministic_rerun"] and bf["no_nan_inf"] and bf["no_routed_expert_leak"] and bf["download"]["peak_dedicated_disk_bytes"] <= CAP_BYTES else "LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_FAIL_GATE"
    dump(out / "summary.json", {"checkpoint": provenance["checkpoint"], "classification": classification, "adapter_parity": gates, "bf16_provenance": bf["pinned_bf16_provenance"], "bytes_fetched": bf["download"]["exact_downloaded_bytes"], "unique_bf16_layer_experts_actually_fetched": bf["unique_bf16_layer_experts_fetched"], "expert_bytes_fetched": bf["download"]["expert_bytes_fetched"], "dense_bytes_reused": bf["download"]["dense_payload_bytes_reused"], "dense_cache_disk_bytes_reused": bf["download"]["dense_cache_disk_bytes_reused"], "network_retries": bf["download"]["network"]["retries"], "network_failures": bf["download"]["network"]["failed_attempts"], "network_exhausted_failures": bf["download"]["network"]["exhausted_failures"], "cache_staging_peak": bf["download"]["peak_dedicated_disk_bytes"], "staging_peak": bf["download"]["peak_staging_bytes"], "first_router_divergence": bf["first_router_divergence"], "tap_metrics": bf["tap_metrics_final_position"], "final_hidden_metrics": bf["final_hidden_metrics"], "logit_metrics": bf["logit_metrics"], "top1": bf["top1"], "margins": bf["top1_top2_margin"], "top5": bf["top5"], "deterministic": bf["deterministic_rerun"], "finite": bf["no_nan_inf"], "root_observation": "Measured paired P1_t01 difference between local Q4 target values and a pinned current-upstream BF16 control; no causal attribution is made.", "causal_status": bf["causal_status"], "gate": "COMPLETE" if classification.endswith("_PASS") else "STOP", "evidence_directory": str(out)})
    print(json.dumps({"classification": classification, "evidence": str(out)}, indent=2))

if __name__ == "__main__": main()
