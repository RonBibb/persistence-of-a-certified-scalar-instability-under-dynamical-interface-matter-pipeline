"""One saved-data attribution, atomic per-case outputs, no certificate rerun."""
from width_runtime_exact import *
import attribution_exact as a
import signal,traceback,argparse
STOP=False
def request_stop(signum,frame):
    global STOP
    STOP=True
def case(name,g,func):
    path=ROOT/'raw'/f'{name}.json';seal=ROOT/'checkpoints'/f'{name}.json'
    if seal.exists():
        meta=rec.read(seal);assert meta['guard']==g and meta['sha256']==rec.sha(path)
        return rec.read(path)
    if path.exists():raise RuntimeError('Unsealed case exists; no implicit overwrite')
    progress('RUNNING',guard=g,case=name)
    start=time.monotonic();result=func()
    result['wall_seconds']=time.monotonic()-start
    rec.atomic(path,result,True)
    rec.atomic(seal,{'guard':g,'case':name,'sha256':rec.sha(path),'utc':rec.now()},True)
    print(json.dumps({'case':name,'wall_seconds':result['wall_seconds'],'sha256':rec.sha(path)}),flush=True)
    if STOP:raise KeyboardInterrupt('Stop requested after completed diagnostic case')
    return result

def run(g):
    if (ROOT/'TERMINAL.json').exists():raise RuntimeError('Terminal task cannot be rerun')
    if (ROOT/'FAILURE.json').exists():raise RuntimeError('Preserved failure requires explicit operational recovery')
    ledgers={}
    for bits in CFG['precisions']:
        ledgers[str(bits)]=case(f'channels-{bits}',g,lambda b=bits:a.channels(b,g))
    interim={'utc':rec.now(),'guard':g,'producer_root':str(ROOT),'status':'CHANNEL_LEDGER_VERIFIED_ATTRIBUTION_PENDING',
       'ledgers':ledgers,'all_channel_radius_closures_exact':all(v['radius_closure_exact'] for d in ledgers.values() for v in d['terms']),
       'not_a_physical_error_partition':True}
    if not (ROOT/'INTERIM_CHANNEL_LEDGER.json').exists():
        rec.atomic(ROOT/'INTERIM_CHANNEL_LEDGER.json',interim,True)
        rec.atomic(SHARED/'STATIC_INTERIM_CHANNEL_LEDGER.json',interim,True)
    controls={};inventories={};cases={}
    for bits in CFG['precisions']:
        key=str(bits)
        controls[key]=case(f'control-{bits}',g,lambda b=bits:a.validate_baseline(b,g))
        inventories[key]=case(f'inventory-{bits}',g,lambda b=bits:a.inventory(b,g))
        for mode in CFG['representation_order']:
            name=f'{bits}-{mode}'
            cases[name]=case(name,g,lambda b=bits,m=mode:a.mean_value_case(b,m,g))
    eligible=all(x['all_passed'] for x in controls.values()) and all(x['all_passed'] for x in cases.values())
    outcome={}
    for bits in CFG['precisions']:
        rows=[]
        for mode in CFG['representation_order']:
            v=cases[f'{bits}-{mode}']['center_corrections'][2]
            rows.append({'mode':mode,'original_halfwidth':v['original']['halfwidth'],
                 'alternate_halfwidth':v['mean_value_enclosure']['halfwidth'],
                 'intersection_halfwidth':v['intersection']['halfwidth'],'removable_fraction_lower':v['removable_fraction_lower']})
        best=max(rows,key=lambda row:Q(row['removable_fraction_lower']))
        outcome[str(bits)]={'ordered_comparison':rows,'best_equivalent_bound':best,
            'dominance_passed':Q(best['removable_fraction_lower'])>=Q(CFG['dominance_rule']['threshold'])}
    dominant=eligible and all(v['dominance_passed'] for v in outcome.values())
    classification='C6_RESIDUAL_WIDTH_DOMINANT_SOURCE_IDENTIFIED' if dominant else 'C6_RESIDUAL_WIDTH_MULTISOURCE_UNRESOLVED'
    if not eligible:classification='C6_RESIDUAL_WIDTH_ATTRIBUTION_INCOMPLETE'
    origin_ledger=[
      {'category':'source and root uncertainty','status':'RIGOROUS_MIXED_INPUT_ENCLOSURES','evidence':'Sealed endpoint and primitive jet boxes; retained in every whole-box analytic derivative. Root/source versus accumulated IVP/wrapping is not separately recoverable.','additive_physical_share':None},
      {'category':'validated integration and spatial Taylor remainder','status':'UNRESOLVED_CUMULATIVE_CONTRIBUTION','evidence':'Stored local fifth-remainder bounds are rigorous for their saved cells only. Missing intervening cells are not recomputed.','additive_physical_share':None},
      {'category':'endpoint event localization','status':'RIGOROUS_RAW_STATE_UPPER_BOUND','evidence':'Event tube RHS bound times halfwidth(D); overlaps source and integration uncertainty and is not automatically a residual contribution.','additive_physical_share':None},
      {'category':'canonical epsilon Taylor remainder','status':'RIGOROUS_COEFFICIENT_UPPER_BOUND','evidence':'Eight saved epsilon-series coefficient remainder bounds, distinct from spatial integration error.','additive_physical_share':None},
      {'category':'high jet and algebraic propagation','status':'RIGOROUS_EQUIVALENT_RANGE_BUDGETS','evidence':'Three ordered representations with full-box analytic mean-value derivatives, every nonlinear interaction retained within those derivative enclosures.','additive_physical_share':None},
      {'category':'interval dependency and wrapping','status':'ALGEBRAIC_REMOVABLE_WIDTH_BOUNDED_IVP_WRAPPING_UNRESOLVED','evidence':'Intersection widths compare rigorous equivalent endpoint evaluations. They bound avoidable algebraic enclosure width, not physical error. Earlier IVP wrapping remains mixed.','additive_physical_share':None}]
    result={'utc':rec.now(),'guard':g,'classification':classification,'joint_classification':False,
       'all_local_controls_passed':eligible,'primary_coordinate_index':2,'primary_comparison':outcome,
       'dominant_enclosure_mechanism':'avoidable high-jet/algebraic interval dependency' if dominant else None,
       'origin_contribution_ledger':origin_ledger,'interim_ledger_sha256':rec.sha(ROOT/'INTERIM_CHANNEL_LEDGER.json'),
       'case_files':{p.name:rec.sha(p) for p in sorted((ROOT/'raw').glob('*.json'))},
       'original_certificate_still_incomplete':True,'no_IVP_advance_or_C6_root_test':True,
       'enabling_value':{
           'consumer':'Lin Initial physical C6 initial-data construction for the broader collapse/horizon effort',
           'next_certificate_premise':'A valid narrow enclosure of the SAME center residual, with all source/event/IVP uncertainty retained, before the existing five-variable root-inclusion gate can be revisited under new authority.',
           'delivered_here':'A bounded attribution ledger and equivalent-range diagnostics identifying which enclosure stage can or cannot support that premise.',
           'not_delivered':'No new root certificate, lapse/inverse-map certificate, C6 datum, evolution, or horizon result.',
           'standalone_novelty':'No first-in-literature claim assessed; enabling numerical-proof value is distinct from standalone novelty.'}}
    rec.atomic(ROOT/'RESULT.json',result,True)
    return result

