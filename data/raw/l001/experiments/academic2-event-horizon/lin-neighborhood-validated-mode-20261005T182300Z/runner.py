"""Uniform static-neighborhood validated mode and inherited exact restart."""
import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone

import flint
from flint import arb, fmpq, ctx

ROOT = Path(__file__).resolve().parent
CONFIG = {"bits":768,"primary_steps":8192,"independent_steps":16384,
          "order":5,"checkpoint_cells":256,"mu":["-33/25000","-131/100000"],
          "A":["696726888586725316547/7036874417766400000000","696727170061702027203/7036874417766400000000"],
          "D":["8177/4096","8187/4096"],
          "scope":"EVERY_PARAMETER_PAIR_IN_COMPLETE_CERTIFIED_STATIC_BOX",
          "parameter_box":{
              "v1":["3256417487256207/36028797018963968","101988226458125/1125899906842624"],
              "lambda_b":["-1703752349608937/281474976710656","-1703696054613595/281474976710656"]},
          "task_order":["primary_low","primary_high","independent_low","independent_high",
                        "primary_strip","independent_strip"]}
ENV = {"PYTHONDONTWRITEBYTECODE":"1","PYTHONHASHSEED":"0","PYTHONNOUSERSITE":"1",
       "OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1"}


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(x):
    return json.dumps(pack(x),sort_keys=True,separators=(",",":"),allow_nan=False).encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def atomic(path,x,immutable=False):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if immutable and path.exists():
        raise RuntimeError(f"Refuse overwrite: {path}")
    descriptor,name = tempfile.mkstemp(prefix=path.name+".uncommitted-",dir=path.parent)
    tmp = Path(name)
    with os.fdopen(descriptor,"wb") as stream:
        stream.write(json.dumps(pack(x),sort_keys=True,indent=2,allow_nan=False).encode()+b"\n")
        stream.flush(); os.fsync(stream.fileno())
    os.replace(tmp,path)
    if immutable:
        path.chmod(0o444)


def pack(x):
    if isinstance(x,arb):
        if not x.is_finite():
            raise ArithmeticError("Nonfinite interval")
        # Arb's public constructor may round a 30-bit radius upward. Choose an
        # outward constructor-stable representation, and use it in BOTH paths.
        for _ in range(3):
            native=[[int(v) for v in x.mid().man_exp()],[int(v) for v in x.rad().man_exp()]]
            y=arb(tuple(native[0]),tuple(native[1]))
            if y.mid()==x.mid() and y.rad()==x.rad():
                return {"_arb_native":native}
            if not y.mid()==x.mid() or not y.rad()>=x.rad():
                raise RuntimeError("Checkpoint canonicalization shrank or shifted interval")
            x=y
        raise RuntimeError("No stable outward checkpoint representation")
    if isinstance(x,fmpq):
        return {"_rational":str(x)}
    if isinstance(x,dict):
        return {key:pack(val) for key,val in x.items()}
    if isinstance(x,(tuple,list)):
        return [pack(v) for v in x]
    return x


def unpack(x):
    if isinstance(x,dict):
        if "_arb_native" in x:
            m,r=x["_arb_native"]
            y=arb(tuple(m),tuple(r))
            raw={"_arb_native":[[int(v) for v in y.mid().man_exp()],[int(v) for v in y.rad().man_exp()]]}
            if raw!=x:
                raise RuntimeError("Native Arb representation did not restore exactly")
            return y
        if "_rational" in x:
            return fmpq(x["_rational"])
        return {key:unpack(val) for key,val in x.items()}
    if isinstance(x,list):
        return [unpack(v) for v in x]
    return x


def enclosure(x):
    lo,hi=x.lower().fmpq(),x.upper().fmpq()
    return {"lo_exact":str(lo),"hi_exact":str(hi),"lo_approx":float(lo),"hi_approx":float(hi)}


def contains_zero(x):
    return x.lower()<=0<=x.upper()


def runtime():
    package=Path(flint.__file__).resolve().parent
    libraries=list(package.rglob("*.so"))+list(package.parent.glob("python_flint.libs/*"))
    return {"python":platform.python_version(),"executable":str(Path(sys.executable).resolve()),
            "executable_sha256":digest(Path(sys.executable).resolve()),"flint":flint.__version__,
            "flint_file":str(package),"libraries":{str(p):digest(p) for p in sorted(libraries) if p.is_file()},
            "precision":int(ctx.prec),"threads":int(ctx.threads),
            "env":{key:os.environ.get(key) for key in ENV}}


