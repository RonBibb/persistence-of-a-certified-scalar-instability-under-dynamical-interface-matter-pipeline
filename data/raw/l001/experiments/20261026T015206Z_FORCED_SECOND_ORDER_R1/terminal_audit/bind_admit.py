"""Independent Linux administrative binding/admission; does not run audit."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
EXPECTED='27b9c8799f3bedef8f49788284549e4ba7cffe5adf7cc5b7c85425c324bb5566'
s=importlib.util.spec_from_file_location('audit_admission_runner',ROOT/'runner.py')
r=importlib.util.module_from_spec(s);sys.modules[s.name]=r;s.loader.exec_module(r)
try:
    assert sys.platform=='linux'
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ADMISSION_CAP_120')));signal.alarm(120)
    cpu,occupied=r.acquire()
    assert r.sha(ROOT/'FROZEN.json')==EXPECTED
    frozen=r.read(ROOT/'FROZEN.json')
    assert str(Path(sys.executable).resolve())==frozen['executable']
    paths=set()
    for p,d in frozen['files'].items():assert r.sha(p)==d,p;paths.add(Path(p))
    # Bind every completed producer receipt, all probe/control outputs and
    # source admissions in this one namespace, including exact raw witnesses.
    paths.update(p for p in ROOT.iterdir() if p.is_file() and p.suffix=='.json')
    for mode in ('controls','probe','production'):
        t=r.read(ROOT/(mode+'_TERMINAL.json'))
        assert t['pass'] is True and t['frozen_sha256']==EXPECTED
        for suffix in ('RUNTIME_BEFORE','RUNTIME_AFTER'):
            for p,d in r.read(ROOT/(mode+'_'+suffix+'.json')).items():assert frozen['files'].get(p)==d and r.sha(p)==d,p
    assert not any(ROOT.glob('*FAILURE.json'))
    for name in ('primary','independent'):
        result=r.read(ROOT/('PRODUCTION_'+name+'.json'))
        assert result['engine']==name and result['all_gates'] is True
        for key in ('raw_lower','raw_upper','FP','FH','Rb_bound','budgets','walls'):assert key in result,key
    assert (ROOT/'PRODUCTION_RESULT.json').is_file()
    paths.update(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.md'))
    # Import the stdlib-only checker without calling main, so actual audit
    # module dependencies are captured prospectively. No Arb or ODE imports.
    spec=importlib.util.spec_from_file_location('bound_audit_source',HERE/'audit.py')
    audit=importlib.util.module_from_spec(spec);sys.modules[spec.name]=audit;spec.loader.exec_module(audit)
    observed=r.observed();paths.update(Path(p) for p in observed)
    files={str(p.resolve()):r.sha(p) for p in sorted(paths)}
    record={'admitted':True,'reviewer':'ab_mechanism_scope','verification_platform':'academic-linux',
            'producer_frozen_sha256':EXPECTED,'executable_realpath':str(Path(sys.executable).resolve()),
            'files':files,'administrative_cpu':cpu,'occupied_cpus':occupied,
            'runtime_observed':observed,'scope':'One unchanged saved-record checker execution via launch.py, 330s, one core/2GiB. No ODE and no scientific result acceptance.',
            'source_review_sha256':r.sha(HERE/'SOURCE_REVIEW.md')}
    audit.save('ADMISSION.json',record)
    print(json.dumps({'admitted':True,'files':len(files),'admission_sha256':r.sha(HERE/'ADMISSION.json'),'cpu':cpu,'audit_executed':False}),flush=True)
finally:
    signal.alarm(0)
    for f in r.handles:f.close()
