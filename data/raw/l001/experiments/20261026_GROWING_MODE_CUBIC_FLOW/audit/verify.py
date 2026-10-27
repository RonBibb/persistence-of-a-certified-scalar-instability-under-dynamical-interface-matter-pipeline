"""Exact saved-record cubic audit; Linux only. Does not rerun ODE tubes.

Usage: python -I -B audit/verify.py PINNED_PRODUCTION_TERMINAL_SHA256
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PACKET=ROOT.parent;BASE=PACKET.parent
PARENT=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def run(lease,pin):
    assert sys.platform=='linux'
    assert not any((ROOT/n).exists() for n in ('AUDIT_START.json','AUDIT_RESULT.json','AUDIT_FAILURE.json')),'NO_RESTART'
    cpu,occupied=lease.acquire();signal.alarm(300)
    put('AUDIT_START.json',dict(cpu=cpu,occupied=occupied))
    assert sha(PACKET/'production_TERMINAL.json')==pin,'PRODUCTION_PIN'
    terminal=read(PACKET/'production_TERMINAL.json');assert terminal['pass']
    inputs={str(PACKET/'production_TERMINAL.json'):pin,str(Path(__file__)):sha(__file__)}
    for n,h in terminal['artifacts'].items():
        p=PACKET/n;assert sha(p)==h,'ARTIFACT:'+n;inputs[str(p)]=h
    required={'production_BINDING.json','controls_BINDING.json','probe_BINDING.json','controls_TERMINAL.json','probe_TERMINAL.json','CONTROLS_RESULT.json','PROBE_RESULT.json','PRODUCTION_primary.json','PRODUCTION_independent.json','RESULT.json','CONTRACT.json'}
    assert required<=set(terminal['artifacts']),'REQUIRED_ARTIFACTS'
    assert not list(PACKET.glob('*FAILURE.json')),'FAILED_PACKET'
    binding=read(PACKET/'production_BINDING.json')
    for group in ('sources','parents','runtime'):
        for p,h in binding[group].items():assert sha(p)==h,'BINDING:'+p;inputs[p]=h
    for stage,result in (('controls','CONTROLS_RESULT.json'),('probe','PROBE_RESULT.json')):
        t=read(PACKET/(stage+'_TERMINAL.json'));assert t['pass']
        assert result in t['artifacts'] and stage+'_BINDING.json' in t['artifacts']
        for n,h in t['artifacts'].items():assert sha(PACKET/n)==h,'STAGE_ARTIFACT:'+n
        assert read(PACKET/(stage+'_BINDING.json'))['sources']==binding['sources'],'STAGE_SOURCE'
    assert read(PACKET/'CONTROLS_RESULT.json')['pass'] and read(PACKET/'PROBE_RESULT.json')['production_admissible']
    # Reuse only the authenticated exact rational interval utility, not its
    # experiment-specific result checker or any integration/source engine.
    prior_terminal=read(PARENT/'audit/AUDIT_TERMINAL.json')
    utility=PARENT/'audit/verify.py'
    assert sha(utility)==prior_terminal['source_sha256'],'EXACT_UTILITY_PIN'
    inputs[str(utility)]=sha(utility)
    old=load('authenticated_exact_interval_utility',utility);I,iv,dec=old.I,old.iv,old.decimal_outward
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    assert sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001
    runtime=lease.observed();known=read(BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/FROZEN.json')['files']
    for p,h in runtime.items():assert inputs.get(p)==h or known.get(p)==h or (p==str(pylong) and h==sha(pylong)),'AUDIT_RUNTIME:'+p
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=pin))
    gates={};arms={};final=[]
    def gate(n,v):gates[n]=bool(v);assert v,n
    contract=read(PACKET/'CONTRACT.json')
    gate('ordinary_neutral_growing_normalization','eta^3' in contract['expansion'] and 'no factorials' in contract['expansion'] and contract['normalization'].startswith('psi1(lower)=1'))
    seedroot=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T2R1_AB_SELECTED_MODE'
    seed=read(seedroot/'output/RESULT.json');cfg=read(seedroot/'inputs/central_bindings.json')
    gate('selected_mode',seed['classification']=='SELECTED_NEUTRAL_MODE_CHARACTERIZED')
    for name in ('primary','independent'):
        rec=read(PACKET/('PRODUCTION_'+name+'.json'));prior=read(PARENT/('PRODUCTION_'+name+'.json'))
        gate(name+'_pass',rec['pass'] and rec['engine']==name)
        dlo,dhi=map(Q,rec['D']);step=Q(1,4096 if name=='primary' else 8192);count=-((-dhi)//step)
        gate(name+'_domain',rec['D']==cfg['config']['D']==prior['D'])
        gate(name+'_count',rec['cells']==len(rec['budgets'])==count)
        keys=('p1','p2P','p2H','c2','p1sq','p3P','p3H','c3','p1c2','p1p2','p1cube')
        sums={k:I(0) for k in keys};ml=Q(0);ol=Q(0)
        for i,row in enumerate(rec['budgets']):
            pos=i*step;mandatory=max(Q(0),min(step,dlo-pos));optional=max(Q(0),min(step,dhi-pos))-mandatory
            gate(f'{name}_cell_{i}',row['index']==i and Q(row['s'])==pos and Q(row['step'])==step)
            gate(f'{name}_length_{i}',Q(row['mandatory'])==mandatory and Q(row['optional'])==optional and optional>=0)
            gate(f'{name}_keys_{i}',set(row['budgets'])==set(keys));ml+=mandatory;ol+=optional
            for key in keys:
                v=iv(row['budgets'][key]);gate(f'{name}_dyadic_{i}_{key}',(v.lo*2**80).denominator==1 and (v.hi*2**80).denominator==1);sums[key]+=v
        gate(name+'_length_totals',ml==dlo and ml+ol==dhi)
        totals={k:iv(rec['totals'][k]) for k in keys}
        gate(name+'_totals_contain_exact_sums',all(totals[k].contains(sums[k]) for k in keys))
        cursor=dlo
        for i,row in enumerate(rec['cover']):
            gate(f'{name}_cover_{i}',Q(row['lo'])==cursor and Q(row['hi'])>=cursor);cursor=Q(row['hi'])
        gate(name+'_cover_complete',bool(rec['cover']) and cursor==dhi)
        p={k:iv(v) for k,v in rec['parameters'].items()};r,h,k=p['rate'],p['h'],p['k'];A2=p['A2']
        gate(name+'_A2_full_parent',A2.contains(iv(prior['A2'])))
        gate(name+'_mass_full_seed',p['mu1'].contains(I(*seed['mu_bracket'])))
        gate(name+'_growing_rate',(r-h).lo>0 and (11*h/10-r).lo>0)
        gate(name+'_h_relation',(h*h-k).zero())
        for j in (1,2,3):gate(name+'_mu'+str(j),(p['mu'+str(j)]+j*r*(j*r+3*h)).zero())
        gate(name+'_c3_factor',(p['c3_factor']-4*r/(3*(3*r-h))).zero())
        lo=rec['walls']['lower'];up=rec['walls']['upper'];zl=list(map(iv,lo['raw']));zu=list(map(iv,up['raw']))
        wl={k:iv(v) for k,v in lo['loads'].items()};wu={k:iv(v) for k,v in up['loads'].items()}
        A3,FP,FH=map(iv,(rec['A3'],rec['FP'],rec['FH']))
        gate(name+'_shoot_inverse',not FH.zero())
        calcA=(-wu['R3']/2-FP)/FH;gate(name+'_A3_contains_reconstruction',A3.contains(calcA))
        gate(name+'_FP_overlap',FP.overlaps(zu[16]+2*zu[3]*zu[14]+wu['Gamma3']*zu[15]/2))
        gate(name+'_FH_overlap',FH.overlaps(zu[19]+2*zu[3]*zu[17]+wu['Gamma3']*zu[18]/2))
        graph=wu['xi3']-wl['xi3'];transport=-2*zu[5]*wu['xi2']+2*zl[5]*wl['xi2']
        bulk=totals['c3']-2*(totals['p3P']+A3*totals['p3H'])-2*totals['p1c2']+4*totals['p1p2']-4*totals['p1cube']/3
        for key,v in dict(graph=graph,transport=transport,bulk=bulk).items():gate(name+'_'+key+'_contains',iv(rec[key]).contains(v))
        gate(name+'_D3_contains',iv(rec['d3']).contains(iv(rec['graph'])+iv(rec['transport'])+iv(rec['bulk'])))
        d1=-2*totals['p1'];d2=wu['xi2']-wl['xi2']+totals['c2']-2*(totals['p2P']+A2*totals['p2H'])+2*totals['p1sq']
        gate(name+'_D1_contains',iv(rec['d1']).contains(d1));gate(name+'_D2_contains',iv(rec['d2_replay']).contains(d2))
        gate(name+'_parent_distance_overlap',iv(rec['d1']).overlaps(iv(prior['d1'])) and iv(rec['d2_replay']).overlaps(iv(prior['d2'])))
        for side,entry,z,w,sigma in (('lower',lo,zl,wl,1),('upper',up,zu,wu,-1)):
            gate(name+'_'+side+'_state_dimensions',len(z)==20)
            matched=z[:8]+[z[j]+A2*z[j+3] for j in (8,9,10)]+z[11:14]
            gate(name+'_'+side+'_parent_endpoint_overlap',all(a.overlaps(iv(b)) for a,b in zip(matched,prior['walls'][side]['state'])))
            gate(name+'_'+side+'_saved_rows',set(entry['residuals'])=={'O','J','graph','constraint'} and all(iv(v).zero() for v in entry['residuals'].values()))
            data={k:iv(v) for k,v in entry['data'].items()};T=z[3];E=z[4]
            gate(name+'_'+side+'_divisors',not w['graph_divisor'].zero() and w['d3'].lo>0)
            gate(name+'_'+side+'_graph', (w['graph_divisor']*w['xi3']+w['qI3']).zero())
            gate(name+'_'+side+'_denominator',(w['d3']-(2-p['mu3']*E*E)).zero())
            gate(name+'_'+side+'_graph_divisor',(w['graph_divisor']-3*sigma*E*E*r*(3*r-h)).zero())
            for label,index in (('p3',14),('f3',15),('g3',16)):
                gate(name+'_'+side+'_matched_'+label,data[label].overlaps(z[index]+A3*z[index+3]))
            osc=w['d3']*data['chi3']-data['f3']-T*w['xi3']+w['o3']
            robin=2*sigma*(data['g3']+2*T*data['p3'])-w['Gamma3']*data['f3']-w['R3']
            gate(name+'_'+side+'_reconstructed_wall',osc.zero() and robin.zero())
        vals={key:iv(rec[key]) for key in ('d1','d3','A3','graph','bulk','transport')};vals.update(d2=iv(rec['d2_replay']),gamma=r,growth_ratio=r/h)
        arms[name]={'cells':count,'exact_saved_budget_sums':{k:v.pack() for k,v in sums.items()},'A3_reconstructed':calcA.pack(),'outward_decimal_bounds':{k:dec(v) for k,v in vals.items()}}
        final.append(iv(rec['d3']))
    result=read(PACKET/'RESULT.json');v=iv(result['d3'])
    gate('two_engine_overlap',final[0].overlaps(final[1]));gate('final_hull_contains',v.contains(final[0].hull(final[1])))
    sign=1 if v.lo>0 else -1 if v.hi<0 else 0
    gate('final_sign',result['pass'] and result['sign']==sign and result['normalization']=='psi1(lower)=1')
    gate('runtime_unchanged',lease.observed()==runtime);gate('inputs_unchanged',all(sha(p)==h for p,h in inputs.items()))
    out=dict(classification='NEUTRAL_GROWING_CUBIC_SAVED_RECORD_AUDIT_PASS',production_terminal_sha256=pin,result_sha256=sha(PACKET/'RESULT.json'),sign=sign,d3=v.pack(),outward_decimal_d3=dec(v),arms=arms,gate_count=len(gates),gates=gates,new_physical_integrations=0,scope='Exact saved-budget resummation and shooting/distance reconstruction; endpoint comparisons explicitly overlap. ODE tubes, source qualification and selected-root existence are inherited. Local cubic coefficient, not a controlled finite-amplitude solution.')
    out['pass']=True;put('AUDIT_RESULT.json',out)
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),'binding_sha256':sha(ROOT/'AUDIT_BINDING.json'),'source_sha256':sha(__file__)})
    print(json.dumps(dict(pass_status=True,gate_count=len(gates),sign=sign)),flush=True)
if __name__=='__main__':
    lease=None
    try:
        assert sys.platform=='linux' and len(sys.argv)==2,'LINUX_PIN_REQUIRED'
        assert sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE_PIN'
        lease=load('cubic_saved_audit_lease',lp);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_300_SECONDS')))
        run(lease,sys.argv[1])
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
