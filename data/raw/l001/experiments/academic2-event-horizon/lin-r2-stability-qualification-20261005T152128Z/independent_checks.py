"""Sample-derived proper-distance checks; imports no producer equations."""
import importlib.util
from pathlib import Path
import numpy as np

def load_helper(path):
    spec=importlib.util.spec_from_file_location('frozen_fornberg',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def scaled(terms):
    return float(np.max(np.abs(sum(terms))/(1+sum(np.abs(t) for t in terms))))

def check(data,model,mu,k,helper,stride):
    R=np.longdouble;m2=R(float(model['m2']));gamma=R(float(model['gamma']))
    mu=R(float(mu));k=R(float(k))
    s=np.asarray(data['s'][::stride],dtype=R)
    W,H,phi,T,z=np.asarray(data['background'][:,::stride],dtype=R)
    psi,f,g=np.asarray(data['mode'][:,::stride],dtype=R)
    Wp,Wpp=helper.differentiate(s,W,9);Hp,_=helper.differentiate(s,H,9)
    zp,_=helper.differentiate(s,z,9)
    phip,phipp=helper.differentiate(s,phi,9);Tp,_=helper.differentiate(s,T,9)
    psip,_=helper.differentiate(s,psi,9);fp,fpp=helper.differentiate(s,f,9)
    e=np.exp(-2*W)
    bg={
      'W_s':scaled([Wp,-H]),'Phi_s':scaled([phip,-T]),
      'H_s':scaled([Hp,T*T/3,k*e]),
      'direct_metric':scaled([Wpp,phip*phip/3,k*e]),
      'conformal_coordinate':scaled([zp,-np.exp(-W)]),
      'scalar':scaled([phipp,4*Wp*phip,-m2*phi]),
      'T_s':scaled([Tp,4*H*T,-m2*phi]),
      'first_integral':scaled([Wp*Wp,-k*e,-np.ones_like(W),-phip*phip/12,m2*phi*phi/12])}
    for index,sig,v,lam in [(0,1,model['v0'],model['lambda_a']),(-1,-1,model['v1'],model['lambda_b'])]:
        v=R(float(v));lam=R(float(lam));tau=lam+gamma*(phi[index]-v)**2/2
        bg['Israel_'+str(index)]=scaled([sig*Wp[index],tau/6])
        bg['scalar_wall_'+str(index)]=scaled([sig*phip[index],-gamma*(phi[index]-v)/2])
    # KG is the direct varied scalar equation, using separately differentiated
    # background/mode data, rather than the producer's substituted first-order RHS.
    mode={
      'momentum':scaled([psip,2*Wp*psi,phip*f/3]),
      'constraint':scaled([phip*fp,-(m2*phi-4*Wp*phip)*f,(2*phip*phip-3*(mu+4*k)*e)*psi]),
      'scalar_KG':scaled([fpp,4*Wp*fp,(mu*e-m2)*f,6*phip*psip,4*m2*phi*psi])}
    for index,sig in [(0,1),(-1,-1)]:
        mode['Robin_'+str(index)]=scaled([fp[index],2*phip[index]*psi[index],-sig*gamma*f[index]/2])
    Z=2*helper.simpson(np.exp(2*W)*(f*f+6*psi*psi),s);dD=-2*helper.simpson(psi,s)
    return {'stride':stride,'background':bg,'mode':mode,
            'max_background':max(bg.values()),'max_mode':max(mode.values()),
            'Z':float(Z),'deltaD':float(dD),'overlap':float(dD/np.sqrt(Z)),
            'all_nodes_including_endpoints':True,'primary_rhs_used_as_derivative':False,
            'binary64_inputs_lifted_exactly':True}
