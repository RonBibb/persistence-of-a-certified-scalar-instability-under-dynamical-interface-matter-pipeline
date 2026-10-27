"""Bounded Linux qualification of the all-order compatibility induction."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_GROWING_NEUTRAL_COMPONENT_MAP'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';DEADLINE=1793039120
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def main(lease):
    pin='a189065e25d7f9eb386ca71ee4baf8d99c5a99a78cd60884e37afe7c40d48753'
    need(sha(PARENT/'TERMINAL.json')==pin,'OFF_SHELL_COMPONENT_PIN');t=read(PARENT/'TERMINAL.json');need(t['pass_status'],'COMPONENT_PASS')
    inputs={str(PARENT/'TERMINAL.json'):pin}
    for n,k in (('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256')):
        need(sha(PARENT/n)==t[k],'COMPONENT_RECORD');inputs[str(PARENT/n)]=t[k]
    for group in ('inputs','sources','runtime'):
        for p,h in read(PARENT/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_CLOSURE');inputs[p]=h
    paper=Path('/media/psf/Home/Research/papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md')
    need(paper.is_file(),'INSPECTED_MANUSCRIPT');inputs[str(paper)]=sha(paper)
    code=load('neutral_compatibility_controls',ROOT/'check.py')
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP');inputs[str(pylong)]=sha(pylong)
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'};runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,off_shell_component_terminal_sha256=pin))
    result=code.run(ROOT);need(result['pass'],'CONTROLS_PASS')
    need(lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'SOURCE_UNCHANGED')
    result.update(classification='ALL_ORDER_NEUTRAL_FORMAL_SOURCE_COMPATIBILITY_QUALIFIED',component_map='Separately qualified from exact five-dimensional Christoffel/Ricci construction; standard contracted Bianchi theorem inherited.',scope='Analytic induction and exact algebraic checks establish formal bulk source compatibility for positive growing harmonics, given solved lower orders and exact background. Wall compatibility retains its explicitly named Codazzi/material-exchange premises. No convergence, complex-source norm or finite-amplitude solution is established.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')));print(json.dumps(result),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+180<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('neutral_compatibility_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('COMPATIBILITY_180_SECONDS')));signal.alarm(180)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
