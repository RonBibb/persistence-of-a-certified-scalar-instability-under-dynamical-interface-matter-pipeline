"""Seal only the preserved technical failure; never runs numerical kernels."""
import json,hashlib,sys,os,tempfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(sys.argv[1]).resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):
    assert not p.exists()
    fd,tmp=tempfile.mkstemp(prefix=p.name+'.uncommitted-',dir=p.parent)
    with os.fdopen(fd,'w') as f:
        json.dump(data,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p);p.chmod(0o444)
failure=json.loads((root/'output/FAILURE.json').read_text())
guard=sha(root/'BINDINGS.json');assert failure['guard']==guard
assert not (root/'output/RESULT.json').exists()
assert not (root/'output/LATEST.json').exists()
result={'status':'TECHNICAL_INCOMPLETE','classification':'TECHNICAL_INCOMPLETE_ENCLOSURE_CONSTRUCTION',
        'guard':guard,'accepted_physical_cells':0,'scientific_conclusion':False,
        'failure_sha256':sha(root/'output/FAILURE.json'),
        'report_sha256':sha(root/'RESULT_REPORT.md'),'evolution_launched':False,
        'repair_packet':'../lin-c4-local-certificate-r1-20261005T221400Z',
        'sealed_utc':datetime.now(timezone.utc).isoformat()}
save(root/'RESULT.json',result)
entries=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)}
         for p in sorted(root.rglob('*')) if p.is_file() and p.name!='RUN.lock']
save(root/'MANIFEST.json',{'classification':result['classification'],'entries':entries})
print(json.dumps({'files':len(entries),'result_sha256':sha(root/'RESULT.json'),'manifest_sha256':sha(root/'MANIFEST.json')}))
