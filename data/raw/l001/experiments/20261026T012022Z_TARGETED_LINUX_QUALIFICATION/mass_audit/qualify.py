"""Linux invocation witness: original auditor imported unchanged, stdout captured."""
import sys
sys.dont_write_bytecode=True
import contextlib, datetime, hashlib, importlib.util, json, os, platform, signal, time, traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/'output'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def save(n,v):
    with (HERE/n).open('x') as f: json.dump(v,f,indent=2); f.flush(); os.fsync(f.fileno())
def check():
    a=read(HERE/'ADMISSION.json'); assert a['admitted'] is True
    assert sha(HERE/'FROZEN.json')==a['frozen_sha256']
    b=read(HERE/'FROZEN.json')
    assert str(Path(sys.executable).resolve())==b['executable_realpath']
    for p,d in b['files'].items(): assert sha(p)==d,p
    return b
def runtime():
    mods={}; native={}
    for n,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if p and Path(p).is_file(): mods[n]={'path':str(Path(p).resolve()),'sha256':sha(p)}
    for row in Path('/proc/self/maps').read_text().splitlines():
        f=row.split(None,5)
        if len(f)==6 and f[5].startswith('/') and Path(f[5]).is_file(): native[f[5]]=sha(f[5])
    return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'uname':list(os.uname()),'python':sys.version,'executable':sys.executable,'executable_realpath':str(Path(sys.executable).resolve()),'executable_sha256':sha(sys.executable),'pid':os.getpid(),'affinity':sorted(os.sched_getaffinity(0)),'modules':mods,'mapped_files':native}
def main():
    assert sys.platform=='linux' and not OUT.exists()
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('MASS_AUDIT_CAP_180'))); signal.alarm(180)
    start=time.monotonic(); frozen=check(); OUT.mkdir()
    packet=Path(frozen['packet']); source=packet/'postrun_audit.py'
    save('RUNTIME_BEFORE.json',runtime())
    sys.path.insert(0,frozen['flint_root'])
    spec=importlib.util.spec_from_file_location('unchanged_historical_mass_auditor',source)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    with (OUT/'AUDITOR_STDOUT.json').open('x') as log:
        with contextlib.redirect_stdout(log): module.main(packet)
        log.flush(); os.fsync(log.fileno())
    result=read(OUT/'AUDITOR_STDOUT.json'); old=read(packet/'INDEPENDENT_AUDIT.json')
    assert result['audit_pass'] is True and result['endpoint_certificate'] is True and result['uniform_separation_certificate'] is True
    assert result['classification_independently_derived']=='NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1'
    assert result['checkpoint_count']==288 and result['native_roundtrips_checked']==11808 and result['runtime_libraries_verified']==42
    assert result['new_physical_integration_performed'] is False
    for key in ('result_sha256','terminal_sha256','audit_source_sha256','guard','exact_signs'): assert result[key]==old[key],key
    assert result['audit_source_sha256']==sha(source)
    check(); save('RUNTIME_AFTER.json',runtime())
    save('RESULT.json',{'status':'CURRENT_LINUX_HISTORICAL_MASS_AUDITOR_VERIFIED','auditor_stdout_sha256':sha(OUT/'AUDITOR_STDOUT.json'),'original_auditor_sha256':sha(source),'wall_seconds':time.monotonic()-start,'new_ode_solves':0,'scope':'Fresh runtime/integrity/exact-bound auditor invocation; not a full interval-IVP reconstruction.'})
    signal.alarm(0)
if __name__=='__main__':
    try: main()
    except BaseException as e:
        if not (HERE/'FAILURE.json').exists(): save('FAILURE.json',{'error':repr(e),'traceback':traceback.format_exc(),'classification':'MASS_AUDIT_QUALIFICATION_INCOMPLETE'})
        raise
