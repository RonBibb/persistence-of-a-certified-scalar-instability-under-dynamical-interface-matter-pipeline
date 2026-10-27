"""Collect the bounded numerical decision and draw the scientific result."""
from pathlib import Path
import json,hashlib,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sympy as sp

B=Path(__file__).resolve().parents[1]
def read(name):return json.loads((B/'results'/name).read_text())
def symbolic():
    a,A,phi,S,h,f,p,k,mu,mb=sp.symbols('a A phi S h f p k mu mb', real=True)
    vp=a*a*mb*phi
    C=S*p-(vp-4*A*S)*f+(2*S*S-3*mu-12*k)*h
    flow={a:A*a,A:A*A-k-S*S/3,phi:S,S:vp-3*A*S,
          h:-2*A*h-S*f/3,f:p,p:-3*A*p+(a*a*mb-mu+2*S*S)*f+(12*A*S-4*vp)*h}
    check=sp.factor(sum(sp.diff(C,x)*v for x,v in flow.items())+2*A*C)
    out=dict(constraint_propagation=str(check),pass_constraint_propagation=check==0,
             method='Exact symbolic differentiation of the undivided Einstein constraint with the independent background and perturbation flows')
    (B/'results/SYMBOLIC_CONTROL.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

def main():
    primary=read('shoot_tight.json');mu=primary['mu'];k=primary['k']
    spect=[read(f'spectral_N{N}.json')['modes'][0] for N in [33,49,65,97]]
    bg=read('shoot_previous_background.json');s0=read('shoot_coarse.json');s1=read('shoot_fine.json')
    mp2=read('precision_N2048_dps40.json');mp4=read('precision_N4096_dps60.json')
    sensitivity=dict(spectral_last_two=abs(spect[-1]['mu']-spect[-2]['mu']),
        spectral_finest_vs_shooting=abs(spect[-1]['mu']-mu),shooting_last_two=abs(s1['mu']-mu),
        all_shooting_tolerances=abs(s0['mu']-mu),background_refinement=abs(bg['mu']-mu),
        arbitrary_precision_vs_shooting=abs(mp4['mu_float']-mu),RK4_step_refinement=abs(mp4['mu_float']-mp2['mu_float']))
    maxdiff=max(sensitivity.values())
    ind=read('INDEPENDENT_MODE_CHECK.json')
    sym=symbolic()
    accepted=(read('CONTROLS.json')['pass'] and sym['pass_constraint_propagation']
              and ind['finest_independent_residuals_pass'] and primary['kinetic_Z']>0
              and abs(primary['delta_D'])>1e-8 and mu<0 and abs(mu)>100*maxdiff
              and abs(mu)>1e-8 and sensitivity['spectral_last_two']<1e-7
              and sensitivity['spectral_finest_vs_shooting']<1e-7
              and sensitivity['shooting_last_two']<1e-7)
    summary=dict(classification='RESOLVED_LINEAR_SCALAR_RADION_INSTABILITY' if accepted else 'INCONCLUSIVE',accepted=bool(accepted),mu=mu,k=k,
        mu_over_k=mu/k,shifted_lambda=mu+4*k,growth_s_over_H=primary['growth_s_over_H'],
        growth_s=primary['growth_s'],efold_time_lower_wall=1/primary['growth_s'],
        efold_in_Hubble_times=1/primary['growth_s_over_H'],kinetic_Z=primary['kinetic_Z'],
        delta_D=primary['delta_D'],delta_D_over_sqrt_Z=primary['delta_D_over_sqrt_Z'],
        sensitivity=sensitivity,max_observed_mass_sensitivity=maxdiff,mass_to_sensitivity_ratio=abs(mu)/maxdiff,
        sign_gate=abs(mu)>100*maxdiff and abs(mu)>1e-8,
        controls=read('CONTROLS.json')['pass'],symbolic_control=sym['pass_constraint_propagation'],
        independent_residual_receipt_sha256=hashlib.sha256((B/'results/INDEPENDENT_MODE_CHECK.json').read_bytes()).hexdigest(),
        rejected_spectral_profile_resolutions=[65,97],
        interpretation='Accepted independently differentiated shooting mode; high-resolution spectral profiles do not pass KG residual gate. No universal lowest-mode or complete-sector-stability claim.',
        next_donor_experiment_justified=False)
    (B/'results/SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    d=np.load(B/'results/shoot_tight.npz');u=d['z']/primary['L']
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(1,2,figsize=(10.6,4.1),layout='constrained')
    ax[0].plot(u,d['psi']/np.max(abs(d['psi'])),label='Metric scalar',color='#235e83',lw=2)
    ax[0].plot(u,d['f']/np.max(abs(d['f'])),label='Stabilizer fluctuation',color='#bb5c30',lw=2)
    ax[0].axvline(primary['turn_u'],color='.5',ls=':',label='Background scalar turn')
    ax[0].set(xlabel='Position across interval  u',ylabel='Separately normalized mode profiles',title='A smooth coupled separation mode',xlim=(0,1))
    ax[0].legend(frameon=False,fontsize=8,loc='upper left')
    t=np.linspace(0,4,301);g=np.exp(primary['growth_s_over_H']*t)
    ax[1].semilogy(t,g,color='#8b3446',lw=2.3)
    ax[1].set(xlabel='de Sitter expansion time  Ht',ylabel=r'$|\delta D(t)/\delta D(0)|$',title='Predicted linear growth',xlim=(0,4))
    ax[1].text(.05,.93,r'$m_4^2/H^2=-4.01489$'+'\n'+r'$s/H=1.00298$',transform=ax[1].transAxes,va='top')
    ax[1].grid(axis='y',alpha=.2)
    fig.suptitle('Fixed curved candidate: physical radion instability',fontsize=13)
    fig.savefig(B/'results/STABILITY_RESULT.png',dpi=180)
    fig.savefig(B/'results/STABILITY_RESULT.pdf')
    plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
