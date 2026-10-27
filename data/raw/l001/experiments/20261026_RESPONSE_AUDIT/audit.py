"""Independent real-axis response arithmetic replay. Linux-only; no ODE."""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FLOW=ROOT.parent/'20261026T033400Z_CUBIC_FULL_FLOW'
FROZEN='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
LEASE=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
PINS={
 'BACKGROUND_CUTOFF':'23605bfbe42485d19e9f952ebd8f791984955ad04926eba697f283d6bc5aab38',
 'HIGH_ORDER_RESPONSE':'b6709b339c0725eca29279a9491366bb67bd3752b5d27d92836766fe5a2dbade',
 'LOW_ORDER_RESPONSE':'61419cb0ec42d9b00cdf7c2466fbaf4297c9b974fc2110bb2394bd30b89bcef5',
 'METRIC_RESPONSE':'ba72813582099f8ab47ccb2e855428bf80e4a3cfb670bdbc714b100974e1700d'}
def need(v,label):
    if not v:raise AssertionError(label)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_text())
def put(name,value):
    path=ROOT/name;tmp=ROOT/(name+'.tmp')
    with tmp.open('x') as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o444);os.link(tmp,path);tmp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def bounds(v):
    a,b=map(Q,v['exact_bounds']);need(a<=b,'ORDERED_BOUNDS');return a,b
