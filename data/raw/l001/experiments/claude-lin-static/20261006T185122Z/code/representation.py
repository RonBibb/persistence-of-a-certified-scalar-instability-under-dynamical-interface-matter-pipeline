"""Explicit native-piece selection for the inherited Taylor-integral coordinate map.

reference/producer.py and reference/jet.py are byte-identical copies of the admission
producer (hashes bound in FREEZE.json). That producer chooses the native polynomial piece
at a map knot with floor(s/h) evaluated in floating point. ExplicitDense keeps every
inherited operation and replaces only that choice by an explicit integer table.
"""
import bisect
import math
import sys
from fractions import Fraction
from pathlib import Path

import mpmath as mp

REFERENCE = Path(__file__).resolve().parent / 'reference'
if str(REFERENCE) not in sys.path:
    sys.path.insert(0, str(REFERENCE))
import producer as reference  # noqa: E402
from jet import shift, horner, exp_series  # noqa: E402

from common import exact_mpf, exact_decimal, AMBIGUITY  # noqa: E402


def bind_parent(parent):
    """Point the reference reader at a read-only native packet or a synthetic fixture."""
    reference.PARENT = Path(parent)


def canonical_table(cells):
    """Map cell i is built from native piece i at local offset zero."""
    return list(range(cells))


def floor_table(dense):
    """The reference producer's own knot rule, at the precision active now."""
    return [dense.locate(i * dense.h)[0] for i in range(dense.cells)]


def nearest_interior_knot(value, spacing, count):
    """Index and exact distance of the nearest shared knot j*spacing, 1<=j<=count-1."""
    ratio = value / spacing
    j = math.floor(ratio + Fraction(1, 2))
    j = max(1, min(count - 1, j))
    return j, abs(value - j * spacing)


class ExplicitDense(reference.Dense):
    """Reference Dense with the map-knot piece choice supplied as data."""

    def __init__(self, level, case):
        super().__init__(level, case)
        self.h_exact = exact_decimal(self.seed['h'])
        self.D_exact = exact_decimal(self.seed['D'])
        self.table = None

    def jets_piece(self, piece, z, s, n):
        r = self.seedrows[piece]
        y = self.solrows[piece]
        A = shift(y[0], z, n)
        ell = [-2 * self.eps * v for v in shift(r[5], z, n)]
        F = [v + self.eps * w + c for v, w, c in zip(shift(r[2], z, n), shift(r[6], z, n), shift(self.corr, s, n))]
        B = [a + q for a, q in zip(A, shift(self.q, s, n))]
        return A, B, F, ell

    def make_map_explicit(self, table):
        if len(table) != self.cells:
            raise ValueError('Selection table length')
        self.xknots = [mp.mpf(0)]
        self.xpoly = []
        self.offsets = []
        for i in range(self.cells):
            piece = table[i]
            if piece not in (i - 1, i) or not 0 <= piece < self.cells:
                raise ValueError('Selection must be the left or right native piece of the knot')
            s = i * self.h
            z = s - piece * self.h
            A, B, F, ell = self.jets_piece(piece, z, s, self.degree)
            e = exp_series([l - b for l, b in zip(ell, B)])
            c = [mp.mpf(0)] + [v / (j + 1) for j, v in enumerate(e)]
            self.xpoly.append(c)
            self.xknots.append(self.xknots[-1] + horner(c, self.h))
            self.offsets.append(z)
        self.X = self.xknots[-1]
        self.table = list(table)

    def piece_of(self, s):
        """Exact rational native-piece index; shared knots within the margin are flagged."""
        sq = exact_mpf(s)
        k = math.floor(sq / self.h_exact)
        k = max(0, min(self.cells - 1, k))
        j, margin = nearest_interior_knot(sq, self.h_exact, self.cells)
        ambiguous = margin < AMBIGUITY
        return (j if ambiguous else k), ambiguous, margin, j

    def evaluate_piece(self, piece, s, q):
        z = s - piece * self.h
        base = [horner(row, z) for row in self.seedrows[piece]]
        A = horner(self.solrows[piece][0], z)
        fields = [A, A + horner(q, s), base[2] + self.eps * base[6] + horner(self.corr, s), -2 * self.eps * base[5]]
        return fields, base

    def fields_explicit(self, s, q):
        """Fields (A,B,Phi,ell) and the eight seed rows at s; dual evaluation at a shared knot."""
        piece, ambiguous, margin, j = self.piece_of(s)
        fields, base = self.evaluate_piece(piece, s, q)
        alternate = None
        if ambiguous:
            other = j - 1
            alt_fields, alt_base = self.evaluate_piece(other, s, q)
            alternate = {'piece': other, 'fields': alt_fields, 'seed': alt_base}
        return fields, base, {'piece': piece, 'ambiguous': ambiguous, 'margin': margin, 'alternate': alternate}

    def derivative_row(self, i):
        c = self.xpoly[i]
        return [(j + 1) * c[j + 1] for j in range(len(c) - 1)]

    def map_at(self, s):
        """Represented x(s) and x'(s) on the cell selected by the exact piece rule."""
        cell, ambiguous, margin, j = self.piece_of(s)
        z = s - cell * self.h
        value = self.xknots[cell] + horner(self.xpoly[cell], z)
        slope = horner(self.derivative_row(cell), z)
        alternate = None
        if ambiguous:
            other = j - 1
            zo = s - other * self.h
            alternate = {'cell': other, 'value': self.xknots[other] + horner(self.xpoly[other], zo),
                         'slope': horner(self.derivative_row(other), zo)}
        return value, slope, {'cell': cell, 'ambiguous': ambiguous, 'margin': margin, 'alternate': alternate}

    def invert_in_cell(self, x, i):
        """Body of the reference invert with the cell given explicitly."""
        target = x - self.xknots[i]
        c = self.xpoly[i]
        d = [(j + 1) * c[j + 1] for j in range(len(c) - 1)]
        z = self.h * target / (self.xknots[i + 1] - self.xknots[i])
        for _ in range(20):
            dz = (horner(c, z) - target) / horner(d, z)
            z -= dz
            if abs(dz) < mp.mpf(10) ** (-mp.mp.dps + 15):
                break
        if not abs(horner(c, z) - target) < mp.mpf('1e-55'):
            raise ArithmeticError('Inverse map Newton residual')
        return i * self.h + z

    def invert_explicit(self, x):
        """Inverse map with exact knot comparison; shared map knots within the margin are flagged."""
        i = max(0, min(bisect.bisect_right(self.xknots, x) - 1, self.cells - 1))
        xq = exact_mpf(x)
        best = None
        for j in (i, i + 1):
            if 1 <= j <= self.cells - 1:
                distance = abs(xq - exact_mpf(self.xknots[j]))
                if best is None or distance < best[1]:
                    best = (j, distance)
        ambiguous = best is not None and best[1] < AMBIGUITY
        cell = best[0] if ambiguous else i
        s = self.invert_in_cell(x, cell)
        alternate = None
        if ambiguous:
            other = best[0] - 1
            alternate = {'cell': other, 's': self.invert_in_cell(x, other)}
        return s, {'cell': cell, 'ambiguous': ambiguous,
                   'margin': None if best is None else best[1], 'alternate': alternate}
