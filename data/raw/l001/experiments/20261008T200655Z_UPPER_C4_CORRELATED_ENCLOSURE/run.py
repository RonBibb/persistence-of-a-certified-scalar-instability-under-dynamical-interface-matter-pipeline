"""Frozen finite graph, fresh-process recovery control, concurrent precision cases."""
from runtime import *
import enclosure as e
import argparse, subprocess, signal, traceback, shutil
STOP=False
def stopping(*args):
    global STOP
    STOP=True
def worker(out,bits,mode,stop_after=None):
    g=guard();cid=case_id(g,bits,mode);ctx.prec=bits
    if (out/'TERMINAL.json').exists():raise RuntimeError('Terminal case cannot be restarted')
    if (out/'FAILURE.json').exists():raise RuntimeError('Failed-closed case cannot be restarted')
    held,ident=acquire(out);start=time.monotonic()
    signal.signal(signal.SIGINT,stopping);signal.signal(signal.SIGTERM,stopping)
    try:
        st=load(out,cid) if (out/'LATEST.json').exists() else commit(out,e.prepare(bits,mode),cid)
        if stop_after==st['phase']:return
        while st['phase']<3:
            if STOP:status(out,'STOPPED',case_fingerprint=cid,phase=st['phase']);return
            t=time.monotonic();st=commit(out,e.step(st),cid)
            print(json.dumps({'bits':bits,'mode':mode,'phase':st['phase'],'seconds':time.monotonic()-t}),flush=True)
            if stop_after==st['phase']:return
        result=dict(st['case_result'],guard=g,case_fingerprint=cid,latest_checkpoint=rec.read(out/'LATEST.json'))
        rec.atomic(out/'RESULT.json',result,True)
        rec.atomic(out/'TERMINAL.json',{'guard':g,'case_fingerprint':cid,'result_sha256':rec.sha(out/'RESULT.json'),
           'all_passed':result['all_passed'],'utc':rec.now()},True)
        status(out,'TERMINAL',case_fingerprint=cid,all_passed=result['all_passed'])
    except BaseException as exc:
        rec.atomic(out/'FAILURE.json',{'guard':g,'case_fingerprint':cid,'error':str(exc),'traceback':traceback.format_exc(),'utc':rec.now()},True)
        status(out,'FAILED_CLOSED',error=str(exc));raise
    finally:release(out,held,ident,start)

def command(out,bits,mode,stop=None):
    a=[sys.executable,'-B',str(ROOT/'run.py'),'worker','--output',str(out),'--bits',str(bits),'--mode',mode]
    if stop is not None:a+=['--stop-after',str(stop)]
    return a
def spawn(a,out):
    out.mkdir(parents=True,exist_ok=True)
    log=(out/f'launch-{time.time_ns()}.log').open('w')
    return subprocess.Popen(a,stdout=log,stderr=subprocess.STDOUT),log
def joined(items):
    result=[]
    for p,log in items:
        result.append(p.wait());log.close()
    if any(result):raise RuntimeError('Child process failed: '+str(result))

