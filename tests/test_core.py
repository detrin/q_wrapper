# -*- coding: utf-8 -*-

import sys
import os
import unittest
import time
import numpy as np

from src.core import parallel

N = 10


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
    def SetUp(self):
        np.random.seed(1701)  # NCC-1701-D
        self.data = [x for x in range(N)]

    def test_parallel(self):
        data = []
        for ind in range(N):
            data.append(collatz(ind))

        args = [x for x in range(N)]
        data_new = parallel(collatz, args)

        self.assertEqual(data, data_new)
