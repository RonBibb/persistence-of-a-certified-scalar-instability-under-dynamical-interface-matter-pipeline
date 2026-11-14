import sys, os
sys.path.insert(0, sys.argv[1])
os.environ.setdefault("X", "1")
import importlib.util
spec = importlib.util.spec_from_file_location("cfb", os.path.join(sys.argv[1], "certify_flat_background.py"))
cfb = importlib.util.module_from_spec(spec)
cfb.OUT = None
src = open(os.path.join(sys.argv[1], "certify_flat_background.py")).read().replace("OUT = ROOT / \x27flat_certificate\x27; OUT.mkdir(exist_ok=True)", "OUT = None")
exec(compile(src, "cfb_diag", "exec"), cfb.__dict__)
p = {"m2": cfb.exact(4), "q": cfb.exact(0)}
y, k = cfb.initial_flat(p)
h = cfb.fmpq(1, 8192)
dt = cfb.interval(0, h)
for j in range(6144):
    try:
        y, cell = cfb.step(y, h, p, k)
    except RuntimeError as e:
        print("FAIL at cell", j, "s =", float(j) / 8192)
        names = ["W", "H", "P", "T", "E"]
        for i, nm in enumerate(names):
            lo, hi = cfb.bounds(y[i]); print(" state", nm, float(lo), float(hi), "width", float(hi - lo))
        for i in range(5, 10):
            lo, hi = cfb.bounds(y[i]); print(" dstate", i, float(lo), float(hi))
        box = [cfb.pad(cfb.hull(a, a + dt * v)) for a, v in zip(y, cfb.rhs(y, p, k))]
        for it in range(6):
            image = [cfb.hull(a, a + dt * v) for a, v in zip(y, cfb.rhs(box, p, k))]
            bad = [i for i, (a, b) in enumerate(zip(image, box)) if not cfb.inside(a, b)]
            print(" iter", it, "not-inside comps", bad, [ (float(cfb.bounds(image[i])[0]), float(cfb.bounds(image[i])[1]), float(cfb.bounds(box[i])[0]), float(cfb.bounds(box[i])[1])) for i in bad[:3]])
            box = [cfb.pad(cfb.hull(a, b)) for a, b in zip(image, box)]
        break
else:
    print("no failure")
