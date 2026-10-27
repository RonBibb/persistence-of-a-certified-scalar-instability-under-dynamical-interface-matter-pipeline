"""One serial, finite uniform-amplitude certificate; no physical successor."""
import argparse,fcntl,json,math,os,resource,subprocess,sys,time,traceback
from pathlib import Path
from flint import arb,ctx,fmpq
from algebra import Taylor,maxabs
from series import bounds,interval,hull
from records import atomic,read,sha,now,pack,unpack,fingerprint,save,load
import inherited_driver as base
import nonlinear,preparation,validated

ROOT=Path(__file__).resolve().parent
PREVIOUS='../lin-c4-finite-amplitude-20261005T223500Z'
CONFIG={**base.CONFIG,'max_case_workers':1,'epsilon_interval':['-1/200000','1/200000'],
        'maximum_cover_depth':2,'maximum_cover_nodes':7,'maximum_cells':229110,
        'graph_integration_cpu_seconds_cap':7200,'center':['0','0','0'],
        'cpu_cap_scope':'validated_step_loop_excludes_preparation_and_final_publication',
        'physical_source':'reuse_authenticated_complete_source',
        'traversal':'depth_first_left_before_right_split_only_completed_noncertificate'}
for k in ('epsilon','source_seconds_cap','zero_seconds_cap','case_seconds_cap'):CONFIG.pop(k)
ENV=base.ENV
SOURCES=['CONTRACT.md','CONNECTION_ARGUMENT.md','CENTERED_IVP_DERIVATION.md',
         'runner.py','inherited_driver.py','algebra.py','series.py','records.py',
         'validated.py','source_flow.py','preparation.py','nonlinear.py']
REVIEWS=base.REVIEWS
base.CONFIG=CONFIG
base.ROOT=ROOT
base.sources=lambda:{n:sha(ROOT/n) for n in SOURCES}
exact=base.exact
runtime=base.runtime

def sources():return base.sources()
def authenticate():
    b=read(ROOT/'BINDINGS.json');guard=sha(ROOT/'BINDINGS.json')
    assert read(ROOT/'FREEZE_RECORD.json')['guard']==guard
    assert b['config']==CONFIG and b['sources']==sources() and b['runtime']==runtime()
    for n,h in b['reviews'].items():assert sha(ROOT/n)==h,n
    for n,h in b['inputs'].items():assert sha(ROOT/n)==h,n
    return b,guard

