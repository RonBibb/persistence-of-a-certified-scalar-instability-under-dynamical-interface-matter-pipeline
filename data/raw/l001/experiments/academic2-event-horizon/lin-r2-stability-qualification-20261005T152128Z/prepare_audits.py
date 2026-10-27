"""Bind existing evidence and audit source; evaluates no background or spectrum."""
import hashlib,json,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources={
'd1_high_result':'../lin-d1-high-resolution-confirmation-20261002T015100Z/RESULT.json',
'd1_independent_result':'../lin-d1-independent-ode-replay-20261002T225837Z/output/r1/RESULT.json',
'd1_source':'../lin-d1-validated-sensitivity-newton-20261002T012953Z/validated_sensitivity_newton.py',
'background_receipt':'../capture-to-model-2026-09-12/static-background-successor/proper-shooting/narrow-gap/fine-collocation/results/receipt.json',
'stability_manifest':'../lin-curved-stability-2026-09-29/MANIFEST.json',
'stability_contract':'../lin-curved-stability-2026-09-29/CONTRACT.json',
'stability_summary':'../lin-curved-stability-2026-09-29/results/SUMMARY.json',
'independent_mode_check':'../lin-curved-stability-2026-09-29/results/INDEPENDENT_MODE_CHECK.json',
'independent_formulation':'../lin-curved-stability-2026-09-29/analysis/INDEPENDENT_FORMULATION.md',
'draft_audit_source':'../lin-static-stability-branch-audit-20261005T120000Z/audit_branch.py',
'draft_audit_contract':'../lin-static-stability-branch-audit-20261005T120000Z/CONTRACT.md',
'r2_result':'../lin-static-parameter-neighborhood-r2-20261005T120100Z/output/RESULT.json',
'r2_terminal':'../lin-static-parameter-neighborhood-r2-20261005T120100Z/output/TERMINAL_CHECKPOINT.json',
}
out={'schema':'static-stability-branch-audit-bindings-v2','source_sha256':sha(HERE/'branch_audit.py'),'contract_sha256':sha(HERE/'BRANCH_AUDIT_CONTRACT.md'),'imports':{k:{'relative_path':p,'sha256':sha(HERE/p)} for k,p in sources.items()}}
path=HERE/'BRANCH_AUDIT_BINDINGS.json'
with path.open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
freeze={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{p:sha(HERE/p) for p in ['branch_audit.py','BRANCH_AUDIT_CONTRACT.md','BRANCH_AUDIT_BINDINGS.json','r2_postrun.py','prepare_audits.py']},'scope':'POSTRUN_EVIDENCE_AUDITS_NO_NEW_SPECTRUM'}
with (HERE/'AUDIT_FREEZE.json').open('x') as f:json.dump(freeze,f,indent=2,sort_keys=True);f.write('\n')
for name in freeze['files']: (HERE/name).chmod(0o444)
(HERE/'AUDIT_FREEZE.json').chmod(0o444)
