import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROW = HERE.parent / 'research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01'

def main():
    names = ['run.py', 'FREEZE.json', 'BINDINGS.json', 'TERMINAL.json', 'RESULT_INTEGRITY.json']
    names += [f'flows/{flow}/{file}' for flow in ('uniform_root', 'uniform_center') for file in ('RESULT.json', 'CELLS.json')]
    records = []
    for name in names:
        source = ROW / name
        if any(p.is_symlink() for p in [source, *source.parents]):
            raise ValueError('symlink')
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        target = HERE / 'inputs' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError('copy mismatch')
        records.append({'path': 'inputs/' + name, 'origin_relative_to_experiments': str(source.relative_to(HERE.parent)), 'sha256': digest, 'bytes': target.stat().st_size, 'hash_role': 'snapshot integrity, not independent historical authentication'})
    (HERE / 'SOURCE_BINDINGS.json').write_text(json.dumps({'files': records}, indent=2) + '\n')
    metadata = sorted(ROW.glob('*.json'))
    search = {}
    for flow in ('uniform_root', 'uniform_center'):
        digest = hashlib.sha256((ROW / 'flows' / flow / 'RESULT.json').read_bytes()).hexdigest()
        search[flow] = {'flow_result_sha256': digest, 'matching_original_top_level_metadata': [str(p.relative_to(ROW)) for p in metadata if digest in p.read_text()]}
    (HERE / 'BOUNDED_PROVENANCE_SEARCH.json').write_text(json.dumps({'searched_original_top_level_metadata': [str(p.relative_to(ROW)) for p in metadata], 'results': search, 'source_inspection': 'Original flow() caches a plain RESULT.json with trace_sha256, source_sha256 and guard; no content-addressed flow filename or separate flow-result digest is emitted by that function.', 'limit': 'No claim that every external historical record has been searched.'}, indent=2) + '\n')
    print(json.dumps({'copied': len(records), 'bytes': sum(r['bytes'] for r in records)}))

if __name__ == '__main__':
    main()
