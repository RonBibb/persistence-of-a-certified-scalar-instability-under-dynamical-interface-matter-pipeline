"""Path-only bootstrap.

`python -I` drops the script directory from sys.path, so this adds the job
directory and the pinned python-flint 0.9.0 runtime, sets one Arb thread and
runs the named entry as __main__ from the job directory.
"""
import os
import runpy
import sys

RUNTIME = "/home/parallels/research-runtimes/protocol406-python-flint-0.9.0"

job_dir = os.getcwd()
sys.path.insert(0, RUNTIME)
sys.path.insert(0, job_dir)

import flint  # noqa: E402

flint.ctx.threads = 1
runpy.run_path(os.path.join(job_dir, sys.argv[1]), run_name="__main__")