def preflight(out):
    # Inherited controls use manufactured vacuum only, never the D1 source.
    base.preflight(out/'inherited')
    checks={}
    for a,b in [(-2,3),(-3,-1),(1,4),(0,0)]:
        x=interval(fmpq(a,1000),fmpq(b,1000))
        for n in range(9):
            lo,hi=bounds(preparation.integer_range(x,n))
            grid=[fmpq(a,1000)+fmpq(j*(b-a),7000) for j in range(8)]
            checks[f'power_{a}_{b}_{n}']=all(lo<=v**n<=hi for v in grid)
    # Exact even-crossing and nonzero-degree endpoint checks; not sampling alone.
    lo,hi=bounds(preparation.integer_range(interval(fmpq(-2),fmpq(3)),2))
    checks['even_power_full_domain']=lo<=0 and hi>=9
    for a,b in [('-1/200000','1/200000'),('1/400000','1/200000'),('-1/200000','-1/400000')]:
        I=interval(exact(a),exact(b));lo,hi=bounds(I)
        e=Taylor([0,1]+[0]*7);er=Taylor([interval(min(fmpq(0),lo),max(fmpq(0),hi)),1]+[0]*7)
        # A degree8 polynomial has an exact constant eighth derivative: the
        # implemented remainder formula must enclose its full direct range.
        z=e**2+3*e**7+5*e**8;r=er**2+3*er**7+5*er**8
        outv=preparation.remainder_eval(z,r,I)
        target=preparation.integer_range(I,2)+3*preparation.integer_range(I,7)+5*preparation.integer_range(I,8)
        checks['polynomial_remainder_'+a+'_'+b]=base.zero(outv-target)
    # The identical persisted parameter path, now including crossing-zero eps.
    out.mkdir(parents=True,exist_ok=True)
    h=fmpq(1,8192)
    st={'task_index':0,'cell_index':0,'elapsed_seconds':0.,'h':h,
        'y':[arb(0)]*4+[arb(1)]+[arb(0)]*4,
        'p':{'test_parameter':interval(fmpq(-1,200000),fmpq(1,200000)),
             'eps':interval(fmpq(-1,200000),fmpq(1,200000)),
             'tile':['-1/200000','1/200000']}}
    save(out/'interval-recovery',st,'parameter-control')
    after,_=base.advance(st,h,base.ParameterFixture)
    child=json.loads(subprocess.check_output([sys.executable,'-B',str(ROOT/'runner.py'),'child-parameter',str(out/'interval-recovery')],text=True))
    checks['interval_parameter_fresh_process']=child['digest']==fingerprint(after)
    real=load(out/'inherited'/'recovery','manufactured-control')
    real['p']['eps']=interval(fmpq(-1,200000),fmpq(1,200000))
    save(out/'nonlinear-interval-recovery',real,'manufactured-control')
    after,_=base.advance(real,real['h'],nonlinear)
    child=json.loads(subprocess.check_output([sys.executable,'-B',str(ROOT/'runner.py'),'child',str(out/'nonlinear-interval-recovery')],text=True))
    checks['nonlinear_interval_parameter_fresh_process']=child['digest']==fingerprint(after)
    leaves=[['-1/200000','-1/400000'],['-1/400000','0'],['0','1/400000'],['1/400000','1/200000']]
    checks['coverage_accepts_closed_partition']=coverage(leaves)['full']
    checks['coverage_rejects_gap']=not coverage([leaves[0],leaves[2],leaves[3]])['full']
    checks['coverage_no_false_zero_component']=coverage([leaves[0],leaves[3]])['zero_component'] is None
    inherited=read(out/'inherited'/'RESULT.json')
    result={'pass':inherited['pass'] and all(checks.values()),'checks':checks,
        'inherited_control_sha256':sha(out/'inherited'/'RESULT.json'),
        'sources':sources(),'runtime':runtime(),'utc':now(),'physical_D1_outcomes_evaluated':False}
    atomic(out/'RESULT.json',result,True);print(json.dumps(result,indent=2));assert result['pass']

def coverage(tiles):
    spans=sorted((exact(a),exact(b)) for a,b in tiles);merged=[]
    for a,b in spans:
        assert a<=b
        if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
        else:merged.append([a,b])
    target=list(map(exact,CONFIG['epsilon_interval']))
    full=len(merged)==1 and merged[0]==target
    zero=next(([str(a),str(b)] for a,b in merged if a<=0<=b),None)
    return {'full':full,'components':[[str(a),str(b)] for a,b in merged],'zero_component':zero}

