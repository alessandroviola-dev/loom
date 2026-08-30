#!/usr/bin/env python3
"""Read-only GGUF metadata and tensor-inventory comparison for WP3-R2."""
import argparse, hashlib, json
from pathlib import Path
from gguf import GGUFReader

def scalar(f):
    try: return f.contents()
    except Exception: return '<unreadable>'
def valhash(v):
    if isinstance(v,str): v=v.encode()
    else: v=repr(v).encode()
    return hashlib.sha256(v).hexdigest()
def inventory(r):
    return [(t.name, tuple(t.shape), str(t.tensor_type)) for t in r.tensors]
def main():
 p=argparse.ArgumentParser(); p.add_argument('--base',required=True); p.add_argument('--candidate',required=True); p.add_argument('--out',type=Path,required=True); a=p.parse_args()
 b,c=GGUFReader(a.base,'r'),GGUFReader(a.candidate,'r')
 keys=['general.architecture','general.base_model.0.name','general.base_model.0.organization','general.base_model.0.repo_url','qwen3moe.block_count','qwen3moe.context_length','qwen3moe.embedding_length','qwen3moe.feed_forward_length','qwen3moe.attention.head_count','qwen3moe.attention.head_count_kv','qwen3moe.expert_used_count','qwen3moe.expert_count','qwen3moe.expert_feed_forward_length','tokenizer.ggml.model','tokenizer.ggml.pre','tokenizer.ggml.eos_token_id','tokenizer.ggml.bos_token_id','tokenizer.chat_template']
 comp={}
 for key in keys:
  bv=scalar(b.fields[key]) if key in b.fields else None; cv=scalar(c.fields[key]) if key in c.fields else None
  comp[key]={'base':bv if not isinstance(bv,str) or len(bv)<200 else '<sha256:'+valhash(bv)+'>','candidate':cv if not isinstance(cv,str) or len(cv)<200 else '<sha256:'+valhash(cv)+'>','equal':bv==cv}
 bi,ci=inventory(b),inventory(c); bs=[(n,s) for n,s,_ in bi]; cs=[(n,s) for n,s,_ in ci]
 out={'base_tensor_count':len(bi),'candidate_tensor_count':len(ci),'inventory_equal':bi==ci,'structural_inventory_equal':bs==cs,'base_inventory_sha256':valhash(bi),'candidate_inventory_sha256':valhash(ci),'base_structural_inventory_sha256':valhash(bs),'candidate_structural_inventory_sha256':valhash(cs),'metadata':comp,'candidate_only_tensors':sorted(set(ci)-set(bi))[:20],'base_only_tensors':sorted(set(bi)-set(ci))[:20]}
 a.out.write_text(json.dumps(out, indent=2, default=lambda x: x.item() if hasattr(x, 'item') else str(x))+'\n')
if __name__=='__main__': main()
