"""Read-only saved-cell quartic audit. Linux only; no ODE propagation."""
import sys
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, signal, time
from fractions import Fraction as Q
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
ROOT = BASE / '20261027_QUARTIC_REAL_SOURCE_ENCLOSURE'
CHECKS = 0

def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(v, message):
    global CHECKS
    if not v: raise AssertionError(message)
    CHECKS += 1
def load(name, p):
    s = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(s); sys.modules[name] = m
    s.loader.exec_module(m); return m
def bounds(v): return tuple(map(Q, v['exact_bounds']))
def plus(a, b): return a[0]+b[0], a[1]+b[1]
def minus(a, b): return a[0]-b[1], a[1]-b[0]
def times(a, b):
    c = [x*y for x in a for y in b]; return min(c), max(c)
def encloses(a, b): return a[0] <= b[0] and a[1] >= b[1]

def main():
    ck(sys.platform == 'linux', 'LINUX_ONLY')
    start = time.monotonic()
    audit_sha = sha(__file__)
    lp = BASE/'20261027_SHARED_ADMISSION/lease.py'
    ck(sha(lp) == '0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862', 'LEASE_PIN')
    lease = load('actual4_audit_lease', lp); lease.ROOT = ROOT
    try:
        lease.acquire(); signal.alarm(600)
        terminal = read(ROOT/'production_TERMINAL.json')
        ck(terminal['pass_status'], 'TERMINAL_PASS')
        terminal_pin = sha(ROOT/'production_TERMINAL.json')
        for n,h in terminal['artifacts'].items(): ck(sha(ROOT/n)==h, 'ARTIFACT:'+n)
        binding = read(ROOT/'production_BINDING.json')
        binding_pin = sha(ROOT/'production_BINDING.json')
        for group in ('inputs','sources','runtime'):
            for p,h in binding[group].items(): ck(sha(p)==h, 'BOUND:'+p)
        ck(not list(ROOT.glob('*FAILURE.json')), 'NO_FAILURE')
        sys.path.insert(0, '/home/parallels/research-runs/cap-interval-arb-2026-09-12')
        cubic = BASE/'20261026_GROWING_MODE_CUBIC_AFFINE'
        sys.path.insert(0, str(cubic))
        from flint import arb, fmpq, ctx
        ctx.prec = 1024; ctx.threads = 1
        drv = load('actual4_audit_driver', cubic/'run.py'); drv.arb=arb; drv.fmpq=fmpq
        drv.adapters=load('actual4_audit_adapters',cubic/'adapters.py')
        drv.engines={n:getattr(drv.adapters,n)() for n in ('primary','independent')}
        quad=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
        drv.quad=load('actual4_audit_quad',quad/'run.py')
        drv.quad.wall=load('actual4_audit_quadwall',quad/'wall.py')
        drv.wall=load('actual4_audit_cubicwall',BASE/'20261026_GROWING_MODE_CUBIC_WALL/wall.py')
        drv.wall_affine=load('actual4_audit_affinewall',cubic/'wall_affine.py')
        source=load('actual4_audit_closed',BASE/'20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py')
        wall4=load('actual4_audit_wall4',BASE/'20261027_QUARTIC_WALL_QUALIFICATION/wall.py')
        flow=load('actual4_audit_flow',ROOT/'flow.py')
        def forbid_write(*args): raise AssertionError('READ_ONLY_AUDIT')
        flow.setup(drv,source,wall4,arb,fmpq,read,forbid_write,BASE)
        def iv(v): return drv.engines['primary'].interval(*map(fmpq,v['exact_bounds']))
        def ab(v): return max(abs(Q(str(v.lower().fmpq()))),abs(Q(str(v.upper().fmpq()))))
        def bb(v): return Q(str(v.lower().fmpq())),Q(str(v.upper().fmpq()))
        inverse=read(BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json')
        ck(inverse['scientific_certificate'],'INVERSE_CERTIFIED')
        reports={}; result=read(ROOT/'RESULT.json')
        for name in ('primary','independent'):
            arm=read(ROOT/('ARM_'+name+'.json')); p={k:iv(v) for k,v in arm['parameters'].items()}
            old=read(cubic/('PRODUCTION_'+name+'.json'))
            # The documented producer imports the inherited interval at 768 bits.
            ctx.prec=768
            imported_A3=flow.pack(iv(old['A3']))
            ctx.prec=1024
            ck(arm['parameters']['A3']==imported_A3,'ACTUAL_A3_CONVERSION')
            ck(encloses(bounds(arm['parameters']['A3']),bounds(old['A3'])),'ACTUAL_A3_CONTAINMENT')
            qo=read(quad/('PRODUCTION_'+name+'.json'))
            ctx.prec=768
            imported_A2=flow.pack(iv(qo['A2']))
            ctx.prec=1024
            ck(arm['parameters']['A2']==imported_A2,'ACTUAL_A2_CONVERSION')
            ck(encloses(bounds(arm['parameters']['A2']),bounds(qo['A2'])),'ACTUAL_A2_CONTAINMENT')
            fresh=read(BASE/'20261026_GROWING_INVERSE_READINESS_R1'/('INITIAL_'+name+'.json'))
            ck(arm['D']==fresh['D'],'INVERSE_DOMAIN')
            for k,v in fresh['parameters'].items(): ck(arm['parameters'][k]==v,'INVERSE_PARAMETER:'+k)
            lo_state=arm['lower_canonical']; hi_state=arm['upper_canonical']
            ck(len(lo_state)==len(hi_state)==23,'ENDPOINT_LENGTHS')
            ck(lo_state==old['walls']['lower']['raw'],'ENTRY_REPLAY')
            ck(lo_state[:5]==fresh['initial_native'][:5] if name=='primary' else lo_state[:4]==fresh['initial_native'][:4], 'BACKGROUND_ENTRY')
            dlo,dhi=map(Q,arm['D']); step=Q(1,4096 if name=='primary' else 8192)
            expected=-((-dhi.numerator*step.denominator)//(dhi.denominator*step.numerator))
            cursor=0; prior=None; exact_sum=(Q(0),Q(0)); extrema={k:Q(0) for k in ('forcing','Sc4','T','Tp')}; dmin=None
            for item in arm['chunks']:
                ck(sha(ROOT/item['file'])==item['sha256'],'CHUNK_PIN')
                ck(sha(ROOT/item['checkpoint'])==item['checkpoint_sha256'],'CHECKPOINT_PIN')
                chunk=read(ROOT/item['file']); cp=read(ROOT/item['checkpoint'])
                ck(chunk['binding_sha256']==binding_pin and chunk['previous_sha256']==prior,'CHUNK_CHAIN')
                prior=item['sha256']; ck(cp['chunk_sha256']==prior and cp['binding_sha256']==binding_pin,'CHECKPOINT_BINDING')
                for row in chunk['records']:
                    ck(row['index']==cursor and Q(row['s'])==cursor*step and Q(row['step'])==step,'CELL_COVERAGE')
                    ck(len(row['canonical_box'])==23,'CANONICAL_LENGTH')
                    z=list(map(iv,row['canonical_box'])); q=flow.fields(z,p)
                    vals=dict(forcing=ab(q['forcing']),Sc4=ab(q['s4']['Sc4']),T=ab(z[3]),Tp=ab(q['Tp']))
                    for k,v in vals.items():
                        saved=Q(row['source_suprema'][k]); ck(saved>=v,'SOURCE_ENCLOSURE:'+name+':'+str(cursor)+':'+k)
                        extrema[k]=max(extrema[k],saved)
                    saved_d=Q(row['D_lower']); ck(0<saved_d<=bb(q['D'])[0],'D_ENCLOSURE')
                    dmin=saved_d if dmin is None else min(dmin,saved_d)
                    ck(encloses(bounds(row['known_density']),bb(q['known_density'])),'DENSITY_ENCLOSURE')
                    for v in list(row['constraint_enclosures'].values())+[row['background_first_integral']]:
                        a,b=bounds(v); ck(a<=0<=b,'LOWER_CONSTRAINT')
                    pos=cursor*step; mandatory=max(Q(0),min(step,dlo-pos)); optional=max(Q(0),min(step,dhi-pos))-mandatory
                    ck(Q(row['mandatory'])==mandatory and Q(row['optional'])==optional,'DOMAIN_WEIGHTS')
                    dens=bounds(row['known_density']); budget=plus(times(dens,(mandatory,mandatory)),times(dens,(Q(0),optional)))
                    ck(encloses(bounds(row['integral_budget']),budget),'INTEGRAL_BUDGET')
                    exact_sum=plus(exact_sum,bounds(row['integral_budget'])); cursor+=1
                ck(cp['completed']==cursor and cp['total']==expected,'CHECKPOINT_COUNT')
                ck(cp['resumable']==False,'HONEST_NONRESUMABLE')
            ck(cursor==expected==arm['cells'],'FULL_CELL_COUNT')
            ck({k:str(v) for k,v in extrema.items()}==arm['extrema'] and str(dmin)==arm['D_lower'],'GLOBAL_EXTREMA')
            ck(encloses(bounds(arm['known_integral']),exact_sum),'INTEGRAL_SUM')
            wall_results={}
            for side,state,sigma in [('lower',lo_state,1),('upper',hi_state,-1)]:
                wall=flow.wall(list(map(iv,state)),p,sigma); wall_results[side]=wall
                for k,v in arm['walls'][side].items(): ck(encloses(bounds(v),bb(wall[k])),'WALL_ENCLOSURE:'+side+':'+k)
            ia=inverse['arms'][name]; cf=Q(ia['finite_orders']['4']['constant'])*Q(ia['f_transfer_multiplier'])
            g=max(max(map(abs,bounds(arm['walls'][side]['robin']))) for side in ('lower','upper'))
            size=extrema['forcing']+4*g; fb=cf*size/16; gb=cf*size/4
            pb=(extrema['Sc4']+extrema['T']*gb+extrema['Tp']*fb)/dmin; ib=2*dhi*pb
            for k,v in dict(Cf4=cf,Robin_abs=g,source_size=size,f4_bound=fb,f4prime_bound=gb,p4_bound=pb,unknown_metric_integral_bound=ib).items(): ck(Q(arm[k])==v,'INVERSE_ARITHMETIC:'+k)
            wa=arm['walls']; known=plus(plus(minus(bounds(wa['upper']['xi4']),bounds(wa['lower']['xi4'])),minus(bounds(wa['upper']['transport']),bounds(wa['lower']['transport']))),bounds(arm['known_integral']))
            ck(encloses(bounds(arm['known_distance_part']),known),'KNOWN_DISTANCE')
            ck(encloses(bounds(arm['d4']),plus(bounds(arm['known_distance_part']),(-ib,ib))),'D4_ENCLOSURE')
            ck(result['arms'][name]['sha256']==sha(ROOT/('ARM_'+name+'.json')),'RESULT_ARM_PIN')
            reports[name]=dict(cells=cursor,d4=arm['d4'],inverse_constant=str(cf))
        a,b=[bounds(read(ROOT/('ARM_'+n+'.json'))['d4']) for n in ('primary','independent')]
        ck(max(a[0],b[0])<=min(a[1],b[1]),'TWO_ENGINE_OVERLAP')
        ck(encloses(bounds(result['d4']),(min(a[0],b[0]),max(a[1],b[1]))),'RESULT_HULL')
        ck(sha(ROOT/'production_TERMINAL.json')==terminal_pin,'TERMINAL_UNCHANGED')
        for group in ('inputs','sources','runtime'):
            for p,h in binding[group].items(): ck(sha(p)==h, 'POST_BOUND:'+p)
        for n,h in terminal['artifacts'].items(): ck(sha(ROOT/n)==h, 'POST_ARTIFACT:'+n)
        ck(sha(__file__)==audit_sha,'AUDIT_SOURCE_UNCHANGED')
        print(json.dumps(dict(PASS=True,checks=CHECKS,seconds=time.monotonic()-start,audit_source_sha256=audit_sha,terminal=terminal_pin,result=sha(ROOT/'RESULT.json'),arms=reports,scope='Whole saved canonical-cell source recomputation with qualified formulas; independent exact archive/inverse/integral reduction. Validated ODE propagation and constraint computation are inherited; stored constraint zero containment checked, not independently recomputed.')),flush=True)
    finally:
        signal.alarm(0)
        for h in lease.handles: h.close()

if __name__=='__main__': main()

