import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'academic2-event-horizon'
FILES = {
    'global.json': ('lin-d1-global-first-event-uniqueness-r1-20261004T134600Z/output/RESULT.json', '7bfee6d3300cad92ac95325111ccd688bccb2accdf9fb8d8d1415ec06f936dc4'),
    'primary_root.json': ('lin-d1-high-resolution-confirmation-20261002T015100Z/RESULT.json', '07b22a8bc27eb1884c5607004c8fa8590d603be6e6157f7332369fcbaaf278f9'),
    'independent_root.json': ('lin-d1-independent-ode-replay-20261002T225837Z/output/r1/RESULT.json', '41077a7977079705dbd49379f2f9ecb3fe9c007c518b02277aba6aa4b8df7d16'),
    'isolation.json': ('lin-d1-fixed-d-continuation-dimension-audit-r1-20261004T150137Z/output/RESULT.json', 'f7880e846f248633a547723d1f7e82a7fa9f799d20bfd85b0de01ca4d4ca1faa'),
}

def main():
    (HERE / 'inputs').mkdir(exist_ok=True)
    records = []
    for name, (relative, expected) in FILES.items():
        source = SOURCE / relative
        if any(p.is_symlink() for p in [source, *source.parents]):
            raise ValueError('source symlink')
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('frozen source hash mismatch')
        target = HERE / 'inputs' / name
        shutil.copyfile(source, target)
        if target.read_bytes() != data:
            raise ValueError('copy mismatch')
        records.append({'path': 'inputs/' + name, 'source_relative_to_academic2_event_horizon': relative, 'sha256': expected, 'bytes': len(data)})
    (HERE / 'SOURCE_BINDINGS.json').write_text(json.dumps({'files': records}, indent=2) + '\n')
    print(json.dumps({'copied_inputs': len(records)}))

if __name__ == '__main__':
    main()
