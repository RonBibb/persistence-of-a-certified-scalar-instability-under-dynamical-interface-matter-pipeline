import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z'

def main():
    acceptance = json.loads((SOURCE / 'RESULT.json').read_text())
    binding = json.loads((SOURCE / 'BINDINGS.json').read_text())
    files = {
        'RESULT.json': ('e97910ac0fdf5acbdc224438b03ee3aafbba06547356e347136d5d968bd2df94', 'prior Paper A selected-claim binding'),
        'output/RESULT.json': (acceptance['artifacts']['output/RESULT.json'], 'final acceptance artifacts'),
        'INDEPENDENT_AUDIT.json': (acceptance['artifacts']['INDEPENDENT_AUDIT.json'], 'final acceptance artifacts'),
        'BINDINGS.json': ('fca1b49a652afc1832e61e31e5e8c47dc86d63144de791211c89372f55a82e00', 'frozen producer guard'),
        'CONTRACT.md': (binding['source']['CONTRACT.md'], 'frozen source binding'),
        'runner.py': (binding['source']['runner.py'], 'frozen source binding; text only'),
    }
    records = []
    for relative, (expected, authority) in files.items():
        source = SOURCE / relative
        if any(p.is_symlink() for p in [source, *source.parents]):
            raise ValueError('symlink')
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError('frozen byte mismatch')
        target = HERE / 'mode_inputs' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError('copy mismatch')
        records.append({'path': str(target.relative_to(HERE)), 'origin_relative_to_experiments': str(source.relative_to(HERE.parent)), 'sha256': expected, 'bytes': target.stat().st_size, 'prior_binding': authority})
    (HERE / 'MODE_SOURCE_BINDINGS.json').write_text(json.dumps({'files': records}, indent=2) + '\n')
    print(json.dumps({'copied_records': len(records)}))

if __name__ == '__main__':
    main()
