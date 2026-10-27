"""Closeout evidence inventory and independent clock/wall arithmetic replay.
Linux only. Does not claim to independently repeat inherited ODE proofs.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
DEADLINE=1793039120
PINS={
'20261026_GROWING_MODE_QUADRATIC_R1/production_TERMINAL.json':'ffd7264e8bc8babbf511673c7a313e500f54746f67f1b0668069d3ad3cb727ec',
'20261026_GROWING_MODE_QUADRATIC_R1/audit/AUDIT_TERMINAL.json':'61cfa897dec29277df1dc4783529a09cb4134eb5be13c8dc628945099c761282',
'20261026_GROWING_MODE_CUBIC_BULK/TERMINAL.json':'b63c22645be0ebbc85e69592e51294c49b647f607a3637890205ab30ef1d8883',
'20261026_GROWING_MODE_CUBIC_WALL/TERMINAL.json':'0e3fb6eb17a281df0d7e14cce04af4d499849192f974e25fcf58cc42435adcaa',
'20261026_GROWING_MODE_CUBIC_FLOW/production_TERMINAL.json':'0b15aa17ddc7b7b76b64341db64b0c333a9ae1ba622daf5b2da67766551f2c95',
'20261026_GROWING_MODE_CUBIC_FLOW/audit/AUDIT_TERMINAL.json':'fa56a45fa9de26ebe6d7850300dd99edde2586bfc69cdf6c02903c934e1aaa49',
'20261026_GROWING_MODE_CUBIC_AFFINE/production_TERMINAL.json':'4f59104039d4eff1c3d4ad976ff7987d1830ab1416b43911fb68a1f32b37bd57',
'20261026_GROWING_MODE_CUBIC_AFFINE/audit/AUDIT_TERMINAL.json':'4544f23bd218de5c9ae2d0cb7bd23b248f92669275023f65673f45449bc0dd6a',
'20261026_GROWING_MODE_CLOCK_READOUT/TERMINAL.json':'2990c175d97b42698c2f27ab34219a9755690711d5ff45d0dd1e9b949baa7a9d',
'20261026_GROWING_INVERSE_READINESS_R1/TERMINAL.json':'f8a27fa6aeccb8f6b63af588d02fe8dd9a97c201956adbcf9544decb0a319445',
'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/TERMINAL.json':'1d756bb367a3e8c55452bfa95120b809ef08a2d681c7be1bf040fa0d0eb02bb4',
'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/audit/AUDIT_TERMINAL.json':'970f11cb9734c3dfe725788de8957a4b5ca0fced0727ec1ae6a4f8da14907c35',
'20261026_GROWING_NEUTRAL_METRIC_RESPONSE/TERMINAL.json':'b5d47177496093f1832a6d7a36f5d58d4c095c19d24ea6e5e03f38d38b1ec9b1',
'20261026_GROWING_NEUTRAL_METRIC_RESPONSE/audit/AUDIT_TERMINAL.json':'06c64b772c6765b90a2cbfe43576ac14220793915635fbaa8d8cc572b7057847',
'20261026_GROWING_NEUTRAL_TRACE_WALL_R1/TERMINAL.json':'ca7508e9840b268e01cde2fcc8295e1c452a1aee729ba7b12164712d55432a6e'}
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def main(lease):
    inputs={str(Path(__file__)):sha(__file__)};inventory={};gates={}
    def gate(n,v):need(v,n);gates[n]=bool(v)
    for relative,digest in PINS.items():
        path=BASE/relative;gate('terminal:'+relative,sha(path)==digest);term=read(path);gate('pass:'+relative,term.get('pass',term.get('pass_status')) is True);inputs[str(path)]=digest
        for n,h in term.get('artifacts',{}).items():gate('artifact:'+relative+':'+n,sha(path.parent/n)==h);inputs[str(path.parent/n)]=h
        for n,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
            if key not in term:continue
            if 'audit/' in relative:n={'RESULT.json':'AUDIT_RESULT.json','BINDING.json':'AUDIT_BINDING.json','check.py':'verify.py'}.get(n,n)
            if n=='check.py' and not (path.parent/n).exists():n='run.py'
            target=path.parent/n;gate('linked:'+relative+':'+n,sha(target)==term[key]);inputs[str(target)]=term[key]
        inventory[relative]=dict(sha256=digest,pass_status=True)
    # Bind the full current closure underlying the final response packet.
    closing=BASE/'20261026_GROWING_NEUTRAL_TRACE_WALL_R1/BINDING.json'
    for group in ('inputs','sources','runtime'):
        for p,h in read(closing)[group].items():gate('closure:'+p,sha(p)==h);inputs[p]=h
    utility=BASE/'20261026_GROWING_MODE_QUADRATIC_R1/audit/verify.py';need(sha(utility)==read(utility.parent/'AUDIT_TERMINAL.json')['source_sha256'],'UTILITY');inputs[str(utility)]=sha(utility)
    u=load('closeout_exact_interval',utility);iv,I=u.iv,u.I
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP');inputs[str(pylong)]=sha(pylong)
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h,'RUNTIME:'+p)
    put('VERIFICATION_BINDING.json',dict(inputs=inputs,runtime=runtime,terminals=PINS))
    metric=read(BASE/'20261026_GROWING_NEUTRAL_METRIC_RESPONSE/RESULT.json');wall=read(BASE/'20261026_GROWING_NEUTRAL_TRACE_WALL_R1/RESULT.json');clock=read(BASE/'20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
    for name in ('primary','independent'):
        a=metric['arms'][name];T=Q(a['background_extrema']['T0']);Tp=Q(a['background_extrema']['Tp0']);r=Q(a['r_min']);emin=Q(a['E2_min'])
        cc=2/(r*r);cx=cc/emin;co=1/(r*r*emin);factor=max(Q(1),T*cc,(Tp+Q(21,2)*T)*cx,Q(2),co/2)
        cf=Q(a['constants_exact']['scalar_from_compatible_loads'])*factor;cp=Q(a['constants_exact']['metric_from_compatible_loads'])*factor
        vals=dict(trace=cc,graph=cx,oscillator_raw=co,raw_to_R_metric_norm=factor,scalar=cf,metric_p=cp,metric_b=cc+2*cp,wall_oscillator=co*(1+cf/4+T*cx/4))
        gate(name+'_wall_constants',wall['arms'][name]['constants_exact']=={k:str(v) for k,v in vals.items()})
        gate(name+'_wall_integer_bounds',wall['arms'][name]['constants_outward_integer']=={k:-((-v.numerator)//v.denominator) for k,v in vals.items()})
        q=read(BASE/'20261026_GROWING_MODE_QUADRATIC_R1'/('PRODUCTION_'+name+'.json'));c=read(BASE/'20261026_GROWING_MODE_CUBIC_AFFINE'/('PRODUCTION_'+name+'.json'))
        d1,d2,d3=iv(q['d1']),iv(q['d2']),iv(c['d3']);z=list(map(iv,q['walls']['lower']['state']));a1=z[5];A=z[8]+z[1]*iv(q['walls']['lower']['loads']['xi2']);rate=iv(c['parameters']['rate'])
        gate(name+'_negative_coefficients',d1.hi<0 and d2.hi<0 and d3.hi<0)
        d1sq=d1*d1;ct2=d2/d1sq;ct3=2*d3/(d1sq*d1)-2*d2*d2/(d1sq*d1sq);pt2=(d2-a1*d1)/d1sq;pt3=ct3+(a1*a1/2-A)/d1sq
        computed=dict(d1=d1,d2=d2,d3=d3,rate=rate,lower_log_lapse2=A,coordinate_quadratic=ct2,coordinate_cubic=ct3,proper_quadratic=pt2,proper_cubic=pt3,proper_quadratic_rate=rate*pt2,proper_cubic_rate=rate*pt3)
        for k,v in computed.items():
            gate(name+'_clock_'+k,iv(clock['arms'][name]['values'][k]).contains(v))
            textlo,texthi=clock['arms'][name]['outward_decimal_bounds'][k];gate(name+'_clock_decimal_'+k,I(textlo,texthi).contains(v))
        gate(name+'_proper_clock_interpretation',pt2.hi<0 and pt3.zero())
    gate('wall_qualification_count',len(wall['exact_controls'])==8 and all(wall['exact_controls'].values()))
    gate('runtime_unchanged',lease.observed()==runtime);gate('input_hashes_unchanged',all(sha(p)==h for p,h in inputs.items()))
    out=dict(pass_status=True,classification='GROWING_MODE_GOAL_EVIDENCE_AND_CLOCK_WALL_ARITHMETIC_VERIFIED',terminals=inventory,checks=len(gates),gates=gates,new_ode_solves=0,scope='Pinned terminal and input closure; independent rational replay of final trace/wall constants and formal clock readout. Earlier ODE and exact-polynomial qualifications remain inherited with their separate audits. No finite-amplitude solution or nonlinear convergence claim.')
    put('VERIFICATION.json',out);put('VERIFICATION_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'VERIFICATION.json'),binding_sha256=sha(ROOT/'VERIFICATION_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(dict(pass_status=True,checks=len(gates),terminals=len(inventory))),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+180<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('VERIFY_START.json','VERIFY_FAILURE.json','VERIFICATION_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE')
        lease=load('goal_closeout_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('GOAL_VERIFICATION_180_SECONDS')));signal.alarm(180)
        put('VERIFY_START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('VERIFY_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
