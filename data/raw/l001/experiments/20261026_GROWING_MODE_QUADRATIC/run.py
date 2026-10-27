"""Leased, source-bound Linux controls/probe/production for growing U2.
No import-time numerical work. All runs preserve full input intervals.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import importlib.util,hashlib,json,os,time,signal,traceback,datetime,resource
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION'
SEED=PARENT/'T2R1_AB_SELECTED_MODE'
DEADLINE=1793039120
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,s):
    if not v:raise RuntimeError(s)
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def put(n,obj):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(obj,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
def pack(v):return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def zero(v):return v.lower()<=0<=v.upper()
def overlap(a,b):return a.lower()<=b.upper() and b.lower()<=a.upper()
def initial(m,name):
    from flint import arb,fmpq
    cfg=read(SEED/'inputs/central_bindings.json');record=read(SEED/'output/RESULT.json')
    need(record['classification']=='SELECTED_NEUTRAL_MODE_CHARACTERIZED','SEED_NOT_ACCEPTED')
    A=m.interval(*map(fmpq,cfg['config']['A']));model={k:m.exact(v) for k,v in cfg['model_exact'].items()}
    H=-(model['lambda_a']+model['gamma']*(A-model['v0'])**2/2)/6;T=model['gamma']*(A-model['v0'])/2
    k=H*H-1-T*T/12+model['m2']*A*A/12;h=k.sqrt()
    mu=m.interval(*map(fmpq,record['mu_bracket']));r=(-3*h+(9*k-4*mu).sqrt())/2
    need((r-h).lower()>0 and (11*h/10-r).lower()>0,'GROWING_RATE_RANGE')
    mu2=-2*r*(2*r+3*h)
    pars=dict(m2=model['m2'],k=k,h=h,rate=r,mu1=mu,mu2=mu2,c_factor=r/(2*(2*r-h)),
              radial_v2=12*k-3*r*r-18*h*r,radial_f2=r*r/2)
    G=21-1/(2-mu);tp=model['m2']*A-4*H*T;den=G*T/2-tp
    need(not zero(den),'SEED_LOWER_DIVISOR')
    f=3*(mu+4*k)/den;g=G*f/2-2*T
    canonical=[arb(0),H,A,T,arb(1),arb(1),f,g]+[arb(0)]*6
    y=canonical if name=='primary' else canonical[:4]+canonical[5:]
    src=m.sources(y,pars);sc=src[2] if name=='primary' else src['Sc']
    w=wall.reconstruct(canonical,pars,1);R=w['R2'];G=w['Gamma2'];den=G*T/2-tp
    need(not zero(den),'SECOND_LOWER_DIVISOR')
    blocks=[]
    for v,s,loadR in ((arb(0),sc,R),(arb(1),arb(0),arb(0))):
        ff=(s+3*(mu2+4*k)*v-T*loadR/2)/den;gg=G*ff/2+loadR/2-2*T*v
        blocks.extend((v,ff,gg))
    canonical=canonical[:8]+blocks;y=canonical if name=='primary' else canonical[:4]+canonical[5:]
    need(all(zero(v) for v in m.constraints(y,pars).values()),'INITIAL_CONSTRAINTS')
    need(zero(m.first_integral(y,pars)),'INITIAL_BACKGROUND')
    seed=read(SEED/'output'/('strip_'+name+'.json'))['lower_event']
    for key,val in [('psi',canonical[5]),('f',f),('u',w['chi1'])]:
        need(overlap(val,m.interval(*map(fmpq,seed[key]['exact_bounds']))),'SEED_LOWER_REPLAY_'+key)
    return y,pars,cfg['config']['D']

def flow(name,probe=False):
    from flint import arb,fmpq
    m=engines[name];y,p,D=initial(m,name);low=m.physical(y);dlo,dhi=map(fmpq,D)
    step=fmpq(1,4096 if name=='primary' else 8192)
    count=(64 if name=='primary' else 128) if probe else (Q(str(dhi))/Q(str(step))).__ceil__()
    start=time.monotonic();totals={k:arb(0) for k in ('p1','p2P','p2H','c2','p1sq')};budgets=[];covers=[];end=None
    mincells=[];maxpic=0
    def ball(x):return m.interval(*map(fmpq,x['exact_bounds']))
    def export(v):
        a,b=map(lambda x:Q(str(x)),m.bounds(v));scale=1<<80
        lo,hi=Q((a*scale).__floor__(),scale),Q((b*scale).__ceil__(),scale)
        need(lo<=a<=b<=hi,'OUTWARD_EXPORT');raw={'exact_bounds':[str(lo),str(hi)]}
        return raw,ball(raw)
    for i in range(count):
        need(time.time()<DEADLINE and time.monotonic()-start<(600 if probe else 1700),'OPERATIONAL_TIME_BOUND')
        pos=i*step;y,cell=m.step(y,step,p);z=m.physical(cell['box'])
        need(all(v.is_finite() for v in y+cell['box']),'FINITE')
        need(all(zero(v) for v in m.constraints(cell['box'],p).values()),'WHOLE_CELL_CONSTRAINT')
        need(zero(m.first_integral(cell['box'],p)),'WHOLE_CELL_BACKGROUND')
        need(z[4].lower()>0,'WARP');maxpic=max(maxpic,cell['picard_iterations'])
        if zero(z[3]):mincells.append({'index':i,'s':str(pos),'state':[pack(v) for v in z]})
        if not probe:
            src=m.sources(cell['box'],p);c2=src[3] if name=='primary' else src['c2']
            den=dict(p1=z[5],p2P=z[8],p2H=z[11],c2=c2,p1sq=z[5]*z[5])
            mandatory=max(fmpq(0),min(step,dlo-pos));optional=max(fmpq(0),min(step,dhi-pos))-mandatory
            row={'index':i,'s':str(pos),'step':str(step),'mandatory':str(mandatory),'optional':str(optional),'budgets':{}}
            for key,v in den.items():
                raw,re=export(v*mandatory+v*m.interval(fmpq(0),optional));totals[key]+=re;row['budgets'][key]=raw
            budgets.append(row)
            if pos+step>=dlo and pos<=dhi:
                a,b=max(fmpq(0),dlo-pos),min(step,dhi-pos);ev=m.physical(m.range_on_cell(cell,a,b))
                end=ev if end is None else [m.hull(x,v) for x,v in zip(end,ev)]
                covers.append({'lo':str(pos+a),'hi':str(pos+b)})
        if i%128==0:
            print(json.dumps({'engine':name,'probe':probe,'cell':i,'total':count,'seconds':time.monotonic()-start}),flush=True)
            if not probe:put('PROGRESS_'+name+'_'+str(i).zfill(6)+'.json',{'completed_cells':i+1,'total_cells':count,'elapsed_seconds':time.monotonic()-start,'resumable':False})
    if probe:
        result={'pass':True,'engine':name,'seconds':time.monotonic()-start,'cells':count,'maxpic':maxpic,'final':[pack(v) for v in y],
                'linear_full_projection_seconds':(time.monotonic()-start)*(Q(str(dhi))/Q(str(step))).__ceil__()/count}
        put('PROBE_'+name+'.json',result);return result
    last=Q(str(dlo))
    for row in covers:need(Q(row['lo'])==last,'COVER_GAP');last=Q(row['hi'])
    need(last==Q(str(dhi)),'COVER_END')
    lw,uw=wall.reconstruct(low,p,1),wall.reconstruct(end,p,-1)
    selected=read(SEED/'output'/('strip_'+name+'.json'))
    G1=21-1/(2-p['mu1']*end[4]*end[4]);det=end[7]+2*end[3]*end[5]+G1*end[6]/2
    need(zero(det) and overlap(det,ball(selected['event']['determinant'])),'SEED_UPPER_DETERMINANT')
    for key,val in [('psi_b',end[5]),('f_b',end[6]),('u_b',uw['chi1'])]:need(overlap(val,ball(selected['event'][key])),'SEED_UPPER_REPLAY_'+key)
    d1=-2*totals['p1'];need(overlap(d1,ball(selected['observables']['deltaD_over_Q'])),'SEED_DISTANCE_REPLAY')
    T=end[3];G=uw['Gamma2'];fp=end[10]+2*T*end[8]+G*end[9]/2;fh=end[13]+2*T*end[11]+G*end[12]/2
    need(not zero(fh),'SECOND_ORDER_INVERSE_UNRESOLVED');A2=(-uw['R2']/2-fp)/fh
    walls={}
    for side,z,w,sigma in [('lower',low,lw,1),('upper',end,uw,-1)]:
        full=z[:8]+[z[j]+A2*z[j+3] for j in (8,9,10)]+z[11:]
        res=wall.residuals(full,w,p,sigma);need(all(zero(v) for v in res.values()),'WALL_ROWS_'+side)
        walls[side]={'state':[pack(v) for v in full],'loads':{k:pack(v) for k,v in w.items()},'residuals':{k:pack(v) for k,v in res.items()}}
    graph=uw['xi2']-lw['xi2'];bulk=totals['c2']-2*(totals['p2P']+A2*totals['p2H'])+2*totals['p1sq'];d2=graph+bulk
    minimum=None
    for row in mincells:
        z=list(map(ball,row['state']));tp=p['m2']*z[2]-4*z[1]*z[3]
        need(tp.lower()>0,'MINIMUM_NONDEGENERACY')
        v=z[9]+A2*z[12]-z[7]*z[7]/(2*tp)
        minimum=v if minimum is None else m.hull(minimum,v)
    result={'pass':True,'engine':name,'seconds':time.monotonic()-start,'cells':count,'maxpic':maxpic,'D':D,'cover':covers,
            'parameters':{k:pack(v) for k,v in p.items()},'A2':pack(A2),'FH':pack(fh),'FP':pack(fp),'d1':pack(d1),'d2':pack(d2),
            'graph':pack(graph),'bulk':pack(bulk),'minimum_second':pack(minimum) if minimum is not None else None,'minimum_candidate_cells':mincells,
            'totals':{k:pack(v) for k,v in totals.items()},'budgets':budgets,'walls':walls,
            'scope':'Neutral growing-mode quadratic coefficient at psi1(a)=1. No finite-amplitude remainder bound or endpoint fate.'}
    put('PRODUCTION_'+name+'.json',result);return result

def main(mode):
    global engines,wall
    need(sys.platform=='linux' and time.time()<DEADLINE,'LINUX_AND_DEADLINE')
    # Parent root manifest is authenticated by the already sealed cubic-flow manifest.
    flow=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'
    need(sha(flow/'FROZEN.json')=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FLOW_BINDING')
    oldfrozen=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/FROZEN.json'
    need(read(flow/'FROZEN.json')['files'][str(oldfrozen)]==sha(oldfrozen),'OLD_RUNTIME_MANIFEST_BINDING')
    frozen=read(oldfrozen)
    leasepath=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
    need(read(flow/'FROZEN.json')['files'][str(leasepath)]==sha(leasepath),'LEASE_BINDING')
    # The allocation manifest independently pins seed records and copied engines.
    closure=PARENT/'CLOSURE_MANIFEST.json';need(sha(closure)=='2ab20917e9e8d56fc8c285f10099c1fc1e6cc74836e1ebb51716ab13b8fa0751','PARENT_CLOSURE')
    parentfiles={str(PARENT/p):h for p,h in read(closure)['files'].items()}
    for p,h in parentfiles.items():need(sha(p)==h,'PARENT_HASH:'+p)
    lease=load('growing_lease',leasepath);lease.ROOT=ROOT
    try:
        cpu,occupied=lease.acquire();signal.alarm(3300 if mode=='production' else 600)
        put(mode+'_START.json',{'cpu':cpu,'occupied':occupied,'pid':os.getpid(),'start_unix':time.time()})
        sys.path.insert(0,'/home/parallels/research-runs/cap-interval-arb-2026-09-12')
        import flint
        flint.ctx.prec=768;flint.ctx.threads=1
        engines={n:load('growing_'+n,ROOT/(n+'.py')) for n in ('primary','independent')}
        wall=load('growing_wall',ROOT/'wall.py');controls=load('growing_controls',ROOT/'controls.py')
        # Preload optional exact polynomial dependencies before runtime snapshot.
        controls.prepare(ROOT)
        need(len(str(10**20000))==20001,'INTEGER_FORMAT_WARMUP')
        sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='CONTRACT.json'}
        if mode!='controls':
            gate=read(ROOT/'CONTROLS_RESULT.json');need(gate['pass'],'CONTROLS')
            need(read(ROOT/'controls_BINDING.json')['sources']==sources,'FROZEN_SOURCE_CHANGE')
        runtime=lease.observed()
        # All loaded numerical libraries must belong to inherited runtime or this packet.
        for p,h in runtime.items():need(frozen['files'].get(p)==h or sources.get(p)==h or parentfiles.get(p)==h,'UNBOUND_RUNTIME:'+p)
        put(mode+'_BINDING.json',{'sources':sources,'parent_closure_sha256':sha(closure),'runtime':runtime})
        if mode=='controls':put('CONTROLS_RESULT.json',controls.run(ROOT))
        elif mode=='probe':
            results={n:flow(n,True) for n in engines};projection=sum(v['linear_full_projection_seconds'] for v in results.values())*1.5
            put('PROBE_RESULT.json',{'pass':True,'planning_projection_seconds':projection,'production_admissible':projection<3000})
        else:
            probe=read(ROOT/'PROBE_RESULT.json');need(probe['production_admissible'],'PROBE_NOT_ADMITTED')
            need(time.time()+3300<DEADLINE,'INSUFFICIENT_REMAINING_WINDOW')
            results={n:flow(n) for n in engines};m=engines['primary']
            vals=[m.interval(*map(flint.fmpq,v['d2']['exact_bounds'])) for v in results.values()]
            need(overlap(*vals),'ENGINE_DISTANCE_DISAGREEMENT');hull=m.hull(*vals)
            put('RESULT.json',{'pass':True,'d2':pack(hull),'sign':1 if hull.lower()>0 else -1 if hull.upper()<0 else 0,
                'classification':'NEUTRAL_GROWING_QUADRATIC_COMPUTED_AUDIT_PENDING','normalization':'psi1(lower)=1',
                'scope':'Quadratic local unstable-mode response; no finite-amplitude validity or nonlinear endpoint claim.'})
        after=lease.observed();need(runtime==after,'RUNTIME_DRIFT')
        need(all(sha(p)==h for p,h in sources.items()),'SOURCE_DRIFT')
        need(all(sha(p)==h for p,h in parentfiles.items()),'PARENT_DRIFT')
        put(mode+'_TERMINAL.json',{'pass':True,'runtime_unchanged':True,'source_unchanged':True,'parent_unchanged':True,
            'artifacts':{p.name:sha(p) for p in ROOT.glob('*.json') if not p.name.endswith('_START.json')},'finished_unix':time.time()})
    finally:
        signal.alarm(0)
        for h in lease.handles:h.close()
if __name__=='__main__':
    mode=sys.argv[1];need(mode in ('controls','probe','production'),'MODE')
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('BOUNDED_'+mode)))
        main(mode)
    except BaseException as e:
        put(mode+'_FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(e),'traceback':traceback.format_exc()});raise
