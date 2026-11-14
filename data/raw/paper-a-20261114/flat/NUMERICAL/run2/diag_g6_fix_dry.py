import sys, math, time
sys.path.insert(0, sys.argv[1])
import flatcount as fc
cid, ta, tb = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
t0 = time.time()
bg, meta = fc.build_case(cid, 2000)
lam_abs_min = 2.0 * max(1.0, bg.coop_bound())
grid = fc.merged_grid(bg, lam_abs_min)
k4 = 4.0 * bg.k
nfail = 0; maxge2 = 0.0; maxdisc = 0.0; maxdepth = 0; nref = 0
for mu in grid:
    r = fc.shoot(bg, mu, ta, tb, phase=True)
    if not fc.g6_check(r, mu + k4, True): nfail += 1
    maxge2 = max(maxge2, r["max_dtheta"]); maxdisc = max(maxdisc, r["max_refine_discrepancy"])
    maxdepth = max(maxdepth, r["max_refine_depth"]); nref += r["n_refined_steps"]
print("DRY(redacted) %s t=(%g,%g): G6 failures %d; max per-step(>=2) %.4f; refined steps %d; max refine discrepancy %.2e; max depth %d; %.1fs" % (cid, ta, tb, nfail, maxge2, nref, maxdisc, maxdepth, time.time()-t0))
