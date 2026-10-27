"""Full two-engine cubic flow with bounded-memory streamed witnesses."""
import resource,sys,time
from fractions import Fraction as Q
from flint import arb,fmpq
import probe as c
from storage import ROOT,sha,read,put,digest
PROBE=ROOT.parent/'20261026T033000Z_CUBIC_PROBE_R1'
def vector(values):return [c.pack(v) for v in values]
def match(z,p,R):
    T,E=z[3],z[4];G=21-1/(2+270*p['k']*E*E)
    FP=z[16]+2*T*z[14]+G*z[15]/2
    FH=z[19]+2*T*z[17]+G*z[18]/2
    return G,FP,FH
def physical_rows(z,p,A,R,side):
    T,E=z[3],z[4];Tp=p['m2']*z[2]-4*z[1]*T
    a,f,g=[z[j]+A*z[j+3] for j in (14,15,16)]
    G=21-1/(2+270*p['k']*E*E)
    robin=2*(g+2*T*a)+side*G*f-R
    constraint=T*g-Tp*f+(2*T*T+798*p['k']*E*E)*a-c.source_at(z,p)['Sc3']
    return {'robin':c.pack(robin),'constraint':c.pack(constraint),'state':vector([a,f,g])}
def run_arm(name,binding):
    m=c.ENGINES[name];y,p,launch=c.initial(name);initial=vector(y);params={k:c.pack(v) for k,v in p.items()};ph=digest(params)
    h=fmpq(1,4096 if name=='primary' else 8192);dlo,dhi=map(fmpq,launch['D']);count=(Q(str(dhi))/Q(str(h))).__ceil__()
    need=c.need;need(dlo>0 and dlo<=dhi,'DOMAIN');start=time.monotonic();chunks=[];pending=[];previous=None;maxpic=0;maxwidth=[fmpq(0) for _ in y];upper=None;cover=[]
    anchor=read(PROBE/('PROBE_'+name+'.json'));anchor_n=anchor['cells'];anchor_pass=False
    def publish():
        nonlocal pending,previous
        first=pending[0]['index'];last=pending[-1]['index'];filename=f'chunks/{name}/{first:06d}.json'
        payload={'engine':name,'binding_sha256':binding,'parameters_sha256':ph,'previous_sha256':previous,'first':first,'last':last,'records':pending}
        ch=put(filename,payload)
        checkpoint=f'checkpoints/{name}/{last+1:06d}.json'
        cp=put(checkpoint,{'engine':name,'binding_sha256':binding,'parameters_sha256':ph,'chunk_sha256':ch,'completed':last+1,'total':count,'state':pending[-1]['end'],'elapsed_seconds':time.monotonic()-start,'resume_supported':False})
        chunks.append({'file':filename,'sha256':ch,'first':first,'last':last,'checkpoint':checkpoint,'checkpoint_sha256':cp});previous=ch;pending=[]
    for j in range(count):
        before=list(y);y,cell=m.step(y,h,p);pos=j*h
        need(all(v.is_finite() for v in y+cell['box']),'FINITE_CELL:'+name+str(j))
        constraints=m.constraints(cell['box'],p);need(all(c.zero(v) for v in constraints.values()),'WHOLE_CONSTRAINT:'+name+str(j))
        bg=m.first_integral(cell['box'],p);need(c.zero(bg),'WHOLE_BACKGROUND:'+name+str(j))
        maxpic=max(maxpic,cell['picard_iterations'])
        for k,v in enumerate(cell['box']):maxwidth[k]=max(maxwidth[k],v.upper().fmpq()-v.lower().fmpq())
        record={'index':j,'start':vector(before),'end':vector(y),'box':vector(cell['box']),'rhs_box':vector(m.rhs(cell['box'],p)),
                'point_coefficients':[vector(row) for row in cell['point_coefficients']],'remainder_coefficient':vector(cell['remainder_coefficient']),
                'constraints':{k:c.pack(v) for k,v in constraints.items()},'background':c.pack(bg),'picard_iterations':cell['picard_iterations']}
        if pos+h>=dlo and pos<=dhi:
            lo=max(fmpq(0),dlo-pos);hi=min(h,dhi-pos);raw=m.range_on_cell(cell,lo,hi);event=m.physical(raw)
            need(all(v.is_finite() for v in event),'FINITE_EVENT')
            upper=event if upper is None else [m.hull(a,b) for a,b in zip(upper,event)]
            record['event']={'offset_lo':str(lo),'offset_hi':str(hi),'raw':vector(raw),'physical':vector(event)}
            cover.append({'index':j,'lo':str(pos+lo),'hi':str(pos+hi)})
        pending.append(record)
        if j+1==anchor_n:
            need(vector(y)==anchor['final'],'SEALED_PROBE_BITWISE_ANCHOR:'+name);anchor_pass=True
        if len(pending)==32 or j+1==count:publish()
        if (j+1)%256==0 or j+1==count:print(name,j+1,'/',count,'seconds',round(time.monotonic()-start,1),flush=True)
    end=Q(str(dlo))
    for piece in cover:need(Q(piece['lo'])==end,'COVER_GAP');end=Q(piece['hi'])
    need(end==Q(str(dhi)) and upper is not None and anchor_pass,'COVER_COMPLETE')
    parent=read(c.PARENT/('PRODUCTION_'+name+'.json'))
    need(all(c.overlap(a,c.iv(b)) for a,b in zip(upper[:14],parent['raw_upper'])),'LOWER_ORDER_ENDPOINT_REPLAY')
    R=c.iv(read(c.SYSTEM/'RESULT.json')['per_engine'][name]['upper']['R3']);G,FP,FH=match(upper,p,R)
    matched={'resolved':not c.zero(FH),'Gamma3':c.pack(G),'FP3':c.pack(FP),'FH3':c.pack(FH),'R3_upper':c.pack(R)}
    if matched['resolved']:
        A=(-R/2-FP)/FH;need(A.is_finite(),'FINITE_A3');matched['A3']=c.pack(A)
        low=m.physical(list(map(c.iv,initial)));rl=c.iv(launch['R3_lower'])
        matched['lower']=physical_rows(low,p,A,rl,-1);matched['upper']=physical_rows(upper,p,A,-R,1)
        for side in ('lower','upper'):
            for key in ('robin','constraint'):need(c.zero(c.iv(matched[side][key])),'MATCHED_ROW:'+name+side+key)
    result={'pass':True,'engine':name,'cells':count,'step':str(h),'D':list(map(str,(dlo,dhi))),'initial':initial,'final':vector(y),'physical_upper':vector(upper),'parameters':params,'parameters_sha256':ph,'launch':launch,
            'chunks':chunks,'cover':cover,'anchor_pass':anchor_pass,'max_picard_iterations':maxpic,'max_box_widths':list(map(str,maxwidth)),
            'matching':matched,'seconds':time.monotonic()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    put('FLOW_'+name+'.json',result);return result
def run():
    c.need(sys.platform=='linux','LINUX_ONLY');controls=c.controls();put('CONTROLS_RESULT.json',controls)
    binding=sha(ROOT/'FROZEN.json');arms={name:run_arm(name,binding) for name in ('primary','independent')}
    c.need(all(c.overlap(c.iv(a),c.iv(b)) for a,b in zip(arms['primary']['physical_upper'],arms['independent']['physical_upper'])),'ENGINE_ENDPOINT_OVERLAP')
    resolved=all(a['matching']['resolved'] for a in arms.values());result={'pass':True,'classification':'CUBIC_FULL_FLOW_UPPER_INVERSE_RESOLVED' if resolved else 'CUBIC_FULL_FLOW_UPPER_INVERSE_UNRESOLVED',
           'source_and_recurrence_checks':len(controls['checks']),'arms':{n:{k:a[k] for k in ('cells','seconds','peak_rss_kib','max_picard_iterations','matching')} for n,a in arms.items()},'full_distance_computed':False}
    if resolved:
        a,b=[c.iv(r['matching']['A3']) for r in arms.values()];c.need(c.overlap(a,b),'ENGINE_A3_OVERLAP');result['A3_hull']=c.pack(c.primary.hull(a,b))
    return result
