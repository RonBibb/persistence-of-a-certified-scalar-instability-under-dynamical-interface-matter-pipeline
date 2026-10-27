"""Exact Q5 quadratic wall sources and explicit Eulerian/pulled load bridge."""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); return v
c=module('wall_common',ROOT/'common.py'); c.ROOT=ROOT; I=c.I
T10=ROOT/'../T10_AB_CURRENT_RADAR_RESPONSE'; T15=ROOT/'../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION'
T17=ROOT/'../T17_AB_COMPLETE_QUADRATIC_GRAPH_SUBSYSTEM'

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY'); gate=c.read(ROOT/'ADMISSION.json'); c.need(gate.get('admitted') is True,'ADMISSION')
    for key in ('t10','t15','t17'): c.need(gate.get(key+'_terminal_review_accepted') is True,'PARENT_REVIEW:'+key)
    required=['../SECOND_ORDER_EULERIAN_WALL_SCRATCH.md','../T10_AB_CURRENT_RADAR_RESPONSE/TERMINAL_REVIEW.md',
              '../T10_AB_CURRENT_RADAR_RESPONSE/output/RESULT.json','../T10_AB_CURRENT_RADAR_RESPONSE/basis.py',
              '../T10_AB_CURRENT_RADAR_RESPONSE/inputs/central_bindings.json','../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py',
              '../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/TERMINAL_REVIEW.md','../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/RESULT.json',
              '../T17_AB_COMPLETE_QUADRATIC_GRAPH_SUBSYSTEM/TERMINAL_REVIEW.md','../T17_AB_COMPLETE_QUADRATIC_GRAPH_SUBSYSTEM/RESULT.json']
    required+=['../T10_AB_CURRENT_RADAR_RESPONSE/output/current_radar_'+n+'.json' for n in ('primary','independent')]
    for rel in required: c.need(rel in gate['sources'],'MISSING_PARENT_BINDING:'+rel)
    for rel,d in gate['sources'].items(): c.need(c.sha(ROOT/rel)==d,'SOURCE_HASH:'+rel)
    c.need(c.sha(ROOT/'polynomial_helper.py')==c.sha(T15/'producer.py'),'QUALIFIED_HELPER_COPY')
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for path,d in rt['files'].items(): c.need(c.sha(path)==d,'RUNTIME_HASH:'+path)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')
    c.need(c.read(T10/'output/RESULT.json')['classification']=='FIRST_CURRENT_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','T10_SCOPE')
    c.need(c.read(T15/'RESULT.json')['classification']=='EULERIAN_QUADRATIC_BULK_SOURCES_QUALIFIED','T15_SCOPE')
    c.need(c.read(T17/'RESULT.json')['classification']=='TRIANGULAR_QUADRATIC_GRAPH_SUBSYSTEM_ENCLOSED','T17_SCOPE')

