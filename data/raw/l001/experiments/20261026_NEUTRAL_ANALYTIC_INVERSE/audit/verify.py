"""Independent rational saved-archive/constant replay. No producer import or ODE."""
import sys
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT = Path(__file__).resolve().parent
PACKET = ROOT.parent
BASE = PACKET.parent
FRESH = BASE/'20261026_GROWING_INVERSE_READINESS_R1'
INV = BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE'
FROZEN = BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
DEADLINE = 1793047195
PIN = '7ec861cf5d45f7799f5f88d2d776445acf4c4f4ad7d6626c4ab5e06b3c640d99'


def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v, label):
    if not v: raise AssertionError(label)
def bounds(v):
    a,b = map(Q,v['exact_bounds']); need(a<=b,'ORDERED_INTERVAL'); return a,b
def ceil(q): return -((-q.numerator)//q.denominator)
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m
def put(name,value):
    path=ROOT/name; tmp=ROOT/(name+'.tmp')
    with tmp.open('x') as f: json.dump(value,f,indent=2); f.flush(); os.fsync(f.fileno())
    os.chmod(tmp,0o444); os.link(tmp,path); tmp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def main(lease):
    started=time.monotonic(); checks=0
    def gate(v,label):
        nonlocal checks
        need(v,label); checks+=1
    gate(sha(PACKET/'TERMINAL.json')==PIN,'PRODUCTION_TERMINAL_PIN')
    terminal=read(PACKET/'TERMINAL.json'); gate(terminal['pass_status'],'PRODUCTION_PASS')
    authority={str(PACKET/'TERMINAL.json'):PIN,str(Path(__file__)):sha(__file__)}
    for name,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
        gate(sha(PACKET/name)==terminal[key],'PRODUCTION_'+name); authority[str(PACKET/name)]=terminal[key]
    binding=read(PACKET/'BINDING.json')
    for group in ('inputs','sources','runtime'):
        for p,h in binding[group].items():
            gate(sha(p)==h,'AUTHENTICATED_INPUT'); authority[p]=h
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    gate(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG')
    gate(len(str(10**20000))==20001,'RUNTIME_WARMUP'); authority[str(pylong)]=sha(pylong)
    runtime=lease.observed()
    for p,h in runtime.items(): gate(authority.get(p)==h,'RUNTIME_AUTHORITY:'+p)
    put('AUDIT_BINDING.json',dict(inputs=authority,runtime=runtime,production_terminal_sha256=PIN))
    prod=read(PACKET/'RESULT.json'); ft=read(FRESH/'TERMINAL.json'); inverse=read(INV/'RESULT.json'); reports={}
    for engine in ('primary','independent'):
        initial_path=FRESH/('INITIAL_'+engine+'.json'); arm_path=FRESH/('ARM_'+engine+'.json')
        gate(authority.get(str(initial_path))==sha(initial_path) and authority.get(str(arm_path))==sha(arm_path),'ARCHIVE_AUTHORITY')
        ini=read(initial_path); arm=read(arm_path)
        gate(sha(initial_path)==arm['initial_identity_sha256'],'INITIAL_IDENTITY')
        p={key:bounds(v) for key,v in ini['parameters'].items()}
        gate(0<p['m2'][0]<=p['m2'][1]<=1,'MASS_DOMAIN')
        gate(0<p['k'][0]<=p['k'][1]<=Q(1,1024),'CURVATURE_DOMAIN')
        gate(Q(1,64)<=p['h'][0]<=p['h'][1]<p['rate'][0]<=p['rate'][1]<=Q(1,32),'RATE_DOMAIN')
        gate(p['h'][0]**2<=p['k'][1] and p['k'][0]<=p['h'][1]**2,'INHERITED_SQRT_ENCLOSURE')
        count=0; previous=None; last=ini['initial_native'][:ini['background_native_dimension']]; ds=Q(ini['step'])
        for entry in arm['chunks']:
            gate(time.monotonic()-started<550 and time.time()<DEADLINE,'RESOURCE_BOUND')
            path=FRESH/entry['file']; cp_path=FRESH/entry['checkpoint']
            gate(path.resolve().is_relative_to(FRESH.resolve()) and cp_path.resolve().is_relative_to(FRESH.resolve()),'PATH_SCOPE')
            gate(sha(path)==entry['sha256'] and sha(cp_path)==entry['checkpoint_sha256'],'CHUNK_AND_CHECKPOINT_HASH')
            chunk=read(path); cp=read(cp_path)
            gate(chunk['engine']==engine and chunk['binding_sha256']==ft['binding_sha256'] and chunk['initial_identity_sha256']==arm['initial_identity_sha256'],'CHUNK_PROVENANCE')
            gate(chunk['previous_sha256']==previous and chunk['first']==entry['first']==count,'CHUNK_CHAIN')
            for cell in chunk['records']:
                gate(cell['index']==count and Q(cell['s'])==count*ds and Q(cell['step'])==ds,'CELL_POSITION')
                gate(cell['start_native_background']==last,'STATE_CHAIN'); last=cell['end_native_background']
                box=cell['box_canonical_background']; gate(len(box)==5 and box[:4]==cell['box_native_background'][:4],'CANONICAL_MAP')
                _,H,Phi,T,E=map(bounds,box)
                gate(-2<=H[0] and H[1]<=2,'WHOLE_CELL_H')
                gate(-1<=Phi[0] and Phi[1]<=1,'WHOLE_CELL_PHI')
                gate(-1<=T[0] and T[1]<=1,'WHOLE_CELL_T')
                gate(Q(1,2)<=E[0] and E[1]<=16,'WHOLE_CELL_E')
                gate(cell['whole_cell_constraints_contain_zero'] and cell['background_first_integral_contains_zero'],'INHERITED_TUBE_ADMISSION')
                count+=1
            gate(count==entry['last']+1 and cp['completed']==count and cp['last_native_background']==last and cp['chunk_sha256']==entry['sha256'],'CHECKPOINT_CHAIN')
            previous=entry['sha256']
        dlo,dhi=map(Q,ini['D'])
        gate(0<dlo<=dhi and (count-1)*ds<dhi<=count*ds,'FULL_INTERVAL_COVER')
        gate(count==ini['cells']==arm['cells']==prod['arms'][engine]['cells'] and last==arm['final_native_background'],'COMPLETE_ARM')
        gate(prod['arms'][engine]['domain']==ini['D'],'DOMAIN_REPLAY')
        real=Q(inverse['arms'][engine]['C_f'])
        gate(Q(prod['arms'][engine]['real_inverse_constant'])==real,'INHERITED_REAL_INVERSE')
        reports[engine]=dict(cells=count,real_inverse_constant=str(real))
        print('audit',engine,count,round(time.monotonic()-started,2),flush=True)
    # Independent replay from fixed broad envelopes, not producer helpers.
    eps=Q(1,65536); prior=eps/128; d=3*Q(1,64)**2*Q(1,2)**2
    f_rows=(Q(2)**2/3+Q(17)**2/1024,Q(2),Q(2)+4*3*2,Q(3)*17)
    jac_rows=(Q(4,3)+Q(34,1024),Q(1),Q(1)+8+12,Q(17)+3)
    gate(max(f_rows)<=64 and max(jac_rows)<=32,'PICARD_ENVELOPES')
    gate(prior*64<=eps/2 and prior*32<Q(1,2),'PICARD_CONTRACTION')
    temporal_upper=Q(1,32)**2+3*Q(1,32)**2/2
    difference=(2*eps+eps**2)/2+3*temporal_upper*(32*eps+eps**2)
    gate(difference<d/2 and eps<Q(1,2),'COMPLEX_DENOMINATOR')
    a_bound=4*3+(12*3*2+4*2)*2/(4*(d/2))
    v_bound=Q(1,4)+temporal_upper*17**2+Q(8,4)+(12*3*2+4*2)*26/(16*(d/2))
    selected=None
    for power in range(1,65):
        rho=prior/(2**power)
        contraction=max(v_bound*(rho/2+rho**2/4),a_bound*(rho/5+rho**2/8))
        if rho<=1 and contraction<=Q(1,4): selected=(power,rho,contraction); break
    gate(selected is not None,'COLLAR_SEARCH'); power,rho,contraction=selected
    real=max(Q(v['real_inverse_constant']) for v in reports.values())
    joint=(real*(2+rho/2)+rho/2+rho**2/4)/(1-contraction)
    scalar=(1+max(v_bound,a_bound/2))*joint+1
    anchor=max(Q(1),Q(1,2)+Q(9,4))/d
    gate(3*rho/2<1,'METRIC_ABSORPTION')
    px=(anchor+rho*(Q(1,6)+Q(1,2)))/(1-3*rho/2)
    py=3*px+Q(1,3)+1
    metric=px+py+9*py/rho
    expected=dict(delta=eps,prior_radius=prior,rho=rho,real_D_normalized_lower=d,
                  denominator_variation=difference,complex_D_normalized_lower=d/2,
                  A=a_bound,B=v_bound,q=contraction,C0=real,XY=joint,scalar_C=scalar,
                  metric_anchor=anchor,metric_X=px,metric_Y=py,metric_C=metric)
    gate(set(expected)==set(prod['constants_exact']),'CONSTANT_INVENTORY')
    for key,val in expected.items(): gate(Q(prod['constants_exact'][key])==val,'EXACT_CONSTANT:'+key)
    gate(prod['selected_halving']==power,'FIRST_ADMISSIBLE_COLLAR')
    for key in ('scalar_C','metric_C'): gate(prod['constants_outward_integer'][key]==ceil(expected[key]),'OUTWARD_INTEGER:'+key)
    gate(prod['pass_status'] and prod['new_ode_solves']==0 and all(prod['gates'].values()),'PRODUCTION_CLASSIFICATION')
    gate(lease.observed()==runtime,'RUNTIME_UNCHANGED')
    gate(all(sha(p)==h for p,h in authority.items()),'ALL_INPUTS_UNCHANGED')
    result=dict(pass_status=True,classification='INDEPENDENT_ANALYTIC_INVERSE_ARITHMETIC_AUDIT_PASS',
                checks=checks,arms=reports,rho=str(rho),scalar_constant=ceil(scalar),metric_constant=ceil(metric),
                production_terminal_sha256=PIN,seconds=time.monotonic()-started,
                scope='Exact full-archive bound/chain replay and independent rational Picard, denominator, Nagumo inverse constants. Analytic inequalities reviewed separately; ODE tube existence, standard analytic theorems and h²=k model identity inherited. No new ODE or nonlinear convergence claim.')
    put('AUDIT_RESULT.json',result)
    put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)))
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE')
        need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN_PIN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE_PIN')
        lease=load('analytic_inverse_independent_audit_lease',lp); lease.ROOT=ROOT; cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS'))); signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time())); main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc())); raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles: f.close()
