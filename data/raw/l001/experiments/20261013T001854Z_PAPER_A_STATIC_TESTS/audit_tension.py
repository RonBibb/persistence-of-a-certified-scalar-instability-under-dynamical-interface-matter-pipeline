"""Reviewer exact reconstruction, independent of owner test and numerical producer."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

P=Path(__file__).resolve().parent
T=P/'tension_inputs'

def load(path): return json.loads(path.read_text())
def pair(xs):
    a,b=map(F,xs)
    assert a<=b
    return a,b
def bounds(r): return pair(r['exact_bounds'])

def main():
    for row in load(P/'TENSION_SOURCE_BINDINGS.json')['files']:
        raw=(P/row['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
        assert raw==(P.parent/row['origin_relative_to_experiments']).read_bytes()
    result=load(T/'RESULT.json'); root=load(T/'flows/uniform_root/RESULT.json'); center=load(T/'flows/uniform_center/RESULT.json')
    binding=load(T/'BINDINGS.json'); transport=load(T/'D2A_TRANSPORT.json'); parent=load(T/'d2a_parent.json')
    model=binding['exact_model']; n=result['neighborhood']; rq=root['event']['event_quantities'];cq=center['event']['event_quantities']
    baseline=F(-851862101055633,140737488355328); width=F(1,1000000)
    assert F(model['LAMBDA_B_Q'])==F(result['parameter']['baseline_exact'])==baseline
    assert pair(result['parameter']['delta_exact'])==(-width,width)==pair(binding['contract']['delta_exact'])
    intended=(baseline-width,baseline+width)
    assert pair(result['parameter']['tension_exact'])==intended==pair(binding['intended_tension_exact'])
    enclosure=bounds(result['parameter']['outward_tension_enclosure'])
    assert enclosure[0]<=intended[0]<=intended[1]<=enclosure[1]
    for saved in [root,center]:
        assert bounds(saved['tension_enclosure'])==enclosure
        assert saved['source_sha256']==hashlib.sha256((T/'run.py').read_bytes()).hexdigest()
        assert saved['guard']==result['guard']==hashlib.sha256((T/'FREEZE.json').read_bytes()).hexdigest()
    lo,hi=F(model['ROOT_LO_Q']),F(model['ROOT_HI_Q']); cp=F(model['ROOT_CENTER_Q'])
    assert pair(root['launch_exact'])==(lo,hi) and pair(center['launch_exact'])==(cp,cp)
    q=bounds(rq['q_a']);h=bounds(cq['h']);assert q[0]>0
    quotients=[x/y for x in h for y in q]
    newton=(cp-max(quotients),cp-min(quotients))
    assert lo<newton[0]<=newton[1]<hi and newton==bounds(n['newton_image'])
    gd,ga,hd,ha=[bounds(rq[k]) for k in ['G_s','G_a','h_s','h_a']]
    assert gd[1]<0 and min(ga[0],hd[0],ha[0])>0
    chain=(-gd[1]*q[0],-gd[0]*q[1])
    direct=(ga[0]*hd[0]-gd[1]*ha[0],ga[1]*hd[1]-gd[0]*ha[1])
    assert chain==bounds(n['determinant_chain']) and direct==bounds(n['determinant_direct'])
    det=(max(chain[0],direct[0]),min(chain[1],direct[1]));assert 0<det[0]<=det[1]
    da=(hd[0]/(6*det[1]),hd[1]/(6*det[0]))
    dd=(-ha[1]/(6*det[0]),-ha[0]/(6*det[1]))
    assert da==bounds(n['response']['da_dlambda_b']) and dd==bounds(n['response']['dD_dlambda_b'])
    assert da[0]>0 and dd[1]<0 and bounds(rq['curvature'])[0]>0
    parent_rows=parent['terminal_boxes'];target=transport['boxes'];assert len(parent_rows)==len(target)==693
    assert pair(transport['delta_exact'])==(-width,width)
    minimum=None;negative=0;endpoint=F(0)
    for index,(original,row) in enumerate(zip(parent_rows,target)):
        left,right=pair(original['a_exact_bounds'])
        assert left==endpoint and left<right;endpoint=right
        assert pair(row['a_exact'])==(left,right) and row['index']==index
        r=original['record'];k=pair(r['curvature_exact_bounds'])
        if k[1]<0:
            negative+=1
            assert row['kind']=='NEGATIVE_CURVATURE' and pair(row['k_exact'])==k
        else:
            g0=pair(r['G_exact_bounds']);g=(g0[0]-width/6,g0[1]+width/6);h0=pair(r['scalar_residual_exact_bounds'])
            assert row['kind']=='RESIDUAL_EXCLUSION' and pair(row['G_exact'])==g and pair(row['h_exact'])==h0
            distances=[F(0) if low<=0<=high else min(abs(low),abs(high)) for low,high in [g,h0]]
            margin=max(distances);assert margin>0 and F(row['lower_bound_exact'])==margin
            minimum=margin if minimum is None else min(minimum,margin)
    assert negative==20 and endpoint==F(3602879701896397,36028797018963968)
    assert transport['negative_curvature_boxes']==20 and transport['residual_boxes']==673
    assert minimum==F(transport['minimum_lower_bound_exact'])==F(result['fixed_separation']['minimum_lower_bound_exact'])>F(77,10000)
    assert not transport['unresolved'] and not result['fixed_separation']['unresolved']
    owner=load(P/'runs/tension.stdout.json')
    assert owner['status']=='PASS' and owner['baseline']['pass'] and not owner['baseline']['failed_predicates']
    assert len(owner['semantic_negative_controls'])==7
    for c in owner['semantic_negative_controls']:
        assert c['rejected_for_targeted_reason'] and c['expected_failed_predicate'] in c['failed_predicates']
    print(json.dumps({'status':'PASS','independent_implementation':True,'newton_determinants_and_response_exact_match':True,'da_display':list(map(float,da)),'dD_display':list(map(float,dd)),'transport_rows':693,'negative_curvature_boxes':negative,'residual_boxes':693-negative,'minimum_margin_display':float(minimum),'semantic_controls_checked':7,'provenance_premise':'Uniform-flow snapshots have cross-consistent guards, not separately established prior terminal authentication; comparison authenticates the reconstructed outputs only.'},indent=2))

if __name__=='__main__':main()
