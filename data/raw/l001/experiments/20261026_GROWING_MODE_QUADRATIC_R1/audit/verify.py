"""Independent exact saved-record audit. Linux only; no ODE replay.

Usage: python -I -B audit/verify.py EXPECTED_PRODUCTION_TERMINAL_SHA256
The caller pins the completed terminal before this auditor is executed.
Containment means the saved outward interval encloses the reconstructed
exact interval; overlap is separately named and never called containment.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PACKET=ROOT.parent
BASE=PACKET.parent
PARENT=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION'
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'

def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
    p=ROOT/name;t=ROOT/(name+'.tmp')
    with t.open('x') as f: json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

class I:
    def __init__(self,lo,hi=None):
        self.lo=Q(lo);self.hi=Q(lo if hi is None else hi)
        assert self.lo<=self.hi,'INTERVAL_ORDER'
    @staticmethod
    def cast(x): return x if isinstance(x,I) else I(x)
    def __add__(self,x):
        x=self.cast(x);return I(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,x):return self+-self.cast(x)
    def __rsub__(self,x):return self.cast(x)+-self
    def __mul__(self,x):
        x=self.cast(x);v=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)]
        return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=self.cast(x);assert not x.zero(),'DIVISOR_CONTAINS_ZERO'
        return self*I(1/x.hi,1/x.lo)
    def __rtruediv__(self,x):return self.cast(x)/self
    def zero(self):return self.lo<=0<=self.hi
    def contains(self,x):return self.lo<=x.lo<=x.hi<=self.hi
    def overlaps(self,x):return self.lo<=x.hi and x.lo<=self.hi
    def hull(self,x):return I(min(self.lo,x.lo),max(self.hi,x.hi))
    def pack(self):return {'exact_bounds':[str(self.lo),str(self.hi)]}
def iv(x):return I(*x['exact_bounds'])
def decimal_outward(x,places=12):
    scale=10**places
    def text(n):
        sign='-' if n<0 else '';digits=str(abs(n)).zfill(places+1)
        return sign+digits[:-places]+'.'+digits[-places:]
    lo=(x.lo*scale).__floor__();hi=(x.hi*scale).__ceil__()
    return [text(lo),text(hi)]

def run(lease,expected_terminal):
    assert sys.platform=='linux','LINUX_ONLY'
    assert not any((ROOT/n).exists() for n in ('AUDIT_START.json','AUDIT_RESULT.json','AUDIT_FAILURE.json')),'NO_RESTART'
    cpu,occupied=lease.acquire();signal.alarm(240)
    put('AUDIT_START.json',{'cpu':cpu,'occupied':occupied})
    termpath=PACKET/'production_TERMINAL.json'
    assert sha(termpath)==expected_terminal,'TERMINAL_PIN'
    term=read(termpath)
    assert all(term.get(k) is True for k in ('pass','runtime_unchanged','source_unchanged','parent_unchanged'))
    inputs={str(termpath):expected_terminal,str(Path(__file__)):sha(__file__)}
    for name,digest in term['artifacts'].items():
        p=PACKET/name;assert sha(p)==digest,'ARTIFACT_HASH:'+name;inputs[str(p)]=digest
    required=('production_BINDING.json','controls_BINDING.json','CONTROLS_RESULT.json','PROBE_RESULT.json',
              'PRODUCTION_primary.json','PRODUCTION_independent.json','RESULT.json','CONTRACT.json')
    assert all(name in term['artifacts'] for name in required),'MISSING_TERMINAL_ARTIFACT'
    assert not list(PACKET.glob('*FAILURE.json')),'FAILED_PACKET'
    binding=read(PACKET/'production_BINDING.json')
    assert binding['sources']==read(PACKET/'controls_BINDING.json')['sources'],'SOURCE_BINDINGS_DISAGREE'
    for p,digest in binding['sources'].items():
        assert sha(p)==digest,'SOURCE_HASH';inputs[p]=digest
    closure=PARENT/'CLOSURE_MANIFEST.json'
    assert sha(closure)==binding['parent_closure_sha256']=='2ab20917e9e8d56fc8c285f10099c1fc1e6cc74836e1ebb51716ab13b8fa0751'
    inputs[str(closure)]=sha(closure)
    for rel,digest in read(closure)['files'].items():
        p=PARENT/rel;assert sha(p)==digest,'PARENT_HASH:'+rel;inputs[str(p)]=digest
    contract=read(PACKET/'CONTRACT.json')
    assert contract['normalization'].startswith('psi1(lower)=1')
    assert 'eta^2' in contract['expansion'] and 'no factorials' in contract['expansion']
    assert read(PACKET/'CONTROLS_RESULT.json')['pass'] and read(PACKET/'PROBE_RESULT.json')['production_admissible']
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    assert sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001
    runtime=lease.observed()
    old=read(BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/FROZEN.json')['files']
    for p,digest in runtime.items():
        assert old.get(p)==digest or inputs.get(p)==digest or (p==str(pylong) and digest==sha(pylong)),'AUDIT_RUNTIME:'+p
    put('AUDIT_BINDING.json',{'inputs':inputs,'runtime':runtime,'expected_production_terminal_sha256':expected_terminal})
    gates={};arms={};finals=[]
    def gate(name,ok):
        gates[name]=bool(ok);assert ok,name
    seedroot=PARENT/'T2R1_AB_SELECTED_MODE'
    seed=read(seedroot/'output/RESULT.json')
    gate('actual_selected_action_seed',seed['classification']=='SELECTED_NEUTRAL_MODE_CHARACTERIZED')
    cfg=read(seedroot/'inputs/central_bindings.json')
    for name in ('primary','independent'):
        record=read(PACKET/('PRODUCTION_'+name+'.json'))
        gate(name+'_production_pass',record['pass'] and record['engine']==name)
        dlo,dhi=map(Q,record['D']);step=Q(1,4096 if name=='primary' else 8192)
        gate(name+'_same_endpoint',record['D']==cfg['config']['D'])
        count=-((-dhi)//step)
        gate(name+'_cell_count',record['cells']==count==len(record['budgets']))
        keys=('p1','p2P','p2H','c2','p1sq')
        sums={k:I(0) for k in keys};ml=Q(0);ol=Q(0)
        for index,row in enumerate(record['budgets']):
            pos=index*step
            gate(f'{name}_cell_{index}',row['index']==index and Q(row['s'])==pos and Q(row['step'])==step)
            mandatory=max(Q(0),min(step,dlo-pos))
            optional=max(Q(0),min(step,dhi-pos))-mandatory
            gate(f'{name}_length_{index}',Q(row['mandatory'])==mandatory and Q(row['optional'])==optional and optional>=0)
            ml+=mandatory;ol+=optional
            gate(f'{name}_budget_keys_{index}',set(row['budgets'])==set(keys))
            for key in keys:
                value=iv(row['budgets'][key])
                gate(f'{name}_dyadic_{index}_{key}',(value.lo*2**80).denominator==1 and (value.hi*2**80).denominator==1)
                sums[key]=sums[key]+value
        gate(name+'_integral_lengths',ml==dlo and ml+ol==dhi)
        totals={k:iv(record['totals'][k]) for k in keys}
        gate(name+'_totals_contain_exact_saved_sums',all(totals[k].contains(sums[k]) for k in keys))
        cursor=dlo
        for row in record['cover']:
            gate(f'{name}_cover_{row["lo"]}',Q(row['lo'])==cursor and Q(row['hi'])>=cursor)
            cursor=Q(row['hi'])
        gate(name+'_full_event_cover',cursor==dhi and bool(record['cover']))
        pars={k:iv(v) for k,v in record['parameters'].items()}
        r,h,k,mu=map(pars.get,('rate','h','k','mu1'))
        gate(name+'_full_selected_mass',mu.contains(I(*seed['mu_bracket'])))
        gate(name+'_positive_growing_not_forced',(r-h).lo>0 and (11*h/10-r).lo>0)
        gate(name+'_h_k_relation',(h*h-k).zero())
        gate(name+'_mass_rate_relation',(mu+r*(r+3*h)).zero())
        gate(name+'_second_rate_relation',(pars['mu2']+2*r*(2*r+3*h)).zero())
        gate(name+'_c_factor_relation',(pars['c_factor']-r/(2*(2*r-h))).zero())
        gate(name+'_radial_time_stress', (pars['radial_v2']-(12*k-3*r*r-18*h*r)).zero() and (pars['radial_f2']-r*r/2).zero())
        A2=iv(record['A2']);FP=iv(record['FP']);FH=iv(record['FH'])
        lower=record['walls']['lower'];upper=record['walls']['upper']
        wl={key:iv(v) for key,v in lower['loads'].items()};wu={key:iv(v) for key,v in upper['loads'].items()}
        gate(name+'_nonzero_shooting_inverse',not FH.zero())
        calcA=(-wu['R2']/2-FP)/FH
        gate(name+'_A2_contains_reconstruction',A2.contains(calcA))
        graph=wu['xi2']-wl['xi2']
        bulk=totals['c2']-2*(totals['p2P']+A2*totals['p2H'])+2*totals['p1sq']
        gate(name+'_graph_contains_reconstruction',iv(record['graph']).contains(graph))
        gate(name+'_bulk_contains_reconstruction',iv(record['bulk']).contains(bulk))
        d2=iv(record['d2']);gate(name+'_d2_contains_reconstruction',d2.contains(iv(record['graph'])+iv(record['bulk'])))
        gate(name+'_d1_contains_reconstruction',iv(record['d1']).contains(-2*totals['p1']))
        oldseed=read(seedroot/'output'/('strip_'+name+'.json'))
        gate(name+'_first_distance_overlap',iv(record['d1']).overlaps(iv(oldseed['observables']['deltaD_over_Q'])))
        for side,entry,w,sigma in (('lower',lower,wl,1),('upper',upper,wu,-1)):
            z=list(map(iv,entry['state']));W,H,Phi,T,E,p1,f1,g1,p2,f2,g2,ph,fh,gh=z
            gate(name+'_'+side+'_saved_residuals',all(iv(v).zero() for v in entry['residuals'].values()))
            d1w=2-mu*E*E;d2w=2-pars['mu2']*E*E
            gate(name+'_'+side+'_oscillator_denominators',d1w.lo>0 and d2w.lo>0)
            chi=f1/d1w;xi=sigma*r*chi*chi/(4*(2*r-h))
            # Repeated saved interval products may widen fresh reconstruction;
            # comparison is deliberately OVERLAP, not an enclosure assertion.
            for label,v in dict(chi1=chi,xi2=xi,c2=-pars['c_factor']*(6*p1*p1+f1*f1),
                                o2=-6*h*r*E*E*p1*chi,j2=2*p1*g1+2*T*p1*p1).items():
                gate(name+'_'+side+'_load_overlap_'+label,w[label].overlaps(v))
            chi2=(f2+T*w['xi2']-w['o2'])/w['d2']
            rows={'scalar':g2+w['Tp']*w['xi2']-T*w['c2']+2*T*p2-sigma*(21*(f2+T*w['xi2'])-chi2)/2+w['j2'],
                  'robin':2*sigma*(g2+2*T*p2)-w['Gamma2']*f2-w['R2'],
                  'graph':w['divisor']*w['xi2']+w['qI'],
                  'oscillator':w['d2']*chi2-f2-T*w['xi2']+w['o2']}
            gate(name+'_'+side+'_reconstructed_rows',all(v.zero() for v in rows.values()))
        upperstate=list(map(iv,upper['state']))
        fh_rebuild=upperstate[13]+2*upperstate[3]*upperstate[11]+wu['Gamma2']*upperstate[12]/2
        gate(name+'_FH_overlap',FH.overlaps(fh_rebuild))
        for key,index in (('psi_b',5),('f_b',6)):
            gate(name+'_seed_upper_overlap_'+key,upperstate[index].overlaps(iv(oldseed['event'][key])))
        gate(name+'_seed_upper_oscillator_overlap',wu['chi1'].overlaps(iv(oldseed['event']['u_b'])))
        minimum=None;indices=[]
        for row in record['minimum_candidate_cells']:
            index=row['index'];indices.append(index)
            gate(f'{name}_minimum_index_{index}',0<=index<count and Q(row['s'])==index*step)
            z=list(map(iv,row['state']));tp=pars['m2']*z[2]-4*z[1]*z[3]
            gate(f'{name}_minimum_local_{index}',z[3].zero() and tp.lo>0)
            val=z[9]+A2*z[12]-z[7]*z[7]/(2*tp)
            minimum=val if minimum is None else minimum.hull(val)
        gate(name+'_minimum_indices_unique',len(indices)==len(set(indices)))
        if minimum is not None:
            gate(name+'_minimum_contains_reconstruction',iv(record['minimum_second']).contains(minimum))
        else:gate(name+'_minimum_absent',record['minimum_second'] is None)
        arms[name]={'exact_saved_budget_sums':{key:v.pack() for key,v in sums.items()},
                    'A2_reconstructed':calcA.pack(),'graph_reconstructed':graph.pack(),'bulk_reconstructed':bulk.pack(),
                    'd2_saved':d2.pack(),'minimum_reconstructed':minimum.pack() if minimum else None,
                    'outward_decimal_bounds':{key:decimal_outward(value) for key,value in
                        dict(d1=iv(record['d1']),d2=d2,graph=iv(record['graph']),bulk=iv(record['bulk']),
                             gamma=r,growth_ratio=r/h,**({'minimum_second':iv(record['minimum_second'])} if minimum else {})).items()},
                    'cells':count,'mandatory_length':str(ml),'optional_length':str(ol)}
        finals.append(d2)
    gate('two_engine_distance_overlap',finals[0].overlaps(finals[1]))
    hull=finals[0].hull(finals[1]);result=read(PACKET/'RESULT.json')
    gate('final_hull_contains_engines',iv(result['d2']).contains(hull))
    sign=1 if iv(result['d2']).lo>0 else -1 if iv(result['d2']).hi<0 else 0
    gate('final_sign',result['pass'] and result['sign']==sign and result['normalization']=='psi1(lower)=1')
    gate('runtime_unchanged',lease.observed()==runtime)
    gate('inputs_unchanged',all(sha(p)==digest for p,digest in inputs.items()))
    out={'pass':True,'classification':'NEUTRAL_GROWING_QUADRATIC_SAVED_RECORD_AUDIT_PASS',
         'production_terminal_sha256':expected_terminal,'result_sha256':sha(PACKET/'RESULT.json'),
         'd2':iv(result['d2']).pack(),'outward_decimal_d2':decimal_outward(iv(result['d2'])),
         'sign':sign,'arms':arms,'gate_count':len(gates),'gates':gates,
         'new_physical_integrations':0,
         'scope':'Independent exact resummation and reconstruction of authenticated saved records. ODE/Picard tube correctness, eigenmode/root premises and completeness of minimum candidate inventory remain inherited. Overlap checks are explicitly distinguished from containment. Local quadratic response only; no nonlinear endpoint.'}
    put('AUDIT_RESULT.json',out)
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
                              'binding_sha256':sha(ROOT/'AUDIT_BINDING.json'),'source_sha256':sha(__file__)})
    print(json.dumps({'pass':True,'gate_count':len(gates),'sign':sign}),flush=True)

if __name__=='__main__':
    lease=None
    try:
        assert sys.platform=='linux' and len(sys.argv)==2,'LINUX_AND_TERMINAL_PIN_REQUIRED'
        assert sha(FLOW/'FROZEN.json')=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert read(FLOW/'FROZEN.json')['files'][str(lp)]==sha(lp),'LEASE_HASH'
        spec=importlib.util.spec_from_file_location('growing_audit_lease',lp)
        lease=importlib.util.module_from_spec(spec);sys.modules[spec.name]=lease;spec.loader.exec_module(lease);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_240_SECONDS')))
        run(lease,sys.argv[1])
    except BaseException as exc:
        put('AUDIT_FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        if lease:
            for handle in lease.handles:handle.close()
