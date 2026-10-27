import sys,json,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,jet
from interval import box
def integrate_x(z):
    return sum((z[j].shift(j)*F(2,j+1) for j in range(0,jet.N,2)),jet.P(0))
def get(v):return box(F(v['lo']),F(v['hi']))
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    parent=json.loads((HERE.parent/'T7_SIXTH_ORDER_DERIVATION/RESULT.json').read_text())
    lam=jet.P([F(v) for v in parent['lambda_halfwidth']])
    B=jet.P([F(v) for v in parent['central_g_halfwidth']])
    e,o,z=jet.boundary(lam,B)
    assert all(v==0 for v in e.c+o.c),'EXACT_BOUNDARY_JETS'
    a,H,Phi,T,psi,f,g=z
    a2=jet.mul(a,a)
    Fint=integrate_x(jet.mul(a2,jet.mul(f,f)))
    IP=integrate_x(jet.mul(a2,jet.mul(psi,psi)))
    SS=integrate_x(psi)
    assert Fint.c[:4]==(F(0),)*4
    IF=jet.P(list(Fint.c[4:]))  # Only coefficients through d^2 are complete.
    sn=IF/(16*(Fint+6*IP));cn=SS*SS/(Fint+6*IP)
    assert (sn.c[0],cn.c[0])==(F(1,45),F(1,3)),'LIMIT_CONTROLS'
    assert sn.c[1]==cn.c[1]==0,'SYMMETRIC_WIDTH_PARITY'
    coefficients={}
    for key,obj in [('scalar_fraction_over_D4',sn),('canonical_separation_squared_over_D',cn)]:
        coefficients[key]={'constant':str(obj.c[0]),'D2':str(obj.c[2]/4)}
    numerical=json.loads((HERE.parent/'T10_ACTUAL_MODE_NORM_SCALING/RESULT.json').read_text())
    comparisons={}
    for name,case in numerical['cases'].items():
        D=F(case['D']);row={}
        for key,c in coefficients.items():
            c0=F(c['constant']);c2=F(c['D2'])
            measured=(get(case['quantities'][key])-c0)/(D*D)
            remainder=get(case['quantities'][key])-c0-c2*D*D
            row[key]={'measured_D2_coefficient':measured.record(),
                'post_D2_remainder':remainder.record(),
                'relative_coefficient_discrepancy':((measured-c2)/abs(c2)).record() if c2 else None}
        comparisons[name]=row
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='EXACT_LOCAL_NORM_CORRECTIONS_WITH_RETROSPECTIVE_COMPARISON',
        coefficients=coefficients,comparisons=comparisons,
        fullwidth_order_published=2,no_higher_coefficients_claimed=True,
        finite_width_remainder_certified=False,retrospective_comparison=True,
        normalization_cancels=True,all_technical_gates_passed=True))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
