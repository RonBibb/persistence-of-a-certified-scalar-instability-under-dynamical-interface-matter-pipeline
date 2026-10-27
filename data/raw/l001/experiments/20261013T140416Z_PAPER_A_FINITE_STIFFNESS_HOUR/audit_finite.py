"""Independent standard-library terminal reconstruction; no ODE or owner imports."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,datetime,time

P=Path(__file__).resolve().parent
started=time.monotonic()
def read(n): return json.loads((P/n).read_text())
def sha(n): return hashlib.sha256((P/n).read_bytes()).hexdigest()
def interval(obj):
    x=tuple(map(F,obj['exact_bounds']))
    assert x[0]<=x[1]
    return x
def add(a,b): return a[0]+b[0],a[1]+b[1]
def mul(a,b):
    z=[x*y for x in a for y in b]
    return min(z),max(z)
def contained(a,b): return b[0]<=a[0]<=a[1]<=b[1]
gate=read('INDEPENDENT_GATE.json')
assert gate['decision']=='APPROVED_FOR_ONE_BOUNDED_EXECUTION'
for name,digest in gate['frozen_hashes'].items(): assert sha(name)==digest,name
bindings=read('SOURCE_BINDINGS.json')['files']
for name,item in bindings.items(): assert sha(name)==item['sha256'],name
for name,item in read('COPY_PROVENANCE.json')['source_mapping'].items():
    source=Path(item['source']).read_bytes(); copied=(P/name).read_bytes()
    assert hashlib.sha256(source).hexdigest()==item['original_sha256']
    assert hashlib.sha256(copied).hexdigest()==item['copy_sha256']
    assert copied==(source if item['transformation']=='identity' else source+b'\n')
spec=read('TEST_SPEC.json'); result=read('output/RESULT.json')
execution=read('EXECUTION_finite100.json')
assert execution['exit_code']==0 and execution['timed_out'] is False
assert execution['admitted'] and execution['cpu'] in range(10)
assert execution['cpu'] not in set(execution['held'])|set(execution['excluded'])
assert len(set(execution['held'])|set(execution['excluded'])|{execution['cpu']})<=10
assert result['elapsed_seconds']<spec['production_seconds_max']
assert read('output/STARTED.json')['gate_sha256']==sha('INDEPENDENT_GATE.json')
cfg=read('inputs/central_bindings.json')['config']; D=tuple(map(F,cfg['D']))
summary={}; records=0
for engine in ('primary','independent'):
    summary[engine]={}; endpoints={}
    h=F(2,spec['steps'][engine]); n=-(-D[1]//h)
    expected_indices=[j for j in range(n) if (j+1)*h>=D[0] and j*h<=D[1]]
    for label,mass in spec['mass_points'].items():
        ref=result['source_records'][engine][label]
        name='output/'+ref['path']; assert sha(name)==ref['sha256']
        rec=read(name); records+=1
        assert rec['engine']==engine and rec['label']==label
        assert F(rec['mu_exact'])==F(mass)
        assert rec['cells']==n and rec['steps']==spec['steps'][engine]
        assert rec['all_cell_checks_pass'] is True
        assert rec['max_picard_iterations']>0
        assert rec['elapsed_seconds']<spec['flow_seconds_max']
        assert rec['source_sha256']==sha('engine/'+engine+'_interval.py')
        rows=rec['event_cover']; assert [r['index'] for r in rows]==expected_indices
        last=D[0]; tight={}
        for row in rows:
            lo,hi=F(row['lo_exact']),F(row['hi_exact']); j=row['index']
            assert lo==last and lo==max(D[0],j*h) and hi==min(D[1],(j+1)*h)
            assert lo<=hi; last=hi
            for key in ('R0','f'):
                value=interval(row[key])
                tight[key]=value if key not in tight else (min(value[0],tight[key][0]),max(value[1],tight[key][1]))
        assert last==D[1]
        event={key:interval(rec['event'][key]) for key in ('R0','f')}
        for key in event: assert contained(tight[key],event[key])
        endpoints[label]=event
        eta=F(spec['eta'])
        at100=add(event['R0'],mul(event['f'],(eta/2,eta/2)))
        uniform=add(event['R0'],mul(event['f'],(F(0),eta/2)))
        derived=result['engines'][engine]['derived'][label]
        assert at100==interval(derived['R_eta100'])
        assert uniform==interval(derived['R_eta_uniform'])
        summary[engine][label]={'R0':list(map(float,event['R0'])),'f':list(map(float,event['f'])),'R100':list(map(float,at100)),'uniform_R':list(map(float,uniform)),'event_rows':len(rows)}
    e=result['engines'][engine]
    a=endpoints['low']['R0'][0]>0 and endpoints['low']['f'][0]>0
    b=interval(e['derived']['low']['R_eta_uniform'])[0]>0 and interval(e['derived']['high']['R_eta_uniform'])[1]<0
    c=interval(e['derived']['finite_lower']['R_eta100'])[0]>0 and interval(e['derived']['high']['R_eta100'])[1]<0
    assert a==e['all_finite_lower_witness'] and b==e['uniform_strip_endpoints'] and c==e['finite_displacement']
    assert a and b and c
assert records==6
assert result['classification']=='FINITE_RESPONSE_AND_GLOBAL_BRANCH'
old=tuple(map(F,read('inputs/narrowing_result.json')['mu_bracket']))
gap=F(spec['mass_points']['finite_lower'])-old[1]
assert gap==F(3,16000000)==F(result['strict_displacement_lower_exact'])
assert list(map(F,result['eta100_mu_bracket']))==[F('-164/125000'),F('-131/100000')]
assert result['all_finite_branch_numerical_premise_pass'] and result['quantitative_pass']
controls=result['controls']; assert len(controls)==3
assert controls[0]['pass'] is True
assert controls[1]['rejected_by']=='DENOMINATOR_NONZERO'
assert controls[2]['rejected_by']=='EVENT_GAP'
assert time.monotonic()-started<180
print(json.dumps({'status':'INDEPENDENT_EXACT_RECONSTRUCTION_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner_result_sha256':sha('output/RESULT.json'),'execution_sha256':sha('EXECUTION_finite100.json'),'audit_script_sha256':sha('audit_finite.py'),'gate_sha256':sha('INDEPENDENT_GATE.json'),'source_hashes_checked':len(bindings),'copied_sources_checked':15,'flow_records_checked':records,'all_exact_predicates_reconstructed':True,'strict_displacement_lower_exact':str(gap),'summary_approximate_only':summary,'elapsed_seconds':time.monotonic()-started,'limitation':'Event hull arithmetic and stored qualification records audited; original interval-ODE validity inherited, no ODE reintegration.'},indent=2))
