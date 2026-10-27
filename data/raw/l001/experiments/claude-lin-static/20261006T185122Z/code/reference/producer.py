"""Dense Cauchy pullback and actual proposed SBP wave operator. No time stepping."""
from pathlib import Path
import json, hashlib, bisect, time, os, argparse, platform
import mpmath as mp
from jet import Jet, shift, horner, exp_series

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/'d1-native-cauchy-20261005T201829Z'

def encode(x):
    if isinstance(x,mp.mpf): return mp.nstr(x,mp.mp.dps)
    if isinstance(x,mp.matrix): return [[encode(x[i,j]) for j in range(x.cols)] for i in range(x.rows)]
    if isinstance(x,dict): return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x
def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(encode(data),indent=2)+'\n');os.replace(tmp,path)
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def action():
    d=json.loads((PARENT/'BINDINGS.json').read_text())['model_exact']
    return {k:mp.mpf(v.split('/')[0])/mp.mpf(v.split('/')[1]) if '/' in v else mp.mpf(v) for k,v in d.items()}
def guard():
    b=json.loads((ROOT/'BINDINGS.json').read_text())
    for row in b['inputs']:
        assert digest(PARENT/row['path'])==row['sha256'],row['path']
    assert digest(ROOT/'CONTRACT.md')==b['contract_sha256']
    releases=sorted(ROOT.glob('SOURCE_RELEASE_*.json'));assert releases
    rel=json.loads(releases[-1].read_text())
    for p,h in rel['source'].items(): assert digest(ROOT/p)==h,p
    return {'binding':digest(ROOT/'BINDINGS.json'),'release':releases[-1].name,'release_sha256':digest(releases[-1])}

def times(A,B,F,dx,k,m2):
    a,b,f=dx(A),dx(B),dx(F); V=-6+m2*F**2/2
    E=(2*B).exp(); Q=k*(2*(B-A)).exp()
    a2=dx(a)+3*a*a-2*Q+E*V*mp.mpf(2)/3
    b2=dx(b)-3*a*a+3*Q-E*V/3+f*f/2
    f2=dx(f)+3*a*f-m2*E*F
    dA,dB,dF=dx(a2),dx(b2),dx(f2)
    dEV=E*(2*V*b2+m2*F*f2)
    a4=dx(dA)+6*a*dA-4*Q*(b2-a2)+dEV*mp.mpf(2)/3-6*a2*a2
    b4=dx(dB)-6*a*dA+6*Q*(b2-a2)-dEV/3+f*dF+6*a2*a2-f2*f2
    f4=dx(dF)+3*(dA*f+a*dF)-m2*E*(2*b2*F+f2)-6*a2*f2
    return [a2,b2,f2],[a4,b4,f4]

