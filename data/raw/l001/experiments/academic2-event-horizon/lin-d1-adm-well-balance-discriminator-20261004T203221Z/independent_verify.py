#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,math,os
from pathlib import Path
import numpy as np
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,v):
    p=Path(p);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');os.replace(t,p)
def order(c,f,cn,fn): return None if c<=0 or f<=0 or c==f else math.log(c/f)/math.log((fn-1)/(cn-1))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--namespace',type=Path,required=True);a=ap.parse_args();root=a.root.resolve();ns=a.namespace.resolve();out=ns/'output'
    rp=out/'RESULT.json';tp=out/'TERMINAL.json';ep=out/'EVIDENCE.npz';r=json.loads(rp.read_text());t=json.loads(tp.read_text());f=json.loads((ns/'FREEZE_RECORD.json').read_text());b=json.loads((ns/'BINDINGS.json').read_text())
    checks={'terminal_status':r['status']==t['status']=='COMPLETE','classification':r['classification']==t['classification'],'result_hash':sha(rp)==t['result_sha256'],'evidence_hash':sha(ep)==t['evidence_sha256'],'contract_hash':r['contract_sha256']==sha(ns/'CONTRACT.md'),'bindings_hash':r['bindings_sha256']==sha(ns/'BINDINGS.json')}
    fm={i['path']:sha(ns/i['path'])==i['sha256'] for i in f['files']};pm={i['path']:sha(root/i['path'])==i['sha256'] for i in b['parents']+b['production_sources']};checks['frozen']=all(fm.values());checks['parents']=all(pm.values())
    A=r['producer_A'];B=r['producer_B'];checks['A_grids']=[x['grid'] for x in A['levels']]==[[65,121],[97,181],[129,241]];checks['A_zero']=all(x['equilibrium_well_balanced']['maximum_normalized']==0 for x in A['levels']);checks['A_response']=A['perturbation_control']['finite'] and A['perturbation_control']['maximum_normalized']>1e-12;checks['A_decision']=all(A['gates'].values())==A['passed']
    levels=B['levels'];checks['B_grids']=[x['grid'] for x in levels]==[[129,241],[193,241],[257,241],[385,241],[513,241]];passing=[i for i,x in enumerate(levels) if x['maximum_normalized']<=5e-5];last=order(levels[-2]['maximum_normalized'],levels[-1]['maximum_normalized'],levels[-2]['grid'][0],levels[-1]['grid'][0]);expected={'finest':levels[-1]['maximum_normalized']<=5e-5,'monotone':all(y['maximum_normalized']<x['maximum_normalized'] for x,y in zip(levels[:-1],levels[1:])),'last_order':last is not None and 2<=last<=6,'two_consecutive':len(passing)>=2 and passing[-2:]==[len(levels)-2,len(levels)-1]};checks['B_decision']=expected==B['gates'] and passing==B['passing_indices'] and all(expected.values())==B['passed']
    with np.load(ep,allow_pickle=False) as e: checks['finite_evidence']=all(np.all(np.isfinite(e[n])) for n in e.files)
    ok=all(checks.values());audit={'schema':'lin-d1-adm-independent-audit-v1','classification':'VERIFIED' if ok else 'NOT_VERIFIED','producer_classification':r['classification'],'checks':checks,'freeze_matches':fm,'parent_matches':pm,'B_expected_gates':expected,'claim_boundary':'finite-resolution formulation audit only'};atomic(out/'INDEPENDENT_AUDIT.json',audit);print(json.dumps(audit,indent=2,sort_keys=True));raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()
