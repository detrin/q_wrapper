# -*- coding: utf-8 -*-

import sys
import pickle

from q_wrapper.src.core import parallel

import main_exec

with open("transfer/task.pkl", "rb") as f:
    fun_str, fun_args = pickle.load(f)

fun = getattr(main_exec, fun_str)
# eval('from main_exec import '+fun_str)

args = list(map(lambda s: s.lower(), sys.argv))
pages = None
if "--task_num" in args:
    task_num = int(args[args.index("--task_num") + 1])

n_jobs = None
if "--n_jobs" in args:
    n_jobs = int(args[args.index("--n_jobs") + 1])

if (n_jobs is not None) and task_num is not None:
    results = parallel(fun, fun_args[task_num], n_jobs=n_jobs)

elif (n_jobs is None or n_jobs == 1) and task_num is not None:
    results = fun(fun_args[task_num])

else:
    results = []

with open("transfer/results_" + str(task_num) + ".pkl", "wb") as f:
    pickle.dump(results, f)
