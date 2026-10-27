"""Exact disjoint source/path budget of the component-routed bulk bound."""
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
    t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,ROOT/n);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
NAMES=('TRACE','GRAPH','BM','BK','BR','BJ','BO')
def primitives(w,lam,kap,c,env):
    B=w;X=lam*w;C=kap*w;Y=B+X+C;gap=c['gap'];rho=c['rho']
    J=1/(1-2*X);d=B*(1+4*X*J)
    Z=64+1320*X+37600*X*X+64*(4*X/gap)**3/(1-4*X/gap);v=Z*X/(1-B)**2
    I=(2+v*v)*2*d*X+(Z+2*J*B)*X*X+v*v*X+C*C/(2*(1-B)*(1-v*v))
    ws=4*Y*(1+2*Y)/(1-2*Y)**3;V=3*Y+22*ws*Y/rho
    cn=138*V*V/(1-160*ws/rho-840*ws*ws/rho**2)
    e=env(Y,gap)
    return (cn,8192*I,e['BM'],e['BK'],e['BR'],e['BJ'],e['BO'])
def paths(e,c,iv):
    cn,xn,bm,bk,br,bj,bo=e;r=c['rho'];d0=Q(3,16384);dc=d0/2
    sp=Q(3,2)*cn+64*bm;sc=18*sp+28*cn+br;sg=2*cn+6*sp+bk
    force=sg+80*sc/(4*dc);rw=cn+Q(39,4)*xn+2*bj+bo/2
    S=force+(Q(1,2)+1/(4*d0))*rw+sc/d0
    x=c['value'];y=c['gradient'];Cm=Q(11,4)/d0;den=1-Q(3,2)*r
    return dict(metric_real_scalar=42*Cm*c['C0']*S/den,
      metric_real_sources=42*Cm*(sc+sp)/den,
      metric_continuation_scalar=7*r*x*S/den,
      metric_continuation_source=21*r*sp/den,
      metric_value=Q(21,2)*x*S,metric_gradient=y*S,
      metric_source=12*sp,metric_source_derivative=27*sp/r,
      trace_direct=cn,scalar_value=x*S,scalar_gradient=y*S,
      scalar_curvature_potential=iv['B']*x*S,
      scalar_curvature_gradient=iv['A']*y*S/2,
      scalar_curvature_source=S)
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    parent=BASE/'20261026_COMPONENT_ROUTED_CERTIFICATE'
    bind(parent/'TERMINAL.json','4faee2fc89db5df2148a02d3395ca2a5e8d8bbe3ddb534f9f9c127a6b4b53efb')
    t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
    p=load('routed_parent',parent/'check.py');ep=load('routed_endpoint',BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/check.py')
    joint=load('routed_joint',BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py');Jet=load('routed_jets',BASE/'20261026_TAIL_FEASIBILITY_ORACLE/check.py').Jet
    def env(x,gap):
        e=joint.envelopes(x,gap);e['BR']=ep.radial_envelope(x,gap);e['BM']=ep.mixed_envelope(x,gap);return e
    rec=read(parent/'RESULT.json');sel=rec['selected'];a=Q(sel['a']);lam=Q(sel['graph_weight']);kap=Q(sel['oscillator_weight'])
    c={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
    iv={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact'].items()}
    c.update({k:Q(v) for k,v in rec['component_constants'].items()});c['C0']=iv['C0']
    gate(c['total']==c['value']+c['gradient']+iv['B']*c['value']+iv['A']*c['gradient']/2+1,'CURVATURE_SPLIT')
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','CONTRACT.txt')}
    len(str(10**20000));runtime=lease.observed()
    for name,h in runtime.items():need(inputs.get(name)==h or sources.get(name)==h,'RUNTIME:'+name)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
    vals=primitives(a,lam,kap,c,env);jets=primitives(Jet(0,1),lam,kap,c,env)
    gate(sum(paths(vals,c,iv).values())==p.response(a,lam,kap,c,env)[0],'FINITE_RESPONSE_REPLAY')
    gate(sum(paths(jets,c,iv).values()).v==p.response(Jet(0,1),lam,kap,c,env)[0].v,'JET_RESPONSE_REPLAY')
    loads=[v-j.v[0]-a*j.v[1] for v,j in zip(vals,jets)]
    gate(all(v>=0 for v in loads),'NONNEGATIVE_LOADS')
    columns=paths(loads,c,iv);total=sum(columns.values());gate(total==Q(sel['masses'][0]),'SEALED_BULK_MASS')
    matrix={};rows={};coeff={}
    for i,name in enumerate(NAMES):
        basis=[Q(0)]*7;basis[i]=Q(1);coeff[name]=sum(paths(basis,c,iv).values());basis[i]=loads[i]
        matrix[name]=paths(basis,c,iv);rows[name]=sum(matrix[name].values())
        gate(rows[name]==coeff[name]*loads[i],'SOURCE_LINEAR:'+name)
    gate(all(v>=0 for row in matrix.values() for v in row.values()),'NONNEGATIVE_MATRIX')
    for name in columns:gate(sum(row[name] for row in matrix.values())==columns[name],'COLUMN:'+name)
    gate(sum(rows.values())==total,'GRAND_TOTAL')
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for name,h in dict(inputs,**sources).items():need(sha(name)==h,'POST_BINDING:'+name)
    result=dict(pass_status=True,classification='ROUTED_SUFFICIENT_BOUND_SOURCE_PATH_BUDGET',selected=sel,total=str(total),loads=dict(zip(NAMES,map(str,loads))),transfer_coefficients={k:str(v) for k,v in coeff.items()},source_masses={k:str(v) for k,v in rows.items()},source_shares={k:str(v/total) for k,v in rows.items()},path_masses={k:str(v) for k,v in columns.items()},path_shares={k:str(v/total) for k,v in columns.items()},source_path_matrix={k:{n:str(v) for n,v in row.items()} for k,row in matrix.items()},gates=gates,seconds=time.monotonic()-started,ode_solves=0,new_certificate=False,scope='Exact attribution of a sufficient proof bound, not physical contributions or realizable gains.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,source_sha256=sha(__file__),result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),contract_sha256=sha(ROOT/'CONTRACT.txt')))
    print(json.dumps(dict(seconds=result['seconds'],gates=len(gates),source_shares={k:float(v/total) for k,v in rows.items()},path_shares={k:float(v/total) for k,v in columns.items()})),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(not any((ROOT/n).exists() for n in ('START.json','TERMINAL.json','FAILURE.json')),'NO_RESTART')
        frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(frozen)['files'][str(lp)],'LEASE_PIN')
        lease=load('routed_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ROUTED_BUDGET_300_SECONDS')));signal.alarm(300)
        put('START.json',dict(cpu=cpu,occupied=occupied,pid=os.getpid(),time=time.time()));main(lease)
    except BaseException as e:
        if not (ROOT/'TERMINAL.json').exists():put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()))
        raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
