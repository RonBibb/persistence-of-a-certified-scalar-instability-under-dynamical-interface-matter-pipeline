"""Independent Fraction-interval cubic wall audit; no producer/series imports.

All h powers are eliminated analytically using r=-6h and h^2=k.
This module writes nothing. The admitted Linux runner saves run()'s report.
"""
import sys
sys.dont_write_bytecode=True
import importlib.util
import json
from pathlib import Path
from fractions import Fraction as F

ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
def read(path):return json.loads(Path(path).read_text())
def need(value,label):
    if not value:raise AssertionError(label)

def run():
    need(sys.platform=='linux','LINUX_ONLY')
    # Only reuse the already reviewed exact interval class, not its audit run.
    spec=importlib.util.spec_from_file_location('accepted_parent_interval',PARENT/'terminal_audit/audit.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    I=module.I
    def iv(record):
        need(set(record)=={'exact_bounds'},'INTERVAL_SCHEMA')
        return I(*record['exact_bounds'])
    output=read(ROOT/'RESULT.json')
    need(output['all_gates'] is True and output['qualification']['pass'] is True,'PRODUCER_QUALIFIED')
    reports={};published_graphs=[]
    for engine in ('primary','independent'):
        parent=read(PARENT/('PRODUCTION_'+engine+'.json'))
        k=iv(parent['parameters']['k']);m=iv(parent['parameters']['m2'])
        need(k.lo>0 and parent['all_gates'] is True,'PARENT_K_AND_GATES')
        saved=output['per_engine'][engine];wall_reports={};xis={}
        for side,sigma in (('lower',1),('upper',-1)):
            pw=parent['walls'][side];z=list(map(iv,pw['state']))
            need(len(z)==14,'PARENT_STATE_DIMENSION')
            W,H,Phi,T,E,p,f,g,p2,f2,g2,_,_,_=z
            w={key:iv(value) for key,value in pw['fresh'].items()}
            x,y,chi,chi2,n=w['xi'],w['xi2'],w['chi'],iv(pw['chi2']),w['n']
            e2=E*E;Hp=-T*T/3-k*e2;Tp=m*Phi-4*H*T
            u=-2*H*p-T*f/3;c2=w['c2']
            need(E.lo>0,'POSITIVE_E')
            if side=='upper':need(x.lo==x.hi==n.lo==n.hi==0,'REMOTE_RESTRICTION')
            else:need(n.overlap(e2*e2*e2),'UNIT_LOWER_CURRENT')
            observed=saved['walls'][side]
            # Validate numerical sqrt provenance, although this audit never uses h.
            hh=iv(observed['inputs']['h'])
            need(hh.lo>0 and (hh*hh).contains(k),'POSITIVE_H_SQUARE_ENCLOSES_K')
            inputs=dict(E=E,xi1=x,xi2=y,p1=p,p2=p2,H=H,Hp=Hp,u=u,c2=c2,
                        T=T,Tp=Tp,f1=f,f2=f2,g1=g,chi1=chi,chi2=chi2,n=n)
            for key,value in inputs.items():
                need(value.overlap(iv(observed['inputs'][key])),'INPUT_RECONSTRUCTION:'+engine+side+key)
            A=H*x+p;B=H*y+Hp*x*x/2+p2+x*u
            C=-3*p-H*x;J=c2-3*p2-3*x*u-H*y-Hp*x*x/2
            # v1=-6h E x, v2=h E V2, v3=h E V3 when xi3=0.
            V2=-12*y-6*x*C
            V3=-12*y*C-6*x*(J+C*C/2)
            # r*v1^3 contributes1296 k^2 E^4 x^3 after sigma E.
            # (v1^2/2)*t1 contributes756 k^2 E^4 x^3. Keep BOTH.
            boost=2052*sigma*k*k*e2*e2*x*x*x
            geometric=sigma*k*e2*(-19*V3+18*p*V2+72*x*(c2-3*p2)-108*x*x*u
                         -A*(-13*V2-108*x*p)+42*x*(A*A/2-B))+boost
            phi1=T*x+f;phi2=T*y+Tp*x*x/2+f2+x*g
            current=n*(phi2/1000+6*B-18*A*A-6*A*phi1/1000)
            oscillator=-72*k*e2*chi*chi2+36*k*e2*A*chi*chi
            terms=dict(geometric=geometric,current=current,oscillator=oscillator)
            terms['total']=geometric+current+oscillator
            for key,value in terms.items():
                need(value.overlap(iv(observed['sources_closed'][key])),'CLOSED_COEFFICIENT:'+engine+side+key)
                need(value.overlap(iv(observed['sources_direct'][key])),'DIRECT_COEFFICIENT:'+engine+side+key)
            divisor=342*sigma*k*e2
            need(not divisor.zero() and divisor.overlap(iv(observed['divisor'])),'DIVISOR')
            xi=-terms['total']/divisor;published=iv(observed['xi3'])
            need(xi.overlap(published),'XI3')
            need((divisor*published+terms['total']).zero() and iv(observed['solved_row']).zero(),'CUBIC_ROW')
            first=42*sigma*k*e2*x-n
            second=156*sigma*k*e2*y-sigma*k*e2*x*(384*p+120*H*x)+n*((T*x+f)/1000+6*A)-18*k*e2*chi*chi
            need(first.zero() and second.zero(),'FIRST_SECOND_PARENT_GRAPH_ROWS')
            need(first.overlap(iv(observed['first_row'])) and second.overlap(iv(observed['second_row'])),'PARENT_ROW_RECORDS')
            if side=='upper':
                remote=-1056*sigma*k*e2*y*p-72*k*e2*chi*chi2+36*k*e2*p*chi*chi
                need(remote.overlap(terms['total']),'REMOTE_WITH_XI2')
            xis[side]=xi
            wall_reports[side]=dict(reconstructed={key:v.record() for key,v in terms.items()},
                xi3=xi.record(),boost_h4=boost.record(),first_row=first.record(),second_row=second.record())
        graph=xis['upper']-xis['lower'];published=iv(saved['graph3'])
        need(graph.overlap(published),'ENGINE_GRAPH3')
        exported_difference=iv(saved['walls']['upper']['xi3'])-iv(saved['walls']['lower']['xi3'])
        need(exported_difference.overlap(published),'EXPORTED_WALL_DIFFERENCE')
        graph2=iv(parent['graph']);need(not graph2.zero(),'GRAPH2_NONZERO')
        need(iv(saved['graph2_parent']).contains(graph2),'PARENT_GRAPH2')
        need((graph/graph2).overlap(iv(saved['graph3_over_graph2'])),'HIERARCHY_RATIO')
        published_graphs.append(published)
        reports[engine]=dict(walls=wall_reports,graph3=graph.record(),graph3_over_graph2=(graph/graph2).record())
    need(published_graphs[0].overlap(published_graphs[1]),'ENGINE_GRAPH_OVERLAP')
    for side in ('lower','upper'):
        need(iv(output['per_engine']['primary']['walls'][side]['xi3']).overlap(iv(output['per_engine']['independent']['walls'][side]['xi3'])),'ENGINE_WALL_OVERLAP')
    union=I(min(v.lo for v in published_graphs),max(v.hi for v in published_graphs))
    graph=iv(output['graph3']);need(graph.contains(union),'OUTWARD_COMBINED_HULL')
    sign=1 if graph.lo>0 else -1 if graph.hi<0 else 0
    label='CUBIC_GRAPH_POSITIVE' if sign>0 else 'CUBIC_GRAPH_NEGATIVE' if sign<0 else 'CUBIC_GRAPH_SIGN_UNRESOLVED'
    need(output['classification']==label,'CLASSIFICATION')
    return dict({'pass':True},classification=label,sign=sign,per_engine=reports,
        method='Independent exact Fraction interval evaluation with h eliminated via h^2=k; h^4 boost terms retained.',
        source_modules_not_imported=['producer.py','series.py','closed.py'],
        scope='Saved full endpoint cubic graph consistency, first/second graph replay and outward hull. Not full d_sep3, tail bound, or independent ODE proof.',
        comparison_semantics='Exact reconstruction intervals must overlap saved outward evaluations; this is not a claim that alternate interval evaluation is narrower.')
