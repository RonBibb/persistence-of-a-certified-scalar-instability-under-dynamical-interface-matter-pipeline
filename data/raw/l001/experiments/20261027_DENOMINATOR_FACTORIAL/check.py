"""Typed Klein-Gordon source paired full certificates."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def need(v,n):
    if not v:raise AssertionError(n)
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def transfer(e,c,row,mode,split):
    cn,xn,bm,bk,br,bj,bo=e;r=c['rho'];d0=c['d0'];dc=c['dc'];n=Q(row['n_lower'])
    sp=3*cn/n+64*bm;sc=36*sp/n+112*cn/(n*n)+br
    sg=(2/n+4/(n*n))*cn+12*sp/n+bk
    F=sg+80*sc/(dc*n*n);rw=2*cn/n+39*xn/(n*n)+2*bj+bo/2
    G=(Q(1,2)+1/(d0*n*n))*rw+2*sc/(d0*n)
    f=split['F'];g=split['G']
    X=f['value']*F+g['value']*G;Y=f['gradient']*F+g['gradient']*G
    U=f['total']*F+g['total']*G
    mp=(f['real_gradient']/n+9*f['real_value']/(n*n))*F+(g['real_gradient']/n+9*g['real_value']/(n*n))*G
    op=(f['real_value']*F+g['real_value']*G)/n
    xp=((sc+mp)/d0+r*(X/(3*n)+sp/2))/(1-3*r/n)
    yp=6*xp/n+2*X/(3*n)+sp
    up=(1+4/(n*n))*xp+(1+6/n)*yp+26*X/(3*n*n)+2*Y/(3*n)+(6+6/n)*sp/r
    return (3*up+cn+U,32768*(op+xn/4+bo))
NAMES=('TRACE','GRAPH','BM','BK','BR','BJ','BO')
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    parent=BASE/'20261027_BACKGROUND_SEED_CERTIFICATE_R1'
    bind(parent/'TERMINAL.json','76587dbd7c33d3bb9dcb4c7db565d754c4786b66d1eadf66830bc490c98b5315')
    t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
    def authenticated(name):
        p=BASE/name/'RESULT.json';gate(inputs.get(str(p))==sha(p),'AUTHORITY:'+name);return read(p)
    ir=authenticated('20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE')
    iv={k:Q(v) for k,v in authenticated('20261026_NEUTRAL_ANALYTIC_INVERSE')['constants_exact'].items()}
    hr=authenticated('20261027_HARMONIC_MATCHED_INVERSE')['rows']
    prior=authenticated('20261027_SPLIT_FORCING_BOUNDARY_CERTIFICATE')
    delta=iv['delta'];rho=iv['rho'];dold=iv['real_D_normalized_lower'];dcold=iv['complex_D_normalized_lower']
    drift=delta+delta*delta/2+Q(15,2048)*(32*delta+delta*delta)
    gate(drift==iv['denominator_variation'] and dold==Q(3,16384) and dcold==dold/2,'OLD_DENOMINATOR_REPLAY')
    gate(set(ir['arms'])=={'primary','independent'},'TWO_ENGINES')
    alpha={name:Q(arm['extrema']['alpha']) for name,arm in ir['arms'].items()}
    dnew=3*min(alpha.values());dcnew=dnew-drift
    gate(dnew>=dold>0 and dcnew>=dcold>0,'DENOMINATOR_DOMINATION')
    configs=dict(baseline=dict(rho=rho,d0=dold,dc=dcold),real=dict(rho=rho,d0=dnew,dc=dcold),complex=dict(rho=rho,d0=dold,dc=dcnew),joint=dict(rho=rho,d0=dnew,dc=dcnew))
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
    auth=BASE/'20261027T020711Z_TWO_HOUR_CONTINUATION/AUTHORITY.txt';bind(auth,sha(auth))
    len(str(10**20000));runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=1793074031))
    expected={e+':'+str(n) for e in ('primary','independent') for n in range(2,65)}|{e+':high_n_ge_65' for e in ('primary','independent')}
    gate(set(hr)==set(prior['split_inverse_rows'])==expected,'ALL128_ROWS')
    inverse={};weights={};controls={};raw={}
    for mode,c in configs.items():
        inverse[mode]={}
        for label,row in hr.items():
            gate(row['n_lower']==(65 if row['tail'] else int(label.split(':')[-1])),'ROW_LABEL:'+label)
            n=Q(row['n_lower']);A=12+160/(c['dc']*n*n);B=9/(n*n)+Q(289*5,2048)+2080/(c['dc']*n**4)
            if mode=='baseline':gate(A==Q(row['A']) and B==Q(row['B']),'OLD_AB:'+label)
            u=B*rho*rho/4;v=A*rho*rho/8;w=B*rho/2;z=A*rho/5;det=(1-u)*(1-z)-v*w
            gate(0<=u<1 and 0<=z<1 and det>0,'POSITIVE_INVERSE:'+mode+':'+label)
            channels={}
            for name in ('F','G'):
                old=prior['split_inverse_rows'][label][name];cv=Q(old['real_value']);cg=Q(old['real_gradient']);f=Q(int(name=='F'))
                a=cv+rho*cg/2+f*rho*rho/4;b=cg+f*rho/2
                x=((1-z)*a+v*b)/det;y=(w*a+(1-u)*b)/det;zz=B*x+A*y/2+f
                gate(x==a+u*x+v*y and y==b+w*x+z*y,'SYSTEM:'+mode+':'+label+':'+name)
                new=dict(real_value=cv,real_gradient=cg,value=x,gradient=y,curvature=zz,total=x+y+zz)
                if mode=='baseline':gate({k:str(v) for k,v in new.items()}==old,'OLD_CHANNEL:'+label+':'+name)
                gate(all(0<val<=Q(old[k]) for k,val in new.items()),'CHANNEL_DOMINATION:'+mode+':'+label+':'+name)
                channels[name]=new
            inverse[mode][label]=channels
        weights[mode]={out:[] for out in ('B','C')}
        for i,name in enumerate(NAMES):
            e=[Q(0)]*7;e[i]=Q(1);entries={}
            for label,row in hr.items():
                vals=transfer(e,c,row,mode,inverse[mode][label]);entries[label]=vals
                old=list(map(Q,prior['harmonic_coefficients']['split:'+name][label]))
                if mode=='baseline':gate(vals==tuple(old),'OLD_SOURCE_PAIR:'+name+':'+label)
                gate(all(0<=val<=ov for val,ov in zip(vals,old)),'PAIR_DOMINATION:'+mode+':'+name+':'+label)
            raw[mode+':'+name]={k:list(map(str,v)) for k,v in entries.items()}
            for j,out in enumerate(('B','C')):
                top=max(vals[j] for vals in entries.values());weights[mode][out].append(top)
                controls[mode+':'+out+':'+name]=[k for k,vals in entries.items() if vals[j]==top]
    for name in NAMES:
        for label in hr:
            gate(all(Q(raw['joint:'+name][label][j])<=min(Q(raw['real:'+name][label][j]),Q(raw['complex:'+name][label][j])) for j in (0,1)),'PAIR_FACTORIAL_ORDER:'+name+':'+label)
    gate({out:list(map(str,vals)) for out,vals in weights['baseline'].items()}==prior['weights']['split'],'OLD_FULL_WEIGHTS')
    gate(all(weights['joint'][out][i]<=min(weights['real'][out][i],weights['complex'][out][i])<=weights['baseline'][out][i] for out in ('B','C') for i in range(7)),'FACTORIAL_ORDER')
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,digest in dict(inputs,**sources).items():need(sha(p)==digest,'POST:'+p)
    result=dict(pass_status=True,classification='REAL_COMPLEX_DENOMINATOR_FACTORIAL_DIAGNOSTIC',denominators={k:str(v) for k,v in dict(old_real=dold,old_complex=dcold,new_real=dnew,new_complex=dcnew,drift=drift,delta=delta,rho=rho).items()},alpha={k:str(v) for k,v in alpha.items()},configs={m:{k:str(v) for k,v in c.items()} for m,c in configs.items()},weights={m:{out:list(map(str,vals)) for out,vals in ww.items()} for m,ww in weights.items()},controls=controls,source_coefficients=raw,inverse_rows={m:{label:{kind:{k:str(v) for k,v in rr.items()} for kind,rr in row.items()} for label,row in rows.items()} for m,rows in inverse.items()},gates=gates,seconds=time.monotonic()-started,ode_solves=0,new_convergence_certificate=False)
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps(dict(seconds=result['seconds'],gates=len(gates),denominators={k:float(Q(v)) for k,v in result['denominators'].items()},coefficient_gains={m:{out:{name:float(weights['baseline'][out][i]/ww[out][i]) for i,name in enumerate(NAMES)} for out in ('B','C')} for m,ww in weights.items() if m!='baseline'})),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(time.time()<1793074031,'FIXED_WINDOW_CUTOFF');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(frozen)['files'][str(lp)],'LEASE_PIN')
        lease=load('component_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        need(time.time()<1793074031,'POST_LEASE_LAUNCH_CUTOFF')
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('COMPONENT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
