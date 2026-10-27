"""Regular coupled scalar--geometry test; no division by the scalar gradient."""
from pathlib import Path
import argparse, hashlib, json, os, time
import numpy as np
from scipy.interpolate import PPoly, BarycentricInterpolator
from scipy.integrate import solve_ivp, simpson
from scipy.linalg import eig
from scipy.optimize import brentq

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
PARENT = BASE.parent / 'capture-to-model-2026-09-12/static-background-successor'
FINE = PARENT / 'proper-shooting/narrow-gap/fine-collocation/results'
M2 = .41
GAMMA = 20.

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_json(path, obj):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)

def authenticate():
    c = json.loads((BASE/'CONTRACT.json').read_text())
    for p,h in c['bound_files'].items():
        q = Path(p)
        if not q.is_absolute(): q=BASE/q
        if digest(q)!=h: raise RuntimeError('Binding mismatch: '+str(q))
    return c

class Background:
    def __init__(self, folder=FINE):
        folder=Path(folder)
        data=np.load(folder/'arrays.npz')
        self.data=data
        self.pp=PPoly(data['poly_coefficients'],data['mesh'])
        self.L=float(np.exp(data['parameters'][0]))
        self.k=float(data['parameters'][1])
        self.folder=str(folder)
    def __call__(self,z):
        W,A,phi,S=np.moveaxis(self.pp(np.asarray(z)/self.L),-1,0)
        a=np.exp(W)
        Vp=a*a*M2*phi
        B=Vp-4*A*S
        return a,A,phi,S,Vp,B

def cheb(N,L):
    j=np.arange(N)
    z=.5*L*(1-np.cos(np.pi*j/(N-1)))
    w=(-1.)**j
    w[[0,-1]]*=.5
    delta=z[:,None]-z[None,:]
    np.fill_diagonal(delta,1.)
    D=w[None,:]/w[:,None]/delta
    np.fill_diagonal(D,0.)
    np.fill_diagonal(D,-D.sum(axis=1))
    return z,D,w

def normalized(value,terms):
    return float(np.max(np.abs(value)/(1+sum(np.abs(t) for t in terms))))

def diagnostics(bg,mu,z,psi,f):
    ip=BarycentricInterpolator(z,psi)
    jf=BarycentricInterpolator(z,f)
    x=np.linspace(0,bg.L,1001)
    h=ip(x); hp=ip.derivative(x); g=jf(x); gp=jf.derivative(x); gpp=jf.derivative(x,2)
    a,A,phi,S,Vp,B=bg(x)
    mom=[hp,2*A*h,S*g/3]
    con=[S*gp,-B*g,(2*S*S-3*mu-12*bg.k)*h]
    kg=[gpp,3*A*gp,(mu-a*a*M2)*g,6*S*hp,4*Vp*h]
    wall=[]
    for i,sig in [(0,1),(-1,-1)]:
        wall.append(float(gp[i]+2*S[i]*h[i]-sig*a[i]*GAMMA*g[i]/2))
    norm=float(2*simpson(a**3*(g*g+6*h*h),x=x))
    dD=float(-2*simpson(a*h,x=x))
    return dict(momentum=normalized(sum(mom),mom),constraint=normalized(sum(con),con),
                scalar_kg=normalized(sum(kg),kg),wall_absolute=wall,kinetic_Z=norm,
                delta_D=dD,delta_D_over_sqrt_Z=dD/np.sqrt(norm),
                scalar_gradient_turn_brackets=np.where(S[:-1]*S[1:]<0)[0].tolist())

