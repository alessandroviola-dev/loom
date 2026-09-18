#!/usr/bin/env python3
"""Bounded persistent-cache BF16 tap re-extraction and one-state DFlash probe."""
from __future__ import annotations
import gc, hashlib, json, os, platform, shutil, sys, time
from datetime import datetime, timezone
from pathlib import Path

import mlx.core as mx
import numpy as np

import loom_dflash_unquantized_target_p1t01_range_control_001 as rc
import loom_30b_moe_dflash_target_interface_001 as oracle
import loom_30b_moe_first_greedy_generation_001 as target
import loom_dflash_greedy_e2e_001 as dflash

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T212818Z"
LOCAL_DENSE = ROOT / "results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T173131Z/control-cache/dense"
EXTERNAL_ARCHIVE = Path(os.environ["LOOM_EXTERNAL_ARCHIVE"])
CACHE = EXTERNAL_ARCHIVE / "bf16-cache/Qwen3-30B-A3B/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39"
ARTIFACTS = EXTERNAL_ARCHIVE / "artifacts/dflash-bf16-tap-drafter-probe-001"
OUTROOT = ROOT / "results-local/research/dflash-bf16-tap-drafter-probe-001"
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
TAPS = (1, 12, 23, 34, 45)
REVISION = "ad44e777bcd18fa416d9da3bd8f70d33ebb85d39"
PREFIX_SHA = "7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f"


def sha_bytes(value): return hashlib.sha256(value).hexdigest()
def sha_file(path): return rc.fsha(path)
def dump(path, value): rc.atomic_dump(path, value)
def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)
def softmax_logprob(logits, token):
    x = np.asarray(logits, dtype=np.float64); m = float(x.max()); z = m + np.log(np.exp(x - m).sum())
    return float(x[token]), float(x[token] - z), float(np.exp(x[token] - z))
def rank(logits, token): return int(np.count_nonzero(np.asarray(logits) > np.asarray(logits)[token]) + 1)
def top_ids(logits, k): return np.argsort(np.asarray(logits))[-k:][::-1].astype(int).tolist()


def storage_gate():
    mount = EXTERNAL_ARCHIVE
    if not mount.is_dir() or not CACHE.parent.parent.parent.exists() or not os.access(CACHE.parent.parent.parent, os.W_OK):
        raise RuntimeError("EXTERNAL_RESEARCH_STORAGE_UNAVAILABLE")
    stat = shutil.disk_usage(mount)
    if stat.free < 100 * 1024**3: raise RuntimeError("EXTERNAL_RESEARCH_STORAGE_UNAVAILABLE")
    # The mount path is explicitly checked instead of accepting an internal fallback.
    if str(CACHE).startswith(str(ROOT)): raise RuntimeError("EXTERNAL_RESEARCH_STORAGE_UNAVAILABLE")
    return {"mount": str(mount), "writable": True, "free_bytes": stat.free, "free_gib": stat.free / 1024**3, "external_not_internal_project_disk": True}


def copy_dense(validation):
    dense = CACHE / "dense"; manifests = CACHE / "manifests"; dense.mkdir(parents=True, exist_ok=True); manifests.mkdir(parents=True, exist_ok=True)
    copied = reused = 0; rows = []
    for item in validation["dense_files"]:
        src, dst = LOCAL_DENSE / item["filename"], dense / item["filename"]
        valid = dst.is_file() and dst.stat().st_size == item["file_bytes"] and sha_file(dst) == item["sha256"]
        if not valid:
            if not src.is_file() or src.stat().st_size != item["file_bytes"] or sha_file(src) != item["sha256"]:
                raise RuntimeError(f"LOCAL_DENSE_CACHE_PROVENANCE_FAIL: {src}")
            tmp = dense / f".{dst.name}.{os.getpid()}.partial"
            with src.open("rb") as a, tmp.open("xb") as b:
                shutil.copyfileobj(a, b, 8 * 1024 * 1024); b.flush(); os.fsync(b.fileno())
            if tmp.stat().st_size != item["file_bytes"] or sha_file(tmp) != item["sha256"]: raise RuntimeError("EXTERNAL_DENSE_COPY_HASH_FAIL")
            os.replace(tmp, dst); fsync_dir(dense); copied += 1
        else: reused += 1
        rows.append(item)
    manifest = {"model": "Qwen/Qwen3-30B-A3B", "revision": REVISION, "source_completed_control": str(CONTROL), "source_dense_validation": validation["dense_file_manifest_sha256"], "files": rows, "payload_bytes": validation["dense_payload_bytes"], "disk_bytes": sum(x["file_bytes"] for x in rows)}
    dump(manifests / "dense-manifest.json", manifest)
    return dense, {"copied": copied, "reused": reused, "manifest": str(manifests / "dense-manifest.json"), "payload_bytes": manifest["payload_bytes"], "disk_bytes": manifest["disk_bytes"]}