def freeze(control):
    c=read(control/'RESULT.json');assert c['pass'] and c['sources']==sources() and c['runtime']==runtime()
    old=ROOT/PREVIOUS
    assert sha(old/'MANIFEST.json')=='4063c179e73776e9a615b2bbfdf65ecc2eeea86a8b2bda29baeda3bfdf9d988b'
    assert sha(old/'RESULT.json')=='07272075e30a1a700fcaba57be3b490a86682b092965432c6885e1a0e7105d29'
    assert sha(old/'BINDINGS.json')=='3e790eafe0a899d900e94ed8bf4adf2e268e5bab6bf96676ffd4680dc05845b4'
    m=read(old/'MANIFEST.json');entries=m.get('entries') or [{'path':n,**v} for n,v in m['files'].items()]
    inputs={}
    for e in entries:
        n=PREVIOUS+'/'+e['path'];assert sha(ROOT/n)==e['sha256'],n;inputs[n]=e['sha256']
    inputs[PREVIOUS+'/MANIFEST.json']=sha(old/'MANIFEST.json')
    b=read(old/'BINDINGS.json')
    for n,h in b['inputs'].items():
        nn=PREVIOUS+'/'+n;assert sha(ROOT/nn)==h,nn;inputs[nn]=h
    assert read(old/'RESULT.json')['independently_accepted']
    assert b['config']['root']==CONFIG['root'] and b['config']['D']==CONFIG['D'] and b['config']['mu']==CONFIG['mu']
    assert b['runtime']==runtime()
    common=read(old/'output/source/RESULT.json');terminal=read(old/'output/source/TERMINAL.json')
    assert common['guard']==terminal['guard']==sha(old/'BINDINGS.json')
    assert terminal['result_sha256']==sha(old/'output/source/RESULT.json')
    assert read(old/'output/zero/RESULT.json')['pass']
    inputs[str(control.relative_to(ROOT))+'/RESULT.json']=sha(control/'RESULT.json')
    binding={'utc':now(),'sources':sources(),'reviews':{n:sha(ROOT/n) for n in REVIEWS},
        'runtime':runtime(),'inputs':inputs,'config':CONFIG,'model_exact':b['model_exact'],
        'previous_manifest_count':len(entries),'new_physical_outcomes_before_freeze':False}
    atomic(ROOT/'BINDINGS.json',binding,True)
    atomic(ROOT/'FREEZE_RECORD.json',{'guard':sha(ROOT/'BINDINGS.json'),'utc':now()},True)
    for n in SOURCES+REVIEWS:(ROOT/n).chmod(0o444)
    print(json.dumps({'status':'FROZEN','guard':sha(ROOT/'BINDINGS.json'),'inputs':len(inputs)}))

def integrate(state,guard,out,jets,remaining_cpu):
    h=exact(CONFIG['step']);lo,hi=map(exact,CONFIG['D']);total=math.ceil(hi/h)
    wall0=time.monotonic();cpu0=time.process_time()
    priorwall=state['elapsed_seconds'];priorcpu=state['elapsed_cpu_seconds']
    while state['cell_index']<total:
        j=state['cell_index'];s=j*h
        ynext,cell=base.advance(state,h,nonlinear);base.require_finite(ynext)
        if bounds(cell['box'][4])[0]<=0:raise ArithmeticError('Source exponential positivity lost')
        state['max_picard']=max(state['max_picard'],cell['picard_iterations'])
        if s+h>=lo and s<=hi:
            a=max(fmpq(0),lo-s);b=min(h,hi-s)
            z=validated.range_on_cell(cell,a,b)
            state['cover'].append([str(s+a),str(s+b)])
            result=base.map_at(z,state['p'],state['preparation'],jets)
            state['map']=result if state.get('map') is None else {k:[hull(a,b) for a,b in zip(state['map'][k],result[k])] for k in result}
        state['y']=ynext;state['cell_index']+=1
        state['elapsed_seconds']=priorwall+time.monotonic()-wall0
        state['elapsed_cpu_seconds']=priorcpu+time.process_time()-cpu0
        if state['elapsed_cpu_seconds']>remaining_cpu:raise TimeoutError('Frozen cumulative graph CPU cap')
        if state['cell_index']%CONFIG['checkpoint_cells']==0 or state['cell_index']==total:save(out,state,guard)
    assert base.full_cover(state['cover'])
    return state

