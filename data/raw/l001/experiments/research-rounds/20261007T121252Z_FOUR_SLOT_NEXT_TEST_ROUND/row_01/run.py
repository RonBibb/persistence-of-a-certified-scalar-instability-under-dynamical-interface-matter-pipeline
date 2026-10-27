"""One authorized correction-root/material-bound update; numerical work Linux-only."""
import argparse
import copy
import fcntl
import importlib.util
import json
import math
import os
import platform
import signal
import subprocess
import sys
import time
import traceback
from array import array
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROUND = ROOT.parents[1]
RESEARCH = Path('/media/psf/Home/Research')
CONTRACT = json.loads((ROOT/'CONTRACT.json').read_text())
PREV = RESEARCH/CONTRACT['predecessor_relative']
BASE = RESEARCH/CONTRACT['baseline_relative']
REP = RESEARCH/CONTRACT['representation_relative']
spec = importlib.util.spec_from_file_location('predecessor_r01', PREV/'run.py')
r01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r01)
rp, c4, rec = r01.rp, r01.c4, r01.rec
import verify4 as vv
import prepared_flow
import nonlinear
import preparation
import validated
from flint import arb, fmpq, ctx
from series import bounds, interval

OUT = ROOT/'output'
PRE = ROOT/'preflight'
STATUS = ROUND/'status/row_01.json'
D1, D2 = map(rp.f2q, CONTRACT['D_prime'])
H = rp.f2q(CONTRACT['step'])
TOTAL = CONTRACT['maximum_cells_per_material_flow']
FIELDS, COLS = rp.FIELDS, rp.COLUMNS
C = [rp.f2q(v) for v in CONTRACT['preconditioner_diagonal']]
GUARD = None
STARTED = None
CARRIED = 0.0
CURRENT = None
PROFILES = {}


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def exactq(x):
    return rp.fq(x) if isinstance(x, fmpq) else Q(str(x))


def endpoints(x):
    return [str(v) for v in bounds(x)]


def ivsubset(inner, outer):
    a,b=map(exactq,bounds(inner)); c,d=map(exactq,bounds(outer))
    return c<=a<=b<=d


def subset_rows(new, old, label, rows):
    if isinstance(new, arb):
        rows[label] = ivsubset(new, old)
    elif isinstance(new, dict):
        for k,v in new.items():
            need(k in old, 'Missing inherited domain field '+label+'.'+k)
            subset_rows(v, old[k], label+'.'+k, rows)
    elif isinstance(new, (list,tuple)):
        need(len(new)==len(old), 'Domain shape mismatch '+label)
        for i,(a,b) in enumerate(zip(new,old)):
            subset_rows(a,b,label+'.'+str(i),rows)
    else:
        rows[label] = new == old


def cp_path(folder, cell):
    matches=list((folder/'checkpoints').glob('00-'+str(cell).zfill(6)+'-*.json'))
    need(len(matches)==1, 'Ambiguous inherited checkpoint '+str(folder))
    p=matches[0]; b=rec.read(p)
    need(rec.fingerprint(b)==p.stem.split('-')[-1], 'Inherited checkpoint digest')
    return p


def loadcp(p):
    return rec.unpack(rec.read(p)['state'])


def put(path, value):
    if path.exists():
        need(rec.read(path)==rec.pack(value), 'Refuse differing immutable artifact '+str(path))
    else:
        rec.atomic(path,value,True)


def profile(w):
    if w not in PROFILES:
        PROFILES[w]=rp.ir.SavedProfile(c4.CONFIG['case_of'][w])
    return PROFILES[w]


def identity():
    return {'pid':os.getpid(),'hostname':platform.node(),
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'proc_start_ticks':Path('/proc/self/stat').read_text().split()[21],
            'executable':str(Path(sys.executable).resolve()),'source_sha256':rec.sha(__file__)}


def spent():
    return CARRIED + (0.0 if STARTED is None else time.monotonic()-STARTED)


def budget():
    if spent() >= CONTRACT['maximum_cumulative_compute_seconds']:
        raise TimeoutError('Two-hour cumulative Linux compute ceiling')


def status(phase, running=False, outcome=None, **kw):
    data={'round_id':CONTRACT['round_id'],'row':1,'phase':phase,'updated_utc':rec.now(),
          'experiment_running':running,'owned_pid':os.getpid(),'runtime_identity':identity(),
          'current_step':CURRENT,'cumulative_compute_seconds':spent(),'run_path':str(ROOT),
          'terminal_outcome':outcome,'guard':GUARD}
    data.update(kw); rec.atomic(STATUS,data)


