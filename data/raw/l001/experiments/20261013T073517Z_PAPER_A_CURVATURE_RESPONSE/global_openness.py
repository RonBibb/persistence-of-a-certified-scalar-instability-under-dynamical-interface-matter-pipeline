"""Interior first-event witnesses for a conditional compactness corollary."""
import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
OWNER=HERE.parents[1]
GLOBAL='experiments/20261013T001854Z_PAPER_A_STATIC_TESTS/inputs/global.json'
TENSION='experiments/research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01/RESULT.json'
class Rejected(Exception): pass
def need(ok,name):
    if not ok: raise Rejected(name)
def check(data,p01):
    root=p01['neighborhood']['root_box_exact']
    need(root==data['root_authority']['root_exact_bounds'],'SAME_ROOT_BOX')
    need(all(p01['gates'][f'P01-G{i}']=='PASS' for i in range(1,5)),'LOCAL_P01_PREMISE')
    need(data['frozen_design']['proper_distance_endpoint']=='2','DOMAIN_ENDPOINT')
    n=0; curvature=0; start=[]; end=[]
    for box in data['terminal_boxes']:
        if box['classification']=='NEGATIVE_CURVATURE_EXCLUDED':
            curvature+=1
            for engine in ('primary','independent'):
                need(Q(box['record']['curvature'][engine]['exact_bounds'][1])<0,'UNCHANGED_CURVATURE_EXCLUSION')
        elif box['classification']=='FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED':
            n+=1
            for engine in ('primary','independent'):
                e=box['record'][engine]; first,last=e['event_cells']; steps=e['steps']; after=e['negative_after_cell']
                need(first>0,'INTERIOR_EVENT_START')
                need(after<steps,'INTERIOR_EVENT_END')
                need(after==last+1 and first<=last,'EVENT_CELL_ORDER')
                bracket=tuple(map(Q,e['event_bracket_exact']))
                need(bracket==(Q(2*first,steps),Q(2*(last+1),steps)),'EVENT_BRACKET')
                start.append(bracket[0]); end.append(Q(2)-bracket[1])
    need(n==706 and curvature==19,'EXPECTED_COVER_COUNTS')
    return {'scalar_boxes':n,'engine_witnesses':len(start),'unchanged_curvature_boxes':curvature,
            'minimum_pre_event_duration':str(min(start)),
            'minimum_duration_after_event_bracket_to_s2':str(min(end)),
            'duration_margins_are_not_tension_radii':True}
def main():
    manifest=json.loads((HERE/'GLOBAL_OPENNESS_BINDINGS.json').read_text())
    for name,digest in manifest['sources'].items():
        need(hashlib.sha256((OWNER/name).read_bytes()).hexdigest()==digest,'SOURCE_HASH:'+name)
    data=json.loads((OWNER/GLOBAL).read_text()); p01=json.loads((OWNER/TENSION).read_text())
    witness=check(data,p01); controls=[]
    for name in ('INTERIOR_EVENT_START','INTERIOR_EVENT_END','SAME_ROOT_BOX'):
        d=copy.deepcopy(data); p=copy.deepcopy(p01)
        e=next(b for b in d['terminal_boxes'] if b['classification']=='FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED')['record']['primary']
        if name=='INTERIOR_EVENT_START': e['event_cells'][0]=0
        elif name=='INTERIOR_EVENT_END': e['negative_after_cell']=e['steps']
        else: p['neighborhood']['root_box_exact']=['0','1']
        try: check(d,p)
        except Rejected as err:
            need(str(err)==name,'WRONG_CONTROL_REJECTION')
            controls.append({'control':name,'rejected_by':str(err)})
        else: raise Rejected('CONTROL_ACCEPTED')
    print(json.dumps({'status':'PASS_PENDING_INDEPENDENT_TERMINAL_REVIEW','witnesses':witness,'controls':controls,
      'candidate_corollary':'Some epsilon>0 preserves full-launch first-event uniqueness near baseline tension, conditional on full original first-event validity and local P01 validity.',
      'numerical_epsilon_certified':False,
      'inherited_premise':'Full baseline regular flows, all earlier G>0 history, event transversality, scalar exclusions, complete cover and source model provenance remain inherited from original accepted certificates.'},indent=2))
if __name__=='__main__': main()
