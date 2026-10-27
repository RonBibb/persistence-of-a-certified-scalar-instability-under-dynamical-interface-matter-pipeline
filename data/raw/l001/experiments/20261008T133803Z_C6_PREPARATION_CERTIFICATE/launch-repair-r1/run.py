"""Bounded Linux runner; exact checkpoints precede all reported progress."""
from common import *
import argparse, signal, traceback, subprocess, math
import flow, physics
STOP=False
def stop_request(signum,frame):
    global STOP
    STOP=True

def publish_progress(job,state,st=None,**extra):
    d={'utc':rec.now(),'job':job,'state':state,'pid':os.getpid(),'source_guard':rec.sha(ROOT/'BINDINGS.json')}
    if st is not None:
        total=int(math.ceil(bounds(st['p']['D'])[1]/exact(CFG['step'])))
        d.update(completed_cells=st['cell_index'],total_cells=total,
          elapsed_seconds=st['elapsed_seconds'],cpu_seconds=st['cpu_seconds'])
        d['remaining_seconds_estimate']=(total-st['cell_index'])*st['elapsed_seconds']/st['cell_index'] if st['cell_index'] else None
        p=ROOT/'output'/job/'LATEST.json'
        if p.exists():d['last_durable_checkpoint']=rec.read(p)
    d.update(extra);rec.atomic(ROOT/'progress'/f'{job}.json',d)
    return d

def charge_budget(job,delta):
    if delta<0:raise RuntimeError('Negative numerical CPU charge')
    p=ROOT/'progress'/'CPU_BUDGET.json';lock=ROOT/'progress'/'budget.lock'
    with lock.open('a+') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        d=rec.read(p) if p.exists() else {'jobs':{}}
        d['jobs'][job]=d['jobs'].get(job,0.0)+delta
        d.update(utc=rec.now(),total_core_seconds=sum(d['jobs'].values()),ceiling=CFG['execution']['maximum_cumulative_numerical_core_seconds'])
        rec.atomic(p,d)
        if d['total_core_seconds']>=d['ceiling']:raise ArithmeticError('Frozen cumulative numerical CPU budget exhausted')

def job_finished(output,g):
    p=output/'TERMINAL.json'
    if not p.exists():return False
    d=rec.read(p)
    if d['guard']!=g or rec.sha(output/'RESULT.json')!=d['result_sha256']:raise ArithmeticError('Invalid existing worker terminal')
    return True

def worker(job,bits,which,g):
    from inherited.series import bounds
    import mapping
    output=ROOT/'output'/job;output.mkdir(parents=True,exist_ok=True)
    if job_finished(output,g):return
    if (output/'FAILURE.json').exists():raise RuntimeError('Failed-closed worker cannot be resumed')
    ref=None
    if (output/'LATEST.json').exists():
        st=rec.load(output,g);assert st['bits']==bits and st['which']==which
        ctx.prec=bits
    else:
        root_box=None
        if which=='map':
            a=rec.read(ROOT/'DECISION.json');assert a['preparation_passed']
            root_box=a['decisions']['1024']['root_enclosure']
        st=flow.initial(bits,which,g,root_box)
        if which=='map':
            st['y']=st['y'][:11];st['initial_y']=st['initial_y'][:11];st['map_stats']=mapping.new_stats()
        rec.save(output,st,g)
    if which=='map':ref=mapping.Reference()
    publish_progress(job,'RUNNING',st,bits=bits,phase='VALIDATED_FLOW')
    origin_wall=time.monotonic();origin_cpu=time.process_time();oldwall=st['elapsed_seconds'];oldcpu=st['cpu_seconds'];lastcharge=origin_cpu
    try:
        while not flow.complete(st):
            if st['cell_index']>=CFG['execution']['maximum_validated_cells_per_flow']:raise ArithmeticError('Frozen validated-cell ceiling exhausted')
            cell=flow.advance(st)
            if ref is not None:mapping.compare(st,cell,st['last_cell']['s'],ref)
            st['elapsed_seconds']=oldwall+time.monotonic()-origin_wall;st['cpu_seconds']=oldcpu+time.process_time()-origin_cpu
            if st['cell_index']%16==0:
                nowcpu=time.process_time();charge_budget(job,nowcpu-lastcharge);lastcharge=nowcpu
            if st['cell_index']%CFG['checkpoint_cells']==0 or STOP or flow.complete(st):
                rec.save(output,st,g)
                publish_progress(job,'STOPPED' if STOP else 'RUNNING',st,bits=bits,phase='VALIDATED_FLOW')
                print(json.dumps({'utc':rec.now(),'job':job,'cells':st['cell_index'],'elapsed':st['elapsed_seconds']}),flush=True)
            if STOP:return
        if not flow.check_cover(st):raise ArithmeticError('Endpoint event cover incomplete')
        publish_progress(job,'RUNNING',st,phase='ENDPOINT_CORNER_MAP',bits=bits)
        corner=physics.corner_map(st['initial_y'],st['end'],st['p'])
        result={'utc':rec.now(),'guard':g,'bits':bits,'which':which,'completed_cells':st['cell_index'],
             'endpoint_event_cover':st['cover'],'endpoint_cover_passed':True,'max_picard_iterations':st['max_picard'],
             'map':corner,'p':st['p'],'initial_y':st['initial_y'],'endpoint_y':st['end'],
             'wall_seconds':oldwall+time.monotonic()-origin_wall,'cpu_seconds':oldcpu+time.process_time()-origin_cpu,
             'last_checkpoint':rec.read(output/'LATEST.json')}
        if ref is not None:result['observable_bounds']=mapping.finish(st,corner,ref)
        rec.atomic(output/'RESULT.json',result,True)
        rec.atomic(output/'TERMINAL.json',{'utc':rec.now(),'guard':g,'result_sha256':rec.sha(output/'RESULT.json'),
            'classification':'VALIDATED_FLOW_COMPLETE_NOT_JOINT_CERTIFICATE'},True)
        publish_progress(job,'COMPLETE',st,terminal_sha256=rec.sha(output/'TERMINAL.json'))
    except BaseException as exc:
        if not isinstance(exc,(KeyboardInterrupt,SystemExit)):
            rec.atomic(output/'FAILURE.json',{'utc':rec.now(),'guard':g,'cell':st['cell_index'],'error':str(exc),
                'type':type(exc).__name__,'traceback':traceback.format_exc(),'classification':'TECHNICAL_INCOMPLETE_NOT_EXCLUSION'},True)
            publish_progress(job,'FAILED_CLOSED',st,error=str(exc))
        raise
    finally:
        nowcpu=time.process_time()
        try:charge_budget(job,nowcpu-lastcharge)
        except ArithmeticError:
            if (output/'TERMINAL.json').exists():raise

