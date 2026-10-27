"""Upper-emitter radar from saved validated cells and four predeclared minors."""
import importlib.util, os, signal, time, traceback
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); return v
c=module('upper_radar_common',ROOT/'common.py'); c.ROOT=ROOT; c.OUT=ROOT/'output'
f=module('upper_radar_fraction',ROOT/'fraction_common.py'); I=f.I
PARENTS={'t2':'T2R1_AB_SELECTED_MODE','t8':'T8_AB_NEUTRAL_RADAR_RESPONSE',
         't10':'T10_AB_CURRENT_RADAR_RESPONSE','t12':'T12_AB_THREE_READOUT_IDENTIFIABILITY'}
ROWS=('proper_separation','minimum_scalar_value','lower_emitter_elapsed_radar','upper_emitter_elapsed_radar')
MINORS=tuple(combinations(range(4),3))
def p(key,file): return ROOT/'..'/PARENTS[key]/file
def determinant(cols):
    a,b,d=cols
    return a[0]*(b[1]*d[2]-b[2]*d[1])-b[0]*(a[1]*d[2]-a[2]*d[1])+d[0]*(a[1]*b[2]-a[2]*b[1])

def controls():
    Ea,Eb,xa,xb=map(Q,('2/3','3/2','4/7','-5/11'))
    for rate,u in ((Q(2,3),Q(7,5)),(Q(-2,3),Q(3,5))):
        first=Eb*xb-Ea*u*xa; second=Eb*u*u*xb-Ea*u*xa
        graph=Eb*(1+u*u)*xb-2*Ea*u*xa
        c.need(first+second==graph,'REVERSED_GRAPH_TWO_LEGS')
        J=(u*u-1)/rate; P=Q(3,7)
        c.need((u-1)/rate+(u*u-u)/rate==J,'REVERSED_FLAT_TIME_WEIGHTS')
        c.need(-3*P*J+P*J==-2*P*J,'REVERSED_FLAT_CLOCK')
        beta=Q(5,13); c.need(beta*(u*u-1)-rate*beta*J==0,'UPPER_TEMPORAL_GAUGE_CLOCK')
        E,H,alpha,ap,wd,wu=map(Q,('2/3','-3/5','5/7','7/11','11/13','13/17'))
        # Down-leg has the negative shift contribution, up-leg positive.
        integrand=E*(H*alpha-ap)*(wd+wu)-rate*alpha*E*E*(wu-wd)
        derivative=-(E*(ap-H*alpha)*(wd+wu)+E*alpha*rate*E*(wu-wd))
        c.need(integrand==derivative,'REVERSED_RADIAL_GAUGE_DERIVATIVE')
        boundary=-Eb*xb*(1+u*u)+2*Ea*xa*u
        c.need(graph+boundary==0,'REVERSED_GAUGE_ENDPOINTS')
        c.need(-H*alpha+H*alpha==0,'UPPER_RADIAL_GAUGE_CLOCK')
    D=Q(5,11); P=Q(3,7)
    c.need(-3*P*2*D+P*2*D==-4*P*D,'STATIC_FLAT_LIMIT')
    c.need((1+Q(1))*xb-2*xa==2*(xb-xa),'STATIC_GRAPH_LIMIT')
    cols=[list(map(Q,v)) for v in ((2,3,5),(7,11,13),(17,19,23))]
    c.need(determinant([cols[1],cols[0],cols[2]])==-determinant(cols),'MINOR_PERMUTATION')
    c.need(determinant([cols[0],cols[1],[a+b for a,b in zip(cols[0],cols[1])]])==0,'DEPENDENT_CONTROL')
    c.need(len(MINORS)==4 and MINORS==((0,1,2),(0,1,3),(0,2,3),(1,2,3)),'ALL_PREDECLARED_MINORS')
    return {'reversed_graphs':True,'both_rate_sign_flat_time_weights':True,'radial_shift_gauge':True,
            'temporal_gauge':True,'static_limits':True,'minor_permutation':True,'dependent_columns':True,'all_four_minors':True}

