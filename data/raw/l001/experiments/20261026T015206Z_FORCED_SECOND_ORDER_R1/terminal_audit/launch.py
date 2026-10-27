"""One-core admitted saved-record audit; no producer writes or ODE replay."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
r=load('audit_lease_runner',ROOT/'runner.py')
def main():
    assert sys.platform=='linux'
    ad=r.read(HERE/'ADMISSION.json');assert ad['admitted'] is True
    assert r.sha(ROOT/'FROZEN.json')==ad['producer_frozen_sha256']
    for p,d in ad['files'].items():assert r.sha(p)==d,p
    cpu,occupied=r.acquire()
    # Common lease is in producer directory but no producer scientific record
    # is opened or altered; audit output is confined to terminal_audit.
    audit=load('independent_saved_record_audit',HERE/'audit.py')
    before=r.observed()
    allowed=dict(r.read(ROOT/'FROZEN.json')['files']);allowed.update(ad['files'])
    assert all(allowed.get(p)==d for p,d in before.items()),'AUDIT_UNBOUND_RUNTIME_BEFORE'
    audit.save('RUNTIME_BEFORE.json',before)
    start=time.monotonic();audit.main()
    after=r.observed();audit.save('RUNTIME_AFTER.json',after)
    assert all(allowed.get(p)==d for p,d in after.items()),'AUDIT_UNBOUND_RUNTIME_AFTER'
    for p,d in ad['files'].items():assert r.sha(p)==d,p
    audit.save('TERMINAL.json',{'pass':True,'cpu':cpu,'occupied_cpus':occupied,'seconds':time.monotonic()-start,
        'producer_frozen_sha256':ad['producer_frozen_sha256'],'runtime_coverage':True})
try:
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_CAP_330')));signal.alarm(330)
    main()
finally:
    signal.alarm(0)
    for f in r.handles:f.close()
