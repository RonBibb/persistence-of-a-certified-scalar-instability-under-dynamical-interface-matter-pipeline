"""Bounded two-precision producer; no C6 inclusion decisions."""
from tail_core import *
import argparse,subprocess,shutil,signal,traceback,json
STOP=False
def stop(*args):
    global STOP
    STOP=True
def worker(out,bits,stop_after=None):
    g=guard();fp=cid(g,bits);ctx.prec=bits
    if (out/'TERMINAL.json').exists() or (out/'FAILURE.json').exists():raise RuntimeError('Terminal or failed-closed case cannot restart')
    held,ident=acquire(out);start=time.monotonic()
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:
        st=load(out,fp) if (out/'LATEST.json').exists() else commit(out,prepare(bits),fp)
        domain_proof(st)
        if st['phase']==stop_after:return
        while st['phase']<3:
            if STOP:status(out,'STOPPED',phase=st['phase'],case_fingerprint=fp);return
            before=time.monotonic();st=commit(out,step(st),fp);domain_proof(st)
            print(json.dumps({'bits':bits,'phase':st['phase'],'seconds':time.monotonic()-before}),flush=True)
            if st['phase']==stop_after:return
        r=dict(st['case_result'],guard=g,case_fingerprint=fp,last_checkpoint=rec.read(out/'LATEST.json'))
        rec.atomic(out/'RESULT.json',r,True)
        rec.atomic(out/'TERMINAL.json',{'utc':rec.now(),'guard':g,'case_fingerprint':fp,'result_sha256':rec.sha(out/'RESULT.json'),'all_passed':r['all_passed']},True)
        status(out,'TERMINAL',case_fingerprint=fp,all_passed=r['all_passed'])
    except BaseException as ex:
        rec.atomic(out/'FAILURE.json',{'guard':g,'case_fingerprint':fp,'error':str(ex),'traceback':traceback.format_exc(),'utc':rec.now()},True)
        status(out,'FAILED_CLOSED',error=str(ex));raise
    finally:release(out,held,ident,start)
def command(out,bits,phase=None):
    a=[sys.executable,'-B',str(ROOT/'tail_run.py'),'worker','--output',str(out),'--bits',str(bits)]
    return a+(['--stop-after',str(phase)] if phase is not None else [])
def spawn(out,bits,phase=None):
    out.mkdir(parents=True,exist_ok=True);log=(out/f'launch-{time.time_ns()}.log').open('w')
    return subprocess.Popen(command(out,bits,phase),stdout=log,stderr=subprocess.STDOUT),log
def join(items):
    codes=[]
    for p,f in items:codes.append(p.wait());f.close()
    if any(codes):raise RuntimeError('Child failed: '+str(codes))
def preflight(g):
    bits=768;fp=cid(g,bits);pf=ROOT/'preflight';anchor=pf/'anchor'
    join([spawn(anchor,bits,0)]);ctx.prec=bits
    st=load(anchor,fp);ptr=rec.sha(anchor/'LATEST.json');checks={'domain_containment':domain_proof(st)['all_passed']}
    rec.atomic(anchor/'checkpoints'/'partial.uncommitted-test',{'not_resumable':True},True)
    checks['partial_write_ignored']=rec.sha(anchor/'LATEST.json')==ptr and rec.fingerprint(load(anchor,fp))==rec.fingerprint(st)
    for label,bad in [('source_input_protocol','0'*64),('precision',cid(g,1024)),('ordering',rec.fingerprint({'phase_order':list(reversed(CFG['recovery']['phase_order']))}))]:
        try:load(anchor,bad);checks['reject_'+label]=False
        except AssertionError:checks['reject_'+label]=True
    out=pf/'uninterrupted';held,ident=acquire(out);start=time.monotonic()
    try:
        expected=commit(out,step(load(anchor,fp)),fp)
        controls={str(b):base.baseline(b) for b in CFG['precisions']}
    finally:release(out,held,ident,start)
    fresh=pf/'fresh-process';fresh.mkdir();shutil.copytree(anchor/'checkpoints',fresh/'checkpoints');shutil.copy2(anchor/'LATEST.json',fresh/'LATEST.json')
    join([spawn(fresh,bits,1)]);ctx.prec=bits;actual=load(fresh,fp)
    checks['fresh_process_exact']=rec.fingerprint(actual)==rec.fingerprint(expected)
    checks['both_original_map_reproductions']=all(x['all_passed'] for x in controls.values())
    checks['original_residual_driver_bytecode_reused']=kernel.__code__ is base.kernel.__code__
    for b in CFG['precisions']:
        s=prepare(b);_,_,meta=make_fields(s['values'],s,True)
        checks[f'domain_eligibility_{b}']=all(not d['mode_denominator'].contains(0) and bounds(d['radicand'])[0]>0 for d in meta['domain'])
    checks['bindings_unchanged']=guard()==g
    body={'utc':rec.now(),'guard':g,'checks':checks,'all_passed':all(checks.values()),'controls':controls,
       'expected_state_digest':rec.fingerprint(expected),'fresh_state_digest':rec.fingerprint(actual)}
    rec.atomic(ROOT/'PREFLIGHT.json',body,True)
    if not body['all_passed']:raise ArithmeticError('Frozen recovery/domain preflight failed')