def parent_gate():
    g=c.read(ROOT/'ADMISSION.json')
    required=[]
    for key,folder in PARENTS.items():
        c.need(g.get(key+'_terminal_review_accepted') is True,'REVIEW_REQUIRED:'+key)
        suffix='RESULT.json' if key=='t12' else 'output/RESULT.json'
        required+=['../'+folder+'/TERMINAL_REVIEW.md','../'+folder+'/'+suffix]
    for name in ('primary','independent'):
        required+=['../'+PARENTS['t2']+'/output/strip_'+name+'.json',
                   '../'+PARENTS['t8']+'/output/radar_'+name+'.json','../'+PARENTS['t8']+'/output/'+name+'_RADAR_BUDGET.json',
                   '../'+PARENTS['t10']+'/output/current_radar_'+name+'.json']
        for kind in ('homogeneous','particular_lower'):
            required+=['../'+PARENTS['t10']+'/output/'+kind+'_'+name+suffix for suffix in ('.json','_RADAR_BUDGET.json')]
    for rel in required: c.need(rel in g['sources'],'MISSING_PARENT_BINDING:'+rel)
    c.need(c.read(p('t2','output/RESULT.json'))['classification']=='SELECTED_NEUTRAL_MODE_CHARACTERIZED','T2_SCOPE')
    c.need(c.read(p('t8','output/RESULT.json'))['classification']=='NEUTRAL_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','T8_SCOPE')
    c.need(c.read(p('t10','output/RESULT.json'))['classification']=='FIRST_CURRENT_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','T10_SCOPE')
    rank=c.read(p('t12','RESULT.json')); c.need(rank['classification']=='UNRESOLVED','PRESERVE_T12_UNRESOLVED')
    return rank

def weighted(name,key,record,budget_path,rate,begun):
    from flint import arb
    m=c.load(name); c.need(c.sha(budget_path)==record['budget']['sha256'],'PARENT_BUDGET_HASH')
    budget=c.read(budget_path); L=c.ball_record(m,budget['L']); c.need(L.lower()>0,'OPTICAL_LENGTH')
    Dlo,Dhi=map(Q,budget['D_bounds']); expected=Q(0); mandatory_sum=Q(0); possible_sum=Q(0)
    total=arb(0); rows=[]
    for j,row in enumerate(budget['cells']):
        if j%64==0: c.need(time.monotonic()-begun<900,'TOTAL_CAP')
        s,h,mandatory,optional=map(Q,(row['s'],row['step'],row['mandatory'],row['optional']))
        c.need(row['index']==j and s==expected,'CELL_CHAIN'); expected=s+h
        c.need(mandatory==max(Q(0),min(h,Dlo-s)) and mandatory+optional==max(Q(0),min(h,Dhi-s)),'CELL_DOMAIN')
        mandatory_sum+=mandatory; possible_sum+=mandatory+optional
        E=c.ball_record(m,row['E']); psi=c.ball_record(m,row['psi']); tau=c.ball_record(m,row['tau_box'])
        c.need(E.lower()>0,'POSITIVE_OPTICAL_DENSITY')
        # Outward/return times from upper emitter are L-tau and L+tau.
        kernel=(rate*(L-tau)).exp()+(rate*(L+tau)).exp()
        raw_kernel,kr=c.dyadic_export(m,kernel)
        from flint import fmpq
        raw,back=c.dyadic_export(m,c.integral_piece(m,E*psi*kr,fmpq(str(mandatory)),fmpq(str(optional))))
        total+=back
        rows.append({'index':j,'s':str(s),'step':str(h),'mandatory':str(mandatory),'optional':str(optional),
                     'upper_kernel':raw_kernel,'weighted_contribution':raw})
    c.need(mandatory_sum==Dlo and possible_sum==Dhi,'FULL_DOMAIN')
    filename=key+'_'+name+'_UPPER_KERNEL_BUDGET.json'
    c.put(filename,{'parent_budget':str(budget_path),'parent_budget_sha256':c.sha(budget_path),'D_bounds':budget['D_bounds'],
                   'L':c.pack(L),'rate':c.pack(rate),'weighted_integral':c.pack(total),'cells':rows,
                   'premise':'Inherited validated E,psi,tau boxes; outward Arb exponential plus outward dyadic contributions. No midpoint replacement.'})
    return total,L,budget['D_bounds'],{'path':filename,'sha256':c.sha(c.OUT/filename)}

