import sys,json,signal,time
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,method
from interval import I,box
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    qualified=json.loads((HERE.parent/'qualification/RESULT.json').read_text())
    assert qualified['classification']=='QUALIFIED_FOURTH_PARAMETER_DERIVATIVE_METHOD' and qualified['all_technical_gates_passed']
    assert core.digest(HERE/'method.py')==core.digest(HERE.parent/'qualification/method.py')
    config=json.loads((HERE/'CONFIG.json').read_text())
    assert config=={'bins':16,'n':16,'representations':['G','W'],'betas':['-766/25','-1532/75'],'scale':'1/100','spatial_order':8,'parameter_order':4}
    start=time.monotonic();out=[]
    for b in range(16):
        q=box(F(b,1600),F(b+1,1600));row=[]
        for k,beta in enumerate((F(-766,25),F(-1532,75))):
            assert method.alpha(method.seed(q),beta).c[0].in_exact(F(-4,5),F(-8,15)),'INHERITED_BRANCH_BRACKET'
            cases=[]
            for rep in ('G','W'):
                method.CONTEXT.update(bin=b,beta=str(beta),q=q.record(),representation=rep)
                t=time.monotonic();r=method.propagate(16,q,beta,rep)
                C=r['upper'][25:30];physical_fourth=C[4]/method.SCALE**4
                rec=dict(bin=b,d=[str(F(b,1600)),str(F(b+1,1600))],beta=str(beta),representation=rep,
                    lower=[v.record() for v in r['lower']],upper_background=[v.record() for v in r['upper_background']],
                    upper=[v.record() for v in r['upper']],scaled_characteristic_derivatives=[v.record() for v in C],
                    fourth_derivative_over_factorial=physical_fourth.record(),wall_seconds=time.monotonic()-t)
                core.save('bin_'+str(b)+'_beta_'+str(k)+'_'+rep+'.json',rec);cases.append(physical_fourth)
            assert core.overlap(*cases),'PARAMETER_REPRESENTATION_OVERLAP'
            hull=I(min(v.lo for v in cases),max(v.hi for v in cases))
            sign=1 if hull.lo>0 else -1 if hull.hi<0 else 0
            row.append(dict(beta=str(beta),fourth_derivative_over_factorial=hull.record(),
                sign=sign,expected_sign=1 if k==0 else -1,sign_certified=sign==(1 if k==0 else -1)))
        rec=dict(bin=b,d=[str(F(b,1600)),str(F(b+1,1600))],endpoints=row,
            signs_certified=all(v['sign_certified'] for v in row))
        core.save('bin_'+str(b)+'_SUMMARY.json',rec);out.append(rec)
    passed=all(v['signs_certified'] for v in out)
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='PASS_UNIFORM_SIXTH_ORDER_ENVELOPE' if passed else 'INCONCLUSIVE_DERIVATIVE_BOUND',
        bins=out,all_continuous_bins_completed=True,uniform_coefficient_envelope=['383/1200','383/800'] if passed else None,
        target_D=['0','1/50'],zero_excluded=True,all_technical_gates_passed=True,
        certified_counterexample=False,finite_eighth_order_remainder_about_exact_coefficient=False,
        wall_seconds=time.monotonic()-start))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('2690s production cap')));signal.alarm(2690)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=method.CONTEXT,error=repr(e)));raise
    finally:signal.alarm(0)
