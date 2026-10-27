"""Namespace-only wrapper of reviewed independent finite contour arithmetic."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
start=time.time();own=sha(__file__);helper=HERE/'finite_contour_audit.py';helperpin='10104b3108cbe86bde45e9d1b52a4f0857a9a5cbed9f2d7ede87ecb6caefcba4';dest=HERE/'FINITE_CONTOUR_AUDIT_R1.json';lease=None;a=None
if dest.exists():raise AssertionError('NO_RESTART')
try:
 assert sha(helper)==helperpin,'REVIEWED_AUDIT_SOURCE'
 a=load('finite_contour_independent_r1',helper);a.ROOT=a.BASE/'20261027_FINITE_CONTOUR_CERTIFICATE_R1'
 a.ck(sys.platform=='linux' and time.time()<a.CUTOFF-600,'LINUX_WINDOW')
 p=a.BASE/'20261027_SHARED_ADMISSION/lease.py';a.ck(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
 len(str(10**20000))
 lease=load('finite_contour_review_r1_lease',p);lease.ROOT=HERE;lease.acquire();a.ck(time.time()<a.CUTOFF-600,'POST_LEASE_WINDOW')
 signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600)
 report=a.main();a.ck(sha(helper)==helperpin and sha(__file__)==own,'AUDIT_SOURCES_UNCHANGED')
except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=a.COUNT if a else 0)
finally:
 signal.alarm(0)
 if lease:
  for h in lease.handles:h.close()
report.update(audit_source_sha256=own,arithmetic_source_sha256=helperpin,seconds=time.time()-start)
with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
os.chmod(dest,0o444);print(json.dumps(report),flush=True)
if not report['PASS']:raise SystemExit(1)
