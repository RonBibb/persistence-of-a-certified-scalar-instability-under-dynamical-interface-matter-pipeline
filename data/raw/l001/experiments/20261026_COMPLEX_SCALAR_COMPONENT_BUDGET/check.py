"""Exact component diagnostic only; no new convergence certificate."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import json, hashlib, importlib.util, time
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
    assert sys.platform=='linux'
    assert not any((ROOT/n).exists() for n in ('RESULT.json','FAILURE.json','START.json'))
    parent=BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT'
    assert sha(parent/'TERMINAL.json')=='d71230e13b956f8b3e7a3469d429a9add68700e3f44d70359eaa99cf4b811173'
    t=read(parent/'TERMINAL.json');assert t['pass_status']
    bindings={str(parent/'TERMINAL.json'):sha(parent/'TERMINAL.json')}
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256')]:
        assert sha(parent/n)==t[k];bindings[str(parent/n)]=t[k]
    for group in ('inputs','sources','runtime'):bindings.update(read(parent/'BINDING.json')[group])
    for p,h in bindings.items():assert sha(p)==h,p
    lease=load('component_lease',BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py');lease.ROOT=ROOT
    util=load('component_util',parent/'check.py');util.ROOT=ROOT
    cpu,occupied=lease.acquire()
    try:
        util.put('START.json',dict(cpu=cpu,occupied=occupied,time=time.time()))
        len(str(10**20000));runtime=lease.observed()
        for p,h in runtime.items():assert bindings.get(p)==h or Path(p)==Path(__file__).resolve(),p
        source=sha(__file__)
        iv={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact'].items()}
        A,B,r,C0=map(iv.get,('A','B','rho','C0'))
        a=C0*(1+r/2)+r*r/4;b=C0+r/2
        u=B*r*r/4;v=A*r*r/8;w=B*r/2;z=A*r/5
        det=(1-u)*(1-z)-v*w
        assert 0<=u<1 and 0<=z<1 and det>0
        x=((1-z)*a+v*b)/det;y=(w*a+(1-u)*b)/det
        zz=B*x+A*y/2+1;total=x+y+zz
        assert x==a+u*x+v*y and y==b+w*x+z*y
        assert x+y<=iv['XY'] and total<=iv['scalar_C']
        old=Q(read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact']['Cscalar'])
        # Scalar-source coefficient in B=3Up+cn+Uf, holding sc/sp/cn fixed.
        cm=Q(11,4)/Q(3,16384);den=1-Q(3,2)*r
        def scalar_bulk(xc,yc,full):
            xp=(cm*C0+r*xc/6)/den
            yp=3*xp+xc/3
            up=2*xp+4*yp+Q(13,6)*xc+yc/3
            return 3*up+full
        inherited=42*(cm*C0+r*old/6)/den+Q(25,2)*old
        assert scalar_bulk(old,old,old)==inherited
        routed=scalar_bulk(x,y,old);tight=scalar_bulk(x,y,total)
        assert 0<tight<=routed<=inherited
        exact=dict(value=x,gradient=y,curvature=zz,total=total,old_full=old,det=det,
                   inherited_bulk_scalar_coefficient=inherited,routed_old_full_coefficient=routed,
                   separated_full_coefficient=tight,routing_gain=inherited/routed,
                   combined_coefficient_gain=inherited/tight,full_norm_gain=old/total,
                   curvature_share=zz/total)
        assert lease.observed()==runtime
        for p,h in bindings.items():assert sha(p)==h,p
        assert sha(__file__)==source
        util.put('BINDING.json',dict(inputs=bindings,runtime=runtime,source_sha256=source))
        util.put('RESULT.json',dict(classification='COMPONENT_COEFFICIENT_DIAGNOSTIC_ONLY',exact={k:str(v) for k,v in exact.items()},display={k:float(v) for k,v in exact.items()},ode_solves=0,new_radius_certified=False,scope='Coefficient comparisons hold other source channels fixed; not full-map gains or physical allocations.'))
        util.put('TERMINAL.json',dict(pass_status=True,source_sha256=source,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json')))
        print(json.dumps(read(ROOT/'RESULT.json')['display']))
    finally:
        for f in lease.handles:f.close()
if __name__=='__main__':main()
