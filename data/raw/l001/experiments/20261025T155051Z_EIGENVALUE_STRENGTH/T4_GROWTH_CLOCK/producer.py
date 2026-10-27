import hashlib,json,math,os,sys,signal
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from interval import I,S,box
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
    dest=HERE/n;assert not dest.exists()
    tmp=HERE/(n+'.tmp')
    with tmp.open('x') as f:json.dump(d,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,dest);tmp.unlink()
def sqrtbox(x):
    assert x.lo>=0
    a=math.isqrt(x.lo*S);b=math.isqrt(x.hi*S)
    if b*b<x.hi*S:b+=1
    return I(a,b)
def rate(mu):return (sqrtbox(9-4*mu/3)-3)/2
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    for mu,r in ((F(0),F(0)),(F(-12),F(1)),(F(-21,4),F(1,2))):
        assert rate(I(mu)).contains(r)
    out={};rates={};masses={}
    for name in ('T1R2_SOFT_MODE','T2_STIFF_MODE'):
        data=json.loads((HERE.parent/name/'RESULT.json').read_text());b=data['physical_mu_bracket']
        mu=box(F(b['lo']),F(b['hi']));r=rate(mu)
        assert r.lo>0 and r.hi<S,'EXTRA_BAND_RATE'
        assert rate(I(F(b['hi']))).lo>=r.lo and rate(I(F(b['lo']))).hi<=r.hi,'MONOTONE_BOUNDS'
        rates[name]=r
        masses[name]=mu
        out[name]=dict(mu=mu.record(),sigma_over_H=r.record(),Hubble_times_per_efold=(1/r).record())
    ratio=rates['T2_STIFF_MODE']/rates['T1R2_SOFT_MODE']
    massratio=masses['T2_STIFF_MODE']/masses['T1R2_SOFT_MODE']
    assert ratio.lo>0 and ratio.hi<S,'SUPPRESSION'
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='CONDITIONAL_SEPARATED_MODE_GROWTH_RATES',cases=out,
        rate_ratio=ratio.record(),suppressed_fraction=(1-ratio).record(),clock_invariant_ratio=True,
        mass_squared_magnitude_ratio=massratio.record(),mass_squared_suppressed_fraction=(1-massratio).record(),
        persistent_mode_rate_strictly_above_one=True,arbitrary_data_dominance_claim=False,
        seconds_or_years_inferred=False,controls_passed=True))
if __name__=='__main__':
    def timeout(s,f):raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
