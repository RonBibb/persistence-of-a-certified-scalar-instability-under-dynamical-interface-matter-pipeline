"""Physical-state projection of the authenticated full centered Hamiltonian flow."""
from flint import arb
import nonlinear


def rhs(y,p):
    return nonlinear.rhs(list(y)+[arb(0)]*6,p)[:11]


def coeff(y,N,p):
    return nonlinear.coeff(list(y)+[arb(0)]*6,N,p)[:11]
