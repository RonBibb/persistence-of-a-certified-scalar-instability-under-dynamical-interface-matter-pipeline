"""Seal the completed bounded certificate after the independent audit."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT/name).read_text())


def write(name,data):
    path=ROOT/name
    with path.open("x") as stream:
        json.dump(data,stream,sort_keys=True,indent=2,allow_nan=False)
        stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    path.chmod(0o444)


def main():
    if ROOT.name!="lin-central-validated-mode-r1-20261005T172800Z":
        raise RuntimeError("Publication target is not this capsule")
    B=read("BINDINGS.json"); R=read("output/RESULT.json"); A=read("INDEPENDENT_AUDIT.json")
    guard=sha(ROOT/"BINDINGS.json")
    assert guard==R["guard"]==A["guard"]==read("FREEZE_RECORD.json")["binding_sha256"]
    assert guard=="fca1b49a652afc1832e61e31e5e8c47dc86d63144de791211c89372f55a82e00"
    assert A["audit_pass"] and A["classification_independently_derived"]==R["classification"]
    assert A["result_sha256"]==sha(ROOT/"output/RESULT.json")
    assert A["terminal_sha256"]==sha(ROOT/"output/TERMINAL.json")
    assert A["audit_source_sha256"]==sha(ROOT/"postrun_audit.py")
    assert not (ROOT/"output/FAILURE.json").exists()
    for name,expected in (B["source"]|B["review_sources"]).items():
        assert sha(ROOT/name)==expected,name
    for entry in B["inputs"].values():
        assert sha(ROOT/entry["path"])==entry["sha256"],entry["path"]
    required=["POSTRUN_REVIEW.md","INDEPENDENT_AUDIT.json","RESULT_REPORT.md"]
    assert all((ROOT/name).is_file() for name in required)
    now=datetime.now(timezone.utc).isoformat()
    final={"status":"COMPLETE","classification":R["classification"],"independently_accepted":True,
           "evidence_class":"INTERVAL_CERTIFIED_CENTRAL_MODE_EXISTENCE_WITH_NONZERO_SEPARATION_COMPONENT",
           "guard":guard,"sealed_utc":now,"physical_run_seconds":R["elapsed_seconds"],
           "mu_open_interval":["-33/25000","-131/100000"],"validated_cells":sum(t["cells"] for t in R["tasks"]),
           "checkpoint_count":A["checkpoint_count"],"technical_predecessor":"../lin-central-validated-mode-20261005T165817Z",
           "artifacts":{name:sha(ROOT/name) for name in ["output/RESULT.json","output/TERMINAL.json",*required,"postrun_audit.py"]},
           "limits":["one central exact static background","not eigenvalue uniqueness or a full spectrum",
                     "not a continuous parameter neighborhood instability theorem","not nonlinear fate or causal admission",
                     "declared canonical scalar and pure-potential two-wall model only"],
           "successor_launched":False}
    write("RESULT.json",final)
    write("TERMINAL.json",{"status":"COMPLETE","classification":R["classification"],"guard":guard,
                           "result_sha256":sha(ROOT/"RESULT.json"),"audit_sha256":sha(ROOT/"INDEPENDENT_AUDIT.json"),"utc":now})
    files={}
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path.name!="MANIFEST.json":
            if path.suffix==".pyc" or "__pycache__" in path.parts:
                raise RuntimeError("Unintended cache in packet")
            files[str(path.relative_to(ROOT))]={"sha256":sha(path),"bytes":path.stat().st_size}
    write("MANIFEST.json",{"schema":"whole-file-seal-v1","sealed_utc":now,"file_count":len(files),"files":files})
    for rel,entry in files.items():
        assert sha(ROOT/rel)==entry["sha256"]
        (ROOT/rel).chmod(0o444)
    print(json.dumps({"status":"SEALED","classification":R["classification"],"verified_files":len(files),
                      "result_sha256":sha(ROOT/"RESULT.json"),"manifest_sha256":sha(ROOT/"MANIFEST.json")},indent=2))


if __name__=="__main__":
    main()
