"""Exact, bounded consistency checks; call run() on Linux after binding.

No ODE, no imports of research parents, no execution at import. Full tensor
component identification and Bianchi remain explicitly analytic premises.
"""
from fractions import Fraction


class P:
    def __init__(self, value=0):
        if isinstance(value, P): self.t = dict(value.t)
        elif isinstance(value, dict): self.t = {k: Fraction(v) for k, v in value.items() if v}
        else: self.t = {(): Fraction(value)} if value else {}
    def __add__(self, other):
        other = P(other); out = dict(self.t)
        for k, v in other.t.items(): out[k] = out.get(k, 0) + v
        return P(out)
    __radd__ = __add__
    def __neg__(self): return P({k: -v for k, v in self.t.items()})
    def __sub__(self, other): return self + -P(other)
    def __rsub__(self, other): return P(other) + -self
    def __mul__(self, other):
        other = P(other); out = {}
        for a, v in self.t.items():
            for b, w in other.t.items():
                k = tuple(sorted(a + b)); out[k] = out.get(k, 0) + v*w
        return P(out)
    __rmul__ = __mul__
    def __truediv__(self, other): return self * (1 / Fraction(other))
    def __pow__(self, n):
        if not isinstance(n, int) or n < 0: raise ValueError('nonnegative integer power')
        out = P(1)
        for _ in range(n): out = out*self
        return out
    def coefficient(self, variable, degree):
        return P({tuple(x for x in k if x != variable): v
                  for k, v in self.t.items() if k.count(variable) == degree})
    def substitute(self, variable, replacement):
        out = P()
        for k, v in self.t.items():
            rest = tuple(x for x in k if x != variable)
            out += P({rest:v}) * P(replacement)**k.count(variable)
        return out


def var(name): return P({(name,): 1})


def run(root=None):
    checks = []
    def eq(a, b, label):
        if (P(a)-b).t: raise AssertionError(label)
        checks.append(label)
    def nonzero(a, label):
        if not P(a).t: raise AssertionError(label)
        checks.append(label)
    h, a, b, at, bt, v = map(var, ('h','alpha','beta','alpha_t','beta_t','v'))
    HR = h+a
    # Temporal Ricci difference; radial equality is an analytic premise.
    ric_tt = 3*(at+HR**2-a*HR)+bt+b**2-a*b
    ric_xx = at+HR*(3*HR+b-a)
    trace = 2*at+bt-h*(2*a+b)+b**2-2*a*b-2*a**2+v**2
    eq(ric_tt-ric_xx+v**2, trace, 'TEMPORAL_RICCI_DIFFERENCE_TO_TRACE')
    As, pts, u = map(var, ('A','p_ts','u'))
    mixed = pts-b*As+v*u/3
    eq(-3*pts+3*b*As-v*u, -3*mixed, 'COVARIANT_MIXED_TO_S6')
    eq(3*(at+HR*(2*h+a)), 6*h**2+3*(at+3*h*a)+3*a**2,
       'RADIAL_EINSTEIN_TEMPORAL_PART')
    z, marker, lam, H, pt, bs, ps, et, ex, es, esp = map(var,
        ('z','marker','lambda','H','pt','bt','ps','et','ex','es','esp'))
    temporal = marker*lam*et+3*(h+z*pt)*marker*(et-ex)+z*bs*marker*(et-es)
    radial = marker*esp+(H+z*ps)*marker*(4*es-et-3*ex)
    lead_t = temporal.coefficient('marker',1).coefficient('z',0)
    lead_s = radial.coefficient('marker',1).coefficient('z',0)
    eq(lead_t, lam*et+3*h*(et-ex), 'TEMPORAL_LEADING_EXTRACTION')
    eq(lead_t.substitute('ex',et), lam*et, 'TRACEFREE_TEMPORAL_REDUCTION')
    eq(lead_s, esp+H*(4*es-et-3*ex), 'RADIAL_LEADING_EXTRACTION')
    eq(lead_s.substitute('et',0).substitute('ex',0), esp+4*H*es,
       'RADIAL_AFTER_TEMPORAL_CONSTRAINT')
    eq(temporal.coefficient('marker',1).coefficient('z',1),
       3*pt*(et-ex)+bs*(et-es), 'POSITIVE_ORDER_PRODUCTS_RETAINED_SEPARATELY')
    C, Cp, Sc, Scp, T, Sg, D, Sp = map(var,
        ('C','Cp','Sc','Scp','T','Sg','D','Sp'))
    eq((esp+4*H*es).substitute('esp',-Cp).substitute('es',-C),
       -(Cp+4*H*C), 'RADIAL_TO_CONSTRAINT_SIGN')
    compatibility = Scp+4*H*Sc-T*Sg-D*Sp
    eq(T*Sg+D*Sp-Scp-4*H*Sc, -compatibility,
       'CONSTRAINT_IDENTITY_TO_SOURCE_COMPATIBILITY_SIGN')
    # Controls preserve the conditions which make the induction work.
    nonzero(lead_t.substitute('ex',et), 'NONZERO_RATE_REQUIRED')
    eq(lead_t.substitute('ex',et).substitute('lambda',0), 0,
       'ZERO_HARMONIC_NOT_REMOVED')
    nonzero(lead_t-lam*et, 'TRACEFREE_EQUALITY_REQUIRED')
    nonzero((marker*bs*(et-es)).coefficient('marker',1),
            'ZEROTH_ORDER_RADIAL_VELOCITY_WOULD_BREAK_EXTRACTION')
    nonzero(esp+3*H*es-(esp+4*H*es), 'RADIAL_DIMENSION_MUTATION_DETECTED')
    # Conditional wall induction: J^a_b=j delta^a_b, independently at each
    # wall. Codazzi and material exchange establishing div(J)=0 are inherited.
    j, jt = var('wall_trace'), var('wall_trace_t')
    connections = [var('wall_connection_'+str(i)) for i in range(4)]
    pure_trace_divergence = jt + sum((q*(j-j) for q in connections), P())
    eq(pure_trace_divergence, jt, 'WALL_IDENTITY_TENSOR_CONNECTION_CANCELLATION')
    eq(pure_trace_divergence.substitute('wall_trace_t',lam*j), lam*j,
       'WALL_NONZERO_HARMONIC_REDUCTION')
    eq((lam*j).substitute('lambda',0), 0, 'WALL_ZERO_HARMONIC_NOT_REMOVED')
    nonzero(lam*j, 'WALL_RATE_REQUIRED')
    return {'pass': True, 'checks': checks, 'check_count': len(checks),
            'scope': 'Exact algebraic component reductions, leading homogeneous extraction and conditional pure-trace wall cancellation. Bulk tensor identification is separately qualified; contracted Bianchi and wall Codazzi/material exchange are inherited. No ODE or convergence proof.',
            'rate': 'lambda=n*r, nonzero; trace reconstruction also lambda!=h',
            'unproved': ['full nonlinear convergence', 'complex-collar/source-norm closure',
                         'finite-amplitude endpoint', 'zero-harmonic closure']}
