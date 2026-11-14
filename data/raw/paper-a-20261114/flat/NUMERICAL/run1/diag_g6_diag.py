import sys, math
sys.path.insert(0, sys.argv[1])
import flatcount as fc
cid, ta, tb = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
bg, meta = fc.build_case(cid, 2000)
lam_abs_min = 2.0 * max(1.0, bg.coop_bound())
grid = fc.merged_grid(bg, lam_abs_min)
k4 = 4.0 * bg.k
fails = []
for mu in grid:
    r = fc.shoot(bg, mu, ta, tb, phase=True)
    ok = fc.g6_check(r, mu + k4, True)
    if not ok:
        fails.append((mu + k4, round(r["first_dtheta"], 4), round(r["max_dtheta"], 4), r["f_launch"], r["f_h"] > 0))
print(cid, ta, tb, "grid", len(grid), "G6 failures", len(fails), "h", bg.h)
for f in fails[:12]:
    print("  lambda=%.3e first=%.4f maxge2=%.4f f_launch=%r f_h>0=%s" % f)
