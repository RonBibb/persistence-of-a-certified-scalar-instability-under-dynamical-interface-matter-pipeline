"""Exact real-inverse harmonic provenance and complex coefficient budget."""
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
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    parent=BASE/'20261026_ROUTED_SOURCE_BUDGET_R1'
    bind(parent/'TERMINAL.json','e2900f154161575f86dcf44fbac623f308cc93877aa685b194e8f4d8afd22bb1');t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('CONTRACT.txt','contract_sha256')]:bind(parent/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
    inverse=BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json'
    analytic=BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json'
    for p in (inverse,analytic):gate(inputs.get(str(p))==sha(p),'ANCESTRY:'+p.parent.name)
    ir=read(inverse);iv={k:Q(v) for k,v in read(analytic)['constants_exact'].items()}
    gate(ir['scientific_certificate'],'REAL_AUTHORITY')
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','CONTRACT.txt')}
    len(str(10**20000));runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
    reports={};old=[];cv=[];cg=[]
    for engine,arm in ir['arms'].items():
        path=BASE/'20261026_GROWING_INVERSE_READINESS_R1'/('INITIAL_'+engine+'.json')
        gate(inputs.get(str(path))==sha(path),'INITIAL:'+engine);L=Q(read(path)['D'][0])
        ext={k:Q(v) for k,v in arm['extrema'].items()};N=arm['N'];H=ext['H'];ratio=ext['E2hi']/ext['E2lo']
        c,A,v,lam=map(Q,(arm['c'],arm['A'],arm['v'],arm['lambda']))
        C0=max(1/c,4/lam);C1=((2+v/2)*C0+Q(1,2))/(1-A/(2*N));C2=A*C1/N+v*C0+1
        gate({k:str(v) for k,v in dict(value=C0,first=C1,second=C2,sum=C0+C1+C2).items()}==arm['high_constants'],'HIGH_REPLAY:'+engine)
        rows={'high_n_ge_'+str(N):dict(value=C0,first=C1,second=C2,sum=C0+C1+C2,f_value=ratio*C0,f_gradient=ratio*(C1+2*H*C0/N))}
        gate(set(arm['finite_orders'])=={str(n) for n in range(2,N)},'ALL_HARMONICS:'+engine)
        for n in range(2,N):
            rec=arm['finite_orders'][str(n)];V,U,drift,beta=map(Q,rec['bounds']);ell=min(L/2,1/(drift+1));den=1-drift*ell/2
            gate(V>0 and beta>0 and ell>0 and den>0,'LOW_ADMISSION:'+engine+':'+str(n))
            c0=max(1/V,1/(n*beta));c1=((2/ell+ell*U/2)*c0+ell/2)/den;c2=drift*c1+U*c0+1
            val=n*n*c0;grad=n*c1;total=val+grad+c2
            gate(total==Q(rec['constant']),'FINITE_REPLAY:'+engine+':'+str(n))
            rows[str(n)]=dict(value=val,first=grad,second=c2,sum=total,f_value=ratio*val,f_gradient=ratio*(grad+2*H*n*c0))
        Cy=max(row['sum'] for row in rows.values());mult=max(1+H+H*H+ext['Hp']/2,1+2*H,Q(1));Cf=ratio*mult*Cy
        gate(Cy==Q(arm['C_y']) and Cf==Q(arm['C_f']) and ratio*mult==Q(arm['f_transfer_multiplier']),'OLD_TRANSFER_REPLAY:'+engine)
        value=max(row['f_value'] for row in rows.values());gradient=max(row['f_gradient'] for row in rows.values())
        gate(0<value<=Cf and 0<gradient<=Cf,'COMPONENT_DOMINATION:'+engine)
        controls={key:[k for k,row in rows.items() if row[key]==max(r[key] for r in rows.values())] for key in ('sum','f_value','f_gradient')}
        reports[engine]=dict(N=N,controls=controls,rows={k:{n:str(v) for n,v in row.items()} for k,row in rows.items()},old_Cf=str(Cf),E2_ratio=str(ratio),transfer_multiplier=str(mult),real_value=str(value),real_gradient=str(gradient),value_gain=str(Cf/value),gradient_gain=str(Cf/gradient))
        old.append(Cf);cv.append(value);cg.append(gradient)
    gate(max(old)==iv['C0'],'COMMON_C0_REPLAY')
    dc=iv['complex_D_normalized_lower'];ap=dict(direct=Q(12),denominator_ratio=Q(160)/(4*dc));bp=dict(mass=Q(1,4),temporal=Q(5,2048)*289,scalar=Q(2),denominator_ratio=Q(80*26)/(16*dc))
    gate(sum(ap.values())==iv['A'] and sum(bp.values())==iv['B'],'AB_REPLAY')
    common=dict(old_C0=iv['C0'],real_value=max(cv),real_gradient=max(cg),value_gain=iv['C0']/max(cv),gradient_gain=iv['C0']/max(cg))
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST:'+p)
    result=dict(pass_status=True,classification='INVERSE_CONSTANT_PROVENANCE_DIAGNOSTIC',arms=reports,common={k:str(v) for k,v in common.items()},A_terms={k:str(v) for k,v in ap.items()},B_terms={k:str(v) for k,v in bp.items()},A_shares={k:str(v/iv['A']) for k,v in ap.items()},B_shares={k:str(v/iv['B']) for k,v in bp.items()},gates=gates,seconds=time.monotonic()-started,new_ode_solves=0,new_convergence_certificate=False,scope='Saved aggregate inverse replay and component transfer diagnostic. No cell extrema locations inferred; no claim of physical amplification or realized full-map gain.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,source_sha256=sha(__file__),result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),contract_sha256=sha(ROOT/'CONTRACT.txt')))
    print(json.dumps(dict(seconds=result['seconds'],gates=len(gates),common={k:float(v) for k,v in common.items()},controls={k:v['controls'] for k,v in reports.items()},A_shares={k:float(v/iv['A']) for k,v in ap.items()},B_shares={k:float(v/iv['B']) for k,v in bp.items()})),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        f=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';need(sha(f)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(f)['files'][str(lp)],'LEASE_PIN')
        lease=load('provenance_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('PROVENANCE_300_SECONDS')));signal.alarm(300)
        put('START.json',dict(cpu=cpu,occupied=occupied,pid=os.getpid(),time=time.time()));main(lease)
    except BaseException as e:
        if not (ROOT/'TERMINAL.json').exists():put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()))
        raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
