"""Independent saved-record exact bridge. No ODE or scientific producer imports."""
import ast, hashlib, json, os, platform, signal, sys, traceback
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
def need(x,msg):
    if not x: raise RuntimeError(msg)
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,data):
    p=OUT/name; t=OUT/(name+'.tmp'); need(not p.exists() and not t.exists(),'NO_OVERWRITE')
    with t.open('x') as f: json.dump(data,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.link(t,p); t.unlink()
def pair(x):
    need(all(isinstance(v,str) for v in x),'EXACT_STRING_INPUT'); a,b=map(Q,x); need(a<b,'ORDERED_INTERVAL'); return a,b
def binary64_label(text):
    # Exact nearest-even 53-bit conversion for finite nonzero normal decimals.
    x=Q(text)
    if not x: return Q(0)
    def power(n): return Q(2**n) if n>=0 else Q(1,2**(-n))
    sg=-1 if x<0 else 1; x=abs(x); e=0
    while x<power(e): e-=1
    while x>=power(e+1): e+=1
    need(-1022<=e<=1023,'NORMAL_BINARY64_RANGE')
    unit=power(e-52); n=x//unit; rem=x/unit-n
    if rem>Q(1,2) or (rem==Q(1,2) and n%2): n+=1
    return sg*n*unit
def constants(path):
    result={}
    for node in ast.parse(Path(path).read_text()).body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str): result[node.targets[0].id]=node.value.value
    return result
def main():
    need(sys.platform=='linux','LINUX_ONLY'); OUT.mkdir(exist_ok=True)
    need(not any((OUT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('BRIDGE_CAP_120'))); signal.alarm(120)
    adm=read(ROOT/'ADMISSION.json'); need(adm['admitted'] is True,'NOT_ADMITTED')
    need(sha(ROOT/'FROZEN.json')==adm['frozen_sha256'],'FROZEN_HASH')
    for p,d in read(ROOT/'FROZEN.json')['files'].items(): need(sha(p)==d,'FROZEN_FILE:'+p)
    runtime=read(ROOT/'RUNTIME_BINDINGS.json')
    need(str(Path(sys.executable).resolve())==runtime['executable_realpath'],'EXECUTABLE_PATH')
    for p,d in runtime['files'].items(): need(sha(p)==d,'RUNTIME_HASH:'+p)
    manifest=read(ROOT/'INPUTS.json'); records={}
    for key,item in manifest.items(): need(sha(item['path'])==item['sha256'],'INPUT_HASH:'+key); records[key]=Path(item['path'])
    put('STARTED.json',{'utc':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'platform':platform.platform(),'python':sys.version,'executable':sys.executable,'admission_sha256':sha(ROOT/'ADMISSION.json')})
    gates={}; details={}
    def gate(n,x): gates[n]=bool(x); need(x,n)
    # These controls have known exact dyadics and tie outcomes, no float use.
    gate('label_point_one',binary64_label('0.1')==Q(3602879701896397,36028797018963968))
    gate('label_negative',binary64_label('-0.1')==-Q(3602879701896397,36028797018963968))
    gate('ties_even_low',binary64_label(str(Q(1)+Q(1,2**53)))==1)
    gate('ties_even_high',binary64_label(str(Q(1)+Q(3,2**53)))==Q(1)+Q(1,2**51))
    p=read(records['primary_result']); ind=read(records['independent_result']); current=read(records['current_binding']); historical=read(records['phase_binding'])
    gate('current_historical_model_exact',current['model_exact']==historical['model_exact'])
    gate('current_historical_A_D',all(current['config'][k]==historical['config'][k] for k in ('A','D')))
    mapping={'M2':'m2','GAMMA':'gamma','V0':'v0','V1':'v1','LAMBDA_A':'lambda_a','LAMBDA_B':'lambda_b'}
    for role in ('primary','independent'):
        vals=constants(records[role+'_source'])
        derived={key:binary64_label(vals[label]) for label,key in mapping.items()}
        for key,val in derived.items(): gate(role+'_exact_model_'+key,val==Q(current['model_exact'][key]))
        details[role+'_exact_model']={key:str(v) for key,v in derived.items()}
    gate('primary_complete',p['status']=='COMPLETE' and p['classification']=='RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS')
    gate('independent_complete',ind['status']=='COMPLETE' and ind['classification']=='INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS')
    n=p['finest_narrow_result']; inputbox=pair(n['box_exact_dyadic_bounds']); ni=pair(n['interval_newton_image']['exact_bounds']); ia=pair(current['config']['A']); di=pair(current['config']['D'])
    gate('primary_strict_newton',inputbox[0]<ni[0]<ni[1]<inputbox[1] and n['strict_self_map'] and n['qualified_newton_inclusion'])
    gate('current_A_literal_image',ni==ia); gate('current_D_literal_event',pair(n['box_event']['event_bracket'])==di)
    gate('same_common_input_box',tuple(binary64_label(x) for x in ind['frozen_inputs']['root_box'])==inputbox)
    gate('independent_exact_level_inventory',[lev['steps'] for lev in ind['levels']]==[8192,16384])
    for lev in ind['levels']:
        label=str(lev['steps']); image=pair(lev['interval_newton_image']['exact_bounds'])
        gate(label+'_strict_newton',inputbox[0]<image[0]<image[1]<inputbox[1] and lev['strict_self_map'] and lev['root_replay_pass'])
        gate(label+'_geometry_reported',lev['geometry']['pass'] and all(lev['geometry']['checks'].values()))
        for field in ('root_box','center'):
            ev=lev[field]; gate(label+field+'_event_reported',all(ev[k] for k in ('zero_cells_contiguous','positive_before','negative_after','G_s_strictly_negative','q_a_excludes_zero','event_validated')))
            qa=pair(ev['event_quantities']['q_a']['exact_bounds']); gs=pair(ev['event_quantities']['G_s']['exact_bounds'])
            gate(label+field+'_derivatives',gs[1]<0 and (qa[0]>0 or qa[1]<0))
        for key in ('S','curvature'): gate(label+'_positive_'+key,pair(lev['root_box']['event_quantities'][key]['exact_bounds'])[0]>0)
        gate(label+'_positive_warp',pair(lev['geometry']['global_warp_enclosure']['exact_bounds'])[0]>0)
    gate('lower_T_negative',Q(current['model_exact']['gamma'])>0 and inputbox[1]<Q(current['model_exact']['v0']))
    # Strong domain/action separation: no substitution of distinct oscillator boundary law.
    gate('background_gamma20',Q(current['model_exact']['gamma'])==20)
    details.update(A=list(map(str,ia)),D=list(map(str,di)),common_root_input=list(map(str,inputbox)))
    for key,item in manifest.items(): need(sha(item['path'])==item['sha256'],'INPUT_CHANGED:'+key)
    put('RESULT.json',{'classification':'EXACT_BACKGROUND_TO_CURRENT_AB_BRIDGE_VERIFIED','gates':gates,'details':details,'inputs':manifest,
        'scope':'Exact saved-record/model/box linkage only; root existence and internal interval predicates inherited. Common-box uniqueness is the analytic identification, not approximate root overlap. No ODE or Arb execution.',
        'current_boundary_action_requires_separate_analytic_bridge':True,'utc':datetime.now(timezone.utc).isoformat()})
    signal.alarm(0)
if __name__=='__main__':
    try: main()
    except BaseException as e:
        if OUT.is_dir() and not (OUT/'FAILURE.json').exists(): put('FAILURE.json',{'classification':'BRIDGE_QUALIFICATION_INCOMPLETE','error':repr(e),'traceback':traceback.format_exc()})
        raise
