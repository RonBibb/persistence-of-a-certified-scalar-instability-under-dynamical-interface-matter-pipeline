"""One bounded proper-distance reconstruction and nine-point stability test."""
import argparse,datetime,hashlib,importlib.util,json,os,platform,signal,time
from fractions import Fraction
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp,simpson
from scipy.interpolate import PPoly
from scipy.optimize import brentq
from independent_checks import check,load_helper,scaled

HERE=Path(__file__).resolve().parent
OUT=HERE/'spectrum-r1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,x,immutable=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if immutable and p.exists():raise RuntimeError('refusing overwrite '+str(p))
    def scalar(obj):
        if isinstance(obj,np.generic):return obj.item()
        raise TypeError('Unsupported JSON object '+type(obj).__name__)
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False,default=scalar)+'\n');os.replace(tmp,p)
    if immutable:p.chmod(0o444)

def authenticate():
    b=json.loads((HERE/'SPECTRUM_R1_BINDINGS.json').read_text())
    for n,h in b['source'].items():
        if sha(HERE/n)!=h:raise RuntimeError('source mismatch '+n)
    for n,x in b['inputs'].items():
        if sha(HERE/x['path'])!=x['sha256']:raise RuntimeError('input mismatch '+n)
    if platform.system()!='Linux':raise RuntimeError('Linux numerical execution required')
    runtime={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'longdouble_nmant':int(np.finfo(np.longdouble).nmant)}
    if runtime!=b['runtime']:raise RuntimeError('runtime binding mismatch')
    for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']:
        if os.environ.get(key)!='1':raise RuntimeError('thread control '+key)
    return b

def bg_rhs(m,k,s,y):
    W,H,phi,T,z=y
    return [H,-T*T/3-k*np.exp(-2*W),T,m['m2']*phi-4*H*T,np.exp(-W)]

def launch(m,a):
    H=-(m['lambda_a']+m['gamma']*(a-m['v0'])**2/2)/6
    T=m['gamma']*(a-m['v0'])/2
    k=H*H-1-T*T/12+m['m2']*a*a/12
    return np.array([0.,H,a,T,0.]),k

def background(m,bracket,control):
    rtol=control['rtol'];den=control['step_denominator']
    def evaluate(a,dense=False):
        y,k=launch(m,a)
        if k<=0:raise RuntimeError('nonpositive curvature')
        def event(s,Y):return Y[1]-(m['lambda_b']+m['gamma']*(Y[2]-m['v1'])**2/2)/6
        event.direction=-1;event.terminal=True
        if event(0,y)<=0:raise RuntimeError('nonpositive initial Israel event')
        sol=solve_ivp(lambda s,Y:bg_rhs(m,k,s,Y),(0,2),y,method='DOP853',rtol=rtol,atol=rtol*1e-3,max_step=2/den,events=event,dense_output=dense)
        if not sol.success or len(sol.t_events[0])!=1:raise RuntimeError('first event not admitted')
        end=sol.y_events[0][0];res=end[3]+m['gamma']*(end[2]-m['v1'])/2
        return float(res),sol,float(k)
    lo,hi=bracket;f0=evaluate(lo)[0];f1=evaluate(hi)[0]
    if f0*f1>=0:raise RuntimeError('background bracket failed')
    root=brentq(lambda a:evaluate(a)[0],lo,hi,xtol=5e-17,rtol=1e-14,maxiter=80)
    residual,sol,k=evaluate(root,True)
    return {'a':float(root),'k':k,'D':float(sol.t[-1]),'L':float(sol.y[4,-1]),'scalar_wall':residual,'bracket_values':[f0,f1]},sol

def mode_rhs(m,k,bg,mu,s,y):
    W,H,phi,T,z=bg.sol(s);psi,f,g=y
    return [-2*H*psi-T*f/3,g,-4*H*g+(m['m2']-mu*np.exp(-2*W)+2*T*T)*f+(12*H*T-4*m['m2']*phi)*psi]

