"""Reviewer central-mode saved proof audit using inverse-positive exponential bounds."""
from fractions import Fraction as F
from pathlib import Path
import math
import hashlib
import json

P=Path(__file__).resolve().parent
M=P/'mode_inputs'

def read(p):return json.loads(p.read_text())
def bounds(r):
    lo,hi=F(r['lo_exact']),F(r['hi_exact'])
    assert lo<=hi
    return lo,hi
def exp_negative(x):
    assert -8<x<=0
    y=-x
    terms=[y**k/F(math.factorial(k)) for k in range(49)]
    lower_positive=sum(terms,F(0))
    assert y/50<1
    upper_positive=lower_positive+(terms[-1]*y/49)/(1-y/50)
    return 1/upper_positive,1/lower_positive

def main():
    for row in read(P/'MODE_SOURCE_BINDINGS.json')['files']:
        raw=(P/row['path']).read_bytes()
        assert raw==(P.parent/row['origin_relative_to_experiments']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
    result=read(M/'output/RESULT.json');accepted=read(M/'RESULT.json');old_audit=read(M/'INDEPENDENT_AUDIT.json')
    assert accepted['independently_accepted'] and old_audit['audit_pass'] and result['producer_provisional_pending_audit']
    assert accepted['artifacts']['output/RESULT.json']==old_audit['result_sha256']==hashlib.sha256((M/'output/RESULT.json').read_bytes()).hexdigest()
    assert accepted['artifacts']['INDEPENDENT_AUDIT.json']==hashlib.sha256((M/'INDEPENDENT_AUDIT.json').read_bytes()).hexdigest()
    mu=(-F(33,25000),-F(131,100000));d=(F(32727,16384),F(32729,16384))
    a=(F(456607025194779413,4611686018427387904),F(114151756532473697,1152921504606846976))
    assert tuple(map(F,result['config']['mu']))==tuple(map(F,accepted['mu_open_interval']))==mu
    assert tuple(map(F,result['config']['D']))==d and tuple(map(F,result['config']['A']))==a
    tasks=result['tasks'];assert [t['task'] for t in tasks]==['primary_low','primary_high','independent_low','independent_high','primary_strip','independent_strip']
    signs=[];strip_summary=[]
    for t in tasks:
        steps=8192 if t['task'].startswith('primary') else 16384
        cell_width=F(2,steps);needed=math.ceil(d[1]/cell_width)
        assert t['cells']==needed
        expected=[]
        for j in range(needed):
            start=j*cell_width;end=start+cell_width
            if end>=d[0] and start<=d[1]:expected.append({'index':j,'s_exact':str(start),'lo_exact':str(max(start,d[0])),'hi_exact':str(min(end,d[1]))})
        assert expected==t['event_cover']
        k=bounds(t['K']);b=bounds(t['B0']);sector=bounds(t['sector'])
        assert k[0]>0 and (b[1]<0 or b[0]>0)
        assert sector[0]<=mu[0]+4*k[0]<=mu[1]+4*k[1]<=sector[1]<0
        if not t['task'].endswith('strip'):
            low,high=bounds(t['determinant']);assert low>0 or high<0
            signs.append(1 if low>0 else -1)
        else:
            psi=bounds(t['extrema']['psi']);w=bounds(t['extrema']['W']);assert psi[0]>0
            e=exp_negative(2*w[0]);norm=tuple(12*d[0]*psi[0]**2*x for x in e)
            assert norm[0]>F(437,1000)
            z=bounds(t['Z_lower_bound']);assert max(norm[0],z[0])<=min(norm[1],z[1])
            displacement=(-2*d[1]*psi[1],-2*d[0]*psi[0]);saved=bounds(t['deltaD_bound'])
            assert saved[0]<=displacement[0]<=displacement[1]<=saved[1]<0
            assert -219<displacement[0] and displacement[1]<-F(1997,500)
            strip_summary.append({'task':t['task'],'norm_lower_display':float(norm[0]),'displacement_display':list(map(float,displacement))})
    assert signs==[1,-1,1,-1]
    for left,right in [(tasks[0],tasks[2]),(tasks[1],tasks[3])]:
        one,two=bounds(left['determinant']),bounds(right['determinant']);assert max(one[0],two[0])<=min(one[1],two[1])
    owner=read(P/'runs/mode.stdout.json');assert owner['status']=='PASS' and owner['baseline']['pass'] and not owner['baseline']['failures']
    assert len(owner['semantic_negative_controls'])==6
    for c in owner['semantic_negative_controls']:
        assert c['rejected_for_targeted_reason'] and c['expected_failed_predicate'] in [f['check'] for f in c['failures']]
    print(json.dumps({'status':'PASS','method':'Positive exponential degree48 plus geometric tail and reciprocal; independent of owner alternating negative degree64/65 sums','endpoint_signs':signs,'strip_bounds':strip_summary,'semantic_controls_checked':6,'inputs_unchanged':True},indent=2))

if __name__=='__main__':main()