class PersistentStore(rc.RangeStore):
    def __init__(self, manifest, index, validation, progress_path, network_byte_cap=None,
                 network_request_cap=None, network_ledger_path=None):
        self.cache_root = CACHE; self.experts_root = CACHE / "experts"; self.cache_tmp = CACHE / "tmp"
        self.cache_hits = self.cache_misses = self.experts_newly_persisted = self.expert_hdd_bytes = 0
        self.cache_persistent_bytes = sum(p.stat().st_size for p in self.experts_root.rglob("*") if p.is_file()) if self.experts_root.exists() else 0
        self.last_cache_operation = None
        scratch = self.cache_tmp / f"runtime-{RUN_ID}"
        super().__init__(scratch, CACHE / "dense", manifest, index, validation, progress_path,
                         network_byte_cap=network_byte_cap, network_request_cap=network_request_cap,
                         network_ledger_path=network_ledger_path)
    def write_progress(self, state):
        if not self.progress_path: return
        rc.atomic_dump(self.progress_path, {"checkpoint": "LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001", "state": state, "updated_utc": rc.utc_now(), "started_utc": self.started_utc, "elapsed_seconds": time.monotonic()-self.started_monotonic, "current_layer_1_based": None if self.current_layer is None else self.current_layer+1, "layers_total": target.LAYERS, "unique_experts_required_current_layer": len(self.current_layer_required), "unique_experts_completed_current_layer": len(self.current_layer_completed), "completed_layer_expert_pairs": self.cumulative_expert_layer_pairs_completed, "cache_hits": self.cache_hits, "cache_misses": self.cache_misses, "expert_bytes_read_from_hdd": self.expert_hdd_bytes, "expert_bytes_fetched_network": self.expert_tensor_payload_bytes_fetched, "experts_newly_persisted": self.experts_newly_persisted, "persistent_expert_cache_bytes": self.cache_persistent_bytes, "retries": self.network_retries, "http_request_count": self.http_request_count, "connection_reuse_count_observable": self.connection_reuse_count, "last_successful_cache_or_network_operation": self.last_cache_operation or self.last_successful_fetch_timestamp})
    def _expert_dir(self, layer, expert): return self.experts_root / f"layer_{layer:03d}" / f"expert_{expert:03d}"
    def _load_cached(self, layer, expert, names):
        directory = self._expert_dir(layer, expert); mf = directory / "manifest.json"
        if not mf.is_file(): return None
        try:
            meta = json.loads(mf.read_text())
            if meta["model"] != "Qwen/Qwen3-30B-A3B" or meta["revision"] != REVISION or meta["layer"] != layer or meta["expert"] != expert or meta["tensor_names"] != names: return None
            arrays, records = {}, []
            for row in meta["tensors"]:
                path = directory / row["filename"]
                if not path.is_file() or path.stat().st_size != row["file_bytes"] or sha_file(path) != row["file_sha256"]: return None
                info = rc.staged_tensor_metadata(path)
                if info["payload_bytes"] != row["payload_bytes"] or info["shape"] != row["shape"]: return None
                arr = mx.load(str(path))["x"]; mx.eval(arr)
                if list(arr.shape) != row["shape"]: return None
                arrays[row["name"]] = arr; records.append({k: row[k] for k in ("name","shard","payload_offset","payload_bytes","shape","object_sha256") } | {"cache_reused": True})
            self.cache_hits += 1; self.expert_hdd_bytes += sum(x["payload_bytes"] for x in records); self.last_cache_operation = rc.utc_now()
            self.record_cache_hit({"layer": layer, "expert": expert}); self.write_progress("persistent_expert_cache_hit")
            return arrays, records
        except Exception:
            return None
    def expert(self, layer, expert, names):
        hit = self._load_cached(layer, expert, names)
        if hit is not None: return hit[0], [], hit[1]
        self.cache_misses += 1; rows, payloads, _ = self.fetch_names(names, "ephemeral_expert")
        directory = self._expert_dir(layer, expert); directory.parent.mkdir(parents=True, exist_ok=True); self.cache_tmp.mkdir(parents=True, exist_ok=True)
        tmp = self.cache_tmp / f"layer_{layer:03d}_expert_{expert:03d}.{os.getpid()}.partial"
        tmp.mkdir(exist_ok=False); entries = []
        try:
            for row in rows:
                name = row["name"]; projection = name.split(".")[-2]; path = tmp / f"{projection}.safetensors"; length = row["length"]
                header = json.dumps({"x":{"dtype":"BF16","shape":row["shape"],"data_offsets":[0,length]}}, separators=(",", ":")).encode()
                self._write_tensor(path, header, payloads[name])
                meta = rc.staged_tensor_metadata(path)
                entries.append({"name": name, "filename": path.name, "shard": row["shard"], "payload_offset": row["start"], "payload_bytes": length, "shape": row["shape"], "dtype": "BF16", "object_sha256": self.weights[row["shard"]]["sha256"], "file_bytes": meta["file_bytes"], "file_sha256": meta["sha256"], "payload_sha256": sha_bytes(payloads[name])})
            if sum(x["payload_bytes"] for x in entries) != rc.BF16_EXPERT_BYTES: raise RuntimeError("PERSISTENT_EXPERT_BYTE_RECONCILIATION_FAIL")
            dump(tmp / "manifest.json", {"model":"Qwen/Qwen3-30B-A3B", "revision":REVISION, "layer":layer, "expert":expert, "tensor_names":names, "tensors":entries, "source":"pinned range transport", "created_utc":rc.utc_now()})
            fsync_dir(tmp)
            if directory.exists(): shutil.rmtree(tmp); return self.expert(layer, expert, names)
            os.replace(tmp, directory); fsync_dir(directory.parent)
            self.experts_newly_persisted += 1; self.cache_persistent_bytes += sum(x["file_bytes"] for x in entries) + (directory / "manifest.json").stat().st_size; self.last_cache_operation = rc.utc_now(); self.write_progress("persistent_expert_cache_persisted")
            return self.expert(layer, expert, names)
        except Exception:
            if tmp.exists(): shutil.rmtree(tmp)
            raise


