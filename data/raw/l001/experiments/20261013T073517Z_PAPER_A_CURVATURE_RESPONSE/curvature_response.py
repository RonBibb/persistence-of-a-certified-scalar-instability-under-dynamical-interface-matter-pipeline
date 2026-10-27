"""One frozen exact-rational static consequence; no numerical producer imports."""
import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = HERE.parents[1]
ROW = 'experiments/research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01/'
EXPECTED = {'GAMMA_Q':'20', 'LAMBDA_A_Q':'6755388606266369/1125899906842624',
            'LAMBDA_B_Q':'-851862101055633/140737488355328',
            'M2_Q':'7385903388887613/18014398509481984',
            'V0_Q':'3602879701896397/36028797018963968',
            'V1_Q':'6520040733916207/72057594037927936'}

class Rejected(Exception): pass
def need(ok, name):
    if not ok: raise Rejected(name)
def iv(record):
    z = tuple(map(Q, record['exact_bounds']))
    need(len(z)==2 and z[0]<=z[1], 'INTERVAL_ORDER')
    return z
def point(x): return (Q(x), Q(x))
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def neg(a): return (-a[1],-a[0])
def sub(a,b): return add(a,neg(b))
def mul(a,b):
    z=[x*y for x in a for y in b]
    return min(z),max(z)
def scale(a,c): return mul(a,point(c))
def div(a,b):
    need(not b[0]<=0<=b[1], 'DENOMINATOR_NONZERO')
    return mul(a,(1/b[1],1/b[0]))
def square(a):
    return (Q(0) if a[0]<=0<=a[1] else min(x*x for x in a), max(x*x for x in a))
def padd(a,b):
    n=max(len(a),len(b))
    return [(a[i] if i<len(a) else Q(0))+(b[i] if i<len(b) else Q(0)) for i in range(n)]
def pscale(a,c): return [x*c for x in a]
def pmul(a,b):
    out=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    return out
def peval(p,a):
    out=point(0)
    for c in reversed(p): out=add(mul(out,a),point(c))
    return out