def source_hashes():
    names=["primary_interval.py","independent_interval.py","runner.py","CONTRACT.md"]
    return {name:digest(ROOT/name) for name in names}


def save_checkpoint(output,state,guard):
    payload={"guard":guard,"state":pack(state)}
    restored=unpack(payload["state"])
    state.clear(); state.update(restored)
    sha=fingerprint(payload)
    name=f"checkpoints/{state['task_index']:02d}-{state['cell_index']:06d}-{sha}.json"
    dest=output/name
    if not dest.exists():
        atomic(dest,payload,True)
    atomic(output/"LATEST.json",{"path":name,"digest":sha,"guard":guard})
    atomic(output/"PROGRESS.json",{"state":"RUNNING","utc":now(),"guard":guard,
           "current_task":CONFIG["task_order"][state["task_index"]] if state["task_index"]<6 else "finished",
           "completed_tasks":len(state["results"]),"completed_cells":state["cell_index"],
           "task_total_cells":state.get("total_cells"),"elapsed_seconds":state["elapsed_seconds"],
           "checkpoint":name,"checkpoint_digest":sha})


def load_checkpoint(output,guard):
    ptr=json.loads((output/"LATEST.json").read_text())
    if ptr["guard"]!=guard:
        raise RuntimeError("Checkpoint pointer guard mismatch")
    path=(output/ptr["path"]).resolve()
    if path.parent!=(output/"checkpoints").resolve():
        raise RuntimeError("Checkpoint escapes expected directory")
    data=json.loads(path.read_text())
    if data["guard"]!=guard or fingerprint(data)!=ptr["digest"]:
        raise RuntimeError("Checkpoint digest or guard mismatch")
    return unpack(data["state"])


def authenticate():
    binding=json.loads((ROOT/"BINDINGS.json").read_text())
    frozen=json.loads((ROOT/"FREEZE_RECORD.json").read_text())
    if digest(ROOT/"BINDINGS.json")!=frozen["binding_sha256"]:
        raise RuntimeError("Binding changed")
    if binding["config"]!=CONFIG or binding["source"]!=source_hashes():
        raise RuntimeError("Source or scientific configuration changed")
    for item in binding["inputs"].values():
        if digest(ROOT/item["path"])!=item["sha256"]:
            raise RuntimeError("Parent input changed: "+item["path"])
    for name,sha in binding["review_sources"].items():
        if digest(ROOT/name)!=sha:
            raise RuntimeError("Review source changed")
    if runtime()!=binding["runtime"]:
        raise RuntimeError("Runtime changed")
    return binding, frozen["binding_sha256"]


