"""Non-scientific inspection of lazy Python integer-conversion imports."""
import sys,json,importlib.util,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
base=Path(__file__).resolve().parent.parent
p=base/'20261027_SHARED_ADMISSION/lease.py'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862'
s=importlib.util.spec_from_file_location('diag_lease',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parent
try:
 m.acquire();before=m.observed();len(str(10**20000));after=m.observed()
 print(json.dumps(dict(added=sorted(set(after)-set(before)),changed=[p for p in before if p in after and before[p]!=after[p]],removed=sorted(set(before)-set(after))),indent=2),flush=True)
finally:
 for h in m.handles:h.close()