def assemble(g):
    import checks
    decisions={};raws={};producer={}
    for bits in CFG['precision_ladder_bits']:
        cc=ROOT/'output'/f'{bits}-center';bb=ROOT/'output'/f'{bits}-box'
        assert job_finished(cc,g) and job_finished(bb,g)
        ctx.prec=bits
        c=rec.unpack(rec.read(cc/'RESULT.json'));b=rec.unpack(rec.read(bb/'RESULT.json'))
        raw=checks.raw_decision(c,b);d=checks.rational_decision(raw);a=flow.decision(c,b)
        # Rational audit may be sharper but must be enclosed by the outward Arb calculation.
        assert all(Q(x)<=Q(y) for x,y in zip(d['image_radius'],a['image_radius']))
        assert all(Q(x)<=Q(y) for x,y in zip(d['weighted_row_norm'],a['weighted_row_norm']))
        decisions[str(bits)]=d;raws[str(bits)]=raw;producer[str(bits)]=a
        rec.atomic(ROOT/f'RAW_DECISION_{bits}.json',raw,True)
    D=rec.read(ROOT/'DESIGN.json');c=list(map(Q,D['center']));r=list(map(Q,D['radii']))
    domain=abs(c[0])+r[0]<Q(CFG['scientific_gates']['parameter_domain_metric_adjustment_max']) and all(abs(v)+a<=1 for v,a in zip(c[1:],r[1:]))
    passed=domain and all(d['passed'] for d in decisions.values()) and all(d['passed'] for d in producer.values())
    rec.atomic(ROOT/'DECISION.json',{'utc':rec.now(),'guard':g,'preparation_passed':passed,
         'frozen_box_domain_passed':domain,'decisions':decisions,'producer_arb_decisions':producer,
         'method':'Both outward Arb and separate exact Fraction gates required at both precisions.',
         'no_exclusion_inferred_from_failed_inclusion':True},True)

