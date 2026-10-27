"""Read-only connected-cover audit. No producer kernel imports or IVP replay.

Reuses this reviewer's authenticated preceding Fraction/native audit primitives;
the new graph, uniform gates, coverage and endpoint identifications are separate.
Run only after the producer is terminal and serial verification is authorized.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import sys
import traceback
from fractions import Fraction as Q
from pathlib import Path

GUARD='20151671f46efccf55d0a6aba012acaef477eb1705e922d454ede5d3b3104412'
PREVIOUS='lin-c4-finite-amplitude-20261005T223500Z'
OLD_AUDITOR='8ae051f604f2828db3706b0e56877b4346ab8655392febe79863e84856af8716'
OLD_MANIFEST='4063c179e73776e9a615b2bbfdf65ecc2eeea86a8b2bda29baeda3bfdf9d988b'
OLD_RESULT='07272075e30a1a700fcaba57be3b490a86682b092965432c6885e1a0e7105d29'
E=Q(1,200000)
RAD=[Q(1,100000),Q(1,10),Q(1,10)]
C=[Q(-24,23),Q(1),Q(1)]
TOTAL=16365
COVER=[['32727/16384','4091/2048'],['4091/2048','32729/16384']]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def merge(tiles):
    out=[]
    for a,b in sorted((Q(a),Q(b)) for a,b in tiles):
        assert -E<=a<=b<=E
        if out and a<=out[-1][1]:out[-1][1]=max(b,out[-1][1])
        else:out.append([a,b])
    zero=next(([str(a),str(b)] for a,b in out if a<=0<=b),None)
    gaps=[];at=-E
    for a,b in out:
        if at<a:gaps.append([str(at),str(a)])
        at=max(at,b)
    if at<E:gaps.append([str(at),str(E)])
    return {'full':out==[[-E,E]],'components':[[str(a),str(b)] for a,b in out],
            'zero_component':zero,'gap_endpoints':gaps,
            'gap_convention':'Interior of each listed gap is uncovered; endpoints may belong to a closed accepted tile.'}


class Review:
    def __init__(self,packet):
        self.root=Path(packet).resolve();self.prev=self.root.parent/PREVIOUS
        ap=self.prev/'postrun_audit.py';assert sha(ap)==OLD_AUDITOR
        spec=importlib.util.spec_from_file_location('authenticated_prior_independent_audit',ap)
        self.old=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.old)
        self.io=self.old.Audit(self.root);self.I=self.old.I
        self.checkpoints=0;self.hash_links=0;self.runtime_links=0;self.nodes={}
    def read(self,p):return self.io.read(p)
    def native(self,x):return self.io.native(x)
    def authenticate(self):
        b=self.read('BINDINGS.json');assert sha(self.root/'BINDINGS.json')==GUARD
        assert self.read('FREEZE_RECORD.json')['guard']==GUARD
        assert sha(self.prev/'MANIFEST.json')==OLD_MANIFEST and sha(self.prev/'RESULT.json')==OLD_RESULT
        assert b['model_exact']==self.old.MODEL
        old=self.read(self.prev/'BINDINGS.json');expected=dict(old['config'])
        for k in ('epsilon','source_seconds_cap','zero_seconds_cap','case_seconds_cap'):expected.pop(k)
        expected.update(max_case_workers=1,epsilon_interval=['-1/200000','1/200000'],maximum_cover_depth=2,
            maximum_cover_nodes=7,maximum_cells=229110,graph_integration_cpu_seconds_cap=7200,
            center=['0','0','0'],cpu_cap_scope='validated_step_loop_excludes_preparation_and_final_publication',
            physical_source='reuse_authenticated_complete_source',
            traversal='depth_first_left_before_right_split_only_completed_noncertificate')
        assert b['config']==expected and b['runtime']==old['runtime']
        for label in ('sources','reviews','inputs'):
            for name,h in b[label].items():
                p=(self.root/name).resolve();assert sha(p)==h,(label,name)
                self.io.files[str(p)]=h;self.hash_links+=1
        rt=b['runtime'];assert rt['python']==platform.python_version() and rt['flint']==self.io.flint.__version__
        assert rt['bits']==768 and rt['threads']==1 and rt['environment']==self.old.ENV
        assert all(os.environ.get(k)==v for k,v in self.old.ENV.items())
        assert str(Path(sys.executable).resolve())==rt['executable']
        for p,h in {rt['executable']:rt['executable_sha256'],**rt['libraries']}.items():
            assert sha(p)==h,p;self.io.files[p]=h;self.runtime_links+=1
        m=self.read(self.prev/'MANIFEST.json');entries=m.get('entries') or [{'path':n,**v} for n,v in m['files'].items()]
        assert len(entries)==b['previous_manifest_count']
        for e in entries:assert b['inputs']['../'+PREVIOUS+'/'+e['path']]==e['sha256']
        controls=[n for n in b['inputs'] if not n.startswith('../') and n.endswith('/RESULT.json')]
        assert len(controls)==1;control=self.read(controls[0])
        assert control['pass'] and all(control['checks'].values()) and control['sources']==b['sources']
        assert control['runtime']==rt and not control['physical_D1_outcomes_evaluated']
        inherited_path=Path(controls[0]).parent/'inherited/RESULT.json'
        inherited=self.read(inherited_path)
        assert sha(self.root/inherited_path)==control['inherited_control_sha256']
        assert inherited['pass'] and all(inherited['checks'].values()) and inherited['sources']==b['sources']
        prior=self.read(self.prev/'RESULT.json');audit=self.read(self.prev/'INDEPENDENT_AUDIT.json')
        assert prior['independently_accepted'] and audit['overall']=='PASS' and audit['both_signed_certificates_accepted']
        assert prior['artifacts']['INDEPENDENT_AUDIT.json']==sha(self.prev/'INDEPENDENT_AUDIT.json')
        for name in ('INDEPENDENT_CENTERED_IVP.json','INDEPENDENT_NONLINEAR_ENDPOINT.json'):
            s=self.read(name);assert s['status']=='PASS' and all(s['checks'].values()) and not s['physical_integration_performed']
        self.binding=b;self.control_counts=[len(control['checks']),len(inherited['checks'])]
        # Recheck the inherited certified source and zero control, read-only.
        self.parentio=self.old.Audit(self.prev);self.parentio.authenticate()
        self.source=self.parentio.source();self.zero=self.parentio.case('zero')
        assert self.source['status']=='COMPLETE' and self.zero['pass']
        self.io.files.update(self.parentio.files)
    def gates(self,G,J):
        M=[[int(i==j)-C[i]*J[i][j] for j in range(3)] for i in range(3)]
        norms=[sum(M[i][j].maxabs()*RAD[j] for j in range(3))/RAD[i] for i in range(3)]
        image=[-C[i]*G[i]+sum((M[i][j]*self.I(-RAD[j],RAD[j]) for j in range(3)),self.I(0)) for i in range(3)]
        ratios=[v.maxabs()/r for v,r in zip(image,RAD)]
        include=[q<Q(9,10) for q in ratios];contract=max(norms)<=Q(1,2)
        return {'pass':all(include) and contract,'component_inclusions':include,'contraction':contract,
                'image':image,'ratio_exact':list(map(str,ratios)),'ratio_decimal':list(map(float,ratios)),
                'norm_exact':list(map(str,norms)),'norm_decimal':list(map(float,norms))}
    def checkpoint_audit(self,node):
        folder=self.root/'output'/node['id'];states={};I=self.I(*map(Q,node['epsilon']))
        for path in sorted((folder/'checkpoints').glob('*.json')):
            raw=self.read(path);assert raw['guard']==GUARD;h=digest(raw)
            sraw=raw['state'];slot=(sraw['task_index'],sraw['cell_index'])
            assert path.name==f'{slot[0]:02d}-{slot[1]:06d}-{h}.json' and slot not in states
            s=self.native(sraw);assert s['node']==node and slot[0] in (0,1,2) and 0<=slot[1]<=TOTAL
            assert slot[1]==0 or slot[1]==TOTAL or slot[1]%256==0
            assert len(s['y'])==17 and 1<=s['max_picard']<=32
            assert s['elapsed_cpu_seconds']>=0 and s['elapsed_seconds']>=0
            self.io.parameters(s['p']);assert s['p']['eps'].contains(I) and s['preparation']['eps'].contains(I)
            assert s['common_sha256']==sha(self.prev/'output/source/RESULT.json')
            a,b=map(Q,s['preparation']['epsilon_remainder_domain']);assert a<=min(0,I.lo) and max(0,I.hi)<=b
            for item in s['preparation']['c7_epsilon_evidence']:
                assert item['base'][0].exactzero() and item['base'][1].exactzero()
            for item in s['preparation']['W_epsilon_evidence']:
                assert item['base_coefficients'][0].exactzero() and item['base_coefficients'][1].exactzero()
            if slot[1]:
                assert s['y'][8].contains(Q(slot[1],8192)) and s['y'][4].lo>0
                for x,r in zip(s['p']['x'],RAD):
                    assert x.exactzero() if slot[0]==0 else x.contains(self.I(-r,r))
            assert s['cover']==(COVER if slot[1]==TOTAL or slot[1]==0 and slot[0]>0 else [])
            states[slot]=(sraw,s);self.checkpoints+=1
        if states:
            ptr=self.read(folder/'LATEST.json');assert ptr['guard']==GUARD
            p=(folder/ptr['path']).resolve();assert p.parent==(folder/'checkpoints').resolve()
            z=self.read(p);assert digest(z)==ptr['digest'] and p.stem.endswith(ptr['digest'])
            assert (z['state']['task_index'],z['state']['cell_index'])==max(states)
            for phase in (0,1):
                cells=sorted(k for j,k in states if j==phase and k)
                if cells:
                    last=cells[-1];expected=list(range(256,min(last,TOTAL-1)+1,256))
                    if last==TOTAL:expected.append(TOTAL)
                    assert cells==expected
        return states
    def node(self,node):
        folder=self.root/'output'/node['id'];states=self.checkpoint_audit(node)
        if (folder/'FAILURE.json').exists():
            failure=self.read(folder/'FAILURE.json');assert failure['guard']==GUARD
            assert not (folder/'TERMINAL.json').exists()
            return {'status':'TECHNICAL_INCOMPLETE','node':node,'failure':failure}
        raw=self.read(folder/'RESULT.json');t=self.read(folder/'TERMINAL.json')
        assert t['guard']==GUARD and t['result_sha256']==sha(folder/'RESULT.json')
        assert raw['guard']==GUARD and raw['status']=='COMPLETE' and raw['node']==node
        assert raw['common_sha256']==sha(self.prev/'output/source/RESULT.json') and raw['event_covers']==[COVER,COVER]
        phases=[]
        for idx,name in enumerate(('center','box')):
            p=self.read(folder/(name+'.json'));assert p['guard']==GUARD and p['node']==node and p['phase']==name
            assert p['cells']==TOTAL and p['event_cover']==COVER and 1<=p['max_picard']<=32
            assert p['map']==states[(idx,TOTAL)][0]['map'];phases.append(p)
            dd=self.native(p['map']['wall_diagnostics']);assert all(dd[n].lo>0 for n in (0,3,5,8))
        assert raw['G_center']==phases[0]['map']['G'] and sum(raw['J_box'],[])==phases[1]['map']['J']
        r=self.native(raw);g=self.gates(r['G_center'],r['J_box'])
        assert g['pass']==r['pass'] and g['component_inclusions']==r['component_inclusions']
        for x,y in zip(g['image'],r['image_offset']):assert x.overlap(y)
        assert (2,0) in states and states[(2,0)][0]['preparation']==raw['preparation']
        return {'status':'COMPLETE','node':node,'pass':g['pass'],
                'independent_image_ratios_exact':g['ratio_exact'],'independent_image_ratios_decimal':g['ratio_decimal'],
                'independent_weighted_norms_exact':g['norm_exact'],'independent_weighted_norms_decimal':g['norm_decimal'],
                'component_inclusions':g['component_inclusions'],'contraction':g['contraction'],
                'G_center':[v.record() for v in r['G_center']],
                'J_box':[[v.record() for v in row] for row in r['J_box']],
                'max_picard':[p['max_picard'] for p in phases],'cells':2*TOTAL,
                'elapsed_cpu_seconds':r['elapsed_cpu_seconds'],'elapsed_seconds':r['elapsed_seconds'],
                'result_sha256':sha(folder/'RESULT.json')}
    def endpoints(self):
        out={}
        for name,eps in [('positive',E),('negative',-E)]:
            path=self.prev/'output'/name/'RESULT.json';raw=self.read(path);r=self.native(raw)
            t=self.read(path.parent/'TERMINAL.json');assert t['result_sha256']==sha(path) and t['guard']==self.old.GUARD
            assert Q(r['epsilon'])==eps and list(map(Q,r['radii']))==RAD and list(map(Q,r['C']))==C
            g=self.gates(r['G_center'],r['J_box']);assert g['pass'] and r['pass']
            translated=[x+Q(c) for x,c in zip(g['image'],r['center'])]
            inside=[self.I(-rr,rr).contains(v) for v,rr in zip(translated,RAD)]
            out[name]={'pass':all(inside),'epsilon':str(eps),'component_containment':inside,
                'translated_root_image':[v.record() for v in translated],
                'absolute_radius_ratios_exact':[str(v.maxabs()/rr) for v,rr in zip(translated,RAD)],
                'absolute_radius_ratios_decimal':[float(v.maxabs()/rr) for v,rr in zip(translated,RAD)],
                'old_gates_recomputed_pass':g['pass'],'old_result_sha256':sha(path)}
        return out
    def run(self):
        out=self.root/'output';assert (out/'RESULT.json').exists() or (out/'FAILURE.json').exists(),'Producer not terminal'
        self.authenticate();pending=[{'id':'r','depth':0,'epsilon':['-1/200000','1/200000']}]
        accepted=[];unresolved=[];completed=[];used=0.;technical=False;visited=[]
        while pending:
            node=pending.pop(0);visited.append(node['id']);r=self.node(node);self.nodes[node['id']]=r
            if r['status']!='COMPLETE':technical=True;unexamined=[node]+pending;break
            used+=r['elapsed_cpu_seconds'];assert used<=7200
            completed.append(node)
            if r['pass']:accepted.append(node['epsilon'])
            elif node['depth']==2:unresolved.append(node['epsilon'])
            else:
                a,b=map(Q,node['epsilon']);mid=(a+b)/2
                pending=[{'id':node['id']+'l','depth':node['depth']+1,'epsilon':[str(a),str(mid)]},
                         {'id':node['id']+'r','depth':node['depth']+1,'epsilon':[str(mid),str(b)]}]+pending
            assert len(completed)<=7
        assert {p.name for p in out.iterdir() if p.is_dir() and re.fullmatch('r[lr]{0,2}',p.name)}==set(visited)
        cover=merge(accepted);endpoint=self.endpoints()
        local=self.read(self.prev.parent/'lin-c4-local-certificate-r1-20261005T221400Z/RESULT.json')
        assert local['independently_accepted'] and local['qualitative_certificate'] and local['quantitative_radius_certificate']
        assert Q(1,2**9216)<min(RAD)
        reconciliation={'pass':cover['zero_component'] is not None and self.zero['pass'],
            'zero_component':cover['zero_component'],'inherited_zero_control_pass':self.zero['pass'],
            'same_shifted_chart_and_source':True,'exact_G_zero_and_G_epsilon_zero':'Authenticated independent identities plus unchanged physical source',
            'tangent':'x_prime(0)=0; physical tangent (psi,-2psi,f)',
            'local_identification':'Uniqueness in common X on a neighborhood of zero; no radius extrapolation'}
        if technical:
            root=self.read('output/FAILURE.json');assert root['guard']==GUARD
            assert root['completed']==completed and root['accepted_tiles']==accepted and root['unresolved_tiles']==unresolved
            assert root['unexamined']==unexamined
            label='TECHNICAL_INCOMPLETE';connected=False;terminal_path=out/'FAILURE.json'
        else:
            root=self.read('output/RESULT.json');t=self.read('output/TERMINAL.json')
            assert t['guard']==GUARD and t['result_sha256']==sha(out/'RESULT.json')
            assert root['guard']==GUARD and root['status']=='COMPLETE' and root['completed']==completed
            assert root['accepted_tiles']==accepted and root['unresolved_tiles']==unresolved
            assert root['coverage']=={k:cover[k] for k in ('full','components','zero_component')}
            expected='CONNECTED_SIGNED_C4_BRANCH_CANDIDATE' if cover['full'] else 'PARTIAL_INTERVAL_C4_COVER' if accepted else 'NO_CONNECTED_INTERVAL_CERTIFICATE'
            assert root['classification']==expected and abs(root['cpu_seconds']-used)<1e-8
            assert root['no_automatic_successor'] and not root['independently_accepted']
            connected=cover['full'] and reconciliation['pass'] and all(v['pass'] for v in endpoint.values())
            label='CONNECTED_SIGNED_C4_BRANCH_CERTIFIED' if connected else 'PARTIAL_INTERVAL_C4_COVER' if accepted else 'NO_CONNECTED_INTERVAL_CERTIFICATE'
            terminal_path=out/'RESULT.json'
        unique_files={}
        for p,h in list(self.io.files.items()):
            assert sha(p)==h,('changed during audit',p)
            resolved=str(Path(p).resolve())
            assert resolved not in unique_files or unique_files[resolved]==h
            unique_files[resolved]=h
        return {'overall':'PASS','guard':GUARD,'scientific_classification':label,
            'connected_interval_certified':connected,'accepted_tiles':accepted,'unresolved_tiles':unresolved,
            'coverage':cover,'nodes':self.nodes,'endpoint_identity':endpoint,'zero_local_reconciliation':reconciliation,
            'checkpoint_count':self.checkpoints,'native_ball_count':self.io.native_count,
            'inherited_source_zero_checkpoint_count':self.parentio.checkpoints,
            'inherited_source_zero_native_ball_count':self.parentio.native_count,
            'validated_cells_in_completed_nodes':len(completed)*2*TOTAL,
            'integration_cpu_seconds_completed':used,'inputs_unchanged':True,
            'unchanged_file_count':len(unique_files),'checked_file_path_record_count':len(self.io.files),
            'source_review_input_hash_links':self.hash_links,
            'runtime_hash_links':self.runtime_links,'preflight_check_counts':self.control_counts,
            'checked_file_index_sha256':digest(unique_files),'graph_terminal_evidence_sha256':sha(terminal_path),
            'physical_IVP_replayed':False,'arithmetic':'Exact Fraction intervals from published native balls; authenticated prior independent audit primitives reused',
            'source_and_zero_rechecked':True,'scope':'Connected initial-data branch only; no all-order compatibility, evolution or causal-fate claim'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--packet',required=True);a=p.parse_args()
    try:r=Review(a.packet).run()
    except Exception as exc:
        r={'overall':'FAIL','exception':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'physical_IVP_replayed':False}
    r['audit_source_sha256']=sha(__file__)
    print(json.dumps(r,indent=2,sort_keys=True,allow_nan=False))
    if r['overall']!='PASS':raise SystemExit(1)