def preflight():
    g=guard();pf=ROOT/'preflight';pf.mkdir(exist_ok=True)
    if (ROOT/'PREFLIGHT.json').exists():raise RuntimeError('Preflight already sealed')
    bits=768;mode='wall_identities';cid=case_id(g,bits,mode)
    anchor=pf/'anchor';joined([spawn(command(anchor,bits,mode,0),anchor)])
    before=rec.sha(anchor/'LATEST.json');s=load(anchor,cid)
    checks={'native_roundtrip':rec.fingerprint(rec.unpack(rec.pack(s)))==rec.fingerprint(s),'anchor_is_real_primitive_checkpoint':s['phase']==0}
    # Simulate a crash that leaves an uncommitted write; only LATEST may select a checkpoint.
    rec.atomic(anchor/'checkpoints'/'partial.uncommitted-test',{'not_a_checkpoint':True},True)
    checks['partial_write_ignored']=rec.sha(anchor/'LATEST.json')==before and rec.fingerprint(load(anchor,cid))==rec.fingerprint(s)
    for label,altered in [('source_or_input','0'*64),('precision',case_id(g,1024,mode)),('representation',case_id(g,bits,'static_hamiltonian')),
                          ('order',rec.fingerprint({'guard':g,'bits':bits,'mode':mode,'phase_order':list(reversed(CFG['restart']['phases']))}))]:
        try:load(anchor,altered);checks['reject_'+label]=False
        except AssertionError:checks['reject_'+label]=True
    # Continuation A runs in this current process from the canonical saved state.
    out=pf/'uninterrupted';held,ident=acquire(out);t=time.monotonic()
    try:expected=commit(out,e.step(load(anchor,cid)),cid)
    finally:release(out,held,ident,t)
    # Continuation B is a new interpreter which deserializes the same actual checkpoint.
    restart=pf/'fresh-process';restart.mkdir()
    shutil.copytree(anchor/'checkpoints',restart/'checkpoints');shutil.copy2(anchor/'LATEST.json',restart/'LATEST.json')
    joined([spawn(command(restart,bits,mode,1),restart)])
    actual=load(restart,cid);checks['fresh_process_continuation_exact']=rec.fingerprint(actual)==rec.fingerprint(expected)
    controls={}
    for b in CFG['precisions']:
        ctx.prec=b;controls[str(b)]=e.baseline(b);checks[f'original_map_reproduction_{b}']=controls[str(b)]['all_passed']
    physics.Dual.size=1;x=physics.Dual(arb(4),[arb(1)]);y=e.sqrt_dual(x)
    checks['sqrt_AD_value']=(y.v-2).contains(0);checks['sqrt_AD_derivative']=(y.d[0]-arb(fmpq(1,4))).contains(0)
    try:e.sqrt_dual(physics.Dual(interval(-1,2),[arb(1)]));checks['sqrt_nonsingularity_rejection']=False
    except ArithmeticError:checks['sqrt_nonsingularity_rejection']=True
    checks['bindings_unchanged']=guard()==g
    body={'utc':rec.now(),'guard':g,'checks':checks,'controls':controls,'all_passed':all(checks.values()),
       'recovery_anchor':str(anchor/'LATEST.json'),'expected_state_digest':rec.fingerprint(expected),'fresh_process_state_digest':rec.fingerprint(actual)}
    rec.atomic(ROOT/'PREFLIGHT.json',body,True)
    if not body['all_passed']:raise ArithmeticError('Frozen preflight failed')
    return body