def packed(a):
    # Outward rational rounding, not binary float display.
    n=10**12
    lo=a[0]*n; hi=a[1]*n
    low=lo.numerator//lo.denominator
    high=-((-hi.numerator)//hi.denominator)
    def fixed(x):
        sign='-' if x<0 else ''; x=abs(x)
        return f'{sign}{x//n}.{x%n:012d}'
    return {'exact_bounds':list(map(str,a)), 'outward_decimal_12':[fixed(low),fixed(high)]}

def consequence(result, model, a0=Q(0), derivative_corruption=Q(0)):
    need(all(model[k]==v for k,v in EXPECTED.items()), 'MODEL_EXACT')
    need(a0==0, 'LOWER_NORMALIZATION')
    p=result['parameter']; z=result['neighborhood']
    need(p['baseline_exact']==EXPECTED['LAMBDA_B_Q'] and p['delta_exact']==['-1/1000000','1/1000000'], 'TENSION_RANGE')
    need(all(result['gates'].get(f'P01-G{i}')=='PASS' for i in range(1,5)), 'INHERITED_GATES')
    a=iv(z['newton_image']); root=tuple(map(Q,z['root_box_exact']))
    need(root[0]<a[0]<=a[1]<root[1], 'IMAGE_INSIDE_ROOT_BOX')
    ap=iv(z['response']['da_dlambda_b']); dp=iv(z['response']['dD_dlambda_b'])
    need(ap[0]>0, 'A_RESPONSE_POSITIVE'); need(dp[1]<0, 'D_RESPONSE_NEGATIVE')
    g,la,m,v=(Q(model[key]) for key in ('GAMMA_Q','LAMBDA_A_Q','M2_Q','V0_Q'))
    x=sub(a,point(v)); H=scale(add(point(la),scale(square(x),g/2)),-Q(1,6))
    S=scale(x,g/2)
    k=add(sub(sub(square(H),point(1)),scale(square(S),Q(1,12))),scale(square(a),m/12))
    # Exact polynomial k and its derivative, independently assembled from launch maps.
    xp=[-v,Q(1)]; hp=pscale(padd([la],pscale(pmul(xp,xp),g/2)),-Q(1,6))
    sp=pscale(xp,g/2)
    kp=padd(padd(pmul(hp,hp),[-Q(1)]),padd(pscale(pmul(sp,sp),-Q(1,12)),[Q(0),Q(0),m/12]))
    kd=[i*kp[i] for i in range(1,len(kp))]
    analytic=padd(padd(pscale(pmul(hp,xp),-g/3),pscale(xp,-g*g/24)),[Q(0),m/6])
    analytic[0]+=derivative_corruption
    need(kd==analytic, 'DERIVATIVE_IDENTITY')
    direct=add(add(scale(mul(H,x),-g/3),scale(x,-g*g/24)),scale(a,m/6))
    polynomial=peval(kd,a)
    ka=(max(direct[0],polynomial[0]),min(direct[1],polynomial[1]))
    need(ka[0]<=ka[1], 'DERIVATIVE_ENCLOSURES_INTERSECT')
    need(k[0]>0,'CURVATURE_POSITIVE'); need(ka[0]>0,'CURVATURE_A_POSITIVE')
    kl=mul(ka,ap); rl=scale(kl,12); rd=div(rl,dp)
    need(kl[0]>0 and rl[0]>0,'CURVATURE_RESPONSE_POSITIVE')
    need(rd[1]<0,'CURVATURE_SEPARATION_NEGATIVE')
    return {'a':packed(a),'k':packed(k),'dk_da_direct':packed(direct),'dk_da_polynomial':packed(polynomial),
            'dk_da':packed(ka),'dk_dlambda_b':packed(kl),'dR_lower_dlambda_b':packed(rl),
            'dR_lower_dD':packed(rd),'full_endpoint_delta_k':packed(scale(kl,Q(1,500000))),
            'full_endpoint_delta_R_lower':packed(scale(rl,Q(1,500000))),
            'derivative_polynomial_coefficients':list(map(str,kd))}

def main():
    manifest=json.loads((HERE/'SOURCE_BINDINGS.json').read_text())
    for name,digest in manifest['sources'].items():
        need(hashlib.sha256((OWNER/name).read_bytes()).hexdigest()==digest,'SOURCE_HASH:'+name)
    result=json.loads((OWNER/(ROW+'RESULT.json')).read_text())
    model=json.loads((OWNER/(ROW+'BINDINGS.json')).read_text())['exact_model']
    baseline=consequence(result,model)
    controls=[]
    for name in ['A_RESPONSE_POSITIVE','D_RESPONSE_NEGATIVE','LOWER_NORMALIZATION','MODEL_EXACT','IMAGE_INSIDE_ROOT_BOX','DERIVATIVE_IDENTITY']:
        r=copy.deepcopy(result); m=copy.deepcopy(model); a0=Q(0); corruption=Q(0)
        if name=='A_RESPONSE_POSITIVE': r['neighborhood']['response']['da_dlambda_b']['exact_bounds']=['-2','-1']
        if name=='D_RESPONSE_NEGATIVE': r['neighborhood']['response']['dD_dlambda_b']['exact_bounds']=['-1','0']
        if name=='LOWER_NORMALIZATION': a0=Q(1)
        if name=='MODEL_EXACT': m['GAMMA_Q']='21'
        if name=='IMAGE_INSIDE_ROOT_BOX': r['neighborhood']['newton_image']['exact_bounds']=['0','1']
        if name=='DERIVATIVE_IDENTITY': corruption=Q(1)
        try: consequence(r,m,a0,corruption)
        except Rejected as err:
            need(str(err)==name,'CONTROL_WRONG_REJECTION:'+name)
            controls.append({'control':name,'rejected_by':str(err)})
        else: raise Rejected('CONTROL_ACCEPTED:'+name)
    print(json.dumps({'status':'PASS_PENDING_INDEPENDENT_TERMINAL_AUDIT',
          'classification':'STATIC_CURVATURE_RESPONSE_CONSEQUENCE_OF_SAVED_UNIFORM_INTERVALS',
          'results':baseline,'controls':controls,'source_count':len(manifest['sources']),
          'premises':manifest['premises'],'normalization':'A0=0; R_lower=12k; D is proper distance',
          'scope':'One local static family over exact delta=[-1/1000000,1/1000000]; no dynamics or independent flow producer'},indent=2))

if __name__=='__main__': main()
