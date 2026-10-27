"""Exact harmonic-matched complex inverse diagnostic."""
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
    parent=BASE/'20261027_SEPARATE_REAL_ANCHOR_CERTIFICATE'
    bind(parent/'TERMINAL.json','30023c49219ef22c3b9ddd7a26fa16c6907b47538094299553a26e2da4cc6251');t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
    provenance=BASE/'20261026_INVERSE_CONSTANT_PROVENANCE/RESULT.json'
    analytic=BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json'
    for p in (provenance,analytic):gate(inputs.get(str(p))==sha(p),'ANCESTRY:'+p.parent.name)
    pr=read(provenance);old=read(parent/'RESULT.json');iv={k:Q(v) for k,v in read(analytic)['constants_exact'].items()}
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','CONTRACT.txt')}
    len(str(10**20000));runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
    r=iv['rho'];dc=iv['complex_D_normalized_lower']
    def coefficients(n):return Q(12)+Q(160)/(dc*n*n),Q(9,n*n)+Q(289*5,2048)+Q(2080)/(dc*n**4)
    gate(coefficients(2)==(iv['A'],iv['B']),'N2_COEFFICIENT_REPLAY')
    def inverse(Cv,Cg,A,B,label):
        a=Cv+r*Cg/2+r*r/4;b=Cg+r/2
        u=B*r*r/4;v=A*r*r/8;w=B*r/2;z=A*r/5;det=(1-u)*(1-z)-v*w
        gate(0<=u<1 and 0<=z<1 and det>0,'POSITIVE:'+label)
        x=((1-z)*a+v*b)/det;y=(w*a+(1-u)*b)/det;zz=B*x+A*y/2+1
        gate(x==a+u*x+v*y and y==b+w*x+z*y,'IDENTITY:'+label)
        return dict(value=x,gradient=y,curvature=zz,total=x+y+zz,det=det)
    Cv=Q(pr['common']['real_value']);Cg=Q(pr['common']['real_gradient'])
    baseline=inverse(Cv,Cg,iv['A'],iv['B'],'BASELINE')
    gate(all(baseline[k]==Q(old['component_constants'][k]) for k in ('value','gradient','total')),'SEALED_COMPONENT_REPLAY')
    gate(Cv==Q(old['real_component_constants']['real_value']) and Cg==Q(old['real_component_constants']['real_gradient']),'REAL_BASELINE_REPLAY')
    rows={}
    gate(set(pr['arms'])=={'primary','independent'},'TWO_ENGINES')
    for engine,arm in pr['arms'].items():
        N=arm['N'];expected={str(n) for n in range(2,N)}|{'high_n_ge_'+str(N)}
        gate(N==65,'FROZEN_CUTOFF:'+engine)
        gate(set(arm['rows'])==expected,'COMPLETE_RANGE:'+engine)
        for label,row in arm['rows'].items():
            n=N if label.startswith('high_n_ge_') else int(label)
            cv=Q(row['f_value']);cg=Q(row['f_gradient']);A,B=coefficients(n)
            key=engine+':'+label
            gate(0<cv<=Cv and 0<cg<=Cg and 0<A<=iv['A'] and 0<B<=iv['B'],'INPUT_DOMINATION:'+key)
            out=inverse(cv,cg,A,B,key)
            gate(all(0<out[k]<=baseline[k] for k in ('value','gradient','curvature','total')),'OUTPUT_DOMINATION:'+key)
            rows[key]=dict(n_lower=n,tail=label.startswith('high_n_ge_'),real_value=cv,real_gradient=cg,A=A,B=B,**out)
    gate(len(rows)==128,'ALL_128_ROWS')
    matched={k:max(v[k] for v in rows.values()) for k in ('value','gradient','curvature','total')}
    controls={k:[label for label,row in rows.items() if row[k]==matched[k]] for k in matched}
    gains={k:baseline[k]/matched[k] for k in matched}
    gate(matched['total']<=matched['value']+matched['gradient']+matched['curvature'],'SUM_VS_MATCHED_SUPREMUM')
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST:'+p)
    result=dict(pass_status=True,classification='HARMONIC_MATCHED_COMPLEX_INVERSE_DIAGNOSTIC',baseline={k:str(v) for k,v in baseline.items()},matched={k:str(v) for k,v in matched.items()},gains={k:str(v) for k,v in gains.items()},controls=controls,rows={label:{k:v if k in ('n_lower','tail') else str(v) for k,v in row.items()} for label,row in rows.items()},gates=gates,seconds=time.monotonic()-started,new_ode_solves=0,new_convergence_certificate=False,scope='Same-collar harmonic-matched sufficient inverse bounds; no nonlinear-map or physical trajectory gain certified.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,source_sha256=sha(__file__),result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),contract_sha256=sha(ROOT/'CONTRACT.txt')))
    print(json.dumps(dict(seconds=result['seconds'],gates=len(gates),rows=len(rows),matched={k:float(v) for k,v in matched.items()},gains={k:float(v) for k,v in gains.items()},controls=controls)),flush=True)
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
