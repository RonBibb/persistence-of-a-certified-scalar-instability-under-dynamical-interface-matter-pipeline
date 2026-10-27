"""Exact attribution of a sealed sufficient bound; no physical-source deletion."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import json,signal,time,hashlib
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
P=BASE/'20261026_FIELD_SPECIFIC_MIXED'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
assert hashlib.sha256((P/'check.py').read_bytes()).hexdigest()=='68416f4a516f219adfb0dcf25c5f061732b9bf5bfb2fadac21940373f9cec5b6'
u=load('budget_parent',P/'check.py')
NAMES=('TRACE','GRAPH','BM','BK','BR','BJ','BO')
def transfer(e,c,cf=Q(1),cm=Q(1),der=Q(1)):
    cn,xn,bm,bk,br,bj,bo=e;rho=c['rho'];d0=Q(3,16384);dc=d0/2
    sp=Q(3,2)*cn+64*bm;sc=18*sp+28*cn+br;sg=2*cn+6*sp+bk
    force=sg+80*sc/(4*dc);rw=cn+Q(39,4)*xn+2*bj+bo/2
    g=(Q(1,2)+1/(4*d0))*rw+sc/d0;uf=cf*c['Cscalar']*(force+g)
    xp=(cm*Q(11,4)/d0*(sc+uf+sp)+rho*(uf/6+sp/2))/(1-Q(3,2)*rho)
    yp=3*xp+uf/3+sp;up=2*xp+4*yp+Q(5,2)*uf+der*9*sp/rho
    return 3*up+cn+uf
def primitives(w,lam,kap,c,env):
    B=w;X=lam*w;C=kap*w;Y=B+X+C;gap=c['gap'];rho=c['rho']
    J=1/(1-2*X);d=B*(1+4*X*J)
    Z=64+1320*X+37600*X*X+64*(4*X/gap)**3/(1-4*X/gap);v=Z*X/(1-B)**2
    I=(2+v*v)*2*d*X+(Z+2*J*B)*X*X+v*v*X+C*C/(2*(1-B)*(1-v*v))
    ws=4*Y*(1+2*Y)/(1-2*Y)**3;V=3*Y+22*ws*Y/rho
    cn=138*V*V/(1-160*ws/rho-840*ws*ws/rho**2)
    e=env(Y,gap)
    return (cn,8192*I,e['BM'],e['BK'],e['BR'],e['BJ'],e['BO'])
def main(lease):
    started=time.monotonic();inputs={}
    def bind(p,h):u.need(u.sha(p)==h,str(p));inputs[str(p)]=h
    bind(P/'TERMINAL.json','2eba82895e008d93f1ab7d2b7e782f8857632af5a692bcbe81114b066880a500')
    t=u.read(P/'TERMINAL.json')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(P/n,t[k])
    pb=u.read(P/'BINDING.json')
    for group in ('inputs','sources','runtime'):
        for p,h in pb[group].items():bind(p,h)
    bind(ROOT/'CONTRACT.txt',u.sha(ROOT/'CONTRACT.txt'))
    par=load('budget_envelopes',BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py')
    def typed(x,gap):
        out=par.envelopes(x,gap);out['BR']=u.radial_envelope(x,gap);out['BM']=u.mixed_envelope(x,gap);return out
    jet=load('budget_jets',BASE/'20261026_TAIL_FEASIBILITY_ORACLE/check.py').Jet
    source_hash=u.sha(__file__);u.need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():u.need(inputs.get(p)==h or (p==str(Path(__file__).resolve()) and h==source_hash),'RUNTIME:'+p)
    c={k:Q(v) for k,v in u.read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
    sel=u.read(P/'RESULT.json')['selected'];a=Q(sel['a']);lam=Q(sel['graph_weight']);kap=Q(sel['oscillator_weight'])
    vals=primitives(a,lam,kap,c,typed);jets=primitives(jet(0,1),lam,kap,c,typed)
    u.need(transfer(vals,c)==u.response(a,lam,kap,c,typed)[0],'FINITE_RESPONSE')
    u.need(transfer(jets,c).v==u.response(jet(0,1),lam,kap,c,typed)[0].v,'JET_RESPONSE')
    loads=[v-j.v[0]-a*j.v[1] for v,j in zip(vals,jets)]
    u.need(all(v>=0 for v in loads),'POSITIVE_LOADS')
    total=transfer(loads,c);u.need(total==Q(sel['masses'][0]),'SEALED_MASS_EXACT')
    def partition(e):
        corners={k:transfer(e,c,Q(bool(k&1)),Q(bool(k&2)),Q(bool(k&4))) for k in range(8)}
        parts={}
        for k in range(8):
            parts[k]=sum((-1)**(k.bit_count()-j.bit_count())*corners[j] for j in range(8) if j&k==j)
        u.need(sum(parts.values())==corners[7] and all(v>=0 for v in parts.values()),'EXACT_NONNEGATIVE_PARTITION')
        for k in range(8):u.need(sum(parts[j] for j in range(8) if j&k==j)==corners[k],'ALL_CORNERS_RECONSTRUCT')
        return corners,parts
    corners,parts=partition(loads);matrix={}
    for i,name in enumerate(NAMES):
        e=[Q(0)]*7;e[i]=loads[i];_,pp=partition(e);matrix[name]={str(k):str(v) for k,v in pp.items()}
    for k in range(8):u.need(sum(Q(row[str(k)]) for row in matrix.values())==parts[k],'SOURCE_PATH_RECONSTRUCT')
    sensitivities=[]
    for target in ('Cscalar','Cm','derivative_payment'):
        bit={'Cscalar':1,'Cm':2,'derivative_payment':4}[target]
        dependent=sum(v for k,v in parts.items() if k&bit);floor=total-dependent
        u.need(floor>0,'POSITIVE_HYPOTHETICAL_FLOOR')
        for reduction in (2,10,100):
            args=[Q(1),Q(1),Q(1)];args[{'Cscalar':0,'Cm':1,'derivative_payment':2}[target]]=Q(1,reduction)
            new=transfer(loads,c,*args)
            u.need(new==floor+dependent/reduction,'SENSITIVITY_AFFINE_IDENTITY')
            sensitivities.append(dict(target=target,reduction=reduction,mass=str(new),mass_gain=str(total/new)))
    labels={0:'direct',1:'scalar_only',2:'metric_only',3:'scalar_times_metric',4:'explicit_derivative',5:'scalar_times_derivative',6:'metric_times_derivative',7:'triple'}
    rows=[dict(mask=k,path=labels[k],mass=str(parts[k]),share=str(parts[k]/total)) for k in range(8)]
    dependencies={name:dict(share=str(sum(v for k,v in parts.items() if k&bit)/total),zero_constant_floor=str(corners[7^bit]),ideal_mass_gain=str(total/corners[7^bit])) for name,bit in [('Cscalar',1),('Cm',2),('derivative_payment',4)]}
    for p,h in inputs.items():u.need(u.sha(p)==h,'POST:'+p)
    u.need(lease.observed()==runtime and u.sha(__file__)==source_hash,'RUNTIME_SOURCE_DRIFT')
    u.put('BINDING.json',dict(inputs=inputs,runtime=runtime,source_sha256=source_hash))
    result=dict(pass_status=True,classification='SHARED_RESPONSE_PROOF_BUDGET_DIAGNOSTIC',rows=rows,source_path_matrix=matrix,total=str(total),dependencies=dependencies,hypothetical_sensitivities=sensitivities,selected=sel,seconds=time.monotonic()-started,scope='Exact partition of sufficient estimate only. No altered inverse is certified; no radius gains or physical contributions inferred.',ode_solves=0)
    u.put('RESULT.json',result);u.put('TERMINAL.json',dict(pass_status=True,result_sha256=u.sha(ROOT/'RESULT.json'),binding_sha256=u.sha(ROOT/'BINDING.json'),source_sha256=u.sha(__file__)))
    print(json.dumps(dict(seconds=result['seconds'],paths={v['path']:float(Q(v['share'])) for v in rows},dependencies={n:{k:float(Q(v)) for k,v in row.items()} for n,row in dependencies.items()})),flush=True)

if __name__=='__main__':
    lease=None;u.ROOT=ROOT
    try:
        u.need(sys.platform=='linux','LINUX_ONLY');u.need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        f=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';u.need(u.sha(f)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';u.need(u.sha(lp)==u.read(f)['files'][str(lp)],'LEASE')
        lease=load('budget_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('BUDGET_300_SECONDS')));signal.alarm(300)
        u.put('START.json',dict(cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        if not (ROOT/'TERMINAL.json').exists():u.put('FAILURE.json',dict(error=repr(e),classification='TECHNICAL_INCOMPLETE'))
        raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()