def preflight(output):
    output.mkdir(parents=True,exist_ok=False)
    reports={}; timings={}
    for engine in ("primary","independent"):
        mod=importlib.import_module(engine+"_interval")
        reports[engine+"_algebra"]=mod.algebra_controls()
        if engine=="independent": reports["symbolic"]=mod.symbolic_controls()
        p={"m2":arb(fmpq(41,100)),"mu":arb(0),"k":arb(0),"gamma":arb(20)}
        for name,pair in CONFIG["parameter_box"].items():
            p[name]=mod.interval(*map(fmpq,pair))
        y=[arb(0),arb(-1),arb(0),arb(0),arb(1),arb(1),arb(0),arb(0)]
        if engine=="independent": y.pop(4)
        h=fmpq(2,CONFIG[engine+"_steps"])
        start=time.monotonic()
        for j in range(256):
            y,cell=mod.step(y,h,p)
        timings[engine]=time.monotonic()-start
        exact_s=256*h
        target=[-arb(exact_s),arb(-1),arb(0),arb(0),(arb(exact_s)).exp(),(2*arb(exact_s)).exp(),arb(0),arb(0)]
        if engine=="independent": target.pop(4)
        encloses=all(a.lower()<=b.lower() and a.upper()>=b.upper() for a,b in zip(y,target))
        reports[engine+"_analytic_containment"]=encloses
        control={"task_index":0,"cell_index":256,"results":[],"elapsed_seconds":0,
                 "total_cells":int(math.ceil(fmpq(CONFIG["D"][1])/h)),
                 "state":y,"params":p,"engine":engine,"step":h}
        controlroot=output/engine
        save_checkpoint(controlroot,control,"analytic-control-v1")
        y,p=control["state"],control["params"]
        loaded=load_checkpoint(controlroot,"analytic-control-v1")
        reports[engine+"_post_canonical_native_roundtrip"]=pack(loaded)==pack(control)
        next_y,_=mod.step(y,h,p)
        expected=fingerprint(pack(next_y))
        child=subprocess.run([sys.executable,"-B",str(ROOT/"runner.py"),"control-child",str(controlroot)],
                             text=True,capture_output=True,check=True,env=os.environ.copy())
        reports[engine+"_fresh_process_next_step"]=json.loads(child.stdout)["digest"]==expected
        try:
            load_checkpoint(controlroot,"changed-config-input-source-runtime")
        except RuntimeError:
            reports[engine+"_changed_guard_rejected"]=True
        else: reports[engine+"_changed_guard_rejected"]=False
        atomic(controlroot/"uncommitted.tmp.json",{"partial":"not authoritative"},True)
        reports[engine+"_uncommitted_ignored"]=pack(load_checkpoint(controlroot,"analytic-control-v1"))==pack(control)
    def passing(x):
        return all(passing(v) for v in x.values()) if isinstance(x,dict) else x is True
    result={"pass":passing(reports),"checks":reports,"timing_256_steps_seconds":timings,
            "source":source_hashes(),"runtime":runtime(),"utc":now(),"physical_model_evaluated":False}
    atomic(output/"RESULT.json",result,True)
    print(json.dumps({k:v for k,v in result.items() if k not in ("runtime","source")},indent=2))
    if not result["pass"]: raise RuntimeError("Preflight failed")


