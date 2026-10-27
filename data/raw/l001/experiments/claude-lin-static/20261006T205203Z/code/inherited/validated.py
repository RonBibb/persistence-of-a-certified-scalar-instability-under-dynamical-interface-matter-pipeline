"""Shared strict-Picard/fifth-order-Taylor enclosure driver, disclosed explicitly."""
from flint import fmpq
from series import bounds,interval,hull,inflate


def range_on_cell(cell,lo,hi):
    if not fmpq(0)<=lo<=hi<=cell['h']:
        raise ValueError('Cell offset outside validated interval')
    t=interval(lo,hi);out=[]
    for row,r in zip(cell['coeff'],cell['remainder']):
        v=r
        for a in reversed(row):
            v=v*t+a
        out.append(v)
    return out


def step(y,h,p,engine):
    dt=interval(fmpq(0),h)
    box=[inflate(hull(a,a+dt*v)) for a,v in zip(y,engine.rhs(y,p))]
    for it in range(1,33):
        image=[hull(a,a+dt*v) for a,v in zip(y,engine.rhs(box,p))]
        enclosed=[bounds(b)[0]<bounds(a)[0] and bounds(a)[1]<bounds(b)[1] for a,b in zip(image,box)]
        if all(enclosed):
            break
        # Retain already-contained coordinates; recheck EVERY coordinate against
        # the entire updated box next iteration. Blind repeated inflation of
        # s'=1 needlessly magnifies the high-order shape forcing near s=0.
        box=[a if ok else inflate(hull(a,b)) for a,b,ok in zip(box,image,enclosed)]
    else:
        raise ArithmeticError('Frozen strict Picard inclusion limit')
    cell={'h':h,'box':box,'coeff':engine.coeff(y,4,p),
          'remainder':[row[5] for row in engine.coeff(box,5,p)],'picard_iterations':it}
    return range_on_cell(cell,h,h),cell
