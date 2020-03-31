# -*- coding: utf-8 -*-

import sys
import os
import pickle

from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool
from tqdm import tqdm


def parallel(function, array, n_jobs=4, use_kwargs=False):
    """Funtion for parallel calculations with usage of tqdm progress bar."""
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


def rk4(f, x0, y0, x1, n, *args):
    """Runge-Kutta for pure pythonic solutions. """
    vx = [0] * (n + 1)
    vy = [0] * (n + 1)
    h = (x1 - x0) / float(n)
    vx[0] = x = x0
    vy[0] = y = y0
    for i in range(1, n + 1):
        k1 = h * f(x, y, *args)
        k2 = h * f(x + 0.5 * h, y + 0.5 * k1, *args)
        k3 = h * f(x + 0.5 * h, y + 0.5 * k2, *args)
        k4 = h * f(x + h, y + k3, *args)
        vx[i] = x = x0 + i * h
        vy[i] = y = y + (k1 + k2 + k2 + k3 + k3 + k4) / 6
    return vx, vy