def spectral(N):
    started=time.monotonic(); bg=Background(); z,D,_=cheb(N,bg.L)
    a,A,phi,S,Vp,B=bg(z)
    K=np.zeros((2*N,2*N)); W=np.zeros_like(K)
    K[:N,:N]=D+np.diag(2*A); K[:N,N:]=np.diag(S/3)
    K[N:,:N]=np.diag(2*S*S-12*bg.k)
    K[N:,N:]=np.diag(S)@D-np.diag(B)
    W[N:,:N]=3*np.eye(N)
    for i,sig in [(0,1),(N-1,-1)]:
        K[N+i,:]=0;W[N+i,:]=0
        K[N+i,i]=2*S[i];K[N+i,N:]=D[i,:]
        K[N+i,N+i]-=sig*a[i]*GAMMA/2
    vals,vec=eig(K,W)
    select=[i for i,v in enumerate(vals) if np.isfinite(v) and abs(v.imag)<=1e-8*max(1,abs(v.real)) and -1<=v.real<=1]
    select.sort(key=lambda i: vals[i].real)
    modes=[]; profiles=[]
    for i in select[:12]:
        mu=float(vals[i].real); v=np.real(vec[:,i]); v/=np.max(abs(v[:N]))
        if v[0]<0:v=-v
        d=diagnostics(bg,mu,z,v[:N],v[N:])
        d.update(mu=mu,lambda_shifted=mu+4*bg.k,mu_over_k=mu/bg.k,
                 pencil_residual=float(np.linalg.norm(K@v-mu*W@v)/(np.linalg.norm(K@v)+abs(mu)*np.linalg.norm(W@v)+1e-300)))
        modes.append(d);profiles.append(v)
    out=dict(N=N,method='undivided two-field Chebyshev generalized pencil',k=bg.k,L=bg.L,
             finite_count=int(np.isfinite(vals).sum()),infinite_count=int((~np.isfinite(vals)).sum()),
             modes=modes,elapsed_seconds=time.monotonic()-started)
    np.savez_compressed(BASE/'results'/f'spectral_N{N}.npz',z=z,eigenvalues=vals,profiles=np.array(profiles))
    save_json(BASE/'results'/f'spectral_N{N}.json',out)
    return out

def initial(bg,mu):
    a,A,phi,S,Vp,B=bg(0.)
    c=a*GAMMA/2;den=c*S-B
    if abs(den)<1e-12: raise RuntimeError('Lower-wall initial normalization degenerate')
    f=3*(mu+4*bg.k)/den
    return np.array([1.,f,c*f-2*S])

def rhs(bg,mu,z,y):
    a,A,phi,S,Vp,B=bg(z);h,f,p=y
    return [-2*A*h-S*f/3,p,-3*A*p+(a*a*M2-mu+2*S*S)*f+(12*A*S-4*Vp)*h]

def shoot_at(bg,mu,rtol,dense=False):
    sol=solve_ivp(lambda z,y:rhs(bg,mu,z,y),(0,bg.L),initial(bg,mu),method='DOP853',
                  rtol=rtol,atol=rtol*1e-3,dense_output=dense,max_step=bg.L/32)
    if not sol.success: raise RuntimeError(sol.message)
    a,A,phi,S,Vp,B=bg(bg.L);h,f,p=sol.y[:,-1]
    return float(p+2*S*h+a*GAMMA*f/2),sol

def shooting(mu_guess,rtol,label,folder=None):
    started=time.monotonic();bg=Background(folder) if folder else Background()
    width=max(1e-5,.05*abs(mu_guess)); samples=[]
    for attempt in range(4):
        lo=mu_guess-width;hi=mu_guess+width
        fl=shoot_at(bg,lo,rtol)[0];fh=shoot_at(bg,hi,rtol)[0]
        samples.append(dict(lo=lo,hi=hi,flo=fl,fhi=fh))
        if fl*fh<=0:break
        width*=2
    else:raise RuntimeError('No root bracket under fixed bounded expansions')
    mu=brentq(lambda m:shoot_at(bg,m,rtol)[0],lo,hi,xtol=5e-16,rtol=2e-14,maxiter=50)
    residual,sol=shoot_at(bg,mu,rtol,True)
    x=np.linspace(0,bg.L,2001);h,f,p=sol.sol(x);a,A,phi,S,Vp,B=bg(x)
    C=S*p-B*f+(2*S*S-3*mu-12*bg.k)*h
    scale=1+abs(S*p)+abs(B*f)+abs((2*S*S-3*mu-12*bg.k)*h)
    Z=float(2*simpson(a**3*(f*f+6*h*h),x=x)); dD=float(-2*simpson(a*h,x=x))
    turn=brentq(lambda zz:bg(zz)[3],0,bg.L)
    ht,ft,pt=sol.sol(turn);at,At,phit,St,Vpt,Bt=bg(turn)
    turn_c=-Vpt*ft-3*(mu+4*bg.k)*ht
    out=dict(label=label,method='regular three-field DOP853 shooting',mu=float(mu),lambda_shifted=float(mu+4*bg.k),
             mu_over_k=float(mu/bg.k),growth_s_over_H=float(np.sqrt(2.25-mu/bg.k)-1.5) if mu<0 else None,
             growth_s=float(np.sqrt(bg.k)*(np.sqrt(2.25-mu/bg.k)-1.5)) if mu<0 else None,
             k=bg.k,L=bg.L,rtol=rtol,atol=rtol*1e-3,wall_residual=float(residual),
             max_constraint=float(np.max(abs(C))),normalized_constraint=float(np.max(abs(C)/scale)),
             kinetic_Z=Z,delta_D=dD,delta_D_over_sqrt_Z=dD/np.sqrt(Z),
             turn_z=float(turn),turn_u=float(turn/bg.L),turn_constraint=float(turn_c),
             turn_fields=[float(ht),float(ft),float(pt)],initial=initial(bg,mu).tolist(),
             bracket_attempts=samples,background=bg.folder,elapsed_seconds=time.monotonic()-started)
    np.savez_compressed(BASE/'results'/f'{label}.npz',z=x,psi=h,f=f,p=p,constraint=C)
    save_json(BASE/'results'/f'{label}.json',out)
    return out

