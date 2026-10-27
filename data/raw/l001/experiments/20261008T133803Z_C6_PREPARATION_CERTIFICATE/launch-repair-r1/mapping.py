"""Full-domain bounds at common u=s/D, conditional on certified preparation."""
from common import *
from inherited.series import bounds, interval, hull
from inherited.algebra import ev, Taylor
from inherited import validated
import physics
import math
def magnitude(x):return max(abs(v) for v in bounds(x))
def bernstein(c):
    n=len(c)-1
    return max(magnitude(sum((c[j]*fmpq(math.comb(i,j),math.comb(n,j)) for j in range(i+1)),arb(0))) for i in range(n+1))
def shift(c,z):
    return [sum((v*math.comb(j,k)*z**(j-k) for j,v in enumerate(c) if j>=k),arb(0)) for k in range(len(c))]
class Reference:
    def __init__(self):
        src=loadin('native_seed'); data=loadin('c6_dense100'); cand=loadin('c6_p100')
        self.D=exact(src['D']);self.k=arb(exact(src['k']))
        self.seed=[[[arb(exact(v)) for v in row] for row in cell] for cell in src['segments']]
        self.metric=[[[arb(exact(v)) for v in row] for row in cell] for cell in data['segments']]
        self.eps=arb(exact(CFG['epsilon']));self.c=[arb(exact(v)) for v in data['correction']]
        self.q=[arb(exact(v)) for v in cand['q']]
    def piece(self,pieces,field,lo,hi,der):
        n=len(pieces);h=self.D/n
        aa=max(0,int(lo/h)); bb=min(n-1,int(hi/h))
        aa=min(aa,n-1); out=None
        for i in range(aa,bb+1):
            z=interval(max(fmpq(0),lo-i*h),min(h,hi-i*h))
            v=ev(pieces[i][field],z,der)
            out=v if out is None else hull(out,v)
        if out is None:raise ArithmeticError('Uncovered saved-reference piece')
        return out
    def jets(self,ulo,uhi,n=7):
        lo=ulo*self.D;hi=uhi*self.D;s=interval(lo,hi)
        ans={k:[] for k in ('A','ell','Phi','W','q')}
        for der in range(n+1):
            factor=self.D**der
            ans['A'].append(self.piece(self.metric,0,lo,hi,der)*factor)
            ans['W'].append(self.piece(self.seed,0,lo,hi,der)*factor)
            ans['ell'].append(-2*self.eps*self.piece(self.seed,5,lo,hi,der)*factor)
            ans['Phi'].append((self.piece(self.seed,2,lo,hi,der)+self.eps*self.piece(self.seed,6,lo,hi,der)+ev(self.c,s,der))*factor)
            ans['q'].append(ev(self.q,s,der)*factor)
        return ans

def field_values(y,p):
    eps=p['eps'];s=y[8]
    d=ev(p['c7'],s)+sum((b*h for b,(h,hp) in zip(p['x'][1:],physics.shapes(s,p['D']))),arb(0))
    return {'A':y[0]+eps*y[5]+y[9],'ell':-2*eps*y[5],'Phi':y[2]+eps*y[6]+d,'W':y[0],
            'departure':max(magnitude(eps*y[5]+y[9]),magnitude(-2*eps*y[5]),magnitude(eps*y[6]+d))}
def field_jets(y,p):
    cc=physics.coeff(y[:11],7,p);eps=p['eps'];S=Taylor([y[8],1]+[0]*6)
    d=ev(p['c7'],S)+sum((b*h for b,(h,hp) in zip(p['x'][1:],physics.shapes(S,p['D']))),Taylor([0]*8))
    out={k:[] for k in ('A','ell','Phi','W')}
    for n in range(8):
        fact=math.factorial(n)*p['D']**n
        out['A'].append((cc[0][n]+eps*cc[5][n]+cc[9][n])*fact)
        out['ell'].append(-2*eps*cc[5][n]*fact)
        out['Phi'].append((cc[2][n]+eps*cc[6][n]+d.c[n])*fact)
        out['W'].append(cc[0][n]*fact)
    return out
def new_stats():
    return {'error':{k:[fmpq(0)]*8 for k in ('A','ell','Phi','W')},
        'hat_lipschitz':{k:fmpq(0) for k in ('A','Phi','BminusW')},
        'hat_j_min':None,'hat_j_max':fmpq(0),'departure_max':fmpq(0),
        'covered':fmpq(0),'cells':0,'subcells':0,'gaps':0}
