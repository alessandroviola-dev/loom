#!/usr/bin/env python3
"""Bounded preregistered Q4-vs-pinned-BF16 DFlash causal pilot; no E2E."""
from __future__ import annotations

import gc
import hashlib
import json
import os
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import mlx.core as mx
import numpy as np

import loom_dflash_unquantized_target_p1t01_range_control_001 as rc
import loom_dflash_bf16_tap_drafter_probe_001 as probe
import loom_30b_moe_dflash_target_interface_001 as oracle
import loom_30b_moe_first_greedy_generation_001 as target
import loom_dflash_greedy_e2e_001 as dflash
import loom_dflash_q4_baseline_replay_shared_001 as q4_replay

ROOT = Path(__file__).resolve().parents[1]
OUTROOT = ROOT / "results-local/research/dflash-representable-bf16-target-causal-pilot-001"
PREFLIGHT = ROOT / "results-local/research/dflash-representable-bf16-target-control-preflight-001/20260825T115402Z"
CORPUS = ROOT / "results-local/research/dflash-masked-reference-parity-001/20260824T142830Z/corpus.json"
FREEZE = ROOT / "results-local/research/dflash-target-continuation-freeze-001/20260824T145202Z/target-continuation-reference.json"
TRACE = ROOT / "results-local/moe/routing-cache-trace-001/20260824T090555Z/generations.json"
EXTERNAL = Path("<external-archive>")
CACHE = EXTERNAL / "bf16-cache/Qwen3-30B-A3B/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39"
CAP_BYTES, CAP_REQUESTS = 8 * 1024**3, 1024
TAPS = (1, 12, 23, 34, 45)
SOURCE_HASHES = {
    "scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py": "dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376",
    "scripts/loom_dflash_bf16_tap_drafter_probe_001.py": "7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f",
    "scripts/test_loom_dflash_bf16_network_cap_guard_001.py": "7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae",
}
# Fixed execution order. Do not derive or sort this list.
ORDER = (("P3_t01", 2, 1620, 64), ("P1_t32", 6, 326, 79), ("P2_t16", 3, 994, 74))


def utc_id(): return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
def sha_file(path): return rc.fsha(path)
def raw_sha(value): return hashlib.sha256(np.ascontiguousarray(np.asarray(value)).tobytes()).hexdigest()
def dump(path, value): rc.atomic_dump(path, value)
def rank(logits, row): return int(1 + np.count_nonzero(logits > logits[row]))


def check_preconditions(out):
    hashes = {path: sha_file(ROOT / path) for path in SOURCE_HASHES}
    if hashes != SOURCE_HASHES:
        raise RuntimeError(f"NETWORK_GUARD_SOURCE_SHA256_MISMATCH: {hashes}")
    if mx.__version__ != "0.31.2":
        raise RuntimeError(f"PINNED_RUNTIME_FAIL: {mx.__version__}")
    if not EXTERNAL.is_dir() or not CACHE.is_dir() or not os.access(EXTERNAL, os.W_OK):
        raise RuntimeError("EXTERNAL_BF16_CACHE_OR_STORAGE_UNAVAILABLE")
    free = shutil.disk_usage(EXTERNAL).free
    if free < 100 * 1024**3:
        raise RuntimeError("EXTERNAL_BF16_STORAGE_FREE_SPACE_GATE_FAIL")
    ledger = out / "network-ledger.json"
    if ledger.exists():
        old = json.loads(ledger.read_text())
        if old.get("ledger_version") != 1 or old.get("network_byte_cap") != CAP_BYTES or old.get("network_request_cap") != CAP_REQUESTS:
            raise RuntimeError("AGGREGATE_LEDGER_CONFIGURATION_MISMATCH")
    else:
        dump(ledger, {"ledger_version": 1, "network_byte_cap": CAP_BYTES, "network_request_cap": CAP_REQUESTS,
                      "network_accounted_bytes": 0, "network_accounted_requests": 0,
                      "network_cap_abort_count": 0, "events": []})
    row = json.loads(ledger.read_text())
    if int(row["network_accounted_bytes"]) < 0 or int(row["network_accounted_requests"]) < 0:
        raise RuntimeError("AGGREGATE_LEDGER_NEGATIVE_COUNTER")
    return {"guard_source_sha256": hashes, "runtime_mlx": mx.__version__,
            "external_cache": str(CACHE), "external_free_bytes": free,
            "external_free_gib": free / 1024**3, "ledger_start": row}


