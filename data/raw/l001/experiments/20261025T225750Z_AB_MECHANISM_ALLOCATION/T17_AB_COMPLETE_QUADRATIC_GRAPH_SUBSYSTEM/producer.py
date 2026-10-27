"""Complete triangular quadratic graph subsystem; not full second-order geometry."""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); return v
c=module('graph_common',ROOT/'common.py'); c.ROOT=ROOT; I=c.I
T10=ROOT/'../T10_AB_CURRENT_RADAR_RESPONSE'; T15=ROOT/'../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION'
T16=ROOT/'../T16_AB_REMOTE_WALL_OSCILLATOR_BACKREACTION'

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY'); gate=c.read(ROOT/'ADMISSION.json'); c.need(gate.get('admitted') is True,'ADMISSION')
    for key in ('t10','t15','t16'): c.need(gate.get(key+'_terminal_review_accepted') is True,'ACCEPTED_PARENT_REQUIRED:'+key)
    required=['../T10_AB_CURRENT_RADAR_RESPONSE/TERMINAL_REVIEW.md','../T10_AB_CURRENT_RADAR_RESPONSE/output/RESULT.json',
              '../T10_AB_CURRENT_RADAR_RESPONSE/basis.py','../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py',
              '../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/TERMINAL_REVIEW.md','../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/RESULT.json',
              '../T16_AB_REMOTE_WALL_OSCILLATOR_BACKREACTION/TERMINAL_REVIEW.md','../T16_AB_REMOTE_WALL_OSCILLATOR_BACKREACTION/RESULT.json']
    required+=['../T10_AB_CURRENT_RADAR_RESPONSE/output/current_radar_'+n+'.json' for n in ('primary','independent')]
    for rel in required: c.need(rel in gate['sources'],'MISSING_PARENT_BINDING:'+rel)
    for rel,d in gate['sources'].items(): c.need(c.sha(ROOT/rel)==d,'SOURCE_HASH:'+rel)
    c.need(c.sha(ROOT/'polynomial_helper.py')==c.sha(T15/'producer.py'),'ACCEPTED_POLYNOMIAL_HELPER_COPY')
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for path,d in rt['files'].items(): c.need(c.sha(path)==d,'RUNTIME_HASH:'+path)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')
    c.need(c.read(T10/'output/RESULT.json')['classification']=='FIRST_CURRENT_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','T10_SCOPE')
    c.need(c.read(T15/'RESULT.json')['classification']=='EULERIAN_QUADRATIC_BULK_SOURCES_QUALIFIED','T15_SCOPE')

