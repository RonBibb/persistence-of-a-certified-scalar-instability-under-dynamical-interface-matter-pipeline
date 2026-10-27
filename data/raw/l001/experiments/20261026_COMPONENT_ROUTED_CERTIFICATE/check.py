"""Paired full certificates with component-routed scalar estimates."""
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
def response(w,lam,kap,c,env):
    B=w;X=lam*w;C=kap*w;Y=B+X+C;rho=c['rho'];gap=c['gap'];d0=Q(3,16384);dc=d0/2
    J=1/(1-2*X);W=4*X*J;d=B*(1+W)
    Z=64+1320*X+37600*X*X+64*(4*X/gap)**3/(1-4*X/gap);v=Z*X/(1-B)**2
    I=(2+v*v)*2*d*X+(Z+2*J*B)*X*X+v*v*X+C*C/(2*(1-B)*(1-v*v))
    ws=4*Y*(1+2*Y)/(1-2*Y)**3;V=3*Y+22*ws*Y/rho
    cn=138*V*V/(1-160*ws/rho-840*ws*ws/rho**2)
    e=env(Y,gap);xn=8192*I;sp=Q(3,2)*cn+64*e['BM'];sc=18*sp+28*cn+e['BR'];sg=2*cn+6*sp+e['BK']
    force=sg+80*sc/(4*dc);rw=cn+Q(39,4)*xn+2*e['BJ']+e['BO']/2;g=(Q(1,2)+1/(4*d0))*rw+sc/d0
    S=force+g;uf=c['total']*S;ux=c['value']*S;uy=c['gradient']*S;ureal=c['C0']*S;Cm=Q(11,4)/d0
    xp=(Cm*(sc+ureal+sp)+rho*(ux/6+sp/2))/(1-Q(3,2)*rho)
    yp=3*xp+ux/3+sp;up=2*xp+4*yp+Q(13,6)*ux+uy/3+9*sp/rho
    return (3*up+cn+uf,xn,32768*(ureal/2+xn/4+e['BO']))
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    parent=BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT';diag=BASE/'20261026_COMPLEX_SCALAR_COMPONENT_BUDGET'
    for folder,pin in ((parent,'d71230e13b956f8b3e7a3469d429a9add68700e3f44d70359eaa99cf4b811173'),(diag,'9f5a068f775ab8389b2b4cd11d153ad0b26e17389355320961765995a43ec208')):
        bind(folder/'TERMINAL.json',pin);t=read(folder/'TERMINAL.json');gate(t['pass_status'],'PASS:'+folder.name)
        for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256')]:bind(folder/n,t[k])
        b=read(folder/'BINDING.json')
        for group in ('inputs','sources','runtime'):
            for p,h in b.get(group,{}).items():bind(p,h)
    par=load('component_parent',parent/'check.py')
    jet=load('component_jet',BASE/'20261026_TAIL_FEASIBILITY_ORACLE/check.py')
    joint=load('component_joint',BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py')
    def env(x,gap):
        e=joint.envelopes(x,gap);e['BR']=par.radial_envelope(x,gap);e['BM']=par.mixed_envelope(x,gap);return e
    c={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
    iv={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact'].items()}
    c['C0']=iv['C0'];r=iv['rho'];A=iv['A'];B=iv['B'];C0=iv['C0']
    a=C0*(1+r/2)+r*r/4;b=C0+r/2;u=B*r*r/4;v=A*r*r/8;w=B*r/2;z=A*r/5;det=(1-u)*(1-z)-v*w
    gate(0<=u<1 and 0<=z<1 and det>0,'POSITIVE_INVERSE')
    x=((1-z)*a+v*b)/det;y=(w*a+(1-u)*b)/det;zz=B*x+A*y/2+1
    gate(x==a+u*x+v*y and y==b+w*x+z*y,'INVERSE_IDENTITIES')
    c.update(value=x,gradient=y,total=x+y+zz)
    d=read(diag/'RESULT.json')['exact']
    gate(all(c[k]==Q(d[k]) for k in ('value','gradient','total')),'DIAGNOSTIC_REPLAY')
    gate(x+y<=iv['XY'] and c['total']<=iv['scalar_C']<=c['Cscalar'],'DOMINATION')
    gate(r==c['rho'],'SAME_COLLAR')
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
    len(str(10**20000));runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
    cfg=read(parent/'CONTRACT.json');old=read(parent/'RESULT.json');rows=[];prows=[]
    for lam in map(Q,cfg['graph_weights']):
        for kap in map(Q,cfg['oscillator_weights']):
            jets=response(jet.Jet(0,1),lam,kap,c,env);pj=par.response(jet.Jet(0,1),lam,kap,c,env)
            gate(jets[1].v==pj[1].v and jets[2].v==pj[2].v,'XC_JETS:'+str((lam,kap)))
            for exponent in cfg['evaluation_exponents']:
                aa=Q(1,2**exponent);row=dict(graph_weight=str(lam),oscillator_weight=str(kap),exponent=exponent,a=str(aa))
                gate(par.domain(aa,lam,kap,c),'DOMAIN:'+str(len(rows)))
                vv=response(aa,lam,kap,c,env);pv=par.response(aa,lam,kap,c,env)
                masses=[(f-j.v[0]-aa*j.v[1])/s for f,j,s in zip(vv,jets,(Q(1),lam,kap))]
                pm=[(f-j.v[0]-aa*j.v[1])/s for f,j,s in zip(pv,pj,(Q(1),lam,kap))]
                gate(all(q>=0 for q in masses) and masses[0]<=pm[0] and masses[1:]==pm[1:],'PAIRED_MASSES:'+str(len(rows)))
                def entry(m):return dict(row,admitted=True,masses=list(map(str,m)),K=str(par.ceil(max(Q(1),1/aa,2*max(m)/aa**2))))
                rows.append(entry(masses));prows.append(entry(pm))
    gate(prows==old['candidates'],'ALL_81_PARENT_ROWS_EXACT')
    best=min(rows,key=lambda v:Q(v['K']));pbest=min(prows,key=lambda v:Q(v['K']))
    gate(pbest==old['selected'],'PARENT_SELECTION')
    def certify(chosen,label):
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
        return dict(C0=c['C0'],Cscalar=c['Cscalar'] if label=='PARENT' else c['total'],K=K,seed=seed,R=R,aggregate_bound=Y,physical_radius=radius,clock_eta=eta,observable_sup=MD,clock_sup=MF,clock_tail=tail,known_cubic=known,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000)
    pe=certify(pbest,'PARENT');ne=certify(best,'ROUTED')
    gate({k:str(v) for k,v in pe.items()}==old['constants_exact'],'ALL_PARENT_CERTIFICATE_CONSTANTS')
    def branch(row):
        aa=Q(row['a']);m=list(map(Q,row['masses']));terms=dict(one=Q(1),inverse_a=1/aa,mass=2*max(m)/aa**2);top=max(terms.values())
        return dict(active=[k for k,v in terms.items() if v==top],mass_over_inverse_a=str(terms['mass']*aa),relative_masses=[str(v/max(m)) for v in m])
    effects={k:ne[k]/pe[k] for k in ('physical_radius','clock_eta')}
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
    result=dict(classification='PAIRED_COMPONENT_ROUTED_LOCAL_CERTIFICATES',pass_status=True,selected=best,parent_selected=pbest,candidates=rows,parent_candidates=prows,constants_exact={k:str(v) for k,v in ne.items()},component_constants={k:str(c[k]) for k in ('value','gradient','total')},parent_constants_exact={k:str(v) for k,v in pe.items()},effects_exact={k:str(v) for k,v in effects.items()},active_K_branches=dict(parent=branch(pbest),routed=branch(best)),gates=gates,seconds=time.monotonic()-started,ode_solves=0)
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,source_sha256=sha(__file__),result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps(dict(seconds=result['seconds'],selected={k:best[k] for k in ('graph_weight','oscillator_weight','exponent')},display={k:float(ne[k]) for k in ('physical_radius','clock_eta')},gains={k:float(v) for k,v in effects.items()},gates=len(gates),branches=result['active_K_branches'])))
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(frozen)['files'][str(lp)],'LEASE_PIN')
        lease=load('component_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('COMPONENT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