def magnitude(v):return max(map(abs,bounds(v)))
def ceil(q):return -(-q.numerator//q.denominator)
def low_constants(n,V,U,A,b,L):
    if V<=0 or b<=0:return None
    length=min(L/2,1/(A+1));den=1-A*length/2;need(length>0 and den>0,'LOW_ABSORPTION')
    c0=max(1/V,1/(n*b));c1=((2/length+length*U/2)*c0+length/2)/den
    c2=A*c1+U*c0+1
    return n*n*c0+n*c1+c2
def global_constants(ext):
    k,e,H,T,P,m=[ext[x] for x in ('k0','e0','H0','T0','P0','m0')]
    need(k>0 and e>0,'POSITIVE_K_E')
    U=m*P+4*H*T;B=12*H*T+4*m*P;d=42*k*e*e;c=9*k*e*e
    return dict(U0=U,B0max=B,d0=d,c0=c,C0=B*U/d,Cb=2*T*U/d,drift_bound=4*H+B*T/d)
def metric_constants(ext,C,kup,Cf):
    H,T,U,d=ext['H0'],ext['T0'],C['U0'],C['d0']
    Hp=T*T/3+64*kup;p0=(1+(T+U)*Cf)/d;p1=2*H*p0+T*Cf/3+1
    p2=2*Hp*p0+2*H*p1+(U+T)*Cf/3+1
    return dict(Hprime_bound=Hp,P_value=p0,P_first=p1,P_second=p2,P_sum=p0+p1+p2)
def high_constants(ext,C,kup,L):
    N=39;lam=Q(1,64);c=C['c0'];A=C['drift_bound']
    v=ext['m0']+36*kup*64+2*ext['T0']*ext['T0']+C['C0']
    gates=dict(barrier=c-lam*lam-A*lam/N,boundary_separation=lam*N*L-1,taylor_segment=N*L-2,derivative_absorption=1-A/(2*N))
    if min(gates.values())<0 or gates['derivative_absorption']<=0:return gates,None
    c0=max(1/c,4/lam);c1=((2+v/2)*c0+Q(1,2))/gates['derivative_absorption'];c2=A*c1/N+v*c0+1
    return gates,dict(c=c,A=A,v=v,C_value=c0,C_first=c1,C_second=c2,C_sum=c0+c1+c2)
def main(lease):
    from flint import arb,fmpq,ctx
    ctx.prec=768;ctx.threads=1
    def ball(v):
        a,b=bounds(v);return arb(fmpq(str((a+b)/2)),fmpq(str((b-a)/2)))
    def lo(v):need(v.is_finite(),'FINITE_ARB');return Q(str(v.lower().fmpq()))
    def hi(v):need(v.is_finite(),'FINITE_ARB');return Q(str(v.upper().fmpq()))
    need(sha(FLOW/'FROZEN.json')==FROZEN,'PARENT_FROZEN');frozen=read(FLOW/'FROZEN.json')
    for path,digest in frozen['files'].items():need(sha(path)==digest,'PARENT_SOURCE:'+path)
    inputs={};saved={}
    for key,digest in PINS.items():
        folder=ROOT.parent/('20261026_'+key);r=folder/'RESULT.json';t=folder/'TERMINAL.json';b=folder/'BINDING.json'
        need(sha(r)==digest,'PIN:'+key);terminal=read(t)
        need(terminal['pass'] and terminal['result_sha256']==digest and terminal['binding_sha256']==sha(b),'DIAGNOSTIC_TERMINAL:'+key)
        for path in (r,t,b):inputs[str(path)]=sha(path)
        saved[key]=read(r)
    for mode in ('production','audit'):
        path=FLOW/(mode+'_TERMINAL.json');t=read(path);need(t['pass'] and t['frozen_sha256']==FROZEN,'FLOW_TERMINAL')
        inputs[str(path)]=sha(path)
        for name,digest in t['artifacts'].items():need(sha(FLOW/name)==digest,'FLOW_ARTIFACT');inputs[str(FLOW/name)]=digest
    runtime=lease.observed();source=sha(__file__)
    put('BINDING.json',{'source_sha256':source,'inputs':inputs,'parent_frozen_sha256':FROZEN,'runtime':runtime,'precision':768,'threads':1})
    started=time.monotonic();reports={};unresolved=[]
    need(low_constants(1,Q(1),Q(1),Q(0),Q(1),Q(2))==Q(6),'EXACT_RESPONSE_CONTROL')
    for name,dimension,step in (('primary',20,Q(1,4096)),('independent',19,Q(1,8192))):
        flow=read(FLOW/('FLOW_'+name+'.json'));need(flow['pass'] and Q(flow['step'])==step,'FLOW_PARAMETERS')
        L,Lhi=map(Q,flow['D']);need(0<L<=Lhi,'DOMAIN')
        need(bounds(flow['initial'][0])==(0,0),'W_ZERO_ORIGIN')
        m,k=ball(flow['parameters']['m2']),ball(flow['parameters']['k']);kup=bounds(flow['parameters']['k'])[1]
        ext=dict(H0=Q(0),T0=Q(0),P0=Q(0),m0=magnitude(flow['parameters']['m2']),k0=bounds(flow['parameters']['k'])[0])
        e0=None;wmax=None;low={n:None for n in range(1,39)};j=0;previous=None;last_state=flow['initial']
        ph=hashlib.sha256(json.dumps(flow['parameters'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        need(ph==flow['parameters_sha256'],'PARAMETER_HASH')
        for entry in flow['chunks']:
            path=FLOW/entry['file'];cp_path=FLOW/entry['checkpoint']
            need(path.resolve().is_relative_to(FLOW.resolve()) and cp_path.resolve().is_relative_to(FLOW.resolve()),'PATH_SCOPE')
            need(sha(path)==entry['sha256'] and sha(cp_path)==entry['checkpoint_sha256'],'CHUNK_CHECKPOINT_HASH')
            chunk=read(path);cp=read(cp_path)
            need(chunk['engine']==name and chunk['binding_sha256']==FROZEN and chunk['parameters_sha256']==ph and chunk['previous_sha256']==previous,'CHUNK_BINDING')
            need(chunk['first']==entry['first']==j and chunk['last']==entry['last'] and 1<=len(chunk['records'])<=32,'CHUNK_INDICES')
            for cell in chunk['records']:
                need(cell['index']==j and cell['start']==last_state,'CELL_SEQUENCE');box=cell['box'];need(len(box)==dimension,'DIMENSION')
                last_state=cell['end']
                for key,index in (('H0',1),('P0',2),('T0',3)):ext[key]=max(ext[key],magnitude(box[index]))
                if name=='primary':e=bounds(box[4])[0];e0=e if e0 is None else min(e0,e)
                else:w=bounds(box[0])[1];wmax=w if wmax is None else max(wmax,w)
                W,H,P,T=map(ball,box[:4]);E=ball(box[4]) if name=='primary' else (-W).exp();e2=E*E
                Tp=m*P-4*H*T;B=12*H*T-4*m*P;tt=2*T*T
                for n in low:
                    temporal=(36*n*n-18*n)*k*e2;J=3*temporal-12*k*e2;need(lo(J)>0,'POSITIVE_J');D=J+tt;need(lo(D)>0,'POSITIVE_D')
                    V=m+temporal+tt+B*Tp/D;drift=4*H+B*T/D
                    beta=(21-1/(2+temporal))*D/(2*J)-abs(2*T*Tp)/J
                    row=(lo(V),hi(abs(V)),hi(abs(drift)),lo(beta));old=low[n]
                    low[n]=row if old is None else (min(row[0],old[0]),max(row[1],old[1]),max(row[2],old[2]),min(row[3],old[3]))
                j+=1
                if j%2048==0:print(name,j,'cells',round(time.monotonic()-started,1),'seconds',flush=True)
            need(j==entry['last']+1,'CHUNK_END')
            need(cp['engine']==name and cp['binding_sha256']==FROZEN and cp['parameters_sha256']==ph and cp['chunk_sha256']==entry['sha256'],'CHECKPOINT_BINDING')
            need(cp['completed']==j and cp['total']==flow['cells'] and cp['state']==last_state and cp['resume_supported'] is False,'CHECKPOINT_STATE')
            previous=entry['sha256']
        need(j==flow['cells'] and last_state==flow['final'] and (j-1)*step<Lhi<=j*step,'FULL_COVERAGE')
        if name=='independent':e0=lo(arb(fmpq(str(-wmax))).exp())
        ext['e0']=e0;C=global_constants(ext);oldbg=saved['BACKGROUND_CUTOFF']['arms'][name]
        oldext={k:Q(v) for k,v in oldbg['extrema_exact'].items()};oldC=global_constants(oldext)
        need(all(oldC[k]==Q(v) for k,v in oldbg['cutoff']['constants'].items()),'SAVED_BACKGROUND_ARITHMETIC')
        N=oldbg['cutoff']['N'];need(N>=1 and oldC['c0']*N*N>=oldext['m0']+oldC['C0'] and oldC['Cb']<=Q(37,4)*N*N,'SAVED_CUTOFF')
        if not(C['c0']*39*39>=ext['m0']+C['C0'] and C['Cb']<=Q(37,4)*39*39):unresolved.append(name+':N39_CUTOFF')
        Eupper=hi(arb(fmpq(str(ext['H0']*Lhi))).exp());need(Eupper<8,'E_UPPER_EIGHT')
        gates,high=high_constants(ext,C,kup,L);oldhigh=saved['HIGH_ORDER_RESPONSE']['arms'][name]
        oldg,oldhc=high_constants(oldext,oldC,kup,L)
        need(oldhigh['N']==39 and Q(oldhigh['lambda'])==Q(1,64) and oldhigh['E_upper']==8,'SAVED_HIGH_SETTINGS')
        need(oldhc is not None and all(Q(oldhigh['gates_exact'][k])==v for k,v in oldg.items()) and all(Q(oldhigh['constants_exact'][k])==v for k,v in oldhc.items()),'SAVED_HIGH_ARITHMETIC')
        need(oldhigh['outward_integer_C_sum']==ceil(oldhc['C_sum']),'SAVED_HIGH_ROUNDING')
        if high is None or high['C_sum']>3932:unresolved.append(name+':HIGH_CONSTANT')
        low_report={};savedlow=saved['LOW_ORDER_RESPONSE']['arms'][name];need(set(savedlow)==set(map(str,range(1,39))),'SAVED_LOW_INVENTORY')
        for n,row in low.items():
            claimed=savedlow[str(n)];b=claimed['bounds_exact'];oldtuple=tuple(Q(b[k]) for k in ('V_min','V_abs_max','drift_abs_max','beta_lower'))
            oldsum=low_constants(n,*oldtuple,L);need(oldsum is not None and claimed['positive_gate'] and oldsum==Q(claimed['C_sum_exact']) and ceil(oldsum)==claimed['C_sum_integer'],'SAVED_LOW_ARITHMETIC')
            total=low_constants(n,*row,L)
            dominates=total is not None and total<=3932
            if not dominates:unresolved.append(name+':LOW_'+str(n))
            low_report[str(n)]={'bounds':list(map(str,row)),'bounds_minus_saved':list(map(str,(a-b for a,b in zip(row,oldtuple)))),'response_sum':None if total is None else str(total),'sum_minus_saved':None if total is None else str(total-oldsum),'fixed_3932_dominates':dominates}
        metric=metric_constants(ext,C,kup,Q(3932));oldmetric=metric_constants(oldext,oldC,kup,Q(3932));sm=saved['METRIC_RESPONSE']['arms'][name]
        need(all(Q(sm['exact'][k])==v for k,v in oldmetric.items()) and sm['outward_integer_P_sum']==ceil(oldmetric['P_sum']),'SAVED_METRIC_ARITHMETIC')
        if metric['P_sum']>306389:unresolved.append(name+':METRIC_CONSTANT')
        reports[name]={'cells':j,'extra_terminal_cover_included':True,'covered_to':str(j*step),'extrema':{k:str(v) for k,v in ext.items()},'extrema_minus_saved':{k:str(v-oldext[k]) for k,v in ext.items()},'high_gates':{k:str(v) for k,v in gates.items()},'high_sum':None if high is None else str(high['C_sum']),'high_sum_minus_saved':None if high is None else str(high['C_sum']-oldhc['C_sum']),'low':low_report,'metric_sum':str(metric['P_sum']),'metric_sum_minus_saved':str(metric['P_sum']-oldmetric['P_sum'])}
        put('ARM_'+name+'.json',reports[name]);print(name,'finished',round(time.monotonic()-started,1),flush=True)
    need(saved['METRIC_RESPONSE']['common_P_constant']==306389,'CLAIMED_METRIC_CONSTANT')
    for path,digest in frozen['files'].items():need(sha(path)==digest,'PARENT_UNCHANGED')
    for path,digest in inputs.items():need(sha(path)==digest,'INPUT_UNCHANGED')
    need(sha(__file__)==source,'SOURCE_UNCHANGED');after=lease.observed();need(after==runtime,'RUNTIME_UNCHANGED')
    out={'pass':not unresolved,'classification':'REAL_AXIS_RESPONSE_ARITHMETIC_VERIFIED' if not unresolved else 'RESPONSE_ARITHMETIC_UNRESOLVED','unresolved':unresolved,'scalar_constant':3932,'metric_constant':306389,'arms':reports,'seconds':time.monotonic()-started,'scope':'Independent archive reduction and scalar/metric response arithmetic. Inherits saved ODE enclosures; no ODE replay, complex collar, analytic majorant or amplitude radius certificate.'}
    put('RESULT.json',out);put('TERMINAL.json',{'completed':True,'pass':not unresolved,'result_sha256':sha(ROOT/'RESULT.json'),'binding_sha256':sha(ROOT/'BINDING.json')})
    print(json.dumps({k:v for k,v in out.items() if k!='arms'}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FLOW/'FROZEN.json')==FROZEN,'PARENT_FROZEN');need(read(FLOW/'FROZEN.json')['files'][str(LEASE)]==sha(LEASE),'LEASE_AUTHENTICATED')
        spec=importlib.util.spec_from_file_location('response_audit_lease',LEASE);lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=ROOT
        cpu,occupied=lease.acquire()
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):need(os.environ.get(key)=='1','SINGLE_THREAD_ENV')
        need(os.environ.get('PYTHONHASHSEED')=='0','HASH_SEED')
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('RESPONSE_AUDIT_1200_SECONDS')));signal.alarm(1200)
        put('START.json',{'pid':os.getpid(),'cpu':cpu,'occupied':occupied});sys.path.insert(0,str(lease.FLINT));main(lease)
    except BaseException as exc:
        put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        if lease is not None:
            for handle in lease.handles:handle.close()
