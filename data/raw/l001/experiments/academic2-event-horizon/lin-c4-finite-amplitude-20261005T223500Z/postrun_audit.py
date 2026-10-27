"""Read-only finite-amplitude evidence audit; never imports or runs an IVP kernel.

Native Arb payloads are checked with the pinned constructor. Scientific image
and norm decisions use separate exact Fraction interval arithmetic.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import re
import sys
import traceback
from fractions import Fraction as Q
from pathlib import Path

GUARD='3e790eafe0a899d900e94ed8bf4adf2e268e5bab6bf96676ffd4680dc05845b4'
MODEL={'gamma':'20','lambda_a':'6755388606266369/1125899906842624',
       'lambda_b':'-851862101055633/140737488355328','m2':'7385903388887613/18014398509481984',
       'v0':'3602879701896397/36028797018963968','v1':'6520040733916207/72057594037927936'}
A=[Q('456607025194779413/4611686018427387904'),Q('114151756532473697/1152921504606846976')]
D=[Q('32727/16384'),Q('32729/16384')]
MU=[Q('-33/25000'),Q('-131/100000')]
STEP=Q(1,8192)
TOTAL=math.ceil(D[1]/STEP)
COVER=[[str(D[0]),'4091/2048'],['4091/2048',str(D[1])]]
RAD=[Q(1,100000),Q(1,10),Q(1,10)]
PRE=[Q(-24,23),Q(1),Q(1)]
ENV={'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTHONNOUSERSITE':'1',
     'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}


class I:
    def __init__(self,lo,hi=None):
        self.lo=Q(lo);self.hi=Q(lo if hi is None else hi)
        assert self.lo<=self.hi
    @staticmethod
    def lift(x):return x if isinstance(x,I) else I(x)
    def __add__(self,x):
        x=self.lift(x);return I(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,x):return self+-self.lift(x)
    def __rsub__(self,x):return self.lift(x)+-self
    def __mul__(self,x):
        x=self.lift(x);v=[self.lo*x.lo,self.lo*x.hi,self.hi*x.lo,self.hi*x.hi]
        return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=self.lift(x);assert not x.zero()
        return self*I(1/x.hi,1/x.lo)
    def __rtruediv__(self,x):return self.lift(x)/self
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        v=I(1)
        for _ in range(n):v=v*self
        return v
    def zero(self):return self.lo<=0<=self.hi
    def exactzero(self):return self.lo==self.hi==0
    def contains(self,x):
        x=self.lift(x);return self.lo<=x.lo and x.hi<=self.hi
    def overlap(self,x):
        x=self.lift(x);return max(self.lo,x.lo)<=min(self.hi,x.hi)
    def maxabs(self):return max(abs(self.lo),abs(self.hi))
    def record(self):return {'exact':[str(self.lo),str(self.hi)],'decimal':[float(self.lo),float(self.hi)]}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def native_value(pair):return Q(pair[0])*Q(2)**pair[1]


class Audit:
    def __init__(self,root):
        self.root=Path(root).resolve();self.files={};self.native_count=0;self.checkpoints=0
        self.source_links=0;self.runtime_links=0;self.cases={};self.notes=[]
        import flint
        self.flint=flint;flint.ctx.prec=768;flint.ctx.threads=1
    def read(self,p):
        p=Path(p);p=p if p.is_absolute() else self.root/p
        raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
        if str(p) in self.files:assert self.files[str(p)]==h,('changed during audit',str(p))
        self.files[str(p)]=h
        return json.loads(raw)
    def native(self,x):
        if isinstance(x,dict):
            if '_arb_native' in x:
                assert set(x)=={'_arb_native'}
                raw=x['_arb_native'];assert len(raw)==2 and all(len(a)==2 for a in raw)
                assert all(isinstance(n,int) for a in raw for n in a) and raw[1][0]>=0
                ball=self.flint.arb(tuple(raw[0]),tuple(raw[1]));assert ball.is_finite()
                assert [[int(v) for v in ball.mid().man_exp()],[int(v) for v in ball.rad().man_exp()]]==raw
                m,r=map(native_value,raw);self.native_count+=1
                return I(m-r,m+r)
            if '_rational' in x:
                assert set(x)=={'_rational'};return Q(x['_rational'])
            return {k:self.native(v) for k,v in x.items()}
        if isinstance(x,list):return [self.native(v) for v in x]
        if isinstance(x,float):assert math.isfinite(x)
        return x
    def authenticate(self):
        b=self.read('BINDINGS.json');f=self.read('FREEZE_RECORD.json')
        assert sha(self.root/'BINDINGS.json')==GUARD==f['guard']
        assert b['model_exact']==MODEL
        c=b['config'];assert list(map(Q,c['root']))==A and list(map(Q,c['D']))==D and list(map(Q,c['mu']))==MU
        assert c['bits']==768 and c['threads']==1 and Q(c['step'])==STEP
        assert c['epsilon']=={'positive':'1/200000','negative':'-1/200000'}
        assert list(map(Q,c['radii']))==RAD and list(map(Q,c['preconditioner_diagonal']))==PRE
        assert c['epsilon_order']==8 and c['e2_degree']==14 and Q(c['e2_limit'])==Q(1,10)
        assert c['checkpoint_cells']==256 and Q(c['contraction_ceiling'])==Q(1,2) and Q(c['image_fraction'])==Q(9,10)
        assert c['source_seconds_cap']==c['zero_seconds_cap']==900 and c['case_seconds_cap']==1800
        assert c['max_case_workers']==2 and c['address_space_bytes']==4*1024**3
        for label in ('sources','reviews','inputs'):
            for name,h in b[label].items():
                p=(self.root/name).resolve();assert sha(p)==h,(label,name)
                self.files[str(p)]=h;self.source_links+=1
        rt=b['runtime'];assert rt['bits']==768 and rt['threads']==1 and rt['environment']==ENV
        assert rt['python']==platform.python_version() and rt['flint']==self.flint.__version__
        assert all(os.environ.get(k)==v for k,v in ENV.items())
        assert str(Path(sys.executable).resolve())==rt['executable']
        for path,h in {rt['executable']:rt['executable_sha256'],**rt['libraries']}.items():
            assert sha(path)==h,path;self.files[path]=h;self.runtime_links+=1
        counts={}
        for parent,count in b['parent_manifest_counts'].items():
            mf=self.read(parent+'/MANIFEST.json');entries=mf.get('entries') or [{'path':n,**v} for n,v in mf['files'].items()]
            assert len(entries)==count
            for e in entries:assert b['inputs'][parent+'/'+e['path']]==e['sha256']
            counts[parent]=count
        local=self.read('../lin-c4-local-certificate-r1-20261005T221400Z/RESULT.json')
        spectral=self.read('../lin-central-validated-mode-r1-20261005T172800Z/RESULT.json')
        assert local['independently_accepted'] and spectral['independently_accepted']
        assert local['classification']=='LOCAL_C4_D1_NATIVE_FAMILY_CERTIFIED_WITH_EXPLICIT_CONSERVATIVE_RADIUS'
        assert spectral['classification']=='NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1'
        old=self.read('../../01-horizon-core/d1-native-cauchy-20261005T201829Z/BINDINGS.json')
        assert old['model_exact']==MODEL and list(map(Q,old['a_enclosure']))==A
        assert list(map(Q,old['D_enclosure']))==D and list(map(Q,old['mu_enclosure']))==MU
        control=[n for n in b['inputs'] if not n.startswith('../') and n.endswith('/RESULT.json')]
        assert len(control)==1
        ctl=self.read(control[0]);assert ctl['pass'] and all(ctl['checks'].values())
        assert ctl['sources']==b['sources'] and ctl['runtime']==rt and ctl['physical_D1_outcomes_evaluated'] is False
        for receipt,script in [('INDEPENDENT_NONLINEAR_ENDPOINT.json','independent_nonlinear_endpoint.py'),('INDEPENDENT_CENTERED_IVP.json','independent_centered_ivp.py')]:
            r=self.read(receipt);assert r['status']=='PASS' and all(r['checks'].values())
            assert r['source_sha256']==b['reviews'][script] and r['physical_integration_performed'] is False
        self.binding=b;self.parent_counts=counts;self.control_count=len(ctl['checks'])
    def parameters(self,p,which=None):
        for k,v in MODEL.items():assert p[k].contains(Q(v)),('model parameter',k)
        assert p['D'].contains(I(*D)) and p['mu'].contains(I(*MU))
        assert p['k'].lo>0
        if which and which!='source':
            target=Q(0) if which=='zero' else Q(self.binding['config']['epsilon'][which])
            assert p['eps']==target
            assert len(p['c7'])==8 and len(p['x'])==3
    def checkpoints_for(self,which):
        folder=self.root/'output'/which;states={}
        for path in sorted((folder/'checkpoints').glob('*.json')):
            body=self.read(path);assert body['guard']==GUARD
            digest=canonical_hash(body);assert path.stem.endswith(digest)
            raw=body['state'];slot=(raw['task_index'],raw['cell_index'])
            assert path.name==f'{slot[0]:02d}-{slot[1]:06d}-{digest}.json' and slot not in states
            s=self.native(raw);assert s['which']==which
            assert 0<=s['cell_index']<=TOTAL and 1<=s['max_picard']<=32
            assert s['cell_index']==0 or s['cell_index']==TOTAL or s['cell_index']%256==0
            assert s['elapsed_seconds']>=0 and len(s['y'])==(9 if which=='source' else 17)
            self.parameters(s['p'],which)
            if s['cell_index']:
                assert s['y'][8].contains(s['cell_index']*STEP)
                assert s['y'][4].lo>0
            if s['cell_index']==TOTAL or s['cell_index']==0 and s['task_index']:
                assert s['cover']==COVER
            else:assert s['cover']==[]
            if which!='source':
                assert s['common_sha256']==sha(self.root/'output/source/RESULT.json')
                assert s['preparation']['eps']==s['p']['eps']
                for item in s['preparation']['c7_epsilon_evidence']:
                    assert item['base'][0].exactzero() and item['base'][1].exactzero()
                for item in s['preparation']['W_epsilon_evidence']:
                    assert item['base_coefficients'][0].exactzero() and item['base_coefficients'][1].exactzero()
            states[slot]=(raw,s);self.checkpoints+=1
        if (folder/'LATEST.json').exists():
            ptr=self.read(folder/'LATEST.json');assert ptr['guard']==GUARD
            path=(folder/ptr['path']).resolve();assert path.parent==(folder/'checkpoints').resolve()
            body=self.read(path);assert canonical_hash(body)==ptr['digest'] and path.stem.endswith(ptr['digest'])
            assert (body['state']['task_index'],body['state']['cell_index'])==max(states)
        # Every committed spatial phase is a contiguous checkpoint prefix.
        for phase in sorted({slot[0] for slot in states}):
            cells=sorted(k for j,k in states if j==phase and k)
            if cells:
                end=cells[-1];expected=list(range(256,min(end,TOTAL-1)+1,256))
                if end==TOTAL:expected.append(TOTAL)
                assert cells==expected,(which,phase,'missing checkpoint')
        return states
    def terminal(self,which):
        folder=self.root/'output'/which
        if (folder/'RESULT.json').exists():
            raw=self.read(folder/'RESULT.json');t=self.read(folder/'TERMINAL.json')
            assert t['guard']==GUARD and t['status']=='COMPLETE' and t['result_sha256']==sha(folder/'RESULT.json')
            assert raw['guard']==GUARD and raw['status']=='COMPLETE' and raw['which']==which
            return raw,self.native(raw)
        if (folder/'FAILURE.json').exists():
            r=self.read(folder/'FAILURE.json');assert r['guard']==GUARD
            assert not (folder/'TERMINAL.json').exists()
            return r,None
        return None,None
    def source(self):
        states=self.checkpoints_for('source');raw,r=self.terminal('source')
        if r is None:return {'status':'FAILED_OR_NOT_COMPLETE','failure':raw}
        assert r['cells']==TOTAL and r['event_cover']==COVER and r['max_picard']<=32
        s=states[(0,TOTAL)][1];self.parameters(r['p']);p=r['p'];y0=r['y0'];end=s['end']
        assert y0[0].exactzero() and y0[4].contains(1) and y0[5].contains(1) and y0[8].exactzero()
        assert y0[2].contains(I(*A))
        aa=I(*A);H=-(p['lambda_a']+p['gamma']*(aa-p['v0'])**2/2)/6;T=p['gamma']*(aa-p['v0'])/2
        assert y0[1].overlap(H) and y0[3].overlap(T)
        kval=H*H-1-T*T/12+p['m2']*aa*aa/12;assert p['k'].overlap(kval)
        B=p['gamma']*T/2-p['m2']*aa+4*H*T;assert not B.zero()
        ff=3*(p['mu']+4*p['k'])/B
        assert y0[6].overlap(ff) and y0[7].overlap(p['gamma']*ff/2-2*T)
        wall=[]
        for side,j in enumerate(r['jets']):
            sigma=1 if side==0 else -1;c=sigma*p['gamma']/2;v=p['v0' if side==0 else 'v1'];lam=p['lambda_a' if side==0 else 'lambda_b']
            assert j['sigma']==sigma and j['vi'].overlap(v) and j['lam'].overlap(lam)
            for name in ('Phi','psi','f'):assert len(j[name])==6
            P=j['Phi'][0];H=j['H'];T=j['T'];psi=j['psi'][0];f=j['f'][0];g=j['f'][1]
            carrier=y0 if side==0 else end
            for vv,idx in [(H,1),(P,2),(T,3),(psi,5),(f,6),(g,7)]:assert vv.overlap(carrier[idx])
            checks={
              'Israel':(H+sigma*(lam+p['gamma']*(P-v)**2/2)/6).zero(),
              'scalar_Robin':(T-c*(P-v)).zero(),
              'mode_Robin':(g+2*T*psi-c*f).zero(),
              'background_constraint':(H*H-1-T*T/12+p['m2']*P*P/12-j['qbg']).zero(),
              'regular_mode_constraint':(T*g-j['Phi'][2]*f+(2*T*T-3*(p['mu']*j['qbg']/p['k']+4*j['qbg']))*psi).zero(),
              'Phi_first':(j['Phi'][1]-T).zero(),
              'Phi_second':(j['Phi'][2]-p['m2']*P+4*H*T).zero(),
              'psi_first':(j['psi'][1]+2*H*psi+T*f/3).zero(),
              'q_carrier':j['qbg'].overlap(p['k']*carrier[4]*carrier[4]),
            }
            assert all(checks.values()),(side,checks)
            wall.append({'side':side,'checks':checks,'qbg':j['qbg'].record(),'psi':psi.record()})
        self.common=r
        return {'status':'COMPLETE','cells':TOTAL,'event_cover':COVER,'max_picard':r['max_picard'],
                'elapsed_seconds':r['elapsed_seconds'],'wall_consistency':wall}
    def phases(self,which,states):
        folder=self.root/'output'/which;out={}
        for idx,name in enumerate(['center'] if which=='zero' else ['center','box']):
            if not (folder/(name+'.json')).exists():continue
            raw=self.read(folder/(name+'.json'));assert raw['guard']==GUARD and raw['phase']==name
            assert raw['cells']==TOTAL and raw['event_cover']==COVER
            assert raw['map']==states[(idx,TOTAL)][0]['map'],(which,name,'published map/checkpoint mismatch')
            z=self.native(raw);assert len(z['map']['G'])==3 and len(z['map']['J'])==9
            assert len(z['map']['wall_diagnostics'])==10 and 1<=z['max_picard']<=32
            assert all(z['map']['wall_diagnostics'][n].lo>0 for n in (0,3,5,8))
            if which!='zero':
                case=3 if which=='positive' else 4
                old=self.read('../../01-horizon-core/d1-native-cauchy-20261005T201829Z/results/fine_c4/case_'+str(case)+'.dense.json')
                eps=Q(self.binding['config']['epsilon'][which]);center=[Q(old['A0'])-eps]+list(map(Q,old['fifth_jet_coefficients']))
                # The old epsilon string is rounded example metadata, not an
                # exact amplitude input. Only A0/fifth strings set centers;
                # production subtracts the prospectively exact target.
                z['old_epsilon_metadata_offset']=str(Q(old['epsilon'])-eps)
                pp=states[(idx,TOTAL)][1]['p']
                for v,c,r in zip(pp['x'],center,RAD):assert v.contains(I(c-r,c+r) if name=='box' else c)
            out[name]=z
        return out
    def prep_summary(self,p):
        assert p['eps']==0 or p['eps'] in (Q(1,200000),Q(-1,200000))
        rem=[]
        for z in p['W_epsilon_evidence']:
            assert z['base_coefficients'][0].exactzero() and z['base_coefficients'][1].exactzero()
            assert all(v.zero() for v in z['analytically_zero_unreduced_interval_coefficients'])
            rem.append(float(z['remainder_coefficient'].maxabs()*abs(p['eps'])**8))
        return {'W':[v.record() for v in p['W']],
                'maximum_abs_c7_coefficient':float(max(v.maxabs() for v in p['c7'])),
                'eighth_order_W_remainder_abs_upper':rem}
    def case(self,which):
        states=self.checkpoints_for(which);phases=self.phases(which,states)
        raw,r=self.terminal(which)
        if r is None:
            return {'status':'TECHNICAL_OR_ENCLOSURE_FAILURE' if raw else 'NOT_RUN_OR_RUNNING',
                    'certificate':False,'failure':raw,'completed_phases':list(phases)}
        if which=='zero':
            assert list(phases)==['center']
            m=r['map'];assert raw['map']==self.read('output/zero/center.json')['map']
            checks={'zero_map_contains_zero':all(v.zero() for v in m['G']),
                    'zero_map_small':all(v.maxabs()<=Q(1,2**500) for v in m['G']),
                    'reduced_fifth_rows_identity':all((m['J'][3+3*i+j]-int(j==i+1)).zero() for i in range(2) for j in range(3))}
            assert checks==r['checks'] and all(checks.values())==r['pass']
            return {'status':'COMPLETE','pass':all(checks.values()),'checks':checks,
                    'G':[v.record() for v in m['G']],'elapsed_seconds':r['elapsed_seconds']}
        assert list(phases)==['center','box']
        eps=Q(self.binding['config']['epsilon'][which]);assert Q(r['epsilon'])==eps
        case=3 if which=='positive' else 4
        old=self.read('../../01-horizon-core/d1-native-cauchy-20261005T201829Z/results/fine_c4/case_'+str(case)+'.dense.json')
        exact_center=[Q(old['A0'])-eps]+list(map(Q,old['fifth_jet_coefficients']))
        assert list(map(Q,r['center']))==exact_center
        assert list(map(Q,r['radii']))==RAD and list(map(Q,r['C']))==PRE
        assert r['event_covers']==[COVER,COVER] and r['common_sha256']==sha(self.root/'output/source/RESULT.json')
        assert raw['G_center']==self.read('output/'+which+'/center.json')['map']['G']
        flat=self.read('output/'+which+'/box.json')['map']['J'];assert sum(raw['J_box'],[])==flat
        J=r['J_box'];G=r['G_center'];M=[[int(i==j)-PRE[i]*J[i][j] for j in range(3)] for i in range(3)]
        rownorm=[sum(M[i][j].maxabs()*RAD[j] for j in range(3))/RAD[i] for i in range(3)]
        image=[-PRE[i]*G[i]+sum((M[i][j]*I(-RAD[j],RAD[j]) for j in range(3)),I(0)) for i in range(3)]
        ratios=[v.maxabs()/rr for v,rr in zip(image,RAD)]
        include=[v<Q(9,10) for v in ratios];contract=max(rownorm)<=Q(1,2);passed=all(include) and contract
        assert r['component_inclusions']==include and r['contraction_pass']==contract and r['pass']==passed
        assert r['classification']==('FINITE_AMPLITUDE_INITIAL_DATA_CERTIFIED' if passed else 'UNRESOLVED_INTERVAL_CERTIFICATE')
        for i in range(3):
            assert image[i].overlap(r['image_offset'][i])
            for j in range(3):assert M[i][j].overlap(r['I_minus_CJ'][i][j])
        return {'status':'COMPLETE','certificate':passed,'epsilon':str(eps),'center':r['center'],
                'old_epsilon_metadata_offset':str(Q(old['epsilon'])-eps),
                'radii':r['radii'],'G_center':[v.record() for v in G],
                'J_box':[[v.record() for v in row] for row in J],
                'independent_image_radius_ratios_exact':list(map(str,ratios)),
                'independent_image_radius_ratios_decimal':list(map(float,ratios)),
                'independent_weighted_row_norms_exact':list(map(str,rownorm)),
                'independent_weighted_row_norms_decimal':list(map(float,rownorm)),
                'component_inclusions':include,'contraction_pass':contract,
                'elapsed_seconds':r['elapsed_seconds'],
                'phase_cells':{n:z['cells'] for n,z in phases.items()},
                'phase_max_picard':{n:z['max_picard'] for n,z in phases.items()},
                'preparation':self.prep_summary(r['preparation'])}
    def run(self):
        self.authenticate();out=self.root/'output'
        assert (out/'RESULT.json').exists() or (out/'FAILURE.json').exists(),'Graph not terminal; audit must wait'
        source=self.source();zero=None
        if (out/'zero').exists():zero=self.case('zero')
        cases={name:self.case(name) for name in ('positive','negative') if (out/name).exists()}
        if (out/'RESULT.json').exists():
            result=self.read('output/RESULT.json');terminal=self.read('output/TERMINAL.json')
            assert terminal['guard']==GUARD and terminal['result_sha256']==sha(out/'RESULT.json')
            assert result['guard']==GUARD and result['status']=='COMPLETE'
            assert source['status']=='COMPLETE' and zero['pass'] and set(cases)=={'positive','negative'}
            passed=sorted(k for k,v in cases.items() if v['certificate'])
            classification=('BOTH_SIGNED_FINITE_AMPLITUDE_C4_SAMPLES_CERTIFIED' if len(passed)==2 else
                            'ONE_SIGNED_SAMPLE_CERTIFIED_OTHER_UNRESOLVED' if len(passed)==1 else
                            'NO_FINITE_AMPLITUDE_CERTIFICATE_OBTAINED')
            assert sorted(result['passed_cases'])==passed and result['classification']==classification
            for name,a in result['case_artifacts'].items():
                assert sha(out/a['path'])==a['sha256']
                assert bool(result['return_codes'][name]==0)==(cases[name]['status']=='COMPLETE')
            assert result['not_nonexistence'] and not result['next_experiment_authorized']
        else:
            result=self.read('output/FAILURE.json');assert result['guard']==GUARD
            assert result['failed_phase'] in ('source','zero') and not cases
            assert result['scope']=='BOUNDED_GRAPH_STOPPED_NO_SUCCESSOR'
            classification='SOURCE_OR_ZERO_CONTROL_FAILED_NO_NONZERO_CERTIFICATE'
            passed=[]
        for path,h in list(self.files.items()):assert sha(path)==h,('changed during audit',path)
        return {'overall':'PASS','scientific_classification':classification,
                'both_signed_certificates_accepted':len(passed)==2,'accepted_cases':passed,
                'guard':GUARD,'inputs_unchanged':True,'source':source,'zero':zero,'cases':cases,
                'checkpoint_count':self.checkpoints,'native_ball_count':self.native_count,
                'source_review_input_hash_links':self.source_links,'runtime_hash_links':self.runtime_links,
                'unchanged_file_count':len(self.files),'parent_manifest_counts':self.parent_counts,
                'preflight_control_count':self.control_count,'physical_IVP_replayed':False,
                'independent_decision_arithmetic':'Exact rational intervals from native midpoint/radius tuples',
                'limits':['No physical IVP replay; method is independently reviewed and frozen state/evidence authenticated.',
                          'Interval wall consistency is checked, not asserted as equality for every rectangle point.',
                          'Only two signed amplitudes; no connected amplitude interval, evolution or successor.'],
                'checked_files_sha256_index_digest':canonical_hash(self.files),
                'binding_sha256':GUARD,
                'graph_terminal_evidence_sha256':sha(out/('RESULT.json' if (out/'RESULT.json').exists() else 'FAILURE.json')),
                'checkpoint_inventory_sha256':canonical_hash({p:h for p,h in self.files.items() if '/output/' in p and '/checkpoints/' in p})}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--packet',required=True)
    args=parser.parse_args()
    try:r=Audit(args.packet).run()
    except Exception as exc:
        r={'overall':'FAIL','exception':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),
           'physical_IVP_replayed':False}
    r['audit_source_sha256']=sha(__file__)
    print(json.dumps(r,indent=2,sort_keys=True,allow_nan=False))
    if r['overall']!='PASS':raise SystemExit(1)
