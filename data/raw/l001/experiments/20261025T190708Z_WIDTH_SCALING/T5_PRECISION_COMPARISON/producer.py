import sys,json,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core
from interval import I,box
def get(v):return box(F(v['lo']),F(v['hi']))
def classify(x,w):
    return 'SUPPORTED' if w.contains(x) else ('CONTRADICTED' if max(x.lo,w.lo)>min(x.hi,w.hi) else 'INCONCLUSIVE')
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    records=[json.loads((HERE.parent/n/'RESULT.json').read_text()) for n in ('T3_FULL_WIDTH_PRECISION','T4_HALF_WIDTH_PRECISION')]
    a,b=records;assert F(a['width'])==2*F(b['width'])
    ga,gb=[get(r['negative_lambda_gap']) for r in records];assert ga.lo>0 and gb.lo>0
    ca,cb=[get(r['leading_minus_actual_gap']) for r in records]
    result=dict(gap_ratio=(ga/gb).record(),coefficient_intervals=[r['fourth_order_coefficient'] for r in records])
    if ca.lo>0 and cb.lo>0:
        ratio=ca/cb;window=box(F(64,5),F(96,5))
        result.update(correction_ratio=ratio.record(),correction_ratio_window=window.record(),correction_ratio_outcome=classify(ratio,window))
    else:result.update(correction_ratio=None,correction_ratio_outcome='UNRESOLVED_OR_WRONG_CORRECTION_SIGN')
    remainder=[]
    for r in records:
        D=F(r['width']);g=get(r['negative_lambda_gap']);R=g-D*D/6+5*D**4/36
        remainder.append(dict(width=str(D),after_fourth_order=R.record(),scaled_by_D6=(R/D**6).record()))
    assert F(1,50)**4/F(1,100)**4==16 and F(1,50)**2/F(1,100)**2==4
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='CERTIFIED_TWO_WIDTH_PRECISION_COMPARISON',comparison=result,
        sixth_order_diagnostics=remainder,uniform_remainder_claim=False,asymptotic_order_claim=False,all_gates_passed=True))
try:main()
except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
