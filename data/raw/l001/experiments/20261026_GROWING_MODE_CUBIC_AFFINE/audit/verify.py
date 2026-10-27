"""Independent affine saved-record audit. Linux only; no ODE rerun.
Usage: python -I -B audit/verify.py PINNED_PRODUCTION_TERMINAL_SHA256
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
OLD=BASE/'20261026_GROWING_MODE_CUBIC_FLOW'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
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
    cpu,occupied=lease.acquire();signal.alarm(300);put('AUDIT_START.json',dict(cpu=cpu,occupied=occupied))
    assert sha(PACKET/'production_TERMINAL.json')==pin,'PIN'
    t=read(PACKET/'production_TERMINAL.json');assert t['pass']
    inputs={str(PACKET/'production_TERMINAL.json'):pin,str(Path(__file__)):sha(__file__)}
    for n,h in t['artifacts'].items():assert sha(PACKET/n)==h,'ARTIFACT:'+n;inputs[str(PACKET/n)]=h
    required={'production_BINDING.json','controls_BINDING.json','probe_BINDING.json','controls_TERMINAL.json','probe_TERMINAL.json','CONTROLS_RESULT.json','PROBE_RESULT.json','PRODUCTION_primary.json','PRODUCTION_independent.json','RESULT.json','CONTRACT.json'}
    assert required<=set(t['artifacts']) and not list(PACKET.glob('*FAILURE.json'))
    binding=read(PACKET/'production_BINDING.json')
    for group in ('sources','parents','runtime'):
        for p,h in binding[group].items():assert sha(p)==h,'BOUND_INPUT:'+p;inputs[p]=h
    for stage,result in (('controls','CONTROLS_RESULT.json'),('probe','PROBE_RESULT.json')):
        st=read(PACKET/(stage+'_TERMINAL.json'));assert st['pass']
        assert result in st['artifacts'] and stage+'_BINDING.json' in st['artifacts']
        for n,h in st['artifacts'].items():assert sha(PACKET/n)==h,'PRIOR_STAGE:'+n
        assert read(PACKET/(stage+'_BINDING.json'))['sources']==binding['sources']
    assert read(PACKET/'CONTROLS_RESULT.json')['pass'] and read(PACKET/'PROBE_RESULT.json')['production_admissible']
    utility=QUAD/'audit/verify.py';qt=read(QUAD/'audit/AUDIT_TERMINAL.json');assert sha(utility)==qt['source_sha256']
    inputs[str(utility)]=sha(utility);u=load('affine_exact_interval_utility',utility);I,iv,dec=u.I,u.iv,u.decimal_outward
    sourcepath=OLD/'sources.py';wallpath=BASE/'20261026_GROWING_MODE_CUBIC_WALL/wall.py'
    assert inputs[str(sourcepath)]==sha(sourcepath) and inputs[str(wallpath)]==sha(wallpath)
    source=load('affine_audit_original_source',sourcepath);wall=load('affine_audit_original_wall',wallpath)
    pylong=Path('/usr/lib/python3.12/_pylong.py');assert sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c';assert len(str(10**20000))==20001
    runtime=lease.observed();known=read(BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/FROZEN.json')['files']
    for p,h in runtime.items():assert inputs.get(p)==h or known.get(p)==h or (p==str(pylong) and h==sha(pylong)),'AUDIT_RUNTIME:'+p
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=pin))
    gates={};arms={};final=[]
    def gate(n,v):gates[n]=bool(v);assert v,n
    contract=read(PACKET/'CONTRACT.json')
    gate('ordinary_neutral_affine_contract',contract['state_dimensions']==[23,22] and 'no factorials' in contract['expansion'] and contract['normalization'].startswith('psi1(lower)=1'))
    seedroot=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T2R1_AB_SELECTED_MODE'
    seed=read(seedroot/'output/RESULT.json');cfg=read(seedroot/'inputs/central_bindings.json')
    gate('actual_selected_seed',seed['classification']=='SELECTED_NEUTRAL_MODE_CHARACTERIZED')
    keys=('p1','p2P','p2H','c2','p1sq','p30','p31','p3H','c30','c31','p1c2','p1p20','p1p21','p1cube')
    for name in ('primary','independent'):
        rec=read(PACKET/('PRODUCTION_'+name+'.json'));prior=read(QUAD/('PRODUCTION_'+name+'.json'));old=read(OLD/('PRODUCTION_'+name+'.json'))
        gate(name+'_pass',rec['pass'] and rec['engine']==name)
        dlo,dhi=map(Q,rec['D']);step=Q(1,4096 if name=='primary' else 8192);count=-((-dhi)//step)
        gate(name+'_domain',rec['D']==cfg['config']['D']==prior['D']==old['D'])
        gate(name+'_count',rec['cells']==len(rec['budgets'])==count)
        sums={k:I(0) for k in keys};ml=Q(0);ol=Q(0)
        for i,row in enumerate(rec['budgets']):
            pos=i*step;mandatory=max(Q(0),min(step,dlo-pos));optional=max(Q(0),min(step,dhi-pos))-mandatory
            gate(f'{name}_cell_{i}',row['index']==i and Q(row['s'])==pos and Q(row['step'])==step)
            gate(f'{name}_length_{i}',Q(row['mandatory'])==mandatory and Q(row['optional'])==optional and optional>=0)
            gate(f'{name}_keys_{i}',set(row['budgets'])==set(keys));ml+=mandatory;ol+=optional
            for key in keys:
                v=iv(row['budgets'][key]);gate(f'{name}_dyadic_{i}_{key}',(v.lo*2**80).denominator==1 and (v.hi*2**80).denominator==1);sums[key]+=v
        gate(name+'_total_lengths',ml==dlo and ml+ol==dhi)
        tot={k:iv(rec['totals'][k]) for k in keys}
        gate(name+'_totals_contain_exact_sums',all(tot[k].contains(sums[k]) for k in keys))
        cursor=dlo
        for j,row in enumerate(rec['cover']):gate(f'{name}_cover_{j}',Q(row['lo'])==cursor and Q(row['hi'])>=cursor);cursor=Q(row['hi'])
        gate(name+'_complete_cover',bool(rec['cover']) and cursor==dhi)
        p={k:iv(v) for k,v in rec['parameters'].items()};r,h,k=p['rate'],p['h'],p['k'];A2=p['A2']
        gate(name+'_full_A2',A2.contains(iv(prior['A2'])))
        gate(name+'_selected_mass',p['mu1'].contains(I(*seed['mu_bracket'])))
        gate(name+'_growing_rate',(r-h).lo>0 and (11*h/10-r).lo>0)
        gate(name+'_h_relation',(h*h-k).zero())
        for n in (1,2,3):gate(name+'_mu'+str(n),(p['mu'+str(n)]+n*r*(n*r+3*h)).zero())
        gate(name+'_c3_factor',(p['c3_factor']-4*r/(3*(3*r-h))).zero())
        sides={s:rec['walls'][s] for s in ('lower','upper')};z={s:list(map(iv,v['raw'])) for s,v in sides.items()}
        w={s:[{k:iv(v) for k,v in entry['loads'+str(j)].items()} for j in (0,1)] for s,entry in sides.items()}
        A30,A31,A3,FP0,FP1,FH=[iv(rec[k]) for k in ('A30','A31','A3','FP0','FP1','FH')]
        gate(name+'_shoot_inverse',not FH.zero())
        for j,amp,FP in ((0,A30,FP0),(1,A31,FP1)):
            gate(name+'_A3'+str(j)+'_contains',amp.contains((-w['upper'][j]['R3']/2-FP)/FH))
            zz=z['upper'];G=w['upper'][0]['Gamma3'];index=14+3*j
            gate(name+'_FP'+str(j)+'_overlap',FP.overlaps(zz[index+2]+2*zz[3]*zz[index]+G*zz[index+1]/2))
        zz=z['upper'];gate(name+'_FH_overlap',FH.overlaps(zz[22]+2*zz[3]*zz[20]+w['upper'][0]['Gamma3']*zz[21]/2))
        gate(name+'_A3_affine_contains',A3.contains(A30+A2*A31))
        graph0=w['upper'][0]['xi3']-w['lower'][0]['xi3'];graph1=w['upper'][1]['xi3']-w['lower'][1]['xi3']
        transport=-2*z['upper'][5]*w['upper'][0]['xi2']+2*z['lower'][5]*w['lower'][0]['xi2']
        bulk0=tot['c30']-2*(tot['p30']+A30*tot['p3H'])-2*tot['p1c2']+4*tot['p1p20']-4*tot['p1cube']/3
        bulk1=tot['c31']-2*(tot['p31']+A31*tot['p3H'])+4*tot['p1p21']
        for key,v in dict(graph0=graph0,graph1=graph1,transport=transport,bulk0=bulk0,bulk1=bulk1).items():gate(name+'_'+key+'_contains',iv(rec[key]).contains(v))
        gate(name+'_D30_contains',iv(rec['d30']).contains(iv(rec['graph0'])+iv(rec['transport'])+iv(rec['bulk0'])))
        gate(name+'_D31_contains',iv(rec['d31']).contains(iv(rec['graph1'])+iv(rec['bulk1'])))
        gate(name+'_D3_affine_contains',iv(rec['d3']).contains(iv(rec['d30'])+A2*iv(rec['d31'])))
        gate(name+'_original_representation_overlap',iv(rec['d3']).overlaps(iv(old['d3'])) and A3.overlaps(iv(old['A3'])))
        d1=-2*tot['p1'];d2=w['upper'][0]['xi2']-w['lower'][0]['xi2']+tot['c2']-2*(tot['p2P']+A2*tot['p2H'])+2*tot['p1sq']
        gate(name+'_D1_contains',iv(rec['d1']).contains(d1));gate(name+'_D2_contains',iv(rec['d2_replay']).contains(d2))
        gate(name+'_lower_replay',iv(rec['d1']).overlaps(iv(prior['d1'])) and iv(rec['d2_replay']).overlaps(iv(prior['d2'])))
        for side,sigma in (('lower',1),('upper',-1)):
            zz=z[side];entry=sides[side];w0,w1=w[side];data={k:iv(v) for k,v in entry['data'].items()}
            gate(name+'_'+side+'_dimension',len(zz)==23)
            matched=zz[:8]+[zz[j]+A2*zz[j+3] for j in (8,9,10)]+zz[11:14]
            gate(name+'_'+side+'_parent_endpoint_overlap',all(a.overlaps(iv(b)) for a,b in zip(matched,prior['walls'][side]['state'])))
            for field,index in (('p2',8),('f2',9),('g2',10)):gate(name+'_'+side+'_'+field+'_overlap',data[field].overlaps(zz[index]+A2*zz[index+3]))
            for field,index in (('p3',14),('f3',15),('g3',16)):gate(name+'_'+side+'_'+field+'_overlap',data[field].overlaps(zz[index]+A2*zz[index+3]+A3*zz[index+6]))
            gate(name+'_'+side+'_xi3_overlap',data['xi3'].overlaps(w0['xi3']+A2*w1['xi3']))
            gate(name+'_'+side+'_saved_rows',set(entry['residuals'])=={'O','J','graph','constraint'} and all(iv(v).zero() for v in entry['residuals'].values()))
            # Re-evaluate the original non-affine qualified equations, not the
            # candidate affine formulas. Expanded interval arithmetic only
            # supports overlap/zero-inclusion checks at this step.
            original=wall.extract(data,sigma)
            gate(name+'_'+side+'_original_full_wall_rows',all(original['full'][key].a[3].zero() for key in ('O','J','graph')))
            W,H,Phi,T,E,a,f,g=zz[:8]
            src=source.cubic(H,T,Phi,E*E,a,f,g,data['p2'],data['f2'],data['g2'],p)
            gate(name+'_'+side+'_original_c3_overlap',src['c3'].overlaps(data['c3']))
            residual=T*data['g3']-data['Tp']*data['f3']+(2*T*T-3*(p['mu3']+4*k)*E*E)*data['p3']-src['Sc3']
            gate(name+'_'+side+'_original_constraint',residual.zero())
            gate(name+'_'+side+'_wall_divisors',not w0['graph_divisor'].zero() and w0['d3'].lo>0)
            for j,wj in enumerate((w0,w1)):gate(name+'_'+side+'_graph_channel_'+str(j),(w0['graph_divisor']*wj['xi3']+wj['qI3']).zero())
            robin=2*sigma*(data['g3']+2*T*data['p3'])-w0['Gamma3']*data['f3']-w0['R3']-A2*w1['R3']
            gate(name+'_'+side+'_full_robin',robin.zero())
        display={key:iv(rec[key]) for key in ('d1','d3','d30','d31','A3','A30','A31','graph0','graph1','bulk0','bulk1','transport')};display.update(d2=iv(rec['d2_replay']),A2=A2,gamma=r,growth_ratio=r/h)
        arms[name]={'cells':count,'exact_saved_budget_sums':{k:v.pack() for k,v in sums.items()},'outward_decimal_bounds':{k:dec(v) for k,v in display.items()}}
        final.append(iv(rec['d3']))
    result=read(PACKET/'RESULT.json');v=iv(result['d3']);sign=1 if v.lo>0 else -1 if v.hi<0 else 0
    gate('two_engine_overlap',final[0].overlaps(final[1]));gate('final_hull_contains',v.contains(final[0].hull(final[1])))
    gate('final_sign',result['pass'] and result['sign']==sign and result['normalization']=='psi1(lower)=1')
    gate('runtime_unchanged',lease.observed()==runtime);gate('inputs_unchanged',all(sha(p)==h for p,h in inputs.items()))
    put('AUDIT_RESULT.json',{'pass':True,'classification':'NEUTRAL_GROWING_CUBIC_AFFINE_SAVED_RECORD_AUDIT_PASS','production_terminal_sha256':pin,'result_sha256':sha(PACKET/'RESULT.json'),'d3':v.pack(),'outward_decimal_d3':dec(v),'sign':sign,'arms':arms,'gate_count':len(gates),'gates':gates,'new_physical_integrations':0,'scope':'Exact saved-budget resummation, affine shooting/distance reconstruction and original non-affine endpoint equations. Endpoint expanded reconstructions use zero inclusion/overlap, not containment. The saved cell inventory/coverage is checked; ODE step/state-chain validity remains inherited because production saves budgets, not full ODE cells. Qualified source identities and selected eigenmode existence are inherited. No finite-amplitude or endpoint claim.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),'binding_sha256':sha(ROOT/'AUDIT_BINDING.json'),'source_sha256':sha(__file__)})
    print(json.dumps(dict(gate_count=len(gates),sign=sign)),flush=True)
if __name__=='__main__':
    lease=None
    try:
        assert sys.platform=='linux' and len(sys.argv)==2,'LINUX_PIN_REQUIRED'
        assert sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';assert read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE_PIN'
        lease=load('affine_saved_audit_lease',lp);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AFFINE_AUDIT_300_SECONDS')))
        run(lease,sys.argv[1])
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
