"""Seal the reviewed identity experiment and preserve its failed predecessor.

Publication only: no numerical-flow imports, no evolution and no source edits.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
FAILED = ROOT.parent / 'lin-c4-evolution-identity-20261006T044000Z'
assert ROOT.name == 'lin-c4-evolution-identity-r1-20261006T051000Z'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path, data):
    if path.exists():
        raise RuntimeError('Refuse overwrite: ' + str(path))
    fd, name = tempfile.mkstemp(prefix=path.name + '.uncommitted-', dir=path.parent)
    with os.fdopen(fd, 'w') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(name, path)
    path.chmod(0o444)


def verify_bindings(root):
    binding = read(root / 'BINDINGS.json')
    guard = sha(root / 'BINDINGS.json')
    assert read(root / 'FREEZE_RECORD.json')['guard'] == guard
    for name, digest in binding['sources'].items():
        assert sha(root / name) == digest, name
    for name, digest in binding['inputs'].items():
        assert sha(Path(name)) == digest, name
    assert sha(root / 'PREFLIGHT_REVIEW.md') == binding['review_sha256']
    assert sha(Path(binding['preflight']['path'])) == binding['preflight']['sha256']
    runtime = binding['runtime']
    for name, digest in runtime['libraries'].items():
        assert sha(Path(name)) == digest, name
    return guard, binding


def manifest(root, classification, utc):
    entries = []
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        if path.name == 'MANIFEST.json':
            raise RuntimeError('Already sealed: ' + str(root))
        assert '__pycache__' not in path.parts, str(path)
        if '.uncommitted-' in path.name:
            relative = path.relative_to(root)
            assert len(relative.parts) == 3 and relative.parts[0].startswith('control-')
            assert relative.parts[1:] == ('split','LATEST.json.uncommitted-fixture')
            assert read(path) == {'invalid':True}, 'Only the known preflight interruption fixture is allowed'
        path.chmod(0o444)
        entries.append({'path':str(path.relative_to(root)), 'bytes':path.stat().st_size,
                        'sha256':sha(path)})
    atomic(root / 'MANIFEST.json', {'classification':classification, 'entries':entries,
           'sealed_utc':utc, 'exclusions':['MANIFEST.json self reference'],
           'synthetic_uncommitted_fixtures':'Preserved preflight-only invalid-pointer controls; never production checkpoints.'})
    assert all(sha(root / row['path']) == row['sha256'] for row in entries)
    return len(entries)


def main():
    assert len(sys.argv) == 1, 'No optional publication overrides'
    assert not (ROOT / 'RESULT.json').exists() and not (ROOT / 'MANIFEST.json').exists()
    assert not (FAILED / 'RESULT.json').exists() and not (FAILED / 'MANIFEST.json').exists()
    guard, binding = verify_bindings(ROOT)
    old_guard, old_binding = verify_bindings(FAILED)
    assert binding['config'] == old_binding['config']
    audit = read(ROOT / 'INDEPENDENT_AUDIT.json')
    spatial = read(ROOT / 'SPATIAL_ENCLOSURES.json')
    replay_failure = read(ROOT / 'NUMERICAL_READBACK_FAILURE.json')
    replay_checkpoint = read(ROOT / 'readback/case0-p80.json')
    assert not (ROOT / 'NUMERICAL_READBACK.json').exists()
    assert audit['overall'] == 'PASS' and audit['inputs_unchanged'] is True
    assert audit['finite_jet_target_identification_accepted']
    assert audit['mode_source_unique_in_inherited_bracket']
    assert not audit['full_numerical_representation_admission_accepted']
    assert not audit['bounded_identification_accepted']
    assert spatial['passed'] and replay_checkpoint['passed']
    assert guard == audit['guard'] == spatial['guard'] == replay_failure['guard'] == replay_checkpoint['guard']
    assert audit['spatial_enclosures_sha256'] == sha(ROOT / 'SPATIAL_ENCLOSURES.json')
    assert audit['numerical_readback_sha256'] is None
    assert audit['numerical_readback_failure_sha256'] == sha(ROOT / 'NUMERICAL_READBACK_FAILURE.json')
    audit_sources = [path for path in (ROOT / 'audit').rglob('*.py')
                     if sha(path) == audit['audit_source_sha256']]
    assert len(audit_sources) == 1
    classification = audit['scientific_classification']
    assert classification and any(word in classification for word in ('PARTIAL','INCOMPLETE'))
    assert [row['task'] for row in spatial['tasks']] == binding['config']['flow_order']
    assert all(row['passed'] and row['cells'] == 16365 and row['new_evolution_steps'] == 0
               for row in spatial['tasks'])
    assert replay_checkpoint['case'] == 0 and replay_checkpoint['dps'] == 80
    assert replay_checkpoint['new_evolution_steps'] == 0
    assert replay_checkpoint['rigorous_lapse_error_bound'] is None
    assert replay_checkpoint['rigorous_inverse_map_error_bound'] is None
    assert replay_failure['status'] == 'FAILED_CLOSED'
    assert replay_failure['automatic_restart_allowed'] is False
    assert replay_failure['error'] == 'Frozen representation replay gate'
    assert sorted(path.name for path in (ROOT / 'readback').glob('*.json')) == ['case0-p80.json']
    for name in ('RESULT_REPORT.md', 'POSTRUN_REVIEW.md', 'REPAIR_RECORD.md'):
        assert (ROOT / name).is_file()
    assert 'Draft pending' not in (ROOT / 'RESULT_REPORT.md').read_text()
    old_failure = read(FAILED / 'RUN_FAILURE.json')
    assert old_failure['guard'] == old_guard
    assert not list((FAILED / 'output').rglob('checkpoints/*.json'))
    workers = []
    for line in subprocess.check_output(['ps','-eo','pid=,args='], text=True).splitlines():
        if not any(str(root) in line for root in (ROOT, FAILED)):
            continue
        if any(marker in line for marker in ('identity_run.py run', 'numerical_readback.py', '/audit/')):
            workers.append(line.strip())
    assert not workers, workers
    utc = datetime.now(timezone.utc).isoformat()
    liveness = {'utc':utc, 'matching_numerical_processes':workers,
                'scope':'These two identity attempts only. Other research lines untouched.'}
    atomic(ROOT / 'FINAL_LIVENESS.json', liveness)
    atomic(FAILED / 'FINAL_LIVENESS.json', liveness)
    atomic(FAILED / 'RESULT.json', {
        'status':'TECHNICAL_INCOMPLETE', 'classification':'EXACT_DECIMAL_PARSER_FAILED_BEFORE_FIRST_CELL',
        'guard':old_guard, 'accepted_physical_cells':0, 'physical_time_steps':0,
        'failure_sha256':sha(FAILED / 'RUN_FAILURE.json'), 'immutable_failure_preserved':True,
        'implementation_only_successor':ROOT.name, 'sealed_utc':utc})
    old_count = manifest(FAILED, 'EXACT_DECIMAL_PARSER_FAILED_BEFORE_FIRST_CELL', utc)
    artifacts = ['SPATIAL_ENCLOSURES.json','NUMERICAL_READBACK_FAILURE.json','readback/case0-p80.json','INDEPENDENT_AUDIT.json',
                 'audit/FAILED_REPLAY_DIAGNOSTIC.json','audit/diagnose_failed_replay.py',
                 str(audit_sources[0].relative_to(ROOT)), 'POSTRUN_REVIEW.md','RESULT_REPORT.md',
                 'FINAL_LIVENESS.json','REPAIR_RECORD.md']
    atomic(ROOT / 'RESULT.json', {
        'status':'COMPLETE_WITH_INCOMPLETE_NUMERICAL_ADMISSION', 'classification':classification, 'guard':guard,
        'independently_accepted_record':True, 'numerical_admission_passed':False,
        'evidence_class':'INITIAL_FAMILY_IDENTIFICATION_WITH_PARTIAL_NUMERICAL_ERROR_ADMISSION',
        'exact_shared_amplitude_interval':['-1/200000','1/200000'],
        'source_mode_unique_in_inherited_bracket':True,
        'finite_jet_gauge_bridge_checks':15,
        'spatial_flows':3, 'accepted_spatial_cells':sum(row['cells'] for row in spatial['tasks']),
        'independently_checked_checkpoints':audit['checkpoint_count'],
        'independently_checked_native_balls':audit['native_ball_count'],
        'independently_checked_files':audit['checked_unique_file_count'],
        'new_time_evolution_steps':0,
        'rigorous_error_scope':{'whole_domain_source_fields':True,'signed_prepared_material_fields':True,
            'exact_conformal_lapse':False,'exact_inverse_coordinate_map':False,
            'distinct_zero_case_metric_correction':False,'continuum_time_evolution':False},
        'numerical_replay':{'requested_cases':[0,3,4],'grid_degrees':[160,192],
            'requested_decimal_precisions':[80,100], 'absolute_gate':'1e-50','all_passed':False,
            'completed_case_precision_pairs':[[0,80]], 'failed_case_precision_pair':[0,100],
            'signed_replays_not_executed':True, 'failure_preserved':True},
        'signed_material_error_bounds':{row['task']:dict(zip(row['field_order'],row['max_error_bounds_exact']))
                                        for row in spatial['tasks'] if row['task'] != 'mode'},
        'integration_seconds':sum(row['elapsed_seconds'] for row in spatial['tasks']),
        'completed_readback_case_seconds':replay_checkpoint['seconds'],
        'failed_predecessor':{'name':FAILED.name,'guard':old_guard,
            'manifest_sha256':sha(FAILED / 'MANIFEST.json'),'files':old_count},
        'artifacts':{name:sha(ROOT / name) for name in artifacts},
        'live_numerical_processes':workers,'no_automatic_successor':True,
        'limits':['Initial finite-jet identity only, not all-order wall compatibility or spacetime existence',
                  'Saved numerical fields are approximations, not exact certified solutions',
                  'Reported interval error bounds are not ppm accuracy claims',
                  'No amplitude enlargement, parameter-neighborhood identification or P16/MOTS bridge',
                  'No collapse, causal horizon, child-universe or halo conclusion'],
        'sealed_utc':utc})
    atomic(ROOT / 'TERMINAL_CHECKPOINT.json', {'status':'COMPLETE','classification':classification,
           'guard':guard,'result_sha256':sha(ROOT / 'RESULT.json'),'utc':utc,
           'restart_allowed':False})
    count = manifest(ROOT, classification, utc)
    print(json.dumps({'status':'SEALED','classification':classification,'files':count,
        'result_sha256':sha(ROOT / 'RESULT.json'),'manifest_sha256':sha(ROOT / 'MANIFEST.json'),
        'failed_attempt_files':old_count}, indent=2))


if __name__ == '__main__':
    main()
