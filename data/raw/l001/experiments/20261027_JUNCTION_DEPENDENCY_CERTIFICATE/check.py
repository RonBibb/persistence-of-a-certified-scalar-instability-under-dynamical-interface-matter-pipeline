"""Isolate higher-order scalar junction source dependence."""
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
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    parent=BASE/'20261027_DIRECT_G_BARRIER_CERTIFICATE'
    bind(parent/'TERMINAL.json','da0b1151a2ef1964a19663ab3269150f6be600a936ca929f21b0c784237b06f2')
    t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,digest in read(parent/'BINDING.json')[group].items():bind(p,digest)
    def authenticated(name):
        p=BASE/name/'RESULT.json';gate(inputs.get(str(p))==sha(p),'AUTHORITY:'+name);return read(p)
    old=read(parent/'RESULT.json');diag=authenticated('20261027_DENOMINATOR_FACTORIAL');seedparent=authenticated('20261027_BACKGROUND_SEED_CERTIFICATE_R1')
    ep=load('denom_endpoint',BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/check.py')
    prim=load('denom_primitives',BASE/'20261026_ROUTED_SOURCE_BUDGET_R1/check.py').primitives
    Jet=load('denom_jets',BASE/'20261026_TAIL_FEASIBILITY_ORACLE/check.py').Jet
    envmod=load('denom_env',BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py')
    def env(x,gap):
        e=envmod.envelopes(x,gap);e['BR']=ep.radial_envelope(x,gap);e['BM']=ep.mixed_envelope(x,gap)
        H,T,Phi,E=ep.field_jets(x,gap);TP=26+1320*x+37600*x*x+64*(4*x/gap)**3/(1-4*x/gap)
        G=1/(1-2*x);w=4*x*G;wu=2*x*G;wt=4*x*G+8*x*x*G*G
        d=x*(1+w);dd=x*(1+2*w+w*wu+wt+w*w);l=G*x;ll=G*G*x
        e['BK']=E*E*G*(dd+(Q(3,32)+3*d)*d)+G*(TP+ll+(4*H+5*l)*(T+l))+Phi+x
        return e
    c={k:Q(v) for k,v in authenticated('20261026_NEUTRAL_SOURCE_MAJORANT')['constants_exact'].items()}
    c['C0']=Q(old['constants_exact']['boundary']['C0']);c['total']=Q(old['constants_exact']['boundary']['Cscalar'])
    cfg=read(BASE/'20261027_SPLIT_NORM_GRID/CONTRACT.json');cfg=dict(cfg,bulk_seed_bound=seedparent['bulk_seed_integer'])
    weights={mode:{out:list(map(Q,vals)) for out,vals in old['response_weights']['boundary'].items()} for mode in ('baseline','junction')}
    def primitive(w,lam,kap,mode):
        original=prim(w,lam,kap,c,env)
        W=w+lam*w;rho=c['rho']
        ws=4*W*(1+2*W)/(1-2*W)**3;V=3*W+22*ws*W/rho
        cn=138*V*V/(1-160*ws/rho-840*ws*ws/rho**2)
        e=env(W,c['gap'])
        return (cn,original[1],e['BM'],e['BK'],e['BR'],e['BJ'] if mode=='junction' else original[5],original[6])
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
    for n in ('lease.py','DESIGN.txt'):
        p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
    auth=BASE/'20261027T020711Z_TWO_HOUR_CONTINUATION/AUTHORITY.txt';bind(auth,sha(auth))
    len(str(10**20000));runtime=lease.observed()
    for p,digest in runtime.items():need(inputs.get(p)==digest or sources.get(p)==digest,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=1793074031))
    prior=old['candidates']['boundary'];gate(len(prior)==1123,'FROZEN1123_GRID')
    candidates={mode:[] for mode in weights};jets={}
    for idx,p in enumerate(prior):
        lam=Q(p['graph_weight']);kap=Q(p['oscillator_weight']);a=Q(p['a']);exponent=p['exponent']
        gate(max(Q(cfg['bulk_seed_bound']),Q(cfg['summed_wall_seed_bound'])/kap)==Q(cfg['bulk_seed_bound']),'GRID_SEED:'+str(idx))
        gate(ep.domain(a,lam,kap,c),'DOMAIN:'+str(idx))
        masses={};lane_loads={}
        for mode,w in weights.items():
            if (mode,lam,kap) not in jets:jets[mode,lam,kap]=primitive(Jet(0,1),lam,kap,mode)
            pj=jets[mode,lam,kap];pv=primitive(a,lam,kap,mode)
            loads=[v-j.v[0]-a*j.v[1] for v,j in zip(pv,pj)]
            lane_loads[mode]=loads
            gate(all(v>=0 for v in loads),'POSITIVE_LOADS:'+mode+':'+str(idx))
            m=[sum(k*v for k,v in zip(w['B'],loads)),loads[1]/lam,sum(k*v for k,v in zip(w['C'],loads))/kap];masses[mode]=m
            K=Q(ep.ceil(max(Q(1),1/a,2*max(m)/a**2)))
            rec=dict(graph_weight=str(lam),oscillator_weight=str(kap),exponent=exponent,a=str(a),admitted=True,masses=list(map(str,m)),K=str(K));candidates[mode].append(rec)
            if mode=='baseline':gate(rec==p,'PARENT_ROW:'+str(idx))
        gate(all(lane_loads['junction'][j]==lane_loads['baseline'][j] for j in (0,1,2,3,4,6)),'UNCHANGED_PRIMITIVES:'+str(idx))
        gate(0<=lane_loads['junction'][5]<=lane_loads['baseline'][5],'LOAD_DOMINATION:'+str(idx))
        gate(all(masses['junction'][j]<=masses['baseline'][j] for j in range(3)),'MASS_DOMINATION:'+str(idx))
    selected={mode:min(rows,key=lambda v:Q(v['K'])) for mode,rows in candidates.items()}
    constants={mode:certify(row,mode,c,cfg,gate) for mode,row in selected.items()}
    gate(selected['baseline']==old['selected']['boundary'],'PARENT_SELECTION')
    gate({k:str(v) for k,v in constants['baseline'].items()}==old['constants_exact']['boundary'],'FULL_PARENT_CONSTANTS')
    effects={mode:{k:constants[mode][k]/constants['baseline'][k] for k in ('physical_radius','clock_eta')} for mode in weights if mode!='baseline'}
    budgets={};branches={};names=('TRACE','GRAPH','BM','BK','BR','BJ','BO')
    for mode,row in selected.items():
        a=Q(row['a']);lam=Q(row['graph_weight']);kap=Q(row['oscillator_weight']);w=weights[mode]
        pv=primitive(a,lam,kap,mode);pj=jets[mode,lam,kap];loads=[v-j.v[0]-a*j.v[1] for v,j in zip(pv,pj)]
        budgets[mode]={out:{name:str(k*v) for name,k,v in zip(names,w[out],loads)} for out in ('B','C')}
        m=list(map(Q,row['masses']));gate(sum(map(Q,budgets[mode]['B'].values()))==m[0],'BUDGET_B:'+mode);gate(sum(map(Q,budgets[mode]['C'].values()))/kap==m[2],'BUDGET_C:'+mode)
        terms=dict(one=Q(1),inverse_a=1/a,mass=2*max(m)/a**2);top=max(terms.values())
        branches[mode]=dict(active=[k for k,v in terms.items() if v==top],mass_over_inverse_a=str(terms['mass']*a),relative_masses=[str(v/max(m)) for v in m])
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,digest in dict(inputs,**sources).items():need(sha(p)==digest,'POST:'+p)
    result=dict(pass_status=True,classification='SCALAR_JUNCTION_DEPENDENCY_CERTIFICATE',response_weights={mode:{out:list(map(str,vals)) for out,vals in row.items()} for mode,row in weights.items()},candidates=candidates,selected=selected,constants_exact={mode:{k:str(v) for k,v in row.items()} for mode,row in constants.items()},effects_exact={mode:{k:str(v) for k,v in row.items()} for mode,row in effects.items()},source_budgets=budgets,active_K_branches=branches,gates=gates,seconds=time.monotonic()-started,ode_solves=0)
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps(dict(seconds=result['seconds'],gates=len(gates),candidates={mode:len(rows) for mode,rows in candidates.items()},display={mode:{k:float(v[k]) for k in ('physical_radius','clock_eta','seed')} for mode,v in constants.items()},gains={mode:{k:float(v) for k,v in row.items()} for mode,row in effects.items()},selection={mode:{k:v[k] for k in ('a','exponent','graph_weight','oscillator_weight')} for mode,v in selected.items()},branches={mode:dict(active=v['active'],mass_over_inverse_a=float(Q(v['mass_over_inverse_a'])),relative_masses=[float(Q(x)) for x in v['relative_masses']]) for mode,v in branches.items()})),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(time.time()<1793074031,'FIXED_WINDOW_CUTOFF');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(frozen)['files'][str(lp)],'LEASE_PIN')
        newlp=BASE/'20261027_SHARED_ADMISSION/lease.py'
        need(sha(newlp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','SHARED_LEASE_PIN')
        lease=load('component_lease',newlp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        need(time.time()<1793074031,'POST_LEASE_LAUNCH_CUTOFF')
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('COMPONENT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