def auth():
    authorization=rec.read(ROUND/'authorized/row_01.json')
    need(authorization['row']==1 and authorization['objective']==
         'Certify the correction-root enclosure and signed full-domain material bounds using the newly contracted static scalar/radion eigenvalue interval.', 'Wrong authorization')
    need(rec.sha(PREV/'HANDOFF.json')==authorization['source_sha256']==CONTRACT['predecessor_handoff_sha256'], 'Predecessor handoff changed')
    prevterm=rec.read(PREV/'TERMINAL.json')
    need(prevterm['integrity_passed'] and prevterm['result_sha256']==rec.sha(PREV/'RESULT.json'), 'Unverified predecessor')
    need(prevterm['integrity_sha256']==rec.sha(PREV/'RESULT_INTEGRITY.json'), 'Predecessor integrity changed')
    need(rec.read(PREV/'RESULT.json')['gates']=={'R01-G1':'PASS','R01-G2':'PASS','R01-G3':'REPORTED'}, 'Predecessor gates')
    need(r01.guard_check()==prevterm['guard'], 'Predecessor source/input guard')
    old=rec.read(BASE/'FREEZE.json')
    paths=[ROUND/'authorized/row_01.json', PREV/'HANDOFF.json',PREV/'TERMINAL.json',PREV/'RESULT.json',
           PREV/'RESULT_INTEGRITY.json',PREV/'BINDINGS.json',PREV/'FREEZE.json',PREV/'run.py',PREV/'CONTRACT.json',
           PREV/'output/PREPARATION.json',PREV/'output/NEWTON.json',PREV/'output/contracted_source/RESULT.json',
           PREV/'preflight/BASELINE_PREPARATION.json', BASE/'MANIFEST.json',BASE/'FREEZE.json',BASE/'CONTRACT.md',
           BASE/'verification/VERIFICATION.json',REP/'MANIFEST.json',REP/'verification/VERIFICATION.json',
           REP/'outputs/PRODUCER_RESULT.json',REP/'FREEZE.json']
    for p in sorted((BASE/'code').rglob('*.py')):
        need(rec.sha(p)==old['sources'][str(p.relative_to(BASE))], 'Changed inherited source '+str(p))
        paths.append(p)
    for w in CONTRACT['cases']:
        paths.extend([PREV/f'output/{w}_center/RESULT.json',
                      BASE/f'outputs/phase-{w}-center/PHASE.json',
                      BASE/f'outputs/phase-{w}-box/PHASE.json',
                      cp_path(BASE/f'outputs/phase-{w}-box',TOTAL),
                      BASE/f'outputs/material-{w}/SUMMARY.json',
                      BASE/f'outputs/material-{w}/CELLS.f64'])
    paths.extend([cp_path(BASE/'outputs/material-positive',16128),cp_path(BASE/'outputs/material-positive',TOTAL)])
    native=c4.PACKET['native']
    paths.extend([native/'MANIFEST.json',native/'results/fine_c4/SEED.json',
                  native/'results/fine_c4/case_3.dense.json',native/'results/fine_c4/case_4.dense.json'])
    for p in paths:
        if p.is_relative_to(BASE) and p.name not in ('MANIFEST.json','FREEZE.json'):
            r01.parent_entry(BASE,str(p.relative_to(BASE)))
        elif p.is_relative_to(native) and p.name!='MANIFEST.json':
            r01.parent_entry(native,str(p.relative_to(native)))
        elif p.is_relative_to(REP) and p.name!='MANIFEST.json':
            r01.parent_entry(REP,str(p.relative_to(REP)))
    vr=rec.read(REP/'verification/VERIFICATION.json')
    receipt=rec.read(REP/'outputs/PRODUCER_RESULT.json')['inherited_original_equation_receipts']
    need(vr['resolved'] and vr['classification']=='DETERMINISTIC_KNOT_REPRESENTATION_ADMITTED__HISTORICAL_RAW_GATE_RETAINED_FAILED','Representation admission missing')
    need(receipt['all_authenticated_and_passing'],'Original equation receipts not accepted')
    # Match native comparison inputs to the admitted representation's original freeze.
    rep_inputs=rec.read(REP/'FREEZE.json')['inputs']
    for p in paths:
        if p.is_relative_to(native) and p.name!='MANIFEST.json':
            need(rep_inputs.get(str(p))==rec.sha(p),'Representation uses a different native input')
    cap=c4.capacity()
    need(cap['available_bytes']>=4*1024**3 and cap['load1']<11,'Insufficient inherited capacity')
    data={'utc':rec.now(),'contract':CONTRACT,'runtime':c4.runtime_fingerprint(),'capacity':cap,
          'sources':{str(ROOT/n):rec.sha(ROOT/n) for n in ('run.py','CONTRACT.json')},
          'inputs':{str(p):rec.sha(p) for p in paths},
          'inherited_original_equation_receipts':receipt,
          'predecessor_guard':prevterm['guard']}
    put(ROOT/'BINDINGS.json',data)
    return rec.sha(ROOT/'BINDINGS.json')


