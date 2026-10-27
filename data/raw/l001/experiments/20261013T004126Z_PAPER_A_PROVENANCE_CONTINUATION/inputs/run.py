"""P01: uniform upper-tension neighborhood, one process on approved CPU 0."""
import argparse
import ast
import fcntl
import hashlib
import importlib.util
import json
import os
import resource
import signal
import sys
import time
import traceback
from datetime import datetime
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROUND = ROOT.parents[1]
CFG = json.loads((ROOT/'CONTRACT.json').read_text())
RESEARCH = Path('/media/psf/Home/Research')
ACADEMIC = Path('/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon')
ENGINE = ACADEMIC/'lin-d1-independent-ode-replay-20261002T225837Z/independent_d1_replay.py'
HELPERS = RESEARCH/'ClaudeCode/lines/02_lin_static/runs/20261007T030034Z/code'
if sys.platform != 'linux': raise RuntimeError('Numerical work is Linux-only')
os.sched_setaffinity(0, {CFG['cpu_id']})
resource.setrlimit(resource.RLIMIT_AS, (CFG['address_space_bytes'], CFG['address_space_bytes']))
for path, key in ((ENGINE,'engine_sha256'), (HELPERS/'inherited/records.py','records_sha256'),
                  (HELPERS/'common4.py','runtime_helper_sha256')):
    if hashlib.sha256(path.read_bytes()).hexdigest() != CFG[key]: raise RuntimeError('Changed imported source '+str(path))
sys.path[:0] = [str(HELPERS), str(HELPERS/'inherited')]
import common4 as c4
import records as rec
from flint import arb, ctx, fmpq
ctx.prec = CFG['precision_bits']; ctx.threads = 1
spec = importlib.util.spec_from_file_location('p01_inherited_independent_d1', ENGINE)
eng = importlib.util.module_from_spec(spec); sys.modules[spec.name] = eng
spec.loader.exec_module(eng)

BASE = ACADEMIC/'lin-d1-independent-ode-replay-20261002T225837Z/output/r1/RESULT.json'
D2A = ACADEMIC/'lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json'
APPROVED = ROUND/'approved/row_01'
STATUS = ROUND/'status/row_01.json'
ORIGINAL_EVENT, ORIGINAL_UPPER = eng.run_event, eng.upper_quantities
ORIGINAL_ADVANCE, ORIGINAL_PICARD = eng.advance, eng.picard_box
LB0 = eng.LAMBDA_B_Q
FLOW = None
GUARD = None
START = None
CARRIED = 0.0
PHASE = 'STARTING'


def need(ok, message):
    if not ok: raise RuntimeError(message)


def put(path, obj):
    if path.exists(): need(rec.read(path) == rec.pack(obj), 'Refuse different immutable record '+str(path))
    else: rec.atomic(path, obj, True)


def q(x):
    return Q(int(x.p), int(x.q)) if isinstance(x, fmpq) else Q(str(x))


def fq(x):
    x = q(x); return fmpq(x.numerator, x.denominator)


def ib(record):
    return tuple(map(Q, record['exact_bounds']))


def iadd(a,b): return (a[0]+b[0], a[1]+b[1])
def ineg(a): return (-a[1],-a[0])
def isub(a,b): return iadd(a,ineg(b))
def imul(a,b):
    p=[x*y for x in a for y in b]; return (min(p),max(p))
def idiv(a,b):
    need(not b[0] <= 0 <= b[1], 'Interval denominator includes zero')
    return imul(a,(1/b[1],1/b[0]))
def izero(a): return a[0] <= 0 <= a[1]
def ioverlap(a,b): return max(a[0],b[0]) <= min(a[1],b[1])
def ilowerabs(a): return Q(0) if izero(a) else min(abs(v) for v in a)
def ir(a): return {'exact_bounds':list(map(str,a)), 'decimal_bounds':list(map(float,a)), 'contains_zero':izero(a)}


