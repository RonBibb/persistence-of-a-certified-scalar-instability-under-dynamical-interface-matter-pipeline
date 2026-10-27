"""Independent leased Linux terminal integrity/readout; no ODE or Arb imports."""
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
def ivdisplay(rec):
    a,b=map(Q,rec['exact_bounds']);assert a<=b
    return {'lower':dec(a,False),'upper':dec(b,True)}
try:
    assert sys.platform=='linux'
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('TERMINAL_VERIFY_120')));signal.alarm(120)
    cpu,occupied=r.lease.acquire()
    admission=r.read(ROOT/'ADMISSION.json');assert admission['admitted'] is True
    frozen_sha=r.sha(ROOT/'FROZEN.json');assert admission['frozen_sha256']==frozen_sha
    frozen=r.verify();assert not any(ROOT.glob('*FAILURE.json'))
    for mode in ('production','audit'):
        terminal=r.read(ROOT/(mode+'_TERMINAL.json'))
        assert terminal['pass'] is True and terminal['frozen_sha256']==frozen_sha
        for name,d in terminal['artifacts'].items():assert r.sha(ROOT/name)==d,name
        for suffix in ('RUNTIME_BEFORE','RUNTIME_AFTER'):
            for p,d in r.read(ROOT/(mode+'_'+suffix+'.json')).items():assert frozen['files'].get(p)==d and r.sha(p)==d,p
    result=r.read(ROOT/'RESULT.json');audit=r.read(ROOT/'AUDIT_RESULT.json')
    assert result['pass'] is True and audit['pass'] is True
    assert audit['classification']=='CUBIC_PROBE_SAVED_CERTIFICATES_VERIFIED'
    readout={'scope':'Outward six-significant-digit decimal bounds from exact saved rationals; no ODE. Widths are interval widths, not physical amplitudes.','engines':{}}
    for name,dim,n in (('primary',20,64),('independent',19,128)):
        data=r.read(ROOT/('PROBE_'+name+'.json'));assert data['cells']==n and len(data['records'])==n
        off=14 if name=='primary' else 13
        values={}
        for j,label in enumerate(('p3_part','f3_part','g3_part','p3_hom','f3_hom','g3_hom')):
            i=off+j
            widths={k:Q(data[k][i]) for k in ('initial_widths','final_widths','max_box_widths')}
            assert all(q>=0 for q in widths.values())
            values[label]={'initial':ivdisplay(data['initial'][i]),'final':ivdisplay(data['final'][i]),
                          **{k:{'lower':dec(q,False),'upper':dec(q,True)} for k,q in widths.items()}}
            if widths['initial_widths']>0:
                ratio=widths['final_widths']/widths['initial_widths']
                values[label]['width_growth_ratio']={'lower':dec(ratio,False),'upper':dec(ratio,True)}
        readout['engines'][name]={'launch_divisor':ivdisplay(data['launch']['launch_divisor']),
            'cubic_components':values,'seconds':data['seconds'],'max_picard_iterations':data['max_picard_iterations'],
            'linear_work_projection_seconds':data['linear_work_projection_seconds']}
    readout['combined_linear_work_projection_seconds']=result['combined_linear_work_projection_seconds']
    readout['full_run_admitted']=False
    r.put('READOUT.json',readout)
    r.verify()
    r.put('INDEPENDENT_TERMINAL_CHECK.json',{'pass':True,'files_verified':len(frozen['files']),
        'frozen_sha256':frozen_sha,'cpu':cpu,'occupied_cpus':occupied,'no_failure':True,
        'runtime_and_terminal_artifacts_verified':True,'readout_sha256':r.sha(ROOT/'READOUT.json'),
        'no_ode':True})
    print(json.dumps({'pass':True,'bindings':len(frozen['files']),'readout':readout}),flush=True)
finally:
    signal.alarm(0)
    for f in r.lease.handles:f.close()
