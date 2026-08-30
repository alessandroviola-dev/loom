#!/usr/bin/env python3
"""Deterministic WP2 unit/invariant checks; no model/server calls."""
import json, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
CLI=ROOT/'scripts/loom-context'
def run(*args): return json.loads(subprocess.check_output([str(CLI),*args],text=True,cwd=ROOT))
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    secret='Authorization: Bearer sk-this-is-a-secret-token-123456\nERROR path=/tmp/boom code=42\n' + ('noise line\n'*300)
    p=td/'log.txt'; p.write_text(secret)
    result=run('compress','--input',str(p),'--query','boom','--type','log')
    assert result['tokens_after'] < result['tokens_before']
    assert 'sk-this-is-a-secret' not in result['text']
    ref=result['text'].split('exact=')[1].split(']')[0]
    recovered=run('recover',ref)
    assert 'sk-this-is-a-secret' not in recovered['content'] and 'code=42' in recovered['content']
    compact='path=a.py\nvalue=7\n'
    p.write_text(compact)
    assert run('compress','--input',str(p),'--query','value')['bypassed'] is True
    payload={'messages':[{'role':'user','content':'old evidence\n'+('WARNING one\n'*350)},{'role':'assistant','content':'ack'},{'role':'user','content':'What warning exists?'}]}
    q=td/'payload.json'; q.write_text(json.dumps(payload))
    packed=run('pack-payload','--input',str(q),'--query','warning','--budget','300','--no-memory')
    a=packed['accounting']; assert a['saved']>0 and a['recovery_refs'] and packed['payload']['messages'][-1]['content']==payload['messages'][-1]['content']
print('PASS deterministic privacy, compression, recovery, no-op, packing invariants')