def new_context():
    prep=rec.unpack(rec.read(PREV/'output/PREPARATION.json'))
    initial,y0=r01.source_initial(prep['mu'],'contracted_source')
    oldsrc=rec.unpack(rec.read(PREV/'output/contracted_source/RESULT.json'))
    need(rec.pack(initial['p'])==rec.pack(oldsrc['p']),'New source parameters mismatch')
    return {'common':{'p':oldsrc['p'],'y0':rp.canonical(y0)},'jets':prep['jets'],
            'D_ball':oldsrc['p']['D'],'preps':prep['preps']}


def domain_check(A):
    result={}
    oldprep=rec.unpack(rec.read(PREV/'preflight/BASELINE_PREPARATION.json'))
    oldcommon=rec.unpack(rec.read(c4.PACKET['finite']/'output/source/RESULT.json'))
    for w in CONTRACT['cases']:
        box=rec.unpack(rec.read(BASE/f'outputs/phase-{w}-box/PHASE.json'))
        center=rec.unpack(rec.read(BASE/f'outputs/phase-{w}-center/PHASE.json'))
        old=loadcp(cp_path(BASE/f'outputs/phase-{w}-box',TOTAL))
        newcenter=rec.unpack(rec.read(PREV/f'output/{w}_center/RESULT.json'))
        need(box['box']==center['box'] and box['center']==center['center'],'Root center/domain mismatch')
        need(rec.pack(newcenter['p']['x'])==rec.pack([arb(rp.f2q(x)) for x in center['center']]),'New center differs')
        need(box['cover']==center['cover']==newcenter['cover']==[[str(D1),str(D2)]],'Event coverage mismatch')
        rows={}
        for k in ('gamma','lambda_a','lambda_b','m2','v0','v1','k','D'):
            need(rec.pack(A['common']['p'][k])==rec.pack(old['p'][k]),'Changed non-mu source '+k)
        rows['mu']=ivsubset(A['common']['p']['mu'],old['p']['mu'])
        need(rows['mu'],'New eigenvalue outside old domain')
        need(rec.pack(A['preps'][w]['eps'])==rec.pack(old['p']['eps']),'Changed signed amplitude')
        subset_rows(A['common']['y0'],oldcommon['y0'],'initial_source',rows)
        subset_rows(A['jets'],oldprep['jets'],'wall_jets',rows)
        for k in ('c7','W'):
            subset_rows(A['preps'][w][k],old['p'][k],k,rows)
        x=[interval(rp.f2q(a),rp.f2q(b)) for a,b in box['box']]
        for i in range(3):
            rows['correction_X_'+str(i)]=rec.pack(x[i])==rec.pack(old['p']['x'][i])
        need(all(rows['correction_X_'+str(i)] for i in range(3)),'Jacobian correction box changed')
        result[w]={'inherited_jacobian_covers':all(rows.values()),'checks':rows,
                   'failed_containment_fields':[k for k,v in rows.items() if not v],
                   'exact_identity_authenticated':True,'X':box['box'],'c':box['center'],
                   'fallback_if_needed':'one new box flow with same X and new preparation'}
    return result


def new_stats(state):
    start=state['cell_index']*H
    state.update(coverage_start=str(start),covered=str(start),coverage_gaps=0,closure_failures=0,
                 best={f:None for f in FIELDS},component_max={f:{k:fmpq(0) for k in COLS} for f in FIELDS},
                 completed_blocks=0,last_block=None)
    return state


