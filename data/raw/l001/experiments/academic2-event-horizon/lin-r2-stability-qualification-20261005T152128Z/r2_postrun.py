"""Independent rational and provenance verification of the completed R2 record."""
import ast
import hashlib
import json
import os
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter

HERE = Path(__file__).resolve().parent
R2 = HERE.parent / 'lin-static-parameter-neighborhood-r2-20261005T120100Z'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x): return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n');os.replace(t,p)

def main():
    bindings=json.loads((R2/'BINDINGS.json').read_text())
    freeze=json.loads((R2/'FREEZE_RECORD.json').read_text())
    r=json.loads((R2/'output/RESULT.json').read_text())
    terminal=json.loads((R2/'output/TERMINAL_CHECKPOINT.json').read_text())
    preflight=json.loads((R2/'output/PREFLIGHT.json').read_text())
    cp=json.loads((R2/'output/CHECKPOINT.json').read_text());payload=cp['payload']
    checks={}
    for name,expected in freeze['files'].items():checks['frozen:'+name]=sha(R2/name)==expected
    for name,v in bindings['imports'].items():checks['input:'+name]=sha(R2/v['relative_path'])==v['sha256']
    checks['result_terminal_hash']=sha(R2/'output/RESULT.json')==terminal['result_sha256']
    checks['four_guards_match']=r['guard']==terminal['guard']==preflight['guard']==payload['guard']
    checks['preflight_frozen']=sha(R2/'output/PREFLIGHT.json')==freeze['preflight_sha256']
    checks['checkpoint_payload_digest']=hashlib.sha256(canonical(payload)).hexdigest()==cp['checkpoint_sha256']
    immutable=R2/'output'/cp['checkpoint_relative_path']
    checks['immutable_checkpoint_matches']=json.loads(immutable.read_text())==payload and immutable.name=='checkpoint-'+cp['checkpoint_sha256']+'.json'
    checks['state_matches_result']=payload['state']['terminal_cells']==r['terminal_parameter_cells'] and payload['state']['attempted_cells']==r['attempted_parameter_cells']
    checks['no_pending']=payload['state']['current'] is None and not payload['state']['pending_cells']
    checks['exact_volume']=Q(r['total_parameter_volume_exact'])==Q(r['admitted_parameter_volume_exact'])
    checks['complete']=r['status']=='COMPLETE' and not r['unresolved_parameter_cells']
    checks['single_full_parameter_cell']=len(r['terminal_parameter_cells'])==1 and all(r['terminal_parameter_cells'][0]['parameter_cell'][k]==r['frozen_design']['parameter_box'][k] for k in ['v1','lambda_b'])
    c=r['terminal_parameter_cells'][0];details={}
    for producer in ['primary','independent']:
        v=c['root'][producer];a,b=map(Q,c['root']['root_box_exact_bounds']);x,y=map(Q,v['newton_image']['exact_bounds'])
        checks[producer+':strict_newton']=a<x<=y<b and Q(v['strict_inclusion_margin_exact'])==min(x-a,b-y)
        for tag in ['root_box_event','center_event']:
            e=v[tag];gs=tuple(map(Q,e['G_s']['exact_bounds']))
            checks[producer+':'+tag]=e['validated'] and gs[1]<0 and e['negative_after_cell']==e['event_cells'][1]+1
        qa=tuple(map(Q,v['root_box_event']['q_a']['exact_bounds']))
        checks[producer+':derivative_sign']=qa[0]>0 or qa[1]<0
    for label,key in [('global','global_result'),('d0','d0_result')]:
        rows=sorted(c[key]['terminal_boxes'],key=lambda x:Q(x['a_exact_bounds'][0]));previous=Q(0);ok=True
        for row in rows:
            lo,hi=map(Q,row['a_exact_bounds']);ok &= lo==previous and hi>lo;previous=hi
        checks[label+':gap_free']=ok and previous==Q('3602879701896397/36028797018963968')
        details[label]=dict(Counter(x['classification'] for x in rows))
    checks['exactly_one_root']=details['global'].get('CERTIFIED_PARAMETRIC_ROOT_CONTAINER')==1
    checks['global_all_certified']=set(details['global'])<={'NEGATIVE_CURVATURE_EXCLUDED','FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED','CERTIFIED_PARAMETRIC_ROOT_CONTAINER'}
    good=[]
    for row in c['global_result']['terminal_boxes']:
        if row['classification']=='FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED':
            signs=[]
            for prod in ['primary','independent']:
                e=row['record'][prod];a,b=map(Q,e['h']['exact_bounds']);gs=tuple(map(Q,e['G_s']['exact_bounds']));s=1 if a>0 else -1 if b<0 else 0
                signs.append(s);good.append(e['validated'] and gs[1]<0 and s!=0)
            good.append(signs[0]==signs[1])
    checks['all_dual_event_exclusions']=all(good)
    checks['d0_all_excluded']=all(x['excluded'] for x in c['d0_result']['terminal_boxes'])
    checks['d0_positive_margins']=all(Q(x['residual_vector_lower_bound_exact'])>0 for x in c['d0_result']['terminal_boxes'] if x['classification']=='FIXED_D0_WALL_RESIDUAL_EXCLUDED')
    checks['d0_count']=len(c['d0_result']['terminal_boxes'])==693
    out={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'counts':details,'result_sha256':sha(R2/'output/RESULT.json'),'source_sha256':sha(__file__),'evidence_classification':'INDEPENDENT_ARTIFACT_AND_RATIONAL_CERTIFICATE_AUDIT_NO_CAMPAIGN_RERUN'}
    write(HERE/'audit/R2_POSTRUN_AUDIT.json',out)
    print(json.dumps({'audit':'R2','status':out['status'],'checks':len(checks)},sort_keys=True))
    if out['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
