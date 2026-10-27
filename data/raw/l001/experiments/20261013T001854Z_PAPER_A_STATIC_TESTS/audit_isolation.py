"""Reviewer sign-specialized endpoint arithmetic; no owner or producer imports."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent

def pair(value):
    result = tuple(Fraction(x) for x in value)
    assert len(result) == 2 and result[0] <= result[1]
    return result

def main():
    row = next(x for x in json.loads((P/'SOURCE_BINDINGS.json').read_text())['files'] if x['path']=='inputs/isolation.json')
    raw = (P/row['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    assert raw == (P.parent/'academic2-event-horizon'/row['source_relative_to_academic2_event_horizon']).read_bytes()
    data = json.loads(raw)
    owner = json.loads((P/'runs/isolation.stdout.json').read_text())
    output = {}
    brackets = []
    for producer,steps in [('primary',32768),('independent',16384)]:
        r = data[producer]
        gd,ga,hd,ha,qa = [pair(r[k]['exact_bounds']) for k in ['G_D','G_a','h_D','h_a','q_a_along_first_event']]
        assert gd[1] < 0 and min(ga[0],hd[0],ha[0],qa[0]) > 0
        chain = (-gd[1]*qa[0], -gd[0]*qa[1])
        direct = (ga[0]*hd[0]-gd[1]*ha[0], ga[1]*hd[1]-gd[0]*ha[1])
        for name,computed,saved_key in [('chain',chain,'jacobian_determinant_from_chain_rule'),('direct',direct,'jacobian_determinant_direct')]:
            lo,hi = pair(r[saved_key]['exact_bounds'])
            assert 0 < lo <= computed[0] <= computed[1] <= hi
            assert computed == pair(owner['baseline']['reconstructions'][producer][name+'_exact'])
        assert max(chain[0],direct[0]) <= min(chain[1],direct[1])
        assert pair(r['curvature']['exact_bounds'])[0] > 0
        for key in ['G','h']:
            lo,hi = pair(r[key]['exact_bounds'])
            assert lo <= 0 <= hi
        left,right = r['event_cells']
        assert 0 <= left <= right < steps-1 and r['steps']==steps
        assert r['negative_after_cell']==right+1 and r['obstruction'] is None
        bracket = pair(r['event_bracket_exact'])
        assert bracket==(Fraction(left,steps//2),Fraction(right+1,steps//2))
        brackets.append(bracket)
        output[producer]={'chain_display':list(map(float,chain)),'direct_display':list(map(float,direct)),'exact_owner_endpoints_match':True,'archived_outward_containment':True}
    intersection=(max(x[0] for x in brackets),min(x[1] for x in brackets))
    assert intersection[0]<=intersection[1]
    assert intersection==pair(data['cross_producer']['event_bracket_intersection_exact'])
    assert owner['status']=='PASS' and owner['baseline']['pass'] and not owner['baseline']['failures']
    assert len(owner['semantic_negative_controls'])==6
    for c in owner['semantic_negative_controls']:
        assert c['rejected_for_targeted_reason'] and c['expected_failed_predicate'] in [f['check'] for f in c['failures']]
    print(json.dumps({'status':'PASS','method':'sign-specialized exact endpoint formulas independent of owner four-corner implementation','reconstructions':output,'event_intersection_exact':list(map(str,intersection)),'semantic_controls_verified':6,'input_unchanged':True},indent=2))

if __name__=='__main__':
    main()