def finalize(g):
    cases={};checks={'preflight_passed':rec.read(ROOT/'PREFLIGHT.json')['all_passed'],'bindings_unchanged':guard()==g}
    for b in CFG['precisions']:
        for m in CFG['representations']:
            out=ROOT/'work'/f'{b}-{m}';r=rec.read(out/'RESULT.json');term=rec.read(out/'TERMINAL.json');cid=case_id(g,b,m)
            checks[f'integrity_{b}_{m}']=r['guard']==g and r['case_fingerprint']==cid and term['result_sha256']==rec.sha(out/'RESULT.json')
            checks[f'local_controls_{b}_{m}']=r['all_passed']
            load(out,cid)
            acquired=list(out.glob('ACQUIRED-*.json'));released=list(out.glob('RELEASED-*.json'))
            checks[f'released_{b}_{m}']=len(acquired)==len(released) and all(not rec.read(p)['active'] for p in released)
            cases[f'{b}-{m}']=r
    comparisons={}
    for b in CFG['precisions']:
        old=predecessor_intersections(b,'F')[2];lo,hi=old
        for m in CFG['representations']:
            a,z=map(exact,cases[f'{b}-{m}']['residuals'][2]['mean_value']['exact']);lo=max(lo,a);hi=min(hi,z)
        checks[f'nonempty_{b}']=lo<=hi
        if lo>hi:raise ArithmeticError('Two correlated representations have empty intersection')
        comparisons[str(b)]={'prior':record_pair(old),'new':record_pair((lo,hi)),
           'strict_tightening':hi-lo<old[1]-old[0],
           'width_ratio':str((hi-lo)/(old[1]-old[0]))}
    a,b=[list(map(exact,comparisons[str(p)]['new']['exact'])) for p in CFG['precisions']]
    checks['cross_precision_overlap']=max(a[0],b[0])<=min(a[1],b[1])
    cls='UPPER_C4_CORRELATED_ENCLOSURE_TECHNICAL_INCOMPLETE'
    if all(checks.values()):
        cls='UPPER_C4_CORRELATED_ENCLOSURE_TIGHTENED' if all(r['strict_tightening'] for r in comparisons.values()) else 'UPPER_C4_CORRELATED_ENCLOSURE_NOT_TIGHTENED'
    # Independent local rational accounting; no root-certificate test is evaluated.
    for name,r in cases.items():
        for group in ('residuals','center_corrections'):
            for row in r[group]:
                s=sum((Q(t) for t in row['input_radius_terms']),Q(0))
                checks[f'width_accounting_{name}_{group}_{row["index"]}']=s+Q(row['point']['halfwidth'])+Q(row['outward_excess'])==Q(row['mean_value']['halfwidth'])
    if not all(checks.values()):cls='UPPER_C4_CORRELATED_ENCLOSURE_TECHNICAL_INCOMPLETE'
    result={'utc':rec.now(),'guard':g,'classification':cls,'primary_quantity':'upper scalar C4 residual index 2',
       'comparisons':comparisons,'all_local_gates_passed':all(checks.values()),'independent_admission_pending':True,
       'case_files':{str((ROOT/'work'/n/'RESULT.json').relative_to(ROOT)):rec.sha(ROOT/'work'/n/'RESULT.json') for n in cases},
       'enabling_value':'Sharper enclosure of the same C6 center; only Initial may admit it and apply the unchanged inclusion inequalities.',
       'standalone_novelty':'Not assessed; this is an enabling validated-numerical calculation, not a new physics result.',
       'no_new_IVP_or_C6_root_decision':True}
    rec.atomic(ROOT/'RESULT.json',result,True)
    rec.atomic(ROOT/'LOCAL_AUDIT.json',{'utc':rec.now(),'guard':g,'checks':checks,'all_passed':all(checks.values())},True)
    resources={str(p.relative_to(ROOT)):rec.read(p) for p in (ROOT/'work').rglob('RELEASED-*.json')}
    rec.atomic(ROOT/'RESOURCE_RELEASED.json',{'utc':rec.now(),'all_released':all(not d['active'] for d in resources.values()),'workers':resources},True)
    rec.atomic(ROOT/'TERMINAL.json',{'utc':rec.now(),'guard':g,'classification':cls,'result_sha256':rec.sha(ROOT/'RESULT.json'),
        'local_audit_sha256':rec.sha(ROOT/'LOCAL_AUDIT.json'),'resource_release_sha256':rec.sha(ROOT/'RESOURCE_RELEASED.json')},True)
    packet={'utc':rec.now(),'producer_root':str(ROOT),'guard':g,'classification':cls,
        'eligible_for_independent_admission':cls=='UPPER_C4_CORRELATED_ENCLOSURE_TIGHTENED',
        'manifest':{str(p.relative_to(ROOT)):rec.sha(p) for p in ROOT.rglob('*.json') if '/progress/' not in str(p) and p.name!='STATUS.json'},
        'resources_released':True}
    rec.atomic(ROOT/'STATIC_SUBMISSION.json',packet,True);rec.atomic(SHARED/'STATIC_SUBMISSION.json',packet,True)
    status(ROOT/'progress','TERMINAL',guard=g,classification=cls)
    print(json.dumps({'classification':cls,'comparisons':{k:dict(prior_halfwidth=v['prior']['halfwidth'],new_halfwidth=v['new']['halfwidth']) for k,v in comparisons.items()}}),flush=True)

def production():
    g=guard()
    if (ROOT/'TERMINAL.json').exists() or (ROOT/'FAILURE.json').exists():raise RuntimeError('Terminal or failed-closed task cannot be restarted')
    if not (ROOT/'PREFLIGHT.json').exists():preflight()
    assert rec.read(ROOT/'PREFLIGHT.json')['guard']==g and rec.read(ROOT/'PREFLIGHT.json')['all_passed']
    status(ROOT/'progress','PRODUCTION',guard=g,completed_cases=0,total_cases=4)
    children=[]
    for bits in CFG['precisions']:
        for mode in CFG['representations']:
            out=ROOT/'work'/f'{bits}-{mode}'
            if (out/'TERMINAL.json').exists():
                t=rec.read(out/'TERMINAL.json');assert t['guard']==g and t['result_sha256']==rec.sha(out/'RESULT.json');continue
            children.append(spawn(command(out,bits,mode),out))
    joined(children);finalize(g)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','preflight','run','worker'])
    ap.add_argument('--output',type=Path);ap.add_argument('--bits',type=int);ap.add_argument('--mode',choices=CFG['representations']);ap.add_argument('--stop-after',type=int)
    args=ap.parse_args();ctx.threads=1
    if args.action=='freeze':print(json.dumps({'guard':freeze()}))
    elif args.action=='worker':worker(args.output,args.bits,args.mode,args.stop_after)
    else:
        try:preflight() if args.action=='preflight' else production()
        except BaseException as ex:
            if not (ROOT/'FAILURE.json').exists():rec.atomic(ROOT/'FAILURE.json',{'utc':rec.now(),'guard':rec.sha(ROOT/'BINDINGS.json'),'error':str(ex),'traceback':traceback.format_exc()},True)
            status(ROOT/'progress','FAILED_CLOSED',error=str(ex));raise