def finalize(g):
    checks={'bindings_unchanged':guard()==g,'preflight_passed':rec.read(ROOT/'PREFLIGHT.json')['all_passed']};cases={}
    for b in CFG['precisions']:
        ctx.prec=b;out=ROOT/'work'/str(b);r=rec.read(out/'RESULT.json');term=rec.read(out/'TERMINAL.json');st=load(out,cid(g,b))
        checks[f'case_integrity_{b}']=r['guard']==g and r['case_fingerprint']==cid(g,b) and term['result_sha256']==rec.sha(out/'RESULT.json')
        checks[f'case_controls_{b}']=r['all_passed'];checks[f'checkpoint_domain_{b}']=domain_proof(st)['all_passed']
        for cp in sorted((out/'checkpoints').glob('*.json')):
            body=rec.read(cp);checks[f'checkpoint_hash_{b}_{cp.name}']=body['case_fingerprint']==cid(g,b) and cp.stem.endswith(rec.fingerprint(body))
        acq=list(out.glob('ACQUIRED-*.json'));rel=list(out.glob('RELEASED-*.json'))
        checks[f'released_{b}']=len(acq)==len(rel) and all(not rec.read(p)['active'] for p in rel)
        for group in ('residuals','center_corrections'):
            for row in r[group]:
                tot=sum((Q(x) for x in row['input_radius_terms']),Q(0))+Q(row['point']['halfwidth'])+Q(row['outward_excess'])
                checks[f'width_closure_{b}_{group}_{row["index"]}']=tot==Q(row['mean_value']['halfwidth'])
        cases[str(b)]=r
    targets={}
    for i in (1,4):
        rr={b:r['targets'][str(i)] for b,r in cases.items()};pairs=[list(map(exact,r['intersection']['exact'])) for r in rr.values()]
        overlap_gate=max(x[0] for x in pairs)<=min(x[1] for x in pairs)
        checks[f'cross_precision_{i}']=overlap_gate
        targets[str(i)]={'name':CFG['targets'][str(i)],'precisions':rr,'cross_precision_overlap':overlap_gate,
          'eligible_for_independent_admission':overlap_gate and all(v['strict_tightening'] for v in rr.values()) and all(checks.values())}
    all_passed=all(checks.values())
    for t in targets.values():t['eligible_for_independent_admission']&=all_passed
    n=sum(t['eligible_for_independent_admission'] for t in targets.values())
    cls=['REMAINING_C6_CHANNELS_NOT_TIGHTENED','REMAINING_C6_CHANNEL_PARTIALLY_TIGHTENED','REMAINING_C6_CHANNELS_TIGHTENED'][n] if all_passed else 'REMAINING_C6_WIDTHS_TECHNICAL_INCOMPLETE'
    result={'utc':rec.now(),'guard':g,'classification':cls,'targets':targets,'all_local_gates_passed':all_passed,
       'attribution':{'path':'ATTRIBUTION.json','sha256':rec.sha(ROOT/'ATTRIBUTION.json')},
       'case_files':{str((ROOT/'work'/b/'RESULT.json').relative_to(ROOT)):rec.sha(ROOT/'work'/b/'RESULT.json') for b in cases},
       'C6_inclusion_rerun_by_producer':False,'independent_Initial_admission_pending':n>0,
       'uncertainty_interpretation':'All inherited uncertainty retained. Any remaining root/IVP/wrapping mixture is unresolved, not a proven irreducible physical error.',
       'standalone_novelty':'Not assessed; enabling same-source interval proof calculation.'}
    rec.atomic(ROOT/'RESULT.json',result,True)
    rec.atomic(ROOT/'LOCAL_AUDIT.json',{'utc':rec.now(),'guard':g,'checks':checks,'all_passed':all_passed},True)
    releases={str(p.relative_to(ROOT)):rec.read(p) for p in ROOT.rglob('RELEASED-*.json')}
    rec.atomic(ROOT/'RESOURCE_RELEASED.json',{'utc':rec.now(),'workers':releases,'all_released':all(not x['active'] for x in releases.values())},True)
    rec.atomic(ROOT/'TERMINAL.json',{'utc':rec.now(),'guard':g,'classification':cls,'result_sha256':rec.sha(ROOT/'RESULT.json'),
       'local_audit_sha256':rec.sha(ROOT/'LOCAL_AUDIT.json'),'resource_release_sha256':rec.sha(ROOT/'RESOURCE_RELEASED.json')},True)
    packet={'utc':rec.now(),'guard':g,'producer_root':str(ROOT),'classification':cls,
       'eligible_target_coordinates':[int(i) for i,t in targets.items() if t['eligible_for_independent_admission']],
       'resources_released':True,'C6_rerun_by_producer':False,
       'manifest':{str(p.relative_to(ROOT)):rec.sha(p) for p in ROOT.rglob('*.json') if '/progress/' not in str(p) and p.name!='STATUS.json'}}
    rec.atomic(ROOT/'STATIC_SUBMISSION.json',packet,True);rec.atomic(SHARED/'STATIC_SUBMISSION.json',packet,True)
    status(ROOT/'progress','TERMINAL',guard=g,classification=cls)
    print(json.dumps({'classification':cls,'targets':{i:{b:float(exact(r['intersection']['halfwidth'])) for b,r in t['precisions'].items()} for i,t in targets.items()}}),flush=True)

