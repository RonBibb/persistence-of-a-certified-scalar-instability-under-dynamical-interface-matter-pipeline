"""Read-only R1 identity/admission audit; no IVP or producer-kernel execution.

Fraction/native readers follow this reviewer's sealed preceding auditors.
New decisions, root-image translation, coverage and saved polynomial replay are
written here. Arb is used only for native roundtrips and polynomial arithmetic.
Run only after both spatial production and numerical readback are terminal and
the coordinator releases the single serialized Linux verification slot.
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
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path

GUARD='1d038b90a66fa82ca09d5cd419c5352c37b539b94c2bbaeb82f246219fff9ab8'
OLD_GUARD='84d1e800ebb5deedae8e175dcf6b162a08938977f77752080f75f33be240f3ab'
OLD_NAME='lin-c4-evolution-identity-20261006T044000Z'
BRANCH=Path('/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches')
NAMES={
 'connected':'02-event-horizon/lin-c4-connected-branch-20261006T004500Z',
 'finite':'02-event-horizon/lin-c4-finite-amplitude-20261005T223500Z',
 'central':'02-event-horizon/lin-central-validated-mode-r1-20261005T172800Z',
 'neighborhood':'02-event-horizon/lin-neighborhood-validated-mode-20261005T182300Z',
 'native':'01-horizon-core/d1-native-cauchy-20261005T201829Z',
 'admission':'01-horizon-core/d1-evolution-admission-20261005T214600Z',
 'short':'01-horizon-core/d1-short-evolution-20261005T224000Z',
 'spatial':'01-horizon-core/d1-spatial-evolution-20261005T232000Z',
 'second':'01-horizon-core/d1-second-order-scalar-20261006T003543Z'}
MODEL={'gamma':'20','lambda_a':'6755388606266369/1125899906842624',
 'lambda_b':'-851862101055633/140737488355328','m2':'7385903388887613/18014398509481984',
 'v0':'3602879701896397/36028797018963968','v1':'6520040733916207/72057594037927936'}
A=list(map(Q,['456607025194779413/4611686018427387904','114151756532473697/1152921504606846976']))
D=list(map(Q,['32727/16384','32729/16384']))
MU=list(map(Q,['-33/25000','-131/100000']))
E=Q(1,200000);STEP=Q(1,8192);TOTAL=16365
RAD=[Q(1,100000),Q(1,10),Q(1,10)];C=[Q(-24,23),Q(1),Q(1)]
COVER=[[D[0],Q(4091,2048)],[Q(4091,2048),D[1]]]
ENV={'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTHONNOUSERSITE':'1',
 'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
CONFIG={'address_space_bytes':4294967296,'bits':768,'cases':[0,3,4],
 'checkpoint_cells':256,'cpu_seconds_per_flow':1800,'degrees':[160,192],
 'epsilon':['-1/200000','1/200000'],'flow_order':['mode','positive','negative'],
 'maximum_cells_per_flow':16365,'readback_seconds':3600,'replay_dps':[80,100],
 'representation_gate':'1e-50','step':'1/8192','threads':1}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dyadic(pair):return Q(pair[0])*Q(2)**pair[1]


class I:
    def __init__(self,lo,hi=None):
        self.lo=Q(lo);self.hi=Q(lo if hi is None else hi);assert self.lo<=self.hi
    @staticmethod
    def lift(x):return x if isinstance(x,I) else I(x)
    def __add__(self,x):
        x=self.lift(x);return I(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,x):return self+-self.lift(x)
    def __rsub__(self,x):return self.lift(x)+-self
    def __mul__(self,x):
        x=self.lift(x);v=[self.lo*x.lo,self.lo*x.hi,self.hi*x.lo,self.hi*x.hi];return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=self.lift(x);assert not x.zero();return self*I(1/x.hi,1/x.lo)
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


class Review:
    def __init__(self,root):
        import flint
        self.flint=flint;flint.ctx.prec=768;flint.ctx.threads=1
        self.root=Path(root).resolve();self.files={};self.native_count=0;self.checkpoints=0
        self.hash_links=0;self.runtime_links=0;self.flow_results={}
    def read(self,p):
        p=Path(p);p=(p if p.is_absolute() else self.root/p).resolve()
        raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
        if str(p) in self.files:assert self.files[str(p)]==h,('changed during audit',str(p))
        self.files[str(p)]=h;return json.loads(raw)
    def linked(self,p,h):
        p=Path(p).resolve();assert sha(p)==h,('hash mismatch',str(p))
        self.files[str(p)]=h;self.hash_links+=1
    def native(self,x):
        if isinstance(x,dict):
            if '_arb_native' in x:
                assert set(x)=={'_arb_native'};raw=x['_arb_native']
                assert len(raw)==2 and all(len(pair)==2 for pair in raw)
                assert all(type(n) is int for pair in raw for n in pair) and raw[1][0]>=0
                z=self.flint.arb(tuple(raw[0]),tuple(raw[1]));assert z.is_finite()
                assert [[int(a) for a in z.mid().man_exp()],[int(a) for a in z.rad().man_exp()]]==raw
                m,r=map(dyadic,raw);self.native_count+=1;return I(m-r,m+r)
            if '_rational' in x:assert set(x)=={'_rational'};return Q(x['_rational'])
            return {k:self.native(v) for k,v in x.items()}
        if isinstance(x,list):return [self.native(v) for v in x]
        if isinstance(x,float):assert math.isfinite(x)
        return x
    def parent(self,name,relative):return BRANCH/NAMES[name]/relative
    def manifest(self,p):
        m=self.read(p)
        if isinstance(m.get('entries'),list):return m['entries']
        assert isinstance(m.get('files'),dict)
        return [row|{'path':name} for name,row in m['files'].items()]
    def authenticate(self):
        b=self.read('BINDINGS.json');f=self.read('FREEZE_RECORD.json')
        assert sha(self.root/'BINDINGS.json')==GUARD==f['guard']
        assert b['config']==CONFIG and b['model_exact']==MODEL and not b['physical_outcomes_before_freeze']
        assert len(b['sources'])==16 and len(b['inputs'])==2835
        for name,h in b['sources'].items():self.linked(self.root/name,h)
        for name,h in b['inputs'].items():self.linked(name,h)
        self.linked(self.root/'PREFLIGHT_REVIEW.md',b['review_sha256'])
        assert b['review_sha256']=='0b239d0249cf6a678a7cc81959d6c6f48e73bacf272f7c8bf99d6b3a208af794'
        self.linked(b['preflight']['path'],b['preflight']['sha256'])
        ctl=self.read(b['preflight']['path'])
        assert ctl['sources']==b['sources'] and ctl['runtime']==b['runtime'] and ctl['config']==CONFIG
        assert ctl['passed'] and not ctl['physical_outcomes']
        flags=[k for k,v in ctl.items() if k not in ('passed','physical_outcomes') and isinstance(v,bool)]
        assert len(flags)==10 and all(ctl[k] for k in flags)
        rt=b['runtime'];assert rt['bits']==768 and rt['threads']==1 and rt['environment']==ENV
        assert rt['python']==platform.python_version() and rt['flint']==self.flint.__version__
        import mpmath
        assert rt['mpmath']==mpmath.__version__ and all(os.environ.get(k)==v for k,v in ENV.items())
        assert str(Path(sys.executable).resolve()) in rt['libraries']
        for path,h in rt['libraries'].items():self.linked(path,h);self.runtime_links+=1
        for name,relative in NAMES.items():
            parent=BRANCH/relative;rows=self.manifest(parent/'MANIFEST.json')
            assert len(rows)==b['parent_counts'][name]
            assert b['inputs'][str(parent/'MANIFEST.json')]==sha(parent/'MANIFEST.json')
            for row in rows:assert b['inputs'][str(parent/row['path'])]==row['sha256']
        old=self.root.parent/OLD_NAME;ob=self.read(old/'BINDINGS.json')
        assert sha(old/'BINDINGS.json')==OLD_GUARD and self.read(old/'FREEZE_RECORD.json')['guard']==OLD_GUARD
        for name,h in ob['sources'].items():self.linked(old/name,h)
        self.linked(old/'PREFLIGHT_REVIEW.md',ob['review_sha256'])
        failure=self.read(old/'RUN_FAILURE.json')
        assert failure['guard']==OLD_GUARD and failure['status']=='TECHNICAL_INCOMPLETE_BEFORE_FIRST_CELL'
        assert failure['accepted_physical_cells']==0 and not failure['terminal_physical_result']
        assert not failure['original_frozen_source_modified'] and not failure['automatic_restart_allowed']
        assert not list((old/'output').glob('*/checkpoints/*.json'))
        assert [n for n in b['sources'] if b['sources'][n]!=ob['sources'][n]]==['identity_run.py']
        assert b['runtime']==ob['runtime'] and b['config']==ob['config'] and b['inputs']==ob['inputs']
        receipt=self.read('INDEPENDENT_GAUGE_BRIDGE.json')
        assert receipt['status']=='PASS' and len(receipt['checks'])==15 and all(receipt['checks'].values())
        assert not receipt['physical_integration_performed']
        assert receipt['source_sha256']==b['sources']['independent_gauge_bridge.py']
        cb=self.read(self.parent('connected','BINDINGS.json'))
        assert cb['model_exact']==MODEL and list(map(Q,cb['config']['root']))==A
        assert list(map(Q,cb['config']['D']))==D and list(map(Q,cb['config']['mu']))==MU
        for n in ('native','second'):
            assert self.read(self.parent(n,'BINDINGS.json'))['model_exact']==MODEL
        cr=self.read(self.parent('connected','RESULT.json'));ca=self.read(self.parent('connected','INDEPENDENT_AUDIT.json'))
        assert cr['independently_accepted'] and cr['connected_interval_certified']
        assert ca['overall']=='PASS' and ca['connected_interval_certified'] and ca['zero_local_reconciliation']['pass']
        assert ca['coverage']['full'] and ca['coverage']['components']==[['-1/200000','1/200000']]
        assert cr['artifacts']['INDEPENDENT_AUDIT.json']==sha(self.parent('connected','INDEPENDENT_AUDIT.json'))
        sr=self.read(self.parent('central','RESULT.json'));sa=self.read(self.parent('central','INDEPENDENT_AUDIT.json'))
        assert sr['independently_accepted'] and sa['audit_pass'] and sa['endpoint_certificate']
        assert sr['classification']=='NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1'
        assert sr['artifacts']['INDEPENDENT_AUDIT.json']==sha(self.parent('central','INDEPENDENT_AUDIT.json'))
        endpoint=self.read(self.parent('central','output/RESULT.json'));sgn={}
        for task in endpoint['tasks']:
            if task['task'].endswith(('_low','_high')):
                z=task['determinant'];ival=I(z['lo_exact'],z['hi_exact'])
                assert ival.lo>0 if task['task'].endswith('_low') else ival.hi<0
                sgn[task['task']]=ival.record()
        assert len(sgn)==4 and endpoint['endpoint_certificate']
        self.binding=b;self.connected=ca;self.inherited_endpoint_signs=sgn
        self.control_flags=flags;self.old_failure_sha256=sha(old/'RUN_FAILURE.json')
    def parameters(self,p):
        for k,v in MODEL.items():assert p[k].contains(Q(v)),('model parameter',k)
        assert p['D'].contains(I(*D)) and p['mu'].contains(I(*MU)) and p['k'].lo>0
    def source(self):
        path=self.parent('finite','output/source/RESULT.json');rraw=self.read(path);r=self.native(rraw)
        term=self.read(path.parent/'TERMINAL.json')
        assert term['guard']==r['guard'] and term['result_sha256']==sha(path) and term['status']=='COMPLETE'
        assert r['status']=='COMPLETE' and r['cells']==TOTAL and r['event_cover']==[[str(a),str(b)] for a,b in COVER]
        p=r['p'];y=r['y0'];self.parameters(p)
        assert len(y)==9 and y[0].exactzero() and y[4].contains(1) and y[5].contains(1) and y[8].exactzero()
        assert y[2].contains(I(*A));aa=I(*A)
        H=-(p['lambda_a']+p['gamma']*(aa-p['v0'])**2/2)/6;T=p['gamma']*(aa-p['v0'])/2
        assert y[1].overlap(H) and y[3].overlap(T)
        kval=H*H-1-T*T/12+p['m2']*aa*aa/12;assert p['k'].overlap(kval)
        B=p['gamma']*T/2-p['m2']*aa+4*H*T;assert not B.zero()
        ff=3*(p['mu']+4*p['k'])/B
        assert y[6].overlap(ff) and y[7].overlap(p['gamma']*ff/2-2*T)
        wall=[]
        for side,j in enumerate(r['jets']):
            sigma=1 if side==0 else -1;c=sigma*p['gamma']/2
            v=p['v0' if side==0 else 'v1'];lam=p['lambda_a' if side==0 else 'lambda_b']
            assert j['sigma']==sigma and j['vi'].overlap(v) and j['lam'].overlap(lam)
            assert all(len(j[n])==6 for n in ('Phi','psi','f'))
            H,P,T,psi,f,g=j['H'],j['Phi'][0],j['T'],j['psi'][0],j['f'][0],j['f'][1]
            tests={
             'Israel':(H+sigma*(lam+p['gamma']*(P-v)**2/2)/6).zero(),
             'scalar_Robin':(T-c*(P-v)).zero(),
             'mode_Robin':(g+2*T*psi-c*f).zero(),
             'background_constraint':(H*H-1-T*T/12+p['m2']*P*P/12-j['qbg']).zero(),
             'regular_mode_constraint':(T*g-j['Phi'][2]*f+(2*T*T-3*(p['mu']*j['qbg']/p['k']+4*j['qbg']))*psi).zero(),
             'Phi_first':(j['Phi'][1]-T).zero(),
             'Phi_second':(j['Phi'][2]-p['m2']*P+4*H*T).zero(),
             'psi_first':(j['psi'][1]+2*H*psi+T*f/3).zero()}
            assert all(tests.values()),(side,tests);wall.append({'side':side,'checks':tests})
        self.common_raw=rraw;self.common=r
        return {'source_result_sha256':sha(path),'wall_consistency':wall,'background_A':list(map(str,A)),
                'D':list(map(str,D)),'mu':list(map(str,MU)),'physical_normalization':'psi(0)=1',
                'launch_B_interval':B.record(),'source_reintegrated':False}
    def gates(self,G,J):
        M=[[int(i==j)-C[i]*J[i][j] for j in range(3)] for i in range(3)]
        norms=[sum(M[i][j].maxabs()*RAD[j] for j in range(3))/RAD[i] for i in range(3)]
        image=[-C[i]*G[i]+sum((M[i][j]*I(-RAD[j],RAD[j]) for j in range(3)),I(0)) for i in range(3)]
        ratios=[v.maxabs()/r for v,r in zip(image,RAD)]
        return image,ratios,norms,all(x<Q(9,10) for x in ratios) and max(norms)<=Q(1,2)
    def roots(self):
        out={};self.root_intervals={};self.old_preparation={}
        for name,case,eps in [('positive',3,E),('negative',4,-E)]:
            path=self.parent('finite',f'output/{name}/RESULT.json');raw=self.read(path);r=self.native(raw)
            term=self.read(path.parent/'TERMINAL.json');assert term['result_sha256']==sha(path) and term['guard']==r['guard']
            assert r['status']=='COMPLETE' and r['pass'] and Q(r['epsilon'])==eps
            assert list(map(Q,r['radii']))==RAD and list(map(Q,r['C']))==C
            assert r['common_sha256']==sha(self.parent('finite','output/source/RESULT.json'))
            image,ratios,norms,passed=self.gates(r['G_center'],r['J_box']);assert passed
            centers=list(map(Q,r['center']));translated=[v+c for v,c in zip(image,centers)]
            assert all(-rr<v.lo<=v.hi<rr for v,rr in zip(translated,RAD))
            prior=self.connected['endpoint_identity'][name]
            assert prior['pass'] and prior['old_gates_recomputed_pass'] and prior['old_result_sha256']==sha(path)
            assert [v.record()['exact'] for v in translated]==[v['exact'] for v in prior['translated_root_image']]
            dense=self.read(self.parent('native',f'results/fine_c4/case_{case}.dense.json'))
            assert centers==[Q(dense['A0'])-eps]+list(map(Q,dense['fifth_jet_coefficients']))
            saved_eps=Q(dense['epsilon']);assert -E<=saved_eps<=E
            assert r['preparation']['eps']==eps
            for entry in r['preparation']['c7_epsilon_evidence']:
                assert entry['base'][0].exactzero() and entry['base'][1].exactzero()
            for entry in r['preparation']['W_epsilon_evidence']:
                assert entry['base_coefficients'][0].exactzero() and entry['base_coefficients'][1].exactzero()
            self.root_intervals[name]=translated;self.old_preparation[name]=raw['preparation']
            out[name]={'pass':True,'case':case,'epsilon_exact':str(eps),'saved_epsilon_rounding_offset':str(saved_eps-eps),
                'center_exact':list(map(str,centers)),'translated_root_image':[v.record() for v in translated],
                'image_ratios_exact':list(map(str,ratios)),'image_ratios_decimal':list(map(float,ratios)),
                'weighted_norms_exact':list(map(str,norms)),'weighted_norms_decimal':list(map(float,norms)),
                'old_result_sha256':sha(path),'same_connected_branch_by_common_box_uniqueness':True,
                'literal_numerical_point_asserted_exact':False}
        self.root_findings=out;return out
    def coverage(self):
        seed=self.read(self.parent('native','results/fine_c4/SEED.json'))
        nativeD=Q(seed['D']);nativeh=Q(seed['h']);n=len(seed['segments'])
        assert n==256 and all(len(block)==8 for block in seed['segments'])
        assert (n-1)*nativeh<nativeD<(n+1)*nativeh
        assert A[0]<=Q(seed['a'])<=A[1] and MU[0]<=Q(seed['mu'])<=MU[1] and D[0]<=nativeD<=D[1]
        at=Q(0);maxparts=0;parts=0;last=None
        for i in range(TOTAL):
            t=i*STEP;h=min(STEP,D[1]-t);assert h>0
            lo=max(Q(0),t*nativeD/D[1]);hi=min(nativeD,(t+h)*nativeD/D[0])
            assert lo<=hi and lo<=at
            aa=lo/nativeh;bb=hi/nativeh
            first=max(0,min(n-1,aa.numerator//aa.denominator));final=max(0,min(n-1,bb.numerator//bb.denominator))
            cursor=lo;count=0
            for j in range(first,final+1):
                left=max(lo,j*nativeh);right=hi if j==n-1 else min(hi,(j+1)*nativeh)
                if left>right:continue
                assert left<=cursor;cursor=max(cursor,right);count+=1
            assert cursor==hi and count>0
            maxparts=max(maxparts,count);parts+=count;at=max(at,hi);last=[lo,hi]
        assert at==nativeD and (TOTAL-1)*STEP<D[1]<=TOTAL*STEP
        self.seed_raw=seed
        return {'complete':True,'source_cells':TOTAL,'source_closed_domain':['0',str(D[1])],
            'normalized_u_cover':['0','1'],'native_closed_domain':['0',str(nativeD)],
            'native_segments':n,'segment_intersections_count':parts,'max_segments_per_source_cell':maxparts,
            'last_cell_step':str(D[1]-(TOTAL-1)*STEP),'native_D_minus_256h_exact':str(nativeD-n*nativeh),
            'event_cover_expected':[[str(a),str(b)] for a,b in COVER],
            'basis':'Exact rational indexing and coverage; validated cell enclosures are authenticated producer evidence, not reintegrated.'}
    def flow(self,name,index):
        folder=self.root/'output'/name;states={};previous=None;firstp=None;count=0
        for path in sorted((folder/'checkpoints').glob('*.json')):
            body=self.read(path);assert body['guard']==GUARD;h=digest(body);raw=body['state']
            cell=raw['cell_index'];assert path.name==f'{index:02d}-{cell:06d}-{h}.json' and cell not in states
            assert raw['task_index']==index and raw['name']==name
            assert 0<cell<=TOTAL and (cell%256==0 or cell==TOTAL)
            s=self.native(raw);p=s['p'];self.parameters(p)
            assert len(s['y'])==(12 if name=='mode' else 11) and s['y'][4].lo>0
            assert s['y'][8].contains(min(cell*STEP,D[1]))
            assert 1<=s['max_picard']<=32 and 0<=s['integration_cpu_seconds']<=1800 and s['elapsed_seconds']>=0
            assert len(s['max_errors'])==(8 if name=='mode' else 3) and len(s['domain_maxima'])==len(s['y'])
            assert all(v>=0 for v in s['max_errors']+s['domain_maxima'])
            for k,v in self.common_raw['p'].items():assert raw['p'][k]==v,('inherited parameter bytes',name,k)
            if firstp is None:firstp=raw['p']
            else:assert firstp==raw['p'],'Checkpoint parameters drifted'
            if name!='mode':
                assert p['eps']==(E if name=='positive' else -E)
                for k,v in self.old_preparation[name].items():assert raw['p'][k]==v,('signed preparation',name,k)
                assert len(p['x'])==3 and all(a.contains(b) for a,b in zip(p['x'],self.root_intervals[name]))
                assert s['event_cover']==[] and s['event_derivative'] is None
            elif cell<TOTAL:
                assert s['event_cover']==[] and s['event_derivative'] is None
            if previous is not None:
                assert all(a<=b for a,b in zip(previous['max_errors'],s['max_errors']))
                assert all(a<=b for a,b in zip(previous['domain_maxima'],s['domain_maxima']))
                assert previous['integration_cpu_seconds']<=s['integration_cpu_seconds'] and previous['elapsed_seconds']<=s['elapsed_seconds']
            states[cell]=(raw,s);previous=s;count+=1;self.checkpoints+=1
        if states:
            last=max(states);expected=list(range(256,min(last,TOTAL-1)+1,256))
            if last==TOTAL:expected.append(TOTAL)
            assert sorted(states)==expected
            ptr=self.read(folder/'LATEST.json');assert ptr['guard']==GUARD
            path=(folder/ptr['path']).resolve();assert path.parent==(folder/'checkpoints').resolve()
            body=self.read(path);assert digest(body)==ptr['digest'] and body['state']['cell_index']==last
            status=self.read(folder/'STATUS.json');assert status['guard']==GUARD and status['checkpoint_digest']==ptr['digest']
            assert status['cell_index']==last and status['task_index']==index
        if not (folder/'RESULT.json').exists():
            assert (folder/'FAILURE.json').exists() or (self.root/'RUN_FAILURE.json').exists(),'Nonterminal flow'
            failure=self.read(folder/'FAILURE.json') if (folder/'FAILURE.json').exists() else None
            if failure:assert failure['guard']==GUARD
            return {'status':'TECHNICAL_INCOMPLETE','checkpoints':count,'last_cell':max(states,default=0),'failure':failure}
        raw=self.read(folder/'RESULT.json');r=self.native(raw);term=self.read(folder/'TERMINAL_CHECKPOINT.json')
        assert term['guard']==GUARD and term['result_sha256']==sha(folder/'RESULT.json')
        assert r['guard']==GUARD and r['task']==name and r['cells']==TOTAL and count==64
        assert r['new_evolution_steps']==0 and r['source_uncertainty_retained']
        assert r['comparison_coordinate']=='u=s/D; whole closed domain [0,1]'
        final=states[TOTAL][1];assert raw['last_checkpoint']==ptr
        for key in ('elapsed_seconds','integration_cpu_seconds','max_picard'):assert r[key]==final[key]
        assert list(map(Q,r['max_error_bounds_exact']))==final['max_errors']
        assert list(map(Q,r['domain_maxima']))==final['domain_maxima']
        assert r['max_error_bounds_decimal']==list(map(float,final['max_errors']))
        assert raw['event_cover']==states[TOTAL][0]['event_cover']
        mode=None
        if name=='mode':
            assert r['field_order']==['W','H','Phi','T','exp(-W)','psi','f','g']
            expected=[(TOTAL-2,*COVER[0]),(TOTAL-1,*COVER[1])]
            assert [(v['cell'],v['left'],v['right']) for v in r['event_cover']]==expected
            F=I(*r['F_mu']['exact']);stored=final['event_derivative']
            assert F.lo==stored.lo and F.hi==stored.hi
            assert r['F_mu']['decimal']==[float(F.lo),float(F.hi)]
            passed=F.hi<0
            assert all(v['F_mu'].hi<0 for v in r['event_cover'])==passed
            for v in r['event_cover']:assert F.overlap(v['F_mu'])
            y=final['y'];endpoint=y[11]+2*y[3]*y[9]+final['p']['gamma']*y[10]/2
            assert endpoint.overlap(F),'Endpoint derivative expression inconsistent with event hull'
            mode={'uniform_F_mu':F.record(),'strictly_negative':passed,
                  'event_intersections':[[str(v['left']),str(v['right'])] for v in r['event_cover']],
                  'independent_final_state_expression':endpoint.record(),
                  'unique_negative_eigenvalue_in_inherited_bracket':passed,
                  'no_uniqueness_claim_outside_bracket':True,
                  'derivative_fixed_background_and_D':True}
            self.mode_unique=passed
        else:
            assert r['field_order']==['A','ell','Phi'] and r['F_mu'] is None
            passed=True
        assert r['passed']==passed and term['status']==('COMPLETE' if passed else 'SCIENTIFIC_GATE_FAILED')
        finding={'status':term['status'],'passed':passed,'cells':TOTAL,'checkpoint_count':count,
            'max_picard':r['max_picard'],'elapsed_seconds':r['elapsed_seconds'],
            'integration_cpu_seconds':r['integration_cpu_seconds'],'field_order':r['field_order'],
            'material_or_source_error_bounds_exact':r['max_error_bounds_exact'],
            'material_or_source_error_bounds_decimal':r['max_error_bounds_decimal'],
            'domain_maxima_exact':r['domain_maxima'],'domain_maxima_decimal':list(map(lambda q:float(Q(q)),r['domain_maxima'])),
            'result_sha256':sha(folder/'RESULT.json'),'terminal_sha256':sha(folder/'TERMINAL_CHECKPOINT.json')}
        if mode:finding['mode_selection']=mode
        self.flow_results[name]=finding;return finding
    def arbq(self,x):
        x=Q(x);return self.flint.arb(self.flint.fmpq(x.numerator,x.denominator))
    def arange(self,lo,hi):
        lo,hi=Q(lo),Q(hi);assert lo<=hi
        # Addition of an outward radius encloses the exact rational interval.
        m=self.arbq((lo+hi)/2);r=self.arbq((hi-lo)/2)
        return m+self.flint.arb(0,r.upper())
    def abounds(self,z):
        assert z.is_finite();m=dyadic(z.mid().man_exp());r=dyadic(z.rad().man_exp());return I(m-r,m+r)
    def amax(self,z):return self.abounds(z).maxabs()
    def apoly(self,row,z):
        out=self.flint.arb(0)
        for c in reversed(row):out=out*z+c
        return out
    def coefficients(self,x):
        if isinstance(x,list):return [self.coefficients(v) for v in x]
        return self.arbq(x)
    def grid(self,case,N):
        gate=Q(1,10**50);native=self.parent('native','results/fine_c4')
        dense=self.read(native/f'case_{case}.dense.json');seed=self.seed_raw
        h,Dn=Q(seed['h']),Q(seed['D']);eps=Q(dense['epsilon'])
        assert -E<=eps<=E and len(dense['segments'])==256
        name=f'fine_c4_case{case}_N{N}_p80';gp=self.parent('spatial','inputs/'+name+'.grid.json')
        raw=self.read(gp);old=self.read(gp.with_name(name+'.audit.json'))
        assert old['grid_sha256']==sha(gp) and old['all_velocities_exactly_zero']
        assert raw['N']==N and raw['dps']==80 and raw['fields']==['A','B','Phi']
        assert all(Q(raw['action'][k])==Q(v) for k,v in MODEL.items())
        assert self.common['p']['k'].contains(Q(raw['k']))
        assert all(len(raw[k])==N+1 for k in ('A','B','Phi','ell','s','x','seed_fields'))
        assert all(Q(v)==0 for row in raw['velocities'] for v in row)
        assert all(Q(v)==0 for v in raw['Cauchy_constants'].values())
        assert len(raw['gauge_coefficients'])==12 and len(raw['coordinate_integral_polynomials'])==256
        assert len(raw['coordinate_knots'])==257
        base=self.coefficients(seed['segments']);metric=self.coefficients([b[0] for b in dense['segments']])
        correction=self.coefficients(dense['correction']);q=self.coefficients(raw['gauge_coefficients'])
        polys=self.coefficients(raw['coordinate_integral_polynomials']);knots=self.coefficients(raw['coordinate_knots'])
        errors={n:Q(0) for n in ('A','B','Phi','ell','seed_fields','map_at_saved_s','map_join_defect','map_end_length')}
        lower=None
        for i,row in enumerate(polys):
            width=Dn-i*h if i==255 else h;assert width>0
            deriv=[j*c for j,c in enumerate(row) if j]
            bound=self.abounds(self.apoly(deriv,self.arange(0,width))).lo
            lower=bound if lower is None else min(lower,bound)
            join=knots[i]+self.apoly(row,self.arbq(width))-knots[i+1]
            errors['map_join_defect']=max(errors['map_join_defect'],self.amax(join))
        assert lower>0
        errors['map_end_length']=self.amax(knots[-1]-self.arbq(raw['X']))
        clocks=[]
        for i in range(N+1):
            s=Q(raw['s'][i]);x=Q(raw['x'][i]);assert -gate<=s<=Dn+gate
            ratio=s/h;idx=max(0,min(255,ratio.numerator//ratio.denominator));z=self.arbq(s-idx*h)
            values=[self.apoly(row,z) for row in base[idx]]
            aa=self.apoly(metric[idx],z);bb=aa+self.apoly(q,self.arbq(s))
            pp=values[2]+self.arbq(eps)*values[6]+self.apoly(correction,self.arbq(s));ell=-2*self.arbq(eps)*values[5]
            for key,v in zip(('A','B','Phi','ell'),(aa,bb,pp,ell)):
                errors[key]=max(errors[key],self.amax(v-self.arbq(raw[key][i])))
            assert len(raw['seed_fields'][i])==8
            for v,w in zip(values,raw['seed_fields'][i]):
                errors['seed_fields']=max(errors['seed_fields'],self.amax(v-self.arbq(w)))
            errors['map_at_saved_s']=max(errors['map_at_saved_s'],self.amax(knots[idx]+self.apoly(polys[idx],z)-self.arbq(x)))
            if i in (0,N):
                lograte=self.arbq(Q(raw['B'][i])-Q(raw['seed_fields'][i][0]))
                wallq=Q(raw['B'][i])-Q(raw['A'][i]);assert abs(wallq)<=gate
                assert self.amax(self.apoly(q,self.arbq(s)))<=gate
                clocks.append({'wall':0 if i==0 else 1,'normal_orientation_sigma':1 if i==0 else -1,
                    'q_at_wall_exact':str(wallq),'normalized_proper_clock_rate_enclosure':self.abounds(lograte.exp()).record()})
        assert max(errors.values())<=gate,('independent represented polynomial replay',case,N,{k:float(v) for k,v in errors.items()})
        return {'case':case,'N':N,'passed':True,'grid_sha256':sha(gp),'audit_sha256':sha(gp.with_name(name+'.audit.json')),
            'independent_residual_upper_exact':{k:str(v) for k,v in errors.items()},
            'independent_residual_upper_decimal':{k:float(v) for k,v in errors.items()},
            'positive_represented_cell_map_derivative_lower_exact':str(lower),
            'positive_represented_cell_map_derivative_lower_decimal':float(lower),
            'clock_and_normals':clocks,'zero_momenta':True,
            'scope':'Exact saved decimal polynomial replay with outward Arb arithmetic, not exact physical lapse/inverse-map or evolution error.'}
    def readback(self):
        path=self.root/'NUMERICAL_READBACK.json'
        failure=None;aggregate=path.exists()
        if not path.exists():
            fp=self.root/'NUMERICAL_READBACK_FAILURE.json'
            if fp.exists():
                failure=self.read(fp);assert failure['guard']==GUARD and failure['status']=='FAILED_CLOSED'
                assert failure['type']=='ArithmeticError' and failure['error']=='Frozen representation replay gate'
                assert not failure['automatic_restart_allowed']
                records=sorted((self.root/'readback').glob('case*-p*.json'))
                assert [v.name for v in records]==['case0-p80.json']
                r={'cases':[self.read(v) for v in records],'root_bounds':[]}
            else:
                assert not getattr(self,'spatial_pass',False),'Numerical readback not terminal'
                return {'status':'NOT_ADMITTED','passed':False}
        else:
            r=self.read(path);assert r['guard']==GUARD and r['passed'] and r['new_evolution_steps']==0
            assert not r['continuum_evolution_error_certified'] and r['elapsed_seconds_this_invocation']>=0
            assert r['reused_gauge_and_map_kernel_disclosed'] and r['independent_saved_field_polynomial_evaluation']
        admission=self.read(self.parent('admission','VERIFICATION.json'));spatial=self.read(self.parent('spatial','VERIFICATION.json'))
        assert admission['all_passed'] and spatial['record_integrity_valid'] and spatial['complete_signed_cohort_qualified']
        accepted=self.read(self.parent('spatial','GRID_ADMISSION.json'));assert accepted['all_passed']
        required={f'inputs/fine_c4_case{case}_N{N}_p80{suffix}' for case in (0,3,4) for N in (160,192)
                  for suffix in ('.json','.grid.json','.audit.json')}
        selected={v['path']:v['sha256'] for v in accepted['inputs'] if v['path'] in required}
        assert set(selected)==required
        for n,h in selected.items():self.linked(self.parent('spatial',n),h)
        expected=[(i,d) for i in (0,3,4) for d in (80,100)] if aggregate else [(0,80)]
        assert [(v['case'],v['dps']) for v in r['cases']]==expected
        gate=Q(1,10**50);grid_findings={};replay_max=Q(0)
        for entry in r['cases']:
            case,dps=entry['case'],entry['dps'];raw=self.read(f'readback/case{case}-p{dps}.json')
            assert raw==entry and raw['guard']==GUARD and raw['passed'] and raw['new_evolution_steps']==0
            assert raw['rigorous_lapse_error_bound'] is None and raw['rigorous_inverse_map_error_bound'] is None
            assert [v['N'] for v in raw['grids']]==[160,192] and raw['saved_epsilon_in_certified_interval']
            target=Q(0) if case==0 else E if case==3 else -E
            dense=self.read(self.parent('native',f'results/fine_c4/case_{case}.dense.json'))
            eps=Q(dense['epsilon']);assert -E<=eps<=E and Q(raw['epsilon_target'])==target
            assert Q(raw['epsilon_saved_exact_decimal'])==eps and Q(raw['epsilon_rounding_offset'])==eps-target
            for side in raw['gauge_final_rows']:
                for row in side:
                    for v in row:Q(v)  # rejects nonfinite decimal spellings
            for row in raw['grids']:
                N=row['N'];key=f'case{case}_N{N}'
                if key not in grid_findings:grid_findings[key]=self.grid(case,N)
                independent=grid_findings[key]
                assert row['passed'] and row['initial_physical_momenta_exactly_zero']
                assert row['grid_sha256']==independent['grid_sha256'] and row['audit_sha256']==independent['audit_sha256']
                errors=list(map(Q,row['errors'].values()));assert errors and all(0<=v<=gate for v in errors)
                replay_max=max(replay_max,max(errors));assert Q(row['positive_represented_map_derivative_lower'])>0
                assert len(row['clock_and_normals'])==2
                for clock,own in zip(row['clock_and_normals'],independent['clock_and_normals']):
                    assert clock['normal_orientation_sigma']==own['normal_orientation_sigma']
                    assert abs(Q(clock['q_at_wall']))<=gate
                    b=I(*own['normalized_proper_clock_rate_enclosure']['exact'])
                    reported=Q(clock['normalized_proper_clock_rate'])
                    assert I(b.lo-gate,b.hi+gate).contains(reported)
        assert len(r['root_bounds'])==(2 if aggregate else 0)
        for row,name in zip(r['root_bounds'],('positive','negative')):
            own=self.root_findings[name];intervals=self.root_intervals[name]
            assert row['case']==own['case'] and Q(row['target_epsilon'])==Q(own['epsilon_exact'])
            assert row['source_sha256']==own['old_result_sha256'] and row['within_common_uniqueness_box']
            assert row['center_exact']==own['center_exact']
            assert row['root_enclosure_exact']==[v.record()['exact'] for v in intervals]
            errors=[max(abs(v.lo-Q(c)),abs(v.hi-Q(c))) for v,c in zip(intervals,own['center_exact'])]
            assert list(map(Q,row['distance_from_saved_center_upper_exact']))==errors
            assert row['independent_reconstruction_sha256']==sha(self.parent('connected','INDEPENDENT_AUDIT.json'))
        diagnostic=None
        if not aggregate:
            dp=self.root/'audit/FAILED_REPLAY_DIAGNOSTIC.json'
            diagnostic=self.read(dp)
            assert diagnostic['status']=='FAILED_GATE_REPRODUCED_DIAGNOSTIC_ONLY'
            assert diagnostic['guard']==GUARD and diagnostic['case']==0 and diagnostic['dps']==100 and diagnostic['N']==160
            assert diagnostic['failure_sha256']==sha(self.root/'NUMERICAL_READBACK_FAILURE.json')
            self.linked(self.root/'audit/diagnose_failed_replay.py',diagnostic['source_sha256'])
            assert not diagnostic['physical_IVP_run'] and not diagnostic['gate_passed'] and not diagnostic['producer_restarted']
            assert diagnostic['reconstruction_gate']=='1e-50'
            assert any(Q(v)>gate for v in diagnostic['errors_exact_binary'].values())
        return {'status':'COMPLETE' if aggregate else 'NUMERICAL_REPRESENTATION_GATE_FAILED',
            'passed':aggregate,'failure':failure,'failed_replay_diagnostic':diagnostic,
            'case_precision_records':len(r['cases']),'unique_grids_independently_replayed':len(grid_findings),
            'reported_replay_error_max_exact':str(replay_max),'reported_replay_error_max_decimal':float(replay_max),
            'grids':grid_findings,'root_bounds':r['root_bounds'],'new_time_evolution_steps':0,
            'shared_gauge_map_constructor_disclosed':True,'rigorous_exact_conformal_lapse_error_bound':None,
            'rigorous_exact_inverse_map_error_bound':None,'continuum_evolution_error_certified':False,
            'distinct_zero_case_metric_correction_in_producer_validated_error_bounds':False,
            'zero_case_note':'Case 0 is separately reconstructed for polynomial/grid replay. Its metric was separately integrated and has a tiny nonzero C7 scalar correction; the mode/source error receipt alone is not a validated bound for that prepared zero-case metric.',
            'metric_tensor_note':'A, ell and Phi bounds concern coefficient functions at common u=s/D. A g_uu error also involves D^2; no transformed metric-tensor or full conformal-observable error norm was computed.',
            'map_note':'Positive derivatives hold on each represented polynomial cell. Decimal join residuals are measured explicitly; no exact continuum lapse/inverse-map error follows from this representation check.'}
    def run(self):
        assert (self.root/'SPATIAL_ENCLOSURES.json').exists() or (self.root/'RUN_FAILURE.json').exists(),'Spatial producer not terminal'
        self.authenticate();source=self.source();roots=self.roots();cover=self.coverage()
        spatial_path=self.root/'SPATIAL_ENCLOSURES.json';spatial=None
        if spatial_path.exists():
            spatial=self.read(spatial_path);assert spatial['guard']==GUARD and spatial['no_time_evolution']
            names=[v['task'] for v in spatial['tasks']]
            assert names==CONFIG['flow_order'][:len(names)] and 1<=len(names)<=3
        else:
            failure=self.read('RUN_FAILURE.json');assert failure['guard']==GUARD and failure['status']=='FAILED_CLOSED'
            names=[n for n in CONFIG['flow_order'] if (self.root/'output'/n).exists()]
        findings={}
        for index,name in enumerate(names):
            findings[name]=self.flow(name,index)
            if spatial:assert spatial['tasks'][index]==self.read(f'output/{name}/RESULT.json')
        self.spatial_pass=len(findings)==3 and all(v.get('passed',False) for v in findings.values())
        if spatial:assert spatial['passed']==self.spatial_pass
        numerical=self.readback();accepted=self.spatial_pass and numerical['passed'] and self.mode_unique
        identity=self.spatial_pass and self.mode_unique
        classification=('D1_C4_INITIAL_FAMILY_IDENTIFIED_WITH_PARTIAL_NUMERICAL_ERROR_ADMISSION' if accepted else
            'D1_C4_TARGET_IDENTIFIED_WITH_PARTIAL_SPATIAL_BOUNDS__NUMERICAL_REPRESENTATION_ADMISSION_FAILED' if identity else
            'MODE_SOURCE_UNIQUENESS_NOT_CERTIFIED' if findings.get('mode',{}).get('status')=='SCIENTIFIC_GATE_FAILED' else
            'IDENTITY_ADMISSION_TECHNICAL_OR_NUMERICAL_INCOMPLETE')
        # No new numerical work is started. Liveness is a read-only final snapshot.
        import subprocess
        workers=[]
        for line in subprocess.check_output(['ps','-eo','pid=,args='],text=True).splitlines():
            if str(self.root) in line and ('identity_run.py run' in line or 'numerical_readback.py' in line):workers.append(line.strip())
        assert not workers,('Concurrent production is forbidden during serialized audit',workers)
        before=dict(self.files)
        for path,h in before.items():assert sha(path)==h,('File changed during audit',path)
        return {'overall':'PASS','guard':GUARD,'scientific_classification':classification,
            'bounded_identification_accepted':accepted,'inputs_unchanged':True,
            'finite_jet_target_identification_accepted':identity,
            'mode_source_unique_in_inherited_bracket':getattr(self,'mode_unique',False),
            'full_numerical_representation_admission_accepted':numerical['passed'],
            'audit_source_sha256':sha(Path(__file__).resolve()),
            'spatial_enclosures_sha256':sha(spatial_path) if spatial_path.exists() else None,
            'numerical_readback_sha256':sha(self.root/'NUMERICAL_READBACK.json') if (self.root/'NUMERICAL_READBACK.json').exists() else None,
            'numerical_readback_failure_sha256':sha(self.root/'NUMERICAL_READBACK_FAILURE.json') if (self.root/'NUMERICAL_READBACK_FAILURE.json').exists() else None,
            'original_failed_attempt_preserved':True,'original_failure_sha256':self.old_failure_sha256,
            'source_and_wall_premises':source,'inherited_endpoint_signs':self.inherited_endpoint_signs,
            'root_identity':roots,'complete_domain_coverage':cover,'spatial_flows':findings,'numerical_readback':numerical,
            'finite_jet_bridge_symbolic_checks':15,'preflight_controls':self.control_flags,
            'checkpoint_count':self.checkpoints,'native_ball_count':self.native_count,
            'native_count_convention':'Successful native payload roundtrip visits, including re-read result/parent payloads.',
            'source_input_review_hash_links':self.hash_links,'runtime_library_hash_links':self.runtime_links,
            'checked_unique_file_count':len(before),'checked_file_index_sha256':digest(before),
            'parent_manifest_counts':self.binding['parent_counts'],
            'arithmetic':'Separate exact Fraction interval gates; pinned Arb 768-bit roundtrips and saved polynomial enclosures; no producer numerical kernel imported.',
            'physical_IVP_replayed':False,'new_time_evolution_steps':0,
            'current_production_liveness':{'matching_workers':workers,'utc':datetime.now(timezone.utc).isoformat()},
            'claim_limits':['Mode uniqueness only inside the inherited negative bracket, not a complete spectrum.',
                'Exact C4 finite-jet initial-data bridge, not all-order compatibility or a spacetime existence theorem.',
                'Whole-domain coefficient-function bounds are conservative enclosures, not measured error or ppm accuracy.',
                'The represented grid is not literally the exact interval-certified root.',
                'No separately validated zero-case prepared metric correction, exact conformal lapse/inverse map, g_uu tensor-error norm or continuum evolution error.',
                'No amplitude enlargement, parameter-neighborhood identification, P16/MOTS, collapse or causal conclusion.']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--output');args=parser.parse_args()
    try:
        result=Review(args.root).run()
    except Exception as error:
        result={'overall':'FAIL','guard':GUARD,'audit_source_sha256':sha(Path(__file__).resolve()),
                'error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc(),
                'scientific_classification':'INDEPENDENT_AUDIT_NOT_ACCEPTED','physical_IVP_replayed':False}
    payload=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n'
    if args.output:
        with Path(args.output).open('x') as stream:stream.write(payload)
    print(payload,end='');return 0 if result['overall']=='PASS' else 1


if __name__=='__main__':sys.exit(main())