def evaluate(name,rank,begun):
    from flint import arb
    m=c.load(name); ball=lambda v:c.ball_record(m,v)
    neutral=c.read(p('t8','output/radar_'+name+'.json')); old=c.read(p('t2','output/strip_'+name+'.json'))
    c.need(neutral['mu_bounds']==old['mu_bounds'],'NEUTRAL_MASS_MATCH')
    rate=ball(neutral['observables']['gamma'])
    w,L,D,nb=weighted(name,'neutral',neutral,p('t8','output/'+neutral['budget']['path']),rate,begun)
    # Endpoint source fixed prospectively: matched T2R1 event, not a selectable endpoint estimate.
    ab=ball(old['event']['a_squared_b']).sqrt(); Pb=ball(old['event']['psi_b'])
    c.need(ab.lower()>0 and rate.lower()>0,'NEUTRAL_UPPER_DOMAIN')
    J=((2*rate*L).exp()-1)/rate; neutral_clock=ab*Pb*J; neutral_bulk=-3*ab*w
    upper={'neutral':{'proper_roundtrip':neutral_bulk+neutral_clock,'proper_bulk':neutral_bulk,'proper_graph':arb(0),'emitter_clock':neutral_clock}}
    saved=c.read(p('t10','output/current_radar_'+name+'.json')); assembly=saved['full_forced_assembly']['channels']
    flows={}; pieces={}; budgets={'neutral':nb}
    for kind in ('homogeneous','particular_lower'):
        rec=c.read(p('t10','output/'+kind+'_'+name+'.json')); flows[kind]=rec
        result=weighted(name,kind,rec,p('t10','output/'+rec['budget']['path']),ball(rec['rate']),begun)
        c.need(result[2]==D,'SAME_BACKGROUND_DOMAIN'); pieces[kind]=result; budgets[kind]=result[3]
    c.need(c.overlaps(pieces['homogeneous'][1],pieces['particular_lower'][1]),'CURRENT_OPTICAL_BACKGROUND')
    Lc=m.hull(pieces['homogeneous'][1],pieces['particular_lower'][1])
    c.need(c.overlaps(L,Lc),'NEUTRAL_CURRENT_OPTICAL_BACKGROUND')
    rh=ball(flows['homogeneous']['rate']); rp=ball(flows['particular_lower']['rate']); c.need(c.overlaps(rh,rp),'CURRENT_RATE_MATCH')
    r=m.hull(rh,rp); c.need(r.upper()<0,'CURRENT_RATE_NEGATIVE'); Jc=((2*r*Lc).exp()-1)/r
    for side in ('lower','upper'):
        parent=assembly[side]; amp=ball(parent['homogeneous_multiplier'])
        wa={k:ball(v) for k,v in parent['walls']['lower'].items()}; wb={k:ball(v) for k,v in parent['walls']['upper'].items()}
        integral=amp*pieces['homogeneous'][0]+(pieces['particular_lower'][0] if side=='lower' else arb(0))
        abi=1/wb['E']; graph=wb['E']*(1+(2*r*Lc).exp())*wb['xi']-2*wa['E']*(r*Lc).exp()*wa['xi']
        bulk=-3*abi*integral; graph=abi*graph; clock=abi*(wb['psi']+wb['H']*wb['xi'])*Jc
        upper[side+'_current']={'proper_roundtrip':bulk+graph+clock,'proper_bulk':bulk,'proper_graph':graph,'emitter_clock':clock,
                              'proper_density_roundtrip':ball(parent['source_wall_a6'])*(bulk+graph+clock)}
    ranked=rank['per_engine'][name]; raw=[[f.interval(v) for v in col] for col in ranked['raw_columns']]
    c.need(ranked['column_order']==['neutral','lower_current','upper_current'],'COLUMN_ORDER')
    columns=[]
    for col,key in zip(raw,('neutral','lower_current','upper_current')):
        c.need(col[1].lo>0,'POSITIVE_MINIMUM_NORMALIZATION')
        u=f.interval(c.pack(upper[key]['proper_roundtrip']))
        columns.append([col[0]/col[1],I(1),col[2]/col[1],u/col[1]])
    minors={}
    for indices in MINORS:
        value=determinant([[col[i] for i in indices] for col in columns])
        minors['_'.join(map(str,indices))]={'rows':[ROWS[i] for i in indices],'determinant':value.pack(),
               'classification':'UNRESOLVED' if value.zero() else 'LOCAL_LINEAR_READOUT_INJECTIVITY'}
    inherited=f.interval(ranked['authoritative_normalized_determinant'])
    c.need(f.interval(minors['0_1_2']['determinant']).overlap(inherited),'T12_MINOR_REPRODUCTION')
    c.need(inherited.zero(),'T12_REMAINS_UNRESOLVED')
    minors['0_1_2']['independent_reconstruction_consistency_only']=minors['0_1_2']['determinant']
    minors['0_1_2']['determinant']=inherited.pack()
    minors['0_1_2']['classification']='UNRESOLVED'
    minors['0_1_2']['authority']='Unchanged T12 authoritative determinant; no rescoring.'
    return {'engine':name,'upper_observer_readouts':{key:{k:c.pack(v) for k,v in vals.items()} for key,vals in upper.items()},
            'normalized_four_readout_columns':[[v.pack() for v in col] for col in columns],
            'minors':minors,'kernel_budgets':budgets,'T12_original_classification':'UNRESOLVED','D_bounds':D}

