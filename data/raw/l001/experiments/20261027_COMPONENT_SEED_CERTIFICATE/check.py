"""Typed Klein-Gordon source paired full certificates."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def need(v,n):
    if not v:raise AssertionError(n)
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def certify(chosen,label,c,cfg,gate):
    def g(v,n):gate(v,label+':'+n)
    K=Q(chosen['K']);lam=Q(chosen['graph_weight']);kap=Q(chosen['oscillator_weight']);aa=Q(chosen['a'])
    g(K*aa>=1 and K>=2*max(map(Q,chosen['masses']))/aa**2,'MAJORANT')
    seed=max(Q(cfg['bulk_seed_bound']),Q(cfg['summed_wall_seed_bound'])/kap);g(0<seed<=16444,'SEED')
    R=1/(96*K);Y=(1+lam+kap)*R;radius=R/(8*seed);kr=K*R
    g(Q(1,2)+kr/(1-kr)**2<1 and 2*kr/(1-kr)**3<Q(1,2),'CONTRACTION')
    g(4*Y<c['gap'] and 2*Y<1,'CHART')
    Z=64/(1-4*Y/c['gap']);vel=4*Y*Z/(1-Y)**2;g(vel<Q(1,2),'TIMELIKE');g(Z/(1-Y)/(1-vel*vel)<=128,'LAPSE')
    MD=9*Y/(1-Y);MF=Q(129,32)*MD
    coeff=read(BASE/'20261026_NEUTRAL_CUBIC_CLOCK_TAIL/RESULT.json')['coefficient_intervals'];g(set(coeff)=={'primary','independent'},'TWO_ENGINES')
    for name,rec in coeff.items():
        lo,hi=map(Q,rec['F2']);lc,hc=map(Q,rec['F3']);g(-50<lo<=hi<-21 and -10000<lc<=hc<10000,'CLOCK:'+name)
    found=False
    for j in range(1,8193):
        q=Q(1,2**j);eta=radius*q/2;tail=MF*q**4/(1-q);known=10000*eta**3;qd=q/2
        dt=MD*qd**2/(1-qd);st=Y*qd**2/(1-qd);se=Y*qd**2*(2-qd)/(1-qd)**2
        if known+tail<=10*eta**2 and dt<=25*eta and st<=eta/40000 and se<=eta/40000:found=True;break
    g(found,'ALL_REMAINDER_GATES');g(eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0,'OPENING_SIGN')
    return dict(C0=c['C0'],Cscalar=c['total'],K=K,seed=seed,R=R,aggregate_bound=Y,physical_radius=radius,clock_eta=eta,observable_sup=MD,clock_sup=MF,clock_tail=tail,known_cubic=known,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000)
def inverse3(A):
    M=[list(row)+[Q(int(i==j)) for j in range(3)] for i,row in enumerate(A)]
    for i in range(3):
        need(M[i][i]!=0,'MATRIX_PIVOT');v=M[i][i];M[i]=[x/v for x in M[i]]
        for j in range(3):
            if i!=j:
                v=M[j][i];M[j]=[x-v*y for x,y in zip(M[j],M[i])]
    return [row[3:] for row in M]
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    parent=BASE/'20261027_TYPED_KG_CERTIFICATE_R1'
    bind(parent/'TERMINAL.json','86dbf492e07b8f0c68b0d255d5b0074b569d09af081117fb9228c5b9605896f0')
    t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
    seedroot=BASE/'20261026_NEUTRAL_ANALYTIC_SEED'
    for name in ('RESULT.json','BINDING.json','run.py','DERIVATION.txt'):
        gate(inputs.get(str(seedroot/name))==sha(seedroot/name),'SEED_AUTHORITY:'+name)
    seedold=read(seedroot/'RESULT.json');old=read(parent/'RESULT.json')
    c={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
    c['C0']=Q(old['constants_exact']['typed']['C0']);c['total']=Q(old['constants_exact']['typed']['Cscalar'])
    cfg=read(BASE/'20261027_SPLIT_NORM_GRID/CONTRACT.json')
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
    auth=BASE/'20261027T020711Z_TWO_HOUR_CONTINUATION/AUTHORITY.txt';bind(auth,sha(auth))
    len(str(10**20000));runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=1793074031))
    arms={};sb=sha(seedroot/'BINDING.json')
    gate(set(seedold['arms'])=={'primary','independent'},'TWO_ENGINES')
    for name,arm in seedold['arms'].items():
        ip=BASE/'20261026_GROWING_INVERSE_READINESS_R1'/('INITIAL_'+name+'.json')
        gate(inputs.get(str(ip))==sha(ip),'INITIAL:'+name);initial=read(ip)
        count=0;previous=None;last=initial['initial_native'];maxima=[Q(0)]*3;locations=[None]*3;shared=Q(0)
        for item in arm['chunks']:
            p=seedroot/item['file'];cp=seedroot/item['checkpoint']
            gate(inputs.get(str(p))==item['sha256'] and sha(p)==item['sha256'],'CHUNK_AUTH:'+item['file'])
            gate(inputs.get(str(cp))==item['checkpoint_sha256'] and sha(cp)==item['checkpoint_sha256'],'CHECKPOINT_AUTH:'+item['checkpoint'])
            chunk=read(p);checkpoint=read(cp)
            gate(chunk['engine']==name and chunk['binding_sha256']==sb and chunk['previous_sha256']==previous and chunk['first']==count,'CHUNK_CHAIN:'+item['file'])
            for row in chunk['records']:
                gate(row['index']==count and row['start_native']==last and row['constraints_pass'],'CELL:'+name+':'+str(count))
                local=[]
                for j,box in enumerate(row['box_canonical'][5:8]):
                    lo,hi=map(Q,box['exact_bounds']);gate(lo<=hi,'INTERVAL:'+name+':'+str(count)+':'+str(j))
                    v=max(abs(lo),abs(hi));local.append(v)
                    if v>maxima[j]:maxima[j]=v;locations[j]=dict(chunk=item['file'],index=count)
                stored=Q(row['mode_abs_upper']);gate(len(local)==3 and max(local)<=stored,'LOCAL_ENCLOSURE:'+name+':'+str(count))
                shared=max(shared,stored);last=row['end_native'];count+=1
            gate(chunk['last']==count-1 and checkpoint['engine']==name and checkpoint['completed']==count and checkpoint['total']==arm['cells'] and checkpoint['binding_sha256']==sb and checkpoint['previous_sha256']==previous and checkpoint['chunk_sha256']==item['sha256'] and checkpoint['last_native']==last and Q(checkpoint['mode_abs_upper'])==shared,'CHECKPOINT_CHAIN:'+item['file'])
            previous=item['sha256']
        gate(count==arm['cells']==initial['cells'] and last==arm['final_native'] and shared==Q(arm['mode_real_abs_upper']),'COMPLETE_ARM:'+name)
        step=Q(initial['step']);gate((count-1)*step<Q(initial['D'][1])<=count*step,'DOMAIN_COVERAGE:'+name)
        arms[name]=dict(cells=count,component_bounds=list(map(str,maxima)),locations=locations,shared_bound=str(shared))
        print(name,'whole cells authenticated',count,flush=True)
    real=[max(Q(a['component_bounds'][j]) for a in arms.values()) for j in range(3)]
    shared=max(Q(a['shared_bound']) for a in arms.values());rho=c['rho']
    gate(shared==Q(seedold['real_mode_bound']) and rho==Q(seedold['rho']),'SHARED_SEED_REPLAY')
    mc=shared/(1-104*rho);oldnorm=300*mc
    ceil=lambda q:-((-q.numerator)//q.denominator)
    gate(mc==Q(seedold['complex_mode_bound']) and oldnorm==Q(seedold['seed_norm']) and ceil(oldnorm)==seedold['seed_norm_outward_integer']==16444,'OLD_NORM_REPLAY')
    M=[[Q(6),Q(2,3),Q(0)],[Q(0),Q(0),Q(1)],[Q(80),Q(9)+Q(289,256),Q(12)]]
    gate(rho*max(map(sum,M))<1,'NEUMANN_CONDITION')
    A=[[Q(int(i==j))-rho*M[i][j] for j in range(3)] for i in range(3)];inv=inverse3(A)
    gate(all(x>=0 for row in inv for x in row),'POSITIVE_INVERSE')
    gate(all(sum(A[i][k]*inv[k][j] for k in range(3))==int(i==j) for i in range(3) for j in range(3)),'EXACT_MATRIX_INVERSE')
    X=[sum(inv[i][j]*real[j] for j in range(3)) for i in range(3)]
    gate(all(X[i]==real[i]+rho*sum(M[i][j]*X[j] for j in range(3)) for i in range(3)),'CONTINUATION_IDENTITY')
    gate(all(0<=v<=mc for v in X),'COMPONENT_DOMINATION')
    P,F,G=X;Pp=6*P+Q(2,3)*F;Ppp=4*P+6*Pp+Q(26,3)*F+Q(2,3)*G;Fpp=80*P+(Q(9)+Q(289,256))*F+12*G
    bulk=3*(P+Pp+Ppp)+F+G+Fpp;upper=Q(ceil(bulk))
    gate(0<bulk<=oldnorm and upper<=16444,'BULK_SEED_DOMINATION')
    selected=old['selected']['typed'];newcfg=dict(cfg,bulk_seed_bound=str(upper))
    constants=dict(baseline=certify(selected,'baseline',c,cfg,gate),component=certify(selected,'component',c,newcfg,gate))
    gate({k:str(v) for k,v in constants['baseline'].items()}==old['constants_exact']['typed'],'FULL_PARENT_CONSTANTS')
    effects={k:constants['component'][k]/constants['baseline'][k] for k in ('physical_radius','clock_eta')}
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST:'+p)
    result=dict(pass_status=True,classification='COMPONENT_FIRST_MODE_SEED_FULL_CERTIFICATE',arms=arms,real_components=list(map(str,real)),complex_components=list(map(str,X)),matrix=[[str(v) for v in row] for row in M],inverse=[[str(v) for v in row] for row in inv],derivative_bounds={k:str(v) for k,v in dict(Pp=Pp,Ppp=Ppp,Fpp=Fpp).items()},bulk_seed_exact=str(bulk),bulk_seed_integer=str(upper),selected=selected,constants_exact={mode:{k:str(v) for k,v in row.items()} for mode,row in constants.items()},effects_exact={k:str(v) for k,v in effects.items()},gates=gates,seconds=time.monotonic()-started,ode_solves=0)
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps(dict(seconds=result['seconds'],gates=len(gates),bulk_seed=float(upper),real_components=list(map(float,real)),complex_components=list(map(float,X)),display={mode:{k:float(v[k]) for k in ('physical_radius','clock_eta','seed')} for mode,v in constants.items()},gains={k:float(v) for k,v in effects.items()})),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(time.time()<1793074031,'FIXED_WINDOW_CUTOFF');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(frozen)['files'][str(lp)],'LEASE_PIN')
        lease=load('component_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        need(time.time()<1793074031,'POST_LEASE_LAUNCH_CUTOFF')
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('COMPONENT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
