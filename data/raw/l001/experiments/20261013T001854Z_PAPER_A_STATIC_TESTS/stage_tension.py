"""Copy tension proof records only; never import their producer."""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROW = EXP / 'research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01'
PARENT = EXP / 'academic2-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    terminal = json.loads((ROW / 'TERMINAL.json').read_text())
    freeze = json.loads((ROW / 'FREEZE.json').read_text())
    bindings = json.loads((ROW / 'BINDINGS.json').read_text())
    anchors = {
        'RESULT.json': ('1c75769919952469c222a2fbc45cedbad2531b1e37b83de3bb3f815a8a0b07cd', 'prior selected-claim binding and original terminal result_sha256'),
        'RESULT_INTEGRITY.json': (terminal['artifacts']['integrity_sha256'], 'original terminal integrity_sha256'),
        'FREEZE.json': (terminal['artifacts']['freeze_sha256'], 'original terminal freeze_sha256'),
        'BINDINGS.json': (freeze['bindings_sha256'], 'original freeze bindings_sha256'),
        'D2A_TRANSPORT.json': (terminal['artifacts']['d2a_transport_sha256'], 'original terminal d2a_transport_sha256'),
        'run.py': (next(v for k, v in bindings['sources'].items() if k.endswith('/run.py')), 'original frozen BINDINGS sources'),
        'flows/uniform_root/RESULT.json': (None, 'current saved-flow snapshot; source_sha256 and guard are cross-checked against original producer and freeze'),
        'flows/uniform_center/RESULT.json': (None, 'current saved-flow snapshot; source_sha256 and guard are cross-checked against original producer and freeze'),
        'TERMINAL.json': (None, 'original terminal authority record, newly snapshot-hashed'),
    }
    records = []
    for relative, (expected, provenance) in anchors.items():
        source = ROW / relative
        if any(p.is_symlink() for p in [source, *source.parents]):
            raise ValueError('symlink')
        actual = sha(source)
        if expected and actual != expected:
            raise ValueError('frozen hash mismatch: ' + relative)
        dest = HERE / 'tension_inputs' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        if sha(dest) != actual:
            raise ValueError('copy mismatch')
        records.append({'path': str(dest.relative_to(HERE)), 'origin_relative_to_experiments': str(source.relative_to(EXP)), 'sha256': actual, 'bytes': dest.stat().st_size, 'prior_binding': provenance, 'prior_bound_sha256': expected})
    expected = 'eb16a5e4bb027aaf598f954bdd48d51611a1c48ffc7669afabb6b3f3a3dea8a5'
    if sha(PARENT) != expected:
        raise ValueError('D2A parent mismatch')
    dest = HERE / 'tension_inputs/d2a_parent.json'
    shutil.copyfile(PARENT, dest)
    records.append({'path': str(dest.relative_to(HERE)), 'origin_relative_to_experiments': str(PARENT.relative_to(EXP)), 'sha256': expected, 'bytes': dest.stat().st_size, 'prior_binding': 'original tension bindings inputs and transport parent_sha256', 'prior_bound_sha256': expected})
    (HERE / 'TENSION_SOURCE_BINDINGS.json').write_text(json.dumps({'files': records, 'snapshot_limitation': 'Uniform saved-flow records are current snapshots, not separately terminal-hash-bound; reconstructed outputs must exactly reproduce the previously bound final result.'}, indent=2) + '\n')
    print(json.dumps({'copied_records': len(records)}))

if __name__ == '__main__':
    main()