def selected_inputs():
    selected = json.loads((PREFLIGHT / "selected-states.json").read_text())["selected_states"]
    selected_by_key = {(x["state_id"], int(x["continuation_position"])): x for x in selected}
    corpus = {x["state_id"]: x for x in json.loads(CORPUS.read_text())["states"]}
    freeze = json.loads(FREEZE.read_text())
    decisions = {}
    for row in freeze["decisions"]: decisions.setdefault(row["state_id"], []).append(row)
    trace = {x["prompt_id"]: x for x in json.loads(TRACE.read_text())["runs"]}
    result = []
    for state_id, pos, frozen_token, length in ORDER:
        meta, state = selected_by_key[(state_id, pos)], corpus[state_id]
        rows = sorted(decisions[state_id], key=lambda x: int(x["continuation_position"]))
        if len(rows) != 7 or [int(x["continuation_position"]) for x in rows] != list(range(1, 8)):
            raise RuntimeError(f"FROZEN_CONTINUATION_PROVENANCE_FAIL: {state_id}")
        if int(rows[pos - 1]["target_token_id"]) != frozen_token or int(state["context_length"]) + pos - 1 != length:
            raise RuntimeError(f"SELECTED_STATE_GEOMETRY_OR_LABEL_FAIL: {state_id}")
        trace_row = trace[state["prompt_id"]]
        base_outputs = [int(x["output_token_id"]) for x in trace_row["generation"]["records"][:int(state["token_index"]) - 1]]
        ids = list(map(int, trace_row["prompt_token_ids"])) + base_outputs + [int(x["target_token_id"]) for x in rows[:pos - 1]]
        # Preflight uses this portable CSV token sequence commitment.
        token_sha = hashlib.sha256(",".join(map(str, ids)).encode()).hexdigest()
        if len(ids) != length or token_sha != meta["input_token_ids_sha256"] or ids[-1] != int(meta["anchor_token_id"]):
            raise RuntimeError(f"SELECTED_INPUT_PROVENANCE_FAIL: {state_id}")
        result.append({"state_id": state_id, "position": pos, "frozen_token": frozen_token,
                       "prefix_length": length, "anchor_token": ids[-1], "ids": ids,
                       "input_sha256": token_sha, "frozen_logit_sha256": rows[pos - 1]["logits_sha256"],
                       "retained_tap": ROOT / "results-local/research/dflash-masked-reference-parity-001/20260824T142830Z" / state["tap_file"]})
    return result


def save_target(path, result, ids):
    taps = np.stack([result["taps"][x][0].astype(np.float32, copy=False) for x in TAPS])
    routers = {f"router_logits_{x['layer']}": x["logits"] for x in result["routers"]}
    routers |= {f"router_ids_{x['layer']}": x["ids"] for x in result["routers"]}
    routers |= {f"router_weights_{x['layer']}": x["weights"] for x in result["routers"]}
    np.savez_compressed(path, taps=taps, final_hidden=result["final_hidden"][0], logits=result["logits"][0, -1],
                        input_token_ids=np.asarray(ids, dtype=np.int64), tap_layers_1_based=np.asarray(TAPS, dtype=np.int32), **routers)
    return taps, np.asarray(result["logits"][0, -1], dtype=np.float32)


def q4_baseline(state, out):
    """Replay the frozen producer segmentation, never a fresh full-prefix path."""
    return q4_replay.replay_one({"state_id": state["state_id"]}, out)


