#!/usr/bin/env python3
"""Build/verify a lossless GGUF routed-expert-major sidecar; never mutates GGUF."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, sys, time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--model', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--gguf-py', type=Path, required=True)
p.add_argument('--verify-only', action='store_true')
a = p.parse_args()
sys.path.insert(0, str(a.gguf_py))
from gguf import GGUFReader

LAYERS, EXPERTS = 48, 128
ORDER = ('ffn_up_exps.weight', 'ffn_gate_exps.weight', 'ffn_down_exps.weight') # llama-graph bind order
CHUNK = 8 << 20

def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(CHUNK), b''): h.update(b)
    return h.hexdigest()
def pread_exact(fd: int,n:int,o:int)->bytes:
    b=os.pread(fd,n,o)
    if len(b)!=n: raise RuntimeError(f'short read {o} {len(b)}/{n}')
    return b
def write_exact(fd:int,b:bytes):
    m=0
    while m<len(b):
        n=os.write(fd,b[m:])
        if n<=0: raise RuntimeError('short write')
        m+=n
def layout():
    r=GGUFReader(str(a.model),'r')
    ts={t.name:t for t in r.tensors}
    rows=[]
    for layer in range(LAYERS):
        pools=[]
        for suffix in ORDER:
            name=f'blk.{layer}.{suffix}'
            t=ts.get(name)
            if t is None: raise RuntimeError('missing '+name)
            if int(t.n_bytes)%EXPERTS: raise RuntimeError('bad expert axis '+name)
            pools.append({'name':name,'data_offset':int(t.data_offset),'tensor_bytes':int(t.n_bytes),'stride':int(t.n_bytes)//EXPERTS,'shape':[int(x) for x in t.shape]})
        if len({x['stride'] for x in pools}) != 1: raise RuntimeError(f'nonuniform stride L{layer}')
        rows.append({'layer':layer,'pools':pools,'expert_payload_bytes':sum(x['stride'] for x in pools)})
    if len({x['expert_payload_bytes'] for x in rows}) != 1: raise RuntimeError('nonuniform layer payload')
    return rows

def verify(rows, bank):
    sourcefd=os.open(a.model,os.O_RDONLY); bankfd=os.open(bank,os.O_RDONLY)
    bad=[]; checked=0; source_all=hashlib.sha256(); bank_all=hashlib.sha256(); per_layer=[]
    try:
        cursor=0
        for row in rows:
            lhsrc=hashlib.sha256(); lhbank=hashlib.sha256()
            for expert in range(EXPERTS):
                for pool in row['pools']:
                    n=pool['stride']; src=pread_exact(sourcefd,n,pool['data_offset']+expert*n); got=pread_exact(bankfd,n,cursor)
                    source_all.update(src); bank_all.update(got); lhsrc.update(src); lhbank.update(got)
                    if src != got and len(bad)<20: bad.append({'layer':row['layer'],'expert':expert,'pool':pool['name'],'bank_offset':cursor})
                    cursor+=n; checked+=1
            per_layer.append({'layer':row['layer'],'source_concatenated_sha256':lhsrc.hexdigest(),'bank_segment_sha256':lhbank.hexdigest(),'pass':lhsrc.digest()==lhbank.digest()})
    finally: os.close(sourcefd); os.close(bankfd)
    return {'pass':not bad and source_all.digest()==bank_all.digest(),'components_checked':checked,'bytes_checked':cursor,'mismatch_examples':bad,'source_concatenated_sha256':source_all.hexdigest(),'bank_sha256_by_payload_order':bank_all.hexdigest(),'per_layer':per_layer}

rows=layout(); payload=LAYERS*EXPERTS*rows[0]['expert_payload_bytes']
a.out.mkdir(parents=True,exist_ok=True); bank=a.out/'unlocked-expert-major-v1.bin'
free=shutil.disk_usage(a.out).free
if free < payload + 20*(1<<30): raise RuntimeError(f'insufficient safety headroom: free={free}, need={payload + 20*(1<<30)}')
if not a.verify_only:
    if bank.exists(): raise RuntimeError('refusing to overwrite existing bank')
    sf=os.open(a.model,os.O_RDONLY); bf=os.open(bank,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    started=time.monotonic(); copied=0
    try:
        for row in rows:
            for expert in range(EXPERTS):
                for pool in row['pools']:
                    b=pread_exact(sf,pool['stride'],pool['data_offset']+expert*pool['stride']); write_exact(bf,b); copied+=len(b)
        os.fsync(bf)
    finally: os.close(sf); os.close(bf)
    if copied!=payload or bank.stat().st_size!=payload: raise RuntimeError(f'bank size {copied}/{bank.stat().st_size}, expected {payload}')
    build={'wall_s':time.monotonic()-started,'bytes_written':copied,'rate_mib_s':copied/(time.monotonic()-started)/(1<<20)}
else: build={'verify_only':True}
if not bank.is_file() or bank.stat().st_size != payload: raise RuntimeError('missing/incorrect bank')
verification=verify(rows,bank)
manifest={'format':'LOOM_UOPT002_GGUF_EXPERT_MAJOR_SIDECAR_V1','scope':'lossless routed-expert-only sidecar consumed only by isolated patched runtime; source GGUF is unchanged','source_model':str(a.model.resolve()),'source_model_sha256':sha_file(a.model),'source_model_size':a.model.stat().st_size,'pool_order':'llama-graph bind order: up, gate, down','layers':LAYERS,'experts_per_layer':EXPERTS,'per_layer':rows,'expert_payload_bytes':rows[0]['expert_payload_bytes'],'bank_path':str(bank.resolve()),'bank_size':bank.stat().st_size,'bank_file_sha256':sha_file(bank),'construction':build,'verification':verification,'disk_free_after':shutil.disk_usage(a.out).free}
(a.out/'expert-major-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if not verification['pass']: raise SystemExit('verification failed')
print(json.dumps({'bank':str(bank),'bytes':bank.stat().st_size,'bank_sha256':manifest['bank_file_sha256'],'verified':verification['pass'],'free_after':manifest['disk_free_after']},indent=2))
