"""Independent exact terminal audit of retained Dirichlet bisection records."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,datetime,time
P=Path(__file__).resolve().parent
started=time.monotonic()
def read(n): return json.loads((P/n).read_text())
def sha(n): return hashlib.sha256((P/n).read_bytes()).hexdigest()
def iv(x):
    a,b=map(Q,x['exact_bounds']); assert a<=b
    return a,b
def sign(x): return 1 if x[0]>0 else -1 if x[1]<0 else 0
for gate_name in ('INDEPENDENT_GATE.json','DIRICHLET_GATE.json'):
    gate=read(gate_name); assert gate['decision']=='APPROVED_FOR_ONE_BOUNDED_EXECUTION'
    for n,h in gate['frozen_hashes'].items(): assert sha(n)==h,n
for n,h in read('DIRICHLET_BINDINGS.json')['files'].items(): assert sha(n)==h,n
for n,r in read('SOURCE_BINDINGS.json')['files'].items(): assert sha(n)==r['sha256'],n
spec=read('DIRICHLET_SPEC.json'); result=read('output_dirichlet/RESULT.json')
run=read('EXECUTION_dirichlet.json')
assert run['exit_code']==0 and not run['timed_out'] and run['admitted']
assert run['cpu'] not in set(run['held'])|set(run['excluded'])
assert len(set(run['held'])|set(run['excluded'])|{run['cpu']})<=10
assert result['elapsed_seconds']<spec['production_seconds_max']
assert read('output_dirichlet/STARTED.json')['gate_sha256']==sha('DIRICHLET_GATE.json')
bracket=tuple(map(Q,spec['initial_mu'])); D=tuple(map(Q,read('inputs/central_bindings.json')['config']['D']))
for e in ('primary','independent'):
    for label,mass,want in [('finite_lower',bracket[0],1),('high',bracket[1],-1)]:
        rec=read('output/'+label+'_'+e+'.json')
        assert Q(rec['mu_exact'])==mass and sign(iv(rec['event']['f']))==want
        assert iv(result['initial_endpoint_records'][label+'_'+e])==iv(rec['event']['f'])
signs_seen=[]; count=0
assert len(result['attempts'])<=spec['max_attempts']
for i,attempt in enumerate(result['attempts'],1):
    assert bracket[1]-bracket[0]>Q(spec['target_width'])
    assert attempt['attempt']==i and tuple(map(Q,attempt['before']))==bracket
    mid=sum(bracket)/2; assert Q(attempt['midpoint_exact'])==mid
    signs=[]
    for e in ('primary','independent'):
        ref=attempt['engine_results'][e]; name='output_dirichlet/'+ref['path']
        assert sha(name)==ref['sha256']; rec=read(name); count+=1
        assert rec['engine']==e and rec['label']==f'mid_{i:02d}' and Q(rec['mu_exact'])==mid
        h=Q(2,spec['steps'][e]); n=-(-D[1]//h)
        assert rec['cells']==n and rec['steps']==spec['steps'][e]
        assert rec['all_cell_checks_pass'] and rec['max_picard_iterations']>0
        assert rec['elapsed_seconds']<spec['flow_seconds_max']
        assert rec['source_sha256']==sha('engine/'+e+'_interval.py')
        expected=[j for j in range(n) if (j+1)*h>=D[0] and j*h<=D[1]]
        assert [r['index'] for r in rec['event_cover']]==expected
        last=D[0]; lo=None; hi=None
        for r in rec['event_cover']:
            a,b=Q(r['lo_exact']),Q(r['hi_exact']); j=r['index']
            assert a==last==max(D[0],j*h) and b==min(D[1],(j+1)*h) and a<=b
            last=b; v=iv(r['f']); lo=v[0] if lo is None else min(lo,v[0]); hi=v[1] if hi is None else max(hi,v[1])
        assert last==D[1]
        event=iv(rec['event']['f']); assert event[0]<=lo<=hi<=event[1]
        s=sign(event); assert s==ref['sign'] and s!=0; signs.append(s)
    assert signs[0]==signs[1] and attempt['admitted']
    bracket=(mid,bracket[1]) if signs[0]>0 else (bracket[0],mid)
    assert tuple(map(Q,attempt['after']))==bracket
    signs_seen.append(signs[0])
assert count==12 and signs_seen==[-1,-1,1,-1,-1,-1]
assert tuple(map(Q,result['mu_D_bracket']))==bracket
width=bracket[1]-bracket[0]
assert width==Q(result['width_exact'])==Q(1,32000000)
assert width<=Q(spec['target_width']) and result['target_pass']
assert result['stop_reason']=='TARGET_REACHED'
original=tuple(map(Q,read('inputs/narrowing_result.json')['mu_bracket']))
finite=read('output/RESULT.json'); q=Q(finite['eta100_mu_bracket'][0])
total=bracket[0]-original[1],bracket[1]-original[0]
remaining=Q(0),bracket[1]-q
fraction=Q(finite['strict_displacement_lower_exact'])/total[1]
assert tuple(map(Q,result['total_gain_strict_bounds']))==total
assert tuple(map(Q,result['remaining_gain_strict_bounds']))==remaining
assert Q(result['achieved_fraction_strict_lower'])==fraction==Q(6,25)
assert total[1]<Q(spec['max_total_gain_upper'])
assert result['classification']=='QUANTIFIED_SATURATION'
controls=result['controls']; assert len(controls)==3 and controls[0]['pass']
assert controls[1]['rejected_by']=='DENOMINATOR_NONZERO' and controls[2]['rejected_by']=='EVENT_GAP'
assert time.monotonic()-started<180
print(json.dumps({'status':'INDEPENDENT_EXACT_RECONSTRUCTION_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner_result_sha256':sha('output_dirichlet/RESULT.json'),'gate_sha256':sha('DIRICHLET_GATE.json'),'execution_sha256':sha('EXECUTION_dirichlet.json'),'audit_script_sha256':sha('audit_dirichlet.py'),'flow_count':count,'midpoint_signs':signs_seen,'mu_D_strict_bounds':list(map(str,bracket)),'width_exact':str(width),'total_gain_strict_bounds':list(map(str,total)),'remaining_gain_strict_bounds':list(map(str,remaining)),'achieved_fraction_strict_lower':str(fraction),'elapsed_seconds':time.monotonic()-started,'limitation':'Exact output arithmetic and stored qualification audited; no interval ODE rerun and original validity premises inherited.'},indent=2))
