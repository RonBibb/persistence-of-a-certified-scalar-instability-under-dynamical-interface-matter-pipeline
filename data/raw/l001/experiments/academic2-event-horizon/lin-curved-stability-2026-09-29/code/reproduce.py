"""Explicit, non-overwriting replay in this successor's replays/ namespace."""
from pathlib import Path
import argparse,contextlib,datetime,hashlib,importlib.util,json,os

BASE=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location('replay_'+name,BASE/'code'/f'{name}.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');args=p.parse_args()
    if not args.execute:p.error('Use --execute to run the bounded replay; original results are never overwritten.')
    for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
    solver=load('stability');solver.authenticate()
    extra=json.loads((BASE/'preflight/ADDITIONAL_BINDINGS.json').read_text())
    for name,want in extra['files'].items():
        if hashlib.sha256((BASE/name).read_bytes()).hexdigest()!=want:raise RuntimeError('Additional binding mismatch: '+name)
    out=BASE/'replays'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    (out/'results').mkdir(parents=True,exist_ok=False);(out/'logs').mkdir()
    solver.BASE=out
    if not solver.controls()['pass']:raise RuntimeError('Replay controls failed')
    spectra=[solver.spectral(n) for n in [33,49,65,97]]
    mu=spectra[-1]['modes'][0]['mu']
    for label,tol in [('shoot_coarse',2e-9),('shoot_fine',2e-11),('shoot_tight',2e-13)]:solver.shooting(mu,tol,label)
    prior=solver.PARENT/'proper-shooting/narrow-gap/results/collocation/root0_stage1'
    solver.shooting(mu,2e-13,'shoot_previous_background',prior)
    precision=load('precision_check');precision.B=out
    for n,dps in extra['precision_cases']:precision.run(n,dps)
    verifier=load('independent_mode_check')
    verifier.PROFILE=out/'results/shoot_tight.npz';verifier.METADATA=out/'results/shoot_tight.json';verifier.OUTPUT=out/'results/INDEPENDENT_MODE_CHECK.json'
    with (out/'logs/independent_check.log').open('w') as log,contextlib.redirect_stdout(log):verifier.main()
    summary=load('summarize');summary.B=out
    with (out/'logs/summary.log').open('w') as log,contextlib.redirect_stdout(log):summary.main()
    receipt=dict(source_directory=str(BASE),output_directory=str(out),source_contract_sha256=hashlib.sha256((BASE/'CONTRACT.json').read_bytes()).hexdigest(),classification=json.loads((out/'results/SUMMARY.json').read_text())['classification'])
    (out/'REPLAY_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