def freeze(preflight_path):
    pre=json.loads((preflight_path/"RESULT.json").read_text())
    if not pre["pass"] or pre["source"]!=source_hashes() or pre["runtime"]!=runtime():
        raise RuntimeError("Preflight is stale or failed")
    prev=ROOT.parent/"lin-central-validated-mode-r1-20261005T172800Z"
    expected={"RESULT.json":"e97910ac0fdf5acbdc224438b03ee3aafbba06547356e347136d5d968bd2df94",
              "MANIFEST.json":"cbec54af3421ff8251bf7db2119133e262d700a500850322252488c358d9f53d"}
    for name,sha in expected.items():
        if digest(prev/name)!=sha: raise RuntimeError("Previous seal mismatch: "+name)
    manifest=json.loads((prev/"MANIFEST.json").read_text())
    # The previously sealed inventory has file records under files.
    entries=manifest["files"]
    if isinstance(entries,dict):
        entries=[{"path":k,"sha256":v if isinstance(v,str) else v["sha256"]} for k,v in entries.items()]
    for item in entries:
        if digest(prev/item["path"])!=item["sha256"]: raise RuntimeError("Previous file changed: "+item["path"])
    old=json.loads((prev/"BINDINGS.json").read_text())
    paths={"previous_binding":prev/"BINDINGS.json","previous_result":prev/"RESULT.json",
           "previous_manifest":prev/"MANIFEST.json","preflight":preflight_path/"RESULT.json",
           "central_proof_review":prev/"INDEPENDENT_PROOF_AUDIT.md",
           "central_postrun_review":prev/"POSTRUN_REVIEW.md",
           "central_runner":prev/"runner.py"}
    neighborhood=ROOT.parent/"lin-static-parameter-neighborhood-r2-20261005T120100Z"
    paths["static_neighborhood_result"]=neighborhood/"output/RESULT.json"
    paths["static_neighborhood_binding"]=neighborhood/"BINDINGS.json"
    paths["static_neighborhood_terminal"]=neighborhood/"output/TERMINAL_CHECKPOINT.json"
    paths["static_neighborhood_audit"]=ROOT.parent/"lin-r2-stability-qualification-20261005T152128Z/audit/R2_POSTRUN_AUDIT.json"
    assert digest(paths["static_neighborhood_result"])=="3d6353e7277e273fdf35101ef3b9126802de04ac0c1dbf7931d06209e90e8b21"
    assert digest(paths["static_neighborhood_audit"])=="844c3ebd822aa4b487ab6ee306e04fd57c2a401698b1a3a524191582680ef519"
    for name in ("primary_interval.py","independent_interval.py"):
        if digest(ROOT/name)!=old["source"][name]: raise RuntimeError("Interval engine changed")
    for key in ("d1_high_result","d1_independent_result","old_contract","old_proper_source"):
        item=old["inputs"][key]; target=prev/item["path"]
        if digest(target)!=item["sha256"]: raise RuntimeError("Older parent changed: "+key)
        paths[key]=target
    neighborhood_result=json.loads(paths["static_neighborhood_result"].read_text())
    if neighborhood_result["status"]!="COMPLETE" or neighborhood_result["admitted_fraction"]!=1 or neighborhood_result["unresolved_parameter_cells"]:
        raise RuntimeError("Static neighborhood not fully admitted")
    cells=neighborhood_result["terminal_parameter_cells"]
    if len(cells)!=1 or not cells[0]["pass"] or not cells[0]["root"]["pass"]:
        raise RuntimeError("Unexpected static parameter cover")
    cell=cells[0]; root=cell["root"]
    if root["root_box_exact_bounds"]!=CONFIG["A"] or neighborhood_result["frozen_design"]["root_box"]!=CONFIG["A"]:
        raise RuntimeError("Full root tube authority mismatch")
    if neighborhood_result["frozen_design"]["parameter_box"]!=CONFIG["parameter_box"]:
        raise RuntimeError("Full parameter box authority mismatch")
    for name,pair in CONFIG["parameter_box"].items():
        if cell["parameter_cell"][name]!=pair: raise RuntimeError("Parameter cell does not cover full box")
    for engine in ("primary","independent"):
        if not root[engine]["qualified_parametric_interval_newton"] or root[engine]["root_box_event"]["event_bracket_exact"]!=CONFIG["D"]:
            raise RuntimeError("Uniform event-time/root certificate mismatch")
    reviews=["NEIGHBORHOOD_PREFLIGHT_REVIEW.md"]
    binding={"schema":"neighborhood-validated-mode-v1","config":CONFIG,"source":source_hashes(),
             "model_exact":old["model_exact"],"runtime":runtime(),
             "inputs":{key:{"path":os.path.relpath(p,ROOT),"sha256":digest(p)} for key,p in paths.items()},
             "review_sources":{name:digest(ROOT/name) for name in reviews},"utc":now(),
             "science_evaluated_before_freeze":False,"parent_manifest_files_verified":len(entries)}
    atomic(ROOT/"BINDINGS.json",binding,True)
    atomic(ROOT/"FREEZE_RECORD.json",{"utc":now(),"binding_sha256":digest(ROOT/"BINDINGS.json")},True)
    for name in list(binding["source"])+reviews: (ROOT/name).chmod(0o444)
    print(json.dumps({"frozen":True,"binding_sha256":digest(ROOT/"BINDINGS.json")},indent=2))


def sign(bounds):
    if bounds["lo_exact"] is None: return 0
    return 1 if fmpq(bounds["lo_exact"])>0 else -1 if fmpq(bounds["hi_exact"])<0 else 0


def endpoints_pass(results):
    if len(results)<4 or any(x["status"]!="COMPLETE" for x in results[:4]): return False
    f=[x["determinant"] for x in results[:4]]
    opposite=sign(f[0])*sign(f[1])==-1 and sign(f[2])*sign(f[3])==-1
    compatible=all(max(fmpq(f[j]["lo_exact"]),fmpq(f[j+2]["lo_exact"]))<=
                   min(fmpq(f[j]["hi_exact"]),fmpq(f[j+2]["hi_exact"])) for j in (0,1))
    return opposite and compatible


