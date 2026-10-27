"""Independent mpmath RK4 shooting on the authenticated retained polynomial.

This improves solver arithmetic only, not the precision of inherited background data.
"""
from pathlib import Path
import argparse,bisect,hashlib,json,time
import numpy as np
import mpmath as mp

B=Path(__file__).resolve().parents[1]
P=B.parent/'capture-to-model-2026-09-12/static-background-successor/proper-shooting/narrow-gap/fine-collocation/results/arrays.npz'

def run(N,dps):
    started=time.monotonic();mp.mp.dps=dps
    assert hashlib.sha256(P.read_bytes()).hexdigest()=='49c86129314b335a6447d40f488b005060eca4de815306c3389ebdb3ba9e23b3'
    data=np.load(P);mesh=[mp.mpf(float(x)) for x in data['mesh']];mf=[float(x) for x in data['mesh']]
    cf=data['poly_coefficients'];cache={}
    L=mp.mpf(float(np.exp(data['parameters'][0])));k=mp.mpf(float(data['parameters'][1]));mb=mp.mpf(.41)
    def bg(u):
        j=min(max(bisect.bisect_right(mf,float(u))-1,0),len(mf)-2)
        if j not in cache:cache[j]=[[mp.mpf(float(cf[d,j,c])) for d in range(4)] for c in range(4)]
        t=u-mesh[j]
        W,A,phi,S=[((v[0]*t+v[1])*t+v[2])*t+v[3] for v in cache[j]]
        a=mp.exp(W);Vp=a*a*mb*phi
        return a,A,phi,S,Vp
    # Midpoint table makes arithmetic refinement independent of adaptive integration.
    table=[]
    for j in range(2*N+1):
        a,A,phi,S,Vp=bg(mp.mpf(j)/(2*N))
        table.append(tuple(L*x for x in [-2*A,-S/3,12*A*S-4*Vp,a*a*mb+2*S*S,-3*A]))
    a0,A0,phi0,S0,Vp0=bg(mp.mpf(0));ae,Ae,phie,Se,Vpe=bg(mp.mpf(1))
    den=10*a0*S0-(Vp0-4*A0*S0)
    h=mp.mpf(1)/N
    def evolve(mu,retain=False):
        f0=3*(mu+4*k)/den
        y=(mp.mpf(1),f0,10*a0*f0-2*S0)
        def rhs(c,y):
            a,b,c0,d,e=c;psi,f,p=y
            return (a*psi+b*f,L*p,c0*psi+(d-L*mu)*f+e*p)
        for i in range(N):
            c0,cm,c1=table[2*i:2*i+3]
            v1=rhs(c0,y)
            v2=rhs(cm,tuple(y[j]+h*v1[j]/2 for j in range(3)))
            v3=rhs(cm,tuple(y[j]+h*v2[j]/2 for j in range(3)))
            v4=rhs(c1,tuple(y[j]+h*v3[j] for j in range(3)))
            y=tuple(y[j]+h*(v1[j]+2*v2[j]+2*v3[j]+v4[j])/6 for j in range(3))
        return y[2]+2*Se*y[0]+10*ae*y[1]
    guess=mp.mpf(str(json.loads((B/'results/shoot_tight.json').read_text())['mu']))
    x0=guess-mp.mpf('1e-7');x1=guess+mp.mpf('1e-7');f0=evolve(x0);f1=evolve(x1);iters=[]
    for i in range(8):
        x2=x1-f1*(x1-x0)/(f1-f0);f2=evolve(x2)
        iters.append(dict(mu=mp.nstr(x2,dps),residual=mp.nstr(f2,dps)))
        if abs(x2-x1)<mp.mpf('1e-25'):break
        x0,f0,x1,f1=x1,f1,x2,f2
    out=dict(method='mpmath fixed-step RK4 and secant',N=N,dps=dps,mu=mp.nstr(x2,dps),
             mu_float=float(x2),mass_difference_from_DOP853=float(x2-guess),wall_residual=mp.nstr(f2,dps),
             iterations=iters,elapsed_seconds=time.monotonic()-started,
             caveat='Arbitrary precision evolution on retained binary64 background polynomial; not a recomputed high-precision background.')
    p=B/'results'/f'precision_N{N}_dps{dps}.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(out,indent=2)+'\n');t.replace(p)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--N',type=int,required=True);p.add_argument('--dps',type=int,required=True);a=p.parse_args()
    print(json.dumps(run(a.N,a.dps),indent=2))