def mode(m,meta,bg,control):
    mu_bracket=(-.0015,-.0011);D=meta['D'];k=meta['k'];rtol=control['rtol'];den=control['step_denominator']
    W,H,phi,T,z=bg.y[:,0]
    B=m['gamma']*T/2-(m['m2']*phi-4*H*T)
    if abs(B)<=1e-12:raise RuntimeError('lower normalization degeneracy')
    def evaluate(mu,dense=False):
        f=3*(mu+4*k)/B;initial=[1.,f,m['gamma']*f/2-2*T]
        sol=solve_ivp(lambda s,y:mode_rhs(m,k,bg,mu,s,y),(0,D),initial,method='DOP853',rtol=rtol,atol=rtol*1e-3,max_step=D/den,dense_output=dense)
        if not sol.success:raise RuntimeError(sol.message)
        h,f,g=sol.y[:,-1];Tb=bg.y[3,-1]
        return float(g+2*Tb*h+m['gamma']*f/2),sol
    lo,hi=mu_bracket;f0=evaluate(lo)[0];f1=evaluate(hi)[0]
    if f0*f1>=0:raise RuntimeError('fixed mass bracket failed')
    mu=brentq(lambda mu:evaluate(mu)[0],lo,hi,xtol=5e-16,rtol=2e-14,maxiter=80)
    res,sol=evaluate(mu,True)
    return float(mu),sol,{'bracket':list(mu_bracket),'endpoint_values':[f0,f1],'wall_residual':res,'initial_denominator':float(B)}

def controls(helper):
    import sympy as sp
    W,H,P,T,h,f,g,k,mu,m2=sp.symbols('W H P T h f g k mu m2')
    C=T*g-(m2*P-4*H*T)*f+(2*T*T-3*(mu+4*k)*sp.exp(-2*W))*h
    flow=[H,-T*T/3-k*sp.exp(-2*W),T,m2*P-4*H*T,-2*H*h-T*f/3,g,-4*H*g+(m2-mu*sp.exp(-2*W)+2*T*T)*f+(12*H*T-4*m2*P)*h]
    identity=sp.simplify(sum(sp.diff(C,x)*v for x,v in zip([W,H,P,T,h,f,g],flow))+4*H*C)==0
    pc=helper.polynomial_control()
    vac=[]
    for kval in [0.,.0003268413384542497]:
        s=np.linspace(0,2,1001);v=np.sqrt(1+kval)
        w=np.cosh(s)-v*np.sinh(s);hp=(np.sinh(s)-v*np.cosh(s))/w
        psi=1/w**2
        def fun(t,y):
            w0=np.cosh(t)-v*np.sinh(t);H0=(np.sinh(t)-v*np.cosh(t))/w0
            return [-2*H0*y[0],y[2],-4*H0*y[2]+(.41+4*kval/w0**2)*y[1]]
        sol=solve_ivp(fun,(0,2),[1,0,0],method='DOP853',rtol=2e-12,atol=2e-15,t_eval=s,max_step=2/128)
        error=float(np.max(abs(sol.y[0]/psi-1)))
        exact=scaled([2*hp*psi,-2*hp*psi])
        vac.append({'k':kval,'profile_relative_error':error,'exact_momentum':exact,'pass':sol.success and error<=1e-8 and exact<=1e-10})
    q=brentq(lambda x:x*np.tan(x)-1,1e-8,np.pi/2-1e-8,xtol=1e-15)
    robin=max(abs(q*np.sin(q)-np.cos(q)),abs(-q*np.sin(q)+np.cos(q)))
    return {'symbolic_proper_constraint_identity':identity,'polynomial':pc,'vacuum':vac,'flat_robin_error':robin,'pass':identity and pc['first_derivative_max_error']<=1e-20 and pc['second_derivative_max_error']<=1e-20 and all(x['pass'] for x in vac) and robin<=1e-10}

