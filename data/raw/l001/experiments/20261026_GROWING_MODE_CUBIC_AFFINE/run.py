"""Neutral growing cubic coefficient: leased, interval inputs, two engines.
No finite-amplitude solution or endpoint fate is asserted by this calculation.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
BULK=BASE/'20261026_GROWING_MODE_CUBIC_BULK'
WALL=BASE/'20261026_GROWING_MODE_CUBIC_WALL'
DEADLINE=1793039120
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,s):
    if not v:raise AssertionError(s)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def pack(v):
    need(v.is_finite(),'FINITE_EXPORT');return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def iv(v):return engines['primary'].interval(*map(fmpq,v['exact_bounds']))
def zero(v):return v.lower()<=0<=v.upper()
def overlap(a,b):return a.lower()<=b.upper() and b.lower()<=a.upper()
def wall_load(z,p,sigma):
    W,H,Phi,T,E,a,f,g,P,F,G,ah,fh,gh=z[:14]
    w2=quad.wall.reconstruct(z[:14],p,sigma)
    tp=p['m2']*Phi-4*H*T;u=-2*H*a-T*f/3
    gprime=-4*H*g+(p['m2']-p['mu1']*E*E+2*T*T)*f+(12*H*T-4*p['m2']*Phi)*a
    chi20=(F+T*w2['xi2']-w2['o2'])/w2['d2']
    sc0,sc1=adapters.source_channels(z,p)
    data=dict(E=E,h=p['h'],rate=p['rate'],H=H,T=T,Tp=tp,p1=a,u1=u,f1=f,g1=g,g1prime=gprime,
              p2=P,f2=F,g2=G,c2=w2['c2'],xi2=w2['xi2'],chi1=w2['chi1'],chi2=chi20,c3=sc0['c3'])
    tangent=dict(p2=ah,f2=fh,g2=gh,chi2=fh/w2['d2'],c3=sc1['c3'])
    w0,w1=wall_affine.channels(data,tangent,sigma)
    need(not zero(w0['graph_divisor']) and w0['d3'].lower()>0,'CUBIC_WALL_DIVISORS')
    w0['xi2']=w2['xi2']
    return w0,w1,data,tangent
def initial(name):
    m=engines[name];y,p,D=quad.initial(m.lower,name);z=m.lower.physical(y)
    prior=read(PARENT/('PRODUCTION_'+name+'.json'))
    p.update(A2=iv(prior['A2']),mu3=-3*p['rate']*(3*p['rate']+3*p['h']),
             c3_factor=4*p['rate']/(3*(3*p['rate']-p['h'])))
    H,Phi,T,E=z[1:5];tp=p['m2']*Phi-4*H*T
    w0,w1,_,_=wall_load(z,p,1);s0,s1=adapters.source_channels(z,p)
    den=w0['Gamma3']*T/2-tp;need(not zero(den),'CUBIC_LOWER_INVERSE')
    for a,sc,R in ((arb(0),s0['Sc3'],w0['R3']),(arb(0),s1['Sc3'],w1['R3']),(arb(1),arb(0),arb(0))):
        f=(sc+3*(p['mu3']+4*p['k'])*E*E*a-T*R/2)/den
        g=w0['Gamma3']*f/2+R/2-2*T*a;z.extend((a,f,g))
    y=z if name=='primary' else z[:4]+z[5:]
    need(all(zero(v) for v in m.constraints(y,p).values()),'INITIAL_CONSTRAINTS')
    need(zero(m.first_integral(y,p)),'INITIAL_BACKGROUND')
    return y,p,D
def flow(name,probe=False):
    m=engines[name];y,p,D=initial(name);low=m.physical(y);start=time.monotonic()
    dlo,dhi=map(fmpq,D);step=fmpq(1,4096 if name=='primary' else 8192)
    full=(Q(str(dhi))/Q(str(step))).__ceil__();count=(64 if name=='primary' else 128) if probe else full
    keys=('p1','p2P','p2H','c2','p1sq','p30','p31','p3H','c30','c31','p1c2','p1p20','p1p21','p1cube')
    totals={k:arb(0) for k in keys};budgets=[];cover=[];end=None;maxpic=0
    def outward(v):
        lo,hi=map(lambda x:Q(str(x)),m.bounds(v));scale=1<<80
        raw={'exact_bounds':[str(Q((lo*scale).__floor__(),scale)),str(Q((hi*scale).__ceil__(),scale))]}
        return raw,iv(raw)
    for i in range(count):
        need(time.time()<DEADLINE and time.monotonic()-start<(600 if probe else 1200),'OPERATIONAL_TIME_BOUND')
        pos=i*step;y,cell=m.step(y,step,p);z=m.physical(cell['box'])
        need(all(v.is_finite() for v in y+cell['box']),'FINITE')
        need(all(zero(v) for v in m.constraints(cell['box'],p).values()),'WHOLE_CELL_CONSTRAINT')
        need(zero(m.first_integral(cell['box'],p)) and z[4].lower()>0,'BACKGROUND_AND_WARP')
        maxpic=max(maxpic,cell['picard_iterations'])
        if not probe:
            n=14 if name=='primary' else 13;s=m.lower.sources(cell['box'][:n],p)
            c2=s[3] if name=='primary' else s['c2'];s0,s1=adapters.source_channels(z,p)
            dens=dict(p1=z[5],p2P=z[8],p2H=z[11],c2=c2,p1sq=z[5]*z[5],p30=z[14],p31=z[17],p3H=z[20],
                      c30=s0['c3'],c31=s1['c3'],p1c2=z[5]*c2,p1p20=z[5]*z[8],p1p21=z[5]*z[11],p1cube=z[5]*z[5]*z[5])
            mandatory=max(fmpq(0),min(step,dlo-pos));optional=max(fmpq(0),min(step,dhi-pos))-mandatory
            row={'index':i,'s':str(pos),'step':str(step),'mandatory':str(mandatory),'optional':str(optional),'budgets':{}}
            for k,v in dens.items():
                raw,b=outward(v*mandatory+v*m.interval(fmpq(0),optional));totals[k]+=b;row['budgets'][k]=raw
            budgets.append(row)
            if pos+step>=dlo and pos<=dhi:
                a,b=max(fmpq(0),dlo-pos),min(step,dhi-pos);ev=m.physical(m.range_on_cell(cell,a,b))
                end=ev if end is None else [m.hull(x,v) for x,v in zip(end,ev)]
                cover.append({'lo':str(pos+a),'hi':str(pos+b)})
        if (i+1)%256==0 or i+1==count:
            print(json.dumps({'engine':name,'probe':probe,'completed':i+1,'total':count,'seconds':time.monotonic()-start}),flush=True)
            if not probe:put('PROGRESS_'+name+'_'+str(i+1).zfill(6)+'.json',{'completed':i+1,'total':count,'seconds':time.monotonic()-start,'resumable':False})
    if probe:
        out={'pass':True,'cells':count,'seconds':time.monotonic()-start,'final':[pack(v) for v in y],
             'projection_seconds':(time.monotonic()-start)*full/count,'maxpic':maxpic}
        put('PROBE_'+name+'.json',out);return out
    cursor=Q(str(dlo))
    for row in cover:need(Q(row['lo'])==cursor,'COVER_GAP');cursor=Q(row['hi'])
    need(cursor==Q(str(dhi)),'COVER_END')
    prior=read(PARENT/('PRODUCTION_'+name+'.json'));A2=p['A2']
    lw0,lw1,ld,lt=wall_load(low,p,1);uw0,uw1,ud,ut=wall_load(end,p,-1)
    d1=-2*totals['p1'];d2=uw0['xi2']-lw0['xi2']+totals['c2']-2*(totals['p2P']+A2*totals['p2H'])+2*totals['p1sq']
    need(overlap(d1,iv(prior['d1'])) and overlap(d2,iv(prior['d2'])),'LOWER_DISTANCE_REPLAY')
    for side,z in [('lower',low),('upper',end)]:
        matched=z[:8]+[z[j]+A2*z[j+3] for j in (8,9,10)]+z[11:14]
        need(all(overlap(a,iv(b)) for a,b in zip(matched,prior['walls'][side]['state'])),'LOWER_ENDPOINT_REPLAY_'+side)
    T=end[3];G=uw0['Gamma3']
    FP0=end[16]+2*T*end[14]+G*end[15]/2
    FP1=end[19]+2*T*end[17]+G*end[18]/2
    FH=end[22]+2*T*end[20]+G*end[21]/2
    need(not zero(FH),'CUBIC_INVERSE_UNRESOLVED')
    A30=(-uw0['R3']/2-FP0)/FH;A31=(-uw1['R3']/2-FP1)/FH;A3=A30+A2*A31
    walls={}
    for side,z,w0,w1,data,tangent,sigma in [('lower',low,lw0,lw1,ld,lt,1),('upper',end,uw0,uw1,ud,ut,-1)]:
        a,f,g=[z[j]+A2*z[j+3]+A3*z[j+6] for j in (14,15,16)]
        full={k:(v+A2*tangent[k] if k in tangent else v) for k,v in data.items()}
        xi3=w0['xi3']+A2*w1['xi3'];o3=w0['o3']+A2*w1['o3']
        full.update(p3=a,f3=f,g3=g,xi3=xi3,chi3=(f+z[3]*xi3-o3)/w0['d3'])
        direct=wall.extract(full,sigma)
        residuals={k:direct['full'][k].a[3] for k in ('O','J','graph')}
        s0,s1=adapters.source_channels(z,p)
        residuals['constraint']=z[3]*g-data['Tp']*f+(2*z[3]*z[3]-3*(p['mu3']+4*p['k'])*z[4]*z[4])*a-s0['Sc3']-A2*s1['Sc3']
        need(all(zero(v) for v in residuals.values()),'CUBIC_WALL_ROWS_'+side)
        walls[side]={'raw':[pack(v) for v in z],'loads0':{k:pack(v) for k,v in w0.items()},'loads1':{k:pack(v) for k,v in w1.items()},
                     'data':{k:pack(v) for k,v in full.items()},'residuals':{k:pack(v) for k,v in residuals.items()}}
    graph0=uw0['xi3']-lw0['xi3'];graph1=uw1['xi3']-lw1['xi3']
    transport=-2*end[5]*uw0['xi2']+2*low[5]*lw0['xi2']
    bulk0=totals['c30']-2*(totals['p30']+A30*totals['p3H'])-2*totals['p1c2']+4*totals['p1p20']-4*totals['p1cube']/3
    bulk1=totals['c31']-2*(totals['p31']+A31*totals['p3H'])+4*totals['p1p21']
    d30=graph0+transport+bulk0;d31=graph1+bulk1;d3=d30+A2*d31
    prior3=read(BASE/'20261026_GROWING_MODE_CUBIC_FLOW'/('PRODUCTION_'+name+'.json'))
    need(overlap(d3,iv(prior3['d3'])) and overlap(A3,iv(prior3['A3'])),'INTERVAL_REPRESENTATION_REPLAY')
    out={'pass':True,'engine':name,'cells':count,'seconds':time.monotonic()-start,'maxpic':maxpic,'D':D,'cover':cover,
         'parameters':{k:pack(v) for k,v in p.items()},'A3':pack(A3),'A30':pack(A30),'A31':pack(A31),
         'FP0':pack(FP0),'FP1':pack(FP1),'FH':pack(FH),'d1':pack(d1),'d2_replay':pack(d2),'d3':pack(d3),'d30':pack(d30),'d31':pack(d31),
         'graph0':pack(graph0),'graph1':pack(graph1),'transport':pack(transport),'bulk0':pack(bulk0),'bulk1':pack(bulk1),
         'totals':{k:pack(v) for k,v in totals.items()},'budgets':budgets,'walls':walls}
    put('PRODUCTION_'+name+'.json',out);return out
def main(mode):
    global engines,adapters,quad,wall,wall_affine,arb,fmpq
    need(sys.platform=='linux' and time.time()<DEADLINE,'LINUX_AND_DEADLINE')
    need(not any(ROOT.glob('*FAILURE.json')) and not (ROOT/(mode+'_START.json')).exists(),'NO_RESTART')
    frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
    need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
    files=read(frozen)['files']
    for p,h in files.items():need(sha(p)==h,'PARENT:'+p)
    previous=BASE/'20261026_GROWING_MODE_CUBIC_FLOW'
    need(sha(previous/'production_TERMINAL.json')=='0b15aa17ddc7b7b76b64341db64b0c333a9ae1ba622daf5b2da67766551f2c95','PREVIOUS_CUBIC_PIN')
    need(sha(previous/'audit/AUDIT_TERMINAL.json')=='fa56a45fa9de26ebe6d7850300dd99edde2586bfc69cdf6c02903c934e1aaa49','PREVIOUS_CUBIC_AUDIT_PIN')
    prior_terminal=read(previous/'production_TERMINAL.json');need(prior_terminal['pass'],'PREVIOUS_PASS')
    for n,h in prior_terminal['artifacts'].items():need(sha(previous/n)==h,'PREVIOUS_ARTIFACT');files[str(previous/n)]=h
    for p,h in read(previous/'production_BINDING.json')['sources'].items():need(sha(p)==h,'PREVIOUS_SOURCE');files[p]=h
    prior_audit=read(previous/'audit/AUDIT_TERMINAL.json')
    need(prior_audit['pass'] and sha(previous/'audit/AUDIT_RESULT.json')==prior_audit['result_sha256'],'PREVIOUS_AUDIT')
    for n in ('production_TERMINAL.json','audit/AUDIT_TERMINAL.json','audit/AUDIT_RESULT.json'):files[str(previous/n)]=sha(previous/n)
    pt=PARENT/'production_TERMINAL.json'
    need(sha(pt)=='ffd7264e8bc8babbf511673c7a313e500f54746f67f1b0668069d3ad3cb727ec','QUADRATIC_TERMINAL_PIN')
    need(sha(PARENT/'audit/AUDIT_TERMINAL.json')=='61cfa897dec29277df1dc4783529a09cb4134eb5be13c8dc628945099c761282','QUADRATIC_AUDIT_PIN')
    need(sha(BULK/'TERMINAL.json')=='b63c22645be0ebbc85e69592e51294c49b647f607a3637890205ab30ef1d8883','BULK_TERMINAL_PIN')
    need(sha(WALL/'TERMINAL.json')=='0e3fb6eb17a281df0d7e14cce04af4d499849192f974e25fcf58cc42435adcaa','WALL_TERMINAL_PIN')
    for root,term in [(PARENT,'production_TERMINAL.json'),(BULK,'TERMINAL.json'),(WALL,'TERMINAL.json')]:
        t=read(root/term);need(t['pass'],'PARENT_TERMINAL')
        if root==PARENT:
            for n,h in t['artifacts'].items():need(sha(root/n)==h,'PARENT_ARTIFACT')
            binding=read(root/'production_BINDING.json');files.update(binding['sources'])
            manifest=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/CLOSURE_MANIFEST.json'
            need(sha(manifest)==binding['parent_closure_sha256'],'CLOSURE_PIN')
            files.update({str(manifest.parent/n):h for n,h in read(manifest)['files'].items()})
            aud=read(root/'audit/AUDIT_TERMINAL.json');need(aud['pass'] and sha(root/'audit/AUDIT_RESULT.json')==aud['result_sha256'],'AUDIT_RESULT')
            need(read(root/'audit/AUDIT_RESULT.json')['production_terminal_sha256']==sha(pt),'AUDIT_PARENT_PIN')
            for n in ('audit/AUDIT_RESULT.json','audit/AUDIT_TERMINAL.json'):files[str(root/n)]=sha(root/n)
        else:
            need(sha(root/'RESULT.json')==t['result_sha256'] and sha(root/'BINDING.json')==t['binding_sha256'],'QUALIFICATION_PIN')
            for p,h in read(root/'BINDING.json')['files'].items():need(sha(p)==h,'QUALIFIED_SOURCE_CHANGED');files[p]=h
        for p in root.glob('*.json'):files[str(p)]=sha(p)
    for p,h in files.items():need(sha(p)==h,'AUTHENTICATED_PARENT')
    lease=load('growing_cubic_lease',BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py');lease.ROOT=ROOT
    try:
        cpu,occupied=lease.acquire();signal.alarm(min(2500 if mode=='production' else 600,int(DEADLINE-time.time())))
        put(mode+'_START.json',{'cpu':cpu,'occupied':occupied,'pid':os.getpid(),'time':time.time()})
        sys.path.insert(0,'/home/parallels/research-runs/cap-interval-arb-2026-09-12');sys.path.insert(0,str(ROOT))
        from flint import arb,fmpq,ctx
        ctx.prec=768;ctx.threads=1
        adapters=load('adapters',ROOT/'adapters.py');engines={n:getattr(adapters,n)() for n in ('primary','independent')}
        quad=load('growing_quadratic_driver',PARENT/'run.py');quad.wall=load('growing_quadratic_wall',PARENT/'wall.py')
        wall=load('general_cubic_wall',WALL/'wall.py');wall_affine=load('growing_wall_affine',ROOT/'wall_affine.py');controls=load('growing_cubic_controls',ROOT/'controls.py')
        controls.prepare(ROOT)
        need(len(str(10**20000))==20001,'INTEGER_WARMUP')
        sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='CONTRACT.json'}
        for stage in ([] if mode=='controls' else ['controls'] if mode=='probe' else ['controls','probe']):
            terminal=read(ROOT/(stage+'_TERMINAL.json'));need(terminal['pass'],'STAGE_TERMINAL')
            required=[stage+'_BINDING.json',stage.upper()+'_RESULT.json']
            need(all(n in terminal['artifacts'] for n in required),'STAGE_REQUIRED_ARTIFACTS')
            for n,h in terminal['artifacts'].items():need(sha(ROOT/n)==h,'STAGE_ARTIFACT:'+n)
            need(read(ROOT/(stage+'_BINDING.json'))['sources']==sources,'STAGE_SOURCE_BINDING')
            files[str(ROOT/(stage+'_TERMINAL.json'))]=sha(ROOT/(stage+'_TERMINAL.json'))
            for n in required:files[str(ROOT/n)]=sha(ROOT/n)
        if mode!='controls':need(read(ROOT/'CONTROLS_RESULT.json')['pass'],'CONTROLS_PASS')
        runtime=lease.observed();extra={'/usr/lib/python3.12/_pylong.py':'79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'}
        for p,h in runtime.items():need(files.get(p)==h or sources.get(p)==h or extra.get(p)==h,'UNBOUND_RUNTIME:'+p)
        put(mode+'_BINDING.json',{'sources':sources,'parents':files,'runtime':runtime})
        if mode=='controls':put('CONTROLS_RESULT.json',controls.run(ROOT,engines,initial))
        elif mode=='probe':
            arms={n:flow(n,True) for n in engines};projection=1.5*sum(v['projection_seconds'] for v in arms.values())
            put('PROBE_RESULT.json',{'pass':True,'projection_seconds':projection,'production_admissible':projection<1800})
        else:
            need(read(ROOT/'PROBE_RESULT.json')['production_admissible'],'FEASIBILITY')
            need(time.time()+2500<DEADLINE,'INSUFFICIENT_GOAL_TIME')
            arms={n:flow(n) for n in engines};vals=[iv(a['d3']) for a in arms.values()]
            need(overlap(*vals),'TWO_ENGINE_DISAGREEMENT');v=engines['primary'].hull(*vals)
            put('RESULT.json',{'pass':True,'classification':'NEUTRAL_GROWING_CUBIC_AFFINE_COMPUTED_AUDIT_PENDING','d3':pack(v),
                'sign':1 if v.lower()>0 else -1 if v.upper()<0 else 0,'normalization':'psi1(lower)=1',
                'scope':'Cubic local growing-mode coefficient only; no controlled finite-amplitude family or endpoint.'})
        need(lease.observed()==runtime,'RUNTIME_DRIFT')
        need(all(sha(p)==h for p,h in dict(files,**sources).items()),'SOURCE_OR_PARENT_DRIFT')
        put(mode+'_TERMINAL.json',{'pass':True,'artifacts':{p.name:sha(p) for p in ROOT.glob('*.json') if not p.name.endswith('_START.json')},'finished':time.time()})
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
if __name__=='__main__':
    mode=sys.argv[1]
    try:
        need(mode in ('controls','probe','production'),'MODE')
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('BOUNDED_'+mode)))
        main(mode)
    except BaseException as e:
        put(mode+'_FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(e),'traceback':traceback.format_exc()});raise

