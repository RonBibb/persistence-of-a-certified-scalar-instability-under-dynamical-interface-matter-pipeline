"""Independent exact saved-cell audit; no ODE or derivative re-evaluation."""
import importlib.util,json,sys
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
SYSTEM=ROOT.parent/'20261026T025505Z_CUBIC_SYSTEM'
def need(v,label):
    if not v:raise AssertionError(label)
def read(p):return json.loads(Path(p).read_text())
def run():
    need(sys.platform=='linux','LINUX_ONLY')
    spec=importlib.util.spec_from_file_location('probe_audit_interval',PARENT/'terminal_audit/audit.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);I=module.I
    def iv(v):return I(*v['exact_bounds'])
    def equal(a,b):return a.lo==b.lo and a.hi==b.hi
    def power(a,n):
        out=I(1)
        for _ in range(n):out=out*a
        return out
    system=read(SYSTEM/'RESULT.json');need(system['pass'],'SYSTEM_ACCEPTED')
    def sc3(z,p):
        _,H,Phi,T,E,a,f,g,ap,fp,gp,ah,fh,gh=z[:14]
        values=dict(H=H,Phi=Phi,T=T,e=E*E,p=a,f=f,g=g,
                    P=ap+ah*p['A2'],F=fp+fh*p['A2'],G=gp+gh*p['A2'],m=p['m2'])
        total=I(0);names=system['bulk']['variables']
        for term in system['bulk']['sources']['Sc3']:
            need(len(term['powers'])==len(names),'POLYNOMIAL_DIMENSION')
            value=I(F(term['coefficient']))
            for name,n in zip(names,term['powers']):
                need(isinstance(n,int) and n>=0,'NONNEGATIVE_POWER')
                if name=='h':
                    need(n%2==0,'EVEN_H_POWER');value=value*power(p['k'],n//2)
                else:value=value*power(values[name],n)
            total=total+value
        return total
    controls=read(ROOT/'CONTROLS_RESULT.json');need(controls['pass'],'CONTROLS_PASS')
    result=read(ROOT/'RESULT.json');need(result['pass'],'RESULT_PASS')
    reports={};physical={}
    for name,count,dimension,step in (('primary',64,20,F(1,4096)),('independent',128,19,F(1,8192))):
        data=read(ROOT/('PROBE_'+name+'.json'));parent=read(PARENT/('PRODUCTION_'+name+'.json'))
        need(data['pass'] and data['engine']==name,'ENGINE_PASS')
        need(data['cells']==count and len(data['records'])==count,'CELL_COUNT')
        need(F(data['step'])==step and F(data['interval_length'])==step*count==F(1,64),'FIXED_DOMAIN')
        initial=list(map(iv,data['initial']));final=list(map(iv,data['final']))
        need(len(initial)==len(final)==dimension,'STATE_DIMENSION')
        need(list(map(F,data['initial_widths']))==[v.hi-v.lo for v in initial],'EXACT_INITIAL_WIDTHS')
        need(list(map(F,data['final_widths']))==[v.hi-v.lo for v in final],'EXACT_FINAL_WIDTHS')
        raw=list(map(iv,parent['raw_lower']));need(len(raw)==14,'PARENT_DIMENSION')
        old=raw if name=='primary' else raw[:4]+raw[5:]
        need(all(a.contains(b) for a,b in zip(initial,old)),'FULL_PARENT_INITIAL')
        p={k:iv(v) for k,v in data['parameters'].items()}
        for key,value in parent['parameters'].items():need(p[key].contains(iv(value)),'PARAMETER:'+key)
        need(p['A2'].contains(iv(parent['A2'])),'FULL_A2')
        need(p['mu3'].overlap(-270*p['k']) and p['k'].lo>0,'MU3_K')
        # For launch reconstruction use the inherited E interval for both engines.
        z=initial if name=='primary' else initial[:4]+[raw[4]]+initial[4:]
        _,H,Phi,T,E=z[:5];tp=p['m2']*Phi-4*H*T
        d=2+270*p['k']*E*E;need(d.lo>0,'D3_POSITIVE')
        gamma=21-I(1)/d;B=gamma*T/2-tp;need(not B.zero(),'B3_NONZERO')
        need(B.overlap(iv(data['launch']['launch_divisor'])),'B3_RECONSTRUCTION')
        load=iv(data['launch']['R3_lower']);need(load.contains(iv(system['per_engine'][name]['lower']['R3'])),'BOUND_LOWER_LOAD')
        source=sc3(z,p);need(source.overlap(iv(system['per_engine'][name]['lower']['Sc3'])),'QUALIFIED_SC3')
        for label,j,expected,forcing,wall_load in (('particular',14,I(0),source,load),('homogeneous',17,I(1),I(0),I(0)):
            a,f,g=z[j:j+3];need(equal(a,expected),'LAUNCH_NORMALIZATION:'+label)
            rebuilt_f=(forcing-T*wall_load/2+3*(p['mu3']+4*p['k'])*E*E*a)/B
            rebuilt_g=gamma*f/2+wall_load/2-2*T*a
            need(f.overlap(rebuilt_f) and g.overlap(rebuilt_g),'LAUNCH_RECONSTRUCTION:'+label)
            need((2*(g+2*T*a)-gamma*f-wall_load).zero(),'ROBIN_ZERO:'+label)
            need((T*g-tp*f+(2*T*T+798*p['k']*E*E)*a-forcing).zero(),'CUBIC_CONSTRAINT_ZERO:'+label)
            need(iv(data['launch']['rows'][label]).zero(),'RECORDED_ROBIN_ZERO:'+label)
        previous=initial;max_iterations=0;max_widths=[F(0)]*dimension
        constraint_names={'first','third_particular','third_homogeneous'}|({'second_particular','second_homogeneous'} if name=='primary' else {'particular','homogeneous'})
        for index,cell in enumerate(data['records']):
            need(cell['index']==index,'CELL_INDEX')
            start,end,box,rhs=[list(map(iv,cell[key])) for key in ('start','end','box','rhs_box')]
            coefficients=[list(map(iv,row)) for row in cell['point_coefficients']]
            remainder=list(map(iv,cell['remainder_coefficient']))
            need(all(len(v)==dimension for v in (start,end,box,rhs,coefficients,remainder)),'CELL_DIMENSION')
            need(all(equal(a,b) for a,b in zip(start,previous)),'EXACT_CHAIN')
            iterations=cell['picard_iterations'];need(isinstance(iterations,int) and 1<=iterations<=32,'PICARD_ITERATIONS')
            max_iterations=max(max_iterations,iterations)
            for j in range(dimension):
                max_widths[j]=max(max_widths[j],box[j].hi-box[j].lo)
                candidate=start[j]+I(0,step)*rhs[j]
                need(box[j].lo<candidate.lo and candidate.hi<box[j].hi,'STRICT_PICARD')
                row=coefficients[j];need(len(row)==5 and equal(row[0],start[j]),'POINT_COEFFICIENTS')
                endpoint=remainder[j]
                for coefficient in reversed(row):endpoint=endpoint*step+coefficient
                need(end[j].contains(endpoint),'OUTWARD_TAYLOR_ENDPOINT')
            need(set(cell['constraints'])==constraint_names,'CONSTRAINT_INVENTORY')
            need(all(iv(v).zero() for v in cell['constraints'].values()),'RECORDED_CONSTRAINT_ZERO')
            need(iv(cell['background']).zero(),'RECORDED_BACKGROUND_ZERO');previous=end
        need(all(equal(a,b) for a,b in zip(previous,final)),'EXACT_FINAL_CHAIN')
        need(data['max_picard_iterations']==max_iterations,'MAX_ITERATIONS')
        need(list(map(F,data['max_box_widths']))==max_widths,'EXACT_MAX_BOX_WIDTHS')
        output=list(map(iv,data['physical_final']));need(len(output)==20,'PHYSICAL_DIMENSION')
        if name=='primary':need(all(equal(a,b) for a,b in zip(output,final)),'PRIMARY_PHYSICAL_MAPPING')
        else:
            need(all(equal(a,b) for a,b in zip(output[:4]+output[5:],final)),'INDEPENDENT_PHYSICAL_MAPPING')
            need(output[4].lo>0,'POSITIVE_SAVED_EXP_MINUS_W')
        physical[name]=output
        reports[name]={'cells_checked':count,'components_per_cell':dimension,'step':str(step),'interval_length':'1/64','max_picard_iterations':max_iterations,'Sc3_reconstructed':source.record()}
    need(all(a.overlap(b) for a,b in zip(physical['primary'],physical['independent'])),'PHYSICAL_ENGINE_OVERLAP')
    return {'pass':True,'classification':'CUBIC_PROBE_SAVED_CERTIFICATES_VERIFIED','engines':reports,
            'scope':'Exact Fraction audit of recorded strict Picard inclusions, Taylor endpoint enclosures, chains, inherited launch data and cubic Robin/constraint assembly. RHS boxes, derivative/remainder coefficients and recorded constraint values are authenticated producer witnesses, not independently re-evaluated here. Independent E=exp(-W) export is checked for positivity and cross-engine overlap, not independently exponentiated. No full-domain flow, A3 or d_sep3 claim.'}