def bf_forward_single(store, backbone, ids):
    x = backbone.embed_tokens(mx.array([ids], dtype=mx.int32)); mx.eval(x)
    cache = [target.BF16KVCache() for _ in range(target.LAYERS)]
    mask = rc.create_attention_mask(x, cache[0]); taps, routers, all_rows = {}, [], []
    logical_live = max_live = 0
    for layer_no, layer in enumerate(backbone.layers):
        h = x + oracle.attention_with_bf16_cache(layer.self_attn, layer.input_layernorm(x), mask, cache[layer_no])
        z = layer.post_attention_layernorm(h); mx.eval(h, z)
        router_logits, selected, weights = target.route(layer.external_moe.gate, z); mx.eval(router_logits, selected, weights)
        ids_host, weights_host = np.asarray(selected).astype(np.int32, copy=True), rc.bf_host(weights).copy()
        routers.append({"layer": layer_no, "logits": rc.bf_host(router_logits).copy(), "ids": ids_host, "weights": weights_host})
        union_ids = sorted(set(ids_host.reshape(-1).tolist())); store.set_layer(layer_no, union_ids)
        serial = [[None] * rc.TOP_K for _ in range(ids_host.shape[1])]
        for expert in union_ids:
            names = [f"model.layers.{layer_no}.mlp.experts.{expert}.{projection}.weight" for projection in target.PROJS]
            loaded, _, rows = store.expert(layer_no, expert, names); weights_by_projection = {p: loaded[n] for p, n in zip(target.PROJS, names)}
            store.unique_layer_experts_fetched.add((layer_no, expert)); logical_live += rc.BF16_EXPERT_BYTES; max_live = max(max_live, logical_live)
            try:
                for position in np.where(np.any(ids_host[0] == expert, axis=1))[0].tolist():
                    for rank_, selected_id in enumerate(ids_host[0, position].tolist()):
                        if selected_id == expert:
                            y = rc.bf_direct(z[:, position:position + 1, :], weights_by_projection); mx.eval(y)
                            serial[position][rank_] = mx.array(rc.bf_host(y), dtype=mx.bfloat16); mx.eval(serial[position][rank_]); del y
                all_rows.extend(rows)
            finally:
                del weights_by_projection, loaded; logical_live -= rc.BF16_EXPERT_BYTES
            store.complete_expert(layer_no, expert)
        positions = []
        for outputs in serial:
            if any(v is None for v in outputs): raise RuntimeError("BF16_SERIAL_EXPERT_ASSIGNMENT_INCOMPLETE")
            stacked = mx.stack(outputs, axis=-2); mixed = (stacked * weights[:, len(positions):len(positions)+1, :, None]).sum(axis=-2); mx.eval(mixed)
            positions.append(mixed); del stacked, mixed
        moe = mx.concatenate(positions, axis=1); x = h + moe; mx.eval(x)
        if layer_no + 1 in TAPS: taps[layer_no + 1] = rc.bf_host(x).copy()
        del serial, positions, moe, h, z, router_logits, selected, weights
        mx.clear_cache()
    norm = backbone.norm(x); mx.eval(norm); logits = backbone.lm_head(norm); mx.eval(logits)
    result = {"taps": taps, "routers": routers, "final_hidden": rc.bf_host(norm).copy(), "logits": rc.bf_host(logits).copy(), "final_live": logical_live, "max_live": max_live, "expert_rows": all_rows}
    del x, norm, logits, cache
    return result


def label_score(logits, label, inverse, mapping):
    if label < 0 or label >= inverse.size or inverse[label] < 0:
        return {"representable": False, "rank": None, "top1": None, "top5": None, "top10": None, "top50": None, "top100": None, "exact_proposal_match": None}
    row = int(inverse[label]); r = rank(logits, row)
    return {"representable": True, "draft_row": row, "mapping_roundtrip": int(mapping[row]) == label,
            "rank": r, "top1": r == 1, "top5": r <= 5, "top10": r <= 10, "top50": r <= 50, "top100": r <= 100,
            "exact_proposal_match": int(np.argmax(logits)) == row}


