"""Read-only certificate audit; never imports or executes physical ODE kernels.

Uses independent exact-rational matrix arithmetic and native Arb roundtrips.
The authenticated pure-rational majorant checker is replayed, not a trajectory.
Only stdout is written; the caller saves it in the designated reviewer staging.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import itertools
import json
import math
import os
import platform
import sys
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path

import flint
from flint import arb, ctx

GUARD = '233defdff9efcaef4e2c0b427af22776b85c94c233894a7da16e3a9936cf2cdc'
CLASSIFICATION = 'LOCAL_C4_D1_NATIVE_FAMILY_CERTIFIED_WITH_EXPLICIT_CONSERVATIVE_RADIUS'
EXPECTED_SOURCE = {
    'CONTRACT.md':'cfe0bb5ce244eaf0e88291a951a42961f13ee6eb8bf1be2a3f0cb7a316942f6e',
    'ANALYTIC_RADIUS.md':'17f31b2e9fd0bc703bd3860d224e83013062c05f14c341ca02687764418c42bb',
    'series.py':'d2c52ced97bbc78398420f22e40d24b3ee2cf88668a2d00ae0de6f46fdd07603',
    'primary.py':'57235737768737b5d159f20b60a67174f5099ec3c2513d0bce66b934fbd62973',
    'flux.py':'aacbcf5d9c98d4286f78ae9cb206636dd4358297d14c91d44addd2b8e3b4f00f',
    'validated.py':'0a48f058b282197b9b4e6d5a99e36af578bcb9e6d036d9848d5513adc009c7d3',
    'jetmap.py':'3135091e7dd35cbda4cfad77261553aaf11e18bf7f011ba8336ebd0f10014f2d',
    'majorants.py':'e3a97644a5296324bb1e166433a22c3e016f4ebf98aab26261039a9e262e57d5',
    'records.py':'081e7b0b95b416e987bd873179e41152421ad73529163a33982ac8f8e6c2647e',
    'runner.py':'86e875df859f402e59f111c1728792f1230ef0f8171b5d30f3119931fdb01875',
}
EXPECTED_CONFIG = {
    'bits':768,'threads':1,'primary_denominator':8192,'flux_denominator':16384,
    'checkpoint_cells':256,'engine_seconds_cap':900,'address_space_bytes':4*1024**3,
    'task_order':['primary','flux'],
    'root':['456607025194779413/4611686018427387904','114151756532473697/1152921504606846976'],
    'D':['32727/16384','32729/16384'],'mu':['-33/25000','-131/100000'],
    'r0_power_of_two':-4096,'amplitude_radius_power_of_two':-9216,
    'inverse_norm_max_power_of_two':64,
    'scope':'EXACT_CENTRAL_D1_FINAL_THREE_VARIABLE_C4_PREPARATION',
}
SEEN = {}
HASH_LINKS = 0
NATIVE_COUNT = 0


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def track(path, expected=None):
    global HASH_LINKS
    path=Path(path).resolve(); value=sha(path)
    if expected is not None:
        require(value==expected,'Hash mismatch: '+str(path))
        HASH_LINKS+=1
    if str(path) in SEEN:
        require(SEEN[str(path)]==value,'Input changed during audit: '+str(path))
    SEEN[str(path)]=value
    return value


def read(path):
    track(path)
    return json.loads(Path(path).read_text())


def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


class I:
    def __init__(self, lo=0, hi=None):
        self.lo=Q(lo);self.hi=Q(lo if hi is None else hi)
        require(self.lo<=self.hi,'Reversed rational interval')
    def __add__(self, other):
        other=iv(other);return I(self.lo+other.lo,self.hi+other.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self, other):return self+-iv(other)
    def __rsub__(self, other):return iv(other)+-self
    def __mul__(self, other):
        other=iv(other);v=[a*b for a in (self.lo,self.hi) for b in (other.lo,other.hi)]
        return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self, other):
        other=iv(other);require(other.hi<0 or other.lo>0,'Interval division by zero')
        return self*I(1/other.hi,1/other.lo)
    def contains(self, other):
        other=iv(other);return self.lo<=other.lo and other.hi<=self.hi
    def overlaps(self, other):
        other=iv(other);return max(self.lo,other.lo)<=min(self.hi,other.hi)
    def absmax(self):return max(abs(self.lo),abs(self.hi))
    def exact(self):return [str(self.lo),str(self.hi)]
    def decimal(self):return [float(self.lo),float(self.hi)]


def iv(x):return x if isinstance(x,I) else I(x)
def rec(x):return I(*x['exact'])


def determinant(matrix):
    # Independent Leibniz expansion rather than producer's hand-coded formula.
    n=len(matrix);out=I(0)
    for p in itertools.permutations(range(n)):
        inversions=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        term=I((-1)**inversions)
        for row,col in enumerate(p):term*=matrix[row][col]
        out+=term
    return out


def native_interval(obj):
    m,r=obj['_arb_native']
    return I(Q(m[0])*Q(2)**m[1]-Q(r[0])*Q(2)**r[1],
             Q(m[0])*Q(2)**m[1]+Q(r[0])*Q(2)**r[1])


def check_native(obj):
    global NATIVE_COUNT
    if isinstance(obj,dict):
        if '_arb_native' in obj:
            require(set(obj)=={'_arb_native'},'Malformed native encoding')
            m,r=obj['_arb_native'];z=arb(tuple(m),tuple(r))
            require(z.is_finite(),'Nonfinite native ball')
            require([[int(v) for v in z.mid().man_exp()],
                     [int(v) for v in z.rad().man_exp()]]==[m,r],
                    'Native midpoint/radius roundtrip failed')
            require(r[0]>=0,'Negative native radius')
            NATIVE_COUNT+=1
        else:
            for value in obj.values():check_native(value)
    elif isinstance(obj,list):
        for value in obj:check_native(value)


def check_manifest(directory, expected_hash, expected_count):
    path=directory/'MANIFEST.json';track(path,expected_hash);manifest=read(path)
    entries=manifest.get('entries')
    if entries is None:
        entries=[{'path':n,**v} for n,v in manifest['files'].items()]
    require(len(entries)==expected_count,'Parent manifest count mismatch')
    for entry in entries:
        target=(directory/entry['path']).resolve()
        require(target.is_relative_to(directory.resolve()),'Manifest path escapes packet')
        track(target,entry['sha256'])
        if 'bytes' in entry:require(target.stat().st_size==entry['bytes'],'Manifest size mismatch')
    return len(entries)


def task_check(task, old):
    name=task['engine'];step=Q(2,EXPECTED_CONFIG[name+'_denominator'])
    dlo,dhi=map(Q,EXPECTED_CONFIG['D']);cells=math.ceil(dhi/step)
    expected_cover=[]
    for j in range(cells):
        lo=max(j*step,dlo);hi=min((j+1)*step,dhi)
        if lo<=hi:
            expected_cover.append({'cell':j,'lo_exact':str(lo),'hi_exact':str(hi)})
    require(task['cells']==cells and task['event_cover']==expected_cover,'Incorrect full event coverage')
    require(1<=task['max_picard_iterations']<=32,'Picard cap violation')
    require(task['elapsed_seconds']<=900,'Engine runtime cap violation')
    J=[[rec(x) for x in row] for row in task['J']]
    inv=[[rec(x) for x in row] for row in task['inverse']]
    d=rec(task['analytic_determinant']);det=rec(task['determinant'])
    require(J[0][0].exact()==d.exact(),'Analytic derivative not matrix first entry')
    require([x.exact() for x in J[1]]==[['0','0'],['1','1'],['0','0']], 'Lower row mismatch')
    require(det.hi<0 and d.hi<0 and det.overlaps(d),'Nonsingularity failed')
    exact_det=determinant(J)
    require(det.contains(exact_det),'Reported determinant fails independent rational enclosure')
    for i in range(3):
        for j in range(3):
            minor=[[J[r][c] for c in range(3) if c!=i] for r in range(3) if r!=j]
            expected=((-1)**(i+j))*determinant(minor)/det
            require(inv[i][j].contains(expected),'Inverse cofactor enclosure failed')
    norm=max(sum(x.absmax() for x in row) for row in inv)
    require(norm==Q(task['inverse_norm_upper_exact']),'Inverse norm mismatch')
    require(norm<=2**64,'Inverse norm gate failed')
    require(d.overlaps(rec(old['v_at_full_event'])),'Inherited derivative disjoint')
    beta=rec(task['beta'])
    for j in range(3):
        require(J[2][j].overlaps(beta*J[0][j]+int(j==2)), 'Reduced row structure disjoint')
        require(J[2][j].overlaps(rec(task['direct_fourth_rows'][j])), 'Original-PDE fourth row disjoint')
    ext={n:rec(v) for n,v in task['extrema'].items()}
    require(ext['W'].absmax()<=3,'W majorant premise')
    require(all(ext[n].absmax()<=2 for n in ('H','Phi','T')),'Physical-field majorant premise')
    require(ext['exp_minus_2W'].lo>0 and ext['exp_minus_2W'].hi<=256,'Exponential majorant premise')
    require(ext['q'].lo>0 and ext['q'].hi<=1,'Curvature-source majorant premise')
    require(ext['first_integral'].contains(0),'First-integral enclosure excludes zero')
    k=rec(task['k']);B=rec(task['B_lower'])
    require(k.lo>0 and k.hi<=Q(1,1000),'Curvature majorant premise')
    require(B.hi<=-Q(1,20) or B.lo>=Q(1,20),'Lower launch denominator premise')
    for key in ('endpoint_identities','full_event_cover_pass','qualitative_gates_pass',
                'radius_background_premises_pass','radius_inverse_gate_pass'):
        require(task[key] is True,'Producer gate not passed: '+key)
    require(all(task['model_majorant_premises'].values()),'Producer model gate not passed')
    return {'engine':name,'cells':cells,'event_cover':expected_cover,
            'determinant_exact':det.exact(),'determinant_decimal':det.decimal(),
            'analytic_derivative_exact':d.exact(),'analytic_derivative_decimal':d.decimal(),
            'inverse_norm_upper_exact':str(norm),'inverse_norm_upper_decimal':float(norm),
            'independent_rational_determinant_and_inverse_pass':True,
            'original_pde_recorded_rows_overlap':True,'complete_event_coverage':True,
            'radius_background_premises_pass':True,'max_picard_iterations':task['max_picard_iterations'],
            'extrema_decimal':{n:x.decimal() for n,x in ext.items()},
            'beta_decimal':beta.decimal(),'k_decimal':k.decimal(),'B_lower_decimal':B.decimal()}


def audit(root):
    ctx.prec=768;ctx.threads=1;out=root/'output'
    track(root/'BINDINGS.json',GUARD);b=read(root/'BINDINGS.json')
    require(b['config']==EXPECTED_CONFIG and b['source']==EXPECTED_SOURCE,'Unreviewed config/source')
    require(read(root/'FREEZE_RECORD.json')['binding_sha256']==GUARD,'Freeze guard mismatch')
    for name,digest in {**b['source'],**b['reviews']}.items():track(root/name,digest)
    for entry in b['inputs'].values():track(root/entry['path'],entry['sha256'])
    parent=(root/b['inputs']['BINDINGS.json']['path']).parent.resolve()
    central=(root/b['inputs']['central_manifest']['path']).parent.resolve()
    failed=(root/b['inputs']['technical_predecessor_BINDINGS.json']['path']).parent.resolve()
    parents={
        parent.name:check_manifest(parent,b['inputs']['MANIFEST.json']['sha256'],159),
        central.name:check_manifest(central,b['inputs']['central_manifest']['sha256'],326),
        failed.name:check_manifest(failed,'f2ccdc412489ff2f59c671dcb2ff0da6ebeddd8af08557b1942370eca6ac4ca2',39),
    }
    oldb=read(parent/'BINDINGS.json');mode=read(central/'RESULT.json')
    require(oldb['a_enclosure']==EXPECTED_CONFIG['root'] and oldb['D_enclosure']==EXPECTED_CONFIG['D']
            and oldb['mu_enclosure']==EXPECTED_CONFIG['mu'],'Original exact domains changed')
    require(oldb['model_exact']==b['model_exact']==read(central/'BINDINGS.json')['model_exact'],'Action changed')
    require(mode['status']=='COMPLETE' and mode['independently_accepted'] is True
            and mode['classification']=='NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1'
            and mode['mu_open_interval']==EXPECTED_CONFIG['mu'],'Physical mode authority missing')
    oldfailure=read(failed/'output/FAILURE.json')
    require(oldfailure['guard']==b['inputs']['technical_predecessor_BINDINGS.json']['sha256']
            and oldfailure['status']=='TECHNICAL_INCOMPLETE','Original failure provenance mismatch')
    model={n:Q(v) for n,v in b['model_exact'].items()}
    require(model['gamma']==20 and abs(model['m2'])<=1 and
            all(abs(model[n])<=1 for n in ('v0','v1')) and
            all(abs(model[n])<=8 for n in ('lambda_a','lambda_b')),'Exact model bounds fail')
    require(all(abs(Q(x))<=Q(1,500) for x in EXPECTED_CONFIG['mu']),'Mass bound fails')
    runtime=b['runtime'];require(runtime['precision']==768 and runtime['threads']==1,'Arithmetic controls')
    require(platform.python_version()==runtime['python'] and flint.__version__==runtime['flint'],'Runtime version changed')
    require(Path(sys.executable).resolve()==Path(runtime['executable']).resolve(),'Python executable changed')
    require({k:os.environ.get(k) for k in runtime['env']}==runtime['env'],'Runtime environment changed')
    track(runtime['executable'],runtime['executable_sha256'])
    for path,digest in runtime['libraries'].items():track(path,digest)
    preflight=read(root/b['inputs']['preflight']['path'])
    require(preflight['pass'] and len(preflight['checks'])==15 and all(preflight['checks'].values()),'Preflight failure')
    require(preflight['source']==b['source'] and preflight['runtime']==runtime,'Preflight binding mismatch')
    require(preflight['physical_model_evaluated'] is False and preflight['polynomial_fixture_iterations']==[3]*8,'Analytic control scope')
    algebra=read(root/'INDEPENDENT_BOUNDARY_ALGEBRA.json')
    require(algebra['status']=='PASS' and all(algebra['checks'].values()) and
            algebra['source_sha256']==b['reviews']['independent_boundary_algebra.py'],'Exact algebra authentication')
    require(not (out/'FAILURE.json').exists(),'R1 has failure receipt')
    result=read(out/'RESULT.json');terminal=read(out/'TERMINAL.json')
    require(terminal['status']==result['status']=='COMPLETE' and terminal['guard']==result['guard']==GUARD,'Terminal status/guard')
    track(out/'RESULT.json',terminal['result_sha256'])
    require(result['config']==b['config'],'Result controls changed')
    tasks=[]
    for name in EXPECTED_CONFIG['task_order']:
        task=read(out/(name+'.json'));digest=task['digest']
        require(task['engine']==name and task['status']=='COMPLETE' and task['guard']==GUARD,'Task identity')
        require(digest==fingerprint({k:v for k,v in task.items() if k!='digest'}),'Task digest')
        tasks.append(task)
    require(result['tasks']==tasks,'Final task aggregation differs from publications')
    oldreg=read(parent/'results/REGULARITY_CERTIFICATE.json')
    require(oldreg['passed'] is True and oldreg['same_exact_background'] is True,'Old regularity certificate')
    task_results=[task_check(task,old) for task,old in zip(tasks,oldreg['results'])]
    for i in range(3):
        for j in range(3):require(rec(tasks[0]['J'][i][j]).overlaps(rec(tasks[1]['J'][i][j])),'Matrix implementations disjoint')
    # Read-only verification of every checkpoint; no numerical step is replayed.
    checkpoints=sorted((out/'checkpoints').glob('*.json'));states={}
    expected={(0,n) for n in range(256,8184,256)}|{(1,0)}|{(1,n) for n in range(256,16366,256)}|{(2,0)}
    for path in checkpoints:
        body=read(path);digest=fingerprint(body);state=body['state']
        key=(state['task_index'],state['cell_index'])
        require(body['guard']==GUARD and path.stem==f'{key[0]:02d}-{key[1]:06d}-{digest}','Checkpoint guard/name/digest')
        require(key in expected and key not in states,'Unexpected/duplicate checkpoint')
        require(len(state['results'])==key[0] and state['results']==tasks[:key[0]],'Checkpoint accepted-task history')
        check_native(body);states[key]=state
        p=state['p']
        for name,value in model.items():require(native_interval(p[name]).contains(value),'Checkpoint action drift')
        require(native_interval(p['D']).contains(I(*EXPECTED_CONFIG['D'])),'Checkpoint wall-domain exclusion')
        for name,record_name in [('k','k'),('B_lower','B_lower')]:
            require(rec(tasks[0][record_name]).contains(native_interval(p[name])),'Checkpoint fixed-parameter drift')
        require(native_interval(state['extrema']['first_integral']).contains(0),'Checkpoint constraint exclusion')
        require(state['max_picard']<=32 and state['task_elapsed']<=900,'Checkpoint limits')
    require(set(states)==expected and len(checkpoints)==96,'Incomplete checkpoint sequence')
    postpublication_widenings=0
    for index,task in [(1,tasks[0]),(2,tasks[1])]:
        state=states[(index,0)]
        require(state['y']==task['final_native_state'],'Committed final native state differs')
        require(state['event_cover']==task['event_cover'] and state['endpoint_identities'] is True,'Final checkpoint endpoint history')
        for i in range(3):
            for j in range(3):
                published=rec(task['J'][i][j]);saved=native_interval(state['J'][i][j])
                if not published.contains(saved):
                    # The task result is published BEFORE save() canonicalizes
                    # the live checkpoint. Its constructor-stable native radius
                    # can widen outward by a mantissa quantum (at most the three
                    # constructor attempts declared in the reviewed serializer).
                    radius_pair=state['J'][i][j]['_arb_native'][1]
                    quantum=Q(2)**radius_pair[1]
                    require(saved.contains(published) and radius_pair[0]>0,
                            'Final checkpoint is not an outward publication enclosure')
                    require(max(published.lo-saved.lo,saved.hi-published.hi)<=3*quantum,
                            'Checkpoint widening exceeds declared native canonicalization')
                    postpublication_widenings+=1
    latest=read(out/'LATEST.json');require(latest['guard']==GUARD,'Latest guard')
    body=read(out/latest['path']);require(fingerprint(body)==latest['digest'] and body['state']==states[(2,0)],'Latest digest/state')
    # Pure rational proof replay, with source already independently reviewed and hash-bound.
    spec=importlib.util.spec_from_file_location('authenticated_rational_majorants',root/'majorants.py')
    major_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(major_module)
    major=major_module.certify()
    require(major==result['majorants']==preflight['majorants'],'Exact rational majorant receipt mismatch')
    r0=Q(2)**-4096;delta=Q(2)**-9216
    contraction=128*2**64*2**512*delta/(r0*r0)
    selfmap=32*2**64*2**512*delta/(r0*r0)
    require(contraction==Q(2)**-441==Q(major['contraction_exact']) and
            selfmap==Q(2)**-443==Q(major['selfmap_ratio_exact']),'Cauchy arithmetic mismatch')
    require(delta/r0<Q(1,8) and contraction<Q(1,2) and selfmap<Q(1,2),'Contraction fails')
    require(major['pass'] is True and major['physical_outcomes_evaluated'] is False,'Majorant status')
    require(not any(name in sys.modules for name in ('primary','flux','validated','runner','jetmap')),'Physical code imported')
    qualitative=True;radius=True
    require(result['qualitative_certificate']==qualitative and result['quantitative_radius_certificate']==radius,'Producer classification discrepancy')
    require(result['classification']==terminal['classification']==CLASSIFICATION,'Classification mismatch')
    require(result['sample_amplitudes_included'] is False and result['evolution_launched'] is False
            and result['successor_launched'] is False,'Scope flags changed')
    with (out/'RUN.lock').open('rb') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        fcntl.flock(lock,fcntl.LOCK_UN)
    unchanged=all(sha(path)==digest for path,digest in SEEN.items())
    require(unchanged,'Inputs changed during audit')
    return {'status':'PASS','qualitative_accepted':qualitative,'radius_accepted':radius,
        'independently_recomputed_classification':CLASSIFICATION,'guard':GUARD,
        'result_sha256':terminal['result_sha256'],'checkpoint_count':len(checkpoints),
        'postpublication_native_radius_widenings_checked':postpublication_widenings,
        'native_roundtrip_count':NATIVE_COUNT,'hash_links_checked':HASH_LINKS,
        'unique_files_authenticated_and_unchanged':len(SEEN),'inputs_unchanged':unchanged,
        'parent_manifest_counts':parents,'runtime_library_count':len(runtime['libraries']),
        'preflight_controls_passed':15,'total_validated_cells':sum(x['cells'] for x in task_results),
        'tasks':task_results,'matrix_implementations_overlap':True,
        'exact_rational_majorants_replayed':True,'amplitude_radius':'2^-9216',
        'complex_polydisc_radius':'2^-4096','contraction_bound':'2^-441','selfmap_ratio_bound':'2^-443',
        'producer_lock_released':True,'physical_kernel_imported_or_run':False,
        'claim_scope':'Exact central final three-variable C4 constraint family; no finite-sample inclusion or evolution theorem.',
        'audit_method_limit':'Cell inclusion is supported by authenticated reviewed source and checkpoint execution history, not a new physical replay. R2/I4 reductions are exact symbolic identities; saved direct R4 enclosures are compared numerically.',
        'auditor_source_sha256':sha(Path(__file__).resolve()),'checked_utc':datetime.now(timezone.utc).isoformat()}


def main():
    p=argparse.ArgumentParser();p.add_argument('packet',type=Path);args=p.parse_args()
    try:
        receipt=audit(args.packet.resolve())
    except Exception as error:
        print(json.dumps({'status':'FAIL','error':repr(error),'physical_kernel_imported_or_run':False},indent=2))
        raise
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