def exact_q5():
    a=module('qualified_polynomial_helper',ROOT/'polynomial_helper.py')
    a.NAMES=('E','h','xi','p','H','Hp','T','Tp','Tpp','f','g','u','gp','chi','n','p2','f2','g2','chi2','xi2','c2','Xprime')
    a.N=len(a.NAMES); a.ZERO=(0,)*a.N
    E,h,xi,p,H,Hp,T,Tp,Tpp,f,g,u,gp,chi,n,p2,f2,g2,chi2,xi2,c2,Xprime=[a.variable(j) for j in range(a.N)]
    a.R=-6*h; R=a.R; P=a.P; S=a.S
    A=H*xi+p; d1=2+18*h*h*E*E; d2=2+108*h*h*E*E
    # Exact displaced Eulerian wall traces through degree two, including
    # arbitrary new coefficients so reconstruction is tested off shell.
    pwall=S((0,p,p2+xi*u)); bwall=S((0,-2*p,c2-2*p2-2*xi*u))
    logawall=S((0,H*xi,H*xi2+Hp*xi*xi/2))
    invN=E*(-logawall-pwall).expzero(); B=bwall.expzero()
    St=S((0,R*xi,2*R*xi2)); v=B*invN*St
    invone=1+v*v; invsqrt=1+v*v/2
    Hwall=S((H,Hp*xi,0)); Ewall=E*(-logawall).expzero()
    Twall=S((T,Tp*xi,Tp*xi2+Tpp*xi*xi/2))
    scalar_delta=S((0,T*xi+f,T*xi2+Tp*xi*xi/2+f2+xi*g))
    scalar_radial=S((0,g,g2+xi*gp)); scalar_time=S((0,R*f,2*R*f2+R*xi*g))
    oscillator=S((0,chi,chi2)); chid=oscillator.dtime()
    nu2=S((0,n,0))*(-6*logawall-6*pwall).expzero()
    friction=3*h+2*Hwall*St+2*pwall.dtime()+v*v.dtime()*invone
    O=invN*invN*invone*(oscillator.dtime().dtime()+friction*chid)+2*oscillator-scalar_delta
    o=36*h*h*E*E*A*chi-xi*g-xi*xi*Tp/2
    c.need((O.a[1]-(d1*chi-f-T*xi)).iszero(),'Q5_OSCILLATOR_FIRST_ROW')
    c.need((O.a[2]-(d2*chi2-f2-T*xi2+o)).iszero(),'DIRECT_Q5_OSCILLATOR_SOURCE_AND_NEW_ROW')
    output={}
    for sigma in (1,-1):
        J=invsqrt*((-bwall).expzero()*(Twall+scalar_radial)+v*(-pwall).expzero()*Ewall*scalar_time)
        J=J-sigma*(2*sigma*T+21*scalar_delta-oscillator-nu2/1000)/2
        j=xi*xi*Tpp/2+xi*gp+2*p*(xi*Tp+g)+(2*p*p+2*xi*u)*T
        j=j+36*h*h*E*E*xi*f+18*h*h*E*E*xi*xi*T-sigma*(21*(xi*xi*Tp/2+xi*g)+6*n*A/1000)/2
        first=g+Tp*xi+2*T*p-sigma*(21*(T*xi+f)-chi-n/1000)/2
        newrow=g2+Tp*xi2-T*c2+2*T*p2-sigma*(21*(f2+T*xi2)-chi2)/2
        c.need(J.a[0].iszero() and O.a[0].iszero(),'BACKGROUND_WALL_ROWS')
        c.need((J.a[1]-first).iszero(),'Q5_SCALAR_FIRST_ROW')
        c.need((J.a[2]-newrow-j).iszero(),'DIRECT_Q5_SCALAR_SOURCE_AND_NEW_ROW')
        # Eliminate chi2 without dividing by a polynomial: this is d2 times
        # the undivided Q6 boundary law minus its source load.
        load_d=2*sigma*d2*(T*c2-Tp*xi2-j)+(21*d2-1)*T*xi2+o
        robin_d=2*sigma*d2*(g2+2*T*p2)-(21*d2-1)*f2-load_d
        c.need((2*sigma*d2*J.a[2]-O.a[2]-robin_d).iszero(),'EXACT_Q6_ELIMINATION')
        oP=o+xi*g; jP=j-Xprime*g-xi*gp-2*T*xi*u+Q(21*sigma,2)*xi*g
        loadP_d=2*sigma*d2*(T*c2-Tp*xi2-jP)+(21*d2-1)*T*xi2+oP
        delta_load_d=2*sigma*d2*(Xprime*g+xi*gp+2*T*xi*u)-(21*d2-1)*xi*g
        c.need((loadP_d-load_d-delta_load_d).iszero(),'PULLED_LOAD_BRIDGE')
        changed_robin=2*sigma*d2*(g2+Xprime*g+xi*gp+2*T*(p2+xi*u))-(21*d2-1)*(f2+xi*g)
        original_robin=2*sigma*d2*(g2+2*T*p2)-(21*d2-1)*f2
        c.need((changed_robin-original_robin-delta_load_d).iszero(),'ARBITRARY_NEW_FIELDS_CHART_CONTROL')
        mutations={'missing_normal_tilt':j-36*h*h*E*E*xi*f,
                   'missing_boost':j-18*h*h*E*E*xi*xi*T,
                   'current_force_sign':j+sigma*6*n*A/1000}
        detected={}
        for key,bad in mutations.items():
            diff=J.a[2]-newrow-bad; c.need(not diff.iszero(),'UNDETECTED_MUTATION:'+key); detected[key]=diff.pack()
        missing_jacobian=delta_load_d-2*sigma*d2*Xprime*g
        c.need(not (delta_load_d-missing_jacobian).iszero(),'MISSING_XPRIME_MUTATION')
        output[str(sigma)]={'o2_Eulerian':o.pack(),'j2_Eulerian':j.pack(),'direct_O2':O.a[2].pack(),'direct_J2':J.a[2].pack(),
            'Q6_load_times_d2':load_d.pack(),'o2_pulled':oP.pack(),'j2_pulled':jP.pack(),
            'pulled_load_times_d2':loadP_d.pack(),'load_bridge_times_d2':delta_load_d.pack(),'mutations_detected':detected}
    return {'variables':list(a.NAMES),'orientations':output,'arbitrary_new_field_control':True,
            'scope':'Exact source and new-row decomposition of Q5 in Eulerian chart; exact pulled unknown/source transformation including Xprime*g. No n2 fields solved.'}