def tile(node,common,guard,out,remaining_cpu):
    out.mkdir(parents=True,exist_ok=True)
    if (out/'TERMINAL.json').exists():
        t=read(out/'TERMINAL.json');assert t['guard']==guard and t['result_sha256']==sha(out/'RESULT.json')
        r=unpack(read(out/'RESULT.json'))
        assert r['guard']==guard and r['status']=='COMPLETE' and r['node']==node
        assert r['common_sha256']==sha(ROOT/PREVIOUS/'output/source/RESULT.json')
        return r
    if (out/'FAILURE.json').exists():raise RuntimeError('Failed-closed tile restart refused')
    st=load(out,guard) if (out/'LATEST.json').exists() else {'task_index':0,'cell_index':0,'elapsed_seconds':0.,
         'elapsed_cpu_seconds':0.,'node':node,'phase_results':[]}
    assert st['node']==node
    try:
        common_path=ROOT/PREVIOUS/'output/source/RESULT.json';radii=list(map(exact,CONFIG['radii']))
        jets=common['jets'];I=interval(*map(exact,node['epsilon']))
        if 'preparation' not in st:
            st['preparation']=preparation.prepare(I,jets,common['p']);st['common_sha256']=sha(common_path)
        assert st['common_sha256']==sha(common_path)
        while st['task_index']<2:
            name=('center','box')[st['task_index']]
            if st['cell_index']==0:
                p=dict(common['p']);p.update(st['preparation']);p['x']=[arb(0) if name=='center' else interval(-r,r) for r in radii]
                lower=preparation.wall_increment(common['y0'],jets[0],p,p['eps'])['target']
                st.update(p=p,y=list(common['y0'])+[p['x'][0],lower,arb(1),arb(0),arb(0),arb(0),arb(0),arb(0)],max_picard=0,cover=[],map=None)
            integrate(st,guard,out,jets,remaining_cpu)
            phase={'phase':name,'guard':guard,'node':node,'map':st['map'],'event_cover':st['cover'],
                   'cells':st['cell_index'],'max_picard':st['max_picard'],'elapsed_seconds':st['elapsed_seconds'],'elapsed_cpu_seconds':st['elapsed_cpu_seconds']}
            if (out/(name+'.json')).exists():assert read(out/(name+'.json'))==pack(phase)
            else:atomic(out/(name+'.json'),phase,True)
            st['phase_results'].append(phase);st['task_index']+=1;st['cell_index']=0;save(out,st,guard)
        G=st['phase_results'][0]['map']['G'];flat=st['phase_results'][1]['map']['J'];J=[flat[3*i:3*i+3] for i in range(3)]
        C=list(map(exact,CONFIG['preconditioner_diagonal']))
        M=[[int(i==j)-C[i]*J[i][j] for j in range(3)] for i in range(3)]
        norms=[sum(maxabs(M[i][j])*radii[j] for j in range(3))/radii[i] for i in range(3)]
        image=[-C[i]*G[i]+sum((M[i][j]*interval(-radii[j],radii[j]) for j in range(3)),arb(0)) for i in range(3)]
        included=[maxabs(image[i])<exact(CONFIG['image_fraction'])*radii[i] for i in range(3)]
        passed=all(included) and max(norms)<=exact(CONFIG['contraction_ceiling'])
        result={'guard':guard,'node':node,'status':'COMPLETE','pass':passed,'G_center':G,'J_box':J,
            'image_offset':image,'image_ratios':[str(maxabs(v)/r) for v,r in zip(image,radii)],
            'weighted_row_norms':[str(v) for v in norms],'component_inclusions':included,
            'elapsed_seconds':st['elapsed_seconds'],'elapsed_cpu_seconds':st['elapsed_cpu_seconds'],
            'preparation':st['preparation'],'common_sha256':st['common_sha256'],
            'event_covers':[x['event_cover'] for x in st['phase_results']]}
        # A crash between atomic RESULT and TERMINAL does not repeat either
        # flow. The complete phase-boundary checkpoint reproduces the result.
        if (out/'RESULT.json').exists():assert read(out/'RESULT.json')==pack(result)
        else:atomic(out/'RESULT.json',result,True)
        atomic(out/'TERMINAL.json',{'guard':guard,'result_sha256':sha(out/'RESULT.json'),'utc':now()},True)
        atomic(out/'STATUS.json',{'state':'COMPLETE','guard':guard,'utc':now(),'pass':passed})
        print(json.dumps({'node':node,'pass':passed,'ratios':[float(maxabs(v)/r) for v,r in zip(image,radii)],'norms':list(map(float,norms)),'wall_seconds':st['elapsed_seconds']}),flush=True)
        return result
    except KeyboardInterrupt:
        atomic(out/'STOPPED.json',{'guard':guard,'utc':now(),'resumable':(out/'LATEST.json').exists()});raise
    except Exception as exc:
        atomic(out/'FAILURE.json',{'guard':guard,'utc':now(),'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()},True);raise

def launch(out):
    binding,guard=authenticate();out.mkdir(parents=True,exist_ok=True)
    lock=(out/'GRAPH.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if any((out/n).exists() for n in ('RESULT.json','TERMINAL.json','FAILURE.json')):raise RuntimeError('Terminal graph restart refused')
    resource.setrlimit(resource.RLIMIT_AS,(CONFIG['address_space_bytes'],CONFIG['address_space_bytes']))
    common=unpack(read(ROOT/PREVIOUS/'output/source/RESULT.json'))
    pending=[{'id':'r','depth':0,'epsilon':CONFIG['epsilon_interval']}];completed=[];accepted=[];unresolved=[];usedcpu=0.
    try:
        while pending:
            node=pending.pop(0)
            atomic(out/'STATUS.json',{'state':'RUNNING','guard':guard,'utc':now(),'active_node':node,
                'completed_nodes':len(completed),'maximum_nodes':7,'accepted_tiles':accepted,'pending':pending,
                'active_status':node['id']+'/STATUS.json','cpu_seconds_completed':usedcpu})
            r=tile(node,common,guard,out/node['id'],CONFIG['graph_integration_cpu_seconds_cap']-usedcpu)
            usedcpu+=r['elapsed_cpu_seconds'];completed.append(node)
            if r['pass']:accepted.append(node['epsilon'])
            elif node['depth']<2:
                a,b=map(exact,node['epsilon']);mid=(a+b)/2
                pending=[{'id':node['id']+'l','depth':node['depth']+1,'epsilon':[str(a),str(mid)]},
                         {'id':node['id']+'r','depth':node['depth']+1,'epsilon':[str(mid),str(b)]}]+pending
            else:unresolved.append(node['epsilon'])
            assert len(completed)<=CONFIG['maximum_cover_nodes']
        cover=coverage(accepted)
        label='CONNECTED_SIGNED_C4_BRANCH_CANDIDATE' if cover['full'] else 'PARTIAL_INTERVAL_C4_COVER' if accepted else 'NO_CONNECTED_INTERVAL_CERTIFICATE'
        result={'guard':guard,'utc':now(),'status':'COMPLETE','classification':label,'completed':completed,
            'accepted_tiles':accepted,'unresolved_tiles':unresolved,'coverage':cover,'cpu_seconds':usedcpu,
            'independently_accepted':False,'endpoint_and_local_identity':'REQUIRES_INDEPENDENT_AUDIT',
            'no_automatic_successor':True}
        atomic(out/'RESULT.json',result,True);atomic(out/'TERMINAL.json',{'guard':guard,'utc':now(),'result_sha256':sha(out/'RESULT.json')},True)
        atomic(out/'STATUS.json',{'state':'COMPLETE','guard':guard,'utc':now(),'classification':label})
    except KeyboardInterrupt:
        atomic(out/'STOPPED.json',{'guard':guard,'utc':now(),'resumable':True});raise
    except Exception as exc:
        atomic(out/'FAILURE.json',{'guard':guard,'utc':now(),'type':type(exc).__name__,'message':str(exc),
            'traceback':traceback.format_exc(),'accepted_tiles':accepted,'unresolved_tiles':unresolved,
            'unexamined':[node]+pending,'completed':completed},True)
        atomic(out/'STATUS.json',{'state':'TECHNICAL_INCOMPLETE','guard':guard,'utc':now(),'message':str(exc)});raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['preflight','child','child-parameter','freeze','launch']);p.add_argument('path',type=Path)
    a=p.parse_args();ctx.prec=CONFIG['bits'];ctx.threads=1
    assert all(os.environ.get(k)==v for k,v in ENV.items())
    if a.command=='preflight':preflight(a.path)
    elif a.command=='child':
        s=load(a.path,'manufactured-control');y,_=base.advance(s,s['h'],nonlinear);print(json.dumps({'digest':fingerprint(y)}))
    elif a.command=='child-parameter':
        s=load(a.path,'parameter-control');y,_=base.advance(s,s['h'],base.ParameterFixture);print(json.dumps({'digest':fingerprint(y)}))
    elif a.command=='freeze':freeze(a.path)
    elif a.command=='launch':launch(a.path)
