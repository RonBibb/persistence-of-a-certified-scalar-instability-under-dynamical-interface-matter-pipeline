"""Independent streaming exact saved-witness audit, not an ODE replay."""
import hashlib,importlib.util,json,sys
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
SYSTEM=ROOT.parent/'20261026T025505Z_CUBIC_SYSTEM'
PROBE=ROOT.parent/'20261026T033000Z_CUBIC_PROBE_R1'
def need(value,label):
    if not value:raise AssertionError(label)
def read(path):return json.loads(Path(path).read_text())
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def initialize():
    global I
    spec=importlib.util.spec_from_file_location('full_flow_exact_interval',PARENT/'terminal_audit/audit.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);I=module.I
setup=initialize
def iv(value):return I(*value['exact_bounds'])
def equal(a,b):return a.lo==b.lo and a.hi==b.hi
def vector_equal(a,b):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
def power(value,n):
    out=I(1)
    for _ in range(n):out=out*value
    return out
def polynomial_range(cell,lo,hi):
    out=[];dt=I(lo,hi)
    for row,rem in zip(cell['point_coefficients'],cell['remainder_coefficient']):
        value=iv(rem)
        for coefficient in reversed(row):value=value*dt+iv(coefficient)
        out.append(value)
    return out
def check_cell(cell,previous,index,dimension,step,name):
    need(cell['index']==index,'CELL_INDEX')
    start,end,box,rhs=[list(map(iv,cell[key])) for key in ('start','end','box','rhs_box')]
    need(all(len(v)==dimension for v in (start,end,box,rhs,cell['point_coefficients'],cell['remainder_coefficient'])),'CELL_DIMENSIONS')
    need(vector_equal(start,previous),'EXACT_CHAIN')
    need(isinstance(cell['picard_iterations'],int) and 1<=cell['picard_iterations']<=32,'PICARD_ITERATIONS')
    for j in range(dimension):
        candidate=start[j]+I(0,step)*rhs[j]
        need(box[j].lo<candidate.lo and candidate.hi<box[j].hi,'STRICT_PICARD')
        row=cell['point_coefficients'][j]
        need(len(row)==5 and equal(iv(row[0]),start[j]),'POINT_COEFFICIENTS')
    need(all(a.contains(b) for a,b in zip(end,polynomial_range(cell,step,step))),'OUTWARD_TAYLOR_ENDPOINT')
    keys={'first','third_particular','third_homogeneous'}|({'second_particular','second_homogeneous'} if name=='primary' else {'particular','homogeneous'})
    need(set(cell['constraints'])==keys,'CONSTRAINT_INVENTORY')
    need(all(iv(v).zero() for v in cell['constraints'].values()),'RECORDED_CONSTRAINT_ZERO')
    need(iv(cell['background']).zero(),'RECORDED_BACKGROUND_ZERO')
    return end,[v.hi-v.lo for v in box]
def sc3(z,p):
    _,H,Phi,T,E,a,f,g,ap,fp,gp,ah,fh,gh=z[:14]
    values=dict(H=H,Phi=Phi,T=T,e=E*E,p=a,f=f,g=g,P=ap+ah*p['A2'],F=fp+fh*p['A2'],G=gp+gh*p['A2'],m=p['m2'])
    system=read(SYSTEM/'RESULT.json');total=I(0);names=system['bulk']['variables']
    for term in system['bulk']['sources']['Sc3']:
        need(len(term['powers'])==len(names),'POLYNOMIAL_DIMENSION');value=I(F(term['coefficient']))
        for name,n in zip(names,term['powers']):
            need(isinstance(n,int) and n>=0,'NONNEGATIVE_POWER')
            if name=='h':need(n%2==0,'EVEN_H_POWER');value=value*power(p['k'],n//2)
            else:value=value*power(values[name],n)
        total=total+value
    return total
def check_launch(name,initial,params,launch):
    parent=read(PARENT/('PRODUCTION_'+name+'.json'));raw=list(map(iv,parent['raw_lower']))
    need(list(map(F,launch['D']))==list(map(F,parent['inputs']['D'])),'FULL_PARENT_DOMAIN')
    need(len(raw)==14,'PARENT_DIMENSION');old=raw if name=='primary' else raw[:4]+raw[5:]
    need(all(a.contains(b) for a,b in zip(initial,old)),'FULL_PARENT_INITIAL')
    for key,value in parent['parameters'].items():need(params[key].contains(iv(value)),'PARAMETER:'+key)
    need(params['A2'].contains(iv(parent['A2'])),'FULL_A2')
    need(params['mu3'].overlap(-270*params['k']) and params['k'].lo>0,'MU3_K')
    z=initial if name=='primary' else initial[:4]+[raw[4]]+initial[4:]
    _,H,Phi,T,E=z[:5];tp=params['m2']*Phi-4*H*T
    d=2+270*params['k']*E*E;need(d.lo>0,'D3_POSITIVE');gamma=21-I(1)/d;B=gamma*T/2-tp
    need(not B.zero() and B.overlap(iv(launch['launch_divisor'])),'B3_NONZERO_RECONSTRUCTION')
    load=iv(launch['R3_lower']);bound=read(SYSTEM/'RESULT.json')['per_engine'][name]['lower']
    need(load.contains(iv(bound['R3'])),'BOUND_LOWER_LOAD');source=sc3(z,params)
    need(source.overlap(iv(bound['Sc3'])),'QUALIFIED_SC3')
    for label,j,expected,forcing,wall_load in (('particular',14,I(0),source,load),('homogeneous',17,I(1),I(0),I(0))):
        a,f,g=z[j:j+3];need(equal(a,expected),'LAUNCH_NORMALIZATION')
        rebuilt_f=(forcing-T*wall_load/2+3*(params['mu3']+4*params['k'])*E*E*a)/B
        need(f.overlap(rebuilt_f) and g.overlap(gamma*f/2+wall_load/2-2*T*a),'LAUNCH_RECONSTRUCTION')
        need((2*(g+2*T*a)-gamma*f-wall_load).zero(),'LAUNCH_ROBIN')
        need((T*g-tp*f+(2*T*T+798*params['k']*E*E)*a-forcing).zero(),'LAUNCH_CONSTRAINT')
        need(iv(launch['rows'][label]).zero(),'RECORDED_LAUNCH_ROW')
    return z
def run():
    need(sys.platform=='linux','LINUX_ONLY');initialize()
    binding=sha(ROOT/'FROZEN.json');result=read(ROOT/'RESULT.json')
    need(result['pass'] and result['full_distance_computed'] is False,'RESULT_SCOPE')
    controls=read(ROOT/'CONTROLS_RESULT.json');need(controls['pass'] and len(controls['checks'])==151,'CONTROLS')
    reports={};uppers={};amplitudes={}
    for name,dimension,step in (('primary',20,F(1,4096)),('independent',19,F(1,8192))):
        data=read(ROOT/('FLOW_'+name+'.json'));anchor=read(PROBE/('PROBE_'+name+'.json'))
        need(data['pass'] and data['engine']==name and F(data['step'])==step,'ENGINE')
        dlo,dhi=map(F,data['D']);need(0<dlo<=dhi,'DOMAIN')
        need(list(map(F,data['launch']['D']))==[dlo,dhi],'LAUNCH_DOMAIN')
        count=-((-dhi)//step);need(data['cells']==count,'CELL_COUNT')
        params={k:iv(v) for k,v in data['parameters'].items()}
        ph=hashlib.sha256(json.dumps(data['parameters'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        need(data['parameters_sha256']==ph,'PARAMETER_HASH')
        initial=list(map(iv,data['initial']));need(len(initial)==dimension,'INITIAL_DIMENSION')
        lower=check_launch(name,initial,params,data['launch'])
        previous=initial;previous_hash=None;next_index=0;maxpic=0;maxwidth=[F(0)]*dimension
        cover=[];events=[];anchored=False
        for entry in data['chunks']:
            path=ROOT/entry['file'];need(path.resolve().is_relative_to(ROOT.resolve()),'CHUNK_PATH')
            need(sha(path)==entry['sha256'],'CHUNK_HASH');chunk=read(path)
            need(chunk['engine']==name and chunk['binding_sha256']==binding and chunk['parameters_sha256']==ph,'CHUNK_BINDING')
            need(chunk['previous_sha256']==previous_hash,'CHUNK_CHAIN')
            records=chunk['records'];need(1<=len(records)<=32,'CHUNK_SIZE')
            need(entry['first']==chunk['first']==next_index and entry['last']==chunk['last']==next_index+len(records)-1,'CHUNK_INDICES')
            for cell in records:
                previous,width=check_cell(cell,previous,next_index,dimension,step,name)
                maxpic=max(maxpic,cell['picard_iterations']);maxwidth=[max(a,b) for a,b in zip(maxwidth,width)]
                if next_index+1==anchor['cells']:
                    need(cell['end']==anchor['final'],'BITWISE_PROBE_ANCHOR');anchored=True
                pos=step*next_index;intersects=pos+step>=dlo and pos<=dhi
                need(('event' in cell)==intersects,'COMPLETE_EVENT_INVENTORY')
                if intersects:
                    event=cell['event'];lo,hi=F(event['offset_lo']),F(event['offset_hi'])
                    need(lo==max(F(0),dlo-pos) and hi==min(step,dhi-pos),'EVENT_CLIP')
                    raw=list(map(iv,event['raw']));physical=list(map(iv,event['physical']))
                    need(len(raw)==dimension and len(physical)==20,'EVENT_DIMENSION')
                    need(all(a.contains(b) for a,b in zip(raw,polynomial_range(cell,lo,hi))),'EVENT_TAYLOR_ENCLOSURE')
                    mapped=physical if name=='primary' else physical[:4]+physical[5:]
                    need(vector_equal(mapped,raw) and physical[4].lo>0,'EVENT_PHYSICAL_MAPPING')
                    events.append(physical);cover.append({'index':next_index,'lo':str(pos+lo),'hi':str(pos+hi)})
                next_index+=1
            cp_path=ROOT/entry['checkpoint'];need(cp_path.resolve().is_relative_to(ROOT.resolve()),'CHECKPOINT_PATH')
            need(sha(cp_path)==entry['checkpoint_sha256'],'CHECKPOINT_HASH');cp=read(cp_path)
            need(cp['engine']==name and cp['binding_sha256']==binding and cp['parameters_sha256']==ph,'CHECKPOINT_BINDING')
            need(cp['chunk_sha256']==entry['sha256'] and cp['completed']==next_index and cp['total']==count,'CHECKPOINT_POSITION')
            need(cp['resume_supported'] is False and vector_equal(list(map(iv,cp['state'])),previous),'CHECKPOINT_STATE')
            previous_hash=entry['sha256']
        need(next_index==count and anchored and data['anchor_pass'],'COMPLETE_CHAIN')
        need(vector_equal(previous,list(map(iv,data['final']))),'FINAL_STATE')
        need(list(map(F,data['max_box_widths']))==maxwidth and data['max_picard_iterations']==maxpic,'WIDTH_ITERATION_STATS')
        need(data['cover']==cover and events,'COVER_RECORD');edge=dlo
        for piece in cover:need(F(piece['lo'])==edge,'COVER_GAP');edge=F(piece['hi'])
        need(edge==dhi,'COVER_END')
        upper=list(map(iv,data['physical_upper']));need(len(upper)==20,'UPPER_DIMENSION')
        for j in range(20):need(upper[j].contains(I(min(v[j].lo for v in events),max(v[j].hi for v in events))),'OUTWARD_UPPER_HULL')
        parent=read(PARENT/('PRODUCTION_'+name+'.json'))
        need(all(a.overlap(iv(b)) for a,b in zip(upper[:14],parent['raw_upper'])),'LOWER_ORDER_PARENT_REPLAY')
        matching=data['matching'];T,E=upper[3:5];d=2+270*params['k']*E*E;need(d.lo>0,'UPPER_D3')
        gamma=21-I(1)/d;fp=upper[16]+2*T*upper[14]+gamma*upper[15]/2;fh=upper[19]+2*T*upper[17]+gamma*upper[18]/2
        need(gamma.overlap(iv(matching['Gamma3'])) and fp.overlap(iv(matching['FP3'])) and fh.overlap(iv(matching['FH3'])),'UPPER_MATCHING_RECONSTRUCTION')
        load=iv(matching['R3_upper']);need(load.contains(iv(read(SYSTEM/'RESULT.json')['per_engine'][name]['upper']['R3'])),'UPPER_LOAD_BINDING')
        saved_fh=iv(matching['FH3']);need(matching['resolved']==(not saved_fh.zero()),'RESOLUTION_FLAG')
        if matching['resolved']:
            need(not fh.zero(),'RECONSTRUCTED_FH_NONZERO');A=iv(matching['A3'])
            need(A.overlap((-load/2-fp)/fh),'A3_RECONSTRUCTION');amplitudes[name]=A
            for side,z,sign,R in (('lower',lower,-1,iv(data['launch']['R3_lower'])),('upper',upper,1,-load)):
                state=[z[j]+A*z[j+3] for j in (14,15,16)];saved=matching[side]
                need(len(saved['state'])==3 and all(a.overlap(iv(b)) for a,b in zip(state,saved['state'])),'SAME_A3_STATE')
                a,f,g=state;T,E=z[3:5];tp=params['m2']*z[2]-4*z[1]*T;gamma=21-I(1)/(2+270*params['k']*E*E)
                robin=2*(g+2*T*a)+sign*gamma*f-R
                constraint=T*g-tp*f+(2*T*T+798*params['k']*E*E)*a-sc3(z,params)
                for key,value in (('robin',robin),('constraint',constraint)):
                    need(value.zero() and iv(saved[key]).zero() and value.overlap(iv(saved[key])),'MATCHED_ROW:'+side+key)
        else:need('A3' not in matching,'NO_UNRESOLVED_DIVISION')
        uppers[name]=upper;reports[name]={'cells':count,'chunks':len(data['chunks']),'endpoint_cover_pieces':len(cover),'inverse_resolved':matching['resolved']}
    need(all(a.overlap(b) for a,b in zip(uppers['primary'],uppers['independent'])),'ENGINE_UPPER_OVERLAP')
    resolved=len(amplitudes)==2
    need(result['classification']==('CUBIC_FULL_FLOW_UPPER_INVERSE_RESOLVED' if resolved else 'CUBIC_FULL_FLOW_UPPER_INVERSE_UNRESOLVED'),'CLASSIFICATION')
    if resolved:
        a,b=amplitudes.values();need(a.overlap(b),'A3_ENGINE_OVERLAP')
        need(iv(result['A3_hull']).contains(I(min(a.lo,b.lo),max(a.hi,b.hi))),'OUTWARD_A3_HULL')
    return {'pass':True,'classification':'CUBIC_FULL_FLOW_SAVED_CERTIFICATES_VERIFIED','engines':reports,
            'scope':'Streaming exact saved-witness audit of Picard/Taylor enclosures, authenticated chain/checkpoints, complete uncertain-endpoint cover and matching algebra. Does not independently re-evaluate RHS or derivative/constraint witnesses, or exponentiate direct-W exports. No complete proper-distance coefficient or finite-amplitude claim.'}
