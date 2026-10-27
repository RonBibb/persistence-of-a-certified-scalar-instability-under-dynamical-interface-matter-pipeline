"""Prospective homogeneous inverse diagnostic only; no second-order forcing."""
import importlib.util, os, signal, time, traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('t20_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c)
c.ROOT=ROOT; c.OUT=ROOT/'output'

def parents():
    parent=ROOT.parent/'T2R1_AB_SELECTED_MODE'
    for local,original in [('common.py','producer.py'),('inputs/central_bindings.json','inputs/central_bindings.json'),
                            ('engine/primary_interval.py','engine/primary_interval.py'),
                            ('engine/independent_interval.py','engine/independent_interval.py')]:
        c.need(c.sha(ROOT/local)==c.sha(parent/original),'UNCHANGED_PARENT:'+local)
    c.need((parent/'TERMINAL_REVIEW.md').is_file(),'PARENT_REVIEW_REQUIRED')

def flow(name,begun):
    from flint import arb,fmpq
    m=c.load(name); b=c.read(ROOT/'inputs/central_bindings.json'); cfg=b['config']
    A=m.interval(*map(fmpq,cfg['A'])); dlo,dhi=map(fmpq,cfg['D'])
    # Derive the mass from exactly the same background parameter enclosure.
    _,p0=m.initial(A,arb(0),b['model_exact']); mu=-108*p0['k']
    y,p,ua=c.launch(m,name,A,mu,b['model_exact'],1)
    c.need(c.contains0(mu+108*p['k']) and p['k'].lower()>0,'MASS_BACKGROUND_LINK')
    W,H,P,T,E,psi,f,g=c.physical(y,name)
    G,d=c.response(mu,E,1); B=G*T/2-(p['m2']*P-4*H*T)
    lower={k:c.pack(v) for k,v in dict(psi=psi,f=f,g=g,E=E,H=H,T=T,Gamma=G,d=d,launch_divisor=B,u=ua).items()}
    step=fmpq(2,8192 if name=='primary' else 16384)
    count=(Q(str(dhi))/Q(str(step))).__ceil__(); end={}; cover=[]; whole={}; start=time.monotonic()
    for j in range(count):
        if j%32==0:
            c.need(time.monotonic()-start<540,'ENGINE_CAP_540_SECONDS')
            c.need(time.monotonic()-begun<1200,'PRODUCER_CAP')
        pos=j*step; y,cell=m.step(y,step,p); geo=m.geometry(cell,p)
        c.need(all(v.is_finite() for v in y+list(geo.values())),'FINITE_FLOW')
        c.need(c.contains0(geo['constraint']) and c.contains0(geo['first_integral']),'WHOLE_CELL_CONSTRAINT')
        c.need(geo['warp_squared'].lower()>0,'POSITIVE_WARP')
        for key in ('constraint','first_integral','warp_squared','psi'):
            v=geo[key]; whole[key]=v if key not in whole else m.hull(whole[key],v)
        if pos+step>=dlo and pos<=dhi:
            lo=max(fmpq(0),dlo-pos); hi=min(step,dhi-pos)
            z=m.range_on_cell(cell,lo,hi); W,H,P,T,E,psi,f,g=c.physical(z,name)
            G,d=c.response(mu,E,1); u=f/d; F=g+2*T*psi+G*f/2
            undivided=2*(g+2*T*psi)+21*f-u
            c.need(c.contains0(d*u-f) and c.overlaps(undivided,2*F),'UPPER_UNDIVIDED_ROWS')
            vals=dict(W=W,H=H,Phi=P,T=T,E=E,psi=psi,f=f,g=g,u=u,Gamma=G,d=d,F=F,undivided=undivided)
            for key,v in vals.items(): end[key]=v if key not in end else m.hull(end[key],v)
            cover.append({'lo':str(pos+lo),'hi':str(pos+hi)})
    c.need(time.monotonic()-start<540,'ENGINE_FINAL_CAP')
    last=Q(str(dlo))
    for row in cover: c.need(Q(row['lo'])==last,'EVENT_GAP'); last=Q(row['hi'])
    c.need(last==Q(str(dhi)),'EVENT_END')
    out={'engine':name,'mu':c.pack(mu),'k':c.pack(p['k']),'normalization':'psi(a)=1; homogeneous lower wall and physical constraint',
         'A':cfg['A'],'D':cfg['D'],'cells':count,'step':str(step),'event_cover':cover,'lower':lower,
         'endpoint':{k:c.pack(v) for k,v in end.items()},'whole_cell_hulls':{k:c.pack(v) for k,v in whole.items()},
         'all_cell_checks_pass':True,'seconds':time.monotonic()-start,
         'determinant_excludes_zero':not c.contains0(end['F'])}
    if not c.contains0(end['F']): out['reciprocal_F']=c.pack(1/end['F'])
    c.put(name+'.json',out); print(name+' completed',flush=True)
    return out

def main():
    c.OUT.mkdir(exist_ok=True); c.need(not any((c.OUT/x).exists() for x in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    start=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('HARD_CAP_1200'))); signal.alarm(1200)
        c.authenticate(); parents(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        from flint import arb
        controls={name:c.semantic_controls(c.load(name)) for name in ('primary','independent')}
        # Harmonic law: r=-12h, -r(r+3h)=-108h²; first-order -18h² is distinct.
        h=arb(1)/7; r=-12*h
        c.need(c.contains0(-r*(r+3*h)+108*h*h),'SECOND_HARMONIC_MASS_CONTROL')
        c.need(not c.overlaps(-18*h*h,-108*h*h),'FIRST_HARMONIC_MUTATION')
        c.put('CONTROLS.json',dict(engines=controls,second_harmonic_law=True,first_harmonic_mutation=True))
        results={name:flow(name,start) for name in ('primary','independent')}; m=c.load('primary'); hull={}
        for key in results['primary']['endpoint']:
            x,y=[c.ball_record(m,results[n]['endpoint'][key]) for n in ('primary','independent')]
            c.need(c.overlaps(x,y),'ENGINE_ENDPOINT_DISAGREEMENT:'+key); hull[key]=m.hull(x,y)
        resolved=not c.contains0(hull['F'])
        record={'classification':'HOMOGENEOUS_NUMERICAL_INVERSE_RESOLVED' if resolved else 'NUMERICAL_INVERSE_UNRESOLVED',
                'endpoint_hull':{k:c.pack(v) for k,v in hull.items()},'engines':{n:{'path':n+'.json','sha256':c.sha(c.OUT/(n+'.json'))} for n in results},
                'normalization_dependent':True,'not_operator_norm_or_condition_number':True,
                'forced_fields_computed':False,'second_order_distance_computed':False,
                'nonresonance_inherited_not_tested':True,'utc':c.now(),'seconds':time.monotonic()-start}
        if resolved: record['reciprocal_F_hull']=c.pack(1/hull['F'])
        c.put('RESULT.json',record); signal.alarm(0)
    except BaseException as exc:
        if not (c.OUT/'FAILURE.json').exists(): c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc(),'utc':c.now()})
        raise

if __name__=='__main__': main()