def run():
    g=guard()
    if (ROOT/'TERMINAL.json').exists() or (ROOT/'FAILURE.json').exists():raise RuntimeError('Terminal task cannot restart')
    if not (ROOT/'ATTRIBUTION.json').exists():rec.atomic(ROOT/'ATTRIBUTION.json',{'guard':g,'cases':{str(b):attribution(b,g) for b in CFG['precisions']}},True)
    status(ROOT/'progress','PREFLIGHT',guard=g,total_cases=2)
    if not (ROOT/'PREFLIGHT.json').exists():preflight(g)
    assert rec.read(ROOT/'PREFLIGHT.json')['guard']==g and rec.read(ROOT/'PREFLIGHT.json')['all_passed']
    status(ROOT/'progress','PRODUCTION',guard=g,total_cases=2)
    children=[]
    for bits in CFG['precisions']:
        out=ROOT/'work'/str(bits)
        if (out/'TERMINAL.json').exists():
            t=rec.read(out/'TERMINAL.json');assert t['guard']==g and t['result_sha256']==rec.sha(out/'RESULT.json')
        else:children.append(spawn(out,bits))
    join(children);finalize(g)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run','worker']);p.add_argument('--output',type=Path);p.add_argument('--bits',type=int);p.add_argument('--stop-after',type=int)
    args=p.parse_args();ctx.threads=1
    if args.action=='freeze':print(json.dumps({'guard':freeze()}))
    elif args.action=='worker':worker(args.output,args.bits,args.stop_after)
    else:
        try:run()
        except BaseException as ex:
            rec.atomic(ROOT/'FAILURE.json',{'utc':rec.now(),'guard':rec.sha(ROOT/'BINDINGS.json'),'error':str(ex),'traceback':traceback.format_exc()},True)
            status(ROOT/'progress','FAILED_CLOSED',error=str(ex));raise
