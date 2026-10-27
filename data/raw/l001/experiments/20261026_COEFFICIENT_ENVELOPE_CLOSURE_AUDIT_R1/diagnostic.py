"""Bounded runtime-loading diagnostic only; not an authoritative arithmetic audit."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, traceback
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'
PIN='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(value):
    dest=ROOT/'DIAGNOSTIC.json';tmp=ROOT/'DIAGNOSTIC.json.tmp'
    with tmp.open('x') as f:
        json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o444);os.link(tmp,dest);tmp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def delta(before,after):
    return {'added':{p:after[p] for p in after.keys()-before.keys()},
            'missing':{p:before[p] for p in before.keys()-after.keys()},
            'changed':{p:{'before':before[p],'after':after[p]} for p in before.keys()&after.keys() if before[p]!=after[p]}}
def main(lease):
    assert sys.platform=='linux' and not (ROOT/'DIAGNOSTIC.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    source=sha(__file__);start=lease.observed();current=start;records=[]
    for digits in (5000,20000):
        integer=10**digits
        numeric=lease.observed()
        converted=str(integer)
        after_integer=lease.observed()
        # Use a noninteger fraction so both numerator and denominator convert.
        rational=Fraction(integer+1,integer-1)
        after_fraction=lease.observed()
        rational_text=str(rational)
        after_text=lease.observed()
        records.append({'digits':digits,'integer_string_length':len(converted),
            'fraction_string_length':len(rational_text),
            'integer_construction':delta(current,numeric),
            'integer_conversion':delta(numeric,after_integer),
            'fraction_construction':delta(after_integer,after_fraction),
            'fraction_conversion':delta(after_fraction,after_text),
            'runtime_after':after_text})
        current=after_text
    assert sha(__file__)==source
    report={'classification':'RUNTIME_LOADING_DIAGNOSTIC_ONLY','authoritative_audit':False,
            'cpu':cpu,'occupied':occupied,'source_sha256':source,'runtime_start':start,
            'runtime_end':current,'total_difference':delta(start,current),'stages':records,
            'scope':'Two fixed large integer/Fraction construction and decimal-conversion probes; no physical calculation or acceptance-gate relaxation.'}
    put(report)
    print(json.dumps({'classification':report['classification'],'total_difference':report['total_difference'],
                      'stages':[{k:v for k,v in row.items() if k!='runtime_after'} for row in records]}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==PIN
        frozen=json.loads((FLOW/'FROZEN.json').read_text())
        assert frozen['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('runtime_probe_lease',p)
        lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('DIAGNOSTIC_120_SECONDS')))
        main(lease)
    except BaseException as error:
        if not (ROOT/'DIAGNOSTIC.json').exists():
            put({'classification':'TECHNICAL_INCOMPLETE','authoritative_audit':False,
                 'source_sha256':sha(__file__),'error':repr(error),'traceback':traceback.format_exc()})
        raise
    finally:
        signal.alarm(0)
        if lease is not None:
            for handle in lease.handles:handle.close()