def dflash_scores(q4_taps, bf_taps, anchor, frozen, bf_top1):
    drafter = dflash.Drafter()
    q4 = drafter.propose_debug(q4_taps, anchor); bf = drafter.propose_debug(bf_taps, anchor)
    q4_logits, bf_logits = np.asarray(q4["logits"], dtype=np.float32)[0, 1], np.asarray(bf["logits"], dtype=np.float32)[0, 1]
    mapping = np.asarray(drafter.target_ids_by_draft_row, dtype=np.int64)
    inverse = np.full(151936, -1, dtype=np.int64); inverse[mapping] = np.arange(mapping.size, dtype=np.int64)
    if np.unique(mapping).size != 32000 or not np.array_equal(np.sort(mapping), np.flatnonzero(drafter.t2d)):
        raise RuntimeError("CORRECTED_D2T_MAPPING_INVARIANT_FAIL")
    result = {"full_32k_q4_vs_bf16": rc.metric(q4_logits, bf_logits),
              "q4_proposal_token": int(q4["target_ids"][0]), "bf16_proposal_token": int(bf["target_ids"][0]),
              "proposal_changed": int(q4["target_ids"][0]) != int(bf["target_ids"][0]),
              "frozen_label": {"token": frozen, "q4_taps": label_score(q4_logits, frozen, inverse, mapping), "bf16_taps": label_score(bf_logits, frozen, inverse, mapping)},
              "bf16_label": {"token": bf_top1, "q4_taps": label_score(q4_logits, bf_top1, inverse, mapping), "bf16_taps": label_score(bf_logits, bf_top1, inverse, mapping)},
              "mapping": {"decode": "target_id = draft_row + d2t[draft_row]", "supported_targets": int(drafter.t2d.sum())}}
    del drafter; mx.clear_cache()
    return result


def bf_treatment(state, out, q4_taps, ledger):
    validation = rc.validate_reused_evidence()
    probe.RUN_ID = f"{out.parent.parent.name}-{state['state_id']}"
    manifest, index = json.loads(rc.MANIFEST.read_text()), json.loads(rc.INDEX.read_text())
    store = probe.PersistentStore(manifest, index, validation, out / "bf16-progress.json", CAP_BYTES, CAP_REQUESTS, ledger)
    try:
        store.catalog()
        cfg = json.loads((rc.PREFLIGHT / "source-config.json").read_text())
        backbone, _ = rc.load_bf_backbone(store, cfg, index)
        if store.dense_cache_hits != 435: raise RuntimeError("BF16_DENSE_CACHE_REUSE_GATE_FAIL")
        primary = bf_forward_single(store, backbone, state["ids"])
        taps, logits = save_target(out / "bf16-target.npz", primary, state["ids"])
        tap_metrics = [{"layer": layer, **rc.metric(q4_taps[i], taps[i])} for i, layer in enumerate(TAPS)]
        dscore = dflash_scores(q4_taps, taps, state["anchor_token"], state["frozen_token"], int(np.argmax(logits)))
        report = {"bf16_top1": int(np.argmax(logits)), "finite": rc.finite(logits) and all(rc.finite(v) for v in primary["taps"].values()),
                  "no_routed_expert_leak": primary["final_live"] == 0, "tap_drift": tap_metrics,
                  "dflash": dscore,
                  "cache": {"hits": store.cache_hits, "misses": store.cache_misses, "newly_persisted": store.experts_newly_persisted,
                            "expert_hdd_bytes": store.expert_hdd_bytes, "network_payload_bytes": store.expert_tensor_payload_bytes_fetched,
                            "retries": store.network_retries},
                  "network": {"accounted_bytes": store.network_accounted_bytes, "accounted_requests": store.network_accounted_requests,
                              "cap_abort_count": store.network_cap_abort_count, "successful_range_requests_this_state": len(store.fetches)}}
        dump(out / "bf16-treatment.json", report)
        if not report["finite"] or not report["no_routed_expert_leak"]: raise RuntimeError("BF16_FORWARD_INTEGRITY_FAIL")
        return report
    finally:
        dump(out / "range-fetches.json", store.fetches); dump(out / "network-events.json", store.network_events)
        store.close(); gc.collect(); mx.clear_cache()


