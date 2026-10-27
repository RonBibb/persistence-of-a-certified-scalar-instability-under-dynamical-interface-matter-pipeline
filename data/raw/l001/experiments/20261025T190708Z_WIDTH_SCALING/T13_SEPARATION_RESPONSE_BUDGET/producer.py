import sys,json,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,jet
from interval import I,box
def get(q):return box(F(q['lo']),F(q['hi']))
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    parent=json.loads((HERE.parent/'T7_SIXTH_ORDER_DERIVATION/RESULT.json').read_text())
    lam=jet.P([F(v) for v in parent['lambda_halfwidth']]);B=jet.P([F(v) for v in parent['central_g_halfwidth']])
    e,o,z=jet.boundary(lam,B)
    assert all(v==0 for v in e.c+o.c)
    inva2=jet.inv(jet.mul(z[0],z[0]))
    Jseries=sum((inva2[j].shift(j)*F(2,j+1) for j in range(0,jet.N,2)),jet.P(0))
    assert Jseries.c[0]==2 and Jseries.c[1]==0
    J2=Jseries.c[2]/4
    norm=json.loads((HERE.parent/'T10_ACTUAL_MODE_NORM_SCALING/RESULT.json').read_text())
    coh=json.loads((HERE.parent/'T12_UNIFORM_SEPARATION_COHERENCE/RESULT.json').read_text())
    out={}
    for name,case in norm['cases'].items():
        q=case['quantities'];J=get(q['J']);s=get(q['scalar_fraction']);cn=get(q['canonical_separation_squared_over_D'])
        assert J.lo>0 and s.lo>0 and s.hi<I(1).lo
        du=F(coh['comparisons'][name]['theorem_defect_upper'])
        defect=box(0,du)
        warp=(J-2)/6;scalar=J*s/6;coherence=J*(1-s)*defect/6
        net=warp-scalar-coherence;direct=cn-F(1,3)
        assert warp.lo>0 and direct.lo>0
        assert core.overlap(net,direct),'DIRECT_RECONSTRUCTION'
        rawidentity=J*get(q['coherence_raw'])*(1-s)/6
        assert core.overlap(rawidentity,cn),'RAW_IDENTITY'
        out[name]=dict(D=case['D'],warp_gain=warp.record(),scalar_penalty=scalar.record(),
            coherence_penalty=coherence.record(),reconstructed_net=net.record(),direct_net=direct.record(),
            scalar_penalty_over_warp_gain=(scalar/warp).record(),
            coherence_penalty_over_warp_gain=(coherence/warp).record(),
            coherence_penalty_strictly_positive_but_no_numeric_lower=True)
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='CERTIFIED_SEPARATION_RESPONSE_ACCOUNTING',
        analytic_J_D2_coefficient=str(J2),leading_terms=dict(warp_gain_D2=str(J2/6),
        scalar_penalty_D4='1/135',coherence_penalty_D8='1/226800'),cases=out,
        accounting_not_causal_intervention=True,raw_intervals_preserved=True,
        uniform_remainder_not_claimed=True,all_technical_gates_passed=True))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
