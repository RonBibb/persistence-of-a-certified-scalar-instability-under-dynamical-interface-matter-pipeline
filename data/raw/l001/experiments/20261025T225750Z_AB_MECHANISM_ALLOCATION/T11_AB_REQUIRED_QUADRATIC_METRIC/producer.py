"""Necessary second-order chart metric combination from accepted saved cells.

Not a full second-order solution, invariant observable or finite-charge bound.
"""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('quadratic_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT
I=c.I; T10=ROOT/'../T10_AB_CURRENT_RADAR_RESPONSE'
DIRECTIONS=('lower_unit_current','upper_unit_current','both_unit_current','both_unit_proper_density')

def coarsen(x):
    scale=1<<80
    lo=Q((x.lo*scale).__floor__(),scale)
    hi=Q((x.hi*scale).__ceil__(),scale)
    c.need(lo<=x.lo<=x.hi<=hi,'DYADIC_CONTAINMENT')
    return I(lo,hi)

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY'); g=c.read(ROOT/'ADMISSION.json')
    c.need(g.get('admitted') is True and g.get('t10_terminal_review_accepted') is True,'ACCEPTED_T10_REQUIRED')
    required=['../T10_AB_CURRENT_RADAR_RESPONSE/TERMINAL_REVIEW.md','../T10_AB_CURRENT_RADAR_RESPONSE/output/RESULT.json',
              '../NONLINEAR_TRACEFREE_LEAD.md']
    for name in ('primary','independent'):
        required.append('../T10_AB_CURRENT_RADAR_RESPONSE/output/current_radar_'+name+'.json')
        for kind in ('homogeneous','particular_lower'):
            required.extend('../T10_AB_CURRENT_RADAR_RESPONSE/output/'+kind+'_'+name+suffix for suffix in ('.json','_RADAR_BUDGET.json'))
    for rel in required: c.need(rel in g['sources'],'MISSING_INPUT_BINDING:'+rel)
    for rel,d in g['sources'].items(): c.need(c.sha(ROOT/rel)==d,'SOURCE_HASH:'+rel)
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for path,d in rt['files'].items(): c.need(c.sha(path)==d,'RUNTIME_HASH:'+path)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')
    c.need(c.read(T10/'output/RESULT.json')['classification']=='FIRST_CURRENT_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','T10_SCOPE')

def controls():
    h,p,f=Q(2,7),Q(-3,5),Q(5,11); r1=-6*h; r2=-12*h
    dp=r1*p; db=-2*dp; df=r1*f
    raw=db*db-2*dp*db-2*dp*dp+df*df
    formula=-Q(3,13)*(6*p*p+f*f)
    c.need(raw+r2*(r2-h)*formula==0,'S6_QUADRATIC_ROW')
    c.need(raw==r1*r1*(6*p*p+f*f),'S6_SOURCE_EXPANSION')
    # Every transport term of the linear c row is proportional to c1 or its jets.
    c1,cs,ct,css=Q(0),Q(0),Q(0),Q(0)
    c.need(c1+7*cs+11*ct+13*css==0,'ZERO_C1_TRANSPORT')
    pA,pB,fA,fB=map(Q,('2/3','-5/7','3/11','7/13'))
    x,y=Q(2,5),Q(3,7)
    summed=6*(x*pA+y*pB)**2+(x*fA+y*fB)**2
    expanded=x*x*(6*pA*pA+fA*fA)+y*y*(6*pB*pB+fB*fB)+2*x*y*(6*pA*pB+fA*fB)
    c.need(summed==expanded,'MIXED_CURRENT_CROSS_TERM')
    gaa=6*pA*pA+fA*fA; gbb=6*pB*pB+fB*fB; gab=6*pA*pB+fA*fB
    c.need(gaa*gbb-gab*gab==6*(pA*fB-pB*fA)**2,'GRAM_DETERMINANT')
    cross=I(-2,3).sq(); c.need(cross.lo==0 and cross.hi==9,'CROSS_ZERO_SQUARE')
    neg=-Q(3,13)*(6*I(-1,1).sq()+I(-2,2).sq()); c.need(neg.hi==0,'NONPOSITIVE_ENCLOSURE')
    tail=I(-3,-2)*I(0,Q(1,4)); c.need(tail.lo==Q(-3,4) and tail.hi==0,'SIGNED_OPTIONAL_TAIL')
    fixture=I(Q(-1,3),Q(2,7)); rounded=coarsen(fixture)
    c.need(rounded.lo<=fixture.lo and rounded.hi>=fixture.hi,'DYADIC_CONTROL')
    return {'S6_source_and_linear_row':True,'zero_c1_transport':True,'mixed_current_cross_term':True,
            'Gram_determinant':True,'cross_zero_square':True,'nonpositive_enclosure':True,'signed_optional_tail':True,'outward_dyadic_control':True}

def evaluate(name,begun):
    out=T10/'output'; rec=c.read(out/('current_radar_'+name+'.json'))['full_forced_assembly']['channels']
    bases={}; budgets={}
    for kind in ('homogeneous','particular_lower'):
        base=c.read(out/(kind+'_'+name+'.json')); c.need(base['all_cell_checks_pass'],'PARENT_FLOW_GATES')
        bp=out/base['budget']['path']; c.need(c.sha(bp)==base['budget']['sha256'],'PARENT_BUDGET_HASH')
        bases[kind]=base; budgets[kind]=c.read(bp)
    H,P=budgets['homogeneous'],budgets['particular_lower']
    c.need(H['D_bounds']==P['D_bounds'] and len(H['cells'])==len(P['cells']),'BASIS_DOMAIN_MATCH')
    Dlo,Dhi=map(Q,H['D_bounds'])
    amps={side:c.interval(rec[side]['homogeneous_multiplier']) for side in ('lower','upper')}
    a6={side:c.interval(rec[side]['source_wall_a6']) for side in ('lower','upper')}
    c.need(all(v.lo>0 for v in a6.values()),'POSITIVE_PROPER_DENSITY_SCALES')
    weights={'lower_unit_current':(I(1),I(0)),'upper_unit_current':(I(0),I(1)),
             'both_unit_current':(I(1),I(1)),'both_unit_proper_density':(a6['lower'],a6['upper'])}
    stats={key:{'range':None,'integral':I(0),'negative_count':0,'unresolved_count':0,
                'negative_length':I(0),'rows':[]} for key in DIRECTIONS}
    expected=Q(0); total_mand=Q(0); total_possible=Q(0)
    for j,(hr,pr) in enumerate(zip(H['cells'],P['cells'])):
        if j%64==0: c.need(time.monotonic()-begun<900,'TOTAL_CAP')
        for key in ('index','s','step','mandatory','optional'): c.need(hr[key]==pr[key],'CELL_ALIGNMENT:'+key)
        pos,step,mandatory,optional=map(Q,(hr['s'],hr['step'],hr['mandatory'],hr['optional']))
        c.need(hr['index']==j and pos==expected,'CELL_CHAIN'); expected=pos+step
        c.need(mandatory==max(Q(0),min(step,Dlo-pos)) and optional==max(Q(0),min(step,Dhi-pos))-mandatory,'DOMAIN_WIDTHS')
        total_mand+=mandatory; total_possible+=mandatory+optional
        ph,pp,fh,fp=map(c.interval,(hr['psi'],pr['psi'],hr['f'],pr['f']))
        pa=amps['lower']*ph+pp; pb=amps['upper']*ph
        fa=amps['lower']*fh+fp; fb=amps['upper']*fh
        for key,(wa,wb) in weights.items():
            # Sum profiles before squaring, preserving cross-current terms.
            p1=coarsen(wa*pa+wb*pb); f1=coarsen(wa*fa+wb*fb)
            value=coarsen(-Q(3,13)*(6*p1.sq()+f1.sq())); c.need(value.hi<=0,'GRAM_NONPOSITIVITY')
            contribution=value*mandatory+value*I(0,optional)
            st=stats[key]; st['range']=value if st['range'] is None else st['range'].hull(value)
            st['integral']=st['integral']+contribution; negative=value.hi<0
            st['negative_count' if negative else 'unresolved_count']+=1
            if negative: st['negative_length']=st['negative_length']+I(mandatory,mandatory+optional)
            st['rows'].append({'index':j,'s':str(pos),'step':str(step),'mandatory':str(mandatory),'optional':str(optional),
                               'p1':p1.pack(),'f1':f1.pack(),'c2':value.pack(),'integral_contribution':contribution.pack(),
                               'strictly_negative_whole_cell':negative})
    c.need(total_mand==Dlo and total_possible==Dhi,'FULL_DOMAIN_MEASURE')
    result={}
    for key,st in stats.items():
        filename=name+'_'+key+'_CELLS.json'
        c.put(filename,{'engine':name,'direction':key,'D_bounds':H['D_bounds'],
                        'derived_enclosure_dyadic_denominator_power':80,
                        'weights_Na_squared_Nb_squared':[v.pack() for v in weights[key]],'cells':st['rows']})
        result[key]={'whole_collar_range':st['range'].pack(),'integral':st['integral'].pack(),
                     'strict_negative_cell_count':st['negative_count'],'zero_containing_cell_count':st['unresolved_count'],
                     'strict_negative_covered_length':st['negative_length'].pack(),'cell_count':len(st['rows']),
                     'classification':'STRICTLY_NEGATIVE_THROUGHOUT' if st['unresolved_count']==0 else 'NONPOSITIVE_WITH_UNRESOLVED_ZERO_CELLS',
                     'cells':{'path':filename,'sha256':c.sha(ROOT/filename)}}
    return {'engine':name,'D_bounds':H['D_bounds'],'directions':result}

def main():
    c.need(not any((ROOT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART'); begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('QUADRATIC_METRIC_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested=controls(); c.put('CONTROLS.json',tested); per={n:evaluate(n,begun) for n in ('primary','independent')}
        c.need(per['primary']['D_bounds']==per['independent']['D_bounds'],'ENGINE_DOMAIN_MATCH'); combined={}
        for direction in DIRECTIONS:
            a=per['primary']['directions'][direction]; b=per['independent']['directions'][direction]; vals={}
            for key in ('whole_collar_range','integral'):
                x,y=c.interval(a[key]),c.interval(b[key]); c.need(x.overlap(y),'ENGINE_DISAGREEMENT:'+direction+':'+key)
                vals[key]=x.hull(y).pack()
            # Covered lengths describe engine-specific resolved subsets, not the same observable.
            vals['strict_negative_covered_length_by_engine']={n:per[n]['directions'][direction]['strict_negative_covered_length'] for n in per}
            vals['strict_negative_everywhere_both_engines']=all(per[n]['directions'][direction]['zero_containing_cell_count']==0 for n in per)
            combined[direction]=vals
        c.put('RESULT.json',{'classification':'REQUIRED_QUADRATIC_CHART_METRIC_COMBINATION_ENCLOSED','combined':combined,'per_engine':per,
               'controls':tested,'seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'Necessary c2=b2+2p2 in declared chart and first-current coefficient directions only. Not proper distance at second order, full n2 solution, finite-charge existence or remainder bound.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