def main():
    c.OUT.mkdir(exist_ok=True); c.need(not any((c.OUT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('UPPER_RADAR_RANK_CAP_900_SECONDS'))); signal.alarm(900)
        c.authenticate(); rank=parent_gate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested=controls(); c.put('CONTROLS.json',tested); per={}
        for name in ('primary','independent'):
            per[name]=evaluate(name,rank,begun); c.put('upper_radar_rank_'+name+'.json',per[name])
        c.need(per['primary']['D_bounds']==per['independent']['D_bounds'],'ENGINE_DOMAIN_MATCH')
        obs={}; minors={}
        for direction in ('neutral','lower_current','upper_current'):
            obs[direction]={}
            for key in per['primary']['upper_observer_readouts'][direction]:
                a,b=[f.interval(per[n]['upper_observer_readouts'][direction][key]) for n in ('primary','independent')]
                c.need(a.overlap(b),'UPPER_RADAR_ENGINE_DISAGREEMENT:'+direction+':'+key); obs[direction][key]=a.hull(b).pack()
        for indices in MINORS:
            key='_'.join(map(str,indices)); a,b=[f.interval(per[n]['minors'][key]['determinant']) for n in ('primary','independent')]
            c.need(a.overlap(b),'MINOR_ENGINE_DISAGREEMENT:'+key); value=a.hull(b)
            minors[key]={'rows':[ROWS[i] for i in indices],'determinant':value.pack(),
                         'classification':'UNRESOLVED' if value.zero() else 'LOCAL_LINEAR_READOUT_INJECTIVITY'}
        resolved=[key for key,row in minors.items() if row['classification']=='LOCAL_LINEAR_READOUT_INJECTIVITY']
        c.put('RESULT.json',{'classification':'LOCAL_LINEAR_READOUT_INJECTIVITY' if resolved else 'UNRESOLVED',
               'upper_observer_readouts':obs,'all_predeclared_minors':minors,'resolved_minors':resolved,
               'T12_original_classification_preserved':'UNRESOLVED','controls':tested,'seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'New upper-emitter ideal radar measurement and four fixed minors at linear order. No rescoring of T12, conditioning claim, noise robustness, modal excitation or nonlinear inverse; currents occupy a nonnegative cone.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