class Dense:
    def __init__(self,level,case):
        self.level=level;self.case=case; p=PARENT/'results'/level
        self.seed=json.loads((p/'SEED.json').read_text());self.case_data=json.loads((p/f'case_{case}.dense.json').read_text())
        self.D=mp.mpf(self.seed['D']);self.k=mp.mpf(self.seed['k']);self.mu=mp.mpf(self.seed['mu'])
        self.h=mp.mpf(self.seed['h']);self.cells=self.seed['cells'];self.degree=self.seed['degree']
        self.eps=mp.mpf(self.case_data['epsilon']);self.par=action()
        self.seedrows=[[[mp.mpf(c) for c in row] for row in block] for block in self.seed['segments']]
        self.solrows=[[[mp.mpf(c) for c in row] for row in block] for block in self.case_data['segments']]
        self.corr=[mp.mpf(v) for v in self.case_data['correction']]
        self.q=[mp.mpf(0)]*12
        self.build_hermite()
    def build_hermite(self):
        from math import factorial
        M=mp.matrix(12)
        for side,s in enumerate([mp.mpf(0),self.D]):
            for j in range(6):
                for n in range(j,12): M[side*6+j,n]=mp.mpf(factorial(n))/factorial(n-j)*s**(n-j)
        self.hermite=M**-1
    def locate(self,s):
        i=max(0,min(int(mp.floor(s/self.h)),self.cells-1));return i,s-i*self.h
    def jets(self,s,n=7):
        i,z=self.locate(s);r=self.seedrows[i];y=self.solrows[i]
        A=shift(y[0],z,n);ell=[-2*self.eps*v for v in shift(r[5],z,n)]
        F=[v+self.eps*w+c for v,w,c in zip(shift(r[2],z,n),shift(r[6],z,n),shift(self.corr,s,n))]
        B=[a+q for a,q in zip(A,shift(self.q,s,n))]
        return A,B,F,ell
    def wall_jets(self,side):
        s=side*self.D;A,B,F,ell=[Jet(c) for c in self.jets(s)]
        speed=(B-ell).exp();dx=lambda u:speed*u.d()
        t2,t4=times(A,B,F,dx,self.k,self.par['m2'])
        sigma=1-2*side;p=self.par;v=p['v0' if side==0 else 'v1'];lam=p['lambda_a' if side==0 else 'lambda_b']
        U=lam+p['gamma']*(F-v)**2/2;Up=p['gamma']*(F-v)
        b2=t2[1];b4=t4[1];emB=(-B).exp()
        rows=[[],[],[]]
        for j,u in enumerate([A,B,F]):
            r0=emB*dx(u);r2=emB*(dx(t2[j])-b2*dx(u))
            r4=emB*(dx(t4[j])-b4*dx(u)-6*b2*dx(t2[j])+3*b2*b2*dx(u))
            if j<2:
                r0=r0+sigma*U/6;r2=r2+sigma*Up*t2[2]/6
                r4=r4+sigma*(Up*t4[2]+3*p['gamma']*t2[2]**2)/6
            else:
                r0=r0-sigma*Up/2;r2=r2-sigma*p['gamma']*t2[2]/2;r4=r4-sigma*p['gamma']*t4[2]/2
            for row,r in zip(rows,[r0,r2,r4]): row.append(r.val())
        return rows
    def qualify_gauge(self):
        before=[self.wall_jets(i) for i in (0,1)]
        target=mp.matrix(12,1)
        for side in (0,1):
            A,B,F,ell=self.jets(side*self.D)
            target[6*side+3]=-(before[side][1][1]-before[side][1][0])/mp.exp(2*A[0]-3*ell[0])
        self.q=list(self.hermite*target)
        middle=[self.wall_jets(i) for i in (0,1)]
        for side in (0,1):
            A,B,F,ell=self.jets(side*self.D)
            target[6*side+5]=-(middle[side][2][1]-middle[side][2][0])/mp.exp(4*A[0]-5*ell[0])
        self.q=list(self.hermite*target)
        final=[self.wall_jets(i) for i in (0,1)]
        maximum=max(abs(horner(self.q,self.D*j/1000)) for j in range(1001))
        return {'naive':before,'after_third_jet':middle,'final':final,'q_coefficients':self.q,'q_endpoint_derivatives':list(target),'max_q_sampled':maximum}
    def make_map(self):
        self.xknots=[mp.mpf(0)];self.xpoly=[]
        for i in range(self.cells):
            s=i*self.h;A,B,F,ell=self.jets(s,self.degree)
            e=exp_series([l-b for l,b in zip(ell,B)])
            c=[mp.mpf(0)]+[v/(j+1) for j,v in enumerate(e)]
            self.xpoly.append(c);self.xknots.append(self.xknots[-1]+horner(c,self.h))
        self.X=self.xknots[-1]
    def invert(self,x):
        i=max(0,min(bisect.bisect_right(self.xknots,x)-1,self.cells-1));target=x-self.xknots[i]
        c=self.xpoly[i];d=[(j+1)*c[j+1] for j in range(len(c)-1)]
        z=self.h*target/(self.xknots[i+1]-self.xknots[i])
        for _ in range(20):
            dz=(horner(c,z)-target)/horner(d,z);z-=dz
            if abs(dz)<mp.mpf(10)**(-mp.mp.dps+15):break
        assert abs(horner(c,z)-target)<mp.mpf('1e-55')
        return i*self.h+z
    def seed_values(self,s):
        i,z=self.locate(s);return [horner(row,z) for row in self.seedrows[i]]

