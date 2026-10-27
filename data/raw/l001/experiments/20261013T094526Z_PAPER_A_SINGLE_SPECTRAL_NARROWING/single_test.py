"""One frozen dual-engine bisection test; no retries or modified producer code."""
import fcntl, hashlib, importlib.util, json, os, platform, signal, sys, time, traceback
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
class StopTest(Exception): pass
def need(ok,label):
    if not ok: raise StopTest(label)
def now(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def put(path,obj):
    need(not path.exists(),'REFUSE_OVERWRITE:'+str(path))
    temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('x') as f: json.dump(obj,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temp,path)
def interval(r):
    z=tuple(map(Q,r['exact_bounds'])) if 'exact_bounds' in r else (Q(r['lo_exact']),Q(r['hi_exact']))
    need(z[0]<=z[1],'INTERVAL_ORDER'); return z
def p(x): return (Q(x),Q(x))
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def mul(a,b):
    z=[x*y for x in a for y in b]; return min(z),max(z)
def scale(a,b): return mul(a,p(b))
def sq(a): return (Q(0) if a[0]<=0<=a[1] else min(x*x for x in a),max(x*x for x in a))
def div(a,b):
    need(not b[0]<=0<=b[1],'DENOMINATOR_NONZERO'); return mul(a,(1/b[1],1/b[0]))
def meet(a,b):
    z=max(a[0],b[0]),min(a[1],b[1]); need(z[0]<=z[1],'DUAL_OVERLAP'); return z
def sign(a): return 1 if a[0]>0 else -1 if a[1]<0 else 0
def record(a): return {'exact_bounds':list(map(str,a)),'approximate':list(map(float,a))}
def event_cover(rows,D):
    need(bool(rows),'EMPTY_EVENT_COVER'); last=D[0]
    for r in rows:
        lo,hi=Q(r['lo_exact']),Q(r['hi_exact']); need(lo==last and lo<=hi,'EVENT_GAP'); last=hi
    need(last==D[1],'EVENT_END')
def semantic_controls():
    need(sign((Q(-1),Q(0)))==0 and sign((Q(0),Q(1)))==0 and sign((Q(-1),Q(2)))==0,'ZERO_SIGN_CONTROL')
    controls=[{'control':'zero-touching and zero-straddling signs','pass':True}]
    for name,fn in [('DENOMINATOR_NONZERO',lambda:div(p(1),(Q(-1),Q(1)))),('EVENT_GAP',lambda:event_cover([{'lo_exact':'1','hi_exact':'2'}],(Q(0),Q(2))))]:
        try: fn()
        except StopTest as e: need(str(e)==name,'CONTROL_WRONG_REJECTION'); controls.append({'control':name,'rejected_by':str(e)})
        else: raise StopTest('CONTROL_ACCEPTED')
    return controls
def coefficients(mu,spec):
    saved=read(ROOT/'inputs/stiffness_result.json')['result']; beta=interval(saved['background']['bb']); per={}
    for engine in ('primary','independent'):
        old=saved['engines'][engine]; strip=read(ROOT/('inputs/'+engine+'_strip.json'))
        k=interval(strip['K']); shifted=add(mu,scale(k,4)); need(shifted[1]<0,'SHIFTED_SECTOR')
        B=interval(old['B0']); Z=interval(old['Z']); psi=interval(old['psi_b'])
        Ca=div(sq(div(scale(shifted,3),B)),Z); Cb=div(sq(div(scale(mul(shifted,psi),3),beta)),Z)
        per[engine]={'lambda':record(shifted),'Ca':record(Ca),'Cb':record(Cb)}
    both={k:meet(interval(per['primary'][k]),interval(per['independent'][k])) for k in ('Ca','Cb')}
    width={k:str(v[1]/v[0]) for k,v in both.items()}; need(all(v[0]>0 for v in both.values()),'COEFFICIENT_POSITIVITY')
    return {'engines':per,'combined':{k:record(v) for k,v in both.items()},'width_ratios_exact':width,
            'both_width_ratios_pass':all(Q(v)<=Q(spec['max_coeff_width_ratio']) for v in width.values()),
            'unchanged_Cb_over_Ca':saved['combined']['Cb_over_Ca']}
def authenticate():
    gate=read(ROOT/'INDEPENDENT_GATE.json'); need(gate['decision']=='APPROVED_FOR_ONE_BOUNDED_EXECUTION','GATE_NOT_APPROVED')
    for name,digest in gate['frozen_hashes'].items(): need(sha(ROOT/name)==digest,'GATE_HASH:'+name)
    for name,item in read(ROOT/'SOURCE_BINDINGS.json')['files'].items(): need(sha(ROOT/name)==item['sha256'],'SOURCE_HASH:'+name)
    runtime=read(ROOT/'RUNTIME_BINDINGS.json')
    need(str(Path(sys.executable).resolve())==runtime['executable_realpath'],'RUNTIME_EXECUTABLE')
    need(platform.python_version()==runtime['python_version'],'RUNTIME_PYTHON')
    sys.path.insert(0,runtime['flint_path'])
    import flint
    need(flint.__version__==runtime['flint_version'],'RUNTIME_FLINT')
    for path,digest in runtime['files'].items(): need(sha(path)==digest,'RUNTIME_LIBRARY:'+path)
    need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'BLAS_ENVIRONMENT')
    return flint
