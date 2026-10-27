"""One finite-amplitude certificate graph. No time evolution or amplitude search."""
import argparse,fcntl,json,math,os,platform,resource,signal,subprocess,sys,time,traceback
from pathlib import Path
from fractions import Fraction
import flint
from flint import arb,ctx,fmpq
from algebra import Taylor,e1,exp,maxabs,hermite_inverse,stable_e2
from series import bounds,interval,hull,record,power
from records import atomic,read,sha,now,pack,unpack,fingerprint,save,load
import source_flow,nonlinear,preparation,validated

ROOT=Path(__file__).resolve().parent
ENV={'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTHONNOUSERSITE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
CONFIG={'bits':768,'threads':1,'step':'1/8192','epsilon_order':8,'e2_degree':14,'e2_limit':'1/10',
        'checkpoint_cells':256,'source_seconds_cap':900,'zero_seconds_cap':900,'case_seconds_cap':1800,
        'address_space_bytes':4*1024**3,'max_case_workers':2,'radii':['1/100000','1/10','1/10'],
        'preconditioner_diagonal':['-24/23','1','1'],'contraction_ceiling':'1/2','image_fraction':'9/10',
        'epsilon':{'positive':'1/200000','negative':'-1/200000'},
        'root':['456607025194779413/4611686018427387904','114151756532473697/1152921504606846976'],
        'D':['32727/16384','32729/16384'],'mu':['-33/25000','-131/100000']}
SOURCES=['CONTRACT.md','CENTERED_IVP_DERIVATION.md','algebra.py','series.py','records.py','validated.py',
         'source_flow.py','preparation.py','nonlinear.py','runner.py']
REVIEWS=['INDEPENDENT_NONLINEAR_ENDPOINT_DERIVATION.md','INDEPENDENT_NONLINEAR_ENDPOINT.json',
         'independent_nonlinear_endpoint.py','independent_centered_ivp.py','INDEPENDENT_CENTERED_IVP.json',
         'INDEPENDENT_CENTERED_IVP_DERIVATION.md','PREFLIGHT_REVIEW.md']
PARENT='../../01-horizon-core/d1-native-cauchy-20261005T201829Z'
CENTRAL='../lin-central-validated-mode-r1-20261005T172800Z'
LOCAL='../lin-c4-local-certificate-r1-20261005T221400Z'


def exact(x):
    a=Fraction(x);return fmpq(a.numerator,a.denominator)
def zero(x): return bounds(x)[0]<=0<=bounds(x)[1]
def sources():return {n:sha(ROOT/n) for n in SOURCES}
def runtime():
    d=Path(flint.__file__).resolve().parent
    ff=list(d.rglob('*.so'))+list(d.parent.glob('python_flint.libs/*'))
    return {'python':platform.python_version(),'flint':flint.__version__,
        'executable':str(Path(sys.executable).resolve()),'executable_sha256':sha(Path(sys.executable).resolve()),
        'libraries':{str(x):sha(x) for x in sorted(ff) if x.is_file()},
        'bits':int(ctx.prec),'threads':int(ctx.threads),'environment':{n:os.environ.get(n) for n in ENV}}
def auth():
    b=read(ROOT/'BINDINGS.json');guard=sha(ROOT/'BINDINGS.json');f=read(ROOT/'FREEZE_RECORD.json')
    assert f['guard']==guard and b['config']==CONFIG and b['sources']==sources() and b['runtime']==runtime()
    for n,h in b['reviews'].items():assert sha(ROOT/n)==h,n
    for n,h in b['inputs'].items():assert sha(ROOT/n)==h,n
    return b,guard
def initial(model):
    p={k:arb(exact(v)) for k,v in model.items()}
    a=interval(*map(exact,CONFIG['root']));D=interval(*map(exact,CONFIG['D']));mu=interval(*map(exact,CONFIG['mu']))
    H=-(p['lambda_a']+p['gamma']*(a-p['v0'])*(a-p['v0'])/2)/6;T=p['gamma']*(a-p['v0'])/2
    k=H*H-1-T*T/12+p['m2']*a*a/12;B=p['gamma']*T/2-p['m2']*a+4*H*T
    f=3*(mu+4*k)/B;g=p['gamma']*f/2-2*T
    p.update(k=k,D=D,mu=mu)
    return [arb(0),H,a,T,arb(1),arb(1),f,g,arb(0)],p
def centers(which):
    case=3 if which=='positive' else 4
    data=read(ROOT/PARENT/f'results/fine_c4/case_{case}.dense.json')
    eps=exact(CONFIG['epsilon'][which])
    return eps,[exact(data['A0'])-eps]+[exact(x) for x in data['fifth_jet_coefficients']]


class ParameterFixture:
    """Manufactured affine IVP exposes a changing serialized parameter radius."""
    @staticmethod
    def rhs(y,p):return [p['test_parameter']]+[arb(0)]*7+[arb(1)]
    @staticmethod
    def coeff(y,N,p):
        f=ParameterFixture.rhs(y,p)
        return [[v]+([a]+[arb(0)]*(N-1) if N else []) for v,a in zip(y,f)]


def advance(state,h,engine):
    # The only production step entry uses restored state, never a stale p alias.
    return validated.step(state['y'],h,state['p'],engine)


def preflight(out):
    out.mkdir(parents=True,exist_ok=False);checks={}
    # Exact Hermite reconstruction for each of its eight columns.
    M=hermite_inverse()
    checks['hermite_inverse_exact']=all(sum(M[j][k]*math.prod(range(j-d+1,j+1))*fmpq(s)**(j-d) for j in range(d,8))==int(4*s+d==k) for s in (0,1) for d in range(4) for k in range(8))
    for val in ('0','1/1000','-1/1000'):
        x=arb(exact(val));r=stable_e2(x)
        checks['E2_'+val]=zero(r-(x.exp()-1-x))
    e=Taylor([arb(exact('1/1000')),1,0,0,0,0]);z=e.e2();zz=e.exp()-1-e
    checks['E2_series']=all(zero(a-b) for a,b in zip(z.c,zz.c))
    p={k:arb(exact(v)) for k,v in {'gamma':'20','lambda_a':'6','lambda_b':'-6','m2':'41/100','v0':'0','v1':'0','k':'0','D':'2','mu':'0'}.items()}
    y=[arb(0),arb(-1),arb(0),arb(0),arb(1),arb(1),arb(0),arb(0),arb(0)]
    low=preparation.wall_jets(y,p,0)
    high=[arb(-2),arb(-1),arb(0),arb(0),arb(2).exp(),arb(4).exp(),arb(0),arb(0),arb(2)]
    upper=preparation.wall_jets(high,p,1)
    pp=preparation.prepare(fmpq(1,200000),[low,upper],p)
    checks['manufactured_vacuum_preparation']=all(zero(x) for x in pp['c7']+pp['W'])
    p.update(eps=fmpq(0),c7=[arb(0)]*8,x=[arb(fmpq(1,1000)),arb(0),arb(0)])
    y+= [arb(fmpq(1,1000)),arb(0),arb(1),arb(0),arb(0),arb(0),arb(0),arb(0)]
    h=fmpq(1,8192)
    for _ in range(8):y,cell=validated.step(y,h,p,nonlinear)
    checks['nonlinear_vacuum_exact']=zero(y[0]+8*h) and zero(y[4]-arb(8*h).exp()) and zero(y[5]-arb(16*h).exp()) and zero(y[9]-fmpq(1,1000)) and zero(y[10]) and zero(y[11]-1) and all(zero(v) for v in y[12:])
    state={'task_index':0,'cell_index':8,'elapsed_seconds':0.,'y':y,'p':p,'h':h}
    save(out/'recovery',state,'manufactured-control')
    restored=load(out/'recovery','manufactured-control')
    checks['native_restore']=fingerprint(restored)==fingerprint(state)
    one,_=validated.step(state['y'],h,state['p'],nonlinear)
    child=json.loads(subprocess.check_output([sys.executable,'-B',str(ROOT/'runner.py'),'child',str(out/'recovery')],text=True))
    checks['fresh_process_next_step']=child['digest']==fingerprint(one)
    try:load(out/'recovery','wrong-guard')
    except AssertionError:checks['changed_guard_rejected']=True
    else:checks['changed_guard_rejected']=False
    atomic(out/'recovery'/'partial-uncommitted.json',{'partial':True})
    checks['partial_ignored']=fingerprint(load(out/'recovery','manufactured-control'))==fingerprint(state)
    unusual=arb(1,fmpq(1,2))*arb(1,fmpq(1,4))
    pstate={'task_index':0,'cell_index':0,'elapsed_seconds':0.,'h':h,
            'y':[arb(0)]*4+[arb(1)]+[arb(0)]*4,'p':{'test_parameter':unusual}}
    old_p=pstate['p'];old_radius=unusual.rad()
    save(out/'parameter-recovery',pstate,'parameter-control')
    checks['parameter_fixture_radius_really_widens']=pstate['p']['test_parameter'].rad()>old_radius
    checks['parameter_dictionary_replaced']=pstate['p'] is not old_p
    after,_=advance(pstate,h,ParameterFixture)
    child=json.loads(subprocess.check_output([sys.executable,'-B',str(ROOT/'runner.py'),'child-parameter',str(out/'parameter-recovery')],text=True))
    checks['canonical_parameter_fresh_process_continuation']=child['digest']==fingerprint(after)
    symbolic=read(ROOT/'INDEPENDENT_NONLINEAR_ENDPOINT.json')
    checks['nonlinear_endpoint_algebra']=symbolic['status']=='PASS' and all(symbolic['checks'].values()) and symbolic['source_sha256']==sha(ROOT/'independent_nonlinear_endpoint.py')
    result={'pass':all(checks.values()),'checks':checks,'sources':sources(),'runtime':runtime(),'utc':now(),'physical_D1_outcomes_evaluated':False}
    atomic(out/'RESULT.json',result,True);print(json.dumps(result,indent=2))
    assert result['pass']


def freeze(control):
    c=read(control/'RESULT.json');assert c['pass'] and c['sources']==sources() and c['runtime']==runtime()
    pp=read(ROOT/PARENT/'BINDINGS.json');assert pp['a_enclosure']==CONFIG['root'] and pp['D_enclosure']==CONFIG['D'] and pp['mu_enclosure']==CONFIG['mu']
    inputs={};counts={}
    expected={PARENT:'549c998dcb4b61576bb427e73ce793723a88682f44c1f1575ce07b1435b34cf9',CENTRAL:'cbec54af3421ff8251bf7db2119133e262d700a500850322252488c358d9f53d',LOCAL:'35d2f506191bc5f9262e09047522d87bd7adc7a4c370a5ef641c2bc94e9cbaa8'}
    for d,want in expected.items():
        assert sha(ROOT/d/'MANIFEST.json')==want,d
        m=read(ROOT/d/'MANIFEST.json');entries=m.get('entries') or [{'path':n,**v} for n,v in m['files'].items()]
        for e in entries:
            n=d+'/'+e['path'];assert sha(ROOT/n)==e['sha256'],n;inputs[n]=e['sha256']
        inputs[d+'/MANIFEST.json']=want;counts[d]=len(entries)
    assert read(ROOT/LOCAL/'RESULT.json')['independently_accepted'] is True
    rel=str(control.relative_to(ROOT))+'/RESULT.json';inputs[rel]=sha(ROOT/rel)
    b={'utc':now(),'config':CONFIG,'sources':sources(),'reviews':{n:sha(ROOT/n) for n in REVIEWS},
       'inputs':inputs,'runtime':runtime(),'model_exact':pp['model_exact'],'parent_manifest_counts':counts,
       'D1_outcomes_before_freeze':False,'centers_only_dense_files':True}
    atomic(ROOT/'BINDINGS.json',b,True);atomic(ROOT/'FREEZE_RECORD.json',{'guard':sha(ROOT/'BINDINGS.json'),'utc':now()},True)
    for n in SOURCES+REVIEWS:(ROOT/n).chmod(0o444)
    print(json.dumps({'guard':sha(ROOT/'BINDINGS.json'),'status':'FROZEN','counts':counts}))


def full_cover(cover):
    lo,hi=CONFIG['D']
    return bool(cover) and cover[0][0]==lo and cover[-1][1]==hi and all(a[1]==b[0] for a,b in zip(cover,cover[1:]))
def require_finite(y):
    if not all(v.is_finite() for v in y):raise ArithmeticError('Nonfinite interval')
def integrate(state,engine,p,guard,out,endpoint=None):
    h=exact(CONFIG['step']);lo,hi=map(exact,CONFIG['D']);total=int(math.ceil(hi/h))
    start=time.monotonic();previous=state['elapsed_seconds']
    while state['cell_index']<total:
        j=state['cell_index'];s=j*h
        # save() replaces ALL native intervals by their outward-canonicalized
        # restored copies. Never retain a pre-save parameter-dict alias.
        ynext,cell=advance(state,h,engine);require_finite(ynext)
        if bounds(cell['box'][4])[0]<=0:raise ArithmeticError('exp(-W) positivity lost')
        state['max_picard']=max(state['max_picard'],cell['picard_iterations'])
        if s+h>=lo and s<=hi:
            a=max(fmpq(0),lo-s);b=min(h,hi-s)
            z=validated.range_on_cell(cell,a,b)
            state['cover'].append([str(s+a),str(s+b)])
            if state.get('end') is None:state['end']=z
            else:state['end']=[hull(u,v) for u,v in zip(state['end'],z)]
            if endpoint is not None:
                r=endpoint(z)
                if state.get('map') is None:state['map']=r
                else:state['map']={key:[hull(a,b) for a,b in zip(state['map'][key],r[key])] for key in r}
        state['y']=ynext;state['cell_index']+=1
        state['elapsed_seconds']=previous+time.monotonic()-start
        if state['cell_index']%CONFIG['checkpoint_cells']==0 or state['cell_index']==total:
            save(out,state,guard)
    assert full_cover(state['cover'])
    return state


def map_at(y,p,prep,jets):
    eps=p['eps'];parts=[];J=[y[12],y[14],y[16]];G=[y[10]-preparation.wall_increment(y,jets[1],p,eps)['target']]
    for side,j in enumerate(jets):
        e=preparation.wall_increment(y,j,p,eps)
        w=p['x'][0] if side==0 else y[9]
        qnew=j['qbg']*exp(-2*(eps*e['psi']+w))
        Delta=j['qbg']*e1(-2*(eps*e['psi']+w))-e['dr']
        correction=power(e['L'],5)*(-12*e['c']*e['S']*Delta-24*e['t']*Delta*Delta)
        G.append(p['x'][side+1]+prep['W'][side]+correction)
        cols=[arb(1),arb(0),arb(0)] if side==0 else [y[11],y[13],y[15]]
        multiplier=power(e['L'],5)*(-12*e['c']*e['S']-48*e['t']*Delta)*(-2*qnew)
        J.extend([int(n==side+1)+multiplier*cols[n] for n in range(3)])
        parts.extend([qnew,Delta,e['S'],e['L'],correction])
    require_finite(G+J+parts)
    assert all(bounds(parts[i])[0]>0 for i in (0,3,5,8))
    return {'G':G,'J':J,'wall_diagnostics':parts}


def worker(which,out):
    binding,guard=auth();out.mkdir(parents=True,exist_ok=True)
    lock=(out/'RUN.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if any((out/n).exists() for n in ('RESULT.json','FAILURE.json','TERMINAL.json')):raise RuntimeError('Terminal/failed phase restart refused')
    resource.setrlimit(resource.RLIMIT_AS,(CONFIG['address_space_bytes'],CONFIG['address_space_bytes']))
    def timeout(*args):raise TimeoutError('Frozen phase time cap')
    signal.signal(signal.SIGALRM,timeout)
    state=load(out,guard) if (out/'LATEST.json').exists() else {'task_index':0,'cell_index':0,'elapsed_seconds':0.,'which':which,'phase_results':[]}
    assert state['which']==which
    cap=CONFIG['source_seconds_cap'] if which=='source' else CONFIG['zero_seconds_cap'] if which=='zero' else CONFIG['case_seconds_cap']
    signal.alarm(max(1,math.ceil(cap-state['elapsed_seconds'])))
    try:
        y0,p0=initial(binding['model_exact'])
        if which=='source':
            if state['cell_index']==0:state.update(y=y0,p=p0,max_picard=0,cover=[],end=None)
            state=integrate(state,source_flow,state['p'],guard,out)
            jets=[preparation.wall_jets(y0,state['p'],0),preparation.wall_jets(state['end'],state['p'],1)]
            result={'status':'COMPLETE','which':which,'guard':guard,'p':state['p'],'y0':y0,'jets':jets,
                'event_cover':state['cover'],'cells':state['cell_index'],'elapsed_seconds':state['elapsed_seconds'],'max_picard':state['max_picard']}
        else:
            common_path=out.parent/'source'/'RESULT.json';common=unpack(read(common_path))
            assert common['guard']==guard and common['status']=='COMPLETE'
            common_terminal=read(out.parent/'source'/'TERMINAL.json')
            assert common_terminal['guard']==guard and common_terminal['result_sha256']==sha(common_path)
            eps,center=(fmpq(0),[fmpq(0)]*3) if which=='zero' else centers(which)
            radii=list(map(exact,CONFIG['radii']));jets=common['jets']
            if 'preparation' not in state:
                state['preparation']=preparation.prepare(eps,jets,common['p'])
                state['common_sha256']=sha(common_path)
            assert state['common_sha256']==sha(common_path)
            phases=['center'] if which=='zero' else ['center','box']
            while state['task_index']<len(phases):
                name=phases[state['task_index']]
                if state['cell_index']==0:
                    p=dict(common['p']);p.update(state['preparation'])
                    x=[arb(a) if name=='center' else interval(a-r,a+r) for a,r in zip(center,radii)];p['x']=x
                    lower=preparation.wall_increment(y0,jets[0],p,eps)['target']
                    state.update(p=p,y=list(common['y0'])+[x[0],lower,arb(1),arb(0),arb(0),arb(0),arb(0),arb(0)],
                                 max_picard=0,cover=[],end=None,map=None)
                state=integrate(state,nonlinear,state['p'],guard,out,lambda y:map_at(y,state['p'],state['preparation'],jets))
                phase={'phase':name,'guard':guard,'map':state['map'],'event_cover':state['cover'],'max_picard':state['max_picard'],'cells':state['cell_index'],'elapsed_seconds':state['elapsed_seconds']}
                if not (out/(name+'.json')).exists():atomic(out/(name+'.json'),phase,True)
                else:assert read(out/(name+'.json'))==pack(phase)
                state['phase_results'].append(phase);state['task_index']+=1;state['cell_index']=0
                save(out,state,guard)
            maps=[r['map'] for r in state['phase_results']]
            if which=='zero':
                checks={'zero_map_contains_zero':all(zero(x) for x in maps[0]['G']),
                        'zero_map_small':all(maxabs(x)<=fmpq(1,2**500) for x in maps[0]['G']),
                        'reduced_fifth_rows_identity':all(zero(maps[0]['J'][3+3*i+j]-int(j==i+1)) for i in range(2) for j in range(3))}
                result={'status':'COMPLETE','which':which,'guard':guard,'checks':checks,'pass':all(checks.values()),'map':maps[0]}
            else:
                C=list(map(exact,CONFIG['preconditioner_diagonal']));G=maps[0]['G'];flat=maps[1]['J'];J=[flat[i*3:i*3+3] for i in range(3)]
                M=[[int(i==j)-C[i]*J[i][j] for j in range(3)] for i in range(3)]
                rownorm=[sum(maxabs(M[i][j])*radii[j] for j in range(3))/radii[i] for i in range(3)]
                image=[-C[i]*G[i]+sum((M[i][j]*interval(-radii[j],radii[j]) for j in range(3)),arb(0)) for i in range(3)]
                included=[maxabs(image[i])<exact(CONFIG['image_fraction'])*radii[i] for i in range(3)]
                contraction=max(rownorm)<=exact(CONFIG['contraction_ceiling'])
                result={'status':'COMPLETE','which':which,'guard':guard,'epsilon':str(eps),'center':[str(c) for c in center],
                    'radii':CONFIG['radii'],'C':CONFIG['preconditioner_diagonal'],'G_center':G,'J_box':J,'I_minus_CJ':M,
                    'image_offset':image,'image_radius_ratios':[str(maxabs(a)/r) for a,r in zip(image,radii)],
                    'weighted_row_norms':[str(v) for v in rownorm],'component_inclusions':included,'contraction_pass':contraction,
                    'pass':all(included) and contraction,'common_sha256':state['common_sha256'],
                    'classification':'FINITE_AMPLITUDE_INITIAL_DATA_CERTIFIED' if all(included) and contraction else 'UNRESOLVED_INTERVAL_CERTIFICATE',
                    'event_covers':[r['event_cover'] for r in state['phase_results']]}
            result.update(elapsed_seconds=state['elapsed_seconds'],preparation=state['preparation'])
        atomic(out/'RESULT.json',result,True)
        atomic(out/'TERMINAL.json',{'guard':guard,'status':'COMPLETE','result_sha256':sha(out/'RESULT.json'),'utc':now()},True)
        atomic(out/'STATUS.json',{'state':'COMPLETE','guard':guard,'utc':now(),'result_sha256':sha(out/'RESULT.json')})
        print(json.dumps({'which':which,'status':'COMPLETE','pass':result.get('pass'),'elapsed_seconds':state['elapsed_seconds']}),flush=True)
    except KeyboardInterrupt:
        atomic(out/'STOPPED.json',{'guard':guard,'utc':now(),'resumable':(out/'LATEST.json').exists()})
        raise
    except Exception as exc:
        atomic(out/'FAILURE.json',{'guard':guard,'utc':now(),'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'last_durable_checkpoint':read(out/'LATEST.json') if (out/'LATEST.json').exists() else None},True)
        atomic(out/'STATUS.json',{'state':'TECHNICAL_INCOMPLETE','guard':guard,'utc':now(),'message':str(exc)})
        raise
    finally:signal.alarm(0)


def launch(output):
    b,guard=auth();output.mkdir(parents=True,exist_ok=True)
    lock=(output/'GRAPH.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if any((output/n).exists() for n in ('RESULT.json','TERMINAL.json','FAILURE.json')):raise RuntimeError('Terminal graph restart refused')
    def one(which):
        folder=output/which
        if (folder/'TERMINAL.json').exists():
            t=read(folder/'TERMINAL.json');assert t['guard']==guard and t['result_sha256']==sha(folder/'RESULT.json');return 0
        if (folder/'FAILURE.json').exists():return 1
        log=(output/(which+'.log')).open('a')
        return subprocess.Popen([sys.executable,'-B',str(ROOT/'runner.py'),'worker',str(folder),'--which',which],stdout=log,stderr=subprocess.STDOUT)
    phases=[]
    for which in ('source','zero'):
        p=one(which);rc=p if isinstance(p,int) else p.wait();phases.append(which)
        if rc or (which=='zero' and not read(output/which/'RESULT.json')['pass']):
            atomic(output/'FAILURE.json',{'guard':guard,'utc':now(),'failed_phase':which,'scope':'BOUNDED_GRAPH_STOPPED_NO_SUCCESSOR'},True)
            return
    pp={which:one(which) for which in ('positive','negative')}
    codes={which:(p if isinstance(p,int) else p.wait()) for which,p in pp.items()}
    data={which:read(output/which/'RESULT.json') if code==0 else read(output/which/'FAILURE.json') for which,code in codes.items()}
    passed=[which for which in data if data[which].get('pass') is True]
    classification='BOTH_SIGNED_FINITE_AMPLITUDE_C4_SAMPLES_CERTIFIED' if len(passed)==2 else 'ONE_SIGNED_SAMPLE_CERTIFIED_OTHER_UNRESOLVED' if len(passed)==1 else 'NO_FINITE_AMPLITUDE_CERTIFICATE_OBTAINED'
    result={'status':'COMPLETE','guard':guard,'utc':now(),'classification':classification,'passed_cases':passed,'return_codes':codes,
            'case_artifacts':{which:{'path':str((output/which/('RESULT.json' if codes[which]==0 else 'FAILURE.json')).relative_to(output)),
                'sha256':sha(output/which/('RESULT.json' if codes[which]==0 else 'FAILURE.json'))} for which in codes},
            'not_nonexistence':True,'independently_accepted':False,'next_experiment_authorized':False}
    atomic(output/'RESULT.json',result,True)
    atomic(output/'TERMINAL.json',{'guard':guard,'result_sha256':sha(output/'RESULT.json'),'utc':now()},True)


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('command',choices=['preflight','child','child-parameter','freeze','worker','launch']);a.add_argument('path',type=Path);a.add_argument('--which')
    args=a.parse_args();ctx.prec=CONFIG['bits'];ctx.threads=1
    assert all(os.environ.get(k)==v for k,v in ENV.items()),'Frozen runtime environment missing'
    if args.command=='preflight':preflight(args.path)
    elif args.command=='child':
        s=load(args.path,'manufactured-control');y,_=validated.step(s['y'],s['h'],s['p'],nonlinear);print(json.dumps({'digest':fingerprint(y)}))
    elif args.command=='child-parameter':
        s=load(args.path,'parameter-control');y,_=advance(s,s['h'],ParameterFixture);print(json.dumps({'digest':fingerprint(y)}))
    elif args.command=='freeze':freeze(args.path)
    elif args.command=='worker':worker(args.which,args.path)
    elif args.command=='launch':launch(args.path)
