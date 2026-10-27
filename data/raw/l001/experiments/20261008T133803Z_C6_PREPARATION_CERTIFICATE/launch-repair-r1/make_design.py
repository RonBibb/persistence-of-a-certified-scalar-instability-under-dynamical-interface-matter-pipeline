"""Create a prospective exact design from old published centers only."""
from common import *
import mpmath as mp
from inherited.series import bounds
mp.mp.dps=200
old=loadin('native_old'); candidate=loadin('c6_p100'); dense=loadin('c6_dense100')
seed=loadin('native_seed'); eps=Q(CFG['epsilon'])
center=[Q(old['A0'])+Q(candidate['x'][0])-eps]
center += [Q(old['fifth_jet_coefficients'][i])+Q(candidate['delta_c5_c7'][i]) for i in (0,1)]
center += [Q(candidate['delta_c5_c7'][i]) for i in (2,3)]
J=mp.matrix(loadin('c6_matrix100')['J5']); D=mp.mpf(seed['D'])
S=[mp.mpf(1),mp.factorial(5)/D**5,mp.factorial(5)/D**5,mp.factorial(7)/D**7,mp.factorial(7)/D**7]
A=[mp.mpf(dense['A0']),mp.mpf(dense['end'][0])]
Rinv=[mp.mpf(1),mp.exp(4*A[0]),mp.exp(4*A[1]),mp.exp(6*A[0]),mp.exp(6*A[1])]
inverse=J**-1
C=[[str(Q(mp.nstr(S[i]*inverse[i,j]*Rinv[j],90))) for j in range(5)] for i in range(5)]
obj={'created_utc':rec.now(),'no_new_physical_outcome_evaluated':True,
     'center':list(map(str,center)),'radii':CFG['box_halfwidths'],'preconditioner':C,
     'center_origin':'Old native member plus sealed p100 C6 adjustments; total physical jet coordinates.',
     'preconditioner_origin':'Archived numeric J5 only, with the declared coordinate and proper-clock changes.',
     'input_hashes':{k:rec.sha(inputs()[k]) for k in ('native_old','native_seed','c6_p100','c6_dense100','c6_matrix100')}}
rec.atomic(ROOT/'DESIGN.json',obj,True)
print(json.dumps({'design_sha256':rec.sha(ROOT/'DESIGN.json'),'center_approx':[float(x) for x in center],
                  'radii':CFG['box_halfwidths'],'new_outcome':False}))
