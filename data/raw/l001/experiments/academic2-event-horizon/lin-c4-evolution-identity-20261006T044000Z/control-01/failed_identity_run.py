"""Bounded spatial identity/admission controls; no time evolution."""
from pathlib import Path
import argparse, json, os, platform, resource, subprocess, sys, time
from fractions import Fraction
import flint
from flint import arb, fmpq, ctx
import mode_flow, prepared_flow, preparation, validated
from series import bounds, interval, hull, record
from records import atomic, read, unpack, pack, sha, fingerprint, save, load, now

ROOT=Path(__file__).resolve().parent
BRANCH=Path('/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches')
NAMES={
 'connected':'02-event-horizon/lin-c4-connected-branch-20261006T004500Z',
 'finite':'02-event-horizon/lin-c4-finite-amplitude-20261005T223500Z',
 'central':'02-event-horizon/lin-central-validated-mode-r1-20261005T172800Z',
 'neighborhood':'02-event-horizon/lin-neighborhood-validated-mode-20261005T182300Z',
 'native':'01-horizon-core/d1-native-cauchy-20261005T201829Z',
 'admission':'01-horizon-core/d1-evolution-admission-20261005T214600Z',
 'short':'01-horizon-core/d1-short-evolution-20261005T224000Z',
 'spatial':'01-horizon-core/d1-spatial-evolution-20261005T232000Z',
 'second':'01-horizon-core/d1-second-order-scalar-20261006T003543Z'}
CONFIG={'bits':768,'threads':1,'step':'1/8192','maximum_cells_per_flow':16365,
 'flow_order':['mode','positive','negative'],'cpu_seconds_per_flow':1800,
 'checkpoint_cells':256,'address_space_bytes':4*1024**3,'cases':[0,3,4],
 'degrees':[160,192],'replay_dps':[80,100],'representation_gate':'1e-50',
 'readback_seconds':3600,'epsilon':['-1/200000','1/200000']}
