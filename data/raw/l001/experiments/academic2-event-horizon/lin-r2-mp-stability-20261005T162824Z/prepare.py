"""Freeze the higher-precision successor after controls and independent review."""
import json,os
from pathlib import Path
from fractions import Fraction
from runner import sha,read,write,now,runtime

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'lin-r2-stability-qualification-20261005T152128Z'
if (HERE/'BINDINGS.json').exists():raise RuntimeError('already frozen')
terminal=read(PRIOR/'TERMINAL.json');manifest=read(PRIOR/'MANIFEST.json')
if sha(PRIOR/'RESULT.json')!=terminal['result_sha256'] or sha(PRIOR/'MANIFEST.json')!=terminal['manifest_sha256']:
    raise RuntimeError('preceding terminal digest mismatch')
for name,entry in manifest['files'].items():
    if sha(PRIOR/name)!=entry['sha256']:raise RuntimeError('preceding artifact changed '+name)
if terminal['scientific_test_status']!='UNRESOLVED':raise RuntimeError('prior failure not preserved')
old=read(PRIOR/'SPECTRUM_R1_BINDINGS.json')
inputs={n:(PRIOR/v['path']).resolve() for n,v in old['inputs'].items()}
inputs.update(prior_binding=PRIOR/'SPECTRUM_R1_BINDINGS.json',prior_result=PRIOR/'RESULT.json',
              prior_manifest=PRIOR/'MANIFEST.json',prior_terminal=PRIOR/'TERMINAL.json',
              prior_failed_result=PRIOR/'spectrum-r1/RESULT.json',
              old_proper_source=PRIOR/'stability_run_r1.py',
              old_proper_checks=PRIOR/'independent_checks.py',
              prior_review=PRIOR/'audit/INDEPENDENT_POSTRUN.json')
r2=read(inputs['r2_result'])
controls=[dict(name='coarse',dps=50,degree=24,step_denominator=64,rtol=2e-11,shoot_tolerance='1e-30'),
          dict(name='fine',dps=70,degree=30,step_denominator=128,rtol=2e-13,shoot_tolerance='1e-45')]
sources=['CONTRACT.md','mp_background.py','sample_checks.py','runner.py','prepare.py','preflight.py','independent_review.py','PREFLIGHT_SCIENTIFIC_REVIEW.md']
preflight=read(HERE/'preflight-final/RESULT.json')
if not preflight['pass']:raise RuntimeError('preflight controls not passed')
for n,h in preflight['source_sha256'].items():
    if sha(HERE/n)!=h:raise RuntimeError('preflight source has changed '+n)
inputs['preflight_controls']=HERE/'preflight-final/RESULT.json'
b={'schema':'mp-stability-successor-v1','frozen_utc':now(),'science_evaluated_before_freeze':False,
   'model_exact':{n:str(Fraction(float(v))) for n,v in old['model'].items()},'points':old['points'],
   'root_bracket':r2['frozen_design']['root_box'],'controls':controls,
   'source':{n:sha(HERE/n) for n in sources},
   'inputs':{n:{'path':os.path.relpath(p,HERE),'sha256':sha(p)} for n,p in inputs.items()},
   'runtime':runtime(),'preflight_sha256':sha(HERE/'preflight-final/RESULT.json'),
   'background_gate':1e-8,'mode_gate':1e-6,'mass_gate':1e-7,'sample_nodes':[1001,2001],
   'central_conformal_control':{'dps':50,'rk4_substeps':[4,8],'physical_gate':1e-8}}
write(HERE/'BINDINGS.json',b,True)
for n in sources:(HERE/n).chmod(0o444)
print(json.dumps({'frozen':True,'guard':sha(HERE/'BINDINGS.json'),'runtime':b['runtime']},sort_keys=True))
