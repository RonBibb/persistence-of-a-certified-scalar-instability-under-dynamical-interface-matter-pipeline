"""Whole-cell lower-order replay and real inverse enclosure of actual d4."""
from fractions import Fraction as Q

def setup(driver,closed,wall4,arb_type,fmpq_type,read_fn,put_fn,base):
 global drv,source,newwall,arb,fmpq,read,put,BASE
 drv,source,newwall,arb,fmpq,read,put,BASE=driver,closed,wall4,arb_type,fmpq_type,read_fn,put_fn,base

def need(v,s):
 if not v:raise AssertionError(s)
def pack(v):
 need(v.is_finite(),'FINITE_EXPORT');return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def iv(v):return drv.engines['primary'].interval(*map(fmpq,v['exact_bounds']))
def ab(v):return max(abs(Q(str(v.lower().fmpq()))),abs(Q(str(v.upper().fmpq()))))
def lower(v):return Q(str(v.lower().fmpq()))
def zero(v):return v.lower()<=0<=v.upper()
def overlap(a,b):return a.lower()<=b.upper() and b.lower()<=a.upper()

def fields(z,p):
 W,H,Phi,T,E,a,f,g=z[:8];A2,A3=p['A2'],p['A3']
 P,F,G=[z[j]+A2*z[j+3] for j in (8,9,10)]
 p3,f3,g3=[z[j]+A2*z[j+3]+A3*z[j+6] for j in (14,15,16)]
 c2=-p['c_factor']*(6*a*a+f*f)
 s3=drv.adapters.sources_affine.base.cubic(H,T,Phi,E*E,a,f,g,P,F,G,p)
 s4=source.quartic(H,T,Phi,E*E,a,f,g,P,F,G,p3,f3,g3,p,drv.adapters.sources_affine.base)
 D=2*T*T-3*(p['mu4']+4*p['k'])*E*E
 need(D.lower()>0,'FOURTH_POSITIVE_D')
 B0=12*H*T-4*p['m2']*Phi;Tp=p['m2']*Phi-4*H*T
 force=s4['Sg4']+B0*s4['Sc4']/D
 b1=-2*a;b2=c2-2*P;b3=s3['c3']-2*p3
 known=s4['c4']+b1*b3+b2*b2/2+b1*b1*b2/2+b1*b1*b1*b1/24
 return dict(s4=s4,D=D,Tp=Tp,forcing=force,known_density=known,b1=b1,b2=b2,b3=b3,p2=P,f2=F,g2=G,p3=p3,f3=f3,g3=g3,c2=c2,c3=s3['c3'])

def wall(z,p,sigma):
 q=fields(z,p);w0,w1,data,tangent=drv.wall_load(z,p,sigma);A2=p['A2']
 full={k:v+A2*tangent[k] if k in tangent else v for k,v in data.items()}
 xi3=w0['xi3']+A2*w1['xi3'];o3=w0['o3']+A2*w1['o3']
 full.update(p3=q['p3'],f3=q['f3'],g3=q['g3'],xi3=xi3,chi3=(q['f3']+z[3]*xi3-o3)/w0['d3'])
 H,Phi,T,E=z[1:5];u1=full['u1'];a,f,g=z[5:8];Tp=q['Tp'];Hp=-T*T/3-p['k']*E*E
 sp2,sg2,_,_=drv.engines['primary'].lower.sources(z[:14],p)
 full.update(Hp=Hp,Tpp=p['m2']*T-4*Hp*T-4*H*Tp,u2=-2*H*q['p2']-T*q['f2']/3+sp2,
             g2prime=-4*H*q['g2']+(p['m2']-p['mu2']*E*E+2*T*T)*q['f2']+(12*H*T-4*p['m2']*Phi)*q['p2']+sg2,
             c2prime=-p['c_factor']*(12*a*u1+2*f*g))
 direct=newwall.direct(full,sigma);o,j,qi=[direct[k].a[4] for k in ('O','J','graph')]
 dg=4*sigma*E*E*p['rate']*(4*p['rate']-p['h']);d=2-p['mu4']*E*E
 need(not zero(dg) and d.lower()>0,'FOURTH_WALL_DIVISORS');xi4=-qi/dg;Gamma=21-1/d
 R=2*sigma*(T*q['s4']['c4']-Tp*xi4-j)+Gamma*T*xi4+o/d
 J=q['D']-2*T*T;need(J.lower()>0,'FOURTH_ROBIN_J_POSITIVE')
 robin=-q['D']*R/(2*J)+2*sigma*T*q['s4']['Sc4']/J
 transport=xi3*q['b1']+full['xi2']*(q['b2']+q['b1']*q['b1']/2)
 # Existing full lower-order wall equations must still close.
 old=drv.wall.extract(full,sigma)
 need(all(zero(old['full'][key].a[3]) for key in ('O','J','graph')),'LOWER_CUBIC_WALL_REPLAY')
 return dict(data=full,xi4=xi4,robin=robin,transport=transport,o4=o,j4=j,qI4=qi,R4=R,D4=q['D'],J4=J)