ENV={'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTHONNOUSERSITE':'1',
     'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}


def setup():
    ctx.prec=CONFIG['bits'];ctx.threads=1
    for key,value in ENV.items():
        if os.environ.get(key)!=value:raise RuntimeError('Runtime environment '+key)
    resource.setrlimit(resource.RLIMIT_AS,(CONFIG['address_space_bytes'],CONFIG['address_space_bytes']))


def sources():
    return {p.name:sha(p) for p in sorted(ROOT.glob('*.py'))}|{
        name:sha(ROOT/name) for name in ('CONTRACT.md','DERIVATION.md',
        'INDEPENDENT_IDENTITY_NOTES.md','INDEPENDENT_GAUGE_BRIDGE.json')}


def runtime():
    import mpmath
    flintroot=Path(flint.__file__).resolve().parent
    mproot=Path(mpmath.__file__).resolve().parent
    paths=list(flintroot.rglob('*.so'))+list(mproot.rglob('*.py'))
    sibling=flintroot.parent/'python_flint.libs'
    if sibling.exists():paths+=list(sibling.glob('*'))
    paths+=[Path(sys.executable).resolve()]
    return {'python':platform.python_version(),'flint':flint.__version__,
            'mpmath':mpmath.__version__,'bits':ctx.prec,'threads':ctx.threads,
            'environment':ENV,'libraries':{str(p):sha(p) for p in paths if p.is_file()}}


def capacity():
    info=Path('/proc/meminfo').read_text().splitlines()
    available=int(next(line.split()[1] for line in info if line.startswith('MemAvailable:')))*1024
    load1=os.getloadavg()[0]
    if available<4*1024**3 or load1>=11:raise RuntimeError('Insufficient frozen capacity')
    return {'utc':now(),'available_bytes':available,'load1':load1,'cpus':os.cpu_count()}


def authenticate():
    inputs={};counts={}
    for name,relative in NAMES.items():
        parent=BRANCH/relative;manifest=parent/'MANIFEST.json';data=read(manifest)
        inputs[str(manifest)]=sha(manifest);counts[name]=len(data['entries'])
        for row in data['entries']:
            p=parent/row['path']
            if sha(p)!=row['sha256']:raise RuntimeError('Parent mutation: '+str(p))
            inputs[str(p)]=row['sha256']
    old=BRANCH/NAMES['connected'];binding=read(old/'BINDINGS.json')
    for name,digest in binding['inputs'].items():
        p=(old/name).resolve()
        if sha(p)!=digest:raise RuntimeError('Ancestor mutation: '+str(p))
        inputs[str(p)]=digest
    for ancestor in read(BRANCH/NAMES['second']/'BINDINGS.json')['predecessors']:
        p=BRANCH/'01-horizon-core'/ancestor['packet']/'MANIFEST.json'
        if sha(p)!=ancestor['manifest_sha256']:raise RuntimeError('Second-order predecessor changed')
    model=binding['model_exact']
    for name in ('native','second'):
        if read(BRANCH/NAMES[name]/'BINDINGS.json')['model_exact']!=model:
            raise RuntimeError('Exact action mismatch')
    return inputs,counts,model


def freeze(preflight):
    if (ROOT/'BINDINGS.json').exists():raise RuntimeError('Already frozen')
    pre=read(preflight)
    if not pre['passed'] or pre['sources']!=sources() or pre['runtime']!=runtime():
        raise RuntimeError('Stale preflight')
    review=ROOT/'PREFLIGHT_REVIEW.md'
    if not review.exists():raise RuntimeError('Independent preflight review missing')
    inp,counts,model=authenticate()
    b={'utc':now(),'config':CONFIG,'sources':sources(),'inputs':inp,
       'parent_counts':counts,'model_exact':model,'runtime':runtime(),
       'preflight':{'path':str(Path(preflight).resolve()),'sha256':sha(preflight)},
       'review_sha256':sha(review),'capacity':capacity(),
       'physical_outcomes_before_freeze':False}
    atomic(ROOT/'BINDINGS.json',b,True)
    atomic(ROOT/'FREEZE_RECORD.json',{'utc':now(),'guard':sha(ROOT/'BINDINGS.json')},True)


def guard():
    b=read(ROOT/'BINDINGS.json')
    if b['config']!=CONFIG or b['runtime']!=runtime():raise RuntimeError('Changed config/runtime')
    for name,digest in b['sources'].items():
        if sha(ROOT/name)!=digest:raise RuntimeError('Changed source '+name)
    for name,digest in b['inputs'].items():
        if sha(name)!=digest:raise RuntimeError('Changed input '+name)
    if sha(ROOT/'PREFLIGHT_REVIEW.md')!=b['review_sha256']:raise RuntimeError('Changed preflight review')
    if sha(b['preflight']['path'])!=b['preflight']['sha256']:raise RuntimeError('Changed preflight')
    return sha(ROOT/'BINDINGS.json'),b


def exact(value):return fmpq(str(value))


def maximum_abs(ball):
    lo,hi=bounds(ball);return max(abs(lo),abs(hi))


def poly(row,z):
    v=arb(0)
    for coefficient in reversed(row):v=v*z+coefficient
    return v


class SavedProfile:
    """Exact decimal input polynomial, enclosed without rounding it to binary64."""
    def __init__(self,case=None):
        p=BRANCH/NAMES['native']/'results/fine_c4'
        self.raw=read(p/'SEED.json');self.D=exact(self.raw['D']);self.h=exact(self.raw['h'])
        self.seed=[[[arb(exact(c)) for c in row] for row in block] for block in self.raw['segments']]
        self.case=case
        if case is not None:
            self.data=read(p/f'case_{case}.dense.json');self.eps=arb(exact(self.data['epsilon']))
            self.metric=[[arb(exact(c)) for c in block[0]] for block in self.data['segments']]
            self.correction=[arb(exact(c)) for c in self.data['correction']]

    def enclose(self,lo,hi):
        lo=max(fmpq(0),lo);hi=min(self.D,hi)
        if lo>hi:raise ArithmeticError('Empty normalized comparison interval')
        count=len(self.seed)
        start=max(0,min(count-1,int(lo//self.h)))
        stop=max(0,min(count-1,int(hi//self.h)))
        result=None
        for i in range(start,stop+1):
            left=max(lo,i*self.h);right=min(hi,(i+1)*self.h)
            # The decimal D/h relation can differ in its last stored digit.
            if i==count-1:right=hi
            if left>right:continue
            z=interval(left-i*self.h,right-i*self.h)
            base=[poly(row,z) for row in self.seed[i]]
            if self.case is None:values=base
            else:
                s=interval(left,right)
                values=[poly(self.metric[i],z),-2*self.eps*base[5],
                        base[2]+self.eps*base[6]+poly(self.correction,s)]
            result=values if result is None else [hull(a,b) for a,b in zip(result,values)]
        if result is None:raise ArithmeticError('Missing polynomial cover')
        return result


def physical_values(y,p,name):
    if name=='mode':return y[:8]
    W,H,P,T,E,psi,f,g,s,w,v=y
    D=p['D'];eps=p['eps']
    H0=s**5*(D-s)**6/(120*D**6);H1=s**6*(s-D)**5/(120*D**6)
    d=poly(p['c7'],s)+p['x'][1]*H0+p['x'][2]*H1
    return [W+eps*psi+w,-2*eps*psi,P+eps*f+d]


def fresh_state(name,task_index):
    common=unpack(read(BRANCH/NAMES['finite']/'output/source/RESULT.json'))
    p=common['p'];y=common['y0']
    if name=='mode':
        B=p['gamma']*y[3]/2-p['m2']*y[2]+4*y[1]*y[3]
        if bounds(B)[0]<=0<=bounds(B)[1]:raise ArithmeticError('Launch denominator includes zero')
        fm=3/B;y=list(y)+[arb(0),fm,p['gamma']*fm/2]
    else:
        old=unpack(read(BRANCH/NAMES['finite']/f'output/{name}/RESULT.json'))
        if not old['pass']:raise RuntimeError('Uncertified signed parent')
        p=p|old['preparation'];p['x']=[arb(exact(c))+r for c,r in zip(old['center'],old['image_offset'])]
        low=preparation.wall_increment(y,common['jets'][0],p,p['eps'])['target']
        y=list(y)+[p['x'][0],low]
    return {'task_index':task_index,'cell_index':0,'name':name,'y':y,'p':p,
            'max_errors':[fmpq(0)]*(8 if name=='mode' else 3),'event_derivative':None,
            'event_cover':[],'elapsed_seconds':0.0,'integration_cpu_seconds':0.0,
            'max_picard':0,'domain_maxima':[fmpq(0)]*len(y),'capacity':capacity()}


def integrate(name,task_index,g):
    out=ROOT/'output'/name;out.mkdir(parents=True,exist_ok=True)
    if (out/'FAILURE.json').exists():raise RuntimeError('Failed-closed task')
    if (out/'TERMINAL_CHECKPOINT.json').exists():
        term=read(out/'TERMINAL_CHECKPOINT.json')
        if term['guard']!=g or term['result_sha256']!=sha(out/'RESULT.json'):
            raise RuntimeError('Stale terminal')
        return read(out/'RESULT.json')
    if (out/'RESULT.json').exists():raise RuntimeError('Terminal publication interrupted; inspect without recomputing')
    state=load(out,g) if (out/'LATEST.json').exists() else fresh_state(name,task_index)
    if state['name']!=name or state['task_index']!=task_index:raise RuntimeError('Wrong checkpoint task')
    engine=mode_flow if name=='mode' else prepared_flow
    profile=SavedProfile(None if name=='mode' else 3 if name=='positive' else 4)
    oldconfig=read(BRANCH/NAMES['connected']/'BINDINGS.json')['config']
    Dlo,Dhi=map(exact,oldconfig['D']);step=exact(CONFIG['step'])
    start=time.monotonic();cpu_start=time.process_time();basewall=state['elapsed_seconds'];basecpu=state['integration_cpu_seconds']
    try:
        while state['cell_index']*step<Dhi:
            i=state['cell_index'];t=i*step;h=min(step,Dhi-t)
            if i>=CONFIG['maximum_cells_per_flow']:raise RuntimeError('Cell budget exceeded')
            if basecpu+time.process_time()-cpu_start>CONFIG['cpu_seconds_per_flow']:
                raise TimeoutError('Frozen per-flow CPU budget')
            y,cell=validated.step(state['y'],h,state['p'],engine)
            ranged=validated.range_on_cell(cell,fmpq(0),h)
            before=profile.enclose(t*profile.D/Dhi,min(profile.D,(t+h)*profile.D/Dlo))
            after=physical_values(ranged,state['p'],name)
            state['max_errors']=[max(a,maximum_abs(b-c)) for a,b,c in zip(state['max_errors'],after,before)]
            state['domain_maxima']=[max(a,maximum_abs(b)) for a,b in zip(state['domain_maxima'],ranged)]
            if name=='mode' and t+h>=Dlo:
                lo=max(fmpq(0),Dlo-t);hi=min(h,Dhi-t)
                ey=validated.range_on_cell(cell,lo,hi);v=mode_flow.determinant_mu(ey,state['p'])
                state['event_derivative']=v if state['event_derivative'] is None else hull(state['event_derivative'],v)
                state['event_cover'].append({'cell':i,'left':t+lo,'right':t+hi,'F_mu':v})
            state['y']=y;state['cell_index']+=1;state['max_picard']=max(state['max_picard'],cell['picard_iterations'])
            state['elapsed_seconds']=basewall+time.monotonic()-start
            state['integration_cpu_seconds']=basecpu+time.process_time()-cpu_start
            if state['cell_index']%CONFIG['checkpoint_cells']==0 or t+h==Dhi:
                save(out,state,g)
        passed=name!='mode' or bounds(state['event_derivative'])[1]<0
        result={'guard':g,'task':name,'passed':passed,'cells':state['cell_index'],
            'elapsed_seconds':state['elapsed_seconds'],'integration_cpu_seconds':state['integration_cpu_seconds'],
            'max_picard':state['max_picard'],'source_uncertainty_retained':True,
            'comparison_coordinate':'u=s/D; whole closed domain [0,1]',
            'max_error_bounds_exact':[str(v) for v in state['max_errors']],
            'max_error_bounds_decimal':[float(v) for v in state['max_errors']],
            'field_order':['W','H','Phi','T','exp(-W)','psi','f','g'] if name=='mode' else ['A','ell','Phi'],
            'domain_maxima':[str(v) for v in state['domain_maxima']],
            'F_mu':None if name!='mode' else record(state['event_derivative']),
            'event_cover':state['event_cover'],'last_checkpoint':read(out/'LATEST.json'),
            'new_evolution_steps':0,'utc':now()}
        atomic(out/'RESULT.json',result,True)
        atomic(out/'TERMINAL_CHECKPOINT.json',{'guard':g,'status':'COMPLETE' if passed else 'SCIENTIFIC_GATE_FAILED',
               'result_sha256':sha(out/'RESULT.json'),'utc':now()},True)
        return result
    except Exception as e:
        atomic(out/'FAILURE.json',{'guard':g,'type':type(e).__name__,'message':str(e),'utc':now()},True)
        raise


def synthetic_initial():
    p={k:arb(0) for k in ('m2','mu','k')};p['gamma']=arb(20)
    y=[arb(v) for v in (0,0,0,0,1,1,1,0,0,0,0,0)]
    return {'task_index':0,'cell_index':0,'y':y,'p':p,'elapsed_seconds':0.0}


def control_worker(output,steps,resume,guard_value):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    state=load(out,guard_value) if resume else synthetic_initial()
    for i in range(state['cell_index'],steps):
        state['y'],cell=validated.step(state['y'],fmpq(1,128),state['p'],mode_flow)
        state['cell_index']=i+1
        if (i+1)%4==0:save(out,state,guard_value)
    atomic(out/f'AT_{steps}.json',state,True)


def preflight(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    ss=sources();rr=runtime();g=fingerprint({'sources':ss,'runtime':rr,'config':CONFIG})
    cmd=[sys.executable,'-B',str(ROOT/'identity_run.py'),'control-worker']
    subprocess.run(cmd+[str(out/'direct'),'--steps','8','--control-guard',g],check=True)
    subprocess.run(cmd+[str(out/'split'),'--steps','4','--control-guard',g],check=True)
    subprocess.run(cmd+[str(out/'split'),'--steps','8','--resume','--control-guard',g],check=True)
    direct=read(out/'direct/AT_8.json');split=read(out/'split/AT_8.json')
    if direct!=split:raise RuntimeError('Fresh-process replay mismatch')
    state=unpack(direct);s=arb(fmpq(1,16));exact_values={9:arb(0),10:-s*s/2,11:-s}
    for j,v in exact_values.items():
        if not state['y'][j].contains(v):raise RuntimeError('Synthetic derivative failed')
    rejected=False
    try:load(out/'split','wrong guard')
    except AssertionError:rejected=True
    if not rejected:raise RuntimeError('Wrong guard accepted')
    # Atomic temporary files cannot displace the authenticated committed pointer.
    atomic(out/'split/LATEST.json.uncommitted-fixture',{'invalid':True},True)
    if pack(load(out/'split',g))!=split:raise RuntimeError('Temporary file affected resume')
    for j in range(4):
        coefficient=mode_flow.coeff(synthetic_initial()['y'],4,synthetic_initial()['p'])[10][j]
        expected=arb(-fmpq(1,2) if j==2 else 0)
        if not coefficient.contains(expected):raise RuntimeError('Sensitivity Taylor coefficient')
    fixture=SavedProfile.__new__(SavedProfile);fixture.case=None
    fixture.D=fmpq(1);fixture.h=fmpq(1,2)
    fixture.seed=[[[arb(0),arb(2)]]*8,[[arb(1),arb(2)]]*8]
    whole=fixture.enclose(fmpq(1,4),fmpq(3,4))
    if not all(v.contains(arb(fmpq(1,2))) and v.contains(arb(fmpq(3,2))) for v in whole):
        raise RuntimeError('Cross-segment interval cover failed')
    prepared=synthetic_initial()['y'][:9]+[arb(0),arb(0)]
    pp=synthetic_initial()['p']|{'D':arb(2),'eps':fmpq(0),'x':[arb(0)]*3,'c7':[arb(0)]*8}
    py,pcell=validated.step(prepared,fmpq(1,128),pp,prepared_flow)
    if not py[9].contains(arb(0)) or not py[10].contains(arb(0)):
        raise RuntimeError('Prepared-state zero control failed')
    result={'passed':True,'fresh_process_bitwise_exact':True,'wrong_guard_rejected':True,
        'uncommitted_file_ignored':True,'synthetic_inhomogeneous_derivative_passed':True,
        'cross_segment_interval_cover_passed':True,'prepared_zero_control_passed':True,
        'sources':ss,'runtime':rr,'config':CONFIG,'utc':now(),'physical_outcomes':False}
    atomic(out/'RESULT.json',result,True)
    print(json.dumps({'preflight':'PASS','path':str(out/'RESULT.json')}),flush=True)


def run():
    g,b=guard();capacity();results=[]
    for i,name in enumerate(CONFIG['flow_order']):
        result=integrate(name,i,g);results.append(result)
        print(json.dumps({'task':name,'passed':result['passed'],'seconds':result['elapsed_seconds'],
              'error_bounds':result['max_error_bounds_decimal'],'F_mu':result['F_mu']}),flush=True)
        if not result['passed']:break
    atomic(ROOT/'SPATIAL_ENCLOSURES.json',{'guard':g,'passed':len(results)==3 and all(x['passed'] for x in results),
        'tasks':results,'no_time_evolution':True,'utc':now()},True)


if __name__=='__main__':
    setup();p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('preflight');q.add_argument('output')
    q=sub.add_parser('control-worker');q.add_argument('output');q.add_argument('--steps',type=int,required=True)
    q.add_argument('--resume',action='store_true');q.add_argument('--control-guard',required=True)
    q=sub.add_parser('freeze');q.add_argument('preflight')
    sub.add_parser('run');a=p.parse_args()
    if a.command=='preflight':preflight(a.output)
    elif a.command=='control-worker':control_worker(a.output,a.steps,a.resume,a.control_guard)
    elif a.command=='freeze':freeze(a.preflight)
    else:run()
