"""Read-only replay of the failed frozen first cell, same 32 Picard iterations."""
import json,sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
import runner,primary
from flint import ctx,fmpq
from series import bounds,interval,hull,inflate,record
ctx.prec=768;ctx.threads=1
b,guard=runner.authenticate();H,P,T,p=runner.initial(b['model_exact'])
y=primary.initial(H,P,T);h=fmpq(2,runner.CONFIG['primary_denominator']);dt=interval(fmpq(0),h)
box=[inflate(hull(a,a+dt*v)) for a,v in zip(y,primary.rhs(y,p))]
names=['W','H','Phi','T','E','s','hA','vA','h0','v0','h1','v1']
print(json.dumps({'guard':guard,'cell':0,'step':str(h),'frozen_iterations':32}))
for it in range(1,33):
    image=[hull(a,a+dt*v) for a,v in zip(y,primary.rhs(box,p))]
    failed=[i for i,(a,b) in enumerate(zip(image,box)) if not(bounds(b)[0]<bounds(a)[0] and bounds(a)[1]<bounds(b)[1])]
    if it in (1,2,4,8,16,32) or not failed:
        print(json.dumps({'iteration':it,'failed':[{ 'component':names[i],
             'box':record(box[i])['decimal'],'image':record(image[i])['decimal']} for i in failed]}))
    if not failed:break
    box=[inflate(hull(a,b)) for a,b in zip(box,image)]
