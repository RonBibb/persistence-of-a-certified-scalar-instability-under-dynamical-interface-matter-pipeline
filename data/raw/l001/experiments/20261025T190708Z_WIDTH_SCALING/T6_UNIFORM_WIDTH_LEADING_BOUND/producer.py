import sys,json,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,taylor,scaled
from interval import I,box
CTX={}
def controls():
    core.controls()
    for d in (I(0),I(F(1,200)),I(F(1,100))):
        for alpha in (F(-4,5),F(-8,15)):
            y=[I(v) for v in (1,-2,F(1,1000),F(1,3),F(6,5),F(2,5),F(1,5))]
            for rep in ('G','W'):
                j=scaled.jrhs([taylor.const(v,1) for v in y],d,alpha,rep)
                direct=scaled.rhs(y,d,alpha,rep)
                assert all(core.overlap(a[0],b) for a,b in zip(j,direct)),'SCALED_JET_CONSTANT'
            G=scaled.asG(y,'W');wg=scaled.rhs(y,d,alpha,'W');gg=scaled.rhs(G,d,alpha,'G')
            assert all(core.overlap(a,b) for a,b in zip(wg[:6],gg[:6]))
            assert core.overlap(wg[6]+2*wg[3]*y[4]+2*y[3]*wg[4],gg[6]),'SCALED_CHAIN_RULE'
            if d.lo>0:
                a,H,P,t,psi,Fp,g=G
                phys=[a,H,P,d*t,psi,d*d*Fp,d*g];mu=-12+d*d*alpha
                original=core.full(phys,mu)
                mapped=[d*original[0],d*original[1],d*original[2],original[3],d*original[4],original[5]/d,original[6]]
                assert all(core.overlap(a,b) for a,b in zip(mapped,gg)),'PHYSICAL_RESCALE'
    for alpha in (F(-4,5),F(-8,15)):
        d=I(0);n=8;low=scaled.background(n,-1,d)
        a,H,P,t=low;G=3*alpha/(a*a*t);y=low+[I(1),I(0),G]
        for j in range(2*n):y=scaled.step(y,F(1,n),d,alpha,'G')
        assert y[5].contains(-6*alpha-4),'EXACT_ZERO_WIDTH_LIMIT'
    return dict(physical_rescaling=True,jet_constants=True,independent_G_W_chain=True,formal_zero_width_limit=True)
def evaluate(low,up,n,d,alpha,rep):
    a,H,P,t=low;assert t.hi<0 and up[3].lo>0
    G=3*alpha/(a*a*t);y=low+[I(1),I(0),G if rep=='G' else G-2*t]
    assert scaled.constraint(y,d,alpha,rep).contains(0)
    for j in range(2*n):
        CTX.update(n=n,alpha=str(alpha),representation=rep,step=j+1)
        y=scaled.step(y,F(1,n),d,alpha,rep)
        assert scaled.constraint(y,d,alpha,rep).contains(0),'NORMALIZED_CONSTRAINT'
    assert scaled.ham(y,d).contains(0),'FINAL_HAMILTONIAN'
    assert all(core.overlap(a,b) for a,b in zip(y[:4],up)),'FRESH_ENDPOINT_OVERLAP'
    return dict(residual=y[5].record(),sign=core.sign(y[5]),constraint=scaled.constraint(y,d,alpha,rep).record(),upper_state=[v.record() for v in y])
def get(v):return box(F(v['lo']),F(v['hi']))
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    core.save('CONTROLS.json',controls());cfg=json.loads((HERE/'CONFIG.json').read_text())
    assert cfg['bins']==16 and F(cfg['d_max'])==F(1,100)
    outcomes=[]
    for b in range(cfg['bins']):
        lo=F(b,1600);hi=F(b+1,1600);d=box(lo,hi);runs={}
        CTX.update(bin=b,dlo=str(lo),dhi=str(hi))
        for n in cfg['levels']:
            low=scaled.background(n,-1,d);up=scaled.background(n,1,d)
            core.save('bin_'+str(b)+'_BACKGROUND_'+str(n)+'.json',dict(lower=[v.record() for v in low],upper=[v.record() for v in up],d=[str(lo),str(hi)]))
            for rep in ('G','W'):
                for label,alpha in (('low',F(cfg['alpha_lo'])),('high',F(cfg['alpha_hi']))):
                    r=evaluate(low,up,n,d,alpha,rep);runs[rep,n,label]=r
                    core.save('bin_'+str(b)+'_'+rep+'_'+str(n)+'_'+label+'.json',r)
        for label in ('low','high'):
            for rep in ('G','W'):
                assert core.overlap(get(runs[rep,16,label]['residual']),get(runs[rep,32,label]['residual'])),'LEVEL_OVERLAP'
            assert core.overlap(get(runs['G',32,label]['residual']),get(runs['W',32,label]['residual'])),'REPRESENTATION_OVERLAP'
        ok=all(runs[rep,n,'low']['sign']==1 and runs[rep,n,'high']['sign']==-1 for rep in ('G','W') for n in cfg['levels'])
        summary=dict(bin=b,d=[str(lo),str(hi)],uniform_bracket_certified=ok)
        core.save('bin_'+str(b)+'_SUMMARY.json',summary);outcomes.append(summary)
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='UNIFORM_WIDTH_LEADING_GAP_TEST',bins=outcomes,
        all_technical_gates_passed=True,uniform_twenty_percent_bound=all(v['uniform_bracket_certified'] for v in outcomes),
        positive_width_domain='0<D<=1/50',scaled_alpha_bracket=[cfg['alpha_lo'],cfg['alpha_hi']],
        candidate_gap_over_D2_bounds=['2/15','1/5'],formal_zero_width_not_physical_mode=True,
        fourth_order_uniform_remainder_certified=False))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CTX,error=repr(e)));raise
    finally:signal.alarm(0)
