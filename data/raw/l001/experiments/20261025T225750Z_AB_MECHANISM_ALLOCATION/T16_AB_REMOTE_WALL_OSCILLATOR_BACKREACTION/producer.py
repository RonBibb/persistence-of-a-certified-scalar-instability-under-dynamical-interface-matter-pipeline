"""Remote-wall oscillator stress and triangular quadratic graph response."""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('remote_wall_common',ROOT/'common.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c); c.ROOT=ROOT
PARENT=ROOT/'..'/'T10_AB_CURRENT_RADAR_RESPONSE'

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY')
    gate=c.read(ROOT/'ADMISSION.json')
    c.need(gate.get('admitted') is True and gate.get('t10_terminal_review_accepted') is True,'ADMISSION')
    for rel,digest in gate['sources'].items(): c.need(c.sha(ROOT/rel)==digest,'SOURCE_HASH:'+rel)
    for name in ('TERMINAL_REVIEW.md','basis.py','output/RESULT.json','output/current_radar_primary.json','output/current_radar_independent.json'):
        c.need('../T10_AB_CURRENT_RADAR_RESPONSE/'+name in gate['sources'],'MISSING_PARENT:'+name)
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for path,digest in rt['files'].items(): c.need(c.sha(path)==digest,'RUNTIME_HASH:'+path)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')
    c.need(c.read(PARENT/'output/RESULT.json')['classification']=='FIRST_CURRENT_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','PARENT_SCOPE')

def controls():
    h, E, chi=Q(2,7),Q(5,3),Q(-7,11)
    R=-6*h; r2=2*R
    stress=E*E*R*R*chi*chi/2
    mutations=[]
    for sigma in (Q(1),Q(-1)):
        divisor=sigma*E*E*r2*(r2-h)
        direct=stress/divisor
        simple=3*chi*chi/(26*sigma)
        c.need(direct==simple,'GRAPH_DIVISOR_SIMPLIFICATION')
        c.need(divisor*simple-stress==0,'REMOTE_ISRAEL_ROW')
        for name,bad in (('opposite_orientation',-simple),('missing_half_factor',2*simple),('omitted_oscillator_stress',Q(0))):
            c.need(divisor*bad-stress!=0,'MUTATION_NOT_DETECTED:'+name)
            mutations.append(name+':'+str(sigma))
    c.need(E*E*R*R*Q(0)**2/2==0,'ZERO_OSCILLATOR_CONTROL')
    a6=Q(7,5); N2=Q(3,2)
    c.need((a6*N2)**2==a6*a6*N2*N2,'QUADRATIC_DENSITY_NORMALIZATION')
    return {'exact_remote_divisor_identity':True,'two_orientations':True,'zero_oscillator':True,
            'quadratic_density_scaling':True,'detected_mutations':mutations,
            'scope':'Rational algebra controls; independent analytical review supplies the remote order-counting premise.'}

def evaluate(engine):
    record=c.read(PARENT/'output'/('current_radar_'+engine+'.json'))
    assembly=record['full_forced_assembly']; k=c.interval(assembly['k'])
    c.need(k.lo>0,'POSITIVE_CURVATURE')
    out={}
    for source,remote,sigma in (('lower','upper',Q(-1)),('upper','lower',Q(1))):
        ch=assembly['channels'][source]; wall={key:c.interval(value) for key,value in ch['walls'][remote].items()}
        own_density=c.interval(ch['walls'][source]['n'])
        own_E=c.interval(ch['walls'][source]['E'])
        c.need(own_E.lo>0,'SOURCE_WARP_POSITIVE')
        # n in the accepted assembly means Ni_squared*E^6, not Ni_squared.
        # Exact unit/zero channel choice is the authenticated basis.py
        # construction; this interval check is consistency, not its proof.
        unit_consistency=own_density/(own_E.sq()*own_E.sq()*own_E.sq())
        c.need(unit_consistency.lo<=1<=unit_consistency.hi,'SOURCE_UNIT_CURRENT_CONSISTENCY')
        c.need(wall['n'].lo==wall['n'].hi==0,'REMOTE_CURRENT_EXACT_ZERO')
        c.need(wall['xi'].lo==wall['xi'].hi==0,'REMOTE_FIRST_GRAPH_EXACT_ZERO')
        E=wall['E']; d=wall['d']; chi=wall['chi']
        c.need(E.lo>0 and d.lo>0,'WALL_DOMAIN')
        reconstructed=wall['f']/d
        c.need(chi.overlap(reconstructed),'REMOTE_OSCILLATOR_RECONSTRUCTION')
        density_scale=c.interval(ch['source_wall_a6'])
        c.need(density_scale.lo>0,'SOURCE_DENSITY_SCALE')
        scale2=density_scale.sq()
        stress=18*k*E.sq()*chi.sq()
        graph=Q(3,26)/sigma*chi.sq()
        divisor=156*sigma*k*E.sq()
        c.need((divisor*graph-stress).zero(),'ISRAEL_CONSISTENCY')
        out[source+'_to_'+remote]={
            'remote_sigma':str(sigma),'remote_current_zero':True,'remote_first_graph_zero':True,
            'source_unit_current_consistency':unit_consistency.pack(),
            'chi_first':chi.pack(),'chi_reconstruction_consistency_only':reconstructed.pack(),
            'oscillator_half_rho_plus_p_coefficient':stress.pack(),
            'oscillator_rho_plus_p_coefficient':(2*stress).pack(),
            'eulerian_graph_second_coefficient':graph.pack(),
            'half_rho_plus_p_per_source_proper_density_squared':(scale2*stress).pack(),
            'graph_second_per_source_proper_density_squared':(scale2*graph).pack(),
            'classification':'REMOTE_OSCILLATOR_STRESS_AND_GRAPH_RESPONSE_CERTIFIED' if stress.lo>0 and not graph.zero() else 'UNRESOLVED'}
    return out

def main():
    c.need(not any((ROOT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('REMOTE_WALL_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested=controls(); c.put('CONTROLS.json',tested)
        per={engine:evaluate(engine) for engine in ('primary','independent')}; combined={}
        keys=('chi_first','oscillator_half_rho_plus_p_coefficient','oscillator_rho_plus_p_coefficient',
              'eulerian_graph_second_coefficient','half_rho_plus_p_per_source_proper_density_squared','graph_second_per_source_proper_density_squared')
        for direction in ('lower_to_upper','upper_to_lower'):
            vals={}
            for key in keys:
                a,b=[c.interval(per[e][direction][key]) for e in ('primary','independent')]
                c.need(a.overlap(b),'ENGINE_DISAGREEMENT:'+direction+':'+key); vals[key]=a.hull(b).pack()
            stress=c.interval(vals['oscillator_half_rho_plus_p_coefficient']); graph=c.interval(vals['eulerian_graph_second_coefficient'])
            vals['classification']='REMOTE_OSCILLATOR_STRESS_AND_GRAPH_RESPONSE_CERTIFIED' if stress.lo>0 and not graph.zero() else 'UNRESOLVED'
            combined[direction]=vals
        label='REMOTE_OSCILLATOR_STRESS_AND_GRAPH_RESPONSE_CERTIFIED' if all(v['classification']=='REMOTE_OSCILLATOR_STRESS_AND_GRAPH_RESPONSE_CERTIFIED' for v in combined.values()) else 'UNRESOLVED'
        c.put('RESULT.json',{'classification':label,'combined':combined,'per_engine':per,'controls':tested,
             'time_dependence':'Coefficients multiply z squared, hence exp(-12 h t) for the selected analytic current branch.',
             'scope':'Invariant local oscillator anisotropic-stress contribution and chart-labelled triangular remote graph coefficient. Not complete second-order separation, full n2 existence, source switching, causal propagation time, or neutral-mode excitation.',
             'seconds':time.monotonic()-begun,'utc':c.now()})
    except BaseException as exc:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc(),'utc':c.now()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
