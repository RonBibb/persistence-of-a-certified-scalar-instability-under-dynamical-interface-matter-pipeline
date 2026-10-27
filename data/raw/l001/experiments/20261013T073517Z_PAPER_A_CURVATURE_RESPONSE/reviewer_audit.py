"""Independent exact terminal consequence audit; imports no owner implementation."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

P=Path(__file__).resolve().parent
L=P.parents[1]
def read(p): return json.loads(p.read_text())
gate=read(P/'INDEPENDENT_GATE.json')
for name,digest in gate['frozen_hashes'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest
manifest=read(P/'SOURCE_BINDINGS.json')
for name,digest in manifest['sources'].items():
    assert hashlib.sha256((L/name).read_bytes()).hexdigest()==digest
meta=read(P/'RUN_METADATA.json'); output=read(P/'RESULT.json')
assert meta['returncode']==0 and (P/'RUN_STDERR.txt').read_bytes()==b''
assert meta['output_sha256']==hashlib.sha256((P/'RESULT.json').read_bytes()).hexdigest()
assert meta['gate_sha256']==hashlib.sha256((P/'INDEPENDENT_GATE.json').read_bytes()).hexdigest()

class I:
    def __init__(self,l,u=None): self.l=F(l); self.u=F(l if u is None else u); assert self.l<=self.u
    def __add__(self,b):
        b=b if isinstance(b,I) else I(b)
        return I(self.l+b.l,self.u+b.u)
    __radd__=__add__
    def __neg__(self): return I(-self.u,-self.l)
    def __sub__(self,b): return self+-b
    def __mul__(self,b):
        b=b if isinstance(b,I) else I(b)
        v=[self.l*b.l,self.l*b.u,self.u*b.l,self.u*b.u]
        return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=b if isinstance(b,I) else I(b)
        assert b.u<0 or b.l>0
        return self*I(1/b.u,1/b.l)
    def sq(self): return I(0 if self.l<=0<=self.u else min(self.l**2,self.u**2),max(self.l**2,self.u**2))
    def pair(self): return self.l,self.u
def from_record(r): return I(*r['exact_bounds'])
src=read(L/'experiments/research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01/RESULT.json')
mod=read(L/'experiments/research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01/BINDINGS.json')['exact_model']
g,la,m,v=[F(mod[k]) for k in ('GAMMA_Q','LAMBDA_A_Q','M2_Q','V0_Q')]
a=from_record(src['neighborhood']['newton_image']); x=a-I(v)
H=-(I(la)+g*x.sq()/2)/6; S=g*x/2
k=H.sq()-I(1)-S.sq()/12+m*a.sq()/12
direct=-g*H*x/3-g*g*x/24+m*a/6
# Expanded independently in powers of a from g*la*x/18+g^2*x^3/36-g^2*x/24+m*a/6.
coeff=[-g*la*v/18-g*g*v**3/36+g*g*v/24,
       g*la/18+g*g*v*v/12-g*g/24+m/6,
       -g*g*v/12,g*g/36]
assert list(map(F,output['results']['derivative_polynomial_coefficients']))==coeff
poly=I(0)
for c in reversed(coeff): poly=poly*a+I(c)
ka=I(max(direct.l,poly.l),min(direct.u,poly.u))
ap=from_record(src['neighborhood']['response']['da_dlambda_b'])
dp=from_record(src['neighborhood']['response']['dD_dlambda_b'])
kl=ka*ap; rl=12*kl; rd=rl/dp
expected={'a':a,'k':k,'dk_da_direct':direct,'dk_da_polynomial':poly,'dk_da':ka,
          'dk_dlambda_b':kl,'dR_lower_dlambda_b':rl,'dR_lower_dD':rd,
          'full_endpoint_delta_k':kl/F(500000),'full_endpoint_delta_R_lower':rl/F(500000)}
for name,interval in expected.items():
    saved=output['results'][name]
    assert from_record(saved).pair()==interval.pair(),name
    lo,hi=map(F,saved['outward_decimal_12'])
    assert lo<=interval.l<=interval.u<=hi,name
    assert interval.l-lo<F(1,10**12) and hi-interval.u<F(1,10**12),name
assert k.l>0 and ka.l>0 and ap.l>0 and dp.u<0 and kl.l>0 and rd.u<0
assert {x['control'] for x in output['controls']}=={'A_RESPONSE_POSITIVE','D_RESPONSE_NEGATIVE','LOWER_NORMALIZATION','MODEL_EXACT','IMAGE_INSIDE_ROOT_BOX','DERIVATIVE_IDENTITY'}
assert all(x['control']==x['rejected_by'] for x in output['controls'])
print(json.dumps({'status':'PASS','exact_output_enclosures_reconstructed':len(expected),
 'polynomial_coefficients_independently_expanded':True,'all_outward_decimals_valid':True,
 'frozen_sources_and_execution_hashes_match':True,'six_recorded_control_rejections_match':True,
 'owner_result_sha256':meta['output_sha256']},indent=2))
