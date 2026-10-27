"""Read only frozen native and conformal data. Never call their publication entrypoints."""
from pathlib import Path
from fractions import Fraction
import bisect, importlib.util, json, math, signal, sys, time
import mpmath as mp
from flint import arb, fmpq
from identity_run import ROOT, BRANCH, NAMES, CONFIG, setup, guard, capacity, exact, poly
from records import read, atomic, sha, now, unpack
from series import bounds, interval, record


def decimal(x):return mp.nstr(x,mp.mp.dps)


def distance(a,b):
    a,b=mp.mpf(a),mp.mpf(b)
    if not mp.isfinite(a) or not mp.isfinite(b):raise ArithmeticError('Nonfinite replay value')
    value=abs(a-b)
    if not mp.isfinite(value):raise ArithmeticError('Nonfinite replay difference')
    return value


def horner(row,z):
    value=mp.mpf(0)
    for c in reversed(row):value=value*z+mp.mpf(c)
    return value


def native_fields(seed,dense,q,s):
    h=mp.mpf(seed['h']);i=max(0,min(len(seed['segments'])-1,int(mp.floor(s/h))))
    z=s-i*h;base=[horner(row,z) for row in seed['segments'][i]]
    A=horner(dense['segments'][i][0],z);eps=mp.mpf(dense['epsilon'])
    return [A,A+horner(q,s),base[2]+eps*base[6]+horner(dense['correction'],s),-2*eps*base[5]]


