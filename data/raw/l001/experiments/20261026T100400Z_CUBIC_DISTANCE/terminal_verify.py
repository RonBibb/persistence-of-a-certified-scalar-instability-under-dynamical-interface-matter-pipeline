"""Leased post-terminal integrity and outward coefficient display; no ODE."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('distance_terminal_runner',ROOT/'runner.py')
r=importlib.util.module_from_spec(s);sys.modules[s.name]=r;s.loader.exec_module(r)
def dec(q,upper):
    q=Q(q)
    if not q:return '0'
    a=abs(q);e=0
    def ten(n):return Q(10**n) if n>=0 else Q(1,10**(-n))
    while a>=ten(e+1):e+=1
    while a<ten(e):e-=1
    unit=ten(e-5);v=q/unit
    n=-((-v.numerator)//v.denominator) if upper else v.numerator//v.denominator
    return str(n)+'e'+str(e-5)
def bounds(v):
    a,b=map(Q,v['exact_bounds']);assert a<=b;return a,b
def show(v):
    a,b=bounds(v);return {'lower':dec(a,False),'upper':dec(b,True),'width_upper':dec(b-a,True)}
def scale(v,c):
    a,b=bounds(v);q=sorted((a*c,b*c));return {'exact_bounds':list(map(str,q))}
def mul(a,b):
    aa=bounds(a);bb=bounds(b);v=[x*y for x in aa for y in bb]
    return {'exact_bounds':[str(min(v)),str(max(v))]}
def scoped(root,name):
    path=(root/name).resolve();assert path.is_relative_to(root.resolve());return path
try:
    assert sys.platform=='linux'
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('DISTANCE_TERMINAL_VERIFY_300')));signal.alarm(300)
    cpu,occupied=r.lease.acquire()
    a=r.read(ROOT/'ADMISSION.json');frozen_sha=r.sha(ROOT/'FROZEN.json')
    assert a['admitted'] is True and a['frozen_sha256']==frozen_sha
    frozen=r.verify();assert len(frozen['files'])==1356
    assert not any(ROOT.glob('*FAILURE.json'))
    terminals={}
    for mode in ('production','audit'):
        t=r.read(ROOT/(mode+'_TERMINAL.json'));terminals[mode]=t
        assert t['pass'] is True and t['frozen_sha256']==frozen_sha
        for name,digest in t['artifacts'].items():assert r.sha(scoped(ROOT,name))==digest
        for suffix in ('RUNTIME_BEFORE','RUNTIME_AFTER'):
            for path,digest in r.read(ROOT/(mode+'_'+suffix+'.json')).items():assert frozen['files'].get(path)==digest and r.sha(path)==digest
    result=r.read(ROOT/'RESULT.json');audit=r.read(ROOT/'AUDIT_RESULT.json')
    assert result['pass'] and audit['pass'] and audit['classification']=='CUBIC_DISTANCE_EXACT_SAVED_BUDGETS_VERIFIED'
    readout={'scope':'Outward six-significant-digit saved exact-rational coefficient readout. No ODE, amplitude, radius or tail estimate. Contributions are correlated and are not independently variable physical causes.','classification':result['classification'],'distance':show(result['distance']),'engines':{},'terminal_seconds':{m:t['seconds'] for m,t in terminals.items()}}
    checked={}
    for name,count in (('primary',8183),('independent',16365)):
        data=r.read(ROOT/('DISTANCE_'+name+'.json'));flow=r.read(r.PARENT/('FLOW_'+name+'.json'))
        assert data['pass'] and data['cells']==count and len(data['chunks'])==len(flow['chunks'])
        previous=None;parent_previous=None;index=0;archive_bytes=0
        for entry,pe in zip(data['chunks'],flow['chunks']):
            bp=scoped(ROOT,entry['file']);pp=scoped(r.PARENT,entry['parent_file'])
            assert entry['parent_file']==pe['file'] and entry['parent_sha256']==pe['sha256']
            assert r.sha(bp)==entry['sha256'] and r.sha(pp)==pe['sha256']
            b=r.read(bp);p=r.read(pp);archive_bytes+=bp.stat().st_size
            assert b['binding_sha256']==frozen_sha and b['engine']==name and b['previous_sha256']==previous
            assert b['parent_chunk']==pe['file'] and b['parent_sha256']==pe['sha256']
            assert p['binding_sha256']==r.EXPECTED and p['engine']==name and p['previous_sha256']==parent_previous
            assert p['parameters_sha256']==flow['parameters_sha256']
            assert entry['first']==pe['first']==p['first']==index
            assert len(b['records'])==len(p['records']) and 1<=len(b['records'])<=32
            for br,pr in zip(b['records'],p['records']):assert br['index']==pr['index']==index;index+=1
            assert entry['last']==pe['last']==p['last']==index-1
            previous=entry['sha256'];parent_previous=pe['sha256']
            del b,p
        assert index==count
        t=data['totals'];A=data['parameters']['A3']
        pieces={'integral_c3':t['c3'],'minus_2_integral_p3P':scale(t['p3P'],-2),'minus_2_A3_integral_p3H':scale(mul(A,t['p3H']),-2),'minus_2_integral_p1c2':scale(t['p1c2'],-2),'plus_4_integral_p1p2':scale(t['p1p2'],4),'minus_four_thirds_integral_p1cubed':scale(t['p1cubed'],Q(-4,3))}
        readout['engines'][name]={'distance':show(data['distance']),'graph':show(data['graph']),'bulk':show(data['bulk']),'endpoint_transport':show(data['transport']),'integrated_transport':show(t['transport']),'direct_bulk':show(t['direct_bulk']),'bulk_contributions':{k:show(v) for k,v in pieces.items()},'seconds':data['seconds'],'peak_rss_kib':data['peak_rss_kib'],'budget_bytes':archive_bytes}
        checked[name]={'cells':index,'chunks':len(data['chunks']),'budget_bytes':archive_bytes}
    r.put('READOUT.json',readout);r.verify()
    r.put('INDEPENDENT_TERMINAL_CHECK.json',{'pass':True,'files_verified':len(frozen['files']),'frozen_sha256':frozen_sha,'cpu':cpu,'occupied_cpus':occupied,'no_failure':True,'runtime_and_artifacts_verified':True,'streamed_budgets_and_parent_chunks_verified':checked,'readout_sha256':r.sha(ROOT/'READOUT.json'),'no_ode':True})
    print(json.dumps({'pass':True,'bindings':len(frozen['files']),'readout':readout}),flush=True)
finally:
    signal.alarm(0)
    for f in r.lease.handles:f.close()