def run(name,probe=False):
 import time
 start=time.monotonic();m=drv.engines[name];y,p,D=drv.initial(name);low=m.physical(y)
 old=read(BASE/'20261026_GROWING_MODE_CUBIC_AFFINE'/('PRODUCTION_'+name+'.json'))
 p.update(A3=iv(old['A3']),mu4=-4*p['rate']*(4*p['rate']+3*p['h']),c4_factor=p['rate']/(4*(4*p['rate']-p['h'])))
 fresh=read(BASE/'20261026_GROWING_INVERSE_READINESS_R1'/('INITIAL_'+name+'.json'))
 nbg=fresh['background_native_dimension'];need([pack(v) for v in y[:nbg]]==fresh['initial_native'][:nbg],'INVERSE_BACKGROUND_INITIAL_IDENTITY')
 need(D==fresh['D'],'INVERSE_DOMAIN_IDENTITY')
 for key,value in fresh['parameters'].items():need(pack(p[key])==value,'INVERSE_PARAMETER_IDENTITY:'+key)
 for side,z in [('lower',low)]:
  need(len(z)==len(old['walls'][side]['raw'])==23,'CUBIC_ENTRY_LENGTH')
  need(all(pack(v)==vold for v,vold in zip(z,old['walls'][side]['raw'])),'EXACT_CUBIC_INITIAL_REPLAY')
 wlo=wall(low,p,1);step=fmpq(1,4096 if name=='primary' else 8192);dlo,dhi=map(fmpq,D)
 full=(Q(str(dhi))/Q(str(step))).__ceil__();count=(64 if name=='primary' else 128) if probe else full
 total=arb(0);end=None;coverage=[];rows=[];chunks=[];prior=None
 extrema=dict(forcing=Q(0),Sc4=Q(0),T=Q(0),Tp=Q(0));dmin=None;maxpic=0
 for i in range(count):
  need(time.monotonic()-start<(600 if probe else 2400),'PREDECLARED_RESOURCE_CAP')
  pos=i*step;y,cell=m.step(y,step,p);z=m.physical(cell['box'])
  need(all(v.is_finite() for v in y+cell['box']),'FINITE_CELL')
  constraints=m.constraints(cell['box'],p);first_integral=m.first_integral(cell['box'],p)
  need(all(zero(v) for v in constraints.values()),'LOWER_WHOLE_CELL_CONSTRAINTS')
  need(zero(first_integral) and z[4].lower()>0,'BACKGROUND_GATE')
  q=fields(z,p);maxpic=max(maxpic,cell['picard_iterations'])
  vals=dict(forcing=ab(q['forcing']),Sc4=ab(q['s4']['Sc4']),T=ab(z[3]),Tp=ab(q['Tp']))
  for k,v in vals.items():extrema[k]=max(extrema[k],v)
  dmin=lower(q['D']) if dmin is None else min(dmin,lower(q['D']))
  mandatory=max(fmpq(0),min(step,dlo-pos));optional=max(fmpq(0),min(step,dhi-pos))-mandatory
  budget=q['known_density']*mandatory+q['known_density']*m.interval(fmpq(0),optional);total+=budget
  if pos+step>=dlo and pos<=dhi:
   a,b=max(fmpq(0),dlo-pos),min(step,dhi-pos);ev=m.physical(m.range_on_cell(cell,a,b))
   end=ev if end is None else [m.hull(x,v) for x,v in zip(end,ev)];coverage.append(dict(lo=str(pos+a),hi=str(pos+b)))
  rows.append(dict(index=i,s=str(pos),step=str(step),mandatory=str(mandatory),optional=str(optional),canonical_box=[pack(v) for v in z],constraint_enclosures={k:pack(v) for k,v in constraints.items()},background_first_integral=pack(first_integral),source_suprema={k:str(v) for k,v in vals.items()},D_lower=str(lower(q['D'])),known_density=pack(q['known_density']),integral_budget=pack(budget),constraints_contain_zero=True))
  if (i+1)%256==0 or i+1==count:
   print(__import__('json').dumps(dict(engine=name,probe=probe,completed=i+1,total=count,seconds=time.monotonic()-start)),flush=True)
   if True:
    stem=('probe_' if probe else '')+name+'_'+str(i+1).zfill(6);chunk='CHUNK_'+stem+'.json';cp='CHECKPOINT_'+stem+'.json'
    put(chunk,dict(engine=name,binding_sha256=BINDING,previous_sha256=prior,records=rows));digest=SHA(ROOT/chunk)
    put(cp,dict(engine=name,binding_sha256=BINDING,chunk_sha256=digest,completed=i+1,total=count,state=[pack(v) for v in y],integral=pack(total),extrema={k:str(v) for k,v in extrema.items()},D_lower=str(dmin),resumable=False,seconds=time.monotonic()-start))
    chunks.append(dict(file=chunk,sha256=digest,checkpoint=cp,checkpoint_sha256=SHA(ROOT/cp)));prior=digest;rows=[]
 if probe:
  out=dict(pass_status=True,cells=count,seconds=time.monotonic()-start,projection_seconds=(time.monotonic()-start)*full/count,full_cells=full,maxpic=maxpic,chunks=chunks,scope='Resource and whole-cell admissibility probe; no full-domain quartic bound.')
  put('PROBE_'+name+'.json',out);return out
 cursor=Q(str(dlo))
 for row in coverage:need(Q(row['lo'])==cursor,'ENDPOINT_COVER_GAP');cursor=Q(row['hi'])
 need(cursor==Q(str(dhi)) and end is not None,'FULL_ENDPOINT_COVER')
 need(len(end)==len(old['walls']['upper']['raw'])==23,'CUBIC_ENDPOINT_LENGTH')
 need(all(overlap(v,iv(vold)) for v,vold in zip(end,old['walls']['upper']['raw'])),'UPPER_CUBIC_REPLAY')
 whi=wall(end,p,-1)
 for side,w in [('lower',wlo),('upper',whi)]:
  for key,value in old['walls'][side]['data'].items():need(overlap(w['data'][key],iv(value)),'ACTUAL_CUBIC_WALL_REPLAY:'+side+':'+key)
 inverse=read(BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json');need(inverse['scientific_certificate'],'INVERSE_CERTIFIED')
 inverse_arm=inverse['arms'][name];Cf4=Q(inverse_arm['finite_orders']['4']['constant'])*Q(inverse_arm['f_transfer_multiplier'])
 need(Cf4>0 and dmin>0,'POSITIVE_INVERSE_AND_D')
 G=max(ab(wlo['robin']),ab(whi['robin']));S=extrema['forcing']+4*G;fbound=Cf4*S/16;gBound=Cf4*S/4
 pbound=(extrema['Sc4']+extrema['T']*gBound+extrema['Tp']*fbound)/dmin
 known=whi['xi4']-wlo['xi4']+whi['transport']-wlo['transport']+total
 pb=2*Q(str(dhi))*pbound;enclosure=known+m.interval(fmpq(str(-pb)),fmpq(str(pb)))
 out=dict(pass_status=True,engine=name,cells=count,seconds=time.monotonic()-start,maxpic=maxpic,D=D,lower_canonical=[pack(v) for v in low],upper_canonical=[pack(v) for v in end],coverage=coverage,chunks=chunks,parameters={k:pack(v) for k,v in p.items()},extrema={k:str(v) for k,v in extrema.items()},D_lower=str(dmin),Cf4=str(Cf4),Robin_abs=str(G),source_size=str(S),f4_bound=str(fbound),f4prime_bound=str(gBound),p4_bound=str(pbound),known_integral=pack(total),known_distance_part=pack(known),unknown_metric_integral_bound=str(pb),d4=pack(enclosure),walls={side:{k:pack(v) for k,v in w.items() if k!='data'} for side,w in [('lower',wlo),('upper',whi)]},scope='Physical-source-informed unsigned enclosure of actual unique quartic coefficient; not a solved quartic profile or sign.')
 put('ARM_'+name+'.json',out);return out