def terminal(g,failures=None):
    import checks
    failures=failures or [];d=rec.read(ROOT/'DECISION.json') if (ROOT/'DECISION.json').exists() else None
    jobs=[f'{b}-{w}' for b in CFG['precision_ladder_bits'] for w in ('center','box')]
    mapout=ROOT/'output'/'1024-map';mapok=False;bound=None
    if job_finished(mapout,g):
        jobs+=['1024-map'];bound=rec.unpack(rec.read(mapout/'RESULT.json'))['observable_bounds']
        mapok=bound['all_required_bounds_finite'] and bound['material_domain_passed']
    budget=rec.read(ROOT/'progress'/'CPU_BUDGET.json') if (ROOT/'progress'/'CPU_BUDGET.json').exists() else {'total_core_seconds':0}
    budget_ok=budget['total_core_seconds']<=CFG['execution']['maximum_cumulative_numerical_core_seconds']
    prepared=bool(d and d['preparation_passed'] and not failures and budget_ok)
    classification=('C6_PREPARATION_AND_MAP_CERTIFIED' if mapok else 'C6_PREPARATION_CERTIFIED_MAP_BOUNDS_INCOMPLETE') if prepared else 'C6_PREPARATION_CERTIFICATE_INCOMPLETE'
    gates={'current_source_and_inputs_bound':guard()==g,'preflight_passed':rec.read(ROOT/'PREFLIGHT.json')['all_passed'],'cumulative_cpu_budget_respected':budget_ok,
      'registered_equations_and_corners':rec.read(inputs()['initial_analytic_review'])['stage']=='ANALYTIC_FORMULATION_CHECKED_NUMERICAL_CERTIFICATE_PENDING'}
    evidence={}
    for job in jobs:
        p=ROOT/'output'/job
        if not job_finished(p,g):
            evidence[job]={'complete':False,'failure_present':(p/'FAILURE.json').exists()};continue
        v=rec.unpack(rec.read(p/'RESULT.json'));count=0;last=-1
        for cp in sorted((p/'checkpoints').glob('*.json')):
            body=rec.read(cp);st=rec.unpack(body['state']);assert body['guard']==g and st['guard']==g
            assert cp.name.endswith(rec.fingerprint(body)+'.json')
            assert st['cell_index']>last;last=st['cell_index'];count+=1
        release_record=rec.read(ROOT/'progress'/f'{job}.release.json')
        assert not release_record['active']
        gates[job+'_archive_integrity']=v['guard']==g and v['endpoint_cover_passed'] and last==v['completed_cells']
        evidence[job]={'complete':True,'checkpoints_verified':count,'result_sha256':rec.sha(p/'RESULT.json'),'terminal_sha256':rec.sha(p/'TERMINAL.json'),
          'resource_release_sha256':rec.sha(ROOT/'progress'/f'{job}.release.json')}
    if d:
        for bits in CFG['precision_ladder_bits']:
            raw=rec.read(ROOT/f'RAW_DECISION_{bits}.json');again=checks.rational_decision(raw)
            gates[f'{bits}_rational_decision_reproduced']=again==d['decisions'][str(bits)]
    local={'utc':rec.now(),'guard':g,'checks':gates,'all_passed':all(gates.values()),'workers':evidence,
        'method':'Separate exact rational interval calculation and full native checkpoint/hash walk; Initial owner provides independent scientific audit.'}
    rec.atomic(ROOT/'LOCAL_AUDIT.json',local,True)
    if not local['all_passed']:classification='C6_PREPARATION_CERTIFICATE_INCOMPLETE'
    result={'utc':rec.now(),'guard':g,'classification':classification,'joint_classification':False,
        'preparation_passed':prepared,'continuum_map_passed':mapok,'failures':failures,
        'decision_sha256':rec.sha(ROOT/'DECISION.json') if d else None,
        'observable_bounds':bound,'local_audit_sha256':rec.sha(ROOT/'LOCAL_AUDIT.json'),
        'scope':'Fixed physical initial-data certificate; no evolution, nonlinear stability, horizon or cosmology claim.'}
    rec.atomic(ROOT/'RESULT.json',result,True)
    rec.atomic(ROOT/'TERMINAL.json',{'utc':rec.now(),'guard':g,'result_sha256':rec.sha(ROOT/'RESULT.json'),
        'local_audit_sha256':rec.sha(ROOT/'LOCAL_AUDIT.json'),'classification':classification,'joint_classification':False},True)
    packet={'utc':rec.now(),'guard':g,'classification':classification,'joint_classification':False,
        'producer_root':str(ROOT),'artifacts':{str(p.relative_to(ROOT)):rec.sha(p) for p in sorted(ROOT.rglob('*.json')) if '/checkpoints/' not in str(p) and '/progress/' not in str(p) and '/preflight/' not in str(p)},
        'resources_released':True,'workers':evidence,'awaiting_independent_initial_audit':True}
    rec.atomic(ROOT/'CANDIDATE_CERTIFICATE_PACKET.json',packet,True)
    shared=loc('/Users/ronbibb/Research/research_repositories/lin/shared/integration/20261008T133803Z_C6_PREPARATION_CERTIFICATE')
    rec.atomic(shared/'STATIC_CANDIDATE_CERTIFICATE_PACKET_LAUNCH_REPAIR_R1.json',packet,True)
    publish_progress('orchestrator','TERMINAL',classification=classification,result_sha256=rec.sha(ROOT/'RESULT.json'))