def comparison_cell(st,w):
    i=st['cell_index']; t=i*H; h=min(H,D2-t); p=st['p']
    ynext,cell=validated.step(st['y'],h,p,prepared_flow)
    need(all(v.is_finite() for v in ynext),'Nonfinite material state')
    need(bounds(cell['box'][4])[0]>0,'Source exp(-W) positivity lost')
    prof=profile(w); worst=[None]*3
    for k in range(CONTRACT['subcells']):
        lo,hi=h*k/CONTRACT['subcells'],h*(k+1)/CONTRACT['subcells']
        if t+lo!=rp.f2q(st['covered']):st['coverage_gaps']+=1
        st['covered']=str(t+hi)
        a=rp.ir.physical_values(validated.range_on_cell(cell,lo,hi),p,'positive')
        b=prof.enclose((t+lo)*prof.D/D2,min(prof.D,(t+hi)*prof.D/D1))
        for j in range(3):
            difference=a[j]-b[j]; E=rp.ir.maximum_abs(difference)
            if worst[j] is None or E>worst[j][0]:worst[j]=(E,lo,a[j],b[j],difference)
    out=[]
    for j,f in enumerate(FIELDS):
        E,lo,a,b,diff=worst[j]
        pa=rp.ir.physical_values(validated.range_on_cell(cell,lo,lo),p,'positive')[j]
        pb=prof.enclose((t+lo)*prof.D/D2,min(prof.D,(t+lo)*prof.D/D1))[j]
        (ma,ra),(mb,rb)=rp.parts(a),rp.parts(b); r0,rd=rp.parts(pa)[1],rp.parts(pb)[1]
        total=rp.fq(abs(ma-mb)+ra+rb)
        slack=rp.CLOSURE_RADIUS*rp.fq(ra+rb)+rp.CLOSURE_FLOOR*(1+rp.fq(abs(ma))+rp.fq(abs(mb)))
        closed=total-slack<=rp.fq(E)<=total+slack
        if not closed:st['closure_failures']+=1
        row={'E':E,'center':abs(ma-mb),'state':r0,'source_step':ra-r0,'event':rd,'native_step':rb-rd}
        for k,v in row.items():st['component_max'][f][k]=max(st['component_max'][f][k],v)
        best=st['best'][f]
        if best is None or E>best['row']['E']:
            st['best'][f]={'cell':i,'subcell_left':str(lo),'row':row,'closed':closed,
                           'a':endpoints(a),'b':endpoints(b),'difference':endpoints(diff),
                           'point_a':endpoints(pa),'point_b':endpoints(pb)}
        out.extend(c4.up_float(rp.fq(row[k])) for k in COLS)
    st['y']=ynext;st['cell_index']+=1;st['max_picard']=max(st['max_picard'],cell['picard_iterations'])
    return out


def source_keys(st):
    return rec.pack({k:st[k] for k in ('y','p','max_picard','cell_index','task_index','name')})


def restart_child(guard):
    st=rec.load(PRE/'restart',guard)
    row=comparison_cell(st,'positive')
    put(PRE/'restart_child.json',{'state':st,'row':row})


def preflight(bindguard,A,coverage):
    status('PREFLIGHT')
    controls={}
    # Anchor root update to the original, independently verified calculation.
    for w in CONTRACT['cases']:
        bp=rec.unpack(rec.read(BASE/f'outputs/phase-{w}-box/PHASE.json'))
        cp=rec.unpack(rec.read(BASE/f'outputs/phase-{w}-center/PHASE.json'))
        X=[tuple(map(Q,z)) for z in bp['box']]; c=list(map(Q,bp['center']))
        k=rp.krawczyk(C,cp['map']['G'],bp['map']['J'],X,c)
        old=rec.read(BASE/f'outputs/material-{w}/SUMMARY.json')['krawczyk']
        controls[w+'_old_root_reproduced']=k==old
    folder=BASE/'outputs/material-positive'
    st=new_stats(loadcp(cp_path(folder,16128)))
    data=array('d');data.frombytes((folder/'CELLS.f64').read_bytes())
    if sys.byteorder!='little':data.byteswap()
    same=True
    while st['cell_index']<TOTAL:
        budget();i=st['cell_index'];row=comparison_cell(st,'positive')
        same=same and all(row[j]==data[j*TOTAL+i] for j in range(18))
    expected=loadcp(cp_path(folder,TOTAL))
    controls['old_material_final_block_endpoint']=source_keys(st)==source_keys(expected)
    controls['old_material_budget_columns_bitwise']=same
    controls['old_material_closure']=st['closure_failures']==0
    trial=new_stats(loadcp(cp_path(folder,16128)))
    comparison_cell(trial,'positive')
    rec.save(PRE/'restart',trial,bindguard)
    pointer=rec.read(PRE/'restart/LATEST.json')
    put(PRE/'restart/checkpoints/incomplete.uncommitted.json',{'incomplete':True})
    controls['uncommitted_pointer_unchanged']=rec.read(PRE/'restart/LATEST.json')==pointer
    try:
        rec.load(PRE/'restart',bindguard+'-invalid')
        controls['changed_binding_rejected']=False
    except AssertionError:
        controls['changed_binding_rejected']=True
    subprocess.run([sys.executable,'-B',str(ROOT/'run.py'),'restart-control','--guard',bindguard],check=True,timeout=90)
    direct=rec.load(PRE/'restart',bindguard);row=comparison_cell(direct,'positive')
    controls['fresh_process_restart_exact']=rec.pack({'state':direct,'row':row})==rec.read(PRE/'restart_child.json')
    controls['same_physical_identity']=all(v['exact_identity_authenticated'] for v in coverage.values())
    result={'utc':rec.now(),'controls':controls,'passed':all(controls.values()),'new_production_outcomes':False,
            'baseline_replay_cells':[16128,TOTAL],'source_guard':bindguard}
    put(PRE/'RESULT.json',result)
    need(result['passed'],'Preflight failed')
    put(ROOT/'FREEZE.json',{'utc':rec.now(),'bindings_sha256':bindguard,'preflight_sha256':rec.sha(PRE/'RESULT.json'),
                          'domain_check_sha256':rec.sha(PRE/'JACOBIAN_DOMAIN.json')})


