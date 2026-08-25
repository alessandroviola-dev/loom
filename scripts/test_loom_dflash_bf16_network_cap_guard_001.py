#!/usr/bin/env python3
"""Synthetic unit tests for the BF16 range-cache network-cap guard.

The production module's MLX-only imports are stubbed so these tests exercise no
model code.  All range responses are synthetic and HTTPSConnection.request is
patched to fail if any real network dispatch is attempted.
"""
from __future__ import annotations

import hashlib
import http.client
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def install_import_stubs():
    """Allow importing the shared transport module without MLX/model loading."""
    mlx = types.ModuleType("mlx")
    core = types.ModuleType("mlx.core")
    core.__version__ = "synthetic"
    core.load = lambda path: {"x": types.SimpleNamespace(shape=(1,))}
    core.eval = lambda *values: None
    nn = types.ModuleType("mlx.nn")
    nn.Module = object
    nn.RMSNorm = lambda *a, **k: None
    nn.RoPE = lambda *a, **k: None
    utils = types.ModuleType("mlx.utils")
    utils.tree_flatten = lambda value: []
    mlx.core, mlx.nn, mlx.utils = core, nn, utils
    sys.modules.update({"mlx": mlx, "mlx.core": core, "mlx.nn": nn, "mlx.utils": utils})
    mlx_lm = types.ModuleType("mlx_lm")
    models = types.ModuleType("mlx_lm.models")
    activations = types.ModuleType("mlx_lm.models.activations")
    activations.swiglu = lambda value: value
    base = types.ModuleType("mlx_lm.models.base")
    base.create_attention_mask = lambda *a, **k: None
    base.scaled_dot_product_attention = lambda *a, **k: None
    sys.modules.update({"mlx_lm": mlx_lm, "mlx_lm.models": models,
                        "mlx_lm.models.activations": activations,
                        "mlx_lm.models.base": base})
    oracle = types.ModuleType("loom_30b_moe_dflash_target_interface_001")
    target = types.ModuleType("loom_30b_moe_first_greedy_generation_001")
    target.LAYERS, target.PROJS = 48, ("gate_proj", "up_proj", "down_proj")
    dflash = types.ModuleType("loom_dflash_greedy_e2e_001")
    sys.modules.update({"loom_30b_moe_dflash_target_interface_001": oracle,
                        "loom_30b_moe_first_greedy_generation_001": target,
                        "loom_dflash_greedy_e2e_001": dflash})


install_import_stubs()
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loom_dflash_unquantized_target_p1t01_range_control_001 as rc
import loom_dflash_bf16_tap_drafter_probe_001 as probe


def production_store(root, *, byte_cap, request_cap):
    manifest = {"resolved_revision": "synthetic", "artifacts": {"weights": [
        {"filename": "synthetic.safetensors", "bytes": 100, "sha256": "0" * 64}
    ]}}
    return rc.RangeStore(root / "staging", root / "dense", manifest, {"weight_map": {}},
                         {"dense_files": [], "dense_disk_bytes": 0}, root / "progress.json",
                         network_byte_cap=byte_cap, network_request_cap=request_cap)


class SyntheticRangeStore(rc.RangeStore):
    """Calls the production reservation step but returns only local bytes."""
    def __init__(self, root, *, byte_cap, request_cap, outcomes=("success",), ledger=None):
        manifest = {"resolved_revision": "synthetic", "artifacts": {"weights": [
            {"filename": "synthetic.safetensors", "bytes": 100, "sha256": "0" * 64}
        ]}}
        super().__init__(root / "staging", root / "dense", manifest, {"weight_map": {}},
                         {"dense_files": [], "dense_disk_bytes": 0}, root / "progress.json",
                         network_byte_cap=byte_cap, network_request_cap=request_cap,
                         network_ledger_path=ledger)
        self.outcomes = list(outcomes)
        self.synthetic_dispatches = 0
    def _raw_get(self, url, start, length, purpose, attempt, redirect):
        # This is the exact production pre-dispatch charge, followed only by a
        # synthetic response; no socket, HTTP client, or network resolver runs.
        self._reserve_network_dispatch("synthetic.safetensors", start, length, purpose, attempt, redirect)
        self.synthetic_dispatches += 1
        outcome = self.outcomes.pop(0) if self.outcomes else "success"
        if outcome == "failure":
            raise OSError("synthetic transport failure")
        return 206, {"content-range": f"bytes {start}-{start + length - 1}/100"}, b"x" * length


class NetworkCapGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.real_network_dispatches = 0
        self.request_patch = patch.object(http.client.HTTPSConnection, "request", self._real_network_called)
        self.request_patch.start()
    def tearDown(self):
        self.request_patch.stop()
        self.tmp.cleanup()
    def _real_network_called(self, *args, **kwargs):
        self.real_network_dispatches += 1
        raise AssertionError("REAL_NETWORK_DISPATCH_FORBIDDEN")
    def assert_zero_real_network(self):
        self.assertEqual(self.real_network_dispatches, 0)

    def test_exact_boundary_allows_one_dispatch(self):
        store = SyntheticRangeStore(self.root / "boundary", byte_cap=10, request_cap=1)
        self.assertEqual(store.request("synthetic.safetensors", 0, 10, "unit"), b"x" * 10)
        self.assertEqual((store.network_accounted_bytes, store.network_accounted_requests), (10, 1))
        self.assertEqual(store.synthetic_dispatches, 1)
        self.assert_zero_real_network()

    def test_byte_cap_rejects_before_dispatch(self):
        store = production_store(self.root / "byte-reject", byte_cap=9, request_cap=1)
        with self.assertRaisesRegex(rc.NetworkCapAbort, r"NETWORK_CAP_ABORT current_network_bytes=0 current_network_requests=0 proposed_network_bytes=10 proposed_network_requests=1 network_byte_cap=9 network_request_cap=1"):
            store.request("synthetic.safetensors", 0, 10, "unit")
        self.assertEqual(store.http_request_count, 0)
        self.assertEqual((store.network_accounted_bytes, store.network_accounted_requests), (0, 0))
        self.assertEqual(store.network_events[-1]["event"], "NETWORK_CAP_ABORT")
        self.assert_zero_real_network()

    def test_request_cap_rejects_before_dispatch(self):
        store = production_store(self.root / "request-reject", byte_cap=10, request_cap=0)
        with self.assertRaisesRegex(rc.NetworkCapAbort, r"NETWORK_CAP_ABORT.*network_request_cap=0"):
            store.request("synthetic.safetensors", 0, 1, "unit")
        self.assertEqual(store.http_request_count, 0)
        self.assertEqual((store.network_accounted_bytes, store.network_accounted_requests), (0, 0))
        self.assert_zero_real_network()

    def test_persistent_cache_hit_has_zero_network_cost(self):
        # Exercise the production PersistentStore cache-validation path, not a
        # synthetic accounting shortcut.  The tiny staged BF16 file is local.
        old_cache, old_run_id = probe.CACHE, probe.RUN_ID
        try:
            probe.CACHE, probe.RUN_ID = self.root / "persistent-cache", "unit"
            manifest = {"resolved_revision": "synthetic", "artifacts": {"weights": []}}
            store = probe.PersistentStore(manifest, {"weight_map": {}},
                                          {"dense_files": [], "dense_disk_bytes": 0},
                                          self.root / "persistent-progress.json",
                                          network_byte_cap=0, network_request_cap=0)
            names = ["model.layers.7.mlp.experts.11.gate_proj.weight"]
            directory = store._expert_dir(7, 11); directory.mkdir(parents=True)
            header = json.dumps({"x": {"dtype": "BF16", "shape": [1], "data_offsets": [0, 2]}},
                                separators=(",", ":")).encode()
            tensor = directory / "gate_proj.safetensors"
            tensor.write_bytes((len(header)).to_bytes(8, "little") + header + bytes(2))
            info = rc.staged_tensor_metadata(tensor)
            (directory / "manifest.json").write_text(json.dumps({
                "model": "Qwen/Qwen3-30B-A3B", "revision": probe.REVISION,
                "layer": 7, "expert": 11, "tensor_names": names,
                "tensors": [{"name": names[0], "filename": tensor.name, "file_bytes": info["file_bytes"],
                             "file_sha256": info["sha256"], "payload_bytes": 2, "shape": [1],
                             "shard": "synthetic.safetensors", "payload_offset": 0,
                             "object_sha256": "0" * 64}],
            }))
            hit = store._load_cached(7, 11, names)
            self.assertIsNotNone(hit)
            self.assertEqual(store.cache_hits, 1)
            self.assertEqual((store.network_accounted_bytes, store.network_accounted_requests), (0, 0))
            self.assertEqual(store.network_events[-1]["event"], "cache_hit")
            self.assert_zero_real_network()
            store.close()
        finally:
            probe.CACHE, probe.RUN_ID = old_cache, old_run_id

    def test_retry_is_bounded_and_each_attempt_is_accounted_once(self):
        store = SyntheticRangeStore(self.root / "retry", byte_cap=10, request_cap=2,
                                    outcomes=("failure", "success"))
        self.assertEqual(store.request("synthetic.safetensors", 0, 5, "unit"), b"x" * 5)
        self.assertEqual(store.synthetic_dispatches, 2)
        self.assertEqual(store.network_retries, 1)
        self.assertEqual(store.network_failures, 1)
        self.assertEqual((store.network_accounted_bytes, store.network_accounted_requests), (10, 2))
        reservations = [x for x in store.network_ledger_events if x["event"] == "network_dispatch_reserved"]
        self.assertEqual([(x["attempt"], x["accounted_network_bytes"]) for x in reservations], [(1, 5), (2, 5)])
        self.assert_zero_real_network()

    def test_abort_preserves_valid_partial_cache_and_resume_ledger(self):
        cache = self.root / "cache"; cache.mkdir(parents=True)
        valid = cache / "expert-000.complete"; valid.write_bytes(b"validated-cache-entry")
        pending = cache / "expert-001.partial"; pending.write_bytes(b"incomplete-but-preserved")
        hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (valid, pending)}
        ledger = self.root / "resume-ledger.json"
        blocked = SyntheticRangeStore(self.root / "blocked", byte_cap=4, request_cap=1, ledger=ledger)
        with self.assertRaises(rc.NetworkCapAbort):
            blocked.request("synthetic.safetensors", 0, 5, "unit")
        self.assertEqual(blocked.synthetic_dispatches, 0)
        self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (valid, pending)})
        resumed = SyntheticRangeStore(self.root / "resumed", byte_cap=4, request_cap=1, ledger=ledger)
        resumed.record_cache_hit({"path": str(valid)})
        self.assertEqual((resumed.network_accounted_bytes, resumed.network_accounted_requests), (0, 0))
        self.assertTrue(valid.is_file())
        self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (valid, pending)})
        ledger_row = json.loads(ledger.read_text())
        self.assertEqual((ledger_row["network_accounted_bytes"], ledger_row["network_accounted_requests"]), (0, 0))
        self.assert_zero_real_network()


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NetworkCapGuardTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(json.dumps({"classification": "BF16_NETWORK_CAP_GUARD_PASS", "tests": result.testsRun,
                      "real_network_dispatches": 0}, sort_keys=True))
