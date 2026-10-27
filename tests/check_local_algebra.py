"""Bounded algebra checks of revised explanations; no source execution or interval modules."""
from pathlib import Path
import json
import sympy as S
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,help='Optional explicit report destination')
args=parser.parse_args()
sigma,D,T,Tp,Gamma,Sc,wall_R,f,fp,fpp,B,H,m,mu,E,A=S.symbols('sigma D T Tp Gamma Sc wall_R f fp fpp B H m mu E A',nonzero=True)
checks={}
p=(Sc-T*fp+Tp*f)/D
An=1-2*T**2/D
beta=Gamma/(2*An)-2*sigma*T*Tp/(D*An)
g=-wall_R/(2*An)+2*sigma*T*Sc/(D*An)
raw=2*sigma*(fp+2*T*p)-Gamma*f-wall_R
reduced=-sigma*fp+beta*f-g
checks['Q7_constraint_substitution_outward_Robin']=S.simplify((raw+2*An*reduced).subs(sigma**2,1))==0
raw_scalar=fpp+4*H*fp-(m-mu*E**2+2*T**2)*f-B*p-S.symbols('Sg')
a=-4*H-B*T/D; V=m-mu*E**2+2*T**2+B*Tp/D; F=-S.symbols('Sg')-B*Sc/D
checks['Q3_reduced_scalar_source_sign']=S.simplify(-raw_scalar-(-fpp+a*fp+V*f-F))==0
n,h=S.symbols('n h',positive=True)
r=-6*n*h
checks['Q2_tracefree_divisor']=S.expand(r*(r-h)-6*h*h*n*(6*n+1))==0
# Neutral weights follow from sigma shift, dr_tau=Lambda^-1 dr_0 and the fixed-rho density convention.
w={'dr':-1,'q':-1,'alpha':2,'exp_lambda':3,'Hwall':2,'barA':4,'barp':4,'Pi':3,'pwall_input':3,'Pq':4,'wall_pressure':-2,'w':0,'derivative_r':1}
checks['G2_true_density_to_bar_density']=w['Pi']-w['q']==w['barp']
checks['G2_mean_width_constraint']=w['Pq']==w['barA']
scales={'bulk_square':w['dr']+w['alpha']-2*w['exp_lambda']+2*w['barp'],
'wall_square':w['alpha']-w['exp_lambda']-w['Hwall']+2*w['pwall_input'],
'bulk_remainder':w['dr']+2*w['derivative_r']+w['alpha'],
'pressure_endpoint':w['alpha']+w['exp_lambda']+w['wall_pressure']}
checks['G3_all_form_terms_common_weight']=set(scales.values())=={3}
u=w['alpha']/2+w['derivative_r']; Eu=w['dr']+2*u; Arad=w['dr']+2*(u+w['derivative_r'])
checks['G2_radial_gap_and_h_ratio']=Eu==3 and Arad==5 and Arad-Eu==2
out={'scope':'Local exact algebra and homogeneity checks only; not a proof of nonlinear source estimates, inherited inverse, numerical premises or independent scientific review.','checks':checks,'passed':all(checks.values()),'form_scaling_exponents':scales,'radial_energy_exponents':{'E_u':Eu,'mathscr_A':Arad},'source_audit':'The article Lemma C.1 gives the analytical factorwise argument; these checks do not prove its estimates.','producer_imports':0,'new_integrations':0}
if args.output:
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2));assert out['passed']