def guardcheck():
    b=rec.read(ROOT/'BINDINGS.json')
    need(b['contract']==CONTRACT,'Contract changed')
    for p,d in (b['sources']|b['inputs']).items():need(rec.sha(p)==d,'Bound input changed: '+p)
    need(b['runtime']==c4.runtime_fingerprint(),'Runtime changed')
    f=rec.read(ROOT/'FREEZE.json')
    need(f['bindings_sha256']==rec.sha(ROOT/'BINDINGS.json'),'Bindings changed')
    need(f['preflight_sha256']==rec.sha(PRE/'RESULT.json') and rec.read(PRE/'RESULT.json')['passed'],'Preflight changed')
    need(f['domain_check_sha256']==rec.sha(PRE/'JACOBIAN_DOMAIN.json'),'Domain check changed')
    return rec.sha(ROOT/'FREEZE.json')


def missing_jacobian(w,A,domain):
    global CURRENT
    CURRENT=w+'_box_jacobian'
    out=OUT/CURRENT
    if (out/'RESULT.json').exists():
        result=rec.unpack(rec.read(out/'RESULT.json'));need(result['guard']==GUARD,'Stale box flow');return result['map']['J']
    X=[tuple(map(Q,z)) for z in domain['X']];c=list(map(Q,domain['c']))
    st=rp.phase_initial(A,w,'box',X,c);st['name']=CURRENT
    if (out/'LATEST.json').exists():st=rec.load(out,GUARD)
    while st['cell_index']<TOTAL:
        budget();rp.finite_cell(st,nonlinear,D1,D2,H,endpoint=lambda z:rp.map_at(z,st['p'],st['jets']))
        if st['cell_index']%CONTRACT['checkpoint_cells']==0 or st['cell_index']==TOTAL:
            st['elapsed_seconds']=spent();rec.save(out,st,GUARD)
            status('RUNNING',True,completed_cells=st['cell_index'],total_cells=TOTAL,last_checkpoint=rec.read(out/'LATEST.json'))
    need(st['cover']==[[str(D1),str(D2)]],'Incomplete fresh Jacobian event cover')
    put(out/'RESULT.json',{'guard':GUARD,'map':st['map'],'cover':st['cover'],'cells':TOTAL,'domain':domain,'checkpoint':rec.read(out/'LATEST.json')})
    return st['map']['J']


def root_update(w,A,domain):
    center=rec.unpack(rec.read(PREV/f'output/{w}_center/RESULT.json'))
    if domain['inherited_jacobian_covers']:
        J=rec.unpack(rec.read(BASE/f'outputs/phase-{w}-box/PHASE.json'))['map']['J'];origin='inherited_box_phase'
    else:
        J=missing_jacobian(w,A,domain);origin='new_missing_box_phase'
    X=[tuple(map(Q,z)) for z in domain['X']];c=list(map(Q,domain['c']))
    kr=rp.krawczyk(C,center['map']['G'],J,X,c)
    out={'guard':GUARD,'sign':w,'krawczyk':kr,'G':center['map']['G'],'J':J,'jacobian_origin':origin,
         'eigenvalue_interval':rec.read(PREV/'output/NEWTON.json')['intersection'],
         'inherited_existence_and_uniqueness_retained':not kr['empty']}
    put(OUT/f'ROOT_{w}.json',out)
    need(not kr['empty'],'ROOT_ITERATION_INCONSISTENT '+w)
    return out


