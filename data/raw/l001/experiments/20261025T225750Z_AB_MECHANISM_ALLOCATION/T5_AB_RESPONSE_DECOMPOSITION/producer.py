"""Read-only exact interval decomposition of accepted T4/T2R1 records.

This is fixed-operator linear source response, not independent nonlinear
causal attribution. No physical integration and no source-parent mutation.
"""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('decomposition_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT
I=c.I

def authenticate(cfg):
    c.need(sys.platform=='linux','LINUX_ONLY')
    g=c.read(ROOT/'ADMISSION.json'); c.need(g.get('admitted') is True,'ADMISSION')
    c.need(g.get('t4_terminal_review_accepted') is True,'T4_REVIEW_NOT_ACCEPTED')
    c.need(g.get('t2_terminal_review_accepted') is True,'T2_REVIEW_NOT_ACCEPTED')
    required=[cfg['t4']+'/output/RESULT.json',cfg['t4_review'],cfg['t2']+'/output/RESULT.json',cfg['t2_review']]
    for name in ('primary','independent'):
        required.extend(cfg['t4']+'/output/'+f for f in ('homogeneous_'+name+'.json','particular_lower_'+name+'.json','assembled_'+name+'.json'))
        required.append(cfg['t2']+'/output/strip_'+name+'.json')
    for rel in required: c.need(rel in g['sources'],'MISSING_INPUT_BINDING:'+rel)
    for rel,d in g['sources'].items(): c.need(c.sha(ROOT/rel)==d,'SOURCE_HASH:'+rel)
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for path,d in rt['files'].items(): c.need(c.sha(path)==d,'RUNTIME_HASH:'+path)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')

def controls():
    IH,IP,FH,FP,Ra,Rb=map(Q,('2/3','3/7','5/11','7/13','11/17','13/19'))
    Ba=(IP-FP*IH/FH)/Ra; Bb=-IH/(2*FH)
    # Independent direct forced combination, not the reduced B expression.
    direct=(-Rb/2-FP)*IH/FH+IP
    c.need(Ra*Ba+Rb*Bb==direct,'EXACT_RESPONSE_ASSEMBLY')
    geo=Q(5,23); scalar=Ra-geo; graph=Q(-7,29)
    c.need(-2*Ba*geo-2*Ba*scalar+graph==-2*Ba*Ra+graph,'EXACT_LOAD_SPLIT')
    c.need(-2*Ba*geo+2*Ba*scalar+graph!=-2*Ba*Ra+graph,'FORCE_SIGN_MUTATION')
    Zg,Zs,Zw=Q(11,3),Q(2,7),Q(5,13); Z=Zg+Zs+Zw
    c.need(Zg/Z==1-Zs/Z-Zw/Z,'EXACT_KINETIC_COMPLEMENT')
    E=Q(2,3); C=Q(-3,11)
    c.need((C/E**6)*E**6==C,'PROPER_DENSITY_NORMALIZATION')
    try: I(1)/I(-1,1)
    except RuntimeError as e: c.need(str(e)=='ZERO_DENOMINATOR','WRONG_REJECTION')
    else: raise RuntimeError('ZERO_DENOMINATOR_ACCEPTED')
    return {'exact_response_assembly':True,'exact_load_split':True,'force_sign_mutation_rejected':True,
            'kinetic_complement_identity':True,'proper_density_normalization':True,'zero_denominator_rejected':True}

def evaluate(name,cfg):
    t4=ROOT/cfg['t4']/'output'; t2=ROOT/cfg['t2']/'output'
    H=c.read(t4/('homogeneous_'+name+'.json')); P=c.read(t4/('particular_lower_'+name+'.json'))
    A=c.read(t4/('assembled_'+name+'.json')); S=c.read(t2/('strip_'+name+'.json'))
    c.need(H['all_cell_checks_pass'] and P['all_cell_checks_pass'] and S['all_cell_checks_pass'],'PARENT_TECHNICAL_GATES')
    FH=c.interval(H['upper']['F']); FP=c.interval(P['upper']['F'])
    IH=c.interval(H['Ipsi']); IP=c.interval(P['Ipsi'])
    Ra=c.interval(A['channels']['lower']['walls']['lower']['R'])
    c.need(not FH.zero() and not Ra.zero(),'RESPONSE_BASIS_DENOMINATOR_UNRESOLVED')
    Ba=(IP-FP*IH/FH)/Ra; Bb=-IH/(2*FH)
    channels={}
    for channel,B,sigma in [('lower',Ba,1),('upper',Bb,-1)]:
        parent=A['channels'][channel]; wall={k:c.interval(v) for k,v in parent['walls'][channel].items()}
        geo=(wall['Gamma']*wall['T']-2*sigma*wall['Tp'])*wall['xi']
        scalar=-wall['n']/1000; load=geo+scalar
        c.need(load.overlap(wall['R']) and (load-wall['R']).zero(),'LOAD_RECONSTRUCTION:'+channel)
        explicit=c.interval(parent['coefficient_graph'])
        expected_explicit=(-wall['xi']) if channel=='lower' else wall['xi']
        c.need(explicit.overlap(expected_explicit),'EXPLICIT_GRAPH_RECONSTRUCTION')
        bulkgeo=-2*B*geo; bulkscalar=-2*B*scalar; bulk=bulkgeo+bulkscalar; total=bulk+explicit
        expectedbulk=c.interval(parent['coefficient_bulk']); expectedtotal=c.interval(parent['coefficient_total'])
        c.need(bulk.overlap(expectedbulk) and (bulk-expectedbulk).zero(),'BULK_RECONSTRUCTION:'+channel)
        c.need(total.overlap(expectedtotal) and (total-expectedtotal).zero(),'TOTAL_RECONSTRUCTION:'+channel)
        E6=wall['E'].sq()*wall['E'].sq()*wall['E'].sq(); c.need(E6.lo>0,'POSITIVE_DENSITY_SCALE')
        values={'boundary_response_integral_per_unit_R':B,'graph_induced_boundary_load':geo,'direct_scalar_current_load':scalar,
                'bulk_from_graph_load':bulkgeo,'bulk_from_direct_scalar_current':bulkscalar,
                'explicit_interface_displacement':explicit,'reconstructed_bulk':bulk,'reconstructed_total':total,
                'parent_total':expectedtotal,'reconstruction_residual':total-expectedtotal,
                'proper_density_bulk_from_graph_load':bulkgeo/E6,
                'proper_density_bulk_from_direct_scalar_current':bulkscalar/E6,
                'proper_density_explicit_interface_displacement':explicit/E6,
                'proper_density_reconstructed_total':total/E6}
        channels[channel]={k:v.pack() for k,v in values.items()}
    ob={k:c.interval(v) for k,v in S['observables'].items()}
    raw=ob['metric_fraction']; complement=1-ob['scalar_fraction']-ob['oscillator_fraction']
    c.need(raw.overlap(complement) and (raw-complement).zero(),'METRIC_COMPLEMENT_CONSISTENCY')
    recomputed=1-ob['Zs']/ob['Zext']-ob['Zw']/ob['Zext']
    c.need(recomputed.overlap(complement),'KINETIC_FRACTION_BINDING')
    return {'engine':name,'channels':channels,'neutral_metric_fraction':{'raw_ratio':raw.pack(),
            'normalization_identity_complement':complement.pack(),'difference_contains_zero':True,
            'complement_width_less_than_raw':complement.hi-complement.lo<raw.hi-raw.lo}}

def main():
    c.need(not any((ROOT/n).exists() for n in ('RESULT.json','FAILURE.json','STARTED.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('DECOMPOSITION_CAP_900_SECONDS'))); signal.alarm(900)
        cfg=c.read(ROOT/'CONFIG.json'); authenticate(cfg)
        c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested=controls(); c.put('CONTROLS.json',tested)
        c.need(c.read(ROOT/cfg['t4']/'output/RESULT.json')['classification']=='FIRST_CURRENT_SEPARATION_COEFFICIENTS_ENCLOSED','T4_RESULT_SCOPE')
        c.need(c.read(ROOT/cfg['t2']/'output/RESULT.json')['classification'] in ('SELECTED_NEUTRAL_MODE_CHARACTERIZED','SELECTED_NEUTRAL_MODE_SEPARATION_INCONCLUSIVE'),'T2_RESULT_SCOPE')
        per={name:evaluate(name,cfg) for name in ('primary','independent')}; combined={}
        for channel in ('lower','upper'):
            combined[channel]={}
            for key in per['primary']['channels'][channel]:
                a=c.interval(per['primary']['channels'][channel][key]); b=c.interval(per['independent']['channels'][channel][key])
                c.need(a.overlap(b),'ENGINE_DECOMPOSITION_DISAGREEMENT:'+channel+':'+key)
                combined[channel][key]=a.hull(b).pack()
        metric={}
        for key in ('raw_ratio','normalization_identity_complement'):
            a=c.interval(per['primary']['neutral_metric_fraction'][key]); b=c.interval(per['independent']['neutral_metric_fraction'][key])
            c.need(a.overlap(b),'ENGINE_KINETIC_DISAGREEMENT:'+key); metric[key]=a.hull(b).pack()
        c.put('RESULT.json',{'classification':'FIXED_OPERATOR_FIRST_CURRENT_RESPONSE_DECOMPOSED','per_engine':per,'combined':combined,
               'neutral_metric_fraction':metric,'controls':tested,'seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'Linear source-response decomposition at fixed first-order operator; not independent nonlinear causal attribution. Neutral kinetic complement supplements rather than replaces raw ratio.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
