"""Deterministic validated cells; no launch or writes at import."""
from common import *
from inherited.series import bounds, interval, hull
from inherited import preparation, validated, source_flow
import physics
def context(bits):
    ctx.prec=bits; ctx.threads=1
    src=loadin('source_flow_result',True); pp=loadin('canonical_preparation',True)
    p=dict(src['p']); p['eps']=arb(exact(CFG['epsilon']))
    p['c7']=pp['preps']['positive']['c7']; p['source_end']=src['end']
    p['source_jets']=pp['jets']
    binding=loadin('native_binding')
    root=interval(*map(exact,binding['a_enclosure']))
    H=-(p['lambda_a']+p['gamma']*(root-p['v0'])**2/2)/6
    T=p['gamma']*(root-p['v0'])/2
    bb=p['gamma']*T/2-p['m2']*root+4*H*T
    f=3*(p['mu']+4*p['k'])/bb
    y0=[arb(0),H,root,T,arb(1),arb(1),f,p['gamma']*f/2-2*T,arb(0)]
    return p,y0
def initial(bits,which,guard_value,root_box=None):
    p,y0=context(bits); design=rec.read(ROOT/'DESIGN.json')
    c=list(map(exact,design['center'])); radii=list(map(exact,design['radii']))
    if root_box is not None:
        p['x']=[interval(*map(exact,v)) for v in root_box]
    else:
        p['x']=[arb(v) if which=='center' else interval(v-r,v+r) for v,r in zip(c,radii)]
    inc=preparation.wall_increment(y0,p['source_jets'][0],p,p['eps'])
    y=y0+[p['x'][0],inc['target']]
    for i in range(5):y += [arb(int(i==0)),arb(0)]
    return {'guard':guard_value,'bits':bits,'which':which,'task_index':0,'cell_index':0,
       'elapsed_seconds':0.0,'cpu_seconds':0.0,'y':y,'initial_y':list(y),'p':p,
       'cover':[],'end':None,'max_picard':0,'last_cell':None}
def advance(st):
    s=st['cell_index']*exact(CFG['step']); lo,hi=bounds(st['p']['D'])
    h=min(exact(CFG['step']),hi-s)
    if h<=0:raise ArithmeticError('Flow beyond fixed domain')
    yn,cell=validated.step(st['y'],h,st['p'],physics)
    if not all(v.is_finite() for v in yn):raise ArithmeticError('Nonfinite validated state')
    if bounds(cell['box'][4])[0]<=0:raise ArithmeticError('Source positivity lost')
    if s+h>=lo:
        a=max(fmpq(0),lo-s); b=min(h,hi-s)
        z=validated.range_on_cell(cell,a,b)
        if b>a:st['cover'].append([str(s+a),str(s+b)])
        st['end']=z if st['end'] is None else [hull(x,y) for x,y in zip(st['end'],z)]
    st['max_picard']=max(st['max_picard'],cell['picard_iterations'])
    st['y']=yn;st['cell_index']+=1;st['last_cell']={'s':s,'cell':cell}
    return cell
def complete(st):
    return st['cell_index']*exact(CFG['step'])>=bounds(st['p']['D'])[1]
def check_cover(st):
    lo,hi=map(str,bounds(st['p']['D'])); rows=st['cover']
    return bool(rows) and rows[0][0]==lo and rows[-1][1]==hi and all(a[1]==b[0] for a,b in zip(rows,rows[1:]))
def decision(center,box):
    from inherited.series import record
    D=rec.read(ROOT/'DESIGN.json')
    C=[[arb(exact(x)) for x in row] for row in D['preconditioner']]
    c=list(map(exact,D['center']));rad=list(map(exact,D['radii']))
    J=box['map']['J']; F=center['map']['F']
    M=[[arb(int(i==j))-sum((C[i][k]*J[k][j] for k in range(5)),arb(0)) for j in range(5)] for i in range(5)]
    base=[-sum((C[i][k]*F[k] for k in range(5)),arb(0)) for i in range(5)]
    maximum=lambda z:max(abs(x) for x in bounds(z))
    image=[maximum(base[i])+sum(maximum(M[i][j])*rad[j] for j in range(5)) for i in range(5)]
    norm=[sum(maximum(M[i][j])*rad[j] for j in range(5))/rad[i] for i in range(5)]
    ok=all(v<exact(CFG['scientific_gates']['strict_image_radius_fraction'])*r for v,r in zip(image,rad)) and all(v<=exact(CFG['scientific_gates']['weighted_contraction_max']) for v in norm)
    K=[[str(c[i]-image[i]),str(c[i]+image[i])] for i in range(5)]
    return {'passed':ok,'F_center':[record(v) for v in F],'J_box':[[record(v) for v in row] for row in J],
        'preconditioner':D['preconditioner'],'M':[[record(v) for v in row] for row in M],
        'center_displacement':[record(v) for v in base],
        'image_radius':[str(v) for v in image],'image_radius_ratio':[str(v/r) for v,r in zip(image,rad)],
        'weighted_row_norm':[str(v) for v in norm],'root_enclosure':K,
        'failed_sufficient_gate_is_not_exclusion':True}
