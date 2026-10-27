"""Frozen MP-background discriminator; admit original neighbors only after center."""
import datetime,hashlib,importlib.util,json,os,platform,signal,subprocess,sys,time
from fractions import Fraction
from pathlib import Path
import mpmath as mp
import numpy as np
import scipy
from scipy.integrate import simpson
from scipy.optimize import brentq
from mp_background import construct,decimal,rational
from sample_checks import check,scaled

HERE=Path(__file__).resolve().parent
OUT=HERE/'output'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def reject_stopped_packet(folder):
    if (folder/'TERMINAL.json').exists() or (folder/'FAILURE.json').exists():
        raise RuntimeError('terminal/failed packet cannot restart')
def scalar(x):
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)
def write(p,x,immutable=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if immutable and p.exists():raise RuntimeError('refusing overwrite '+str(p))
    tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
    with tmp.open('w') as f:
        json.dump(x,f,indent=2,sort_keys=True,allow_nan=False,default=scalar);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
    if immutable:p.chmod(0o444)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def runtime():
    return {'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
            'mpmath':mp.__version__,'mpmath_backend':mp.libmp.BACKEND,'longdouble_nmant':int(np.finfo(np.longdouble).nmant)}
def authenticate():
    b=read(HERE/'BINDINGS.json')
    for n,h in b['source'].items():
        if sha(HERE/n)!=h:raise RuntimeError('source mismatch '+n)
    for n,v in b['inputs'].items():
        if sha(HERE/v['path'])!=v['sha256']:raise RuntimeError('input mismatch '+n)
    preflight_path=HERE/b['inputs']['preflight_controls']['path']
    if sha(preflight_path)!=b['preflight_sha256'] or not read(preflight_path)['pass']:
        raise RuntimeError('preflight controls changed or failed')
    for n,h in read(preflight_path)['source_sha256'].items():
        if sha(HERE/n)!=h:raise RuntimeError('preflight evaluated different source '+n)
    if platform.system()!='Linux' or runtime()!=b['runtime']:raise RuntimeError('runtime mismatch or non-Linux')
    if any(os.environ.get(k)!='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','PYTHONDONTWRITEBYTECODE','PYTHONNOUSERSITE']):
        raise RuntimeError('environment control mismatch')
    if os.environ.get('PYTHONHASHSEED')!='0':raise RuntimeError('hash seed mismatch')
    return b
def old_modules(b):
    p=HERE/b['inputs']['old_proper_source']['path'];sys.path.insert(0,str(p.parent))
    old=load(p,'sealed_proper_solver');helper=old.load_helper(HERE/b['inputs']['differentiation_helper']['path'])
    return old,helper

def run_case(point,control,b,old,helper):
    start=time.monotonic();model=dict(b['model_exact']);model.update(point['exact_parameters'])
    bg,solution=construct(model,b['root_bracket'],control)
    m={n:float(rational(v)) for n,v in model.items()}
    meta={n:float(bg[n]) for n in ['a','k','D','L']}
    mu,mode,shoot=old.mode(m,meta,solution,control)
    s=np.array(bg['s'],dtype=float);Y=mode.sol(s)
    checks=[check(bg,Y,mu,helper,stride) for stride in [2,1]]
    turn=brentq(lambda t:solution.sol(t)[3],0,meta['D'],xtol=1e-14)
    Wt,Ht,pt,Tt,zt=solution.sol(turn);ht,ft,gt=mode.sol(turn)
    turn_error=scaled([m['m2']*pt*ft,3*(mu+4*meta['k'])*np.exp(-2*Wt)*ht])
    B=np.array(bg['fields'],dtype=float)
    Z=float(2*simpson(np.exp(2*B[0])*(Y[1]**2+6*Y[0]**2),x=s));dD=float(-2*simpson(Y[0],x=s))
    gates={'background_independent':all(x['max_background']<=1e-8 for x in checks),
           'mode_independent':all(x['max_mode']<=1e-6 for x in checks),
           'auxiliary_identity':mp.mpf(bg['auxiliary_identity_max'])<=mp.mpf('1e-20'),
           'turn_relation':turn_error<=1e-6,'positive_norm':Z>0,
           'nonzero_overlap':abs(dD/np.sqrt(Z))>1e-6,'negative_mass':mu<-1e-8,
           'norm_independent_agreement':all(abs(x['Z']/Z-1)<=1e-7 and abs(x['deltaD']/dD-1)<=1e-7 for x in checks)}
    comparison=None
    if point['name']=='center':
        prior=read(HERE/b['inputs']['prior_binding']['path'])
        comparison=old.central_comparison({'s':s,'background':B,'mode':Y},meta,mu,prior)
        d1=read(HERE/b['inputs']['d1_high_result']['path']);ind=read(HERE/b['inputs']['d1_independent_result']['path'])
        fine=max(ind['levels'],key=lambda x:x['steps'])
        inside=lambda value,ab:Fraction(ab[0])<=Fraction(value)<=Fraction(ab[1])
        mp_membership={'a':inside(bg['a'],d1['narrow']['newton_exact_bounds']),
                       'D':inside(bg['D'],list(map(str,d1['narrow']['event_bracket']))),
                       'k':inside(bg['k'],fine['geometry']['curvature']['exact_bounds'])}
        comparison['mp_membership']=mp_membership
        gates['central_branch_qualified']=comparison['pass'] and all(mp_membership.values())
    receipt={'point':point,'control':control,'model':m,'model_exact':model,
             'background':{n:bg[n] for n in ['a','k','D','L']},'mu':mu,'lambda':mu+4*meta['k'],
             'growth_over_H':float(np.sqrt(2.25-mu/meta['k'])-1.5),
             'Z':Z,'deltaD':dD,'overlap':dD/np.sqrt(Z),'shooting':shoot,
             'turn':{'s':turn,'normalized_relation':turn_error},'independent_checks':checks,
             'central_comparison':comparison,'checks':gates,'accepted':all(gates.values()),
             'elapsed_seconds':time.monotonic()-start,
             'evidence_classification':'MP_BACKGROUND_BINARY64_MODE_WITH_INDEPENDENT_SAVED_FIELD_GATES'}
    return receipt,bg,{'s':s,'mode':Y}

