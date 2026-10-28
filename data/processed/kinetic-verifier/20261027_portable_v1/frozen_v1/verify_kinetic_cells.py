#!/usr/bin/env python3
"""Portable orchestration of the pristine exact-Fraction saved-cell verifier.

No numerical routine is copied, patched or replaced. Historical admission binds
historical content; it is not approval of this new launcher or execution.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
import traceback
import types

PRISTINE_SHA256 = '4fb8bad4ef5f197074f6fc5709fe023753a523185c26f26546de64c62d7284f7'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path, data):
    temporary = path.with_name(path.name+'.tmp')
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
    os.replace(temporary, path)


def inside(path, root):
    return path == root or root in path.parents


def safe(root, name):
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe bundle-relative path')
    path = (root/relative).resolve()
    if not inside(path, root):
        raise ValueError('Bundle path escapes its root')
    return path


def checked_manifest(bundle, expected):
    if not re.fullmatch('[0-9a-f]{64}', expected):
        raise ValueError('Require an explicit SHA-256 trust anchor')
    manifest = bundle/'BUNDLE_MANIFEST.json'
    if sha(manifest) != expected:
        raise RuntimeError('Bundle manifest digest mismatch')
    data = json.loads(manifest.read_text())
    if data['schema'] != 'kinetic-saved-cell-bundle-v1':
        raise RuntimeError('Unsupported bundle schema')
    for name, value in data['files'].items():
        path = safe(bundle, name)
        if not path.is_file() or sha(path) != value['sha256']:
            raise RuntimeError('Bundle file digest mismatch: '+name)
    if sha(safe(bundle, data['pristine_source'])) != PRISTINE_SHA256:
        raise RuntimeError('Pristine historical verifier identity mismatch')
    if sha(Path(__file__).resolve()) != data['files']['verify_kinetic_cells.py']['sha256']:
        raise RuntimeError('Launcher differs from bound bundle copy')
    return data


def path_guard(module, bundle, data):
    packet = module.PACKET
    admission_path = packet/'FRACTION_VERIFIER_ADMISSION.json'
    admission = json.loads(admission_path.read_text())
    if not admission['admitted']:
        raise RuntimeError('Historical content admission is not affirmative')
    candidate = module.bounded_path(packet, admission['candidate'])
    if sha(candidate) != admission['candidate_sha256']:
        raise RuntimeError('Changed historical verifier candidate')
    for name, expected in json.loads(candidate.read_text())['files'].items():
        if sha(module.bounded_path(packet, name)) != expected:
            raise RuntimeError('Changed historical candidate file: '+name)
    sources = json.loads((packet/'INPUTS.json').read_text())['files']
    if len(sources) != len(data['original_to_snapshot']):
        raise RuntimeError('Incomplete original-to-snapshot mapping')
    mapping = {entry['historical_source']:entry for entry in data['original_to_snapshot']}
    if len(mapping) != len(sources):
        raise RuntimeError('Duplicate original-to-snapshot mapping')
    for item in sources:
        mapped = mapping[item['source']]
        snapshot = module.bounded_path(packet, item['snapshot'])
        if (safe(bundle, mapped['path']) != snapshot.resolve() or
                mapped['sha256'] != item['sha256'] or sha(snapshot) != item['sha256']):
            raise RuntimeError('Changed bound original/snapshot identity')
    return sha(candidate), sha(admission_path)


def read_audit(bundle, output):
    reads = set()
    runtime_roots = {Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve(),
                     Path(os.__file__).resolve().parent}

    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        flags = args[2]
        writing = flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)
        if writing:
            if not inside(path, output):
                raise PermissionError('Write outside fresh output directory: '+str(path))
        else:
            if inside(path, bundle):
                reads.add(str(path.relative_to(bundle)))
            elif inside(path, output):
                pass
            elif any(inside(path, root) for root in runtime_roots):
                reads.add('python-runtime/'+path.name)
            else:
                raise PermissionError('Read outside bundle/output/Python runtime: '+str(path))
    sys.addaudithook(audit)
    return reads


def worker(args, bundle, output):
    reads = read_audit(bundle, output)
    data = checked_manifest(bundle, args.expected_manifest_sha256)
    launch = json.loads((output/'LAUNCH.json').read_text())
    deadline = dt.datetime.fromisoformat(launch['deadline_utc'])
    remaining = (deadline-dt.datetime.now(dt.timezone.utc)).total_seconds()
    if remaining <= 0:
        raise TimeoutError('Fresh portable verification deadline elapsed')
    source = safe(bundle, data['pristine_source'])
    module = types.ModuleType('pristine_saved_cell_verifier')
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), 'exec'), module.__dict__)
    module.PACKET = safe(bundle, data['packet'])
    module.DEADLINE = deadline
    module.guard = lambda:path_guard(module, bundle, data)
    signal.signal(signal.SIGALRM, module.interruption)
    signal.setitimer(signal.ITIMER_REAL, remaining)
    started = time.monotonic()
    try:
        result = module.check_saved(safe(bundle, data['certificate']), data['pointer_sha256'], output)
        if (not result['complete'] or result['verified_cells'] != data['expected_cells'] or
                len(result['verified_chunks']) != data['expected_chunks'] or
                not result['certified_half_S_gate'] or not all(result['gates'].values())):
            raise RuntimeError('Full portable saved-cell acceptance gate failed')
        checked_manifest(bundle, args.expected_manifest_sha256)
        atomic(output/'PORTABLE_RUN.json', {
            'status':'PASS_PORTABLE_EXACT_FRACTION_SAVED_CELLS',
            'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'elapsed_worker_seconds':time.monotonic()-started,
            'pristine_source_sha256':PRISTINE_SHA256,
            'launcher_sha256':sha(Path(__file__).resolve()),
            'manifest_sha256':args.expected_manifest_sha256,
            'python':sys.version, 'python_executable_sha256':sha(Path(sys.executable).resolve()),
            'verified_cells':result['verified_cells'], 'verified_chunks':len(result['verified_chunks']),
            'all_original_gates':result['gates'], 'input_manifest_unchanged':True,
            'runtime_reads':sorted(reads), 'outside_scientific_input_reads':0,
            'numerical_functions_replaced':[],
            'overrides':['PACKET','DEADLINE','guard'],
            'historical_admission_role':'Historical content binding only; not approval of this launcher or execution.',
            'new_ivp_or_root_solves':0,
            'scope':'Inductive verification of saved Picard/Taylor cells and coarse gates. Root existence and analytical kinetic theorem remain inherited; no nonlinear source/inverse audit.'})
    except BaseException as error:
        atomic(output/'WORKER_FAILURE.json', {
            'status':'REJECTED_OR_HELD','type':type(error).__name__,'error':str(error),
            'stage':dict(module.STAGE),'traceback':traceback.format_exc(),
            'runtime_reads':sorted(reads),'scientific_acceptance':False})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',required=True,type=Path)
    parser.add_argument('--expected-manifest-sha256',required=True)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--timeout-seconds',type=int,default=600)
    parser.add_argument('--_worker',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    bundle=args.bundle.resolve(); output=args.output.resolve()
    if inside(output,bundle) or inside(bundle,output):
        raise ValueError('Keep inputs and outputs in separate trees')
    if not 1 <= args.timeout_seconds <= 3600:
        raise ValueError('Timeout must be between 1 and 3600 seconds')
    if args._worker:
        worker(args,bundle,output)
        return
    # Refuse existing paths, including empty directories, to preserve prior runs.
    output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    try:
        checked_manifest(bundle,args.expected_manifest_sha256)
        deadline=dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=args.timeout_seconds)
        atomic(output/'LAUNCH.json',{'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'deadline_utc':deadline.isoformat(),'timeout_seconds':args.timeout_seconds,
              'manifest_sha256':args.expected_manifest_sha256,'new_execution':True})
        command=[sys.executable,'-B',str(Path(__file__).resolve()),'--bundle',str(bundle),
                 '--expected-manifest-sha256',args.expected_manifest_sha256,'--output',str(output),
                 '--timeout-seconds',str(args.timeout_seconds),'--_worker']
        with (output/'worker.stdout').open('w') as stdout,(output/'worker.stderr').open('w') as stderr:
            finished=subprocess.run(command,cwd=bundle,stdout=stdout,stderr=stderr,
                                    timeout=max(0.01,args.timeout_seconds-(time.monotonic()-started)),check=False)
        if finished.returncode:
            raise RuntimeError('Portable worker rejected inputs or failed; see worker records')
        checked_manifest(bundle,args.expected_manifest_sha256)
        print(json.dumps({'status':'PASS_PORTABLE_EXACT_FRACTION_SAVED_CELLS',
                         'elapsed_seconds':time.monotonic()-started,'output':str(output)}))
    except BaseException as error:
        atomic(output/'SUPERVISOR_FAILURE.json',{'status':'REJECTED_OR_HELD',
               'type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc(),
               'scientific_acceptance':False})
        raise


if __name__=='__main__':
    main()
