#!/usr/bin/env python3
import importlib.util,math
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent;S=importlib.util.spec_from_file_location('gh',H/'d1_gh_discriminator.py');assert S and S.loader;M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class Fake:
 def __init__(self,z,r):self.z=np.asarray(z);self.r=np.asarray(r)
 def acceleration(self,t,q,v):return np.asarray(q)+np.asarray(v)+t,{'finite':True}
def test_contract():assert M.A_GRIDS==((65,121),(97,181),(129,241)) and M.B_NX==(65,97,129,193,257) and M.GATE==1e-4
def test_background_is_exactly_stationary():
 q=np.ones((2,3,1));v=np.zeros_like(q);base={(2,3):{'q':q,'v':v}};R=M.wb_rhs_class(Fake,base)(np.arange(2),np.arange(3));a,_=R.acceleration(0.,q,v);assert np.count_nonzero(a)==0
def test_generic_response_remains():
 q=np.ones((2,3,1));v=np.zeros_like(q);base={(2,3):{'q':q,'v':v}};R=M.wb_rhs_class(Fake,base)(np.arange(2),np.arange(3));a,_=R.acceleration(0.,q+1e-6,v);assert np.max(np.abs(a))>1e-12
def test_order():
 ratio=(257-1)/(129-1);assert math.isclose(M.order(1.,ratio**-4,129,257),4.,abs_tol=1e-14)

