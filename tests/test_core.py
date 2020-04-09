# -*- coding: utf-8 -*-

import sys
import unittest

from contextlib import contextmanager
from io import StringIO

from src.core import parallel

N = 10


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def collatz(n):
    step_num = 0
    while n > 1:
        step_num += 1
        if n % 2:
            n = 3 * n + 1
        else:
            n = n // 2
    return step_num


class TestParallel(unittest.TestCase):
    def setUp(self):
        self.data = [x for x in range(N)]

    def test_parallel(self):
        data = []
        for ind in range(N):
            data.append(collatz(ind))

        args = [x for x in range(N)]
        data_new = parallel(collatz, args)

        self.assertEqual(data, data_new)

        with captured_output() as (out, err):
            data_new = parallel(collatz, args, verbose=True)

        self.assertEqual(data, data_new)