def finish(g,result):
    # Independent local readback uses rational interval endpoints and stored terms.
    checks={'sources_and_inputs_unchanged':guard()==g,'resource_released':not rec.read(ROOT/'RESOURCE_RELEASED.json')['active']}
    for path in sorted((ROOT/'checkpoints').glob('*.json')):
        cp=rec.read(path);raw=ROOT/'raw'/f"{cp['case']}.json"
        checks[path.stem+'_hash']=cp['guard']==g and cp['sha256']==rec.sha(raw)
    for bits in CFG['precisions']:
        d=rec.read(ROOT/'raw'/f'channels-{bits}.json')
        for v in d['terms']:
            checks[f'linear_radius_closure_{bits}_{v["coordinate"]}']=sum((Q(x) for x in v['linear_radius_terms']),Q(0))+Q(v['rounding_and_representation_excess'])==Q(v['represented_center_correction']['halfwidth'])
        for mode in CFG['representation_order']:
            d=rec.read(ROOT/'raw'/f'{bits}-{mode}.json')
            for typ in ('residuals','center_corrections'):
                for v in d[typ]:
                    total=sum((Q(x) for x in v['input_terms']),Q(0))+Q(v['point_evaluation_halfwidth'])+Q(v['outward_radius_excess'])
                    checks[f'mean_value_closure_{bits}_{mode}_{typ}_{v["index"]}']=total==Q(v['mean_value_enclosure']['halfwidth'])
                    original=Q(v['original']['halfwidth']);new=Q(v['intersection']['halfwidth'])
                    checks[f'removable_fraction_{bits}_{mode}_{typ}_{v["index"]}']=Q(v['removable_fraction_lower'])==max(Q(0),1-new/original)
    audit={'utc':rec.now(),'guard':g,'checks':checks,'all_passed':all(checks.values()),'scope':'Local exact accounting/integrity readback; independent Initial audit remains required.'}
    rec.atomic(ROOT/'LOCAL_AUDIT.json',audit,True)
    classification=result['classification'] if audit['all_passed'] else 'C6_RESIDUAL_WIDTH_ATTRIBUTION_INCOMPLETE'
    rec.atomic(ROOT/'TERMINAL.json',{'utc':rec.now(),'guard':g,'classification':classification,'result_sha256':rec.sha(ROOT/'RESULT.json'),
       'local_audit_sha256':rec.sha(ROOT/'LOCAL_AUDIT.json'),'resource_release_sha256':rec.sha(ROOT/'RESOURCE_RELEASED.json'),'joint_classification':False},True)
    packet={'utc':rec.now(),'guard':g,'producer_root':str(ROOT),'classification':classification,
       'joint_classification':False,'artifacts':{str(p.relative_to(ROOT)):rec.sha(p) for p in sorted(ROOT.rglob('*.json')) if '/progress/' not in str(p) and '/checkpoints/' not in str(p)},
       'no_certificate_rerun':True,'resources_released':True,'independent_initial_audit_pending':True}
    rec.atomic(ROOT/'STATIC_SUBMISSION.json',packet,True);rec.atomic(SHARED/'STATIC_SUBMISSION.json',packet,True)
    progress('TERMINAL',guard=g,classification=classification)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','run']);args=ap.parse_args()
    ctx.threads=1
    if args.action=='freeze':print(json.dumps({'guard':freeze()}))
    else:
        g=guard();held,ident=acquire();start=time.monotonic();result=None
        signal.signal(signal.SIGINT,request_stop);signal.signal(signal.SIGTERM,request_stop)
        try:result=run(g)
        except KeyboardInterrupt:
            progress('STOPPED',guard=g);raise
        except BaseException as exc:
            rec.atomic(ROOT/'FAILURE.json',{'utc':rec.now(),'guard':g,'error':str(exc),'traceback':traceback.format_exc()},True)
            progress('FAILED_CLOSED',guard=g,error=str(exc));raise
        finally:release(held,ident,start)
        if result is not None:finish(g,result)
