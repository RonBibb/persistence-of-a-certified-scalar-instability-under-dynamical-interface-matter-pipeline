"""Prospectively freeze this bounded spectrum experiment, without evaluating it."""
import datetime,hashlib,json,platform
import numpy as np
import scipy
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs={
'failed_control_publication':'spectrum/FAILURE.json',
'predecessor_binding':'SPECTRUM_BINDINGS.json',
'r2_result':'../lin-static-parameter-neighborhood-r2-20261005T120100Z/output/RESULT.json',
'r2_audit':'audit/R2_POSTRUN_AUDIT.json',
'branch_audit':'audit/branch/RESULT.json',
'old_summary':'../lin-curved-stability-2026-09-29/results/SUMMARY.json',
'old_background_arrays':'../capture-to-model-2026-09-12/static-background-successor/proper-shooting/narrow-gap/fine-collocation/results/arrays.npz',
'old_background_receipt':'../capture-to-model-2026-09-12/static-background-successor/proper-shooting/narrow-gap/fine-collocation/results/receipt.json',
'old_contract':'../lin-curved-stability-2026-09-29/CONTRACT.json',
'differentiation_helper':'../lin-curved-stability-2026-09-29/code/independent_mode_check.py',
'd1_high_result':'../lin-d1-high-resolution-confirmation-20261002T015100Z/RESULT.json',
'd1_independent_result':'../lin-d1-independent-ode-replay-20261002T225837Z/output/r1/RESULT.json',
}
r2=json.loads((HERE/inputs['r2_result']).read_text());model=json.loads((HERE/inputs['old_contract']).read_text())['model'];bounds=r2['frozen_design']['parameter_box']
if json.loads((HERE/inputs['branch_audit']).read_text())['status']!='COMPLETE':raise RuntimeError('branch audit prerequisite')
if json.loads((HERE/inputs['r2_audit']).read_text())['status']!='PASS':raise RuntimeError('R2 audit prerequisite')
values={k:[F(v[0]),(F(v[0])+F(v[1]))/2,F(v[1])] for k,v in bounds.items()}
coordinates=[('center',1,1),('v_low',0,1),('v_high',2,1),('lambda_low',1,0),('lambda_high',1,2),('low_low',0,0),('low_high',0,2),('high_low',2,0),('high_high',2,2)]
points=[{'name':n,'parameters':{'v1':float(values['v1'][i]),'lambda_b':float(values['lambda_b'][j])},'exact_parameters':{'v1':str(values['v1'][i]),'lambda_b':str(values['lambda_b'][j])}} for n,i,j in coordinates]
out={'schema':'proper-distance-bounded-stability-r1-v1','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':model,'points':points,'root_bracket':[float(F(s)) for s in r2['frozen_design']['root_box']],'controls':[{'name':'coarse','rtol':2e-11,'step_denominator':64},{'name':'fine','rtol':2e-13,'step_denominator':128}],'source':{p:sha(HERE/p) for p in ['STABILITY_CONTRACT.md','STABILITY_RECOVERY_R1.md','stability_run_r1.py','independent_checks.py','prepare_spectrum_r1.py']},'inputs':{k:{'path':p,'sha256':sha(HERE/p)} for k,p in inputs.items()},'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'longdouble_nmant':int(np.finfo(np.longdouble).nmant)},'science_evaluated_before_freeze':False}
with (HERE/'SPECTRUM_R1_BINDINGS.json').open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
for p in list(out['source'])+['SPECTRUM_R1_BINDINGS.json']:(HERE/p).chmod(0o444)
print('Frozen 9 points / 18 paired-control cases; no scientific spectrum evaluated.')