def lgl(N,X):
    xi=[mp.mpf(-1)]
    for i in range(1,N):
        z=-mp.cos(mp.pi*i/N)
        for _ in range(50):
            p=mp.legendre(N,z);dp=N*(z*p-mp.legendre(N-1,z))/(z*z-1)
            dd=(2*z*dp-N*(N+1)*p)/(1-z*z);dz=dp/dd;z-=dz
            if abs(dz)<mp.mpf(10)**(-mp.mp.dps+12):break
        xi.append(z)
    xi.append(mp.mpf(1));P=[mp.legendre(N,z) for z in xi]
    w=[X/(N*(N+1)*p*p) for p in P]
    D=mp.matrix(N+1)
    for i in range(N+1):
        for j in range(N+1):
            if i!=j:D[i,j]=2/X*P[i]/P[j]/(xi[i]-xi[j])
        D[i,i]=-mp.fsum(D[i,j] for j in range(N+1) if i!=j)
    sbp=max(abs(w[i]*D[i,j]+w[j]*D[j,i]-((-1 if i==0 else 1 if i==N else 0) if i==j else 0)) for i in range(N+1) for j in range(N+1))
    polynomial=max(abs(v) for power in (0,1,2,3,7) for v in (D*mp.matrix([z**power for z in xi])-mp.matrix([2/X*power*z**(power-1) if power else 0 for z in xi])))
    return xi,w,D,{'sbp':sbp,'polynomial':polynomial,'mass_positive':all(v>0 for v in w)}

def grid_jets(U,D,w,k,p,weak):
    A,B,F=U;dim=len(A);u1=[D*u for u in U]
    E=[mp.exp(2*b) for b in B];Q=[k*mp.exp(2*b-2*a) for a,b in zip(A,B)]
    V=[-6+p['m2']*f*f/2 for f in F]
    s2=[D*v for v in u1]
    for i in range(dim):
        a,b,f=[u[i] for u in u1]
        s2[0][i]+=3*a*a-2*Q[i]+2*E[i]*V[i]/3
        s2[1][i]+=-3*a*a+3*Q[i]-E[i]*V[i]/3+f*f/2
        s2[2][i]+=3*a*f-p['m2']*E[i]*F[i]
    if weak:
        for side,i in enumerate((0,dim-1)):
            sigma=1-2*side;up=p['gamma']*(F[i]-p['v0' if side==0 else 'v1'])
            wall=p['lambda_a' if side==0 else 'lambda_b']+up*up/(2*p['gamma'])
            g=[-sigma*mp.exp(B[i])*wall/6]*2+[sigma*mp.exp(B[i])*up/2]
            for j in range(3):s2[j][i]+=(-sigma)/w[i]*(g[j]-u1[j][i])
    d2=[D*v for v in s2];s4=[D*v for v in d2]
    for i in range(dim):
        a,b,f=[u[i] for u in u1];a2,b2,f2=[u[i] for u in s2];da,db,df=[u[i] for u in d2]
        dEV=E[i]*(2*V[i]*b2+p['m2']*F[i]*f2)
        s4[0][i]+=6*a*da-4*Q[i]*(b2-a2)+2*dEV/3-6*a2*a2
        s4[1][i]+=-6*a*da+6*Q[i]*(b2-a2)-dEV/3+f*df+6*a2*a2-f2*f2
        s4[2][i]+=3*(da*f+a*df)-p['m2']*E[i]*(2*b2*F[i]+f2)-6*a2*f2
    if weak:
        for side,i in enumerate((0,dim-1)):
            sigma=1-2*side;up=p['gamma']*(F[i]-p['v0' if side==0 else 'v1'])
            wall=p['lambda_a' if side==0 else 'lambda_b']+up*up/(2*p['gamma'])
            b2=s2[1][i];f2=s2[2][i]
            dg=[-sigma*mp.exp(B[i])*(b2*wall+up*f2)/6]*2+[sigma*mp.exp(B[i])*(b2*up+p['gamma']*f2)/2]
            for j in range(3):s4[j][i]+=(-sigma)/w[i]*(dg[j]-d2[j][i])
    d4=[D*v for v in s4];rows=[]
    for side,i in enumerate((0,dim-1)):
        sigma=1-2*side;up=p['gamma']*(F[i]-p['v0' if side==0 else 'v1'])
        wall=p['lambda_a' if side==0 else 'lambda_b']+up*up/(2*p['gamma'])
        b2=s2[1][i];b4=s4[1][i];f2=s2[2][i];f4=s4[2][i];r=[[],[],[]]
        for j in range(3):
            vals=[mp.exp(-B[i])*u1[j][i],mp.exp(-B[i])*(d2[j][i]-b2*u1[j][i]),mp.exp(-B[i])*(d4[j][i]-b4*u1[j][i]-6*b2*d2[j][i]+3*b2*b2*u1[j][i])]
            if j<2:extra=[sigma*wall/6,sigma*up*f2/6,sigma*(up*f4+3*p['gamma']*f2*f2)/6]
            else:extra=[-sigma*up/2,-sigma*p['gamma']*f2/2,-sigma*p['gamma']*f4/2]
            for a in range(3):r[a].append(vals[a]+extra[a])
        rows.append(r)
    Axx=D*u1[0]
    ham=[6*k*mp.exp(-2*A[i])-6*mp.exp(-2*B[i])*(Axx[i]-u1[1][i]*u1[0][i])-12*mp.exp(-2*B[i])*u1[0][i]**2-mp.exp(-2*B[i])*u1[2][i]**2-2*V[i] for i in range(dim)]
    return {'hamiltonian_max':max(map(abs,ham)),'walls':rows,'second':[list(u) for u in s2],'fourth':[list(u) for u in s4]}