def aggregate(out, completed, classification, preconditions, failure=None):
    ledger = json.loads((out / "network-ledger.json").read_text())
    report = {"checkpoint": "LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001", "classification": classification,
              "fixed_execution_order": [x[0] for x in ORDER], "completed_states": completed,
              "aggregate_network": {"accounted_bytes": ledger["network_accounted_bytes"], "accounted_requests": ledger["network_accounted_requests"],
                                    "retries": sum(x.get("bf16", {}).get("cache", {}).get("retries", 0) for x in completed),
                                    "cap_abort_count": ledger.get("network_cap_abort_count", 0), "byte_cap": CAP_BYTES, "request_cap": CAP_REQUESTS},
              "aggregate_cache": {"hits": sum(x.get("bf16", {}).get("cache", {}).get("hits", 0) for x in completed),
                                  "misses": sum(x.get("bf16", {}).get("cache", {}).get("misses", 0) for x in completed)},
              "preconditions": preconditions, "failure": failure, "evidence_directory": str(out)}
    dump(out / "summary.json", report)
    return report


def main():
    out = OUTROOT / utc_id(); out.mkdir(parents=True, exist_ok=False)
    preconditions = check_preconditions(out)
    states = selected_inputs(); dump(out / "preflight.json", preconditions); dump(out / "selected-inputs.json", [{k: v for k, v in s.items() if k not in ("ids", "retained_tap")} for s in states])
    completed = []
    try:
        for state in states:
            state_out = out / state["state_id"]; state_out.mkdir()
            q4_taps, _, q4_report = q4_baseline(state, state_out)
            bf_report = bf_treatment(state, state_out, q4_taps, out / "network-ledger.json")
            completed.append({"state_id": state["state_id"], "q4_baseline": q4_report, "bf16": bf_report})
            dump(out / "progress.json", {"completed_state_ids": [x["state_id"] for x in completed], "next_fixed_state": next((x[0] for x in ORDER if x[0] not in {r["state_id"] for r in completed}), None)})
    except rc.NetworkCapAbort as exc:
        aggregate(out, completed, "BF16_TARGET_PILOT_NETWORK_CAP_ABORT", preconditions, {"type": type(exc).__name__, "error": str(exc), "row": exc.row})
        print(json.dumps({"classification": "BF16_TARGET_PILOT_NETWORK_CAP_ABORT", "evidence": str(out)}, indent=2)); return
    except Exception as exc:
        aggregate(out, completed, "INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP", preconditions, {"type": type(exc).__name__, "error": str(exc)})
        raise
    exact = [x["bf16"]["dflash"]["bf16_label"]["bf16_taps"]["exact_proposal_match"] for x in completed if x["bf16"]["dflash"]["bf16_label"]["bf16_taps"]["representable"]]
    q4_exact = [x["bf16"]["dflash"]["bf16_label"]["q4_taps"]["exact_proposal_match"] for x in completed if x["bf16"]["dflash"]["bf16_label"]["bf16_taps"]["representable"]]
    decision_change = any(x["bf16"]["dflash"]["proposal_changed"] for x in completed)
    topk_change = any(
        any(x["bf16"]["dflash"]["frozen_label"]["q4_taps"][k] != x["bf16"]["dflash"]["frozen_label"]["bf16_taps"][k]
            for k in ("top5", "top10", "top50", "top100"))
        for x in completed
    )
    if sum(exact) >= 2 and any(not x for x in q4_exact): classification = "BF16_TARGET_RECOVERY_SIGNAL"
    elif sum(exact) == 0 and not decision_change and not topk_change: classification = "NO_USEFUL_BF16_TARGET_RECOVERY"
    else: classification = "BF16_TARGET_EFFECT_AMBIGUOUS"
    report = aggregate(out, completed, classification, preconditions)
    print(json.dumps({"classification": classification, "evidence": str(out), "completed": [x["state_id"] for x in completed]}, indent=2))


if __name__ == "__main__": main()
