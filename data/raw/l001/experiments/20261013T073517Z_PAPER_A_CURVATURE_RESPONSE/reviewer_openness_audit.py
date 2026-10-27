"""Independent terminal audit of the new interior-event witnesses."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
P=Path(__file__).resolve().parent; L=P.parents[1]
def read(p): return json.loads(p.read_text())
gate=read(P/'GLOBAL_OPENNESS_GATE.json')
for n,h in gate['frozen_hashes'].items(): assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h
for n,h in read(P/'GLOBAL_OPENNESS_BINDINGS.json')['sources'].items(): assert hashlib.sha256((L/n).read_bytes()).hexdigest()==h
meta=read(P/'GLOBAL_OPENNESS_RUN.json'); out=read(P/'GLOBAL_OPENNESS_RESULT.json')
assert meta['returncode']==0 and (P/'GLOBAL_OPENNESS_STDERR.txt').read_bytes()==b''
assert meta['output_sha256']==hashlib.sha256((P/'GLOBAL_OPENNESS_RESULT.json').read_bytes()).hexdigest()
assert meta['gate_sha256']==hashlib.sha256((P/'GLOBAL_OPENNESS_GATE.json').read_bytes()).hexdigest()
glob=read(L/'experiments/20261013T001854Z_PAPER_A_STATIC_TESTS/inputs/global.json')
p01=read(L/'experiments/research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01/RESULT.json')
assert glob['root_authority']['root_exact_bounds']==p01['neighborhood']['root_box_exact']
assert all(p01['gates'][f'P01-G{i}']=='PASS' for i in range(1,5))
assert glob['frozen_design']['proper_distance_endpoint']=='2'
scalars=[b for b in glob['terminal_boxes'] if b['classification']=='FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED']
curves=[b for b in glob['terminal_boxes'] if b['classification']=='NEGATIVE_CURVATURE_EXCLUDED']
assert len(scalars)==706 and len(curves)==19
starts=[]; tails=[]
for b in scalars:
    for engine in ('primary','independent'):
        r=b['record'][engine]; f,t=r['event_cells']; n=r['steps']; after=r['negative_after_cell']
        assert 0<f<=t and t+1==after<n
        lo,hi=map(F,r['event_bracket_exact'])
        assert lo==F(2*f,n) and hi==F(2*after,n)
        starts.append(lo); tails.append(2-hi)
for b in curves:
    for engine in ('primary','independent'): assert F(b['record']['curvature'][engine]['exact_bounds'][1])<0
w=out['witnesses']
assert w['scalar_boxes']==706 and w['engine_witnesses']==1412 and w['unchanged_curvature_boxes']==19
assert F(w['minimum_pre_event_duration'])==min(starts)==F(1473,4096)
assert F(w['minimum_duration_after_event_bracket_to_s2'])==min(tails)==F(1,1024)
assert w['duration_margins_are_not_tension_radii'] and not out['numerical_epsilon_certified']
assert {x['control'] for x in out['controls']}=={'INTERIOR_EVENT_START','INTERIOR_EVENT_END','SAME_ROOT_BOX'}
assert all(x['control']==x['rejected_by'] for x in out['controls'])
print(json.dumps({'status':'PASS','engine_witnesses_reconstructed':len(starts),'minimum_pre_event_duration':str(min(starts)),
 'minimum_duration_after_event_bracket_to_s2':str(min(tails)),'numerical_epsilon_certified':False,
 'owner_result_sha256':meta['output_sha256']},indent=2))
