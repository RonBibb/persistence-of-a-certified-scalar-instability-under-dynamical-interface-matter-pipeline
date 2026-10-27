"""Bounded analytic and actual-MP-step recovery controls; no physical shooting."""
import argparse,json,os,platform,subprocess,sys,time
from pathlib import Path
import mpmath as mp
from mp_background import coefficients,evaluate,decimal,rational,integrate
from runner import sha,write,read,runtime,validate_checkpoint,reject_stopped_packet
from independent_review import polynomial_control

HERE=Path(__file__).resolve().parent
P=HERE/'preflight-final'
def unpack(state):
    mp.mp.dps=state['dps']
    return [mp.mpf(v) for v in state['state']]
def advance(state):
    y=unpack(state)
    return [decimal(v) for v in evaluate(coefficients(y,rational(state['k']),mp.mpf('0.41'),24),rational(state['step']))]
def main():
    arg=argparse.ArgumentParser();arg.add_argument('--resume-control');a=arg.parse_args()
    if platform.system()!='Linux':raise RuntimeError('Linux required')
    if a.resume_control:
        record=read(a.resume_control)
        if record['source_sha256']!=sha(HERE/'mp_background.py'):raise RuntimeError('control source mismatch')
        print(json.dumps(advance(record)));return
    if P.exists():raise RuntimeError('preflight is immutable; use fresh controls namespace after review')
    P.mkdir();began=time.monotonic();mp.mp.dps=50;k=rational('3/10000')
    initial=[mp.mpf(0),-mp.sqrt(1+k),mp.mpf(0),mp.mpf(0),mp.mpf(1),mp.mpf(0)]
    errors=[]
    for control in [dict(dps=50,degree=24,step_denominator=64,shoot_tolerance='1e-30'),dict(dps=70,degree=30,step_denominator=128,shoot_tolerance='1e-45')]:
        mp.mp.dps=control['dps'];k=rational('3/10000')
        initial=[mp.mpf(0),-mp.sqrt(1+k),mp.mpf(0),mp.mpf(0),mp.mpf(1),mp.mpf(0)]
        solution,_=integrate(initial,k,{'m2':rational('41/100')},control,False)
        maximum=mp.mpf(0)
        for j in range(33):
            s=mp.mpf(j)/16;y=solution.at(s);warp=mp.cosh(s)-mp.sqrt(1+k)*mp.sinh(s)
            H=(mp.sinh(s)-mp.sqrt(1+k)*mp.cosh(s))/warp
            maximum=max(maximum,abs(y[0]-mp.log(warp)),abs(y[1]-H),abs(y[4]-1/warp))
        errors.append({'dps':control['dps'],'max_error':decimal(maximum),'pass':maximum<=mp.mpf('1e-20')})
    mp.mp.dps=50;k=rational('3/10000')
    initial=[mp.mpf(0),-mp.sqrt(1+k),mp.mpf(0),mp.mpf(0),mp.mpf(1),mp.mpf(0)]
    first=evaluate(coefficients(initial,k,rational('41/100'),24),mp.mpf(1)/32)
    state={'dps':50,'k':'3/10000','step':'1/32','state':[decimal(v) for v in first],'source_sha256':sha(HERE/'mp_background.py')}
    write(P/'MP_CHECKPOINT.json',state,True)
    expected=advance(state)
    child=subprocess.run([sys.executable,'-B',str(HERE/'preflight.py'),'--resume-control',str(P/'MP_CHECKPOINT.json')],capture_output=True,text=True,check=True)
    recovered=json.loads(child.stdout)
    exact_resume=(expected==recovered)
    exact_serialization=all(x._mpf_==mp.mpf(decimal(x))._mpf_ for x in first)
    altered=dict(state,source_sha256='0'*64);write(P/'ALTERED_SOURCE_CONTROL.json',altered,True)
    bad=subprocess.run([sys.executable,'-B',str(HERE/'preflight.py'),'--resume-control',str(P/'ALTERED_SOURCE_CONTROL.json')],capture_output=True,text=True)
    import runner
    runner.OUT=P
    fake={'guard':'bound','runtime':runtime(),'completed':{},'pending':['center_coarse']}
    design={'runtime':runtime(),'points':[{'name':'center'}],'controls':[{'name':'coarse'}]}
    validate_checkpoint(fake,'bound',design)
    rejected=[]
    for change in [{'guard':'stale'},{'runtime':{}},{'pending':[]},{'completed':{'center_coarse':{'receipt':'partial.tmp','receipt_sha256':'bad','arrays':'absent','arrays_sha256':'bad','background':'absent','background_sha256':'bad'}},'pending':[]}]:
        try:validate_checkpoint(dict(fake,**change),'bound',design)
        except Exception:rejected.append(True)
        else:rejected.append(False)
    terminal_test=P/'terminal_fixture';terminal_test.mkdir()
    write(terminal_test/'TERMINAL.json',{'status':'COMPLETE'},True)
    try:reject_stopped_packet(terminal_test)
    except RuntimeError:terminal_rejected=True
    else:terminal_rejected=False
    independent_polynomial=polynomial_control()
    result={'pass':all(x['pass'] for x in errors) and exact_resume and exact_serialization and bad.returncode!=0 and all(rejected) and terminal_rejected and independent_polynomial['pass'],
            'vacuum':errors,'fresh_process_exact_next_step':exact_resume,'lossless_mp_round_trip':exact_serialization,
            'altered_source_rejected':bad.returncode!=0,'stale_guard_runtime_order_partial_rejected':rejected,
            'terminal_restart_rejected':terminal_rejected,
            'independent_polynomial':independent_polynomial,
            'runtime':runtime(),'source_sha256':{n:sha(HERE/n) for n in ['mp_background.py','runner.py','sample_checks.py','preflight.py','independent_review.py']},
            'physical_science_run':False,'seconds':time.monotonic()-began}
    write(P/'RESULT.json',result,True);print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
