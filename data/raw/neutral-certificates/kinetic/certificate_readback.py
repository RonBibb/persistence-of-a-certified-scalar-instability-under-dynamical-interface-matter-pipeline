#!/usr/bin/env python3
"""Read-only exact saved-enclosure summary; no producer imports or new IVP."""
from pathlib import Path
from fractions import Fraction
import gzip,hashlib,json
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'certificate';pointer=json.loads((p/'LATEST.json').read_text());assert sha(p/pointer['path'])==pointer['sha256'];state=json.loads((p/pointer['path']).read_text());scale=1<<state['guard']['bits']
start=json.loads((p/'checkpoints/state_00000.json').read_text());hull=[[int(a),int(b)] for a,b in start['state']];event=None;n=0;s=Fraction(0);max_point=[0]*6;max_cell=[0]*6;names=['W','H','Phi','T','Ewarp','q']
for ch in state['completed_chunks']:
 assert sha(p/ch['path'])==ch['sha256'];rows=json.loads(gzip.decompress((p/ch['path']).read_bytes()));assert ch['start']==n
 for row in rows:
  assert row['index']==n and Fraction(row['s'])==s
  end=[[int(a),int(b)] for a,b in row['endpoint']];whole=[[int(a),int(b)] for a,b in row['whole_cell']]
  for j in range(6):
   max_point[j]=max(max_point[j],end[j][1]-end[j][0]);max_cell[j]=max(max_cell[j],whole[j][1]-whole[j][0]);hull[j]=[min(hull[j][0],whole[j][0]),max(hull[j][1],whole[j][1])]
  if 'D_event_overlap' in row:
   ev=[[int(a),int(b)] for a,b in row['D_event_overlap']]
   event=ev if event is None else [[min(a[0],b[0]),max(a[1],b[1])] for a,b in zip(event,ev)]
  n+=1;s+=Fraction(row['h'])
 assert ch['end']==n
assert n==state['completed_cells']==16365 and s==Fraction(state['D_hi'])
assert hull==[[int(a),int(b)] for a,b in state['whole_collar']]
assert event==[[int(a),int(b)] for a,b in state['D_event']]
r={'operation':'Read-only exact Fraction/integer saved-enclosure summary; not a new flow or independent Taylor verification','status':'PASS','chunks':len(state['completed_chunks']),'unique_physical_cells':n,'total_physical_cell_evaluations_including_recovery_replay':n+256,'synthetic_vacuum_steps':1,'new_root_solves':0,'entire_parameter_box_enclosure':'Inherited full A launch, D event, all proper-coordinate cells','maximum_gridpoint_enclosure_width':{name:str(Fraction(v,scale)) for name,v in zip(names,max_point)},'maximum_whole_cell_enclosure_width_including_physical_cell_variation':{name:str(Fraction(v,scale)) for name,v in zip(names,max_cell)},'gridpoint_error_meaning':'Each exact-root profile value at a stored fixed s lies within the saved endpoint interval; its error relative to THAT interval midpoint is <= half its width. These are not errors relative to the prior binary64 approximate profile.','cumulative_hull_and_event_reconstructed_exactly':True,'current_checkpoint_payload_sha256':pointer['sha256'],'source_sha256':sha(R/'certificate_readback.py')}
(R/'BACKGROUND_UNCERTAINTY_READBACK.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'status':r['status'],'cells':n,'chunks':r['chunks'],'point_enclosure_widths_display_only':{name:float(Fraction(v,scale)) for name,v in zip(names,max_point)}},indent=2))
