import hashlib,json,os,sys
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from interval import I,box
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
    p=HERE/n;assert not p.exists();tmp=HERE/(n+'.tmp')
    with tmp.open('x') as f:json.dump(d,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,p);tmp.unlink()
def get(v):return box(F(v['lo']),F(v['hi']))
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    tested=HERE.parent/'T15_COMPACT_WALL_COMPARISON'
    assert not any((tested/p).exists() for p in ('RESOURCE_START.json','EXECUTION.json','RESULT.json','FAILURE.json')),'NOT_PROSPECTIVE'
    parent=json.loads((HERE.parent/'T12_DIRICHLET_CEILING/RESULT.json').read_text())
    q=json.loads((HERE.parent/'T14_DIRICHLET_FORCED_PROFILE/RESULT.json').read_text())['quantities']
    mu=get(parent['physical_mu_bracket']);C=get(q['equal_compact_response_magnitude']);t=I(F(1,101))
    assert C.lo>0
    raw=mu-t*C;window=mu-t*C*box(F(4,5),F(6,5))
    assert window.contains(raw)
    D=F(1,50);d=D/2;gap=D*D/3
    # Leading mixed solution f=-2r²+2dr+4d². L=f'+2r=-2r+2d.
    assert -2*d*d-2*d*d+4*d*d==0
    assert -2*d+2*d==0
    assert -4*d*d==3*(-gap)
    mixed=I(-12)-box(gap*F(4,5),gap*F(6,5))
    preds={name:dict(gap=str(gap),mass_window=mixed.record(),model='leading_mixed_parabola')
        for name in ('lower_dirichlet','upper_dirichlet')}
    preds['equal_100']=dict(raw_linear_mass=raw.record(),mass_window=window.record(),
        compact_t='1/101',base_mass=mu.record(),equal_response_magnitude=C.record(),
        correction_window=(t*C*box(F(4,5),F(6,5))).record(),model='local_dirichlet_response')
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='COMPACT_WALL_PREDICTIONS_PUBLISHED',predictions=preds,
        relative_correction_tolerance='1/5',fit_parameters=0,error_bound_claim=False,
        T15_started=False,controls_passed=True))
try:main()
except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
