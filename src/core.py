# -*- coding: utf-8 -*-

import sys
import os
import pickle

from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool
from tqdm import tqdm


def parallel(function, array, n_jobs=4, use_kwargs=False):
    if n_jobs == 1:
        return [function(**a) if use_kwargs else function(a) for a in tqdm(array)]

    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        if use_kwargs:
            futures = [pool.submit(function, **a) for a in array]
        else:
            futures = [pool.submit(function, a) for a in array]
        kwargs = {
            "total": len(futures),
            "unit": "it",
            "unit_scale": True,
            "leave": True,
        }
        for f in tqdm(as_completed(futures), **kwargs):
            pass

    out = []
    for i, future in tqdm(enumerate(futures)):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return out