class ArtifactWriter:
    def __init__(self, root):
        self.root = root; self.root.mkdir(parents=True, exist_ok=True); self.tmp = self.root / "tmp-taps"; self.tmp.mkdir(exist_ok=False)
    def capture_tap(self, layer, value):
        path = self.tmp / f"post_block_{layer:02d}.npy"; partial = path.with_suffix(".partial")
        with partial.open("xb") as f: np.save(f, np.asarray(value, dtype=np.float32)); f.flush(); os.fsync(f.fileno())
        os.replace(partial, path); fsync_dir(self.tmp)
    def finalize_taps(self):
        taps = np.stack([np.load(self.tmp / f"post_block_{x:02d}.npy", allow_pickle=False) for x in TAPS]).astype(np.float32, copy=False)
        if taps.shape != (5,43,2048) or not np.isfinite(taps).all(): raise RuntimeError("BF16_TAP_CAPTURE_CONTRACT_FAIL")
        path = self.root / "bf16-taps.npz"; partial = self.root / ".bf16-taps.partial"
        with partial.open("xb") as f: np.savez(f, taps=taps, tap_layers_1_based=np.asarray(TAPS,dtype=np.int32), context_length=np.asarray(43,dtype=np.int32), anchor_position=np.asarray(42,dtype=np.int32), anchor_token=np.asarray(271,dtype=np.int32)); f.flush(); os.fsync(f.fileno())
        os.replace(partial,path); fsync_dir(self.root)
        rows=[]
        for i,layer in enumerate(TAPS): rows.append({"index":i,"layer_1_based":layer,"shape":list(taps[i].shape),"dtype":"float32","sha256":sha_bytes(np.ascontiguousarray(taps[i]).tobytes()),"finite":bool(np.isfinite(taps[i]).all())})
        dump(self.root / "bf16-taps-hashes.json", {"aggregate_shape":list(taps.shape),"aggregate_dtype":"float32","aggregate_sha256":sha_bytes(np.ascontiguousarray(taps).tobytes()),"taps":rows})
        return taps
    def save_logits(self, logits):
        final=np.asarray(logits,dtype=np.float32)[0,-1].copy()
        if final.shape != (151936,) or not np.isfinite(final).all(): raise RuntimeError("BF16_LOGIT_CAPTURE_CONTRACT_FAIL")
        path=self.root/"bf16-target-logits.npz"; partial=self.root/".bf16-logits.partial"
        with partial.open("xb") as f: np.savez(f, logits=final, anchor_position=np.asarray(42,dtype=np.int32), context_length=np.asarray(43,dtype=np.int32)); f.flush(); os.fsync(f.fileno())
        os.replace(partial,path); fsync_dir(self.root)
        return final