def compare(st,cell,s,ref):
    stats=st['map_stats'];p=st['p'];Dlo,Dhi=bounds(p['D']); h=cell['h']
    if stats['covered']!=s:stats['gaps']+=1
    ulo=max(fmpq(0),s/Dhi);uhi=min(fmpq(1),(s+h)/Dlo)
    native=ref.jets(ulo,uhi,7);exactj=field_jets(cell['box'],p)
    for name in exactj:
        for n in range(1,8): stats['error'][name][n]=max(stats['error'][name][n],magnitude(exactj[name][n]-native[name][n]))
    for k in range(CFG['map_bounds']['comparison_subcells']):
        a=h*k/CFG['map_bounds']['comparison_subcells']; b=h*(k+1)/CFG['map_bounds']['comparison_subcells']
        ulo=max(fmpq(0),(s+a)/Dhi);uhi=min(fmpq(1),(s+b)/Dlo)
        hat=ref.jets(ulo,uhi,1); yy=validated.range_on_cell(cell,a,b); fields=field_values(yy,p)
        for name in ('A','ell','Phi','W'): stats['error'][name][0]=max(stats['error'][name][0],magnitude(fields[name]-hat[name][0]))
        stats['departure_max']=max(stats['departure_max'],fields['departure'])
        for name in ('A','Phi'): stats['hat_lipschitz'][name]=max(stats['hat_lipschitz'][name],magnitude(hat[name][1]))
        stats['hat_lipschitz']['BminusW']=max(stats['hat_lipschitz']['BminusW'],magnitude(hat['A'][1]+hat['q'][1]-hat['W'][1]))
        jj=(hat['ell'][0]-hat['A'][0]-hat['q'][0]).exp();lo,hi=bounds(jj)
        stats['hat_j_min']=lo if stats['hat_j_min'] is None else min(lo,stats['hat_j_min'])
        stats['hat_j_max']=max(hi,stats['hat_j_max']);stats['subcells']+=1
    stats['covered']=s+h;stats['cells']+=1
def finish(st,corner,ref):
    stats=st['map_stats'];p=st['p'];D=p['D']
    if stats['gaps'] or stats['covered']!=bounds(D)[1]:raise ArithmeticError('Map cover incomplete')
    eq=[]
    qnorm=[v*D**j for j,v in enumerate(corner['q'])]
    diff=[v-ref.q[j]*ref.D**j for j,v in enumerate(qnorm)]
    for n in range(8):
        eq.append(bernstein([v*math.prod(range(j-n+1,j+1)) for j,v in enumerate(diff) if j>=n]))
    ed=magnitude((D/arb(ref.D)).log()); ek=magnitude((p['k']/ref.k).log())
    ea,el,ep,ew=[stats['error'][k][0] for k in ('A','ell','Phi','W')]
    ej=ed+ea+el+eq[0]
    up=lambda x:bounds(x)[1]
    relative=lambda x:up(arb(x).exp()-1)
    mhat=arb(stats['hat_j_min'])/arb(stats['hat_j_max'])
    m=(arb(-2*ej).exp()*mhat).lower().fmpq()
    if m<=0:raise ArithmeticError('Exact normalized-map positive derivative not established')
    inverse=min(fmpq(1),up((arb(2*ej).exp()-1)/arb(m)))
    fixedA=ea+stats['hat_lipschitz']['A']*inverse
    fixedPhi=ep+stats['hat_lipschitz']['Phi']*inverse
    fixedClock=ea+eq[0]+ew+stats['hat_lipschitz']['BminusW']*inverse
    q_abs=bernstein(qnorm)
    domains={'physical_field_departure':stats['departure_max']<exact(CFG['scientific_gates']['maximum_field_departure']),
             'lapse_bound':q_abs<=exact(CFG['scientific_gates']['maximum_lapse_abs'])}
    result={'validated_common_u_errors_through_order7':stats['error'],'q_common_u_errors_through_order7':eq,
      'log_domain_error':ed,'log_k_error':ek,'coordinate_integrand_log_error':ej,
      'coordinate_length_relative_bound':relative(ej),'proper_separation_relative_bound':relative(ed+el),
      'wall_radius_relative_bound':relative(ea+ek/2),'normalized_wall_clock_relative_bound':relative(ea+ew),
      'positive_coordinate_Jacobian_lower':(arb(stats['hat_j_min'])*arb(-ea-el-eq[0]).exp()).lower().fmpq(),
      'normalized_map_derivative_lower':m,'uniform_inverse_u_error':inverse,
      'registered_65_fixed_y_bounds':{'A_absolute':fixedA,'Phi_absolute':fixedPhi,'radius_relative':relative(fixedA+ek/2),'normalized_clock_relative':relative(fixedClock)},
      'saved_profile_lipschitz':stats['hat_lipschitz'],'q_abs_bound':q_abs,'domain_checks':domains,
      'cells':stats['cells'],'subcells':stats['subcells'],'gaps':stats['gaps'],
      'material_domain_passed':all(domains.values()),
      'scope':'Continuum initial data from certified physical root; no time evolution.'}
    def finite(obj):
        if isinstance(obj,(arb,fmpq)):return arb(obj).is_finite()
        if isinstance(obj,dict):return all(finite(v) for v in obj.values())
        if isinstance(obj,(list,tuple)):return all(finite(v) for v in obj)
        if isinstance(obj,float):return math.isfinite(obj)
        return True
    result['all_required_bounds_finite']=finite(result)
    return result
