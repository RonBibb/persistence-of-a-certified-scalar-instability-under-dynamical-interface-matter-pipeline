#!/usr/bin/env python3
"""Prospectively frozen interval background and all-mode scalar bound."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction
import argparse,datetime,gzip,hashlib,json,os,signal,time,traceback
from dyadic_interval import I,BITS,SCALE
from background_engine import initial,step,evaluate,controls,NAMES
ROOT=Path(__file__).resolve().parent
DEADLINE=datetime.datetime.fromisoformat('2026-10-19T16:03:42+00:00')
STEP=Fraction(1,8192)
CHUNK=256
STAGE={'stage':'startup'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc)
def encode(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def atomic(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    with tmp.open('wb') as f:f.write(encode(d)+b'\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def vector_dump(y):return [x.dump() for x in y]
def vector_load(y):return [I.load(x) for x in y]
def hull(a,b):return [x.hull(y) for x,y in zip(a,b)]
def guard():
    a=json.loads((ROOT/'NUMERICAL_ADMISSION.json').read_text())
    if not a['admitted']:raise RuntimeError('No independent prelaunch admission')
    for n,h in a['executable_bindings'].items():
        if sha(ROOT/n)!=h:raise RuntimeError('Changed admitted code/plan/input')
    for e in json.loads((ROOT/'INPUTS.json').read_text())['files']:
        if sha(ROOT/e['snapshot'])!=e['sha256'] or sha(e['source'])!=e['sha256']:raise RuntimeError('Changed scientific source/snapshot')
    g={'files':{n:sha(ROOT/n) for n in ['CHECK_PLAN.md','INPUTS.json','INTERVAL_CERTIFICATE_PLAN.md','WEIGHTED_ALL_MODE_PROOF.md','dyadic_interval.py','background_engine.py','certificate_runner.py','certificate_harness.py','NUMERICAL_ADMISSION.json']},'python':sys.version,'python_executable':sys.executable,'python_executable_sha256':sha(sys.executable),'arithmetic':'outward fixed-point integer intervals','bits':BITS,'step':str(STEP),'order':5,'chunk_cells':CHUNK,'rng':'none'}
    return hashlib.sha256(encode(g)).hexdigest(),g

def gates(p,ran,event):
    W,H,P,T,E,q=ran;k=p['k'];mp=p['m2']*P.square()
    result={'positive_k':k.lo>0,'k_below_1_over_3000':k.hi*3000<SCALE,'positive_warp_reciprocal':E.lo>0,'Ewarp_below_8':E.hi<8*SCALE,'mPhi_squared_below_1':mp.hi<SCALE,'negative_H':H.hi<0}
    if event is not None:result['positive_event_width']=event[5].lo>0
    return result

def readout(y,p):
    W,H,P,T,E,q=y;a=E.reciprocal();a2=a*a;alpha=a2*a;ar=3*a2*a2*H
    arr=alpha*(9*p['k']+a2*(12-p['m2']*P.square()))
    first=H.square()-1-T.square()/12+p['m2']*P.square()/12-p['k']*E.square()
    return {'a':a,'alpha':alpha,'sigma_r':a*H,'Phi_r':a*T,'alpha_r':ar,'alpha_rr':arr,'first_integral':first,'mPhi_squared':p['m2']*P.square()}

def result(out,state,p):
    ran=vector_load(state['whole_collar']);event=vector_load(state['D_event']) if state['D_event'] else None;gs=gates(p,ran,event)
    complete=Fraction(state['s'])==Fraction(state['D_hi'])
    cc=readout(ran,p);endpoint={}
    if event is not None:
        W,H,P,T,E,q=event
        endpoint={'upper_scalar_residual':T+p['gamma']*(P-p['v1'])/2,'upper_metric_residual':H-(p['lambda_b']+p['gamma']*(P-p['v1']).square()/2)/6}
    if complete and (event is None or not all(v.contains(0) for v in endpoint.values())):raise RuntimeError('Inherited root upper-wall enclosure consistency failed')
    # Exact rational implication from the independently proved coarse gates.
    lam=Fraction(55,1024);x=Fraction(1024,165000);delta=Fraction(39,4)*x*(Fraction(21,5)+Fraction(9,2)*x)
    if not delta<Fraction(1,2):raise RuntimeError('Exact rational coarse certificate implication failed')
    status='PASS_ALL_RADIAL_ALL_REAL_K_ZERO_ANCHOR_CANONICAL_PP' if complete and all(gs.values()) else ('INCONCLUSIVE_COARSE_GATE' if complete else 'CHECKPOINTED_PARTIAL')
    d={'utc':now().isoformat(),'status':status,'complete':complete,'fingerprint':state['fingerprint'],'completed_unique_cells':state['completed_cells'],'total_unique_cells':state['total_cells'],'bits':BITS,'step':str(STEP),'order':5,'gates':gs,'uniform_coarse_lambda':str(lam),'strict_Delta_upper_rational':str(delta),'certified_K_at_least_half_S':complete and all(gs.values()),'all_radial_modes':complete and all(gs.values()),'all_real_spatial_frequencies_including_actual_mean':complete and all(gs.values()),'whole_collar_state_bounds':{n:v.rational_bounds() for n,v in zip(NAMES,ran)},'whole_collar_coefficient_bounds':{n:v.rational_bounds() for n,v in cc.items()},'k_bounds':p['k'].rational_bounds(),'D_event_state_bounds':{n:v.rational_bounds() for n,v in zip(NAMES,event)} if event is not None else None,'upper_wall_residual_rectangle_enclosures':{n:v.rational_bounds() for n,v in endpoint.items()},'exact_upper_laws':'Inherited actual root subset only; not every A,D rectangle point','background_root_existence':'Inherited exact central A root in the full frozen A,D boxes; NOT re-solved','background_uncertainty_treatment':'Entire launch A interval and entire D-event interval plus whole-cell Taylor remainder and outward rounding','new_background_root_solve':False,'physical_compatible_trajectory_or_stiffness_stability_claim':False,'finite_charge_numerical_test':False,'maximum_picard_iterations':state['max_picard_iterations'],'scientific_acceptance':'SEPARATE_INDEPENDENT_POSTRUN_AUDIT_REQUIRED'}
    atomic(out/'RESULTS.json',d);return d

def run(out,max_chunks):
    out.mkdir(parents=True,exist_ok=True);STAGE.update(stage='input_guard');fp,g=guard();model=json.loads((ROOT/'inputs/14_21_14_04_MODEL.json').read_text());y,p=initial(model);Dlo,Dhi=map(Fraction,model['D'])
    if not (out/'LATEST.json').exists():
        STAGE.update(stage='synthetic_controls');control=controls();atomic(out/'CONTROLS.json',control)
        total=(Dhi.numerator*STEP.denominator+Dhi.denominator*STEP.numerator-1)//(Dhi.denominator*STEP.numerator)
        state={'fingerprint':fp,'guard':g,'s':'0','D_lo':str(Dlo),'D_hi':str(Dhi),'total_cells':total,'completed_cells':0,'state':vector_dump(y),'whole_collar':vector_dump(y),'D_event':None,'max_picard_iterations':0,'completed_chunks':[],'control_sha256':sha(out/'CONTROLS.json')};atomic(out/'LATEST.json',state)
    STAGE.update(stage='checkpoint_integrity');state=json.loads((out/'LATEST.json').read_text())
    if state['fingerprint']!=fp:raise RuntimeError('Changed interval protocol/runtime fingerprint')
    if sha(out/'CONTROLS.json')!=state['control_sha256']:raise RuntimeError('Changed synthetic controls')
    for row in state['completed_chunks']:
        if sha(out/row['path'])!=row['sha256']:raise RuntimeError('Changed committed interval chunk')
    y=vector_load(state['state']);ran=vector_load(state['whole_collar']);event=vector_load(state['D_event']) if state['D_event'] else None;s=Fraction(state['s']);executed=0
    while s<Dhi and executed<max_chunks:
        rows=[];chunk_start=state['completed_cells'];t0=time.monotonic()
        for _ in range(CHUNK):
            if s>=Dhi:break
            if now()>=DEADLINE:raise TimeoutError('Fixed absolute block maximum')
            index=state['completed_cells'];STAGE.update(stage='validated_cell',index=index,s=str(s));h=min(STEP,Dhi-s)
            yn,whole,box,j,point,rem=step(y,h,p)
            # The exact invariant is a consistency control; the enclosure proof is Picard/Taylor.
            if not readout(whole,p)['first_integral'].contains(0):raise RuntimeError('First-integral enclosure excludes inherited exact invariant')
            if whole[4].lo<=0:raise RuntimeError('Reciprocal warp enclosure lost positivity')
            coeff_hash=hashlib.sha256(encode({'point':[[v.dump() for v in c] for c in point],'remainder':vector_dump(rem)})).hexdigest()
            row={'index':index,'s':str(s),'h':str(h),'picard_box':vector_dump(box),'picard_iterations':j,'whole_cell':vector_dump(whole),'endpoint':vector_dump(yn),'taylor_coefficients_sha256':coeff_hash}
            if s+h>=Dlo and s<=Dhi:
                ev=evaluate(point,rem,max(Fraction(0),Dlo-s),min(h,Dhi-s));event=ev if event is None else hull(event,ev);row['D_event_overlap']=vector_dump(ev)
            rows.append(row);ran=hull(ran,whole);y=yn;s+=h;state['completed_cells']+=1;state['max_picard_iterations']=max(state['max_picard_iterations'],j)
        name=f'cells/chunk_{chunk_start:05d}_{state["completed_cells"]:05d}.json.gz';dest=out/name;dest.parent.mkdir(exist_ok=True);tmp=dest.with_name(dest.name+'.tmp')
        with tmp.open('wb') as f:f.write(gzip.compress(encode(rows),mtime=0));f.flush();os.fsync(f.fileno())
        os.replace(tmp,dest)
        state.update(s=str(s),state=vector_dump(y),whole_collar=vector_dump(ran),D_event=vector_dump(event) if event is not None else None)
        state['completed_chunks'].append({'path':name,'sha256':sha(dest),'start':chunk_start,'end':state['completed_cells']});atomic(out/'LATEST.json',state);executed+=1
        atomic(out/'PROGRESS.json',{'utc':now().isoformat(),'status':'RUNNING','completed_cells':state['completed_cells'],'total_cells':state['total_cells'],'last_durable_chunk':name,'fingerprint':fp,'last_chunk_seconds':time.monotonic()-t0,'scientific_classification':'SEPARATE_FROM_PROGRESS'})
        print(json.dumps({'cells':state['completed_cells'],'total':state['total_cells'],'s':str(s),'chunk_seconds':time.monotonic()-t0}),flush=True)
    STAGE.update(stage='terminal_certificate');r=result(out,state,p);atomic(out/'PROGRESS.json',{'utc':now().isoformat(),'status':'STOPPED','completed_cells':state['completed_cells'],'total_cells':state['total_cells'],'fingerprint':fp,'scientific_classification':r['status']});return r

def timeout(signum,frame):raise TimeoutError('Absolute interval certificate deadline during '+STAGE['stage'])
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--max-chunks',type=int,default=10000);args=ap.parse_args();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
    try:
        remain=(DEADLINE-now()).total_seconds()
        if remain<=0:raise TimeoutError('Past fixed deadline; refusing science')
        signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,remain);r=run(out,args.max_chunks);print(json.dumps({k:v for k,v in r.items() if k not in ['whole_collar_state_bounds','whole_collar_coefficient_bounds','D_event_state_bounds','upper_wall_residual_rectangle_enclosures']},indent=2))
    except BaseException as exc:
        atomic(out/'FAILURE.json',{'utc':now().isoformat(),'stage':dict(STAGE),'type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),'scientific_classification':'FAILURE_NOT_A_SIGN_RESULT'});raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)