def bf_forward(store, backbone, token_ids, writer=None):
    streams=[]
    for _ in range(2):
        x=backbone.embed_tokens(mx.array([token_ids],dtype=mx.int32)); mx.eval(x); streams.append({"x":x,"cache":[target.BF16KVCache() for _ in range(target.LAYERS)],"taps":{},"routers":[]})
    mask=rc.create_attention_mask(streams[0]["x"],streams[0]["cache"][0]); expert_rows=[]; logical_live=max_live=0; layer_accounting=[]
    for layer_no,layer in enumerate(backbone.layers):
        routed=[]
        for stream in streams:
            x=stream["x"]; h=x+oracle.attention_with_bf16_cache(layer.self_attn,layer.input_layernorm(x),mask,stream["cache"][layer_no]); z=layer.post_attention_layernorm(h); mx.eval(h,z)
            router_logits,selected,weights=target.route(layer.external_moe.gate,z); mx.eval(router_logits,selected,weights); ids=np.asarray(selected).astype(np.int32,copy=True); ws=rc.bf_host(weights).copy()
            stream["routers"].append({"layer":layer_no,"logits":rc.bf_host(router_logits).copy(),"ids":ids,"weights":ws}); routed.append({"h":h,"z":z,"router_logits":router_logits,"selected":selected,"weights":weights,"ids":ids})
        assignments={}
        for stream_no,route in enumerate(routed):
            for position in range(route["ids"].shape[1]):
                for rank_,expert in enumerate(route["ids"][0,position].tolist()): assignments.setdefault(int(expert),[]).append((stream_no,position,rank_))
        union_ids=sorted(assignments); store.set_layer(layer_no,union_ids); serial=[[([None]*rc.TOP_K) for _ in range(route["ids"].shape[1])] for route in routed]
        for expert in union_ids:
            names=[f"model.layers.{layer_no}.mlp.experts.{expert}.{proj}.weight" for proj in target.PROJS]; loaded,_,rows=store.expert(layer_no,expert,names); w={proj:loaded[name] for proj,name in zip(target.PROJS,names)}; store.unique_layer_experts_fetched.add((layer_no,expert)); logical_live+=rc.BF16_EXPERT_BYTES; max_live=max(max_live,logical_live)
            try:
                for stream_no,position,rank_ in assignments[expert]:
                    y=rc.bf_direct(routed[stream_no]["z"][:,position:position+1,:],w); mx.eval(y); serial[stream_no][position][rank_]=mx.array(rc.bf_host(y),dtype=mx.bfloat16); mx.eval(serial[stream_no][position][rank_]); del y
                expert_rows.extend(rows)
            finally:
                del w,loaded; logical_live-=rc.BF16_EXPERT_BYTES
            store.complete_expert(layer_no,expert)
        for stream_no,stream in enumerate(streams):
            positions=[]
            for position,outputs in enumerate(serial[stream_no]):
                if any(x is None for x in outputs): raise RuntimeError("serial expert assignment incomplete")
                stacked=mx.stack(outputs,axis=-2); mixed=(stacked*routed[stream_no]["weights"][:,position:position+1,:,None]).sum(axis=-2); mx.eval(mixed); positions.append(mixed); del stacked,mixed
            moe=mx.concatenate(positions,axis=1); stream["x"]=routed[stream_no]["h"]+moe; mx.eval(stream["x"])
            if layer_no+1 in TAPS:
                captured=rc.bf_host(stream["x"]).copy(); stream["taps"][layer_no+1]=captured
                if stream_no == 0 and writer is not None: writer.capture_tap(layer_no+1,captured[0])
            del positions,moe
        layer_accounting.append({"layer":layer_no,"primary_unique_experts":len(set(routed[0]["ids"].reshape(-1).tolist())),"rerun_unique_experts":len(set(routed[1]["ids"].reshape(-1).tolist())),"union_unique_experts_fetched":len(union_ids)})
        del serial,assignments,union_ids
        for route in routed: del route["h"],route["z"],route["router_logits"],route["selected"],route["weights"]
        del routed; mx.clear_cache()
    results=[]
    for stream in streams:
        norm=backbone.norm(stream["x"]); mx.eval(norm); logits=backbone.lm_head(norm); mx.eval(logits); results.append({"taps":stream["taps"],"routers":stream["routers"],"final_hidden":rc.bf_host(norm).copy(),"logits":rc.bf_host(logits).copy(),"final_live":logical_live,"max_live":max_live}); del norm,logits,stream["x"],stream["cache"]
    return results[0],results[1],{"expert_rows":expert_rows,"layers":layer_accounting}


