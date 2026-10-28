#!/usr/bin/env python3
"""Predeclared negative fixtures for the portable saved-cell verifier."""
from pathlib import Path
import argparse,gzip,hashlib,json,shutil,subprocess,sys,time

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def readonly(root):
    for p in root.rglob('*'):
        p.chmod(0o555 if p.is_dir() else 0o444)
    root.chmod(0o555)


def rebound(bundle):
    path=bundle/'BUNDLE_MANIFEST.json'; data=json.loads(path.read_text())
    for name in data['files']:
        p=bundle/name
        data['files'][name]={'sha256':sha(p),'bytes':p.stat().st_size}
    data['pointer_sha256']=sha(bundle/'packet/certificate/LATEST.json')
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    (bundle/'BUNDLE_MANIFEST.sha256').write_text(sha(path)+'  BUNDLE_MANIFEST.json\n')
    return sha(path)


def mutate(bundle,kind):
    manifest=json.loads((bundle/'BUNDLE_MANIFEST.json').read_text())
    cert=bundle/'packet/certificate'
    pointer_path=cert/'LATEST.json';pointer=json.loads(pointer_path.read_text())
    state_path=cert/pointer['path'];state=json.loads(state_path.read_text())
    chunk=state['completed_chunks'][0]; chunk_path=cert/chunk['path']
    if kind=='unbound_chunk':
        chunk_path.write_bytes(chunk_path.read_bytes()+b'corrupted')
        return sha(bundle/'BUNDLE_MANIFEST.json')
    if kind=='protocol_bits':
        state['guard']['bits']=191
    else:
        cells=json.loads(gzip.decompress(chunk_path.read_bytes()))
        cell=cells[0]
        if kind=='cell_index': cell['index']=1
        elif kind=='picard_box':cell['picard_box']=[['0','0'] for _ in range(6)]
        elif kind=='whole_cell':cell['whole_cell'][0]=['0','0']
        elif kind=='endpoint':cell['endpoint'][0]=['0','0']
        elif kind=='spurious_event':cell['D_event_overlap']=[['0','0'] for _ in range(6)]
        elif kind=='iteration_count':cell['picard_iterations']=0
        else:raise ValueError(kind)
        chunk_path.write_bytes(gzip.compress(json.dumps(cells,separators=(',',':')).encode(),mtime=0))
        chunk['sha256']=sha(chunk_path)
    state_path.write_text(json.dumps(state,sort_keys=True,separators=(',',':'))+'\n')
    pointer['sha256']=sha(state_path)
    pointer_path.write_text(json.dumps(pointer,sort_keys=True,separators=(',',':'))+'\n')
    return rebound(bundle)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();base=args.bundle.resolve();output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    cases=[
        ('unbound_chunk','Bundle file digest mismatch'),
        ('protocol_bits','Unexpected saved proof protocol'),
        ('cell_index','Discontinuous saved cell index/time'),
        ('picard_box','Exact rational Picard image not strictly inside saved box'),
        ('whole_cell','Saved tube/endpoint fails exact rational Taylor enclosure'),
        ('endpoint','Saved tube/endpoint fails exact rational Taylor enclosure'),
        ('spurious_event','Spurious saved event cell'),
        ('iteration_count','Invalid declared inclusion iteration count'),
        ('nonempty_output','FileExistsError')]
    results=[]
    for kind,expected in cases:
        case=output/kind;case.mkdir()
        bundle=case/'inputs';shutil.copytree(base,bundle)
        for p in [bundle,*bundle.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
        target=case/'run'
        if kind=='nonempty_output':
            target.mkdir();(target/'sentinel.txt').write_text('preserve this prior output\n')
            expected_hash=sha(bundle/'BUNDLE_MANIFEST.json')
        else:expected_hash=mutate(bundle,kind)
        readonly(bundle)
        before={str(p.relative_to(bundle)):sha(p) for p in bundle.rglob('*') if p.is_file()}
        command=[sys.executable,'-B',str(bundle/'verify_kinetic_cells.py'),
                 '--bundle',str(bundle),'--expected-manifest-sha256',expected_hash,
                 '--output',str(target),'--timeout-seconds','30']
        start=time.monotonic()
        run=subprocess.run(command,cwd=bundle,text=True,capture_output=True,timeout=35)
        (case/'stdout.txt').write_text(run.stdout);(case/'stderr.txt').write_text(run.stderr)
        records={}
        for name in ['WORKER_FAILURE.json','SUPERVISOR_FAILURE.json','VERIFICATION_RESULT.json','PORTABLE_RUN.json']:
            p=target/name
            if p.exists():records[name]=json.loads(p.read_text())
        errors=run.stderr+'\n'+json.dumps(records)
        unchanged=all(sha(bundle/n)==h for n,h in before.items())
        passed=(run.returncode!=0 and expected in errors and unchanged and
                'VERIFICATION_RESULT.json' not in records and 'PORTABLE_RUN.json' not in records)
        if kind=='nonempty_output':passed=passed and (target/'sentinel.txt').read_text()=='preserve this prior output\n'
        receipt={'case':kind,'pass':passed,'expected_rejection':expected,
                 'returncode':run.returncode,'elapsed_seconds':time.monotonic()-start,
                 'input_files_unchanged':unchanged,'manifest_sha256':expected_hash,
                 'rebound_fixture':kind not in ['unbound_chunk','nonempty_output'],
                 'worker_failure':records.get('WORKER_FAILURE.json'),
                 'supervisor_failure':records.get('SUPERVISOR_FAILURE.json')}
        (case/'CONTROL_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
        results.append(receipt)
        print(kind,'PASS' if passed else 'FAIL',flush=True)
    report={'pass':all(x['pass'] for x in results),'controls':results,
            'scope':'Nine representative guard/continuity/Picard/Taylor/event failure controls; not exhaustive formal verification or independent scientific review.'}
    (output/'CONTROLS_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['pass']:raise SystemExit(1)


if __name__=='__main__':main()