def load_engine(name):
    spec=importlib.util.spec_from_file_location('frozen_'+name,ROOT/('engine/'+name+'_interval.py'))
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
def flow(engine,mu,binding,spec,out,attempt,started):
    from flint import arb,fmpq
    mod=load_engine(engine); begun=time.monotonic(); cfg=binding['config']; D=tuple(map(Q,cfg['D']))
    h=fmpq(2,spec['steps'][engine]); Dlo,Dhi=map(fmpq,cfg['D']); A=mod.interval(*map(fmpq,cfg['A']))
    y,par=mod.initial(A,arb(fmpq(str(mu))),binding['model_exact'])
    need(par['k'].lower()>0 and (arb(fmpq(str(mu)))+4*par['k']).upper()<0,'FLOW_SECTOR')
    n=(D[1]*spec['steps'][engine]/2).__ceil__(); rows=[]; event=None; maxpicard=0
    def pack(x):
        lo,hi=mod.bounds(x); return {'exact_bounds':[str(lo),str(hi)]}
    for j in range(n):
        if j%64==0:
            deadline=datetime.fromisoformat(read(ROOT/'TIME_BOUNDARY.json')['deadline_utc'].replace('Z','+00:00')).timestamp()-spec['deadline_reserve_seconds']
            need(time.time()<deadline,'ABSOLUTE_PRODUCTION_DEADLINE')
            need(time.monotonic()-begun<spec['flow_seconds_max'],'FLOW_TIME_BUDGET')
            need(time.monotonic()-started<spec['production_seconds_max'],'TOTAL_TIME_BUDGET')
        s=j*h; y,cell=mod.step(y,h,par); geo=mod.geometry(cell,par)
        need(all(v.is_finite() for v in y+list(geo.values())),'NONFINITE_FLOW')
        need(geo['constraint'].lower()<=0<=geo['constraint'].upper(),'CONSTRAINT_ESCAPE')
        need(geo['first_integral'].lower()<=0<=geo['first_integral'].upper(),'FIRST_INTEGRAL_ESCAPE')
        need(geo['warp_squared'].lower()>0,'WARP_POSITIVITY')
        maxpicard=max(maxpicard,cell['picard_iterations'])
        if s+h>=Dlo and s<=Dhi:
            a=max(fmpq(0),Dlo-s); b=min(h,Dhi-s)
            F=mod.determinant(mod.range_on_cell(cell,a,b),par)
            need(F.is_finite(),'NONFINITE_DETERMINANT'); event=F if event is None else mod.hull(event,F)
            rows.append({'index':j,'lo_exact':str(s+a),'hi_exact':str(s+b),'determinant':pack(F)})
    event_cover(rows,D); r={'attempt':attempt,'engine':engine,'mu_exact':str(mu),'determinant':pack(event),'event_cover':rows,'cells':n,
      'steps':spec['steps'][engine],'all_cell_finite_constraint_first_integral_warp_checks_pass':True,'max_picard_iterations':maxpicard,
      'elapsed_seconds':time.monotonic()-begun,'finished_utc':now(),'source_sha256':sha(ROOT/('engine/'+engine+'_interval.py'))}
    put(out/(f'attempt_{attempt:02d}_{engine}.json'),r); return r