def run_probe(external, primary_logits, primary_taps, q4, provenance):
    import loom_dflash_greedy_e2e_001 as path
    drafter=path.Drafter(); q4_taps=q4["taps"].astype(np.float32,copy=False); bf_taps=primary_taps.astype(np.float32,copy=False)
    def execute(taps):
        a=drafter.propose_debug(taps,271); b=drafter.propose_debug(taps,271); deterministic=bool(np.array_equal(a["logits"],b["logits"],equal_nan=True) and a["target_ids"]==b["target_ids"]); return a,deterministic
    base,base_det=execute(q4_taps)
    if int(base["target_ids"][0]) != 8747 or not base_det or not np.isfinite(base["logits"]).all(): raise RuntimeError("DFLASH_Q4_TAP_BASELINE_PARITY_FAIL")
    treat,treat_det=execute(bf_taps); target=np.asarray(primary_logits,dtype=np.float32); target_ids_by_draft_row=np.asarray(drafter.target_ids_by_draft_row,dtype=np.int64)
    def score(debug,det):
        logits=np.asarray(debug["logits"],dtype=np.float32)[0,1]; proposal=int(debug["target_ids"][0]); drafts=top_ids(logits,5); mapped=[int(target_ids_by_draft_row[i]) for i in drafts]; idx=np.where(target_ids_by_draft_row==12050)[0]; target_rank=min((rank(logits,int(i)) for i in idx),default=None); target_logit=None if not len(idx) else float(max(logits[i] for i in idx)); target_prob=None if target_logit is None else float(np.exp(target_logit-(float(logits.max())+np.log(np.exp(logits-logits.max()).sum()))) )
        plog,plp,pp=softmax_logprob(target,proposal); pr=rank(target,proposal)
        return {"proposal_token":proposal,"top5_proposal_tokens":mapped,"target_token_12050_drafter_rank":target_rank,"target_token_12050_drafter_logit":target_logit,"target_token_12050_drafter_probability":target_prob,"proposal_rank_in_bf16_target":pr,"bf16_target_proposal_logit":plog,"bf16_target_proposal_logprob":plp,"bf16_target_proposal_probability":pp,"compatibility":{"top5":pr<=5,"top10":pr<=10,"top50":pr<=50},"deterministic_rerun":det,"finite":bool(np.isfinite(debug["logits"]).all())}
    baseline,treatment=score(base,base_det),score(treat,treat_det); dl=rc.metric(np.asarray(base["logits"])[0,1:8],np.asarray(treat["logits"])[0,1:8]); changed={"q4_tap_sha256":sha_bytes(np.ascontiguousarray(q4_taps).tobytes()),"bf16_tap_sha256":sha_bytes(np.ascontiguousarray(bf_taps).tobytes()),"only_taps_changed":True,"anchor_token":271,"anchor_position":42,"context_length":43,"mask_bitwise_equal":bool(np.array_equal(base["allowed"],treat["allowed"])),"drafter_model_sha256":sha_file(path.DRAFT/"model.safetensors")}
    strong=treatment["proposal_token"]==12050 or (not baseline["compatibility"]["top50"] and treatment["compatibility"]["top50"])
    directional=not strong and (treatment["target_token_12050_drafter_rank"] is not None and baseline["target_token_12050_drafter_rank"] is not None and treatment["target_token_12050_drafter_rank"]<baseline["target_token_12050_drafter_rank"])
    classification="STRONG_RECOVERY" if strong else "DIRECTIONAL_RECOVERY" if directional else "NO_MATERIAL_RECOVERY"
    dump(external/"q4-baseline.json",baseline); dump(external/"bf16-tap-treatment.json",treatment); dump(external/"comparison.json",{"proposal_distribution_metrics_q4_vs_bf16":dl,"only_taps_changed_proof":changed,"classification":classification})
    del drafter; mx.clear_cache(); return baseline,treatment,dl,changed,classification