def central_comparison(data,meta,mu,bindings):
    inp=lambda n:HERE/bindings['inputs'][n]['path']
    raw=np.load(inp('old_background_arrays'),allow_pickle=False);old=json.loads(inp('old_summary').read_text());receipt=json.loads(inp('old_background_receipt').read_text())['report']
    pp=PPoly(raw['poly_coefficients'],raw['mesh']);oldL=float(np.exp(raw['parameters'][0]))
    W,H,phi,T,z=data['background'];new=np.array([W,np.exp(W)*H,phi,np.exp(W)*T]);ref=pp(z/oldL).T
    diffs=np.max(abs(new-ref)/(1+abs(ref)),axis=1)
    d1=json.loads(inp('d1_high_result').read_text());ind=json.loads(inp('d1_independent_result').read_text());fine=max(ind['levels'],key=lambda x:x['steps'])
    inside=lambda v,ab:Fraction.from_float(v)>=Fraction(ab[0]) and Fraction.from_float(v)<=Fraction(ab[1])
    drel=abs(meta['D']/receipt['proper_separation_D']-1);lrel=abs(meta['L']/oldL-1)
    checks={'a_in_D1':inside(meta['a'],d1['narrow']['newton_exact_bounds']),'D_in_D1':d1['narrow']['event_bracket'][0]<=meta['D']<=d1['narrow']['event_bracket'][1],'k_in_D1':inside(meta['k'],fine['geometry']['curvature']['exact_bounds']),'mass_agreement':abs(mu-old['mu'])<=1e-7,'D_agreement':drel<=1e-7,'L_agreement':lrel<=1e-7,'whole_profile_agreement':float(max(diffs))<=1e-7}
    return {'checks':checks,'pass':all(checks.values()),'mass_difference':mu-old['mu'],'D_relative_difference':drel,'L_relative_difference':lrel,'profile_scaled_maxima':dict(zip(['W','A_conformal','Phi','S_conformal'],map(float,diffs)))}

def run_case(point,control,bindings,helper):
    began=time.monotonic();m=dict(bindings['model']);m.update(point['parameters'])
    meta,bg=background(m,bindings['root_bracket'],control);mu,md,shoot=mode(m,meta,bg,control)
    s=np.linspace(0,meta['D'],2001);B=bg.sol(s);Y=md.sol(s);data={'s':s,'background':B,'mode':Y}
    independent=[check(data,m,mu,meta['k'],helper,stride) for stride in [2,1]]
    turn=brentq(lambda s:bg.sol(s)[3],0,meta['D'],xtol=1e-14);Wt,Ht,pt,Tt,zt=bg.sol(turn);ht,ft,gt=md.sol(turn)
    turn_error=scaled([m['m2']*pt*ft,3*(mu+4*meta['k'])*np.exp(-2*Wt)*ht])
    Z=float(2*simpson(np.exp(2*B[0])*(Y[1]**2+6*Y[0]**2),x=s));dD=float(-2*simpson(Y[0],x=s))
    checks={'background_independent':all(x['max_background']<=1e-8 for x in independent),'mode_independent':all(x['max_mode']<=1e-6 for x in independent),'turn_relation':turn_error<=1e-6,'positive_norm':Z>0,'nonzero_overlap':abs(dD/np.sqrt(Z))>1e-6,'negative_mass':mu<-1e-8,'norm_independent_agreement':all(abs(x['Z']/Z-1)<=1e-7 and abs(x['deltaD']/dD-1)<=1e-7 for x in independent)}
    comp=central_comparison(data,meta,mu,bindings) if point['name']=='center' else None
    if comp is not None:checks['central_branch_qualified']=comp['pass']
    out={'point':point,'control':control,'background':meta,'model':m,'mu':mu,'lambda':mu+4*meta['k'],'mu_over_k':mu/meta['k'],'growth_over_H':float(np.sqrt(2.25-mu/meta['k'])-1.5),'Z':Z,'deltaD':dD,'overlap':dD/np.sqrt(Z),'turn':{'s':float(turn),'normalized_relation':turn_error},'shooting':shoot,'independent_checks':independent,'central_comparison':comp,'checks':checks,'accepted':all(checks.values()),'elapsed_seconds':time.monotonic()-began,'evidence_classification':'NUMERICAL_BINARY64_SOLVES_WITH_EXTENDED_SAMPLE_VERIFICATION'}
    return out,data

