"""Atomic outward-canonicalized interval recovery, inherited algorithm."""
import hashlib,json,os,tempfile
from pathlib import Path
from datetime import datetime,timezone
from flint import arb,fmpq


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pack(x):
    if isinstance(x,arb):
        if not x.is_finite():raise ArithmeticError('Nonfinite native ball')
        for _ in range(3):
            raw=[[int(v) for v in x.mid().man_exp()],[int(v) for v in x.rad().man_exp()]]
            y=arb(tuple(raw[0]),tuple(raw[1]))
            if y.mid()==x.mid() and y.rad()==x.rad():return {'_arb_native':raw}
            if not y.mid()==x.mid() or not y.rad()>=x.rad():raise RuntimeError('Canonicalization shrank/shifted interval')
            x=y
        raise RuntimeError('Native ball did not canonicalize')
    if isinstance(x,fmpq):return {'_rational':str(x)}
    if isinstance(x,dict):return {k:pack(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [pack(v) for v in x]
    return x
def unpack(x):
    if isinstance(x,dict):
        if '_arb_native' in x:
            m,r=x['_arb_native'];v=arb(tuple(m),tuple(r))
            assert [[int(i) for i in v.mid().man_exp()],[int(i) for i in v.rad().man_exp()]]==x['_arb_native']
            return v
        if '_rational' in x:return fmpq(x['_rational'])
        return {k:unpack(v) for k,v in x.items()}
    if isinstance(x,list):return [unpack(v) for v in x]
    return x
def fingerprint(x):return hashlib.sha256(json.dumps(pack(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def atomic(p,x,immutable=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if immutable and p.exists():raise RuntimeError('Refuse overwrite: '+str(p))
    fd,name=tempfile.mkstemp(prefix=p.name+'.uncommitted-',dir=p.parent)
    with os.fdopen(fd,'w') as f:
        json.dump(pack(x),f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(name,p)
    if immutable:p.chmod(0o444)
def save(output,state,guard):
    body={'guard':guard,'state':pack(state)}
    restored=unpack(body['state']);state.clear();state.update(restored)
    digest=fingerprint(body);name=f"checkpoints/{state['task_index']:02d}-{state['cell_index']:06d}-{digest}.json"
    if not (output/name).exists():atomic(output/name,body,True)
    atomic(output/'LATEST.json',{'guard':guard,'path':name,'digest':digest})
    atomic(output/'STATUS.json',{'state':'RUNNING','guard':guard,'utc':now(),
        'task_index':state['task_index'],'cell_index':state['cell_index'],'elapsed_seconds':state['elapsed_seconds'],
        'last_atomic_checkpoint':name,'checkpoint_digest':digest})
def load(output,guard):
    ptr=read(output/'LATEST.json');assert ptr['guard']==guard
    p=(output/ptr['path']).resolve();assert p.parent==(output/'checkpoints').resolve()
    body=read(p);assert body['guard']==guard and fingerprint(body)==ptr['digest']
    return unpack(body['state'])
