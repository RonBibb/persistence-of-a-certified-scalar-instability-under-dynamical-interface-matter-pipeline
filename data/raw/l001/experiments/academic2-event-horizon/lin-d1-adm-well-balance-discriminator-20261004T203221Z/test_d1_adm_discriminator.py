#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,math
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;SPEC=importlib.util.spec_from_file_location('adm_target',HERE/'d1_adm_discriminator.py');assert SPEC and SPEC.loader
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
def fields():
    x=np.linspace(1.,math.e,7);r=np.linspace(0.,1.,5);shape=(7,5);psi=np.ones(shape);q=np.zeros((*shape,9));q[:,:,3]=1;q[:,:,6]=1
    return {'x':x,'r':r,'psi':psi,'a':np.zeros(shape),'b':np.zeros(shape),'c':np.zeros(shape),'phi':np.ones(shape)*.1,'alpha':psi.copy(),'q':q}
def metric(z,r,psi,a,b,c,phi,cr,cz,m,**kw): return {n:psi.copy() for n in ('zz','radial','transverse','zr')}
def scalar(z,r,psi,a,b,c,phi,m,**kw): return phi+psi
def test_contract(): assert M.A_GRIDS==((65,121),(97,181),(129,241)) and M.B_NX==(129,193,257,385,513) and M.GATE==5e-5
def test_background_subtraction_zero(): assert M.difference_record(fields(),fields(),metric,scalar)['maximum_normalized']==0.
def test_generic_response_nonzero():
    base=fields();candidate={k:(v.copy() if isinstance(v,np.ndarray) else v) for k,v in base.items()};candidate['psi']*=1.000001
    assert M.difference_record(candidate,base,metric,scalar)['maximum_normalized']>1e-12
def test_order():
    ratio=(257-1)/(129-1);assert math.isclose(M.observed_order(1.,ratio**-4,129,257),4.,abs_tol=1e-14)

