"""Bounded-memory atomic evidence publication; no resume interface."""
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_text())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def put(name,value):
    path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('x') as f:json.dump(value,f,separators=(',',':'));f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o444);os.link(tmp,path);tmp.unlink()
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return sha(path)