def run(level,case,N,dps):
    mp.mp.dps=dps;beg=time.monotonic();g=guard();d=Dense(level,case);q=d.qualify_gauge()
    assert q['max_q_sampled']<mp.mpf('.01')
    assert max(abs(v) for wall in q['final'] for row in wall[:2] for v in row)<mp.mpf('1e-10'),q
    assert max(abs(v) for wall in q['final'] for v in wall[2])<mp.mpf('1e-12'),q
    d.make_map();xi,w,D,op=lgl(N,d.X)
    s=[d.invert((z+1)*d.X/2) for z in xi];fields=[d.jets(z,0) for z in s]
    U=[mp.matrix([r[j][0] for r in fields]) for j in range(3)]
    seeds=[d.seed_values(z) for z in s];jac=[mp.exp(r[1][0]-r[3][0]) for r in fields]
    norm=2*mp.fsum(wi*mp.exp(2*r[0])*(r[6]**2+6*r[5]**2)*j for wi,r,j in zip(w,seeds,jac))
    tangent=-2*mp.fsum(wi*r[5]*j for wi,r,j in zip(w,seeds,jac))
    separation=mp.fsum(wi*mp.exp(u) for wi,u in zip(w,U[1]))
    r={'guard':g,'level':level,'case':case,'N':N,'dps':dps,'epsilon':d.eps,'k':d.k,'mu':d.mu,'D_star':d.D,'X':d.X,'action':d.par,'gauge':q,'operator':op,'strong':grid_jets(U,D,w,d.k,d.par,False),'weak':grid_jets(U,D,w,d.k,d.par,True),'norm':norm,'separation_tangent':tangent,'proper_separation':separation,'inverse_jacobian_error':max(abs(v-j) for v,j in zip(D*mp.matrix(s),jac)),'evolution_steps':0}
    data={'N':N,'dps':dps,'X':d.X,'xi':xi,'x':[(z+1)*d.X/2 for z in xi],'s':s,'weights':w,'A':list(U[0]),'B':list(U[1]),'Phi':list(U[2]),'velocities':[[mp.mpf(0)]*(N+1) for _ in range(3)],'seed_fields':seeds,'ell':[r[3][0] for r in fields],'gauge_coefficients':d.q,'k':d.k,'action':d.par,'coordinate_knots':d.xknots,'coordinate_integral_polynomials':d.xpoly,'Cauchy_constants':{'K_ij':0,'Pi':0,'collapse_scalar':0,'collapse_momentum':0,'shift':0},'fields':['A','B','Phi']}
    path=ROOT/'results'/f'{level}_case{case}_N{N}_p{dps}'
    save(path.with_suffix('.grid.json'),data);r['grid_sha256']=digest(path.with_suffix('.grid.json'));r['seconds']=time.monotonic()-beg
    save(path.with_suffix('.json'),r)
    print(json.dumps({'case':case,'level':level,'N':N,'dps':dps,'seconds':round(r['seconds'],2),'H':str(r['strong']['hamiltonian_max']),'C4_strong':str(max(abs(v) for wall in r['strong']['walls'] for v in wall[2])),'C4_weak':str(max(abs(v) for wall in r['weak']['walls'] for v in wall[2]))}),flush=True)
    return r

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--level',default='fine_c4');ap.add_argument('--case',type=int,required=True);ap.add_argument('--N',type=int,default=64);ap.add_argument('--dps',type=int,default=80);args=ap.parse_args();run(args.level,args.case,args.N,args.dps)
