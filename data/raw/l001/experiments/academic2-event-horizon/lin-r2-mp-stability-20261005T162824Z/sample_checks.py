"""Independent saved-field equations; MP decimal data never round through float."""
from fractions import Fraction
import numpy as np

R=np.longdouble

def exact(value):
    q=Fraction(value)
    return R(str(q.numerator))/R(str(q.denominator))

def scaled(terms):
    values=np.abs(sum(terms))/(1+sum(np.abs(t) for t in terms))
    if not np.all(np.isfinite(values)):raise RuntimeError('nonfinite equation check')
    return float(np.max(values))

def check(bg,mode,mu,helper,stride):
    s=np.array(bg['s'][::stride],dtype=R)
    W,H,phi,T,z=np.array([v[::stride] for v in bg['fields']],dtype=R)
    psi,f,g=np.array(mode[:,::stride],dtype=R)
    m={n:exact(v) for n,v in bg['model_exact'].items()}
    m2,gamma=m['m2'],m['gamma'];k=R(bg['k']);mu=R(float(mu))
    Wp,Wpp=helper.differentiate(s,W,9);Hp,_=helper.differentiate(s,H,9)
    zp,_=helper.differentiate(s,z,9);phip,phipp=helper.differentiate(s,phi,9)
    Tp,_=helper.differentiate(s,T,9);psip,_=helper.differentiate(s,psi,9)
    fp,fpp=helper.differentiate(s,f,9);e=np.exp(-2*W)
    background={
        'W_s':scaled([Wp,-H]),'Phi_s':scaled([phip,-T]),
        'H_s':scaled([Hp,T*T/3,k*e]),
        'direct_metric':scaled([Wpp,phip*phip/3,k*e]),
        'conformal_coordinate':scaled([zp,-np.exp(-W)]),
        'scalar':scaled([phipp,4*Wp*phip,-m2*phi]),
        'T_s':scaled([Tp,4*H*T,-m2*phi]),
        'first_integral':scaled([Wp*Wp,-k*e,-np.ones_like(W),-phip*phip/12,m2*phi*phi/12])}
    checks={'momentum':scaled([psip,2*Wp*psi,phip*f/3]),
            'constraint':scaled([phip*fp,-(m2*phi-4*Wp*phip)*f,(2*phip*phip-3*(mu+4*k)*e)*psi]),
            'scalar_KG':scaled([fpp,4*Wp*fp,(mu*e-m2)*f,6*phip*psip,4*m2*phi*psi])}
    for j,sig,v,lam in [(0,1,m['v0'],m['lambda_a']),(-1,-1,m['v1'],m['lambda_b'])]:
        tau=lam+gamma*(phi[j]-v)**2/2
        background['Israel_'+str(j)]=scaled([sig*Wp[j],tau/6])
        background['scalar_wall_'+str(j)]=scaled([sig*phip[j],-gamma*(phi[j]-v)/2])
        checks['Robin_'+str(j)]=scaled([fp[j],2*phip[j]*psi[j],-sig*gamma*f[j]/2])
    Z=2*helper.simpson(np.exp(2*W)*(f*f+6*psi*psi),s)
    dD=-2*helper.simpson(psi,s)
    return {'stride':stride,'background':background,'mode':checks,
            'max_background':max(background.values()),'max_mode':max(checks.values()),
            'Z':float(Z),'deltaD':float(dD),'overlap':float(dD/np.sqrt(Z)),
            'all_nodes_including_endpoints':True,'background_digits_dropped_to_binary64':False}
