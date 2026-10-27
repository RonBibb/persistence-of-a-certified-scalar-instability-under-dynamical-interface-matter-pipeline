"""Independent saved polynomial certificate and Robin load assembly audit."""
import json,sys,importlib.util
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parent
def need(v,label):
    if not v:raise AssertionError(label)
def poly(rows):return {tuple(x['powers']):F(x['coefficient']) for x in rows if F(x['coefficient'])}
def add(a,b):
    r=dict(a)
    for k,v in b.items():r[k]=r.get(k,F(0))+v
    return {k:v for k,v in r.items() if v}
def mul(a,b):
    r={}
    for x,u in a.items():
        for y,v in b.items():
            k=tuple(i+j for i,j in zip(x,y));r[k]=r.get(k,F(0))+u*v
    return {k:v for k,v in r.items() if v}
def run():
    need(sys.platform=='linux','LINUX_ONLY')
    r=json.loads((ROOT/'RESULT.json').read_text());need(r['pass'] and r['bulk']['pass'] and r['wall']['pass'],'PRODUCER_PASS')
    b=r['bulk'];reconstruction={}
    need(len(b['compatibility_generators'])==len(b['compatibility_quotients'])==3,'GENERATOR_COUNT')
    for g,q in zip(b['compatibility_generators'],b['compatibility_quotients']):reconstruction=add(reconstruction,mul(poly(g),poly(q)))
    need(not poly(b['compatibility_remainder']),'ZERO_REMAINDER')
    need(reconstruction==poly(b['compatibility_raw']),'EXACT_BIANCHI_CERTIFICATE')
    for sigma,w in r['wall']['orientations'].items():need(not poly(w['Q6_identity']),'EXACT_Q6_CERTIFICATE:'+sigma)
    path=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1/terminal_audit/audit.py'
    s=importlib.util.spec_from_file_location('system_parent_interval',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);I=m.I
    def iv(x):return I(*x['exact_bounds'])
    rebuilt={}
    for engine,records in r['per_engine'].items():
        rebuilt[engine]={}
        for side,sigma in (('lower',1),('upper',-1)):
            rec=records[side];w={k:iv(v) for k,v in rec['inputs'].items()};d=iv(rec['d3']);o=iv(rec['o3']);j=iv(rec['j3'])
            need(d.lo>0,'POSITIVE_OSCILLATOR_DIVISOR')
            load=2*sigma*(w['T']*w['c3']-w['Tp']*w['xi3']-j)+(21-I(1)/d)*w['T']*w['xi3']+o/d
            need(load.overlap(iv(rec['R3'])),'ROBIN_REASSEMBLY:'+engine+side)
            for v in rec['identities'].values():need(iv(v).zero(),'INTERVAL_NEW_ROW_IDENTITIES')
            rebuilt[engine][side]=load.record()
    for side in ('lower','upper'):
        for key in ('o3','j3','d3','R3','Sc3','Sp3','Sg3'):need(iv(r['per_engine']['primary'][side][key]).overlap(iv(r['per_engine']['independent'][side][key])),'ENGINE_OVERLAP:'+side+key)
    return {'pass':True,'classification':'CUBIC_SYSTEM_CERTIFICATES_AND_LOAD_ASSEMBLY_VERIFIED','rebuilt_R3':rebuilt,'scope':'Independent saved polynomial multiplier identity and exact Fraction Robin assembly. Does not independently rerun full source extraction or parent ODE.'}
