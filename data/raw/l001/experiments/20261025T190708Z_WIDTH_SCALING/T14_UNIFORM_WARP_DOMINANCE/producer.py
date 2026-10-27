import sys,json,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    scalar=json.loads((HERE.parent/'T9_UNIFORM_WIDTH_PARTICIPATION/RESULT.json').read_text())
    coh=json.loads((HERE.parent/'T12_UNIFORM_SEPARATION_COHERENCE/RESULT.json').read_text())
    samples=json.loads((HERE.parent/'T13_SEPARATION_RESPONSE_BUDGET/RESULT.json').read_text())
    assert scalar['uniform_profile_mechanism'] and coh['strict_for_positive_width']
    assert len(scalar['bins'])==len(coh['bins'])==16
    for rows in (scalar['bins'],coh['bins']):
        assert F(rows[0]['d'][0])==0 and F(rows[-1]['d'][1])==F(1,100)
        assert all(a['d'][1]==b['d'][0] for a,b in zip(rows,rows[1:]))
    amin,amax=F(9,10),F(11,10);Hmin,Hmax=F(19,10),F(21,10)
    Dmax=F(1,50);Tmax=Dmax*F(3,2)/2
    m=(4*Hmin**2+6/amax**2)/amax**2
    M=(4*Hmax**2+F(2,3)*Tmax**2+6/amin**2)/amin**2
    assert 0<m<=22<=M and 4*F(2)**2+6==22
    Cs=F(scalar['uniform_scalar_share_over_D4'][1]);Ce=F(coh['uniform_defect_over_D8_upper'])
    Jmax=2/amin**2
    A=m/72;B=Jmax*Cs/6;C=Jmax*Ce/6
    lower=A-B*Dmax**2-C*Dmax**6
    ratio=(B*Dmax**2+C*Dmax**6)/A
    certified=lower>0 and ratio<1
    checks={}
    for name,row in samples['cases'].items():
        D=F(row['D']);assert 0<D<=Dmax
        lo=F(row['direct_net']['lo']);hi=F(row['direct_net']['hi'])
        checks[name]=max(lo,lower*D**2)<=min(hi,M*D**2/72)
        assert checks[name],'DIRECT_SAMPLE_CONSISTENCY'
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='UNIFORM_WARP_DOMINANCE_TEST',
        domain_D=['0','1/50'],zero_excluded=True,g_second=[str(m),str(M)],
        scalar_coefficient_upper=str(Cs),coherence_coefficient_upper=str(Ce),
        net_response_over_D2=[str(lower),str(M/72)],
        combined_penalty_over_warp_upper=str(ratio),uniform_dominance_certified=certified,
        sample_consistency=checks,all_technical_gates_passed=True,
        accounting_not_causal_intervention=True))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