def pair(x,y):
    dm=abs(x['mu']-y['mu']);dl=abs(x['lambda']-y['lambda'])
    checks={'both_admitted':x['accepted'] and y['accepted'],'mass_refinement':dm<=1e-7,
            'mass_sign_resolved':y['mu']<-1e-8 and abs(y['mu'])>100*dm,
            'exceptional_sector_separated':abs(y['lambda'])>100*dl}
    return {'accepted':all(checks.values()),'checks':checks,'mass_difference':dm,
            'lambda_difference':dl,'mu':y['mu'],'lambda':y['lambda'],'growth_over_H':y['growth_over_H']}

def validate_checkpoint(cp,guard,b):
    if cp['guard']!=guard or cp['runtime']!=b['runtime']:raise RuntimeError('checkpoint binding/runtime mismatch')
    expected=[p['name']+'_'+c['name'] for p in b['points'] for c in b['controls']]
    completed=list(cp['completed'])
    if set(completed)!=set(expected[:len(completed)]):raise RuntimeError('completed order not a frozen prefix')
    for name,entry in cp['completed'].items():
        for kind in ['receipt','arrays','background']:
            if sha(OUT/entry[kind])!=entry[kind+'_sha256']:raise RuntimeError('checkpoint content mismatch '+name)
        r=read(OUT/entry['receipt'])
        if r['guard']!=guard or r['arrays_sha256']!=entry['arrays_sha256'] or r['background_sha256']!=entry['background_sha256']:
            raise RuntimeError('receipt mismatch '+name)
    if cp['pending']!=expected[len(completed):]:raise RuntimeError('pending queue changed')

def audit(filename):
    result=subprocess.run([sys.executable,'-B',str(HERE/'independent_review.py'),str(HERE),'--output','output','--allow-nonterminal'],
                          capture_output=True,text=True,timeout=600,check=True)
    record=json.loads(result.stdout);write(OUT/filename,record,True)
    return record

