import hashlib,json,sys,signal,math
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,taylor
from interval import I,box
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    core.controls()
    x=taylor.const(1,9);x[1]=I(1);prod=taylor.mul(x,taylor.inv(x))
    assert prod[0].contains(1) and all(v.contains(0) for v in prod[1:]),'RECIPROCAL_PRODUCT'
    try:taylor.inv([box(-1,1),I(0)])
    except AssertionError:pass
    else:raise AssertionError('ZERO_RECIPROCAL_NOT_REJECTED')
    tests=[]
    for h in (F(1,100),F(-1,100)):
        y=[I(1)];one=lambda z:[taylor.const(1,len(z[0]))]
        r=taylor.step(y,h,lambda z:[I(1)],one,[I(2)],False)
        assert r[0].contains(1+h),'CONSTANT_EXACT'
        r=taylor.step(y,h,lambda z:z,lambda z:z,[I(3)],False)
        ah=abs(h);lo=sum((ah**j/F(math.factorial(j)) for j in range(25)),F(0))
        tail=ah**25/F(math.factorial(25))/(1-ah/F(26));exact=box(lo,lo+tail)
        if h<0:exact=1/exact
        assert r[0].contains(exact),'EXPONENTIAL_ENCLOSURE'
        e=taylor.step(y,h,lambda z:z,lambda z:z,[I(3)],False,1)
        old=core.step(y,h,lambda z:z,[I(3)],False)
        assert e[0].bounds()==old[0].bounds(),'FIRST_ORDER_IDENTITY'
        tests.append(dict(h=str(h),exponential=r[0].record(),rational_reference=exact.record()))
    try:taylor.step([I(1)],F(1,100),lambda z:z,lambda z:z,[I(0)],False)
    except AssertionError:pass
    else:raise AssertionError('UNDERSIZED_TUBE_NOT_REJECTED')
    z=taylor.coefficients([I(x) for x in (1,-2,0,0,1,0,0)],4,lambda a:taylor.rhs(a,F(-12),'g'))
    assert all((z[5][j]*math.factorial(j)).contains(v) for j,v in ((2,-4),(3,-72),(4,-1256))),'CENTRAL_JET'
    controls=dict(signed_exponential=tests,reciprocal=True,undersized_rejected=True,central_jet=True)
    backgrounds={}
    for sign in (-1,1):
        vals=[]
        for n in (8,16):
            y=taylor.background(n,F(sign,200));vals.append(y)
            assert core.ham(y).contains(0)
        assert all(core.overlap(a,b) for a,b in zip(*vals)),'RESOLUTION_OVERLAP'
        ref=json.loads((HERE.parent/'T1_HALF_WIDTH/BACKGROUND_32768.json').read_text())['lower' if sign<0 else 'upper']
        assert all(core.overlap(v,box(F(r['lo']),F(r['hi']))) for v,r in zip(vals[-1],ref)),'EULER_ANCHOR'
        backgrounds[str(sign)]=[[v.record() for v in y] for y in vals]
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='QUALIFIED_TAYLOR_INTERVAL_METHOD',order=8,controls=controls,
        background_enclosures=backgrounds,all_gates_passed=True,scientific_root_computed=False))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