def orchestrate(g):
    lock=(ROOT/'progress'/'orchestrator.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if (ROOT/'TERMINAL.json').exists():
        assert rec.read(ROOT/'TERMINAL.json')['result_sha256']==rec.sha(ROOT/'RESULT.json');return
    assert rec.read(ROOT/'PREFLIGHT.json')['all_passed']
    jobs=[(f'{b}-{w}',b,w,cpu) for cpu,(b,w) in enumerate((b,w) for b in CFG['precision_ladder_bits'] for w in ('center','box'))]
    children=[];files=[]
    def launch(job,bits,which,cpu):
        log=(ROOT/'logs'/f'{job}.log').open('a');files.append(log)
        cmd=[sys.executable,'-B',str(ROOT/'run.py'),'flow','--job',job,'--bits',str(bits),'--which',which,'--cpu',str(cpu)]
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
        return job,proc,cmd
    (ROOT/'logs').mkdir(exist_ok=True)
    for row in jobs:
        if not job_finished(ROOT/'output'/row[0],g):children.append(launch(*row))
    publish_progress('orchestrator','RUNNING',workers=[{'job':j,'pid':p.pid,'command':cmd} for j,p,cmd in children],cpu_ids=[0,1,2,3],phase='FOUR_FROZEN_FLOWS')
    while any(p.poll() is None for j,p,cmd in children):
        if STOP:
            for j,p,cmd in children:
                if p.poll() is None:p.send_signal(signal.SIGINT)
        time.sleep(5)
    if STOP:publish_progress('orchestrator','STOPPED');return
    failed=[{'job':j,'returncode':p.returncode} for j,p,cmd in children if p.returncode]
    if not failed:
        if not (ROOT/'DECISION.json').exists():assemble(g)
        if rec.read(ROOT/'DECISION.json')['preparation_passed']:
            j,p,cmd=launch('1024-map',1024,'map',0)
            publish_progress('orchestrator','RUNNING',phase='CONDITIONAL_ROOT_MAP',workers=[{'job':j,'pid':p.pid,'command':cmd}],cpu_ids=[0])
            while p.poll() is None:
                if STOP:p.send_signal(signal.SIGINT)
                time.sleep(5)
            if STOP:publish_progress('orchestrator','STOPPED');return
            # Map failure does not undo an otherwise certified preparation.
            if p.returncode:publish_progress('orchestrator','MAP_INCOMPLETE',returncode=p.returncode)
    terminal(g,failed)
    for f in files:f.close()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['preflight','resume-control','flow','orchestrate','finalize'])
    ap.add_argument('--cpu',type=int,default=0);ap.add_argument('--bits',type=int,choices=[768,1024],default=768)
    ap.add_argument('--which',choices=['center','box','map'],default='center');ap.add_argument('--job');ap.add_argument('--guard')
    args=ap.parse_args();ctx.threads=1;ctx.prec=args.bits
    from inherited.series import bounds
    (ROOT/'progress').mkdir(exist_ok=True)
    signal.signal(signal.SIGINT,stop_request);signal.signal(signal.SIGTERM,stop_request)
    g=guard();start=time.monotonic()
    if args.action=='resume-control':
        import checks
        assert args.guard==g
        st=rec.load(ROOT/'preflight',g);a=rec.fingerprint(checks.numerical_state(st));flow.advance(st)
        rec.atomic(ROOT/'preflight'/'FRESH_PROCESS.json',{'guard':g,'loaded_fingerprint':a,
            'numeric_fingerprint':rec.fingerprint(checks.numerical_state(st)),'pid':os.getpid()},True)
    elif args.action in ('preflight','flow'):
        job=args.job or 'preflight';handles,identity=resources(args.cpu,job)
        try:
            if args.action=='preflight':
                import checks
                publish_progress(job,'RUNNING',phase='IMPLEMENTATION_AND_RESUME_CONTROL')
                result=checks.preflight(g);charge_budget(job,time.process_time());publish_progress(job,'COMPLETE',passed=result['all_passed'])
            else:
                assert rec.read(ROOT/'PREFLIGHT.json')['all_passed']
                worker(job,args.bits,args.which,g)
        finally:release(handles,identity,start)
    elif args.action=='orchestrate':orchestrate(g)
    elif args.action=='finalize':terminal(g)