def qualify_s7():
    a=module('accepted_sparse_helper',ROOT/'polynomial_helper.py')
    # Reuse accepted bounded ring/series classes, not its physical background.
    a.NAMES=('E','h','xi','p','H','T','f','chi','n','Z'); a.N=len(a.NAMES); a.ZERO=(0,)*a.N
    E,h,xi,p,H,T,f,chi,n,Z=[a.variable(j) for j in range(a.N)]
    a.R=-6*h; R=a.R; P=a.P; S=a.S
    A=H*xi+p; deltaPhi=T*xi+f
    v=S((0,E*R*xi,E*R*xi*(-3*p-H*xi)))
    # Z is an arbitrary second-order inverse-lapse coefficient. Its presence
    # demonstrates independence of unknown order-two lapse data in qI2.
    invN=S((E,-E*A,Z)); invsqrt=1+v*v/2; invone=1+v*v
    rho=S((0,n,0))*S((1,-deltaPhi/1000,0))*(-6*S((0,A,0))).expzero()
    chid=S((0,chi,0)).dtime(); oscillator=chid*chid*invN*invN*invone/2
    result={}
    for sigma in (1,-1):
        geometric=sigma*invN*invsqrt*(v.dtime()*invone+v*S((-h,-3*R*p,0)))
        qgeom=-sigma*h*h*E*E*xi*(384*p+120*H*xi)
        qcurrent=n*(deltaPhi/1000+6*A); qosc=-18*h*h*E*E*chi*chi
        direct=(geometric-rho-oscillator).a[2]; simplified=qgeom+qcurrent+qosc
        c.need((geometric.a[2]-qgeom).iszero(),'DIRECT_S7_GEOMETRIC_SOURCE')
        c.need((-rho.a[2]-qcurrent).iszero(),'DIRECT_CONSERVED_CURRENT_SOURCE')
        c.need((-oscillator.a[2]-qosc).iszero(),'DIRECT_OSCILLATOR_SOURCE')
        c.need((direct-simplified).iszero(),'DIRECT_TOTAL_S7_SOURCE')
        first=(geometric-rho-oscillator).a[1]
        c.need((first-(42*sigma*h*h*E*E*xi-n)).iszero(),'FIRST_GRAPH_ROW')
        c.need(direct.derivative(9).iszero(),'UNKNOWN_SECOND_LAPSE_DROPS_OUT')
        # Restrict the exact polynomial to remote n=xi=0, without evaluating points.
        remote=P({powers:coef for powers,coef in direct.t.items() if powers[2]==powers[8]==0})
        c.need((remote-qosc).iszero(),'REMOTE_WALL_LIMIT')
        mutated={'geometry_sign':-qgeom+qcurrent+qosc,
                 'current_force_sign':qgeom+n*(-deltaPhi/1000+6*A)+qosc,
                 'missing_oscillator_half':qgeom+qcurrent+2*qosc,
                 'omitted_oscillator':qgeom+qcurrent}
        mutations={}
        for key,bad in mutated.items():
            diff=direct-bad; c.need(not diff.iszero(),'MUTATION_UNDETECTED:'+key); mutations[key]=diff.pack()
        result[str(sigma)]={'direct_total':direct.pack(),'geometric':qgeom.pack(),'current':qcurrent.pack(),
                            'oscillator':qosc.pack(),'first_order_row':first.pack(),'remote_limit':remote.pack(),
                            'mutations_detected':mutations,'unknown_second_lapse_independence':True}
    return {'variables':list(a.NAMES),'orientations':result,
            'premise':'Source extraction sets xi2=0; linear xi2 row is sigma E² r2(r2-h). Inverse-velocity factors are exact through degree2; omitted terms begin at degree3 in S7.'}

