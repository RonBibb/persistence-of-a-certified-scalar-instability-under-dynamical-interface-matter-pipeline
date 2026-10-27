import sys,json,signal,time
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,method
from interval import I,box
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.platform=='linux' and sys.version_info[:3]==(3,12,3)
    assert core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    cfg=json.loads((HERE/'CONFIG.json').read_text())
    expected={"center":"1/200","halfwidths":["0","1/3200","1/32000","1/320000","1/3200000"],"betas":["-766/25","-1532/75"],"representations":["G","W"],"n":16,"parameter_order":4,"spatial_order":8,"scale":"1/100"}
    assert cfg==expected
    start=time.monotonic();rows=[];prior={}
    for level,w in enumerate(cfg['halfwidths']):
        hw=F(w);q=box(F(cfg['center'])-hw,F(cfg['center'])+hw);ends=[]
        for k,beta in enumerate(map(F,cfg['betas'])):
            assert method.alpha(method.seed(q),beta).c[0].in_exact(F(-4,5),F(-8,15))
            vals=[]
            for rep in cfg['representations']:
                method.CONTEXT.update(level=level,halfwidth=w,beta=str(beta),representation=rep)
                t=time.monotonic();v=method.propagate(16,q,beta,rep)
                C=v['upper'][25:30];d4=C[4]/method.SCALE**4
                for old in prior.get((k,rep),[]): assert core.overlap(old,d4),'NESTED_INPUT_OUTPUT_OVERLAP'
                prior.setdefault((k,rep),[]).append(d4)
                core.save('level_'+str(level)+'_beta_'+str(k)+'_'+rep+'.json',
                    dict(level=level,halfwidth=w,q=q.record(),beta=str(beta),representation=rep,
                    lower=[x.record() for x in v['lower']],upper_background=[x.record() for x in v['upper_background']],
                    upper=[x.record() for x in v['upper']],scaled_characteristic_derivatives=[x.record() for x in C],
                    fourth_derivative_over_factorial=d4.record(),wall_seconds=time.monotonic()-t))
                vals.append(d4)
            assert core.overlap(*vals),'REPRESENTATION_OVERLAP'
            hull=I(min(x.lo for x in vals),max(x.hi for x in vals));sign=core.sign(hull)
            ends.append(dict(beta=str(beta),fourth_derivative_over_factorial=hull.record(),sign=sign,expected_sign=1 if k==0 else -1,sign_certified=sign==(1 if k==0 else -1)))
        row=dict(level=level,halfwidth=w,endpoints=ends,signs_certified=all(x['sign_certified'] for x in ends))
        core.save('level_'+str(level)+'_SUMMARY.json',row);rows.append(row)
    recovered=[x['halfwidth'] for x in rows[1:] if x['signs_certified']]
    cls='POINT_CONTROL_UNRESOLVED' if not rows[0]['signs_certified'] else ('SIGN_RECOVERY_AT_TESTED_WIDTH' if recovered else 'NO_SIGN_RECOVERY_AT_TESTED_WIDTHS')
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification=cls,levels=rows,first_sign_recovery_halfwidth=recovered[0] if recovered else None,
        all_technical_gates_passed=True,all_frozen_levels_completed=True,uniform_envelope_certified=False,
        wall_seconds=time.monotonic()-start))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('2690s diagnostic cap')));signal.alarm(2690)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=method.CONTEXT,error=repr(e)));raise
    finally:signal.alarm(0)
