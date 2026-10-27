"""Two unchanged interval engines; new zero-Hessian launch and certified lift."""
import hashlib,importlib.util,json,math,os,sys,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,'/home/parallels/research-runs/cap-interval-arb-2026-09-12')
from flint import arb,fmpq,ctx
ctx.prec=768;ctx.threads=1
OUT=ROOT/'test1_v3';OUT.mkdir(exist_ok=True)
def save(path,data):
    temp=path.with_suffix('.tmp')
    with temp.open('w') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(x):return x.lower().fmpq(),x.upper().fmpq()
def pack(x):
    lo,hi=bounds(x);return {'bounds':[str(lo),str(hi)],'approx':[float(lo),float(hi)]}
def small(x):
    lo,hi=map(lambda z:Q(str(z)),bounds(x)); d=2**40
    return [str(Q(math.floor(lo*d),d)),str(Q(math.ceil(hi*d),d))]
def check(ok,name):
    if not ok:raise RuntimeError(name)
def module(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'engine'/f'{name}_interval.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fl(y,name):
    psi,f,g=y[-3:];return f,g+2*y[3]*psi
PI=arb.pi()
def arc(f,L):
    if L.lower()>0:return (f/L).atan(),'right'
    if f.lower()>0:return PI/2-(L/f).atan(),'upper'
    if L.upper()<0:return PI+(f/L).atan(),'left'
    if f.upper()<0:return 3*PI/2-(L/f).atan(),'lower'
    raise RuntimeError('PHASE_BOX_CONTAINS_ORIGIN')
def lift(a,reference):
    n=round((float(reference.mid())-float(a.mid()))/(2*math.pi));b=a+2*n*PI
    # An entire chart lies less than pi from the known previous phase midpoint.
    check(abs(b-reference.mid()).upper()<PI.lower(),'AMBIGUOUS_PHASE_LIFT')
    return b
def controls():
    ans=[]
    for f,L,target in [(1,1,.25),(1,-1,.75),(-1,-1,1.25),(-1,1,1.75)]:
        a,_=arc(arb(f),arb(L));a=lift(a,arb(target)*PI)
        check((a/PI).contains(fmpq(str(Q(target)))),'QUADRANT_CONTROL');ans.append(True)
    try:arc(arb(0,1),arb(0,1))
    except RuntimeError:ans.append(True)
    else:raise RuntimeError('ORIGIN_CONTROL')
    return ans
def flow(name,steps,binding,fingerprint):
    m=module(name);check(m.algebra_controls()['pass'],'ALGEBRA_CONTROL')
    a=m.interval(*map(fmpq,binding['config']['A']));Dlo,Dhi=map(fmpq,binding['config']['D'])
    y,p=m.initial(a,arb(0),binding['model_exact']);Ta=y[3];Tp=p['m2']*y[2]-4*y[1]*Ta
    check(Tp.lower()>0 and p['k'].lower()>0,'LOWER_BACKGROUND_PREMISES')
    y[-3:]=[arb(1),-12*p['k']/Tp,-2*Ta]
    check(m.constraint(y,p).contains(0),'ZERO_HESSIAN_CONSTRAINT')
    f,L=fl(y,name);check(L.contains(0) and f.upper()<0,'ZERO_HESSIAN_LAUNCH')
    phase=3*PI/2;h=fmpq(2,steps);n=math.ceil(Q(str(Dhi))/Q(str(h)))
    trace=[];event=[];begun=time.monotonic();minwarp=1.0
    for j in range(n):
        before=y;y,cell=m.step(y,h,p);box=cell['box']
        check(all(v.is_finite() for v in y),'NONFINITE')
        check(m.constraint(box,p).contains(0),'CONSTRAINT_ESCAPE')
        check(m.first_integral(box,p).contains(0),'FIRST_INTEGRAL_ESCAPE')
        warp=(2*box[0]).exp();check(warp.lower()>0,'WARP');minwarp=min(minwarp,float(warp.lower()))
        fc,Lc=fl(box,name);chart,kind=arc(fc,Lc);chart=lift(chart,phase)
        # The validated full-cell box includes both endpoint states. Its fixed
        # half-plane forbids an unseen revolution between endpoints.
        check(chart.overlaps(phase),'PHASE_DISCONNECTED')
        f,L=fl(y,name);end,_=arc(f,L);end=lift(end,chart)
        check(end.overlaps(chart),'END_OUTSIDE_CHART');phase=end
        row={'cell':j,'chart':kind,'arc_over_pi':small(chart/PI),'endpoint_over_pi':small(end/PI)}
        trace.append(row)
        s=j*h
        if s+h>=Dlo and s<=Dhi:
            lo=max(fmpq(0),Dlo-s);hi=min(h,Dhi-s)
            yy=m.range_on_cell(cell,lo,hi);ff,LL=fl(yy,name);ee,_=arc(ff,LL);ee=lift(ee,chart)
            check(ee.overlaps(chart),'EVENT_OUTSIDE_CHART')
            event.append({'lo':str(s+lo),'hi':str(s+hi),'phase':pack(ee),'phase_over_pi':pack(ee/PI),'f':pack(ff),'L':pack(LL)})
        if j%256==0:
            save(OUT/'progress.json',{'state':'RUNNING','engine':name,'completed_cells':j+1,'total_cells':n,'fingerprint':fingerprint,'elapsed_seconds':time.monotonic()-begun})
        check(time.monotonic()-begun<600,'FLOW_TIMEOUT')
    check(bool(event),'EMPTY_EVENT');last=Dlo
    phasewall=None
    for e in event:
        check(fmpq(e['lo'])==last,'EVENT_GAP');last=fmpq(e['hi'])
        v=m.interval(*map(fmpq,e['phase']['bounds']));phasewall=v if phasewall is None else m.hull(phasewall,v)
    check(last==Dhi,'EVENT_END')
    ratio=phasewall/PI
    lo,hi=(Q(str(v)) for v in bounds(ratio));check(lo>1,'PHASE_BELOW_AUXILIARY');nlo=max(0,math.ceil(lo-Q(3,2)));nhi=max(0,math.ceil(hi-Q(3,2)))
    check(nlo==nhi,'MASSLESS_OR_COUNT_UNRESOLVED')
    for j in range(nhi+1):check(not ratio.contains(fmpq(3,2)+j),'MASSLESS_THRESHOLD_CONTACT')
    result={'engine':name,'steps':steps,'k':pack(p['k']),'Tp_a':pack(Tp),'event':event,'phase_over_pi':pack(ratio),'additional_tachyons':nlo,'massless_root_excluded':True,'min_warp_squared':minwarp,'cells':n,'checks_pass':True,'elapsed_seconds':time.monotonic()-begun,'fingerprint':fingerprint}
    save(OUT/f'{name}_trace.json',trace);save(OUT/f'{name}_result.json',result);print(json.dumps(result),flush=True);return result
def main():
    binding=json.loads((ROOT/'inputs/central_bindings.json').read_text())
    source=json.loads((ROOT/'SOURCE_BINDINGS.json').read_text())
    for p,v in source.items():check(sha(ROOT/p)==v['sha256'],'SOURCE_BINDING')
    fingerprint=hashlib.sha256((sha(Path(__file__))+json.dumps(source,sort_keys=True)).encode()).hexdigest()
    result={'controls':controls(),'fingerprint':fingerprint,'engines':{}}
    for name,steps in [('primary',8192),('independent',16384)]:
        path=OUT/f'{name}_result.json'
        if path.exists():
            r=json.loads(path.read_text());check(r['fingerprint']==fingerprint,'RESUME_INCOMPATIBLE')
        else:r=flow(name,steps,binding,fingerprint)
        result['engines'][name]=r
    aa,bb=result['engines'].values();check(aa['additional_tachyons']==bb['additional_tachyons'],'ENGINE_COUNT_DISAGREEMENT')
    a,b=aa['phase_over_pi']['bounds'],bb['phase_over_pi']['bounds']
    check(max(Q(a[0]),Q(b[0]))<=min(Q(a[1]),Q(b[1])),'PHASE_ENGINE_DISAGREEMENT')
    result.update(status='COMPLETE_PENDING_INDEPENDENT_AUDIT',additional_tachyons=aa['additional_tachyons'])
    save(OUT/'RESULT.json',result);save(OUT/'progress.json',{'state':'COMPLETE_PENDING_AUDIT','fingerprint':fingerprint})
if __name__=='__main__':
    try:
        if '--controls' in sys.argv:print(controls())
        else:main()
    except BaseException as e:
        save(OUT/'FAILURE.json',{'status':'TECHNICAL_INCOMPLETE','error':repr(e),'traceback':traceback.format_exc()});raise
