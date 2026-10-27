"""One prospectively bounded coupled C4 Jacobian certificate; never evolves time."""
import argparse,fcntl,importlib,json,math,os,platform,resource,signal,subprocess,sys,time,traceback
from pathlib import Path
from fractions import Fraction
import flint
from flint import arb,ctx,fmpq
import primary,flux,validated,jetmap,majorants
from series import bounds,interval,hull,record,det3,inverse3
from records import now,sha,pack,unpack,fingerprint,read,atomic,save,load

ROOT=Path(__file__).resolve().parent
ENV={'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTHONNOUSERSITE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
CONFIG={'bits':768,'threads':1,'primary_denominator':8192,'flux_denominator':16384,'checkpoint_cells':256,
        'engine_seconds_cap':900,'address_space_bytes':4*1024**3,'task_order':['primary','flux'],
        'root':['456607025194779413/4611686018427387904','114151756532473697/1152921504606846976'],
        'D':['32727/16384','32729/16384'],'mu':['-33/25000','-131/100000'],
        'r0_power_of_two':-4096,'amplitude_radius_power_of_two':-9216,'inverse_norm_max_power_of_two':64,
        'scope':'EXACT_CENTRAL_D1_FINAL_THREE_VARIABLE_C4_PREPARATION'}
SOURCES=['CONTRACT.md','ANALYTIC_RADIUS.md','series.py','primary.py','flux.py','validated.py','jetmap.py','majorants.py','records.py','runner.py']
REVIEWS=['INDEPENDENT_C4_DERIVATION.md','independent_boundary_algebra.py','INDEPENDENT_BOUNDARY_ALGEBRA.json','PREFLIGHT_REVIEW.md']
INITIAL_DATA='../../01-horizon-core/d1-native-cauchy-20261005T201829Z'
CENTRAL='../lin-central-validated-mode-r1-20261005T172800Z'
TECHNICAL_PREDECESSOR='../lin-c4-local-certificate-20261005T214000Z'
INPUT_NAMES=['BINDINGS.json','MANIFEST.json','LOCAL_EXISTENCE_ARGUMENT.md','NEXT_CALCULATION.md','CAUCHY_DATA_SPEC.md',
             'RESULT_REPORT.md','DERIVATION.md','HIGHER_TIME_DERIVATION.md','HIGHER_COMPATIBILITY_CONTRACT.md',
             'code/core.py','code/higher_run.py','code/time_jets.py','HIGHER_CONSTRUCTION_FROZEN.json',
             'results/REGULARITY_CERTIFICATE.json','results/fine_c4/RESULT.json','results/coarse_c4/RESULT.json']


def exact(x):
    q=Fraction(x);return fmpq(q.numerator,q.denominator)
def zero(x):return x.lower()<=0<=x.upper()
def maxabs(x):
    lo,hi=bounds(x);return max(abs(lo),abs(hi))
def source():return {n:sha(ROOT/n) for n in SOURCES}
def runtime():
    p=Path(flint.__file__).resolve().parent
    files=list(p.rglob('*.so'))+list(p.parent.glob('python_flint.libs/*'))
    return {'executable':str(Path(sys.executable).resolve()),'executable_sha256':sha(Path(sys.executable).resolve()),
            'python':platform.python_version(),'flint':flint.__version__,'libraries':{str(x):sha(x) for x in sorted(files) if x.is_file()},
            'precision':int(ctx.prec),'threads':int(ctx.threads),'env':{k:os.environ.get(k) for k in ENV}}
def initial(model):
    p={k:arb(exact(v)) for k,v in model.items()};a=interval(*map(exact,CONFIG['root']))
    d=a-p['v0'];H=-(p['lambda_a']+p['gamma']*d*d/2)/6;T=p['gamma']*d/2
    p['k']=H*H-1-T*T/12+p['m2']*a*a/12;p['D']=interval(*map(exact,CONFIG['D']))
    p['B_lower']=p['gamma']*T/2-(p['m2']*a-4*H*T)
    return H,a,T,p


def authenticate():
    b=read(ROOT/'BINDINGS.json');f=read(ROOT/'FREEZE_RECORD.json');guard=sha(ROOT/'BINDINGS.json')
    assert f['binding_sha256']==guard and b['config']==CONFIG and b['source']==source()
    assert b['runtime']==runtime()
    for n,h in b['reviews'].items():assert sha(ROOT/n)==h,n
    for entry in b['inputs'].values():assert sha(ROOT/entry['path'])==entry['sha256'],entry['path']
    return b,guard


def preflight(output):
    output.mkdir(parents=True,exist_ok=False);checks={}
    for name,engine in [('primary',primary),('flux',flux)]:
        p={'k':arb(0),'m2':arb(exact('41/100')),'D':arb(2)}
        y=engine.initial(arb(-1),arb(0),arb(0));h=fmpq(1,4096)
        for _ in range(8):y,cell=validated.step(y,h,p,engine)
        f=engine.fields(y,p);columns=engine.columns(y)
        checks[name+'_vacuum']=zero(f['W']+8*h) and zero(f['H']+1) and all(zero(v) for u,v in columns)
        checks[name+'_vacuum'] &= zero(columns[0][0]-1) and all(zero(u) for u,v in columns[1:])
        state={'task_index':0,'cell_index':8,'elapsed_seconds':0.,'y':y,'p':p,'engine':name,'h':h}
        folder=output/name;save(folder,state,'analytic-control')
        restored=load(folder,'analytic-control');checks[name+'_native_restore']=fingerprint(restored)==fingerprint(state)
        one,_=validated.step(state['y'],h,state['p'],engine)
        child=subprocess.check_output([sys.executable,'-B',str(ROOT/'runner.py'),'child',str(folder)],text=True)
        checks[name+'_fresh_process_next_step']=json.loads(child)['digest']==fingerprint(one)
        try:load(folder,'changed-guard')
        except AssertionError:checks[name+'_changed_guard_rejected']=True
        else:checks[name+'_changed_guard_rejected']=False
        atomic(folder/'uncommitted-partial.json',{'not':'a checkpoint'})
        checks[name+'_partial_ignored']=fingerprint(load(folder,'analytic-control'))==fingerprint(state)
    class PolynomialForcing:
        @staticmethod
        def rhs(y,p):
            s,u,v=y
            return [arb(1),v,s*s*s*s]
        @staticmethod
        def coeff(y,N,p):
            from series import linear_power
            c=[[v] for v in y];s,u,v=c;forcing=linear_power(s[0],1,4,N-1)
            for n in range(N):
                out=[arb(int(n==0)),v[n],forcing[n]]
                for row,z in zip(c,out):row.append(z/(n+1))
            return c
    y=[arb(0),arb(0),arb(0)];h=fmpq(1,4096);poly_iterations=[]
    for _ in range(8):
        y,cell=validated.step(y,h,{},PolynomialForcing);poly_iterations.append(cell['picard_iterations'])
    t=8*h
    checks['polynomial_forcing_exact_solution']=(zero(y[0]-t) and zero(y[1]-t**6/30) and zero(y[2]-t**5/5))
    symbolic=read(ROOT/'INDEPENDENT_BOUNDARY_ALGEBRA.json')
    checks['independent_exact_boundary_algebra']=(symbolic['status']=='PASS'
        and all(symbolic['checks'].values())
        and symbolic['source_sha256']==sha(ROOT/'independent_boundary_algebra.py'))
    # Synthetic exact flat vacuum has q=T=Phi=0. R4 is just the own fifth jet.
    bg=[arb(0),arb(-1),arb(0),arb(0),arb(0)]
    for fifth in (0,1):
        row=jetmap.rows(bg,arb(1),arb(0),arb(fifth),arb(0),arb(exact('41/100')),arb(10))
        checks['dual_vacuum_'+str(fifth)]=zero(row['R4']-fifth) and zero(row['I4'])
    major=majorants.certify();checks['complex_majorants']=major['pass']
    result={'pass':all(checks.values()),'checks':checks,'source':source(),'runtime':runtime(),
            'majorants':major,'polynomial_fixture_iterations':poly_iterations,'physical_model_evaluated':False,'utc':now()}
    atomic(output/'RESULT.json',result,True);print(json.dumps(result,indent=2))
    if not result['pass']:raise RuntimeError('Preflight controls failed')


def freeze(preflight):
    c=read(preflight/'RESULT.json');assert c['pass'] and c['source']==source() and c['runtime']==runtime()
    parent=ROOT/INITIAL_DATA;old=read(parent/'BINDINGS.json')
    assert old['a_enclosure']==CONFIG['root'] and old['D_enclosure']==CONFIG['D'] and old['mu_enclosure']==CONFIG['mu']
    central=read(ROOT/CENTRAL/'BINDINGS.json');assert old['model_exact']==central['model_exact']
    mode=read(ROOT/CENTRAL/'RESULT.json')
    assert mode['status']=='COMPLETE' and mode['independently_accepted'] is True
    assert mode['classification']=='NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1'
    assert mode['mu_open_interval']==CONFIG['mu']
    counts={}
    for directory in (parent,ROOT/CENTRAL):
        manifest=read(directory/'MANIFEST.json')
        entries=manifest.get('entries') or [{'path':n,**v} for n,v in manifest['files'].items()]
        for e in entries:assert sha(directory/e['path'])==e['sha256'],e['path']
        counts[directory.name]=len(entries)
    assert sha(parent/'MANIFEST.json')=='549c998dcb4b61576bb427e73ce793723a88682f44c1f1575ce07b1435b34cf9'
    inputs={n:{'path':INITIAL_DATA+'/'+n,'sha256':sha(parent/n)} for n in INPUT_NAMES}
    inputs['central_manifest']={'path':CENTRAL+'/MANIFEST.json','sha256':sha(ROOT/CENTRAL/'MANIFEST.json')}
    inputs['central_binding']={'path':CENTRAL+'/BINDINGS.json','sha256':sha(ROOT/CENTRAL/'BINDINGS.json')}
    inputs['central_mode_certificate']={'path':CENTRAL+'/RESULT.json','sha256':sha(ROOT/CENTRAL/'RESULT.json')}
    for n in ('BINDINGS.json','output/FAILURE.json'):
        inputs['technical_predecessor_'+n]={'path':TECHNICAL_PREDECESSOR+'/'+n,'sha256':sha(ROOT/TECHNICAL_PREDECESSOR/n)}
    rel=str(preflight.relative_to(ROOT))+'/RESULT.json';inputs['preflight']={'path':rel,'sha256':sha(ROOT/rel)}
    b={'utc':now(),'config':CONFIG,'source':source(),'reviews':{n:sha(ROOT/n) for n in REVIEWS},
       'inputs':inputs,'model_exact':old['model_exact'],'runtime':runtime(),'parent_manifest_counts':counts,
       'physical_outcomes_evaluated_before_freeze':False}
    atomic(ROOT/'BINDINGS.json',b,True);atomic(ROOT/'FREEZE_RECORD.json',{'binding_sha256':sha(ROOT/'BINDINGS.json'),'utc':now()},True)
    for n in SOURCES+REVIEWS:(ROOT/n).chmod(0o444)
    print(json.dumps({'frozen':True,'guard':sha(ROOT/'BINDINGS.json'),'parent_counts':counts}))


def endpoint(y,p,engine):
    f=engine.fields(y,p);cols=engine.columns(y);d,c0,c1=[v for u,v in cols]
    B=(-p['gamma']/2+4*f['H'])*f['T']-p['m2']*f['Phi'];beta=8*f['q']*B
    J=[[d,c0,c1],[arb(0),arb(1),arb(0)],[beta*d,beta*c0,1+beta*c1]]
    bg=[f[n] for n in ('W','H','Phi','T','q')]
    direct=[];identities=[]
    for j,(u,v) in enumerate(cols):
        r=jetmap.rows(bg,u,v,arb(int(j==2)),p['k'],p['m2'],-p['gamma']/2)
        identities.extend([zero(r['R4']-J[2][j]),zero(r['I4']),zero(r['R2']+4*B*v)])
        direct.append(r['R4'])
    det=det3(J)
    return {'J':J,'determinant':det,'analytic_determinant':d,'beta':beta,'columns':cols,
            'direct_fourth_rows':direct,'endpoint_identities':all(identities)}


def finish_task(state,p):
    J=state['J'];det=det3(J);d=state['analytic_determinant'];inverse=inverse3(J,det)
    norm=max(sum(maxabs(v) for v in row) for row in inverse)
    ext=state['extrema'];klo,khi=bounds(p['k']);B=p['B_lower']
    model_checks={'gamma_is_20':p['gamma']==20,
        'abs_m2_at_most_1':maxabs(p['m2'])<=1,
        'abs_wall_v_at_most_1':all(maxabs(p[n])<=1 for n in ('v0','v1')),
        'abs_wall_lambda_at_most_8':all(maxabs(p[n])<=8 for n in ('lambda_a','lambda_b')),
        'D_in_1_3':bounds(p['D'])[0]>=1 and bounds(p['D'])[1]<=3,
        'abs_mu_at_most_1_500':all(abs(exact(x))<=fmpq(1,500) for x in CONFIG['mu'])}
    premises=(all(model_checks.values()) and klo>0 and khi<=fmpq(1,1000) and maxabs(ext['W'])<=3
        and all(maxabs(ext[n])<=2 for n in ('H','Phi','T'))
        and bounds(ext['exp_minus_2W'])[1]<=256 and bounds(ext['q'])[1]<=1
        and (bounds(B)[1]<=-fmpq(1,20) or bounds(B)[0]>=fmpq(1,20)))
    cover=state['event_cover'];Dlo,Dhi=map(exact,CONFIG['D'])
    complete_cover=(bool(cover) and exact(cover[0]['lo_exact'])==Dlo
        and exact(cover[-1]['hi_exact'])==Dhi
        and all(exact(a['hi_exact'])==exact(b['lo_exact']) for a,b in zip(cover,cover[1:])))
    success=(bounds(det)[1]<0 and bounds(d)[1]<0 and zero(det-d)
             and state['endpoint_identities'] and complete_cover)
    return {'engine':CONFIG['task_order'][state['task_index']],'status':'COMPLETE',
        'cells':state['cell_index'],'event_cover':state['event_cover'],
        'J':[[record(v) for v in row] for row in J],'determinant':record(det),
        'analytic_determinant':record(d),'beta':record(state['beta']),
        'inverse':[[record(v) for v in row] for row in inverse],'inverse_norm_upper_exact':str(norm),
        'direct_fourth_rows':[record(v) for v in state['direct_fourth_rows']],
        'extrema':{n:record(v) for n,v in ext.items()},'k':record(p['k']),'B_lower':record(B),
        'endpoint_identities':state['endpoint_identities'],'max_picard_iterations':state['max_picard'],
        'full_event_cover_pass':bool(complete_cover),'model_majorant_premises':model_checks,
        'qualitative_gates_pass':bool(success),'radius_background_premises_pass':bool(premises),
        'radius_inverse_gate_pass':bool(norm<=2**64),'elapsed_seconds':state['task_elapsed'],
        'final_native_state':pack(state['y'])}


def run(output):
    b,guard=authenticate()
    if any((output/n).exists() for n in ('RESULT.json','TERMINAL.json','FAILURE.json')):raise RuntimeError('Terminal/failed restart refused')
    output.mkdir(parents=True,exist_ok=True);lock=(output/'RUN.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    resource.setrlimit(resource.RLIMIT_AS,(CONFIG['address_space_bytes'],CONFIG['address_space_bytes']))
    start=time.monotonic();state=load(output,guard) if (output/'LATEST.json').exists() else {
        'task_index':0,'cell_index':0,'results':[],'elapsed_seconds':0.,'started_utc':now()}
    previous_elapsed=state['elapsed_seconds'];Dlo,Dhi=map(exact,CONFIG['D'])
    H,P,T,p=initial(b['model_exact'])
    def alarm(*unused):raise TimeoutError('Frozen engine wall-time cap')
    signal.signal(signal.SIGALRM,alarm)
    try:
        while state['task_index']<2:
            name=CONFIG['task_order'][state['task_index']];engine=importlib.import_module(name)
            h=fmpq(2,CONFIG[name+'_denominator']);task_start=time.monotonic()
            committed=output/(name+'.json')
            if committed.exists():
                result=read(committed);assert result['guard']==guard and result['digest']==fingerprint({k:v for k,v in result.items() if k!='digest'})
                assert result['engine']==name and result['status']=='COMPLETE'
                state['results'].append(result);state['task_index']+=1;state['cell_index']=0
                state['elapsed_seconds']=previous_elapsed+time.monotonic()-start;save(output,state,guard);continue
            if state['cell_index']==0:
                state.update(y=engine.initial(H,P,T),p=p,task_elapsed=0.,extrema={},event_cover=[],J=None,
                             beta=None,analytic_determinant=None,direct_fourth_rows=None,endpoint_identities=True,max_picard=0)
                # Own/opposite fifth-jet and lower initial slope are imposed as exact identities.
                lower=[arb(0),H,P,T,p['k']]
                for j in range(3):
                    z=jetmap.rows(lower,arb(int(j==0)),arb(0),arb(int(j==1)),p['k'],p['m2'],p['gamma']/2)
                    assert zero(z['R4']-int(j==1)) and zero(z['I4'])
            old_task_time=state['task_elapsed'];signal.alarm(max(1,int(math.ceil(CONFIG['engine_seconds_cap']-old_task_time))))
            cells=int(math.ceil(Dhi/h))
            while state['cell_index']<cells:
                j=state['cell_index'];s=j*h
                ynext,cell=validated.step(state['y'],h,state['p'],engine);f=engine.fields(cell['box'],state['p'])
                assert all(v.is_finite() for v in ynext+list(f.values())) and zero(f['first_integral'])
                for n,v in f.items():state['extrema'][n]=hull(state['extrema'][n],v) if n in state['extrema'] else v
                if s+h>=Dlo and s<=Dhi:
                    lo=max(fmpq(0),Dlo-s);hi=min(h,Dhi-s);z=validated.range_on_cell(cell,lo,hi);e=endpoint(z,state['p'],engine)
                    state['event_cover'].append({'cell':j,'lo_exact':str(s+lo),'hi_exact':str(s+hi)})
                    for n in ('beta','analytic_determinant'):
                        state[n]=hull(state[n],e[n]) if state[n] is not None else e[n]
                    state['J']=[[hull(a,b) for a,b in zip(x,y)] for x,y in zip(state['J'],e['J'])] if state['J'] is not None else e['J']
                    state['direct_fourth_rows']=[hull(a,b) for a,b in zip(state['direct_fourth_rows'],e['direct_fourth_rows'])] if state['direct_fourth_rows'] is not None else e['direct_fourth_rows']
                    state['endpoint_identities'] &= e['endpoint_identities']
                state['y']=ynext;state['cell_index']=j+1;state['max_picard']=max(state['max_picard'],cell['picard_iterations'])
                state['task_elapsed']=old_task_time+time.monotonic()-task_start
                if state['cell_index']%CONFIG['checkpoint_cells']==0:
                    state['elapsed_seconds']=previous_elapsed+time.monotonic()-start;save(output,state,guard)
            signal.alarm(0);result=finish_task(state,state['p']);result['guard']=guard;result['digest']=fingerprint(result)
            atomic(committed,result,True);state['results'].append(result);state['task_index']+=1;state['cell_index']=0
            state['elapsed_seconds']=previous_elapsed+time.monotonic()-start;save(output,state,guard)
            print(json.dumps({'engine':name,'passed':result['qualitative_gates_pass'],'determinant':result['determinant']['decimal'],
                              'seconds':result['elapsed_seconds']}),flush=True)
        authenticate();tasks=state['results'];overlaps=[]
        for i in range(3):
            for j in range(3):
                x,y=tasks[0]['J'][i][j]['exact'],tasks[1]['J'][i][j]['exact']
                overlaps.append(max(exact(x[0]),exact(y[0]))<=min(exact(x[1]),exact(y[1])))
        parent=read(ROOT/INITIAL_DATA/'results/REGULARITY_CERTIFICATE.json')
        regularity=[]
        for task,old in zip(tasks,parent['results']):
            x,y=task['analytic_determinant']['exact'],old['v_at_full_event']['exact']
            regularity.append(max(exact(x[0]),exact(y[0]))<=min(exact(x[1]),exact(y[1])))
        qualitative=all(t['qualitative_gates_pass'] for t in tasks) and all(overlaps+regularity)
        major=majorants.certify()
        quantitative=qualitative and major['pass'] and all(t['radius_background_premises_pass'] and t['radius_inverse_gate_pass'] for t in tasks)
        classification=('LOCAL_C4_D1_NATIVE_FAMILY_CERTIFIED_WITH_EXPLICIT_CONSERVATIVE_RADIUS' if quantitative else
            'QUALITATIVE_LOCAL_C4_FAMILY_CERTIFIED_RADIUS_UNRESOLVED' if qualitative else 'C4_CERTIFICATION_UNRESOLVED')
        result={'status':'COMPLETE','classification':classification,'producer_provisional_pending_audit':True,'guard':guard,
            'qualitative_certificate':qualitative,'quantitative_radius_certificate':quantitative,'config':CONFIG,
            'majorants':major,'tasks':tasks,'matrix_implementations_overlap':all(overlaps),'inherited_derivative_overlap':all(regularity),
            'elapsed_seconds':previous_elapsed+time.monotonic()-start,'completed_utc':now(),
            'sample_amplitudes_included':False,'evolution_launched':False,'successor_launched':False}
        atomic(output/'RESULT.json',result,True);atomic(output/'TERMINAL.json',{'status':'COMPLETE','classification':classification,
            'guard':guard,'result_sha256':sha(output/'RESULT.json'),'utc':now()},True)
        atomic(output/'STATUS.json',{'state':'COMPLETE','classification':classification,'guard':guard,'utc':now()})
    except KeyboardInterrupt:
        atomic(output/'STATUS.json',{'state':'STOPPED_RECOVERABLE','guard':guard,'utc':now()});raise
    except BaseException as e:
        signal.alarm(0);atomic(output/'FAILURE.json',{'status':'TECHNICAL_INCOMPLETE','error':repr(e),'traceback':traceback.format_exc(),'guard':guard,'utc':now()},True);raise


def main():
    ctx.prec=768;ctx.threads=1
    assert {k:os.environ.get(k) for k in ENV}==ENV
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['preflight','freeze','run','child']);a.add_argument('path',type=Path);args=a.parse_args()
    if args.mode=='preflight':preflight(args.path)
    elif args.mode=='freeze':freeze(args.path)
    elif args.mode=='run':run(args.path)
    else:
        s=load(args.path,'analytic-control');engine=importlib.import_module(s['engine']);y,_=validated.step(s['y'],s['h'],s['p'],engine)
        print(json.dumps({'digest':fingerprint(y)}))


if __name__=='__main__':main()
