"""Summarize and seal completed evidence; no background or mode solve."""
import datetime,hashlib,json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/'output'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
    if p.exists():raise RuntimeError('refusing overwrite '+str(p))
    tmp=p.with_suffix('.tmp')
    with tmp.open('w') as f:json.dump(x,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p);p.chmod(0o444)
if (HERE/'TERMINAL.json').exists():raise RuntimeError('round already sealed')
b=read(HERE/'BINDINGS.json');guard=sha(HERE/'BINDINGS.json')
for name,h in b['source'].items():
    if sha(HERE/name)!=h:raise RuntimeError('frozen source changed '+name)
for name,entry in b['inputs'].items():
    if sha(HERE/entry['path'])!=entry['sha256']:raise RuntimeError('frozen input changed '+name)
r=read(OUT/'RESULT.json');t=read(OUT/'TERMINAL.json');cp=read(OUT/'CHECKPOINT.json')
if sha(OUT/'RESULT.json')!=t['result_sha256'] or any(x['guard']!=guard for x in [r,t,cp]):
    raise RuntimeError('terminal/result/checkpoint binding mismatch')
review=read(OUT/'FINAL_INDEPENDENT.json')
if sha(OUT/'FINAL_INDEPENDENT.json')!=r['independent_sha256'] or review['guard']!=guard:
    raise RuntimeError('independent final receipt mismatch')
cases=[]
for name,entry in cp['completed'].items():
    for kind in ['receipt','arrays','background']:
        if sha(OUT/entry[kind])!=entry[kind+'_sha256']:raise RuntimeError('case artifact changed '+name)
    cases.append(read(OUT/entry['receipt']))
for name in ['RESULT_REPORT.md','INDEPENDENT_POSTRUN_REVIEW.md']:
    if not (HERE/name).is_file():raise RuntimeError('final report missing '+name)
success=(r['status']=='COMPLETE' and len(cases)==18 and not cp['pending']
         and all(x['accepted'] for x in cases) and review['all_completed_cases_pass']
         and review['central_qualified'] and review['inputs_unchanged'])
fine=[x for x in cases if x['control']['name']=='fine']
center=next(x for x in fine if x['point']['name']=='center')
old=read(HERE/b['inputs']['prior_failed_result']['path'])
start=datetime.datetime.fromisoformat(cp['started_utc']);end=datetime.datetime.fromisoformat(r['completed_utc'])
result={'schema':'mp-stability-bounded-round-v1','workflow_status':'COMPLETE',
        'scientific_status':'QUALIFIED_NUMERICAL' if success else 'UNRESOLVED',
        'classification':'BACKGROUND_PRECISION_GATE_RESOLVED_NUMERICAL_GROWING_MODE_PERSISTS_AT_NINE_POINTS' if success else r['classification'],
        'completed_cases':len(cases),'uncomputed_cases':cp['pending'],
        'central_mu':center['mu'],'central_lambda':center['lambda'],'central_growth_over_H':center['growth_over_H'],
        'central_2001_direct_metric':next(x['background']['direct_metric'] for x in center['independent_checks'] if x['stride']==1),
        'physical_mass_range':[min(x['mu'] for x in fine),max(x['mu'] for x in fine)],
        'growth_over_H_range':[min(x['growth_over_H'] for x in fine),max(x['growth_over_H'] for x in fine)],
        'maximum_paired_mass_difference':max(x['mass_difference'] for x in r['pairs']),
        'maximum_independent_background':max(x['max_background'] for c in review['cases'] for x in c['checks']),
        'maximum_independent_mode':max(x['max_mode'] for c in review['cases'] for x in c['checks']),
        'wall_seconds':(end-start).total_seconds(),'guard':guard,
        'producer_result_sha256':sha(OUT/'RESULT.json'),'independent_review_sha256':sha(OUT/'FINAL_INDEPENDENT.json'),
        'prior_failed_test_status_unchanged':old['status'],'rigorous_static_theorem_changed':False,
        'rigorous_spectral_enclosure':False,'continuous_box_spectral_theorem':False,
        'causal_evolution_admitted':False,'D1_P16_merged':False,'manuscript_changed':False,
        'completed_utc':r['completed_utc']}
write(HERE/'RESULT.json',result)
manifest={'schema':'bounded-round-manifest-v1','files':{str(p.relative_to(HERE)):{'sha256':sha(p),'bytes':p.stat().st_size}
          for p in sorted(HERE.rglob('*')) if p.is_file() and p not in [HERE/'MANIFEST.json',HERE/'TERMINAL.json']}}
write(HERE/'MANIFEST.json',manifest)
write(HERE/'TERMINAL.json',{'workflow_status':'COMPLETE','scientific_status':result['scientific_status'],
          'classification':result['classification'],'result_sha256':sha(HERE/'RESULT.json'),
          'manifest_sha256':sha(HERE/'MANIFEST.json'),'completed_utc':result['completed_utc']})
for p in HERE.rglob('*'):
    if p.is_file():p.chmod(0o444)
print(json.dumps({'result_sha256':sha(HERE/'RESULT.json'),'manifest_sha256':sha(HERE/'MANIFEST.json'),
      'files':len(manifest['files']),'classification':result['classification']},sort_keys=True))
