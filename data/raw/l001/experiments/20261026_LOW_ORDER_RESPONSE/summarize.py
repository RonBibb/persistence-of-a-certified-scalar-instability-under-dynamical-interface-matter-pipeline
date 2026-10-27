"""Read and summarize immutable diagnostic results; no new numerical solve."""
import hashlib,json
from fractions import Fraction
from pathlib import Path
root=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def checked(p):
    terminal=read(p/'TERMINAL.json');assert terminal['pass']
    raw=(p/'RESULT.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==terminal['result_sha256']
    return json.loads(raw)
low=checked(root);high=checked(root.parent/'20261026_HIGH_ORDER_RESPONSE')
rows={}
for name,orders in low['arms'].items():
    assert set(orders)==set(map(str,range(1,39)))
    assert all(v['positive_gate'] for v in orders.values())
    values={int(n):Fraction(v['C_sum_exact']) for n,v in orders.items()}
    n=max(values,key=values.get);q=values[n]
    hi=high['arms'][name]['outward_integer_C_sum']
    assert hi<=3932 and all(v<=3932 for v in values.values())
    rows[name]={'low_order_max_at':n,'low_order_C_outward':-(-q.numerator//q.denominator),
                'high_order_C_outward':hi,'common_C':3932}
print(json.dumps({'all_positive_orders_covered':True,'representations':rows,
    'scope':'diagnostic real-axis scalar bound, conditional on inherited saved-cell validation; not complex collar or amplitude certificate'},indent=2))