def pair_checks(x,y):
    if 'mu' not in x or 'mu' not in y:return {'case_solves_completed':False}
    dm=abs(x['mu']-y['mu']);dl=abs(x['lambda']-y['lambda'])
    return {'both_individually_admitted':x['accepted'] and y['accepted'],'mass_refinement':dm<=1e-7,'mass_sign_resolved':abs(y['mu'])>100*dm and y['mu']<-1e-8,'exceptional_sector_separated':abs(y['lambda'])>100*dl}

def main():
    b=authenticate();OUT.mkdir(exist_ok=True);guard=sha(HERE/'SPECTRUM_R1_BINDINGS.json')
    if (OUT/'TERMINAL.json').exists():raise RuntimeError('terminal packet must not restart')
    if (OUT/'FAILURE.json').exists():raise RuntimeError('failed packet requires an explicit successor')
    helper=load_helper(HERE/b['inputs']['differentiation_helper']['path'])
    controlpath=OUT/'CONTROLS.json'
    if controlpath.exists():ctl=json.loads(controlpath.read_text())
    else:
        ctl=controls(helper);ctl['guard']=guard;write(controlpath,ctl,True)
    if ctl.get('guard')!=guard:raise RuntimeError('control receipt guard mismatch')
    if not ctl['pass']:raise RuntimeError('controls failed')
    tasks=[(p,c) for p in b['points'] for c in b['controls']]
    cp_path=OUT/'CHECKPOINT.json'
    cp=json.loads(cp_path.read_text()) if cp_path.exists() else {'guard':guard,'controls_sha256':sha(controlpath),'completed':{},'started_utc':now()}
    if cp['guard']!=guard:raise RuntimeError('checkpoint guard mismatch')
    if cp.get('controls_sha256')!=sha(controlpath):raise RuntimeError('checkpoint controls digest mismatch')
    for name,rec in cp['completed'].items():
        if sha(OUT/rec['receipt'])!=rec['receipt_sha256'] or sha(OUT/rec['arrays'])!=rec['arrays_sha256']:raise RuntimeError('checkpoint artifact mismatch '+name)
    halt_reason=None
    def timeout(signum,frame):raise TimeoutError('600 second case cap exceeded')
    signal.signal(signal.SIGALRM,timeout)
    for i,(point,control) in enumerate(tasks):
        prior_center=[json.loads((OUT/cp['completed'][name]['receipt']).read_text()) for name in ['center_coarse','center_fine'] if name in cp['completed']]
        if any(not row['accepted'] for row in prior_center):
            halt_reason='CENTRAL_QUALIFICATION_FAILED';break
        if point['name']!='center' and (len(prior_center)!=2 or not all(pair_checks(*prior_center).values())):
            halt_reason='CENTRAL_PAIRED_QUALIFICATION_FAILED';break
        name=point['name']+'_'+control['name']
        if name in cp['completed']:continue
        receipt=OUT/(name+'.json');arr=OUT/(name+'.npz')
        if receipt.exists():
            recovered=json.loads(receipt.read_text())
            if recovered['guard']!=guard or not arr.exists() or sha(arr)!=recovered['arrays_sha256']:
                raise RuntimeError('partial publication does not authenticate '+name)
            cp['completed'][name]={'receipt':receipt.name,'receipt_sha256':sha(receipt),'arrays':arr.name,'arrays_sha256':sha(arr)}
            cp['pending']=[p['name']+'_'+c['name'] for p,c in tasks if p['name']+'_'+c['name'] not in cp['completed']]
            write(cp_path,cp)
            if point['name']=='center' and not recovered['accepted']:
                halt_reason='CENTRAL_QUALIFICATION_FAILED';break
            continue
        if arr.exists():raise RuntimeError('orphaned unreceipted array requires recovery review '+name)
        write(OUT/'STATUS.json',{'phase':'RUNNING','case':name,'completed':len(cp['completed']),'total':len(tasks),'pid':os.getpid(),'updated_utc':now(),'guard':guard,'informational_only':True})
        signal.alarm(600)
        try:out,data=run_case(point,control,b,helper)
        except Exception as exc:
            out={'point':point,'control':control,'accepted':False,'error_type':type(exc).__name__,'error':str(exc),'checks':{'case_completed':False},'evidence_classification':'TECHNICAL_OR_QUALIFICATION_UNRESOLVED'}
            data={}
        finally:signal.alarm(0)
        tmp=OUT/(name+'.tmp.npz');np.savez_compressed(tmp,**data);os.replace(tmp,arr);arr.chmod(0o444)
        out['arrays_sha256']=sha(arr);out['guard']=guard
        write(receipt,out,True)
        cp['completed'][name]={'receipt':receipt.name,'receipt_sha256':sha(receipt),'arrays':arr.name,'arrays_sha256':sha(arr)}
        cp['pending']=[p['name']+'_'+c['name'] for p,c in tasks if p['name']+'_'+c['name'] not in cp['completed']]
        write(cp_path,cp)
        print(json.dumps({'completed':len(cp['completed']),'case':name,'accepted':out['accepted'],'mu':out.get('mu'),'seconds':out.get('elapsed_seconds'),'error':out.get('error')}),flush=True)
        if point['name']=='center' and not out['accepted']:
            halt_reason='CENTRAL_QUALIFICATION_FAILED';break
    pairs=[]
    for point in b['points']:
        paths=[OUT/(point['name']+'_'+tag+'.json') for tag in ['coarse','fine']]
        if not all(p.exists() for p in paths):
            pairs.append({'point':point,'accepted':False,'incomplete_reason':halt_reason or 'MISSING_CASE'});continue
        x=json.loads((OUT/(point['name']+'_coarse.json')).read_text());y=json.loads((OUT/(point['name']+'_fine.json')).read_text())
        if 'mu' not in x or 'mu' not in y:
            pairs.append({'point':point,'accepted':False,'incomplete_reason':'CASE_SOLVE_FAILED','errors':[z.get('error') for z in [x,y] if 'error' in z]});continue
        dm=abs(x['mu']-y['mu']);dl=abs(x['lambda']-y['lambda'])
        tests=pair_checks(x,y)
        pairs.append({'point':point,'mu':y['mu'],'lambda':y['lambda'],'k':y['background']['k'],'D':y['background']['D'],'growth_over_H':y['growth_over_H'],'overlap':y['overlap'],'mass_difference':dm,'lambda_difference':dl,'checks':tests,'accepted':all(tests.values())})
    passed=all(x['accepted'] for x in pairs)
    result={'status':'COMPLETE' if passed else 'UNRESOLVED','classification':'RESOLVED_NUMERICAL_RADION_INSTABILITY_AT_NINE_CERTIFIED_PARAMETER_POINTS' if passed else 'BOUNDED_STABILITY_QUALIFICATION_UNRESOLVED','pairs':pairs,'completed_cases':len(cp['completed']),'halt_reason':halt_reason,'guard':guard,'completed_utc':now(),'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'longdouble_nmant':np.finfo(np.longdouble).nmant,'processes':1,'threads':1},'claim_boundary':'Finite nine-point numerical mode evidence; no uniform spectral theorem, no rigorous exact-background eigenvalue enclosure, no nonlinear or global-causal inference.'}
    if (OUT/'RESULT.json').exists():
        retained=json.loads((OUT/'RESULT.json').read_text())
        if {k:v for k,v in retained.items() if k!='completed_utc'}!={k:v for k,v in result.items() if k!='completed_utc'}:
            raise RuntimeError('orphan RESULT does not match reconstructed receipts')
        result=retained
    else:write(OUT/'RESULT.json',result,True)
    write(OUT/'TERMINAL.json',{'status':result['status'],'classification':result['classification'],'result_sha256':sha(OUT/'RESULT.json'),'completed_utc':result['completed_utc'],'guard':guard},True)
    write(OUT/'STATUS.json',{'phase':'TERMINAL','completed':len(cp['completed']),'total':len(tasks),'updated_utc':now(),'informational_only':True})

if __name__=='__main__':
    try:main()
    except Exception as exc:
        if not (OUT/'TERMINAL.json').exists() and not (OUT/'FAILURE.json').exists():
            write(OUT/'FAILURE.json',{'error_type':type(exc).__name__,'error':str(exc),'updated_utc':now(),'evidence':'TECHNICAL_OR_QUALIFICATION_INCOMPLETE'},True)
        raise
