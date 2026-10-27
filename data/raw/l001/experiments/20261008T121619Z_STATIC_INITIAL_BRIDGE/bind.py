"""Pre-outcome file binding only; no scientific calculation."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,os
R=Path(__file__).resolve().parent;S=R.parents[1];I=S.parent/'L009-initial-data-boundary-construction'
C4=S/'experiments/academic2-event-horizon/lin-c4-connected-branch-20261006T004500Z'
N=I/'experiments/academic2/01-horizon-core/d1-native-cauchy-20261005T201829Z'
C6=I/'experiments/research_rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/work/row_09'
P=S/'experiments/research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01'
E=S/'experiments/research-rounds/20261007T132704Z_ALL_LINES_ELEVEN_CORE_ROUND/row_01'
AUTH=Path('/Users/ronbibb/Research/research_repositories/program-hub/rounds/20261008T121619Z_PRIORITY_THREE_TESTS')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
files={'authorization':AUTH/'AUTHORIZATION.json','folder_contract':AUTH/'FOLDER_BINDINGS.json',
 'joint_contract':AUTH/'LIN_BRIDGE_CONTRACT.md','static_binding':C4/'BINDINGS.json','C4_result':C4/'RESULT.json',
 'C4_audit':C4/'INDEPENDENT_AUDIT.json','native_binding':N/'BINDINGS.json','seed':N/'results/fine_c4/SEED.json',
 'old_dense':N/'results/fine_c4/case_3.dense.json','C6_result':C6/'RESULT.json','C6_integrity':C6/'INTEGRITY.json',
 'P01':P/'RESULT.json','P01_integrity':P/'RESULT_INTEGRITY.json','E01':E/'RESULT.json'}
for dps in (80,100):
    for key,name in [('dense','case_3.dense.json'),('candidate','CANDIDATE.json'),('C6_readback','INDEPENDENT_READBACK.json')]:
        files[key+str(dps)]=C6/f'results/p{dps}'/name
sources=['CONTRACT.md','DERIVATION.md','bridge.py','audit.py','bind.py']
for f in sources:
    if f.endswith('.py'):ast.parse((R/f).read_text(),filename=f)
assert sha(files['candidate100'])=='3886aae704a5f9e75a6494448d55b8bce7e1297cdfb4bed92c5a0c82e71c899f'
assert not (R/'BINDINGS.json').exists()
obj={'schema':'lin-static-bridge-binding/v1','utc':datetime.now(timezone.utc).isoformat(),
 'deadline_utc':'2026-10-08T13:16:19Z','cpus':[4,5],'producer_cpu':4,'memory_bytes':4*1024**3,
 'mac_output_root':str(R),'linux_output_root':str(R).replace('/Users/ronbibb/','/media/psf/Home/',1),
 'linux_mapping_verified_utc':'2026-10-08T12:20:59Z','legacy_writes_authorized':False,'evolution_authorized':False,
 'inputs':[{'id':k,'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for k,p in files.items()],
 'sources':[{'path':f,'sha256':sha(R/f),'bytes':(R/f).stat().st_size} for f in sources]}
p=R/'BINDINGS.json';p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');os.chmod(p,0o444)
for f in sources:os.chmod(R/f,0o444)
print(json.dumps({'bound_inputs':len(files),'bound_sources':len(sources),'binding_sha256':sha(p),'deadline_utc':obj['deadline_utc']}))
