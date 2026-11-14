"""Run a frozen job list on at most six concurrent single-thread processes.

Each job runs `/usr/bin/python3.14 -I -B boot.py ENTRY` in its own directory,
with stdout.json, stderr.txt, source_sha256.txt and exec.json beside it.
UTC stamps come from `date -u` at write time.  A job whose dependency did not
exit 0, or whose input preparation failed, is recorded as skipped and never
run.  No job starts after the frozen launch cutoff; running jobs finish.

usage: run_jobs.py JOBS_JSON LOG_PATH
"""
import hashlib
import json
import os
import subprocess
import sys
import time

PYTHON = "/usr/bin/python3.14"
MAX_PARALLEL = 6
LAUNCH_CUTOFF_UTC = "2026-11-14T09:15:00Z"
JOB_TIMEOUT_S = 600
ENV = dict(os.environ, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
OUTPUT_NAMES = {"stdout.json", "stderr.txt", "exec.json", "source_sha256.txt", "prepare.json"}


def utc():
    return subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], text=True).strip()


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def hash_sources(job_dir):
    lines = []
    for root, dirs, files in os.walk(job_dir):
        dirs[:] = sorted(d for d in dirs if d not in ("test1_v3", "__pycache__"))
        for name in sorted(files):
            if name in OUTPUT_NAMES or not (name.endswith(".py") or name.endswith(".json")):
                continue
            path = os.path.join(root, name)
            lines.append(f"{sha256(path)}  {os.path.relpath(path, job_dir)}")
    with open(os.path.join(job_dir, "source_sha256.txt"), "w") as handle:
        handle.write("\n".join(lines) + "\n")


def write_json(path, value):
    with open(path, "w") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)


class Runner:
    def __init__(self, jobs, log_path):
        for job in jobs:
            for name in ("exec.json", "stdout.json", "prepare.json"):
                if os.path.exists(os.path.join(job["dir"], name)):
                    raise RuntimeError(f"STAGE_NOT_FRESH {job['name']} already has {name}")
        self.jobs = {job["name"]: job for job in jobs}
        self.order = [job["name"] for job in jobs]
        self.state = {name: "pending" for name in self.order}
        self.running = {}
        self.log = open(log_path, "a")

    def note(self, text):
        self.log.write(f"{utc()} {text}\n")
        self.log.flush()

    def skip(self, name, reason):
        job = self.jobs[name]
        self.state[name] = "skipped"
        write_json(os.path.join(job["dir"], "exec.json"),
                   {"job": name, "status": "SKIPPED", "reason": reason, "recorded_utc": utc()})
        self.note(f"SKIP {name}: {reason}")

    def prepare(self, name):
        job = self.jobs[name]
        spec = job.get("prepare")
        if not spec:
            return True
        command = [PYTHON, "-I", "-B", spec["script"]] + spec["args"]
        done = subprocess.run(command, capture_output=True, text=True, env=ENV)
        write_json(os.path.join(job["dir"], "prepare.json"),
                   {"command": command, "exit": done.returncode, "stdout": done.stdout,
                    "stderr": done.stderr, "recorded_utc": utc()})
        return done.returncode == 0

    def start(self, name):
        job = self.jobs[name]
        hash_sources(job["dir"])
        started = utc()
        out = open(os.path.join(job["dir"], "stdout.json"), "w")
        err = open(os.path.join(job["dir"], "stderr.txt"), "w")
        process = subprocess.Popen([PYTHON, "-I", "-B", "boot.py", job["entry"]], cwd=job["dir"],
                                   stdout=out, stderr=err, env=ENV)
        self.running[name] = (process, started, time.monotonic(), out, err)
        self.state[name] = "running"
        self.note(f"START {name} pid={process.pid}")

    def reap(self):
        for name, (process, started, t0, out, err) in list(self.running.items()):
            pid, status, usage = os.wait4(process.pid, os.WNOHANG)
            timed_out = False
            if pid == 0 and time.monotonic() - t0 > JOB_TIMEOUT_S:
                process.kill()
                pid, status, usage = os.wait4(process.pid, 0)
                timed_out = True
            if pid == 0:
                continue
            code = os.waitstatus_to_exitcode(status)
            out.close()
            err.close()
            job = self.jobs[name]
            write_json(os.path.join(job["dir"], "exec.json"),
                       {"job": name, "entry": job["entry"], "dir": job["dir"], "started_utc": started,
                        "finished_utc": utc(), "elapsed_s": time.monotonic() - t0, "exit": code,
                        "timed_out": timed_out, "max_rss_kib": usage.ru_maxrss, "cpu_user_s": usage.ru_utime,
                        "cpu_system_s": usage.ru_stime, "python": PYTHON,
                        "source_hashes": "source_sha256.txt"})
            self.state[name] = "ok" if code == 0 else "failed"
            del self.running[name]
            self.note(f"END {name} exit={code}")

    def ready(self, name):
        deps = self.jobs[name].get("deps", [])
        if any(self.state[d] in ("failed", "skipped") for d in deps):
            return "blocked"
        return "yes" if all(self.state[d] == "ok" for d in deps) else "no"

    def run(self):
        self.note(f"RUNNER BEGIN jobs={len(self.order)} max_parallel={MAX_PARALLEL} cutoff={LAUNCH_CUTOFF_UTC}")
        while True:
            self.reap()
            pending = [n for n in self.order if self.state[n] == "pending"]
            if not pending and not self.running:
                break
            for name in pending:
                verdict = self.ready(name)
                if verdict == "blocked":
                    self.skip(name, "DEPENDENCY_DID_NOT_SUCCEED")
            pending = [n for n in self.order if self.state[n] == "pending"]
            past_cutoff = utc() >= LAUNCH_CUTOFF_UTC
            for name in sorted(pending, key=lambda n: -self.jobs[n].get("priority", 0)):
                if len(self.running) >= MAX_PARALLEL:
                    break
                if self.ready(name) != "yes":
                    continue
                if past_cutoff:
                    self.skip(name, "LAUNCH_CUTOFF_REACHED")
                    continue
                if not self.prepare(name):
                    self.skip(name, "INPUT_PREPARATION_FAILED")
                    continue
                self.start(name)
            time.sleep(0.5)
        counts = {}
        for value in self.state.values():
            counts[value] = counts.get(value, 0) + 1
        self.note(f"RUNNER END {json.dumps(counts, sort_keys=True)}")


def main():
    with open(sys.argv[1]) as handle:
        jobs = json.load(handle)
    Runner(jobs, sys.argv[2]).run()


if __name__ == "__main__":
    main()