def evaluate(name,graphs,bindings):
    assembly=c.read(T10/'output'/('current_radar_'+name+'.json'))['full_forced_assembly']
    k=c.interval(assembly['k']); m=I(bindings['model_exact']['m2']); mu1=-18*k
    D=I(*bindings['config']['D']); c.need(D.lo>0 and k.lo>0,'BACKGROUND_DOMAIN'); out={}
    for source in ('lower','upper'):
        ch=assembly['channels'][source]; scale=c.interval(ch['source_wall_a6']).sq()
        xi_a=c.interval(ch['walls']['lower']['xi']); xi_b=c.interval(ch['walls']['upper']['xi']); Xprime=(xi_b-xi_a)/D
        walls={}
        for side,sigma in (('lower',Q(1)),('upper',Q(-1))):
            w={key:c.interval(v) for key,v in ch['walls'][side].items()}
            E,H,T,Tp,Phi,p,f,g,chi,n,xi=[w[key] for key in ('E','H','T','Tp','Phi','psi','f','g','chi','n','xi')]
            c.need(E.lo>0,'POSITIVE_E'); c.need(Tp.overlap(m*Phi-4*H*T),'BACKGROUND_TPRIME_RECONSTRUCTION')
            Hp=-T.sq()/3-k*E.sq(); Tpp=m*T-4*Hp*T-4*H*Tp
            u=-2*H*p-T*f/3; gp=-4*H*g+(m-mu1*E.sq()+2*T.sq())*f+(12*H*T-4*m*Phi)*p
            A=H*xi+p
            o=36*k*E.sq()*A*chi-xi*g-xi.sq()*Tp/2
            j=xi.sq()*Tpp/2+xi*gp+2*p*(xi*Tp+g)+(2*p.sq()+2*xi*u)*T
            j=j+36*k*E.sq()*xi*f+18*k*E.sq()*xi.sq()*T-sigma*(21*(xi.sq()*Tp/2+xi*g)+6*n*A/1000)/2
            c2=-Q(3,13)*(6*p.sq()+f.sq())
            xi2=c.interval(graphs['per_engine'][name][source]['walls'][side]['values']['xi_second'])
            d2=2+108*k*E.sq(); c.need(d2.lo>0,'SECOND_OSCILLATOR_DENOMINATOR'); Gamma2=21-1/d2
            loadE=2*sigma*(T*c2-(Tp-sigma*Gamma2*T/2)*xi2-j+sigma*o/(2*d2))
            oP=o+xi*g; jP=j-Xprime*g-xi*gp-2*T*xi*u+Q(21,2)*sigma*xi*g
            loadP=2*sigma*(T*c2-(Tp-sigma*Gamma2*T/2)*xi2-jP+sigma*oP/(2*d2))
            shift=2*sigma*(Xprime*g+xi*gp+2*T*xi*u)-Gamma2*xi*g
            c.need(loadP.overlap(loadE+shift) and (loadP-loadE-shift).zero(),'NUMERICAL_CHART_LOAD_IDENTITY')
            vals={'p1_prime':u,'f1_second':gp,'T_second':Tpp,'X1_prime':Xprime,'c2_required':c2,'xi2_accepted':xi2,
                  'o2_Eulerian':o,'j2_Eulerian':j,'d2':d2,'Gamma2':Gamma2,'undivided_Robin_load_Eulerian':loadE,
                  'o2_pulled':oP,'j2_pulled':jP,'undivided_Robin_load_pulled':loadP,'load_chart_shift':shift,
                  'proper_density_squared_o2_Eulerian':scale*o,'proper_density_squared_j2_Eulerian':scale*j,
                  'proper_density_squared_load_Eulerian':scale*loadE,'proper_density_squared_load_pulled':scale*loadP}
            walls[side]={key:v.pack() for key,v in vals.items()}
        out[source]=walls
    return out

def main():
    c.need(not any((ROOT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART'); begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('WALL_SOURCE_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        proof=exact_q5(); c.put('Q5_IDENTITIES.json',proof)
        graphs=c.read(T17/'RESULT.json'); bindings=c.read(T10/'inputs/central_bindings.json')
        per={name:evaluate(name,graphs,bindings) for name in ('primary','independent')}; combined={}
        for source in ('lower','upper'):
            combined[source]={}
            for side in ('lower','upper'):
                vals={}
                for key in per['primary'][source][side]:
                    a,b=[c.interval(per[name][source][side][key]) for name in ('primary','independent')]
                    c.need(a.overlap(b),'WALL_SOURCE_ENGINE_DISAGREEMENT:'+source+':'+side+':'+key); vals[key]=a.hull(b).pack()
                combined[source][side]=vals
        c.put('RESULT.json',{'classification':'QUADRATIC_Q5_WALL_SOURCES_AND_CHART_LOADS_QUALIFIED','combined':combined,'per_engine':per,
             'identity_record':'Q5_IDENTITIES.json','identity_sha256':c.sha(ROOT/'Q5_IDENTITIES.json'),
             'seconds':time.monotonic()-begun,'utc':c.now(),
             'scope':'Complete Q5 oscillator/scalar source loads for four wall cases plus accepted graph subsystem and explicit pulled/Eulerian load bridge. Undivided Q6 loads, not Q7 reduced scalar Robin data requiring bulk Sc2. No n2 fields, full geometry, proper-distance coefficient or finite-charge claim.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
