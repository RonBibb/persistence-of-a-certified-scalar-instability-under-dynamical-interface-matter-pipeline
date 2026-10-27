"""Single source/input freeze. No scientific outcomes evaluated."""
from common import *
ctx.threads=1
if (ROOT/'BINDINGS.json').exists():raise RuntimeError('Already frozen')
records={k:{'path':str(v),'sha256':rec.sha(v),'bytes':v.stat().st_size} for k,v in inputs().items()}
native=loadin('native_binding');c4=loadin('c4_binding');result=loadin('source_result')
assert native['model_exact']==c4['model_exact']
assert result['newton']['nonempty'] and result['newton']['subset'] and result['newton']['tenfold_contraction']
assert loadin('source_flow_result',True)['cover']
assert loadin('c6_result')['classification']=='NEW_PHYSICAL_C6_MEMBER_NUMERICALLY_ADMITTED'
trans=[]
binding=loadin('source_binding')
for name,digest in sorted((binding['sources']|binding['inputs']).items()):
    q=Path(name)
    if platform.system()!='Linux' and name.startswith('/media/psf/Home/'):
        q=Path('/Users/ronbibb')/q.relative_to('/media/psf/Home')
    assert rec.sha(q)==digest,name
    trans.append({'path':str(q),'sha256':digest})
b={'utc':rec.now(),'sources':{n:rec.sha(ROOT/n) for n in sourcelist()},
   'inputs':records,'source_transitive':trans,'runtime':runtime(),
   'model_exact':native['model_exact'],'no_new_physical_outcome_before_freeze':True,
   'new_scope':'Actual canonical C7 plus five-variable C6 physical preparation; source uncertainty retained.'}
rec.atomic(ROOT/'BINDINGS.json',b,True)
rec.atomic(ROOT/'FREEZE.json',{'utc':rec.now(),'bindings_sha256':rec.sha(ROOT/'BINDINGS.json')},True)
for n in sourcelist():(ROOT/n).chmod(0o444)
print(json.dumps({'status':'FROZEN','guard':rec.sha(ROOT/'BINDINGS.json'),'inputs':len(records),'source_transitive':len(trans)}))
