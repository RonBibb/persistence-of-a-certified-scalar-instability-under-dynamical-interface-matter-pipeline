"""Source-bound exact arithmetic common-collar inverse certificate; Linux only."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1'
INV=BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE'
METRIC=BASE/'20261026_GROWING_NEUTRAL_METRIC_RESPONSE'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
DEADLINE=1793047195
gates={}
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def gate(v,n):need(v,n);gates[n]=True
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def bounds(v):return tuple(map(Q,v['exact_bounds']))
def ceil(v):return -((-v.numerator)//v.denominator)
def main(lease):
    started=time.monotonic();inputs={}
    for root,pin in [(FRESH,'f8a27fa6aeccb8f6b63af588d02fe8dd9a97c201956adbcf9544decb0a319445'),(INV,'1d756bb367a3e8c55452bfa95120b809ef08a2d681c7be1bf040fa0d0eb02bb4'),(METRIC,'b5d47177496093f1832a6d7a36f5d58d4c095c19d24ea6e5e03f38d38b1ec9b1')]:
        need(sha(root/'TERMINAL.json')==pin,'TERMINAL_PIN');t=read(root/'TERMINAL.json');need(t['pass'],'PARENT_PASS');inputs[str(root/'TERMINAL.json')]=pin
        for name,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')]:need(sha(root/name)==t[key],'PARENT_RECORD');inputs[str(root/name)]=t[key]
    for group in ('inputs','sources','runtime'):
        for p,h in read(METRIC/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_CLOSURE');inputs[p]=h
    for root,pin in [(INV/'audit','970f11cb9734c3dfe725788de8957a4b5ca0fced0727ec1ae6a4f8da14907c35'),(METRIC/'audit','06c64b772c6765b90a2cbfe43576ac14220793915635fbaa8d8cc572b7057847')]:
        need(sha(root/'AUDIT_TERMINAL.json')==pin,'AUDIT_PIN');t=read(root/'AUDIT_TERMINAL.json');need(t['pass_status'],'AUDIT_PASS');inputs[str(root/'AUDIT_TERMINAL.json')]=pin
        for name,key in [('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')]:need(sha(root/name)==t[key],'AUDIT_RECORD');inputs[str(root/name)]=t[key]
    ft=read(FRESH/'TERMINAL.json')
    for name,h in ft['artifacts'].items():need(sha(FRESH/name)==h,'FRESH_ARTIFACT');inputs[str(FRESH/name)]=h
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP');inputs[str(pylong)]=sha(pylong)
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,method='whole-real-archive plus complex Picard and exact uniform weighted inequalities',deadline_unix=DEADLINE))
    ir=read(INV/'RESULT.json');need(ir['scientific_certificate'],'REAL_INVERSE_PASS');arms={}
    for engine in ('primary','independent'):
        arm=read(FRESH/('ARM_'+engine+'.json'));initial=read(FRESH/('INITIAL_'+engine+'.json'))
        need(sha(FRESH/('INITIAL_'+engine+'.json'))==arm['initial_identity_sha256'],'INITIAL_PIN')
        pars={k:bounds(v) for k,v in initial['parameters'].items()}
        gate(0<pars['m2'][0]<=pars['m2'][1]<=1,engine+':MASS_BOUND')
        gate(0<pars['k'][0]<=pars['k'][1]<=Q(1,1024),engine+':K_BOUND')
        gate(Q(1,64)<=pars['h'][0]<=pars['h'][1]<pars['rate'][0]<=pars['rate'][1]<=Q(1,32),engine+':RATE_BOUND')
        # Exact h=sqrt(k) is an inherited model/initializer identity, not
        # asserted for every independent Cartesian pair of stored endpoints.
        gate(pars['h'][0]**2<=pars['k'][1] and pars['h'][1]**2>=pars['k'][0],engine+':H_K_ENCLOSURE_CONSISTENCY')
        index=0;previous=None;last=initial['initial_native'][:initial['background_native_dimension']];step=Q(initial['step'])
        for item in arm['chunks']:
            need(time.time()<DEADLINE and time.monotonic()-started<550,'TIME_BOUND')
            path=FRESH/item['file'];cppath=FRESH/item['checkpoint']
            need(path.resolve().is_relative_to(FRESH.resolve()) and cppath.resolve().is_relative_to(FRESH.resolve()),'SCOPED_PATH')
            need(sha(path)==item['sha256'] and sha(cppath)==item['checkpoint_sha256'],'CHUNK_HASH')
            chunk=read(path);cp=read(cppath)
            need(chunk['engine']==engine and chunk['binding_sha256']==ft['binding_sha256'] and chunk['initial_identity_sha256']==arm['initial_identity_sha256'] and chunk['previous_sha256']==previous,'CHUNK_BINDING')
            need(chunk['first']==item['first']==index,'CHUNK_START')
            for cell in chunk['records']:
                need(cell['index']==index and Q(cell['s'])==index*step and Q(cell['step'])==step and cell['start_native_background']==last,'CELL_CHAIN')
                last=cell['end_native_background'];canonical=cell['box_canonical_background']
                need(len(canonical)==5 and cell['box_native_background'][:4]==canonical[:4],'CANONICAL_BACKGROUND')
                need(cell['whole_cell_constraints_contain_zero'] and cell['background_first_integral_contains_zero'],'INHERITED_ODE_TUBES')
                W,H,P,T,E=map(bounds,canonical)
                need(-2<=H[0]<=H[1]<=2 and -1<=P[0]<=P[1]<=1 and -1<=T[0]<=T[1]<=1 and Q(1,2)<=E[0]<=E[1]<=16,'REAL_BOX:'+engine+':'+str(index))
                index+=1
            need(index==item['last']+1 and cp['completed']==index and cp['last_native_background']==last and cp['chunk_sha256']==item['sha256'],'CHECKPOINT_MATCH')
            previous=item['sha256']
        lengthlo,lengthhi=map(Q,initial['D']);gate(index==arm['cells']==initial['cells'] and last==arm['final_native_background'] and (index-1)*step<lengthhi<=index*step,engine+':COMPLETE_COVER')
        arms[engine]=dict(cells=index,domain=[str(lengthlo),str(lengthhi)],real_inverse_constant=ir['arms'][engine]['C_f'],real_inverse_outward_integer=ir['arms'][engine]['C_f_outward_integer'])
        print(engine,index,'whole cells admitted',flush=True)
    delta=Q(1,2**16);R0=delta/128;d0=Q(3,16384);qmax=Q(5,2048)
    F=max(Q(4,3)+Q(289,1024),Q(2),Q(26),Q(51))
    Lip=max(Q(4,3)+Q(34,1024),Q(1),Q(21),Q(20))
    gate(F<=64 and Lip<=32,'PICARD_POLYNOMIAL_ENVELOPES')
    gate(R0*64<=delta/2 and R0*32<Q(1,2),'COMMON_PICARD_COLLAR')
    variation=delta+delta**2/2+3*qmax*(32*delta+delta**2)
    gate(variation<d0/2,'ALL_N_DENOMINATOR_MARGIN')
    dc=d0/2;A=12+Q(160)/(4*dc);B=Q(1,4)+qmax*289+2+Q(80*26)/(16*dc)
    chosen=None
    for j in range(1,65):
        rho=R0/(2**j);q=max(B*(rho/2+rho*rho/4),A*(rho/5+rho*rho/8))
        if rho<=1 and q<=Q(1,4):chosen=(j,rho,q);break
    gate(chosen is not None,'PREDECLARED_COLLAR_SELECTION');j,rho,q=chosen
    C0=max(Q(a['real_inverse_constant']) for a in arms.values())
    XY=(C0*(2+rho/2)+rho/2+rho*rho/4)/(1-q)
    Cf=(1+max(B,A/2))*XY+1
    Cm=Q(11,4)/d0
    gate(rho*Q(3,2)<1,'METRIC_ABSORPTION')
    Xp=(Cm+rho*(Q(2,12)+Q(1,2)))/(1-rho*Q(3,2))
    Yp=3*Xp+Q(2,6)+1;Cp=Xp+(1+9/rho)*Yp
    constants=dict(delta=delta,prior_radius=R0,rho=rho,real_D_normalized_lower=d0,denominator_variation=variation,complex_D_normalized_lower=dc,A=A,B=B,q=q,C0=C0,XY=XY,scalar_C=Cf,metric_anchor=Cm,metric_X=Xp,metric_Y=Yp,metric_C=Cp)
    need(lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='ALL_NEUTRAL_ORDER_COMMON_COLLAR_SCALAR_METRIC_INVERSE_CERTIFIED',arms=arms,constants_exact={k:str(v) for k,v in constants.items()},constants_outward_integer={k:ceil(v) for k,v in constants.items() if k.endswith('_C')},selected_halving=j,gates=gates,scope='Analytic linear inverse all n>=2 with exact-parameter background and h²=k. Whole-cell background bounds inherited from authenticated validated ODE archives. Picard/Nagumo proof reviewed separately. Does not establish nonlinear source budget, first-mode norm, convergence radius or observable remainder.',seconds=time.monotonic()-started,new_ode_solves=0)
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps(dict(pass_status=True,rho=str(rho),scalar_C=ceil(Cf),metric_C=ceil(Cp),seconds=result['seconds'])),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE')
        need(not any((ROOT/n).exists() for n in ('START.json','TERMINAL.json','FAILURE.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE')
        lease=load('neutral_analytic_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ANALYTIC_INVERSE_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
