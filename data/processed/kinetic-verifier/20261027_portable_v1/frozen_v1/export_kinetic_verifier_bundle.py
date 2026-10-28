#!/usr/bin/env python3
"""Export the explicit saved-cell verifier closure; never execute a producer."""
from pathlib import Path
import argparse,hashlib,json,shutil

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def export(repo,output):
    packet=repo/'data/raw/neutral-certificates/kinetic'
    admission=json.loads((packet/'FRACTION_VERIFIER_ADMISSION.json').read_text())
    candidate=json.loads((packet/admission['candidate']).read_text())
    pointer=json.loads((packet/'certificate/LATEST.json').read_text())
    state=json.loads((packet/'certificate'/pointer['path']).read_text())
    inputs=json.loads((packet/'INPUTS.json').read_text())['files']
    names=set(candidate['files'])|set(state['guard']['files'])
    names.update(item['snapshot'] for item in inputs)
    names.update(['FRACTION_VERIFIER_ADMISSION.json',admission['candidate'],
                  'certificate/LATEST.json','certificate/'+pointer['path'],
                  'certificate/CONTROLS.json','certificate/RESULTS.json',
                  'fraction_verification_v1/VERIFICATION_RESULT.json'])
    names.update(admission['review_receipts'])
    names.update('certificate/'+chunk['path'] for chunk in state['completed_chunks'])
    for name in names:
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Unsafe historical relative path')
        if not (packet/name).is_file():raise FileNotFoundError(name)
    assert sha(packet/admission['candidate'])==admission['candidate_sha256']
    for name,h in candidate['files'].items():assert sha(packet/name)==h,name
    for name,h in state['guard']['files'].items():assert sha(packet/name)==h,name
    output.mkdir(parents=True,exist_ok=False)
    for name in sorted(names):
        dest=output/'packet'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(packet/name,dest)
    shutil.copy2(repo/'src/verify_kinetic_cells.py',output/'verify_kinetic_cells.py')
    files={str(p.relative_to(output)):{'sha256':sha(p),'bytes':p.stat().st_size}
           for p in sorted(output.rglob('*')) if p.is_file()}
    mapping=[{'historical_source':item['source'],'path':'packet/'+item['snapshot'],
              'sha256':item['sha256']} for item in inputs]
    data={'schema':'kinetic-saved-cell-bundle-v1','files':files,
          'packet':'packet','certificate':'packet/certificate',
          'pristine_source':'packet/action_review/fraction_verifier/verify_saved_certificate.py',
          'pointer_sha256':sha(packet/'certificate/LATEST.json'),
          'expected_cells':state['total_cells'],'expected_chunks':len(state['completed_chunks']),
          'original_to_snapshot':mapping,
          'scope':'Executable saved-check closure and historical binding receipts; not the complete analytical dependency tree or interval-producer runtime.'}
    manifest=output/'BUNDLE_MANIFEST.json'
    manifest.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    digest=sha(manifest)
    (output/'BUNDLE_MANIFEST.sha256').write_text(digest+'  BUNDLE_MANIFEST.json\n')
    return {'manifest_sha256':digest,'bound_files':len(files),
            'bound_bytes':sum(v['bytes'] for v in files.values()),
            'cells':state['total_cells'],'chunks':len(state['completed_chunks'])}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(export(args.repo_root.resolve(),args.output.resolve()),indent=2))
