# -*- coding: utf-8 -*-

import sys
import os
import unittest
import time
import numpy as np

from contextlib import contextmanager
from io import StringIO

from src.plotting import print_matrix
from read_output import load_termina_output


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestPlotting(unittest.TestCase):
    def setUp(self):
        np.random.seed(1701)  # NCC-1701-D
        self.A = np.random.uniform(0, 1, size=(10, 10))

    def test_setup(self):
        with captured_output() as (out, err):
            print_matrix(self.A, precision=2, linewidth=100, threshold=None)

        output = out.getvalue().strip()
        output_true = load_termina_output("plotting_matrix")

        self.assertEqual(output_true, output)