def run(output):
    binding,guard=authenticate()
    if (output/"RESULT.json").exists() or (output/"FAILURE.json").exists() or (output/"TERMINAL.json").exists():
        raise RuntimeError("Terminal/failed job must not restart")
    output.mkdir(parents=True,exist_ok=True)
    lock=output/"RUN.lock"
    import fcntl
    lockstream=lock.open("a+")
    fcntl.flock(lockstream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    start=time.monotonic()
    state=load_checkpoint(output,guard) if (output/"LATEST.json").exists() else {
        "task_index":0,"cell_index":0,"results":[],"elapsed_seconds":0.0,"started_utc":now()}
    prior_elapsed=state["elapsed_seconds"]
    try:
        while state["task_index"]<6:
            index=state["task_index"]
            if index==4 and not endpoints_pass(state["results"]): break
            task=CONFIG["task_order"][index]; engine,kind=task.split("_")
            # Atomic task publication can precede the following checkpoint.
            # Recover that committed unit without recomputing it after a crash.
            if (output/(task+".json")).exists():
                committed=json.loads((output/(task+".json")).read_text())
                body={k:v for k,v in committed.items() if k!="task_record_digest"}
                if committed["guard"]!=guard or committed["task"]!=task or fingerprint(body)!=committed["task_record_digest"]:
                    raise RuntimeError("Committed task integrity mismatch")
                state["results"].append(committed); state["task_index"]+=1; state["cell_index"]=0
                state["elapsed_seconds"]=prior_elapsed+time.monotonic()-start
                save_checkpoint(output,state,guard)
                continue
            mod=importlib.import_module(engine+"_interval")
            h=fmpq(2,CONFIG[engine+"_steps"])
            Dlo,Dhi=map(fmpq,CONFIG["D"])
            if state["cell_index"]==0:
                A=mod.interval(*map(fmpq,CONFIG["A"]))
                mu=mod.interval(*map(fmpq,CONFIG["mu"])) if kind=="strip" else arb(fmpq(CONFIG["mu"][kind=="high"]))
                model=dict(binding["model_exact"])
                for name,pair in CONFIG["parameter_box"].items():
                    model[name]=mod.interval(*map(fmpq,pair))
                y,p=mod.initial(A,mu,model)
                sector=mod.interval(*map(fmpq,CONFIG["mu"]))+4*p["k"]
                if not p["k"].lower()>0 or not sector.upper()<0: raise RuntimeError("Curvature/exceptional-sector gate failed")
                state.update({"state":y,"params":p,"total_cells":int(math.ceil(Dhi/h)),"event":None,
                              "event_cells":[],"extrema":{},"max_picard_iterations":0,
                              "sector":enclosure(sector),"K":enclosure(p["k"]),"B0":enclosure(p["B0"])})
            try:
                while state["cell_index"]<state["total_cells"]:
                    j=state["cell_index"]; s=j*h
                    y,cell=mod.step(state["state"],h,state["params"])
                    geo=mod.geometry(cell,state["params"])
                    if not all(v.is_finite() for v in y+list(geo.values())):
                        raise ArithmeticError("Nonfinite cell enclosure")
                    if not contains_zero(geo["constraint"]) or not contains_zero(geo["first_integral"]):
                        raise RuntimeError("Analytic consistency identity escaped its interval enclosure")
                    if not geo["warp_squared"].lower()>0:
                        raise ArithmeticError("Positive warp not enclosed")
                    for key in ("W","psi","f"):
                        state["extrema"][key]=mod.hull(state["extrema"][key],geo[key]) if key in state["extrema"] else geo[key]
                    if s+h>=Dlo and s<=Dhi:
                        a=max(fmpq(0),Dlo-s); b=min(h,Dhi-s)
                        event_y=mod.range_on_cell(cell,a,b)
                        F=mod.determinant(event_y,state["params"])
                        state["event"]=F if state["event"] is None else mod.hull(state["event"],F)
                        state["event_cells"].append({"index":j,"s_exact":str(s),"lo_exact":str(s+a),"hi_exact":str(s+b)})
                    state["state"]=y; state["cell_index"]=j+1
                    state["max_picard_iterations"]=max(state["max_picard_iterations"],cell["picard_iterations"])
                    if state["cell_index"]%CONFIG["checkpoint_cells"]==0:
                        state["elapsed_seconds"]=prior_elapsed+time.monotonic()-start
                        save_checkpoint(output,state,guard)
                result={"task":task,"status":"COMPLETE","cells":state["cell_index"],
                        "determinant":enclosure(state["event"]),"event_cover":state["event_cells"],
                        "extrema":{k:enclosure(v) for k,v in state["extrema"].items()},
                        "max_picard_iterations":state["max_picard_iterations"],
                        "K":state["K"],"B0":state["B0"],"sector":state["sector"],
                        "native_final_state":pack(state["state"])}
                if kind=="strip":
                    psi=state["extrema"]["psi"]; W=state["extrema"]["W"]
                    psilo,psihi=mod.bounds(psi); Wlo,Whi=mod.bounds(W)
                    certified=psilo>0
                    result["separation_qualified"]=bool(certified)
                    if certified:
                        Zlower=12*arb(Dlo)*(2*arb(Wlo)).exp()*arb(psilo)**2
                        result["Z_lower_bound"]=enclosure(Zlower)
                        result["deltaD_bound"]=enclosure(mod.interval(-2*Dhi*psihi,-2*Dlo*psilo))
                        result["separation_qualified"] &= bool(Zlower.lower()>0 and fmpq(result["deltaD_bound"]["hi_exact"])<0)
            except (ArithmeticError,RuntimeError) as error:
                result={"task":task,"status":"ENCLOSURE_UNRESOLVED","cells":state["cell_index"],
                        "reason":str(error),"native_last_state":pack(state["state"])}
            result["utc"]=now(); result["guard"]=guard
            result["task_record_digest"]=fingerprint(result)
            atomic(output/(task+".json"),result,True)
            state["results"].append(result); state["task_index"]+=1; state["cell_index"]=0
            state["elapsed_seconds"]=prior_elapsed+time.monotonic()-start
            save_checkpoint(output,state,guard)
            print(json.dumps({"task":task,"status":result["status"],"elapsed":state["elapsed_seconds"],
                              "determinant":result.get("determinant"),"separation":result.get("separation_qualified")}),flush=True)
        authenticate()
        ep=endpoints_pass(state["results"])
        strip=ep and len(state["results"])==6 and all(x.get("separation_qualified",False) for x in state["results"][4:])
        classification=("NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_ON_STATIC_PARAMETER_NEIGHBORHOOD" if strip else
                        "NEGATIVE_SCALAR_EIGENVALUE_CERTIFIED_ON_STATIC_PARAMETER_NEIGHBORHOOD_RADION_OVERLAP_UNRESOLVED" if ep else "NEIGHBORHOOD_VALIDATED_MODE_UNRESOLVED")
        result={"status":"COMPLETE","classification":classification,"producer_provisional_pending_audit":True,
                "endpoint_certificate":ep,"uniform_separation_certificate":strip,"guard":guard,
                "started_utc":state["started_utc"],"completed_utc":now(),
                "elapsed_seconds":prior_elapsed+time.monotonic()-start,"config":CONFIG,"tasks":state["results"]}
        atomic(output/"RESULT.json",result,True)
        atomic(output/"TERMINAL.json",{"status":"COMPLETE","classification":classification,"guard":guard,
              "result_sha256":digest(output/"RESULT.json"),"completed_utc":now()},True)
        atomic(output/"PROGRESS.json",{"state":"COMPLETE","classification":classification,"utc":now(),"guard":guard})
    except KeyboardInterrupt:
        # The last completed cell checkpoint is already durable. Never publish
        # a partly mutated in-flight cell as resumable state.
        atomic(output/"PROGRESS.json",{"state":"STOPPED_RECOVERABLE","utc":now(),"guard":guard,
                                      "resume_from":"LATEST.json"})
        raise
    except BaseException as error:
        atomic(output/"FAILURE.json",{"status":"TECHNICAL_INCOMPLETE","error":repr(error),"traceback":traceback.format_exc(),
                                      "utc":now(),"guard":guard},True)
        raise


def main():
    ctx.prec=CONFIG["bits"]; ctx.threads=1
    if {k:os.environ.get(k) for k in ENV}!=ENV:
        raise RuntimeError("Frozen environment not set")
    parser=argparse.ArgumentParser(); parser.add_argument("mode",choices=["preflight","freeze","run","control-child"])
    parser.add_argument("path",type=Path); args=parser.parse_args()
    if args.mode=="preflight": preflight(args.path)
    elif args.mode=="freeze": freeze(args.path)
    elif args.mode=="run": run(args.path)
    else:
        state=load_checkpoint(args.path,"analytic-control-v1")
        mod=importlib.import_module(state["engine"]+"_interval")
        y,_=mod.step(state["state"],state["step"],state["params"])
        print(json.dumps({"digest":fingerprint(pack(y))}))


if __name__=="__main__": main()