def controls():
    results={}
    for k in [0.,.0003268413384542497]:
        L=6.38029536996215;z=np.linspace(0,L,1001)
        if k:
            H=np.sqrt(k);w=np.cosh(H*z)+np.sqrt(1+k)/H*np.sinh(H*z)
            wp=H*np.sinh(H*z)+np.sqrt(1+k)*np.cosh(H*z)
        else:w=1+z;wp=np.ones_like(z)
        a=1/w;A=-wp/w;h=w*w;hp=2*w*wp
        mom=hp+2*A*h;mu=-4*k
        def vacuum_rhs(t,y):
            if k:
                H=np.sqrt(k)
                w=np.cosh(H*t)+np.sqrt(1+k)/H*np.sinh(H*t)
                wp=H*np.sinh(H*t)+np.sqrt(1+k)*np.cosh(H*t)
            else:w=1+t;wp=1.
            return [2*wp*y[0]/w]
        sol=solve_ivp(vacuum_rhs,(0,L),[1.],rtol=2e-12,atol=2e-14,method='DOP853',t_eval=z)
        err=float(np.max(abs(sol.y[0]-h)/h))
        results[str(k)]=dict(mu=mu,momentum_max=float(np.max(abs(mom))),constraint=0.,wall=0.,
            kinetic_Z=float(12*simpson(1/a,x=z)),delta_D=float(-2*simpson(1/a,x=z)),profile_relative_error=err)
    from scipy.optimize import brentq as bq
    q=bq(lambda q:q*np.tan(q)-1,1e-9,np.pi/2-1e-9);expect=q*q+M2
    ro=[]
    for N in [33,65]:
        z,D,_=cheb(N,2.);K=-D@D+M2*np.eye(N);W=np.eye(N)
        K[0]=D[0];K[0,0]-=1;K[-1]=D[-1];K[-1,-1]+=1;W[[0,-1]]=0
        ev=eig(K,W,right=False);real=sorted(v.real for v in ev if np.isfinite(v) and abs(v.imag)<1e-8 and v.real>0)
        ro.append(dict(N=N,mu=float(real[0]),expected=float(expect),error=float(abs(real[0]-expect)),derivative_error=float(np.max(abs(D@z-1)))))
    results['flat_scalar_robin']=ro
    results['pass']=all(v['profile_relative_error']<=1e-8 and v['momentum_max']<=1e-10 for v in results.values() if isinstance(v,dict)) and all(v['error']<=1e-8 for v in ro)
    save_json(BASE/'results/CONTROLS.json',results)
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['controls','spectral','shoot'])
    p.add_argument('--N',type=int,default=33);p.add_argument('--mu',type=float);p.add_argument('--rtol',type=float,default=2e-11)
    p.add_argument('--label',default='shoot');p.add_argument('--background')
    args=p.parse_args();authenticate()
    if args.mode=='controls':out=controls()
    elif args.mode=='spectral':
        if not json.loads((BASE/'results/CONTROLS.json').read_text())['pass']:raise RuntimeError('Controls not passed')
        out=spectral(args.N)
    else:out=shooting(args.mu,args.rtol,args.label,args.background)
    print(json.dumps(out,indent=2,allow_nan=False))
