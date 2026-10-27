"""Administrative Linux-only source/runtime binding; no scientific execution."""
import sys
sys.dont_write_bytecode = True
import ast, hashlib, json, os, platform, signal, traceback
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent
R=Path('/media/psf/Home/Research')
B=R/'papers/paper-A/reviews/20261018T170644Z_REPRODUCIBILITY_AUDIT'
P=R/'papers/paper-A/reviews/20261018T181412Z_PHASE_PROVENANCE'
E=R/'research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments'
assert sys.platform=='linux' and (HERE/'SOURCE_REVIEW.md').is_file()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,d):
    with (HERE/n).open('x') as f:
        json.dump(d,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
inputs={
 'primary_result':B/'background_regeneration/output/primary_RESULT.json',
 'independent_result':B/'background_regeneration/output/independent_RESULT.json',
 'primary_source':B/'background_regeneration/source/primary/validated_sensitivity_newton.py',
 'independent_source':B/'background_regeneration/source/independent/independent_d1_replay.py',
 'phase_binding':P/'phase_regeneration/source/inputs/central_bindings.json',
 'current_binding':E/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T2R1_AB_SELECTED_MODE/inputs/central_bindings.json',
 'background_review':B/'FINAL_INDEPENDENT_REVIEW.md',
 'background_terminal_gates':B/'TERMINAL_RECORD_GATES.json',
 'phase_review':P/'FINAL_INDEPENDENT_REVIEW.md',
 'manuscript':R/'papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md'}
for p in inputs.values(): assert p.is_file(), str(p)
save('INPUTS.json',{k:{'path':str(p),'sha256':sha(p)} for k,p in inputs.items()})
runtime={Path(sys.executable).resolve()}; modules={}; mapped=[]
for name,module in list(sys.modules.items()):
    value=getattr(module,'__file__',None)
    if value and Path(value).is_file():
        p=Path(value).resolve(); runtime.add(p); modules[name]=str(p)
for row in Path('/proc/self/maps').read_text().splitlines():
    f=row.split(None,5)
    if len(f)==6 and f[5].startswith('/') and Path(f[5]).is_file():
        runtime.add(Path(f[5])); mapped.append(f[5])
save('RUNTIME_BINDINGS.json',{'executable_realpath':str(Path(sys.executable).resolve()),'files':{str(p):sha(p) for p in sorted(runtime)},'modules':modules,'mapped_files':sorted(set(mapped))})
paths=set(inputs.values())|runtime|{HERE/n for n in ('check_bridge.py','freeze.py','lease.py','PLAN.md','SOURCE_REVIEW.md','INPUTS.json','RUNTIME_BINDINGS.json')}
save('FROZEN.json',{'files':{str(p):sha(p) for p in sorted(paths)},'executable_realpath':str(Path(sys.executable).resolve()),'platform':platform.platform(),'python':sys.version,'pid':os.getpid(),'utc':datetime.now(timezone.utc).isoformat(),'scope':'Administrative binding only; no scientific checker imported.'})
print(json.dumps({'frozen_sha256':sha(HERE/'FROZEN.json'),'files':len(paths)}))