def evaluate(name,remote_parent):
    record=c.read(T10/'output'/('current_radar_'+name+'.json'))['full_forced_assembly']; k=c.interval(record['k'])
    c.need(k.lo>0,'POSITIVE_K'); output={}
    for source in ('lower','upper'):
        ch=record['channels'][source]; a6=c.interval(ch['source_wall_a6']); c.need(a6.lo>0,'POSITIVE_DENSITY_SCALE')
        scale2=a6.sq(); walls={}
        for side,sigma in (('lower',Q(1)),('upper',Q(-1))):
            w={key:c.interval(value) for key,value in ch['walls'][side].items()}
            E=w['E']; n=w['n']; xi=w['xi']; p=w['psi']; H=w['H']; T=w['T']; f=w['f']; chi=w['chi']
            c.need(E.lo>0 and w['d'].lo>0,'WALL_DOMAIN')
            E6=E.sq()*E.sq()*E.sq()
            if side==source:
                c.need(n.lo>0 and n.overlap(E6) and (n/E6-I(1)).zero(),'UNIT_CONSERVED_CURRENT_CONSISTENCY')
            else:
                c.need(n.lo==n.hi==0 and xi.lo==xi.hi==0,'REMOTE_ZERO_CURRENT_AND_FIRST_GRAPH')
            # Exact channel labels 1/0 are inherited from authenticated basis.py.
            reconstructed=(f+T*xi)/w['d']; c.need(chi.overlap(reconstructed),'OSCILLATOR_RECONSTRUCTION')
            qgeom=-sigma*k*E.sq()*xi*(384*p+120*H*xi)
            qcurrent=n*((T*xi+f)/1000+6*(H*xi+p))
            qosc=-18*k*E.sq()*chi.sq(); qtotal=qgeom+qcurrent+qosc
            divisor=156*sigma*k*E.sq(); c.need(not divisor.zero(),'GRAPH_DIVISOR')
            graph=-qtotal/divisor
            pieces={'geometric_kinematic':-qgeom/divisor,'current_feedback':-qcurrent/divisor,'oscillator_kinetic':-qosc/divisor}
            piece_sum=sum(pieces.values(),I(0)); c.need(piece_sum.overlap(graph) and (piece_sum-graph).zero(),'GRAPH_SOURCE_DECOMPOSITION')
            vals={'qI_geometric':qgeom,'qI_current':qcurrent,'qI_oscillator':qosc,'qI_total':qtotal,
                  'graph_divisor':divisor,'xi_second':graph,'source_density_squared_normalized_xi_second':scale2*graph,
                  'chi_first':chi,'oscillator_reconstruction_consistency_only':reconstructed,
                  **{'xi_second_from_'+key:v for key,v in pieces.items()}}
            if side!=source:
                old=remote_parent['per_engine'][name][source+'_to_'+side]
                inherited=c.interval(old['eulerian_graph_second_coefficient'])
                c.need(graph.overlap(inherited),'ACCEPTED_T16_REMOTE_REPRODUCTION')
                vals['T16_remote_consistency_only']=inherited
            walls[side]={'values':{key:v.pack() for key,v in vals.items()},
                         'xi_second_sign':1 if graph.lo>0 else -1 if graph.hi<0 else 0}
        endpoint=c.interval(walls['upper']['values']['xi_second'])-c.interval(walls['lower']['values']['xi_second'])
        output[source]={'walls':walls,'chart_endpoint_width_contribution':endpoint.pack(),
                        'source_density_squared_normalized_endpoint_contribution':(scale2*endpoint).pack(),
                        'exact_source_direction_authority':'Authenticated T10 basis.py assigns (Na²,Nb²)=(1,0) or (0,1); saved n is Ni² Ei^6.'}
    return output

def main():
    c.need(not any((ROOT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART'); begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('GRAPH_SUBSYSTEM_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        proof=qualify_s7(); c.put('S7_IDENTITIES.json',proof)
        remote=c.read(T16/'RESULT.json'); per={name:evaluate(name,remote) for name in ('primary','independent')}; combined={}
        for source in ('lower','upper'):
            walls={}
            for side in ('lower','upper'):
                vals={}
                for key in per['primary'][source]['walls'][side]['values']:
                    if key.endswith('consistency_only'): continue
                    a,b=[c.interval(per[name][source]['walls'][side]['values'][key]) for name in ('primary','independent')]
                    c.need(a.overlap(b),'ENGINE_GRAPH_DISAGREEMENT:'+source+':'+side+':'+key); vals[key]=a.hull(b).pack()
                graph=c.interval(vals['xi_second']); walls[side]={'values':vals,'xi_second_sign':1 if graph.lo>0 else -1 if graph.hi<0 else 0}
            combined[source]={'walls':walls}
            for key in ('chart_endpoint_width_contribution','source_density_squared_normalized_endpoint_contribution'):
                a,b=[c.interval(per[name][source][key]) for name in ('primary','independent')]
                c.need(a.overlap(b),'ENGINE_ENDPOINT_DISAGREEMENT:'+source+':'+key); combined[source][key]=a.hull(b).pack()
        c.put('RESULT.json',{'classification':'TRIANGULAR_QUADRATIC_GRAPH_SUBSYSTEM_ENCLOSED','combined':combined,'per_engine':per,
               'identity_record':'S7_IDENTITIES.json','identity_sha256':c.sha(ROOT/'S7_IDENTITIES.json'),
               'seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'Necessary complete local/remote second-order graph coefficients for two single-current directions, in fixed Eulerian radial chart. Source split is chart diagnostic. Not full n2 geometry, proper-distance coefficient, finite-charge existence or propagation/excitation.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
