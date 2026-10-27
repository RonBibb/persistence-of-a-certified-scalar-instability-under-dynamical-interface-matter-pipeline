import sys,json,signal,math,time
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,taylor,scaled,method,analytic_jet as aj
from interval import I,box,power
def proof(beta):
    lam=[F(0)]*aj.M;lam[2]=F(-2,3);lam[4]=F(20,9);lam[6]=beta
    B=[F(0)]*aj.M;stages=[]
    for j in range(6):
        e,o,z=aj.boundary(aj.P(lam),aj.P(B));left=e-o.shift(1)
        B[j]+=left.c[j+1]
        e,o,z=aj.boundary(aj.P(lam),aj.P(B));left=e-o.shift(1)
        assert all(x==0 for x in left.c[:j+2]),'LOWER_SERIES_CANCELLATION'
        stages.append([j,str(B[j])])
    assert all(x==0 for x in left.c),'LOWER_EXACT_TO_D6'
    upper=e+o.shift(1)
    assert upper.c[:2]==(F(0),F(0))
    pl=sum((z[4][j].shift(j)*((-1)**j) for j in range(aj.N)),aj.P(0))
    C=aj.P(list(upper.c[2:]))/pl
    assert C.c[:4]==(F(0),)*4,'CHARACTERISTIC_ZERO_JET'
    assert C.c[4]==-6*(beta+F(383,15)),'FOURTH_COEFFICIENT'
    return dict(beta=str(beta),B_coefficients=[str(v) for v in B],stages=stages,
        C_coefficients_through_four=[str(v) for v in C.c[:5]],
        expected_scaled_fourth=str(C.c[4]*method.SCALE**4))
def controls():
    q=box(0,F(1,100));d=method.seed(q)
    inv=d+1;product=inv*inv.inverse()
    assert product.c[0].contains(1) and all(v.contains(0) for v in product.c[1:])
    try:method.seed(box(-1,1)).inverse()
    except AssertionError:pass
    else:raise AssertionError('PARAMETER_ZERO_DIVISOR')
    for h in (F(-1,16),F(1,16)):
        c=(d**4).c
        y=taylor.step([I(0)]*5,h,lambda v:c,
            lambda z:[taylor.const(v,len(z[0])) for v in c],[I(1)]*5,False,8)
        for k,v in enumerate(y):
            for qv in (F(0),F(1,100)):
                assert v.contains(h*math.comb(4,k)*qv**(4-k)*method.SCALE**k),'MANUFACTURED_CANCELLATION'
        assert y[4].contains(h*method.SCALE**4)
    try:taylor.step([I(0)]*5,F(1,16),lambda v:[I(1)]*5,
        lambda z:[taylor.const(1,len(z[0])) for _ in z],[I(0)]*5,False,8)
    except AssertionError:pass
    else:raise AssertionError('UNDERSIZED_TUBE')
    return dict(reciprocal=True,zero_divisor_rejected=True,signed_manufactured_d4=True,undersized_tube_rejected=True)
def pointwise(n,q,beta,rep):
    d=I(q);alpha=-F(2,3)+F(20,9)*d*d+beta*power(d,4)
    low=scaled.background(n,-1,d);up=scaled.background(n,1,d)
    a,H,P,t=low;G=3*alpha/(a*a*t)
    y=low+[I(1),I(0),G if rep=='G' else G-2*t]
    for _ in range(2*n):y=scaled.step(y,F(1,n),d,alpha,rep)
    return y
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    start=time.monotonic();core.save('CONTROLS.json',controls())
    betas=(F(-766,25),F(-1532,75));proofs=[proof(b) for b in betas]
    core.save('ANALYTIC_ZERO_JETS.json',dict(proofs=proofs,scaled_parameter_step=str(method.SCALE)))
    for k,beta in enumerate(betas):
        for rep in ('G','W'):
            r=method.propagate(16,I(0),beta,rep);C=r['upper'][25:30]
            assert all(v.contains(0) for v in C[:4]),'ZERO_PARAMETER_DERIVATIVES'
            assert C[4].contains(F(proofs[k]['expected_scaled_fourth'])),'EXACT_C4_CONTROL'
            core.save('zero_'+str(k)+'_'+rep+'.json',dict(C=[v.record() for v in C]))
    results=[]
    for q,beta,rep in ((F(1,100),betas[0],'G'),(F(1,200),betas[1],'W')):
        runs=[]
        for n in (16,32):
            r=method.propagate(n,I(q),beta,rep);ordinary=pointwise(n,q,beta,rep)
            assert all(core.overlap(r['upper'][i*5],v) for i,v in enumerate(ordinary)),'POINTWISE_METHOD_OVERLAP'
            record=dict(q=str(q),beta=str(beta),representation=rep,n=n,
                upper=[v.record() for v in r['upper']],ordinary=[v.record() for v in ordinary])
            core.save('point_'+str(len(results))+'_'+str(n)+'.json',record);runs.append(r['upper'])
        assert all(core.overlap(a,b) for a,b in zip(*runs)),'DERIVATIVE_RESOLUTION_OVERLAP'
        results.append(dict(q=str(q),beta=str(beta),representation=rep))
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='QUALIFIED_FOURTH_PARAMETER_DERIVATIVE_METHOD',
        controls_passed=True,analytic_zero_jets_verified=True,pointwise_controls=results,
        wall_seconds=time.monotonic()-start,parameter_order=4,spatial_order=8,
        production_executed=False,all_technical_gates_passed=True))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('1190s qualification cap')));signal.alarm(1190)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=method.CONTEXT,error=repr(e)));raise
    finally:signal.alarm(0)
