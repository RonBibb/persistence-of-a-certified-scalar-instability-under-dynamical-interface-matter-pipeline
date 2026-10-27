import importlib.util
import itertools
import json
from pathlib import Path
import signal
import sys
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('exact_helpers',HERE.parent/'T5_WALL_ALLOCATION'/'producer.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def save(n,data):
    import os
    with (HERE/n).open('x') as f:
        json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())

def main():
    admission=json.loads((HERE/'ADMISSION.json').read_text())
    assert all(h.digest(HERE/n)==v for n,v in admission['sources'].items())
    exe=Path(sys.executable).resolve();rh=h.digest(exe)
    assert sys.version_info[:3]==(3,12,3) and rh=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    inputs=[]
    for name,classification in (('T4_CORRECTED_COORDINATES','PASS_IMPLEMENTATION_CORRECTED_TRANSITION_COORDINATES'),
        ('T6_SPLIT_TRANSFER','PASS_SPLIT_TRANSFER_CERTIFICATE'),('T7_INTEGER_INTERVAL_REPLICATION','PASS_INTEGER_INTERVAL_REPLICATION')):
        folder=HERE.parent/name
        assert json.loads((folder/'RESULT.json').read_text())['classification']==classification
        level=json.loads((folder/'LEVEL_2048.json').read_text())
        entries=level['transfer'] if name=='T6_SPLIT_TRANSFER' else level['upper_state'][4:]
        inputs.append([h.readball(v) for v in entries])
    boxes=[(min(m[j][0] for m in inputs),max(m[j][1] for m in inputs)) for j in range(4)]
    assert all(boxes[j][0]<=m[j][0]<=m[j][1]<=boxes[j][1] for m in inputs for j in range(4))
    (al,ah),(bl,bh),(cl,ch),(dl,dh)=boxes
    assert al>0 and bl>0 and ch<0 and dl>ah
    # Exact identity controls, no interval library.
    a,b,c,d=F(2),F(1),F(-1),F(3)
    xcrit=-2*c/d;ycrit=-2*c/a
    for x in (F(0),F(1,6),F(1,3),F(1,2),F(2,3)):
        y=-(2*c+d*x)/(a+b*x/2);linear=-(2*c+d*x)/a
        assert linear-y==b*x*y/(2*a)
        assert 0<=y<=ycrit*(1-x/xcrit) and x*y<=xcrit*ycrit/4
    k=F(1,4);c=-((a+d)*k+b*k*k/2)/2
    assert -2*c/(a+d)-k==b*k*k/(2*(a+d))
    ratio=(dl/ah,dh/al);saving=(1-ah/dl,1-al/dh)
    ratio_corners=[d/a for a,d in itertools.product((al,ah),(dl,dh))]
    assert ratio==(min(ratio_corners),max(ratio_corners))
    lower=(-2*ch/dh,-2*cl/dl);upper=(-2*ch/ah,-2*cl/al)
    detlo=al*dl-bl*ch;denhi=ah+bh*lower[1]/2
    assert detlo>denhi*denhi,'UNION_SLOPE_NOT_CERTIFIED'
    low=[x[0] for x in boxes];high=[x[1] for x in boxes]
    kl=h.bisect(lambda x:h.S(high,x,x),F(0),F(1,10))
    ku=h.bisect(lambda x:h.S(low,x,x),F(0),F(1,10))
    equal=(kl[0],ku[1]); assert equal[0]>0 and equal[1]-equal[0]<=F(1,10000)
    linear_equal=(-2*ch/(ah+dh),-2*cl/(al+dl))
    shift=(bl*equal[0]*equal[0]/(2*(ah+dh)),bh*equal[1]*equal[1]/(2*(al+dl)))
    assert 0<shift[0]<=shift[1]
    max_absolute=bh*lower[1]*upper[1]/(8*al)
    max_relative=max_absolute/upper[0]
    assert max_absolute>0 and max_relative>0
    assert all(h.digest(HERE/n)==v for n,v in admission['sources'].items()) and h.digest(exe)==rh
    save('RESULT.json',dict(classification='PASS_TRANSITION_MECHANISM_BOUNDS',
        inputs_combined_by='union_not_intersection',union_transfer=[h.rec(x) for x in boxes],
        upper_to_lower_threshold_ratio=h.rec(ratio),lower_wall_budget_saving_fraction=h.rec(saving),
        lower_only=h.rec(lower),upper_only=h.rec(upper),equal_each=h.rec(equal),linear_equal_each=h.rec(linear_equal),
        equal_wall_interaction_shift=h.rec(shift),global_upper_wall_interaction_shift_upper=h.rec((F(0),max_absolute)),
        global_relative_interaction_shift_upper=h.rec((F(0),max_relative)),
        global_slope_less_than_minus_one=True,controls_passed=True,source_inputs_runtime_unchanged=True,
        remaining_negative_mode=True))

if __name__=='__main__':
    def timeout(signum,frame):raise TimeoutError('590second cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as exc:
        save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(exc)));raise
    finally:signal.alarm(0)