def start_material(w,A,root):
    Xn=[tuple(map(Q,z)) for z in root['krawczyk']['new_box']]
    p=rp.flow_parameters(A,w,[interval(rp.f2q(a),rp.f2q(b)) for a,b in Xn])
    y=list(A['common']['y0'])+[p['x'][0],preparation.wall_increment(A['common']['y0'],A['jets'][0],p,p['eps'])['target']]
    st={'task_index':0,'name':w,'cell_index':0,'elapsed_seconds':0.0,'y':y,'p':p,'max_picard':0,
        'root_sha256':rec.sha(OUT/f'ROOT_{w}.json')}
    return new_stats(st)


def block_bytes(path,rows):
    a=array('d',rows)
    if sys.byteorder!='little':a.byteswap()
    payload=a.tobytes()
    if path.exists():need(path.read_bytes()==payload,'Different immutable block array')
    else:c4.atomic_bytes(path,payload)


def material(w,A,root):
    global CURRENT
    CURRENT=w+'_material';out=OUT/CURRENT
    if (out/'RESULT.json').exists():
        result=rec.read(out/'RESULT.json');need(result['guard']==GUARD,'Stale material result');return result
    st=start_material(w,A,root)
    if (out/'LATEST.json').exists():st=rec.load(out,GUARD)
    need(st['root_sha256']==rec.sha(OUT/f'ROOT_{w}.json'),'Resume root mismatch')
    while st['cell_index']<TOTAL:
        start=st['cell_index'];end=min(TOTAL,((start//CONTRACT['checkpoint_cells'])+1)*CONTRACT['checkpoint_cells'])
        rows=[]
        while st['cell_index']<end:
            budget();rows.extend(comparison_cell(st,w))
        need(st['closure_failures']==0 and st['coverage_gaps']==0,'Material bound budget/coverage failure')
        blocks=out/'blocks';blocks.mkdir(parents=True,exist_ok=True)
        arr=blocks/f'{start:06d}-{end:06d}.f64';block_bytes(arr,rows)
        block={'guard':GUARD,'sign':w,'start_cell':start,'end_cell':end,'previous':st['last_block'],
               'covered':st['covered'],'coverage_gaps':st['coverage_gaps'],'closure_failures':st['closure_failures'],
               'best':st['best'],'component_max':st['component_max'],'array':arr.name,'array_sha256':rec.sha(arr),
               'array_layout':'row-major, cell then field A/ell/Phi then E/center/state/source_step/event/native_step; upward binary64',
               'count_values':len(rows)}
        bp=blocks/f'{start:06d}-{end:06d}.json';put(bp,block)
        st['completed_blocks']+=1;st['last_block']={'path':str(bp.relative_to(out)),'sha256':rec.sha(bp)}
        st['elapsed_seconds']=spent();rec.save(out,st,GUARD)
        status('RUNNING',True,completed_cells=end,total_cells=TOTAL,completed_signs=0 if w=='positive' else 1,
               last_checkpoint=rec.read(out/'LATEST.json'))
        if end%2048==0 or end==TOTAL:print(json.dumps({'sign':w,'cells':end,'total':TOTAL,'cumulative_seconds':spent(),'utc':rec.now()}),flush=True)
    fields={}
    old=rec.read(BASE/f'outputs/material-{w}/SUMMARY.json')
    for f in FIELDS:
        best=st['best'][f];row=best['row'];E=rp.fq(row['E'])
        shares={'CENTER_DISCREPANCY':row['center'],'STATE_RADIUS':row['state'],
                'COMPARISON_STEP':row['source_step']+row['native_step'],'EVENT_WIDTH':row['event']}
        fields[f]={'bound_exact':str(E),'bound_display':c4.show(E),'baseline_exact':old['fieldsummary'][f]['bound_exact'],
                   'ratio_to_baseline_exact':str(E/Q(old['fieldsummary'][f]['bound_exact'])),
                   'ratio_to_baseline_display':float(E/Q(old['fieldsummary'][f]['bound_exact'])),
                   'dominant_width':max(shares,key=lambda k:shares[k]),
                   'shares':{k:float(rp.fq(v)/E) if E else None for k,v in shares.items()},
                   'argmax':best,'component_max':st['component_max'][f]}
    result={'guard':GUARD,'sign':w,'fields':fields,'cells':st['cell_index'],'subcells':st['cell_index']*CONTRACT['subcells'],
            'coverage_start':st['coverage_start'],'covered':st['covered'],'coverage_gaps':st['coverage_gaps'],
            'closure_failures':st['closure_failures'],'max_picard':st['max_picard'],'checkpoint':rec.read(out/'LATEST.json'),
            'completed_blocks':st['completed_blocks'],'last_block':st['last_block'],'root_sha256':st['root_sha256'],
            'material_absolute_accuracy_admission':'NOT_SCORED_NO_INHERITED_CEILING','new_time_evolution_steps':0}
    put(out/'RESULT.json',result)
    return rec.read(out/'RESULT.json')


def exact_peak_check(peak):
    a,b,pa,pb=[list(map(Q,peak[k])) for k in ('a','b','point_a','point_b')]
    diff=list(map(Q,peak['difference']))
    ma,mb=(a[0]+a[1])/2,(b[0]+b[1])/2
    ra,rb=(a[1]-a[0])/2,(b[1]-b[0])/2
    r0,rd=(pa[1]-pa[0])/2,(pb[1]-pb[0])/2
    row={'E':max(abs(v) for v in diff),'center':abs(ma-mb),'state':r0,'source_step':ra-r0,'event':rd,'native_step':rb-rd}
    saved={k:exactq(v) for k,v in peak['row'].items()}
    slack=rp.CLOSURE_RADIUS*(ra+rb)+rp.CLOSURE_FLOOR*(1+abs(ma)+abs(mb))
    return row==saved and diff[0]<=a[0]-b[1] and a[1]-b[0]<=diff[1] and abs(row['E']-(abs(ma-mb)+ra+rb))<=slack


def result_check(result):
    global CURRENT
    CURRENT='result_integrity';status('RESULT_INTEGRITY_CHECK')
    checks={'bindings_unchanged':guardcheck()==GUARD}
    for w in CONTRACT['cases']:
        root=rec.unpack(rec.read(OUT/f'ROOT_{w}.json'));kr=root['krawczyk']
        X=[tuple(map(Q,z)) for z in kr['X']]; c=list(map(Q,kr['c']))
        exact=vv.exact_krawczyk(kr['C'],root['G'],root['J'],X,c)
        box=[tuple(map(Q,z)) for z in kr['new_box']]
        checks[w+'_exact_root_image_contained']=exact is not None and all(a<=l<=h<=b for (l,h),(a,b) in zip(exact,box))
        checks[w+'_root_subset_old']=all(a<=l<=h<=b for (l,h),(a,b) in zip(box,X))
        out=OUT/(w+'_material');final=rec.unpack(rec.read(out/'RESULT.json'))
        ptr=final['checkpoint'];cp=rec.read(out/ptr['path'])
        checks[w+'_terminal_checkpoint']=rec.fingerprint(cp)==ptr['digest'] and cp['guard']==GUARD
        previous=None;end=0;count=0;maxima=[-math.inf]*18;chain_ok=True
        for path in sorted((out/'blocks').glob('*.json')):
            b=rec.unpack(rec.read(path));chain_ok=chain_ok and b['guard']==GUARD and b['start_cell']==end and b['previous']==previous
            arr=path.parent/b['array'];chain_ok=chain_ok and rec.sha(arr)==b['array_sha256']
            values=array('d');values.frombytes(arr.read_bytes())
            if sys.byteorder!='little':values.byteswap()
            n=b['end_cell']-b['start_cell']
            chain_ok=chain_ok and len(values)==18*n and b['coverage_gaps']==0 and b['closure_failures']==0
            for j in range(18):maxima[j]=max(maxima[j],max(values[j::18]))
            for f in FIELDS:chain_ok=chain_ok and exact_peak_check(b['best'][f])
            previous={'path':str(path.relative_to(out)),'sha256':rec.sha(path)};end=b['end_cell'];count+=1
        checks[w+'_blocks_coverage_and_budget']=chain_ok and end==TOTAL and count==final['completed_blocks'] and previous==final['last_block']
        checks[w+'_full_normalized_domain']=(final['coverage_start']=='0' and final['covered']==str(D2) and final['subcells']==TOTAL*CONTRACT['subcells'])
        for j,f in enumerate(FIELDS):
            v=final['fields'][f];e=Q(v['bound_exact'])
            checks[w+'_'+f+'_bound_and_ratio']=(e==exactq(v['argmax']['row']['E']) and exact_peak_check(v['argmax'])
                and c4.up_float(e)==maxima[j*6] and Q(v['ratio_to_baseline_exact'])==e/Q(v['baseline_exact']))
            checks[w+'_'+f+'_component_maxima']=all(c4.up_float(exactq(v['component_max'][col]))==maxima[j*6+k] for k,col in enumerate(COLS))
    output={'utc':rec.now(),'guard':GUARD,'checks':checks,'passed':all(checks.values()),'result_sha256':rec.sha(ROOT/'RESULT.json')}
    put(ROOT/'RESULT_INTEGRITY.json',output)
    return output


def main():
    global GUARD,STARTED,CARRIED,CURRENT
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run','resume','restart-control']);p.add_argument('--guard');args=p.parse_args()
    need(sys.platform=='linux','Numerical work must run on Linux');c4.check_environment();c4.limit_address_space();ctx.prec=CONTRACT['bits'];ctx.threads=1
    if args.command=='restart-control':restart_child(args.guard);return
    lock=open(ROOT/'RUN.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    need(not (ROOT/'TERMINAL.json').exists() and not (ROOT/'FAILURE.json').exists(),'Terminal/failed-closed job cannot restart')
    usage=ROOT/'COMPUTE_USAGE.json'
    if usage.exists():
        previous=rec.read(usage);CARRIED=previous['elapsed_seconds']
        if previous['active']:
            # Conservative charge of all unaccounted wall time after unexpected loss.
            CARRIED+=max(0.0,time.time()-previous['updated_epoch'])
    STARTED=time.monotonic()
    rec.atomic(usage,{'elapsed_seconds':CARRIED,'active':True,'updated_epoch':time.time()})
    signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('SIGTERM')))
    try:
        A=new_context()
        if args.command=='run':
            need(not (ROOT/'BINDINGS.json').exists(),'Use exact resume, not rerun')
            GUARD=auth();coverage=domain_check(A);put(PRE/'JACOBIAN_DOMAIN.json',coverage)
            preflight(GUARD,A,coverage)
        GUARD=guardcheck();coverage=rec.read(PRE/'JACOBIAN_DOMAIN.json')
        roots={}
        for w in CONTRACT['cases']:
            budget();CURRENT=w+'_root';status('ROOT_UPDATE',True)
            roots[w]=root_update(w,A,coverage[w])
        results={}
        for w in CONTRACT['cases']:results[w]=material(w,A,roots[w])
        result={'classification':'CORRECTION_ROOTS_AND_SIGNED_MATERIAL_BOUNDS_CERTIFIED',
                'round_id':CONTRACT['round_id'],'row':1,'guard':GUARD,'completed_utc':rec.now(),
                'gates':{'N01-G1':'PASS','N01-G2':'PASS_BOTH_SIGNS','N01-G3':'VALID_OUTWARD_BOUNDS_BOTH_SIGNS__NO_ABSOLUTE_ACCURACY_CEILING'},
                'roots':roots,'material':results,'cumulative_compute_seconds':spent(),
                'runtime_identity':identity(),'new_time_evolution_steps':0,'historical_failure_rescored':False,
                'evidence_class':'Validated outward-arithmetic correction-root and material-field enclosures for the inherited static signed family; no spacetime evolution certificate.',
                'remaining_gap':'No conformal lapse/inverse-map or time-evolution error propagation. Material bounds have stated magnitudes, not an inherited absolute acceptance threshold.',
                'successor_launched':False}
        put(ROOT/'RESULT.json',result);check=result_check(result)
        classification=result['classification'] if check['passed'] else 'TECHNICAL_INCOMPLETE__RESULT_INTEGRITY_FAILED'
        put(ROOT/'TERMINAL.json',{'utc':rec.now(),'classification':classification,'guard':GUARD,
            'result_sha256':rec.sha(ROOT/'RESULT.json'),'integrity_sha256':rec.sha(ROOT/'RESULT_INTEGRITY.json'),
            'integrity_passed':check['passed'],'successor_launched':False})
        status('TERMINAL',False,classification,result_path=str(ROOT/'RESULT.json'),gates=result['gates'])
        print(json.dumps({'terminal':classification,'integrity':check['passed'],'seconds':spent()}),flush=True)
    except KeyboardInterrupt as error:
        status('STOPPED_RECOVERABLE',False,note=str(error));raise
    except Exception as error:
        failure={'utc':rec.now(),'guard':GUARD,'step':CURRENT,'error_type':type(error).__name__,'error':str(error),
                 'traceback':traceback.format_exc(),'classification':'TECHNICAL_INCOMPLETE','physical_exclusion':False}
        put(ROOT/'FAILURE.json',failure);status('FAILED_CLOSED',False,'TECHNICAL_INCOMPLETE',error=str(error))
        print(json.dumps(failure),flush=True);raise
    finally:
        rec.atomic(usage,{'elapsed_seconds':spent(),'active':False,'updated_epoch':time.time()})


if __name__=='__main__':main()
