"""Leased Linux saved-file size projection only; no numerical flow."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('archive_reader_runner',ROOT/'runner.py')
r=importlib.util.module_from_spec(s);sys.modules[s.name]=r;s.loader.exec_module(r)
try:
    assert sys.platform=='linux';signal.alarm(120)
    cpu,occupied=r.lease.acquire();r.verify();rows={}
    for name in ('primary','independent'):
        path=ROOT/('PROBE_'+name+'.json');data=r.read(path);size=path.stat().st_size
        projected=Fraction(size*data['projected_full_cells'],data['cells'])
        rows[name]={'measured_bytes':size,'sample_cells':data['cells'],
            'projected_full_cells':data['projected_full_cells'],'linear_bytes_projection_exact':str(projected),
            'linear_bytes_projection_ceiling':-((-projected.numerator)//projected.denominator)}
    total=sum(Fraction(x['linear_bytes_projection_exact']) for x in rows.values())
    result={'engines':rows,'combined_projection_exact_bytes':str(total),
        'combined_projection_ceiling_bytes':-((-total.numerator)//total.denominator),
        'scope':'Linear serialized JSON size projection, not measured full-domain size or RAM; streaming required under2GiB.',
        'production_terminal_seconds':r.read(ROOT/'production_TERMINAL.json')['seconds'],
        'audit_terminal_seconds':r.read(ROOT/'audit_TERMINAL.json')['seconds']}
    r.put('ARCHIVE_READOUT.json',result);print(json.dumps(result),flush=True)
finally:
    signal.alarm(0)
    for f in r.lease.handles:f.close()
