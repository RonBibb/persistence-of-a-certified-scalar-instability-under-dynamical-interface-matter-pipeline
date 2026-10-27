"""Independent sign/history/event and coefficient audit; no producer imports."""
import hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
P=Path(__file__).resolve().parent
def read(n): return json.loads((P/n).read_text())
def sha(n): return hashlib.sha256((P/n).read_bytes()).hexdigest()
def iv(r): return tuple(map(F,r['exact_bounds'])) if 'exact_bounds' in r else (F(r['lo_exact']),F(r['hi_exact']))
def mul(a,b):
    z=[x*y for x in a for y in b]; return min(z),max(z)
def square(a): return (F(0) if a[0]<=0<=a[1] else min(x*x for x in a),max(x*x for x in a))
def divide(a,b):
    assert b[1]<0 or b[0]>0
    return mul(a,(1/b[1],1/b[0]))
def sign(a): return 1 if a[0]>0 else -1 if a[1]<0 else 0
gate=read('INDEPENDENT_GATE.json'); spec=read('TEST_SPEC.json')
for n,h in gate['frozen_hashes'].items(): assert sha(n)==h
for n,r in read('SOURCE_BINDINGS.json')['files'].items(): assert sha(n)==r['sha256']
execution=read('EXECUTION_owner.json'); assert execution['exit_code']==0 and not execution['timed_out'] and execution['cpu']==0
start=read('output/STARTED.json'); assert start['runtime']==read('RUNTIME_BINDINGS.json') and start['gate_sha256']==sha('INDEPENDENT_GATE.json')
r=read('output/RESULT.json'); binding=read('inputs/central_bindings.json'); D=tuple(map(F,binding['config']['D']))
bracket=tuple(map(F,spec['initial_mu'])); assert binding['config']['mu']==spec['initial_mu']
for engine in ('primary','independent'):
    for side,sig in [('low',1),('high',-1)]: assert sign(iv(read('inputs/'+engine+'_'+side+'.json')['determinant']))==sig
assert len(r['attempts'])<=spec['max_attempts']
flows=0
for index,a in enumerate(r['attempts'],1):
    assert a['attempt']==index and tuple(map(F,a['before']))==bracket
    assert bracket[1]-bracket[0]>F(spec['target_width'])
    mid=(bracket[0]+bracket[1])/2; assert F(a['midpoint_exact'])==mid
    signs=[]
    for engine in ('primary','independent'):
        info=a['engine_results'][engine]; name='output/'+info['record']; assert sha(name)==info['sha256']
        f=read(name); assert f['engine']==engine and f['attempt']==index and F(f['mu_exact'])==mid
        assert f['source_sha256']==sha('engine/'+engine+'_interval.py')
        steps=spec['steps'][engine]; assert f['steps']==steps and f['cells']==math.ceil(D[1]*steps/2)
        assert f['all_cell_finite_constraint_first_integral_warp_checks_pass'] and 1<=f['max_picard_iterations']<=10
        assert f['elapsed_seconds']<=spec['flow_seconds_max']+1
        previous=D[0]; cells=[]
        for cell in f['event_cover']:
            lo,hi=F(cell['lo_exact']),F(cell['hi_exact']); j=cell['index']; h=F(2,steps)
            assert lo==previous and lo==max(D[0],j*h) and hi==min(D[1],(j+1)*h) and lo<=hi
            previous=hi; cells.append(iv(cell['determinant']))
        assert previous==D[1]
        det=iv(f['determinant']); assert det[0]<=min(x[0] for x in cells) and det[1]>=max(x[1] for x in cells)
        sig=sign(det); assert sig==info['sign'] and sig!=0; signs.append(sig); flows+=1
    assert signs[0]==signs[1] and a['admitted']
    bracket=(mid,bracket[1]) if signs[0]>0 else (bracket[0],mid)
    assert tuple(map(F,a['after']))==bracket
assert tuple(map(F,r['mu_bracket']))==bracket and F(r['mu_width_exact'])==bracket[1]-bracket[0]
assert bracket[1]-bracket[0]<=F(spec['target_width']) and r['target_pass'] and r['stop_reason']=='TARGET_REACHED'
saved=read('inputs/stiffness_result.json')['result']; beta=iv(saved['background']['bb']); per={}
for engine in ('primary','independent'):
    old=saved['engines'][engine]; k=iv(read('inputs/'+engine+'_strip.json')['K'])
    lam=(bracket[0]+4*k[0],bracket[1]+4*k[1]); assert lam[1]<0
    assert iv(r['coefficients']['engines'][engine]['lambda'])==lam
    three=(3*lam[0],3*lam[1]); Z=iv(old['Z']); B=iv(old['B0']); psi=iv(old['psi_b'])
    ca=divide(square(divide(three,B)),Z); cb=divide(square(divide(mul(three,psi),beta)),Z)
    per[engine]={'Ca':ca,'Cb':cb}
    for key,val in per[engine].items(): assert iv(r['coefficients']['engines'][engine][key])==val
summary={}
for key in ('Ca','Cb'):
    a=per['primary'][key]; b=per['independent'][key]; val=max(a[0],b[0]),min(a[1],b[1])
    assert 0<val[0]<=val[1] and iv(r['coefficients']['combined'][key])==val
    ratio=val[1]/val[0]; assert F(r['coefficients']['width_ratios_exact'][key])==ratio and ratio<=F(spec['max_coeff_width_ratio'])
    summary[key]=[float(x) for x in val]
assert r['outcome']=='SHARPENED' and r['coefficients']['both_width_ratios_pass']
assert r['coefficients']['unchanged_Cb_over_Ca']==saved['combined']['Cb_over_Ca']
assert len(r['controls'])==3 and r['controls'][0]['pass'] and all(c['control']==c['rejected_by'] for c in r['controls'][1:])
print(json.dumps({'status':'PASS','result_sha256':sha('output/RESULT.json'),'attempts':len(r['attempts']),
 'dual_flow_records':flows,'mu_bracket':list(map(str,bracket)),'combined_approximate':summary,
 'runtime_binding_scope':'Pinned runtime record and successful owner authentication; no local Linux library reread.',
 'outcome':'SHARPENED'},indent=2))