def main():
    out=ROOT/'output'; out.mkdir(exist_ok=True)
    need(not any((out/n).exists() for n in ('RESULT.json','FAILURE.json','STARTED.json')),'TERMINAL_OR_PRIOR_ATTEMPT_PRESENT')
    lock=(out/'RUN.lock').open('a+'); fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    spec=read(ROOT/'TEST_SPEC.json'); started=time.monotonic(); history=[]; bracket=tuple(map(Q,spec['initial_mu']))
    try:
        flint=authenticate(); flint.ctx.prec=spec['bits']; flint.ctx.threads=1
        deadline=datetime.fromisoformat(read(ROOT/'TIME_BOUNDARY.json')['deadline_utc'].replace('Z','+00:00')).timestamp()-spec['deadline_reserve_seconds']
        need(time.time()<deadline,'ABSOLUTE_PRODUCTION_DEADLINE')
        put(out/'STARTED.json',{'utc':now(),'pid':os.getpid(),'runtime':read(ROOT/'RUNTIME_BINDINGS.json'),'gate_sha256':sha(ROOT/'INDEPENDENT_GATE.json')})
        binding=read(ROOT/'inputs/central_bindings.json'); need(binding['config']['mu']==spec['initial_mu'],'INITIAL_BRACKET_BINDING')
        need(read(ROOT/'inputs/uniqueness_review.json')['status']=='ACCEPTED_UNIQUE_REAL_EIGENVALUE_IN_DECLARED_CENTRAL_MASS_STRIP','UNIQUENESS_PREMISE')
        controls=semantic_controls(); endpoints={}
        for engine in ('primary','independent'):
            need(load_engine(engine).algebra_controls()['pass'],'ENGINE_ALGEBRA_CONTROL')
            for side,expected in [('low',1),('high',-1)]:
                r=read(ROOT/('inputs/'+engine+'_'+side+'.json')); need(sign(interval(r['determinant']))==expected,'INITIAL_OPPOSITE_SIGN')
                endpoints[engine+'_'+side]=r['determinant']
        reason='ATTEMPT_BUDGET'
        for attempt in range(1,spec['max_attempts']+1):
            if bracket[1]-bracket[0]<=Q(spec['target_width']): reason='TARGET_REACHED'; break
            mid=sum(bracket)/2; entry={'attempt':attempt,'before':list(map(str,bracket)),'midpoint_exact':str(mid),'engine_results':{}}
            history.append(entry); signs=[]
            for engine in ('primary','independent'):
                r=flow(engine,mid,binding,spec,out,attempt,started); sig=sign(interval(r['determinant'])); signs.append(sig)
                entry['engine_results'][engine]={'record':f'attempt_{attempt:02d}_{engine}.json','sha256':sha(out/f'attempt_{attempt:02d}_{engine}.json'),'sign':sig}
                if sig==0: reason='ZERO_CONTAINING_MIDPOINT'; break
            if 0 in signs: entry['admitted']=False; break
            if signs[0]!=signs[1]: entry['admitted']=False; reason='ENGINE_SIGN_DISAGREEMENT'; break
            bracket=(mid,bracket[1]) if signs[0]>0 else (bracket[0],mid)
            entry.update(admitted=True,after=list(map(str,bracket)))
        target=bracket[1]-bracket[0]<=Q(spec['target_width'])
        if target: reason='TARGET_REACHED'
        coeff=coefficients(bracket,spec)
        outcome=('SHARPENED' if coeff['both_width_ratios_pass'] else 'NARROW_TARGET_COEFFICIENTS_WIDE') if target else 'RETAINED_WIDE'
        result={'status':'COMPLETE_PENDING_TERMINAL_REVIEW','outcome':outcome,'stop_reason':reason,'mu_bracket':list(map(str,bracket)),
          'mu_width_exact':str(bracket[1]-bracket[0]),'target_pass':target,'attempts':history,'coefficients':coeff,'controls':controls,
          'initial_endpoint_sign_records':endpoints,'finished_utc':now(),'elapsed_seconds':time.monotonic()-started,
          'claim_boundary':'One unique in-strip central mode, unchanged exact background/action; local stiffness coefficients only, no finite stabilizing threshold.'}
        put(out/'RESULT.json',result); print(json.dumps(result,indent=2))
    except BaseException as e:
        put(out/'FAILURE.json',{'status':'TECHNICAL_INCOMPLETE','utc':now(),'error':repr(e),'traceback':traceback.format_exc(),'last_admitted_bracket':list(map(str,bracket)),'attempts':history,'elapsed_seconds':time.monotonic()-started})
        raise
    finally: fcntl.flock(lock.fileno(),fcntl.LOCK_UN); lock.close()
if __name__=='__main__': main()
