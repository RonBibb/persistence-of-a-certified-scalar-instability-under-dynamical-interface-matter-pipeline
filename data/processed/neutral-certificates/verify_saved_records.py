#!/usr/bin/env python3
"""Read-only SHA-256, Fraction/integer and saved-cell checks. No producer imports."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,gzip
ROOT=Path(__file__).resolve().parent
load=lambda p:json.loads((ROOT/p).read_text())
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
gates={}
def check(name,predicate):gates[name]=bool(predicate)
manifest=load('PACKAGE_MANIFEST.json')
for path,digest in manifest['files'].items():check('identity:'+path,sha(path)==digest)
ids=load('SOURCE_IDENTITIES.json')['files']
check('source_copy_identities',all(sha(x['package_path'])==x['package_sha256'] for x in ids))
A=list(map(Q,['456607025194779413/4611686018427387904','114151756532473697/1152921504606846976']))
D=list(map(Q,['32727/16384','32729/16384']))
bg=load('background/background_regeneration/output/primary_RESULT.json')['finest_narrow_result']
box=list(map(Q,bg['box_exact_dyadic_bounds']));image=list(map(Q,bg['interval_newton_image']['exact_bounds']))
check('background_exact_launch',image==A)
check('background_strict_newton_inclusion',box[0]<image[0]<=image[1]<box[1])
check('background_exact_event',list(map(Q,bg['box_event']['event_bracket']))==D)
check('background_record_predicates',all(bg[k] for k in ['qualified_newton_inclusion','strict_self_map']))
phase_ratios=[]
for role in ['primary','independent']:
 d=load(f'phase/phase_regeneration/source/test1_v3/{role}_result.json');ratio=list(map(Q,d['phase_over_pi']['bounds']));phase_ratios.append(ratio)
 check(role+':strict_phase_band',Q(1)<ratio[0]<=ratio[1]<Q(3,2))
 last=D[0];ok=True
 for ev in d['event']:
  lo,hi=Q(ev['lo']),Q(ev['hi']);ok &= lo==last and lo<hi
  pair=list(map(Q,ev['phase_over_pi']['bounds']));ok &= Q(1)<pair[0]<=pair[1]<Q(3,2);last=hi
 check(role+':phase_event_cover',ok and last==D[1])
check('displayed_phase_enclosure',phase_ratios[0]==list(map(Q,['577838035/536870912','577858823/536870912'])))
for role in ['primary','independent']:
 signs=[]
 for endpoint in ['low','high']:
  d=load(f'mass/output/{role}_{endpoint}.json');bounds=[Q(d['determinant'][key]) for key in ['lo_exact','hi_exact']]
  signs.append(1 if bounds[0]>0 else -1 if bounds[1]<0 else 0)
  last=D[0];ok=True
  for ev in d['event_cover']:
   lo,hi=Q(ev['lo_exact']),Q(ev['hi_exact']);ok &= last==lo and lo<hi;last=hi
  check(role+':mass_'+endpoint+'_event_cover',ok and last==D[1])
 check(role+':strict_opposite_mass_signs',signs[0]*signs[1]==-1)
check('mass_inspection_dependencies',all((ROOT/'mass'/p).is_file() for p in ['CONTRACT.md','FREEZE_RECORD.json','runner.py','BINDINGS.json']))
k=load('kinetic/certificate/RESULTS.json')
check('kinetic_exact_remainder_below_half',0<Q(k['strict_Delta_upper_rational'])<Q(1,2))
check('kinetic_saved_gate_values',all(k['gates'].values()))
# Reconstruct saved whole-cell hulls and event coverage; never recompute a flow.
ptr=load('kinetic/certificate/LATEST.json');cp=Path('kinetic/certificate')
check('kinetic_last_checkpoint_identity',sha(cp/ptr['path'])==ptr['sha256'])
state=load(cp/ptr['path']);start=load(cp/'checkpoints/state_00000.json')
hull=[[int(a),int(b)] for a,b in start['state']];event=None;n=0;s=Q(0)
for ch in state['completed_chunks']:
 check('kinetic_chunk_identity:'+ch['path'],sha(cp/ch['path'])==ch['sha256'])
 rows=json.loads(gzip.decompress((ROOT/cp/ch['path']).read_bytes()));assert ch['start']==n
 for row in rows:
  assert row['index']==n and Q(row['s'])==s
  whole=[[int(a),int(b)] for a,b in row['whole_cell']]
  hull=[[min(a[0],b[0]),max(a[1],b[1])] for a,b in zip(hull,whole)]
  if 'D_event_overlap' in row:
   ev=[[int(a),int(b)] for a,b in row['D_event_overlap']]
   event=ev if event is None else [[min(a[0],b[0]),max(a[1],b[1])] for a,b in zip(event,ev)]
  n+=1;s+=Q(row['h'])
 assert ch['end']==n
check('kinetic_saved_cell_cover',n==state['completed_cells']==16365 and s==Q(state['D_hi']))
check('kinetic_whole_collar_hull',hull==[[int(a),int(b)] for a,b in state['whole_collar']])
check('kinetic_event_hull',event==[[int(a),int(b)] for a,b in state['D_event']])
check('kinetic_acceptance_record',load('kinetic/TERMINAL_ACCEPTANCE.json')['accepted'] is True)
report={'status':'PASS' if all(gates.values()) else 'FAIL','checks':len(gates),'failed':[k for k,v in gates.items() if not v],'kinetic_saved_cells_checked':n,'new_integrations':0,'producer_imports':0,'scope':'Saved-record identities, exact terminal arithmetic and stored-cell hull coverage only. Does not re-prove unexported Picard/Taylor/phase-lift predicates, historical faithful execution, arithmetic correctness, analytic theorems or external peer review. Redacted copies are inspection derivatives, not new source-bound runs.'}
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='PASS' else 1)