def main():
    gate=storage_gate(); external=ARTIFACTS/RUN_ID; local=OUTROOT/RUN_ID; external.mkdir(parents=True,exist_ok=False); local.mkdir(parents=True,exist_ok=False)
    for p in (external,local): shutil.copy2(ARTIFACTS/"20260825T063400Z"/"retention-plan.json",p/"retention-plan.json")
    if mx.__version__ != "0.31.2": raise RuntimeError(f"PINNED_RUNTIME_FAIL: {mx.__version__}")
    validation=rc.validate_reused_evidence(); dense,dense_stats=copy_dense(validation); manifest,index=json.loads(rc.MANIFEST.read_text()),json.loads(rc.INDEX.read_text())
    writer=ArtifactWriter(external); store=PersistentStore(manifest,index,validation,external/"progress.json")
    try:
        store.catalog(); cfg=json.loads((rc.PREFLIGHT/"source-config.json").read_text()); backbone,dense_records=rc.load_bf_backbone(store,cfg,index)
        if store.dense_cache_hits != 435: raise RuntimeError("DENSE_EXTERNAL_CACHE_REUSE_FAIL")
        before=rc.memory(); primary,rerun,paired=bf_forward(store,backbone,rc.p1_tokens(),writer); after=rc.memory(); taps=writer.finalize_taps(); logits=writer.save_logits(primary["logits"])
        q4_saved=np.load(rc.REUSE_GATE_A_OUTPUT,allow_pickle=False); q4_taps=q4_saved["taps"][:,0].astype(np.float32,copy=False); q4={"taps":q4_taps,"final_hidden":q4_saved["final_hidden"],"logits":q4_saved["logits"],"max_live":int(q4_saved["max_live"]),"routers":[{"layer":i,"logits":q4_saved[f"router_logits_{i}"],"ids":q4_saved[f"router_ids_{i}"],"weights":q4_saved[f"router_weights_{i}"]} for i in range(target.LAYERS)]}
        deterministic=all(np.array_equal(primary["taps"][x],rerun["taps"][x],equal_nan=True) for x in TAPS) and np.array_equal(primary["logits"],rerun["logits"],equal_nan=True); finite=rc.finite(primary["logits"]) and all(rc.finite(primary["taps"][x]) for x in TAPS); leak=primary["final_live"]==0 and rerun["final_live"]==0
        tap_metrics=[{"layer":x,**rc.metric(primary["taps"][x][:,-1:,:],q4["taps"][i:i+1,-1:,:])} for i,x in enumerate(TAPS)]; hidden=rc.metric(primary["final_hidden"][:,-1:,:],q4["final_hidden"][:,-1:,:]); logit_metrics=rc.metric(primary["logits"][:,-1:,:],q4["logits"][:,-1:,:]); top5q,top5b=rc.top5(q4["logits"][0,-1]),rc.top5(logits); bf_margin=rc.margin(logits)
        parity={"bf16_top1_12050":int(np.argmax(logits))==12050,"deterministic":deterministic,"finite":finite,"no_routed_expert_leak":leak,"tap_relative_l2_matches_completed":all(abs(a["relative_L2"]-b)<1e-12 for a,b in zip(tap_metrics,[0.11486288418683076,0.34579173817152375,0.3106350444608152,0.1986387598714164,0.2746753682776747])),"final_hidden_matches_completed":abs(hidden["relative_L2"]-0.2706646930881716)<1e-12 and abs(hidden["cosine"]-0.9646705787464082)<1e-12,"final_logits_matches_completed":abs(logit_metrics["relative_L2"]-0.336188815819103)<1e-12 and abs(logit_metrics["cosine"]-0.9572688451814544)<1e-12,"margin_matches_completed":abs(bf_margin-11.875)<1e-12,"top5_overlap_4_5":len(set(top5q)&set(top5b))==4}
        provenance={"checkpoint":"LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001","run_id_utc":RUN_ID,"frozen_state":{"id":"P1_t01","prefix_sha256":PREFIX_SHA,"context":43,"anchor_position":42,"anchor_token":271,"tap_layers_1_based":list(TAPS)},"bf16":{"model":"Qwen/Qwen3-30B-A3B","revision":REVISION,"manifest_sha256":sha_file(rc.MANIFEST)},"runtime":{"python":sys.executable,"mlx":mx.__version__,"platform":platform.platform()},"completed_control":str(CONTROL),"dense_cache":dense_stats,"external_cache":str(CACHE),"artifact_root":str(external)}
        dump(external/"bf16-artifact-provenance.json",provenance); dump(external/"bf16-reextraction-validation.json",{"parity":parity,"tap_metrics":tap_metrics,"final_hidden_metrics":hidden,"final_logit_metrics":logit_metrics,"bf16_top1":int(np.argmax(logits)),"bf16_margin":bf_margin,"top5_q4":top5q,"top5_bf16":top5b,"top5_overlap":len(set(top5q)&set(top5b)),"cache":{"hits":store.cache_hits,"misses":store.cache_misses,"new":store.experts_newly_persisted,"bytes":store.cache_persistent_bytes},"memory":{"before":before,"after":after}})
        if not all(parity.values()): raise RuntimeError("BF16_ARTIFACT_REEXTRACTION_PARITY_FAIL")
        baseline,treatment,dist,proof,classification=run_probe(external,logits,taps,q4,provenance)
        summary={"checkpoint":"LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001","classification":classification,"storage_gate":gate,"cache":{"dense":dense_stats,"expert_hits":store.cache_hits,"expert_misses":store.cache_misses,"experts_newly_persisted":store.experts_newly_persisted,"expert_hdd_bytes":store.expert_hdd_bytes,"expert_network_bytes":store.expert_tensor_payload_bytes_fetched,"persistent_expert_cache_bytes":store.cache_persistent_bytes,"retries":store.network_retries},"reextraction_parity":parity,"q4_baseline":baseline,"bf16_treatment":treatment,"proposal_distribution_metrics":dist,"only_taps_changed":proof,"evidence_external":str(external),"evidence_local":str(local)}
        dump(external/"summary.json",summary)
        for name in ("retention-plan.json","bf16-taps-hashes.json","bf16-artifact-provenance.json","bf16-reextraction-validation.json","q4-baseline.json","bf16-tap-treatment.json","comparison.json","summary.json"):
            shutil.copy2(external/name,local/name)
        dump(local/"provenance.json",provenance); print(json.dumps({"classification":classification,"external":str(external),"local":str(local)},indent=2))
    except Exception as exc:
        dump(external/"summary.json",{"checkpoint":"LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001","classification":"BF16_ARTIFACT_REEXTRACTION_PARITY_FAIL" if "PARITY_FAIL" in str(exc) else "BF16_ARTIFACT_EXTRACTION_MECHANICAL_FAIL","error":f"{type(exc).__name__}: {exc}","cache":{"hits":store.cache_hits,"misses":store.cache_misses,"new":store.experts_newly_persisted,"bytes":store.cache_persistent_bytes},"external":str(external)})
        dump(local/"summary.json",json.loads((external/"summary.json").read_text())); raise
    finally:
        dump(external/"range-fetches.json",store.fetches); dump(external/"network-events.json",store.network_events); store.close(); gc.collect(); mx.clear_cache()

if __name__ == "__main__": main()
