"""Post-terminal leased integrity verification and outward display; no ODE."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('terminal_reader_runner',ROOT/'runner.py')
r=importlib.util.module_from_spec(s);sys.modules[s.name]=r;s.loader.exec_module(r)
def dec(q,upper):
    q=Q(q)
    if q==0:return '0'
    a=abs(q);e=0
    def ten(n):return Q(10**n) if n>=0 else Q(1,10**(-n))
    while a>=ten(e+1):e+=1
    while a<ten(e):e-=1
    unit=ten(e-5);x=q/unit
    integer=-((-x.numerator)//x.denominator) if upper else x.numerator//x.denominator
    return str(integer)+'e'+str(e-5)
def display(rec):
    a,b=map(Q,rec['exact_bounds']);assert a<=b
    return {'lower':dec(a,False),'upper':dec(b,True),'width_lower':dec(b-a,False),'width_upper':dec(b-a,True)}
def scoped(path):
    p=(ROOT/path).resolve();assert p.is_relative_to(ROOT.resolve());return p
try:
    assert sys.platform=='linux'
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('TERMINAL_VERIFY_300')));signal.alarm(300)
    cpu,occupied=r.lease.acquire()
    admission=r.read(ROOT/'ADMISSION.json');assert admission['admitted'] is True
    frozen_sha=r.sha(ROOT/'FROZEN.json');assert admission['frozen_sha256']==frozen_sha
    frozen=r.verify();assert len(frozen['files'])==1336
    assert not any(ROOT.glob('*FAILURE.json'))
    terminals={}
    for mode in ('production','audit'):
        terminal=r.read(ROOT/(mode+'_TERMINAL.json'));terminals[mode]=terminal
        assert terminal['pass'] is True and terminal['frozen_sha256']==frozen_sha
        for name,d in terminal['artifacts'].items():assert r.sha(scoped(name))==d,name
        for suffix in ('RUNTIME_BEFORE','RUNTIME_AFTER'):
            for p,d in r.read(ROOT/(mode+'_'+suffix+'.json')).items():assert frozen['files'].get(p)==d and r.sha(p)==d,p
    result=r.read(ROOT/'RESULT.json');audit=r.read(ROOT/'AUDIT_RESULT.json')
    assert result['pass'] is True and audit['pass'] is True and result['full_distance_computed'] is False
    assert audit['classification']=='CUBIC_FULL_FLOW_SAVED_CERTIFICATES_VERIFIED'
    readout={'scope':'Outward six-significant-digit decimal bounds from exact saved rationals. Widths are enclosure widths, not physical amplitudes. No ODE or full proper-distance coefficient.','classification':result['classification'],'engines':{},'terminal_seconds':{m:t['seconds'] for m,t in terminals.items()}}
    checked={}
    for name,count in (('primary',8183),('independent',16365)):
        data=r.read(ROOT/('FLOW_'+name+'.json'));assert data['cells']==count
        previous=None;completed=0;archive_bytes=0
        for entry in data['chunks']:
            path=scoped(entry['file']);assert r.sha(path)==entry['sha256'];archive_bytes+=path.stat().st_size
            chunk=r.read(path)
            assert chunk['binding_sha256']==frozen_sha and chunk['parameters_sha256']==data['parameters_sha256']
            assert chunk['engine']==name and chunk['previous_sha256']==previous
            assert chunk['first']==entry['first']==completed
            assert 1<=len(chunk['records'])<=32
            completed+=len(chunk['records']);assert chunk['last']==entry['last']==completed-1
            cp_path=scoped(entry['checkpoint']);assert r.sha(cp_path)==entry['checkpoint_sha256']
            cp=r.read(cp_path)
            assert cp['binding_sha256']==frozen_sha and cp['parameters_sha256']==data['parameters_sha256'] and cp['engine']==name
            assert cp['chunk_sha256']==entry['sha256'] and cp['completed']==completed and cp['total']==count
            assert cp['state']==chunk['records'][-1]['end'] and cp['resume_supported'] is False
            previous=entry['sha256']
            del chunk,cp
        assert completed==count
        matching=data['matching'];values={k:display(matching[k]) for k in ('FH3','FP3')}
        if matching['resolved']:
            values['A3']=display(matching['A3'])
            for side in ('lower','upper'):
                values[side]={k:display(v) for k,v in zip(('p3','f3','g3'),matching[side]['state'])}
        off=14 if name=='primary' else 13
        values['max_cubic_box_widths']={k:{'lower':dec(Q(v),False),'upper':dec(Q(v),True)} for k,v in zip(('p3_part','f3_part','g3_part','p3_hom','f3_hom','g3_hom'),data['max_box_widths'][off:])}
        readout['engines'][name]={'resolved':matching['resolved'],'values':values,'seconds':data['seconds'],'peak_rss_kib':data['peak_rss_kib'],'max_picard_iterations':data['max_picard_iterations'],'cells':count,'chunks':len(data['chunks']),'archive_bytes':archive_bytes}
        checked[name]={'cells':completed,'chunks':len(data['chunks']),'archive_bytes':archive_bytes}
    if 'A3_hull' in result:readout['A3_hull']=display(result['A3_hull'])
    r.put('READOUT.json',readout)
    r.verify()
    r.put('INDEPENDENT_TERMINAL_CHECK.json',{'pass':True,'files_verified':len(frozen['files']),'frozen_sha256':frozen_sha,'cpu':cpu,'occupied_cpus':occupied,'no_failure':True,'runtime_and_terminal_artifacts_verified':True,'streamed_archive_verified':checked,'readout_sha256':r.sha(ROOT/'READOUT.json'),'no_ode':True})
    print(json.dumps({'pass':True,'bindings':len(frozen['files']),'readout':readout}),flush=True)
finally:
    signal.alarm(0)
    for f in r.lease.handles:f.close()