def main():
    b=authenticate();guard=sha(HERE/'BINDINGS.json');OUT.mkdir(exist_ok=True)
    reject_stopped_packet(OUT)
    old,helper=old_modules(b)
    control_path=OUT/'CONTROLS.json'
    if not control_path.exists():
        control=old.controls(helper);control['guard']=guard;write(control_path,control,True)
    control=read(control_path)
    if not control['pass'] or control['guard']!=guard:raise RuntimeError('analytic controls not admitted')
    tasks=[(p,c) for p in b['points'] for c in b['controls']]
    names=[p['name']+'_'+c['name'] for p,c in tasks]
    cp_path=OUT/'CHECKPOINT.json'
    cp=read(cp_path) if cp_path.exists() else {'guard':guard,'runtime':b['runtime'],'completed':{},'pending':names,'started_utc':now(),'controls_sha256':sha(control_path)}
    if cp.get('controls_sha256')!=sha(control_path):raise RuntimeError('checkpoint analytic controls changed')
    validate_checkpoint(cp,guard,b)
    halt=None
    def cap(signum,frame):raise TimeoutError('unchanged 600-second per-case cap')
    signal.signal(signal.SIGALRM,cap)
    for point,control in tasks:
        name=point['name']+'_'+control['name']
        if name in cp['completed']:
            if not read(OUT/cp['completed'][name]['receipt'])['accepted']:
                halt='SAVED_CASE_NOT_ADMITTED';break
            continue
        if point['name']!='center':
            central=[read(OUT/(x+'.json')) for x in ['center_coarse','center_fine']]
            if not pair(*central)['accepted']:halt='CENTRAL_PAIR_FAILED';break
            ap=OUT/'CENTRAL_INDEPENDENT.json'
            if ap.exists():
                if cp.get('central_independent_sha256')!=sha(ap):
                    raise RuntimeError('central independent admission receipt changed or uncommitted')
                independent=read(ap)
            else:
                independent=audit(ap.name)
                cp['central_independent_sha256']=sha(ap);write(cp_path,cp)
            if independent['guard']!=guard:raise RuntimeError('central independent guard mismatch')
            if not independent['central_qualified']:halt='CENTRAL_INDEPENDENT_FAILED';break
            if sha(HERE/'BINDINGS.json')!=guard:raise RuntimeError('binding changed after audit')
        receipt_path=OUT/(name+'.json');background_path=OUT/(name+'.background.json');array_path=OUT/(name+'.npz')
        if any(p.exists() for p in [receipt_path,background_path,array_path]):
            raise RuntimeError('uncommitted publication requires recovery review '+name)
        write(OUT/'STATUS.json',{'phase':'RUNNING','case':name,'completed':len(cp['completed']),
              'total':len(names),'guard':guard,'pid':os.getpid(),'updated_utc':now(),'informational_only':True})
        signal.alarm(600)
        try:receipt,bg,arrays=run_case(point,control,b,old,helper)
        finally:signal.alarm(0)
        write(background_path,bg,True)
        tmp=array_path.with_name(array_path.name+'.'+str(os.getpid())+'.tmp')
        with tmp.open('wb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
        os.replace(tmp,array_path);array_path.chmod(0o444)
        receipt.update(guard=guard,arrays_sha256=sha(array_path),background_sha256=sha(background_path))
        write(receipt_path,receipt,True)
        cp['completed'][name]={'receipt':receipt_path.name,'receipt_sha256':sha(receipt_path),
              'arrays':array_path.name,'arrays_sha256':sha(array_path),
              'background':background_path.name,'background_sha256':sha(background_path)}
        cp['pending']=names[len(cp['completed']):];write(cp_path,cp)
        print(json.dumps({'case':name,'accepted':receipt['accepted'],'mu':receipt['mu'],'seconds':receipt['elapsed_seconds'],
              'metric_max':max(x['background']['direct_metric'] for x in receipt['independent_checks'])}),flush=True)
        if not receipt['accepted']:halt='CASE_QUALIFICATION_FAILED';break
        if control['name']=='fine':
            paired=pair(read(OUT/(point['name']+'_coarse.json')),receipt)
            if not paired['accepted']:halt='PAIRED_QUALIFICATION_FAILED';break
    complete_pairs=[]
    for p in b['points']:
        paths=[OUT/(p['name']+'_'+c['name']+'.json') for c in b['controls']]
        if all(v.exists() for v in paths):
            complete_pairs.append({'point':p['name'],**pair(*map(read,paths))})
    independent=audit('FINAL_INDEPENDENT.json') if cp['completed'] else None
    success=(len(cp['completed'])==18 and all(x['accepted'] for x in complete_pairs)
             and independent['all_completed_cases_pass'] and independent['central_qualified'])
    result={'status':'COMPLETE' if success else 'UNRESOLVED','classification':
            'MP_BACKGROUND_QUALIFIED_NUMERICAL_GROWING_MODE_AT_NINE_POINTS' if success else 'MP_PRECISION_DISCRIMINATOR_UNRESOLVED',
            'completed_cases':len(cp['completed']),'uncomputed_cases':cp['pending'],'pairs':complete_pairs,
            'halt_reason':halt,'guard':guard,'completed_utc':now(),
            'independent_sha256':sha(OUT/'FINAL_INDEPENDENT.json') if independent else None,
            'rigorous_spectral_statement':False,'prior_failed_gate_reclassified':False}
    write(OUT/'RESULT.json',result,True)
    write(OUT/'TERMINAL.json',{'status':result['status'],'classification':result['classification'],
              'guard':guard,'result_sha256':sha(OUT/'RESULT.json'),'completed_utc':result['completed_utc']},True)
    write(OUT/'STATUS.json',{'phase':'TERMINAL','completed':len(cp['completed']),'total':18,'updated_utc':now(),'guard':guard})

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:
        write(OUT/'STATUS.json',{'phase':'STOPPED','updated_utc':now(),'recoverable_boundary':'last authenticated CHECKPOINT.json'})
        raise
    except Exception as exc:
        if OUT.exists() and not (OUT/'TERMINAL.json').exists() and not (OUT/'FAILURE.json').exists():
            write(OUT/'FAILURE.json',{'status':'TECHNICAL_INCOMPLETE','type':type(exc).__name__,'error':str(exc),'updated_utc':now()},True)
        raise
