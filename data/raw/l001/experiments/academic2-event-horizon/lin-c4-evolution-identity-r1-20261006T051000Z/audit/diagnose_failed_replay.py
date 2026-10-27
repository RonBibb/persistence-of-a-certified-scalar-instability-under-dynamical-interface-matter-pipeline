"""One diagnostic replay of failed case 0 / 100 digits / N160 only.

No IVP, time evolution, producer publication entry point, repair, alternative
map, signed case or acceptance-gate change. The inherited Dense gauge/map
constructor is deliberately shared to diagnose the exact reported failure.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time
from fractions import Fraction as Q
from pathlib import Path
import mpmath as mp

GUARD='1d038b90a66fa82ca09d5cd419c5352c37b539b94c2bbaeb82f246219fff9ab8'
BRANCH=Path('/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches')
NATIVE=BRANCH/'01-horizon-core/d1-native-cauchy-20261005T201829Z'
ADMISSION=BRANCH/'01-horizon-core/d1-evolution-admission-20261005T214600Z'
SPATIAL=BRANCH/'01-horizon-core/d1-spatial-evolution-20261005T232000Z'
ENV={'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTHONNOUSERSITE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def exactmp(x):
    assert mp.isfinite(x);sign,mantissa,exponent,_=x._mpf_
    return (-1 if sign else 1)*Q(mantissa)*Q(2)**exponent
def dec(x):return mp.nstr(x,100)
def horner(row,z):
    result=mp.mpf(0)
    for v in reversed(row):result=result*z+mp.mpf(v)
    return result
def difference(a,b):
    a,b=mp.mpf(a),mp.mpf(b);assert mp.isfinite(a) and mp.isfinite(b)
    return abs(a-b)
def material(seed,dense,q,s):
    h=mp.mpf(seed['h']);i=max(0,min(255,int(mp.floor(s/h))));z=s-i*h
    bg=[horner(row,z) for row in seed['segments'][i]]
    aa=horner(dense['segments'][i][0],z);eps=mp.mpf(dense['epsilon'])
    return [aa,aa+horner(q,s),bg[2]+eps*bg[6]+horner(dense['correction'],s),-2*eps*bg[5]]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.output).resolve()
    assert out.parent==root/'audit' and not out.exists()
    assert all(os.environ.get(k)==v for k,v in ENV.items())
    assert sha(root/'BINDINGS.json')==GUARD==read(root/'FREEZE_RECORD.json')['guard']
    binding=read(root/'BINDINGS.json');failure=read(root/'NUMERICAL_READBACK_FAILURE.json')
    assert failure['guard']==GUARD and failure['error']=='Frozen representation replay gate'
    assert failure['status']=='FAILED_CLOSED' and not failure['automatic_restart_allowed']
    assert not (root/'NUMERICAL_READBACK.json').exists()
    assert [p.name for p in (root/'readback').glob('case*-p*.json')]==['case0-p80.json']
    assert binding['runtime']['python']==platform.python_version() and binding['runtime']['mpmath']==mp.__version__
    sources=[ADMISSION/'code/producer.py',ADMISSION/'code/jet.py',NATIVE/'results/fine_c4/SEED.json',
             NATIVE/'results/fine_c4/case_0.dense.json',SPATIAL/'inputs/fine_c4_case0_N160_p80.grid.json']
    for p in sources:assert sha(p)==binding['inputs'][str(p)]
    assert sha(root/'numerical_readback.py')==binding['sources']['numerical_readback.py']
    sys.path.insert(0,str(ADMISSION/'code'))
    spec=importlib.util.spec_from_file_location('diagnostic_frozen_admission',sources[0])
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    mp.mp.dps=100;start=time.monotonic();d=module.Dense('fine_c4',0);d.qualify_gauge()
    selections=[]
    with mp.workdps(80):
        h80=mp.mpf(d.seed['h']);indices80=[max(0,min(255,int(mp.floor((i*h80)/h80)))) for i in range(256)]
    for i in range(256):
        actual,z=d.locate(i*d.h)
        if actual!=i or actual!=indices80[i]:
            selections.append({'nominal_cell':i,'selected_at_100_digits':actual,'selected_at_80_digits':indices80[i],
                               'division_minus_integer_at_100_digits':dec((i*d.h)/d.h-i),'offset':dec(z)})
    d.make_map()
    seed,dense,grid=map(read,sources[2:])
    errors={k:mp.mpf(0) for k in ('fields_at_saved_s','inverse_s','fields_at_reconstructed_s',
                                  'gauge_coefficients','map_coefficients','map_knots','length')}
    errors['length']=difference(d.X,grid['X'])
    errors['gauge_coefficients']=max(difference(a,b) for a,b in zip(d.q,grid['gauge_coefficients']))
    errors['map_knots']=max(difference(a,b) for a,b in zip(d.xknots,grid['coordinate_knots']))
    maximum=None;weighted_map=mp.mpf(0);weighted_derivative=mp.mpf(0);percell=[]
    for i,(new,old) in enumerate(zip(d.xpoly,grid['coordinate_integral_polynomials'])):
        assert len(new)==len(old)
        diffs=[difference(a,b) for a,b in zip(new,old)]
        for j,v in enumerate(diffs):
            if maximum is None or v>maximum[0]:maximum=(v,i,j)
        weighted=mp.fsum(v*abs(d.h)**j for j,v in enumerate(diffs))
        derivative=mp.fsum(j*v*abs(d.h)**(j-1) for j,v in enumerate(diffs) if j)
        weighted_map=max(weighted_map,weighted+difference(d.xknots[i],grid['coordinate_knots'][i]))
        weighted_derivative=max(weighted_derivative,derivative)
        if max(diffs)>mp.mpf('1e-50'):
            percell.append({'cell':i,'coefficient_max':dec(max(diffs)),'polynomial_difference_triangle_bound':dec(weighted),
                'selected_at_100_digits':d.locate(i*d.h)[0],'selected_at_80_digits':indices80[i]})
    errors['map_coefficients']=maximum[0]
    for i in range(161):
        s=mp.mpf(grid['s'][i]);x=mp.mpf(grid['x'][i]);si=d.invert(x)
        errors['inverse_s']=max(errors['inverse_s'],difference(si,s))
        for values,label in [(material(seed,dense,grid['gauge_coefficients'],s),'fields_at_saved_s'),
                             (material(seed,dense,d.q,si),'fields_at_reconstructed_s')]:
            for v,key in zip(values,('A','B','Phi','ell')):
                errors[label]=max(errors[label],difference(v,grid[key][i]))
    failed=[k for k,v in errors.items() if v>mp.mpf('1e-50')]
    assert failed,'Failed production gate was not reproduced; no altered tolerance is allowed'
    imax,jmax=maximum[1:];mismatch_cells={v['cell'] for v in percell}
    switched={v['nominal_cell'] for v in selections if v['selected_at_100_digits']!=v['selected_at_80_digits']}
    result={'status':'FAILED_GATE_REPRODUCED_DIAGNOSTIC_ONLY','guard':GUARD,'case':0,'dps':100,'N':160,
        'failure_sha256':sha(root/'NUMERICAL_READBACK_FAILURE.json'),'existing_passed_case_sha256':sha(root/'readback/case0-p80.json'),
        'source_sha256':sha(Path(__file__).resolve()),'input_hashes':{str(p):sha(p) for p in sources},
        'reconstruction_gate':'1e-50','gate_passed':False,'failed_metrics':failed,
        'errors_decimal':{k:dec(v) for k,v in errors.items()},'errors_exact_binary':{k:str(exactmp(v)) for k,v in errors.items()},
        'maximum_map_coefficient':{'cell':imax,'power':jmax,'absolute_difference':dec(maximum[0]),
            'selected_at_100_digits':d.locate(imax*d.h)[0],'selected_at_80_digits':indices80[imax],
            'new_coefficient':dec(d.xpoly[imax][jmax]),'saved_coefficient':grid['coordinate_integral_polynomials'][imax][jmax]},
        'knot_selection_diagnostics':selections,'cells_exceeding_raw_coefficient_gate':percell,
        'all_raw_coefficient_failures_occur_at_precision_changed_segment_selection':mismatch_cells<=switched,
        'weighted_represented_map_difference_diagnostic':dec(weighted_map),
        'weighted_represented_map_derivative_difference_diagnostic':dec(weighted_derivative),
        'interpretation':'The raw coefficient gate remains failed. Knot-selection and h-weighted polynomial diagnostics distinguish representation coefficients from physical or map-value errors; these finite-arithmetic diagnostic values are not validated continuum error certificates.',
        'exact_binary_note':'Exact rational values of the mpmath finite-precision residuals, not proof of exact-real reconstruction error.',
        'shared_frozen_gauge_map_constructor':True,'physical_IVP_run':False,'producer_restarted':False,
        'alternative_map_constructed':False,'signed_replay_run':False,'seconds':time.monotonic()-start}
    for p in sources:assert sha(p)==binding['inputs'][str(p)]
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    with out.open('x') as stream:stream.write(payload)
    print(payload,end='')


if __name__=='__main__':main()
