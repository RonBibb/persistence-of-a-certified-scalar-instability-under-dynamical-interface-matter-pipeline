"""Three-lane exact metric anchor and harmonic continuation certificates."""
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
    seed=max(Q(cfg['bulk_seed_bound']),Q(cfg['summed_wall_seed_bound'])/kap);g(seed==16444,'SEED')
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
NAMES=('TRACE','GRAPH','BM','BK','BR','BJ','BO')
def transfer(e,c,row,mode):
    cn,xn,bm,bk,br,bj,bo=e;r=c['rho'];d0=Q(3,16384);dc=d0/2;n=Q(row['n_lower'])
    sp=3*cn/n+64*bm;sc=36*sp/n+112*cn/(n*n)+br
    sg=(2/n+4/(n*n))*cn+12*sp/n+bk
    force=sg+80*sc/(dc*n*n);rw=2*cn/n+39*xn/(n*n)+2*bj+bo/2
    S=force+(Q(1,2)+1/(d0*n*n))*rw+2*sc/(d0*n)
    x=Q(row['value']);y=Q(row['gradient']);full=Q(row['total'])
    cv=Q(row['real_value']);cg=Q(row['real_gradient']);mp=cg/n+9*cv/(n*n);op=cv/n
    anchor=(sc+mp*S)/d0
    nn=Q(2) if mode=='anchor' else n
    xp=(anchor+r*(x*S/(3*nn)+sp/2))/(1-3*r/nn)
    yp=6*xp/nn+2*x*S/(3*nn)+sp
    up=(1+4/(nn*nn))*xp+(1+6/nn)*yp+26*x*S/(3*nn*nn)+2*y*S/(3*nn)+(6+6/nn)*sp/r
    return (3*up+cn+full*S,32768*(op*S+xn/4+bo))
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    parent=BASE/'20261027_JOINT_SOURCE_CERTIFICATE'
    bind(parent/'TERMINAL.json','5e3e0216a2322a111c1eb00db471076340b6c5dc51b65b26f7fa219382015652')
    t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
    helper=BASE/'20261026_ROUTED_SOURCE_BUDGET_R1/check.py'
    gate(inputs.get(str(helper))==sha(helper),'PRIMITIVE_HELPER_AUTHENTICATED')
    par=load('joint_parent',parent/'check.py')
    ep=load('joint_endpoint',BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/check.py')
    prim=load('joint_primitives',helper).primitives
    Jet=load('joint_jets',BASE/'20261026_TAIL_FEASIBILITY_ORACLE/check.py').Jet
    envmod=load('joint_env',BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py')
    def env(x,gap):
        e=envmod.envelopes(x,gap);e['BR']=ep.radial_envelope(x,gap);e['BM']=ep.mixed_envelope(x,gap);return e
    old=read(parent/'RESULT.json');c={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
    ancestor=BASE/'20261027_REAL_PAYMENT_MATCHED_CERTIFICATE/RESULT.json'
    gate(inputs.get(str(ancestor))==sha(ancestor),'COMPONENT_ANCESTOR')
    ac=read(ancestor);c['C0']=Q(ac['constants_exact']['C0'])
    for group in ('component_constants','real_component_constants','payment_constants'):c.update({k:Q(v) for k,v in ac[group].items()})
    diagpath=BASE/'20261027_HARMONIC_MATCHED_INVERSE/RESULT.json'
    gate(inputs.get(str(diagpath))==sha(diagpath),'HARMONIC_INPUT')
    hrows=read(diagpath)['rows']
    expected={e+':'+str(n) for e in ('primary','independent') for n in range(2,65)}|{e+':high_n_ge_65' for e in ('primary','independent')}
    gate(set(hrows)==expected,'ALL128_HARMONIC_RANGES')
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
    auth=BASE/'20261027T020711Z_TWO_HOUR_CONTINUATION/AUTHORITY.txt';bind(auth,sha(auth))
    len(str(10**20000));runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=1793074031))
    weights={m:{out:[] for out in ('B','C')} for m in ('baseline','anchor','metric')};controls={};raw={}
    for i,name in enumerate(NAMES):
        e=[Q(0)]*7;e[i]=Q(1);baseline=[Q(old['weights']['joint'][out][i]) for out in ('B','C')]
        for j,out in enumerate(('B','C')):weights['baseline'][out].append(baseline[j])
        for mode in ('anchor','metric'):
            entries={}
            for label,row in hrows.items():
                gate(row['n_lower']==(65 if row['tail'] else int(label.split(':')[-1])),'HARMONIC_LABEL:'+label)
                vals=transfer(e,c,row,mode);entries[label]=vals
                gate(all(0<=v<=p for v,p in zip(vals,baseline)),'COEFFICIENT_DOMINATION:'+mode+':'+name+':'+label)
            raw[mode+':'+name]={k:[str(v) for v in vals] for k,vals in entries.items()}
            for j,out in enumerate(('B','C')):
                top=max(v[j] for v in entries.values());weights[mode][out].append(top)
                controls[mode+':'+out+':'+name]=[k for k,v in entries.items() if v[j]==top]
    gate(all(weights['metric'][out][i]<=weights['anchor'][out][i]<=weights['baseline'][out][i] for out in ('B','C') for i in range(7)),'LANE_COEFFICIENT_ORDER')
    cfg=read(BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/CONTRACT.json')
    candidates={m:[] for m in weights}
    for lam in map(Q,cfg['graph_weights']):
        for kap in map(Q,cfg['oscillator_weights']):
            pj=prim(Jet(0,1),lam,kap,c,env)
            for exponent in cfg['evaluation_exponents']:
                a=Q(1,2**exponent);gate(ep.domain(a,lam,kap,c),'DOMAIN:'+str((lam,kap,exponent)))
                pv=prim(a,lam,kap,c,env);loads=[v-j.v[0]-a*j.v[1] for v,j in zip(pv,pj)]
                gate(all(v>=0 for v in loads),'POSITIVE_LOADS:'+str((lam,kap,exponent)))
                for mode,w in weights.items():
                    m=[sum(k*v for k,v in zip(w['B'],loads)),loads[1]/lam,sum(k*v for k,v in zip(w['C'],loads))/kap]
                    K=Q(ep.ceil(max(Q(1),1/a,2*max(m)/a**2)))
                    rec=dict(graph_weight=str(lam),oscillator_weight=str(kap),exponent=exponent,a=str(a),admitted=True,masses=list(map(str,m)),K=str(K))
                    candidates[mode].append(rec)
    gate(candidates['baseline']==old['candidates']['joint'],'ALL81_PARENT_ROWS_EXACT')
    selected={mode:min(rows,key=lambda v:Q(v['K'])) for mode,rows in candidates.items()}
    constants={mode:certify(row,mode,c,cfg,gate) for mode,row in selected.items()}
    gate({k:str(v) for k,v in constants['baseline'].items()}==old['constants_exact']['joint'],'FULL_PARENT_CONSTANTS')
    effects={mode:{k:constants[mode][k]/constants['baseline'][k] for k in ('physical_radius','clock_eta')} for mode in ('anchor','metric')}
    budgets={};branches={}
    for mode,row in selected.items():
        a=Q(row['a']);lam=Q(row['graph_weight']);kap=Q(row['oscillator_weight'])
        pv=prim(a,lam,kap,c,env);pj=prim(Jet(0,1),lam,kap,c,env);loads=[v-j.v[0]-a*j.v[1] for v,j in zip(pv,pj)]
        budgets[mode]={out:{name:str(k*v) for name,k,v in zip(NAMES,weights[mode][out],loads)} for out in ('B','C')}
        m=list(map(Q,row['masses']));terms=dict(one=Q(1),inverse_a=1/a,mass=2*max(m)/a**2);top=max(terms.values())
        gate(sum(map(Q,budgets[mode]['B'].values()))==m[0],'BUDGET_B:'+mode)
        gate(sum(map(Q,budgets[mode]['C'].values()))/kap==m[2],'BUDGET_C_UNSCALED:'+mode)
        branches[mode]=dict(active=[k for k,v in terms.items() if v==top],mass_over_inverse_a=str(terms['mass']*a),relative_masses=[str(v/max(m)) for v in m])
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST:'+p)
    result=dict(pass_status=True,classification='MATCHED_METRIC_FULL_CERTIFICATES',selected=selected,candidates=candidates,constants_exact={m:{k:str(v) for k,v in row.items()} for m,row in constants.items()},effects_exact={m:{k:str(v) for k,v in row.items()} for m,row in effects.items()},weights={m:{k:list(map(str,v)) for k,v in row.items()} for m,row in weights.items()},controls=controls,harmonic_coefficients=raw,source_budgets=budgets,active_K_branches=branches,gates=gates,seconds=time.monotonic()-started,ode_solves=0)
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps(dict(seconds=result['seconds'],gates=len(gates),display={m:{k:float(v[k]) for k in ('physical_radius','clock_eta')} for m,v in constants.items()},gains={m:{k:float(v) for k,v in row.items()} for m,row in effects.items()},selection={m:{k:v[k] for k in ('exponent','graph_weight','oscillator_weight')} for m,v in selected.items()},branches={m:dict(active=v['active'],mass_over_inverse_a=float(Q(v['mass_over_inverse_a'])),relative_masses=[float(Q(x)) for x in v['relative_masses']]) for m,v in branches.items()})),flush=True)
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