def identity():
    return {'pid':os.getpid(), 'proc_start_ticks':Path('/proc/self/stat').read_text().split()[21],
        'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        'cpu_affinity':sorted(os.sched_getaffinity(0)), 'executable':str(Path(sys.executable).resolve())}


def spent(): return CARRIED+(time.monotonic()-START if START is not None else 0)
def active_work():
    return CFG['charged_intake_seconds'] + time.time()-datetime.fromisoformat(CFG['execution_work_started_utc'].replace('Z','+00:00')).timestamp()


def cap_check():
    need(spent() < CFG['linux_cumulative_wall_and_core_seconds_max'], 'Cumulative 1200-second Linux cap')
    need(active_work() < CFG['active_work_seconds_max'], '90-minute active-work cap including 431-second intake')
    if FLOW is not None: need(time.monotonic()-FLOW['started'] < CFG['event_flow_seconds_max'], 'Five-minute event-flow cap')


def status(phase=None, **kw):
    global PHASE
    if phase is not None: PHASE=phase
    obj={'round_id':ROUND.name,'row':1,'phase':PHASE,'updated_utc':rec.now(),
        'guard':GUARD,'experiment_running':True,'owned_pids':[os.getpid()], 'runtime_identity':identity(),
        'allocated_cores':1,'allocated_cpu_ids':[0],'allocated_memory_gib':2,
        'charged_intake_seconds':431,'total_active_seconds':active_work(),
        'cumulative_linux_wall_seconds':spent(),'cumulative_occupied_core_seconds':spent(),
        'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'run_path':str(ROOT),'terminal_outcome':None}
    obj.update(kw); rec.atomic(STATUS,obj)
    rec.atomic(ROOT/'COMPUTE_USAGE.json',{'elapsed_seconds':spent(),'active':True,'updated_epoch':time.time()})


def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k!='wall_seconds' and not k.startswith('_')}
    if isinstance(x,list):return [clean(v) for v in x]
    return x


def authenticate():
    need(rec.sha(APPROVED/'PROPOSAL.json')==CFG['proposal_sha256'],'Proposal changed')
    need(rec.sha(APPROVED/'GATE_REVIEW.json')==CFG['grant_sha256'],'Grant changed')
    grant=rec.read(APPROVED/'GATE_REVIEW.json'); proposal=rec.read(APPROVED/'PROPOSAL.json')
    need(grant['decision']=='APPROVED_FOR_ONE_BOUNDED_EXECUTION','Not approved')
    need(grant['allocation']=={'cpu_ids':[0],'cores':1,'memory_gib':2,'threads_per_process':1},'Allocation mismatch')
    need(grant['intake_accounting']['charged_seconds']==431,'Intake accounting mismatch')
    roots={'research':RESEARCH,'academic':ACADEMIC}; inputs={}
    for row in proposal['bindings']['files']:
        path=roots[row['root']]/row['path']; need(rec.sha(path)==row['sha256'],'Input changed '+str(path))
        inputs[str(path)]=row['sha256']
    for path in (APPROVED/'PROPOSAL.json',APPROVED/'GATE_REVIEW.json',HELPERS/'common4.py',HELPERS/'inherited/records.py'):
        inputs[str(path)]=rec.sha(path)
    need(eng.PRECISION_BITS==768 and eng.TAYLOR_ORDER==5 and eng.MAX_PICARD_ITERATIONS==32,'Kernel contract')
    need(eng.S_END==2 and CFG['steps']==16384,'Integration domain/level changed')
    need(c4.capacity()['available_bytes'] >= 2*1024**3,'Insufficient available RAM')
    data={'utc':rec.now(),'contract':CFG,'runtime':c4.runtime_fingerprint(),'inputs':inputs,
        'sources':{str(ROOT/n):rec.sha(ROOT/n) for n in ('run.py','CONTRACT.json')},
        'exact_model':{key:str(getattr(eng,key)) for key in ('M2_Q','GAMMA_Q','V0_Q','V1_Q','LAMBDA_A_Q','LAMBDA_B_Q','ROOT_CENTER_Q','ROOT_LO_Q','ROOT_HI_Q')},
        'intended_tension_exact':[str(q(LB0)+Q(v)) for v in CFG['delta_exact']],
        'affinity':sorted(os.sched_getaffinity(0))}
    put(ROOT/'BINDINGS.json',data)
    return rec.sha(ROOT/'BINDINGS.json')


def guard_check():
    b=rec.read(ROOT/'BINDINGS.json'); need(b['contract']==CFG,'Contract drift')
    for p,digest in (b['inputs']|b['sources']).items():need(rec.sha(p)==digest,'Bound bytes changed '+p)
    need(b['runtime']==c4.runtime_fingerprint(),'Runtime drift')
    f=rec.read(ROOT/'FREEZE.json')
    need(f['bindings_sha256']==rec.sha(ROOT/'BINDINGS.json'),'Bindings drift')
    need(f['preflight_sha256']==rec.sha(ROOT/'preflight/RESULT.json'),'Preflight drift')
    return rec.sha(ROOT/'FREEZE.json')


def watch_picard(initial,step):
    result=ORIGINAL_PICARD(initial,step)
    if FLOW is not None: FLOW['picard']=result[1]
    return result


def watch_upper(state):
    result=ORIGINAL_UPPER(state)
    if FLOW is not None:
        need(all(v.is_finite() for v in state),'Nonfinite physical/sensitivity cell')
        g=list(map(str,eng.bounds(result['G']))); gs=list(map(str,eng.bounds(result['G_s'])))
        FLOW['trace'].append({'cell':len(FLOW['trace']),'G':g,'G_s':gs,'picard':FLOW['picard'],
            'first_integral_contains_zero':eng.contains_zero(eng.first_integral(state)),
            'warp_lower':str(eng.bounds(result['warp'])[0]),'finite':True})
    return result


def watch_advance(initial,enclosure,step):
    cap_check(); value=ORIGINAL_ADVANCE(initial,enclosure,step)
    need(all(v.is_finite() for v in value),'Nonfinite accepted endpoint')
    if FLOW is not None and len(FLOW['trace'])%2048==0:
        status(current_flow=FLOW['name'],completed_cells=len(FLOW['trace']),total_cells=CFG['steps'])
    return value


def flow(name,a_lo,a_hi,steps):
    global FLOW
    folder=ROOT/'flows'/name; checkpoint=folder/'RESULT.json'
    if checkpoint.exists():
        saved=rec.read(checkpoint);need(saved['guard']==GUARD,'Stale flow checkpoint')
        need(saved['source_sha256']==rec.sha(ROOT/'run.py'),'Changed completed-flow source')
        need(saved['trace_sha256']==rec.sha(folder/'CELLS.json'),'Flow trace digest')
        return rec.unpack(saved['event'])
    FLOW={'name':name,'trace':[],'started':time.monotonic(),'picard':None}
    status(current_flow=name,completed_cells=0,total_cells=steps)
    try:
        event=ORIGINAL_EVENT(a_lo,a_hi,steps)
        cap_check(); need(len(FLOW['trace'])==steps,'Missing recorded cells')
        put(folder/'CELLS.json',{'guard':GUARD,'steps':steps,'trace':FLOW['trace']})
        put(checkpoint,{'guard':GUARD,'source_sha256':rec.sha(ROOT/'run.py'),'name':name,
            'launch_exact':[str(a_lo),str(a_hi)],'tension_enclosure':eng.interval_record(arb(eng.LAMBDA_B_Q)),
            'wall_seconds':time.monotonic()-FLOW['started'],'trace_sha256':rec.sha(folder/'CELLS.json'),'event':event})
        print(json.dumps({'flow':name,'seconds':time.monotonic()-FLOW['started'],'event':event['event_bracket_decimal']}),flush=True)
        return event
    finally:FLOW=None


def preflight():
    status('PREFLIGHT')
    tree=ast.parse(ENGINE.read_text())
    users=[n.name for n in tree.body if isinstance(n,ast.FunctionDef) and
           any(isinstance(x,ast.Name) and x.id=='LAMBDA_B_Q' for x in ast.walk(n))]
    upper=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='upper_quantities')
    assignments={n.targets[0].id:n.value for n in upper.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
    expected=ast.parse('G = H - tau_b / 6').body[0].value
    tau_expected=ast.parse('tau_b = arb(LAMBDA_B_Q) + arb(GAMMA_Q) * (phi - arb(V1_Q)) ** 2 / 2').body[0].value
    # Exact formal coefficients in (X, lambda_b, delta), X=H-gamma*(Phi-v1)^2/12.
    G0={'X':Q(1),'lambda_b':-Q(1,6),'delta':Q(0)}
    G1={'X':Q(1),'lambda_b':-Q(1,6),'delta':-Q(1,6)}
    difference={k:G1[k]-G0[k] for k in G0}
    controls={'only_upper_quantities_reads_lambda_b':users==['upper_quantities'],
        'G_formula_matches_reduction':ast.dump(assignments['G'])==ast.dump(expected),
        'tension_formula_matches_action':ast.dump(assignments['tau_b'])==ast.dump(tau_expected),
        'exact_formal_residual_shift':difference=={'X':Q(0),'lambda_b':Q(0),'delta':-Q(1,6)},
        'inherited_algebra_controls':all(eng.algebra_controls().values())}
    names=iter(['baseline_root','baseline_center'])
    eng.run_event=lambda lo,hi,steps:flow(next(names),lo,hi,steps)
    try:baseline=eng.run_level(CFG['steps'])
    finally:eng.run_event=ORIGINAL_EVENT
    old=next(v for v in rec.read(BASE)['levels'] if v['steps']==CFG['steps'])
    controls['baseline_public_scientific_output_exact']=clean(baseline)==clean(old)
    controls['baseline_root_and_geometry_pass']=baseline['root_replay_pass'] and baseline['geometry']['pass']
    put(ROOT/'preflight/BASELINE.json',clean(baseline))
    put(ROOT/'preflight/RESULT.json',{'utc':rec.now(),'controls':controls,'passed':all(controls.values()),
        'algebraic_identity':'G_delta=G_0-delta/6; h, launch, k and bulk RHS are independent of lambda_b',
        'no_new_neighborhood_outcome':True})
    need(all(controls.values()),'Preflight failed')
    put(ROOT/'FREEZE.json',{'utc':rec.now(),'bindings_sha256':rec.sha(ROOT/'BINDINGS.json'),
        'preflight_sha256':rec.sha(ROOT/'preflight/RESULT.json')})
    for path in (ROOT/'run.py',ROOT/'CONTRACT.json'):path.chmod(0o444)


def assemble(root,center):
    rq=root['event_quantities']; cq=center['event_quantities']; der=ib(rq['q_a'])
    box=(q(eng.ROOT_LO_Q),q(eng.ROOT_HI_Q)); cp=(q(eng.ROOT_CENTER_Q),)*2
    N=None if izero(der) else isub(cp,idiv(ib(cq['h']),der))
    inclusion=N is not None and box[0]<N[0]<=N[1]<box[1]
    lower=eng.interval_record(eng.lower_wall_identity(eng.ball(eng.ROOT_LO_Q,eng.ROOT_HI_Q)))
    geometry={'k_positive':ib(rq['curvature'])[0]>0,'D_positive':Q(root['event_bracket_exact'][0])>0,
        'conformal_length_positive':ib(rq['Z'])[0]>0,'global_warp_positive':ib(root['global_warp_enclosure'])[0]>0,
        'warp_monotone':root['all_H_strictly_negative'],'first_integral_all_cells':root['first_integral_every_cell_contains_zero'],
        'lower_wall_identity_contains_zero':izero(ib(lower)),'upper_wall_identity_contains_zero':izero(ib(rq['upper_wall_identity'])),
        'upper_Israel_contains_zero':izero(ib(rq['G'])),'upper_scalar_contains_zero':izero(ib(rq['h']))}
    flow_valid=all(ev['event_validated'] and ev['maximum_picard_iterations']<=32 for ev in (root,center))
    g2=flow_valid and not izero(der) and inclusion and all(geometry.values())
    direct=isub(imul(ib(rq['G_a']),ib(rq['h_s'])),imul(ib(rq['G_s']),ib(rq['h_a'])))
    chain=ineg(imul(ib(rq['G_s']),der))
    g3=(not izero(direct) and not izero(chain) and ioverlap(direct,chain) and
        ((direct[0]>0 and chain[0]>0) or (direct[1]<0 and chain[1]<0)))
    response=None
    if g2 and g3:
        det=(max(direct[0],chain[0]),min(direct[1],chain[1]))
        response={'da_dlambda_b':ir(idiv(ib(rq['h_s']),imul((Q(6),Q(6)),det))),
                  'dD_dlambda_b':ir(ineg(idiv(ib(rq['h_a']),imul((Q(6),Q(6)),det))))}
    return {'root_persistence_pass':g2,'isolation_pass':g3,'uniform_derivative':ir(der),
        'newton_image':ir(N) if N is not None else None,'strict_self_map':inclusion,
        'determinant_direct':ir(direct),'determinant_chain':ir(chain),'response':response,
        'geometry_checks':geometry,'lower_wall_identity':lower,'root_box_exact':list(map(str,box)),
        'event_bracket_exact':root['event_bracket_exact'],'event_bracket_decimal':root['event_bracket_decimal'],
        'curvature':rq['curvature'],'conformal_length':rq['Z'],'global_warp':root['global_warp_enclosure']}


def exclusion():
    original=rec.read(D2A);rows=[];end=Q(0);minimum=None;unresolved=[];negative=0
    delta=tuple(map(Q,CFG['delta_exact']));shift=idiv(delta,(Q(6),Q(6)))
    need(len(original['terminal_boxes'])==693,'D2A cover count changed')
    for index,box in enumerate(original['terminal_boxes']):
        lo,hi=map(Q,box['a_exact_bounds']);need(lo==end and hi>lo,'D2A cover gap/overlap');end=hi
        r=box['record'];k=tuple(map(Q,r['curvature_exact_bounds']))
        if k[1]<0:
            negative+=1;rows.append({'index':index,'a_exact':list(map(str,(lo,hi))),'kind':'NEGATIVE_CURVATURE','k_exact':list(map(str,k))});continue
        G=isub(tuple(map(Q,r['G_exact_bounds'])),shift)
        h=tuple(map(Q,r['scalar_residual_exact_bounds']))
        margin=max(ilowerabs(G),ilowerabs(h))
        if margin<=0:unresolved.append(index)
        minimum=margin if minimum is None else min(minimum,margin)
        rows.append({'index':index,'a_exact':list(map(str,(lo,hi))),'kind':'RESIDUAL_EXCLUSION' if margin>0 else 'UNRESOLVED',
            'G_exact':list(map(str,G)),'h_exact':list(map(str,h)),'lower_bound_exact':str(margin)})
    need(end==q(eng.V0_Q),'Wrong complete launch endpoint')
    return {'parent_sha256':rec.sha(D2A),'delta_exact':CFG['delta_exact'],'boxes':rows,'box_count':len(rows),
        'negative_curvature_boxes':negative,'residual_boxes':len(rows)-negative,'unresolved':unresolved,
        'exact_gap_free_cover':True,'cover_exact':['0',str(end)],'minimum_lower_bound_exact':str(minimum),
        'minimum_lower_bound_approximate':float(minimum),'old_0p0077_margin_preserved':minimum>Q(77,10000),
        'pass':not unresolved and minimum>0,'full_launch_first_event_uniqueness_extended':False}


def cell_check(name,event):
    data=rec.read(ROOT/'flows'/name/'CELLS.json');trace=data['trace'];start,last=event['event_cells']
    okay=len(trace)==CFG['steps'] and 0<start<=last<CFG['steps']-1
    kinds=[];zero=[]
    for i,row in enumerate(trace):
        G=tuple(map(Q,row['G']));Gs=tuple(map(Q,row['G_s']))
        kind=1 if G[0]>0 else (-1 if G[1]<0 else 0);kinds.append(kind)
        if kind==0:zero.append(i)
        okay=okay and row['cell']==i and 1<=row['picard']<=32 and row['finite']
        okay=okay and row['first_integral_contains_zero'] and Q(row['warp_lower'])>0
        if start<=i<=last:okay=okay and Gs[1]<0
    return okay and zero==list(range(start,last+1)) and all(k==1 for k in kinds[:start]) and all(k==-1 for k in kinds[last+1:])


def final_check(result,root,center,transport):
    checks={'bound_source_input_runtime':guard_check()==GUARD,
        'baseline_exact_match':rec.read(ROOT/'preflight/RESULT.json')['passed'],
        'root_exact_arithmetic_reconstruction':assemble(root,center)==result['neighborhood'],
        'full_D2A_exact_reconstruction':exclusion()==transport,
        'result_binding':result['guard']==GUARD}
    for name in ('baseline_root','baseline_center','uniform_root','uniform_center'):
        saved=rec.read(ROOT/'flows'/name/'RESULT.json')
        ev=rec.unpack(saved['event'])
        checks[name+'_checkpoint_and_trace']=saved['source_sha256']==rec.sha(ROOT/'run.py') and saved['trace_sha256']==rec.sha(ROOT/'flows'/name/'CELLS.json')
        checks[name+'_all_cell_event_geometry_checks']=cell_check(name,ev)
    put(ROOT/'RESULT_INTEGRITY.json',{'utc':rec.now(),'checks':checks,'passed':all(checks.values()),
        'result_sha256':rec.sha(ROOT/'RESULT.json'),'separate_independent_producer':False,
        'scope':'Integrity and exact-endpoint reconstruction; no claim of independent parameter-neighborhood replication.'})
    return all(checks.values())


def main():
    global GUARD,START,CARRIED
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['run','resume']);args=parser.parse_args()
    c4.check_environment()
    lock=open(ROOT/'RUN.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    need(not (ROOT/'FAILURE.json').exists() and not (ROOT/'RUN_COMPLETE.json').exists() and not (ROOT/'TERMINAL.json').exists(),'Do not restart terminal or failed-closed job')
    if (ROOT/'COMPUTE_USAGE.json').exists():
        need(args.command=='resume','Explicit resume required')
        previous=rec.read(ROOT/'COMPUTE_USAGE.json');CARRIED=previous['elapsed_seconds']
        if previous['active']:CARRIED+=max(0,time.time()-previous['updated_epoch'])
    START=time.monotonic()
    eng.picard_box=watch_picard;eng.upper_quantities=watch_upper;eng.advance=watch_advance
    signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('SIGTERM')))
    try:
        status('AUTHENTICATING')
        if args.command=='run':
            GUARD=authenticate();preflight()
        else:
            GUARD=rec.sha(ROOT/'BINDINGS.json')
            if not (ROOT/'FREEZE.json').exists():preflight()
        GUARD=guard_check();cap_check()
        status('UNIFORM_PARAMETER_PRODUCTION')
        eng.LAMBDA_B_Q=eng.ball(LB0+fq(CFG['delta_exact'][0]),LB0+fq(CFG['delta_exact'][1]))
        actual=tuple(map(q,eng.bounds(eng.LAMBDA_B_Q)))
        intended=(q(LB0)+Q(CFG['delta_exact'][0]),q(LB0)+Q(CFG['delta_exact'][1]))
        need(actual[0]<=intended[0]<=intended[1]<=actual[1],'Interval does not cover fixed parameter box')
        root=flow('uniform_root',eng.ROOT_LO_Q,eng.ROOT_HI_Q,CFG['steps'])
        center=flow('uniform_center',eng.ROOT_CENTER_Q,eng.ROOT_CENTER_Q,CFG['steps'])
        proof=assemble(root,center);status('EXACT_D2A_TRANSPORT');cap_check()
        transport=exclusion();put(ROOT/'D2A_TRANSPORT.json',transport)
        gates={'P01-G1':'PASS','P01-G2':'PASS' if proof['root_persistence_pass'] else 'NOT_ESTABLISHED',
            'P01-G3':'PASS' if proof['root_persistence_pass'] and proof['isolation_pass'] else 'NOT_ESTABLISHED',
            'P01-G4':'PASS' if transport['pass'] else 'NOT_ESTABLISHED'}
        allpass=all(v=='PASS' for v in gates.values())
        classification='UNIFORM_LOCAL_PERSISTENCE_ISOLATION_AND_FIXED_D0_EXCLUSION_CERTIFIED' if allpass else 'PARAMETER_NEIGHBORHOOD_PARTIAL_OR_PROOF_INCOMPLETE'
        result={'utc':rec.now(),'round_id':ROUND.name,'row':1,'guard':GUARD,'classification':classification,'gates':gates,
            'parameter':{'name':'upper-wall additive vacuum tension lambda_b','baseline_exact':str(LB0),
                'delta_exact':CFG['delta_exact'],'tension_exact':list(map(str,intended)),'outward_tension_enclosure':ir(actual)},
            'neighborhood':proof,'fixed_separation':{k:v for k,v in transport.items() if k!='boxes'},
            'runtime':{'identity':identity(),'linux_wall_seconds_at_result':spent(),'total_active_seconds_at_result':active_work(),
                'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'new_event_flows':2,'baseline_control_flows':2},
            'claim_boundary':'Local existence/uniqueness and isolation for each fixed tension in one uniform interval; full-launch fixed-D0 exclusion separately tested. Full-launch first-event global uniqueness is NOT extended beyond the original tension. No stability, dynamics, MOTS or event horizon claim.',
            'fixed_parameter_theorem_unchanged':True,'E01_comparison_result_unchanged':True,
            'historical_raw_gate_retained_failed':True,'prior_4096_step_failure_retained':True,'successor_launched':False,
            'implementation_repairs_used':CFG['repairs_used']}
        put(ROOT/'RESULT.json',result);status('FINAL_INTEGRITY_CHECK');cap_check()
        integrity=final_check(result,root,center,transport);cap_check()
        put(ROOT/'RUN_COMPLETE.json',{'utc':rec.now(),'classification':classification if integrity else 'TECHNICAL_INCOMPLETE__INTEGRITY_FAILED',
            'result_sha256':rec.sha(ROOT/'RESULT.json'),'integrity_sha256':rec.sha(ROOT/'RESULT_INTEGRITY.json'),
            'integrity_passed':integrity,'identity':identity(),'guard':GUARD,'numerical_work_complete':True,
            'process_exit_verified':False,'cumulative_linux_seconds':spent(),'total_active_seconds':active_work(),
            'successor_launched':False})
        status('AWAITING_PROCESS_EXIT_CONFIRMATION',experiment_running=False,scientific_classification=classification)
        print(json.dumps({'classification':classification,'integrity':integrity,'gates':gates,'seconds':spent()}),flush=True)
    except KeyboardInterrupt:
        status('STOPPED_RECOVERABLE_COMPLETE_FLOW_BOUNDARIES',experiment_running=False);raise
    except Exception as err:
        failure={'utc':rec.now(),'phase':PHASE,'guard':GUARD,'error':str(err),'traceback':traceback.format_exc(),
            'classification':'TECHNICAL_INCOMPLETE','not_a_physical_exclusion':True,'identity':identity(),
            'cumulative_linux_seconds':spent(),'total_active_seconds':active_work()}
        put(ROOT/'FAILURE.json',failure);status('FAILED_CLOSED',experiment_running=False,error=str(err));raise
    finally:
        rec.atomic(ROOT/'COMPUTE_USAGE.json',{'elapsed_seconds':spent(),'active':False,'updated_epoch':time.time()})


if __name__=='__main__':main()
