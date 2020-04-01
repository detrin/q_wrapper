# -*- coding: utf-8 -*-

import sys
import os
import unittest
import time
import numpy as np

from os import listdir
from os.path import isfile, join


def load_termina_output(output_name):
    """Load test outputs from files in terminal outputs/."""
    path_here = os.path.dirname(os.path.abspath(__file__))
    target_dir = join(path_here, "terminal_outputs")

    filenames = [f for f in listdir(target_dir) if isfile(join(target_dir, f))]

    if output_name + ".txt" not in filenames:
        raise Exception("Output name not found in tests/terminal_outputs/")

    with open(join(target_dir, output_name + ".txt"), "r") as f:
        s = ""
        for row in f:
            s += row
    return s