def load_admission():
    path=BRANCH/NAMES['admission']/'code'
    sys.path.insert(0,str(path))
    spec=importlib.util.spec_from_file_location('frozen_admission_producer',path/'producer.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def one_case(case,dps,module):
    mp.mp.dps=dps;started=time.monotonic();d=module.Dense('fine_c4',case)
    gauge=d.qualify_gauge();d.make_map()
    native=BRANCH/NAMES['native']/'results/fine_c4'
    seed=read(native/'SEED.json');dense=read(native/f'case_{case}.dense.json')
    target=Fraction(0) if case==0 else Fraction(1 if case==3 else -1,200000)
    eps_record=Fraction(dense['epsilon']);amplitude_delta=eps_record-target
    if not -Fraction(1,200000)<=eps_record<=Fraction(1,200000):
        raise ArithmeticError('Saved amplitude outside the shared certified domain')
    rows=[]
    for N in CONFIG['degrees']:
        name=f'fine_c4_case{case}_N{N}_p80'
        gp=BRANCH/NAMES['spatial']/'inputs'/(name+'.grid.json');grid=read(gp)
        audit=read(gp.with_name(name+'.audit.json'))
        if audit['grid_sha256']!=sha(gp):raise RuntimeError('Saved admission audit bound to another grid')
        if not audit['all_velocities_exactly_zero']:raise RuntimeError('Nonzero audited velocity')
        if any(mp.mpf(v)!=0 for row in grid['velocities'] for v in row):raise RuntimeError('Nonzero velocity')
        if any(mp.mpf(v)!=0 for v in grid['Cauchy_constants'].values()):raise RuntimeError('Cauchy constants changed')
        errors={'fields_at_saved_s':mp.mpf(0),'inverse_s':mp.mpf(0),'fields_at_reconstructed_s':mp.mpf(0),
                'gauge_coefficients':mp.mpf(0),'map_coefficients':mp.mpf(0),'map_knots':mp.mpf(0),'length':distance(d.X,grid['X'])}
        errors['gauge_coefficients']=max(distance(a,b) for a,b in zip(d.q,grid['gauge_coefficients']))
        errors['map_coefficients']=max(distance(a,b) for ra,rb in zip(d.xpoly,grid['coordinate_integral_polynomials']) for a,b in zip(ra,rb))
        errors['map_knots']=max(distance(a,b) for a,b in zip(d.xknots,grid['coordinate_knots']))
        jac_lower=None
        hh=exact(seed['h']);DD=exact(seed['D']);cells=len(seed['segments'])
        for cell,c in enumerate(grid['coordinate_integral_polynomials']):
            derivative=[arb(exact(value))*j for j,value in enumerate(c) if j>0]
            width=DD-cell*hh if cell==cells-1 else hh
            lower=bounds(poly(derivative,interval(fmpq(0),width)))[0]
            jac_lower=lower if jac_lower is None else min(jac_lower,lower)
        if jac_lower<=0:raise ArithmeticError('Represented map not certified monotone')
        for i in range(N+1):
            s=mp.mpf(grid['s'][i]);x=mp.mpf(grid['x'][i]);si=d.invert(x)
            errors['inverse_s']=max(errors['inverse_s'],distance(si,s))
            for coordinate,key in zip(native_fields(seed,dense,grid['gauge_coefficients'],s),['A','B','Phi','ell']):
                errors['fields_at_saved_s']=max(errors['fields_at_saved_s'],distance(coordinate,grid[key][i]))
            for coordinate,key in zip(native_fields(seed,dense,d.q,si),['A','B','Phi','ell']):
                errors['fields_at_reconstructed_s']=max(errors['fields_at_reconstructed_s'],distance(coordinate,grid[key][i]))
        clock=[]
        for i in (0,N):
            B=mp.mpf(grid['B'][i]);A=mp.mpf(grid['A'][i]);W=mp.mpf(grid['seed_fields'][i][0])
            clock.append({'initial_log_lapse':decimal(B),'initial_log_angular_warp':decimal(A),
                          'q_at_wall':decimal(B-A),'normalized_proper_clock_rate':decimal(mp.exp(B-W)),
                          'normal_orientation_sigma':1 if i==0 else -1})
        if not all(mp.isfinite(v) for v in errors.values()) or max(errors.values())>mp.mpf(CONFIG['representation_gate']):
            raise ArithmeticError('Frozen representation replay gate')
        if max(distance(c['q_at_wall'],0) for c in clock)>mp.mpf(CONFIG['representation_gate']):
            raise ArithmeticError('Wall clocks do not match initially')
        rows.append({'N':N,'grid_sha256':sha(gp),'audit_sha256':sha(gp.with_name(name+'.audit.json')),
            'errors':{k:decimal(v) for k,v in errors.items()},'positive_represented_map_derivative_lower':str(jac_lower),
            'clock_and_normals':clock,'initial_physical_momenta_exactly_zero':True,'passed':True})
    if not all(mp.isfinite(v) for side in gauge['final'] for row in side for v in row):
        raise ArithmeticError('Nonfinite gauge row')
    return {'case':case,'dps':dps,'seconds':time.monotonic()-started,'grids':rows,'passed':True,
        'epsilon_target':str(target),'epsilon_saved_exact_decimal':str(eps_record),'epsilon_rounding_offset':str(amplitude_delta),
        'saved_epsilon_in_certified_interval':-Fraction(1,200000)<=eps_record<=Fraction(1,200000),
        'gauge_final_rows':[[[decimal(v) for v in row] for row in side] for side in gauge['final']],
        'new_evolution_steps':0,'rigorous_lapse_error_bound':None,'rigorous_inverse_map_error_bound':None}


def correction_bounds():
    out=[];box=[Fraction(1,100000),Fraction(1,10),Fraction(1,10)]
    for name,case in [('positive',3),('negative',4)]:
        source=BRANCH/NAMES['finite']/f'output/{name}/RESULT.json'
        old=unpack(read(source));dense=read(BRANCH/NAMES['native']/f'results/fine_c4/case_{case}.dense.json')
        eps=Fraction(old['epsilon'])
        centers=[Fraction(dense['A0'])-eps]+[Fraction(v) for v in dense['fifth_jet_coefficients']]
        if centers!=[Fraction(v) for v in old['center']]:raise RuntimeError('Signed numerical center identity failed')
        absolute=[];errors=[]
        for center,offset,r in zip(centers,old['image_offset'],box):
            lo,hi=bounds(offset);cl=fmpq(center.numerator,center.denominator)
            if not -r<Fraction(str(cl+lo))<=Fraction(str(cl+hi))<r:
                raise ArithmeticError('Root enclosure not inside common uniqueness box')
            absolute.append([str(cl+lo),str(cl+hi)]);errors.append(str(max(abs(lo),abs(hi))))
        out.append({'case':case,'target_epsilon':str(eps),'source_sha256':sha(source),
            'coordinates':['A0-epsilon','b0','b1'],'center_exact':[str(v) for v in centers],
            'root_enclosure_exact':absolute,'distance_from_saved_center_upper_exact':errors,
            'distance_from_saved_center_upper_decimal':[float(Fraction(v)) for v in errors],
            'within_common_uniqueness_box':True,
            'interpretation':'Certified root at exact target versus numerical coefficient center; not literal equality.'})
    return out


def main():
    setup();g,b=guard();capacity()
    if (ROOT/'NUMERICAL_READBACK.json').exists():raise RuntimeError('Readback already terminal')
    if not read(ROOT/'SPATIAL_ENCLOSURES.json')['passed']:raise RuntimeError('Spatial prerequisite failed')
    verification=read(BRANCH/NAMES['admission']/'VERIFICATION.json')
    spatial=read(BRANCH/NAMES['spatial']/'VERIFICATION.json')
    if not verification['all_passed'] or not spatial['record_integrity_valid'] or not spatial['complete_signed_cohort_qualified']:
        raise RuntimeError('Inherited numerical admission not accepted')
    def alarm(*args):raise TimeoutError('Frozen readback wall budget')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(CONFIG['readback_seconds'])
    started=time.monotonic();module=load_admission();cases=[]
    for case in CONFIG['cases']:
        for dps in CONFIG['replay_dps']:
            p=ROOT/'readback'/f'case{case}-p{dps}.json'
            if p.exists():
                result=read(p)
                if result['guard']!=g or not result['passed']:raise RuntimeError('Stale readback checkpoint')
            else:
                result=one_case(case,dps,module)|{'guard':g,'utc':now()};atomic(p,result,True)
            cases.append(result)
            print(json.dumps({'case':case,'dps':dps,'passed':True,'seconds':result['seconds']}),flush=True)
    signal.alarm(0)
    atomic(ROOT/'NUMERICAL_READBACK.json',{'guard':g,'passed':True,'cases':cases,'root_bounds':correction_bounds(),
        'elapsed_seconds_this_invocation':time.monotonic()-started,'utc':now(),
        'reused_gauge_and_map_kernel_disclosed':True,'independent_saved_field_polynomial_evaluation':True,
        'continuum_evolution_error_certified':False,'new_evolution_steps':0},True)


if __name__=='__main__':main()
