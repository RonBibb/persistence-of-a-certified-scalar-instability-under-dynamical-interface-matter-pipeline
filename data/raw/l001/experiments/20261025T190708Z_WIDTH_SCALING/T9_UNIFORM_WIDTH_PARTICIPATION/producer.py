import sys,json,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,taylor,scaled
from interval import I,S,box
CTX={}
def hull(vs):return I(min(v.lo for v in vs),max(v.hi for v in vs))
def get(v):return box(F(v['lo']),F(v['hi']))
def evaluate(n,d,alpha,rep):
    low=scaled.background(n,-1,d);up=scaled.background(n,1,d)
    a,H,P,t=low;assert t.hi<0 and up[3].lo>0
    G=3*alpha/(a*a*t);y=low+[I(1),I(0),G if rep=='G' else G-2*t]
    aa=[];pp=[];ff=[];curv=[]
    for j in range(2*n):
        CTX.update(n=n,representation=rep,step=j+1)
        h=F(1,n);rr=[(I(h)*v).hi for v in scaled.RATES];tube=[v+I(-r,r) for v,r in zip(y,rr)]
        z=tube if rep=='W' else tube[:6]+[tube[6]-2*tube[3]*tube[4]]
        curvature=scaled.rhs(z,d,alpha,'W')[-1]
        if rep=='G':
            g=scaled.rhs(tube,d,alpha,'G')
            alternate=g[-1]-2*g[3]*tube[4]-2*tube[3]*g[4]
            assert core.overlap(curvature,alternate),'CURVATURE_CHAIN_RULE'
            curvature=hull([curvature,alternate])
        aa.append(tube[0]);pp.append(tube[4]);ff.append(tube[5]);curv.append(curvature)
        y=scaled.step(y,h,d,alpha,rep)
        assert scaled.constraint(y,d,alpha,rep).contains(0),'NORMALIZED_CONSTRAINT'
    assert scaled.ham(y,d).contains(0)
    assert all(core.overlap(a,b) for a,b in zip(y[:4],up))
    return dict(a=hull(aa),psi=hull(pp),F=hull(ff),F_second=hull(curv))
def derive(q,dlo,dhi):
    positive=q['psi'].lo>0;concave=q['F_second'].hi<0
    result=dict(positive_metric=positive,strict_scalar_concavity=concave,actual_root_positive_scalar_interior=positive and concave)
    if positive and concave:
        amin,amax=q['a'].bounds();pmin,pmax=q['psi'].bounds()
        gmin=-F(q['F_second'].hi,S);gmax=-F(q['F_second'].lo,S)
        IFlo=amin**2*4*gmin*gmin/15;IFhi=amax**2*4*gmax*gmax/15
        IPlo=2*amin**2*pmin*pmin;IPhi=2*amax**2*pmax*pmax
        lower=IFlo/(16*(dhi**4*IFlo+6*IPhi))
        upper=IFhi/(16*(dlo**4*IFhi+6*IPlo))
        assert 0<lower<=upper
        result['actual_root_certificates']=dict(IF=[str(IFlo),str(IFhi)],Ipsi=[str(IPlo),str(IPhi)],
            scalar_share_over_D4=[str(lower),str(upper)])
    return result
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    parent=json.loads((HERE.parent/'T6_UNIFORM_WIDTH_LEADING_BOUND/RESULT.json').read_text())
    assert parent['uniform_twenty_percent_bound']
    assert 2-F(4,3)+F(2,5)==F(16,15)
    assert (F(64,15)/(16*6*2))==F(1,45),'LIMIT_COEFFICIENT'
    cfg=json.loads((HERE/'CONFIG.json').read_text());assert cfg['bins']==16
    alpha=box(F(-4,5),F(-8,15));out=[]
    for b in range(16):
        dlo=F(b,1600);dhi=F(b+1,1600);d=box(dlo,dhi);runs={}
        assert parent['bins'][b]['d']==[str(dlo),str(dhi)],'BOUND_DOMAIN'
        CTX.update(bin=b)
        for rep in ('G','W'):
            for n in cfg['levels']:
                q=evaluate(n,d,alpha,rep);runs[rep,n]=q
                core.save('bin_'+str(b)+'_'+rep+'_'+str(n)+'.json',dict(quantities={k:v.record() for k,v in q.items()}))
            assert all(core.overlap(runs[rep,16][k],runs[rep,32][k]) for k in q),'LEVEL_OVERLAP'
        assert all(core.overlap(runs['G',32][k],runs['W',32][k]) for k in q),'REPRESENTATION_OVERLAP'
        q={k:hull([runs['G',32][k],runs['W',32][k]]) for k in q}
        result=dict(bin=b,d=[str(dlo),str(dhi)],quantities={k:v.record() for k,v in q.items()},consequences=derive(q,dlo,dhi))
        core.save('bin_'+str(b)+'_SUMMARY.json',result);out.append(result)
    valid=all(x['consequences']['actual_root_positive_scalar_interior'] for x in out)
    coefficient=None
    if valid:
        bb=[r['consequences']['actual_root_certificates']['scalar_share_over_D4'] for r in out]
        coefficient=[str(min(F(v[0]) for v in bb)),str(max(F(v[1]) for v in bb))]
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='UNIFORM_WIDTH_MODE_PARTICIPATION',bins=out,
        uniform_profile_mechanism=valid,uniform_scalar_share_over_D4=coefficient,
        analytic_zero_width_limit='1/45',certificates_separate_from_raw_IVPs=True,
        zero_width_not_physical_mode=True,all_technical_gates_passed=True))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CTX,error=repr(e)));raise
    finally:signal.alarm(0)
