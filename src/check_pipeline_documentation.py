#!/usr/bin/env python3
"""Read-only documentary/linkage checks; no producer imports or integrations."""
import argparse
import hashlib
import json
import re
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.set_int_max_str_digits(0)
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
ap.add_argument('--supplement', type=Path, help='Optional editable supplement for locator checks')
ap.add_argument('--output', type=Path)
args = ap.parse_args()
root = args.repo.resolve()
checks = {}
def check(name, value): checks[name] = bool(value)
def load(path): return json.loads((root/path).read_text())
def sha(path): return hashlib.sha256((root/path).read_bytes()).hexdigest()
ex = 'data/raw/l001/experiments/'
doc = 'docs/pipeline-supplement/'
catalog = load(doc+'TEST_CATALOG.json')
manifest = load('data/processed/l001/ARCHIVE_MANIFEST.json')
index = {'data/raw/l001/'+r['path']:r['sha256'] for r in manifest['files']}
check('catalog_manifest_identity',sha('data/processed/l001/ARCHIVE_MANIFEST.json')==catalog['archive_manifest_sha256'])
counts = catalog['counts']
check('catalog_entry_count',counts['catalog_entries']==len(catalog['packets'])==317)
check('unique_packet_ids',len({r['id'] for r in catalog['packets']})==len(catalog['packets']))
check('top_level_packet_count',counts['top_level_packets']==len([p for p in (root/ex).iterdir() if p.is_dir()])==210)
check('static_gate_count',sum(len(r['static_gate_excerpts']) for r in catalog['packets'])==counts['static_gate_excerpts']==9365)
check('binding_closure_count',sum(r['bound_to_selected_route'] for r in catalog['packets'])==counts['selected_bound_top_level_closure']==137)
for row in catalog['packets']:
    paths = [row['folder']]+row['entry_sources']+row['contract_documents']+row['output_files']
    if row['purpose_source']: paths.append(row['purpose_source'])
    check('paths:'+row['id'],all((root/p).exists() for p in paths))
check('artifact_manifest_crosswalk',all(index.get(a['repo_path'])==a['sha256'] for a in catalog['artifact_table'] if a['repo_path']))
check('no_manifest_mismatch',not any(a['resolution']=='manifest_mismatch' for a in catalog['artifact_table']))
check('gate_source_locations',all(1<=g['line']<=len((root/g['file']).read_text().splitlines()) for r in catalog['packets'] for g in r['static_gate_excerpts']))
stages=load(doc+'STAGE_MAP.json')
for stage in stages['stages']:
    check('stage_locators:'+stage['id'],all((root/p).exists() for p in stage['locations']))
    check('stage_contract_fields:'+stage['id'],all(stage.get(k) for k in ['purpose','inputs','gates','outputs']))

fdir=ex+'20261027_ACTUAL_NINTH_FULL_BUDGET/'
final=load(fdir+'RESULT.json');term=load(fdir+'TERMINAL.json')
for file,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256'),('PINS.json','pins_sha256')]:
    check('final_identity:'+file,sha(fdir+file)==term[key])
check('final_expected_result',term['result_sha256']=='f42c5d1cfd8ce5f3617e700faf6a6c3269a0eaa3d9909959ef737d35338f8b73')
check('final_expected_terminal',sha(fdir+'TERMINAL.json')=='2a0f983f7ac60e5359c48b5a3219136347935b1ac6d5bcd0c26fb96fbd0d9642')
check('final_classification',final['classification']=='PREDECLARED_THREE_QUARTER_ENDPOINT_ADMITTED' and final['iterations']==0)
check('five_gates',set(final['lower']['gates'])=={'clock','distance','scalar','scalar_derivative','opening'} and all(final['lower']['gates'].values()))
R=Q(final['physical_radius']);eta=Q(final['lower']['eta'])
check('exact_radius',R==Q(1,102458487083689624677120))
check('exact_admitted_endpoint',Q(final['lower_q'])==Q(final['upper_q'])==Q(3,4) and eta==3*R/4==Q(1,136611316111586166236160))
check('four_ratios_below_one',all(0<Q(v)<=1 for v in final['lower']['ratios'].values()))
check('opening_inequality',eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0)
grid=load(ex+'20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json')
c=grid['constants_exact']['refined'];sel=grid['selected']['refined']
K=Q(c['K']);seed=Q(c['seed']);R0=Q(c['R'])
check('selected_majorant',K==109802048057794951 and seed==1215 and R0==1/(96*K))
check('selected_ray',Q(sel['graph_weight'])==Q(1,256) and Q(sel['oscillator_weight'])==1 and Q(sel['a'])==Q(21,2305843009213693952))
check('radius_from_majorant',Q(c['physical_radius'])==R==R0/(8*seed))
check('aggregate_from_majorant',Q(c['aggregate_bound'])==Q(513,256)*R0==Q(171,899498377689456238592))
u=K*R0
check('majorant_self_map',R0/2+K*R0**2/(1-u)**2<R0)
check('majorant_contraction',2*u/(1-u)**2+2*u**2/(1-u)**3<1)
audit=load(ex+'20261027_QUARTIC_REAL_SOURCE_AUDIT/ACTUAL_NINTH_FULL_BUDGET_AUDIT.json')
check('audit_pass',audit['PASS'] is True)
check('audit_terminal_link',audit['producer_terminal']==sha(fdir+'TERMINAL.json'))

model=load('data/raw/neutral-certificates/kinetic/inputs/14_21_14_04_MODEL.json')
phase=load('data/raw/neutral-certificates/phase/phase_regeneration/source/inputs/central_bindings.json')
check('model_exact_linkage',model['model_exact']==phase['model_exact'])
check('launch_event_linkage',list(map(Q,model['A']))==list(map(Q,phase['config']['A'])) and list(map(Q,model['D']))==list(map(Q,phase['config']['D'])))
if args.supplement:
    text=args.supplement.read_text()
    for n,s in enumerate(re.findall(r'`([^`\n]+)`',text)):
        p=None
        if s.startswith('NC/'):p='data/raw/neutral-certificates/'+s[3:]
        elif s.startswith('EX/'):p=ex+s[3:]
        elif s.startswith('202610') and re.fullmatch('[A-Za-z0-9_]+',s):p=ex+s
        elif s.startswith(('src/','tests/','data/','docs/','manuscript/')) and not any(c in s for c in '*{}'):
            p=s
        if p:
            check('supplement_locator:'+str(n), (root/p).exists())
    check('supplement_catalog_counts',all(s in text for s in ['317 entries','9365 static gate excerpts','137 top-level packets']))
    check('anonymous_source_copy',not any(s in text for s in ['/Users/','parallels@','github.com/RonBibb']))
report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':len(checks),'failed':[k for k,v in checks.items() if not v],
        'scope':'Document locators, frozen-manifest crosswalk, selected saved identities and exact downstream arithmetic only. No scientific producer imports/integrations, seven-source domination proof, analytic-inverse audit or independent scientific acceptance.',
        'scientific_producers_executed':0,'new_integrations':0,'catalog_counts':counts,
        'checks_detail':checks}
if args.output:
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks_detail'},indent=2))
raise SystemExit(0 if report['status']=='PASS' else 1)
