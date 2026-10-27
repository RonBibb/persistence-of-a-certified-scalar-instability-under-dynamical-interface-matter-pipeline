"""Three readouts of three formal response directions, exact saved intervals."""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('identifiability_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT; I=c.I
PARENTS={'t2':'T2R1_AB_SELECTED_MODE','t4':'T4_AB_FIRST_CURRENT','t6':'T6_AB_MINIMUM_SEPARATION_TRANSFER',
         't7':'T7_AB_MINIMUM_PARTITION','t8':'T8_AB_NEUTRAL_RADAR_RESPONSE','t10':'T10_AB_CURRENT_RADAR_RESPONSE'}
LABELS={'t2':'SELECTED_NEUTRAL_MODE_CHARACTERIZED','t4':'FIRST_CURRENT_SEPARATION_COEFFICIENTS_ENCLOSED',
        't6':'NEUTRAL_MINIMUM_SEPARATION_TRANSFER_ENCLOSED','t7':'FIRST_CURRENT_PHYSICAL_MINIMUM_PARTITION_ENCLOSED',
        't8':'NEUTRAL_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','t10':'FIRST_CURRENT_OPERATIONAL_RADAR_RESPONSE_ENCLOSED'}
FILES={'t2':'strip_','t4':'assembled_','t6':'turn_','t7':'partition_','t8':'radar_','t10':'current_radar_'}
def path(key,file): return ROOT/'..'/PARENTS[key]/file
def det(columns):
    a,b,d=columns
    return a[0]*(b[1]*d[2]-b[2]*d[1])-b[0]*(a[1]*d[2]-a[2]*d[1])+d[0]*(a[1]*b[2]-a[2]*b[1])
def normalized_det(columns):
    a,b,d=columns
    return a[0]*(d[2]-b[2])+b[0]*(a[2]-d[2])+d[0]*(b[2]-a[2])

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY'); g=c.read(ROOT/'ADMISSION.json'); c.need(g.get('admitted') is True,'ADMISSION')
    for key,folder in PARENTS.items():
        c.need(g.get(key+'_terminal_review_accepted') is True,'REVIEW_REQUIRED:'+key)
        required=['../'+folder+'/TERMINAL_REVIEW.md','../'+folder+'/output/RESULT.json']
        required+=['../'+folder+'/output/'+FILES[key]+n+'.json' for n in ('primary','independent')]
        for rel in required: c.need(rel in g['sources'],'MISSING_BINDING:'+rel)
        c.need(c.read(path(key,'output/RESULT.json'))['classification']==LABELS[key],'PARENT_SCOPE:'+key)
    for rel,d in g['sources'].items(): c.need(c.sha(ROOT/rel)==d,'SOURCE_HASH:'+rel)
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for p,d in rt['files'].items(): c.need(c.sha(p)==d,'RUNTIME_HASH:'+p)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')

def controls():
    ident=[list(map(Q,row)) for row in ((1,0,0),(0,1,0),(0,0,1))]
    c.need(det(ident)==1,'BASIS_DETERMINANT')
    A=[list(map(Q,row)) for row in ((2,3,5),(7,11,13),(17,19,23))]
    c.need(det([A[1],A[0],A[2]])==-det(A),'COLUMN_PERMUTATION')
    scales=[Q(2,3),Q(5,7),Q(11,13)]
    scaled=[[v*s for v in col] for col,s in zip(A,scales)]
    c.need(det(scaled)==det(A)*scales[0]*scales[1]*scales[2],'COLUMN_SCALING')
    dependent=[A[0],A[1],[x+y for x,y in zip(A[0],A[1])]]
    c.need(det(dependent)==0,'DEPENDENT_COLUMNS')
    norm=[[v/col[1] for v in col] for col in A]
    c.need(all(col[1]==1 for col in norm),'EXACT_MIDDLE_ROW')
    c.need(normalized_det(norm)==det(norm)==det(A)/(A[0][1]*A[1][1]*A[2][1]),'NORMALIZED_DETERMINANT')
    boxed=[[I(v) for v in col] for col in norm]
    got=normalized_det(boxed); c.need(got.lo==got.hi==det(norm),'POINT_INTERVAL_CONTROL')
    return {'basis':True,'permutation':True,'scaling':True,'dependent_columns':True,
            'exact_normalized_middle_row':True,'independent_full_determinant_identity':True,'point_interval':True}

def evaluate(name):
    r={key:c.read(path(key,'output/'+prefix+name+'.json')) for key,prefix in FILES.items()}
    ball=c.interval
    c.need(r['t2']['mu_bounds']==r['t6']['mu_bounds']==r['t8']['mu_bounds'],'NEUTRAL_MASS_LINKAGE')
    neutral=[ball(r['t2']['observables']['deltaD_over_Q']),ball(r['t6']['turn_hull']['f']),
             ball(r['t8']['observables']['proper_roundtrip_coefficient'])]
    c.need(neutral[0].overlap(ball(r['t6']['deltaD_over_Q'])) and neutral[0].overlap(ball(r['t8']['observables']['deltaD_over_Q'])),'NEUTRAL_READOUT_LINKAGE')
    raw=[neutral]
    for side in ('lower','upper'):
        D=ball(r['t4']['channels'][side]['coefficient_total'])
        F=ball(r['t7']['channels'][side]['observables']['minimum_scalar_value'])
        R=ball(r['t10']['channels'][side]['observables']['proper_roundtrip_coefficient'])
        c.need(D.overlap(ball(r['t7']['channels'][side]['observables']['parent_total'])) and
               D.overlap(ball(r['t10']['channels'][side]['observables']['accepted_separation_coefficient'])),'CURRENT_READOUT_LINKAGE:'+side)
        raw.append([D,F,R])
    record={'engine':name,'column_order':['neutral','lower_current','upper_current'],
            'row_order':['proper_separation','minimum_scalar_value','elapsed_radar_proper_time'],
            'raw_columns':[[v.pack() for v in col] for col in raw]}
    if not all(col[1].lo>0 for col in raw):
        return {**record,'classification':'UNRESOLVED','reason':'STRICT_POSITIVE_MINIMUM_NORMALIZATION_UNRESOLVED'}
    # Middle row is exactly f/f=1 by algebra, not interval division f_box/f_box.
    norm=[[col[0]/col[1],I(1),col[2]/col[1]] for col in raw]
    authoritative=normalized_det(norm); rawdet=det(raw)
    secondary=rawdet/(raw[0][1]*raw[1][1]*raw[2][1])
    c.need(authoritative.overlap(secondary),'RAW_NORMALIZED_CONSISTENCY')
    return {**record,'normalized_columns':[[v.pack() for v in col] for col in norm],
            'authoritative_normalized_determinant':authoritative.pack(),'raw_determinant_consistency_only':rawdet.pack(),
            'raw_determinant_over_minimum_product_consistency_only':secondary.pack(),
            'classification':'UNRESOLVED' if authoritative.zero() else 'LOCAL_LINEAR_READOUT_INJECTIVITY'}

def main():
    c.need(not any((ROOT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART'); begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('IDENTIFIABILITY_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested=controls(); c.put('CONTROLS.json',tested); per={n:evaluate(n) for n in ('primary','independent')}
        combined=None; label='UNRESOLVED'
        if all('authoritative_normalized_determinant' in v for v in per.values()):
            a,b=[c.interval(per[n]['authoritative_normalized_determinant']) for n in ('primary','independent')]
            c.need(a.overlap(b),'ENGINE_DETERMINANT_DISAGREEMENT'); combined=a.hull(b)
            if not combined.zero(): label='LOCAL_LINEAR_READOUT_INJECTIVITY'
        c.put('RESULT.json',{'classification':label,'authoritative_normalized_determinant':None if combined is None else combined.pack(),
               'per_engine':per,'controls':tested,'seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'Local formal response-space injectivity for three specified same-emission readouts only. Current amplitudes lie in a nonnegative cone. No conditioning, noise robustness, mode excitation, finite-charge inverse or nonlinear uniqueness claim. Zero inclusion means unresolved, not degeneracy.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
