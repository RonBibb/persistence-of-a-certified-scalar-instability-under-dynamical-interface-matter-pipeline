import sys,json,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core
def bounds(q):return F(q['lo']),F(q['hi'])
def mean(poly):return sum((v/F(j+1) for j,v in enumerate(poly) if j%2==0),F(0))
def multiply(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for j,x in enumerate(a):
        for k,y in enumerate(b):c[j+k]+=x*y
    return c
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    parent=json.loads((HERE.parent/'T9_UNIFORM_WIDTH_PARTICIPATION/RESULT.json').read_text())
    assert parent['uniform_profile_mechanism']
    out=[]
    for row in parent['bins']:
        q=row['quantities'];amin,amax=bounds(q['a']);pmin,pmax=bounds(q['psi']);fl,fh=bounds(q['F'])
        assert amin>0 and pmin>0 and row['consequences']['actual_root_positive_scalar_interior']
        M=amax**2*F(3,2)*max(abs(fl),abs(fh))/3
        wmin=amin**2*pmin
        C=M*M/(256*wmin*wmin)
        assert C>0
        out.append(dict(bin=row['bin'],d=row['d'],tau_abs_bound='3/2',derivative_bound_over_d4=str(M),
            positive_w_lower=str(wmin),coherence_defect_over_D8_upper=str(C),
            actual_root_defect_strictly_positive=True))
    assert len(out)==16 and F(out[0]['d'][0])==0 and F(out[-1]['d'][1])==F(1,100)
    assert all(a['d'][1]==b['d'][0] for a,b in zip(out,out[1:]))
    h=[F(0),F(0),F(-1,3),F(0),F(1,6)]
    deriv=[F(j)*h[j] for j in range(1,len(h))]
    assert deriv==[F(0),F(-2,3),F(0),F(2,3)],'LIMIT_EQUATION'
    var=mean(multiply(h,h))-mean(h)**2
    assert var==F(16,4725) and var/256==F(1,75600)
    numerical=json.loads((HERE.parent/'T10_ACTUAL_MODE_NORM_SCALING/RESULT.json').read_text())
    comparisons={}
    for name,case in numerical['cases'].items():
        D=F(case['D']);d=D/2
        eligible=[F(r['coherence_defect_over_D8_upper']) for r in out if F(r['d'][0])<=d<=F(r['d'][1])]
        C=max(eligible) # Conservative at shared bin boundaries.
        lo,hi=bounds(case['quantities']['coherence_raw'])
        deficit=(1-hi,1-lo);upper=C*D**8
        assert max(deficit[0],F(0))<=min(deficit[1],upper),'RAW_THEOREM_CONSISTENCY'
        comparisons[name]=dict(raw_defect=[str(v) for v in deficit],theorem_defect_upper=str(upper),
            leading_local_prediction=str(D**8/F(75600)),no_raw_interval_replacement=True)
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='UNIFORM_D8_COHERENCE_MECHANISM',
        bins=out,uniform_defect_over_D8_upper=str(max(F(r['coherence_defect_over_D8_upper']) for r in out)),
        analytic_defect_over_D8_limit=str(var/256),comparisons=comparisons,
        strict_for_positive_width=True,zero_width_not_physical_mode=True,
        local_limit_not_finite_remainder=True,all_technical_gates_passed=True))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
