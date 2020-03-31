# -*- coding: utf-8 -*-

import sys
import os
import unittest
import time

import numpy as np

from src.data_manipulation import Saveable, loadSave


class TestObject:
    def __init__(self):
        self.data = [0]

    def run(self):
        self.data += [0]


def test_fun(num):
    return (
        "1-7-3-4-6-7-3-2-1-4-7-6-Charlie-3-2-7-8-9-7-7-7-6-4-3-Tango-7-"
        + "3-2-Victor-7-3-1-1-7-8-8-8-7-3-2-4-7-6-7-8-9-7-6-4-3-7-6"
    )


class TestSaveable(unittest.TestCase):
    def setUp(self):
        np.random.seed(1701)  # NCC-1701-D
        self.data_array = np.random.uniform(0, 1, size=2 ** 5)
        self.data_obj = TestObject()
        self.path_here = os.path.dirname(os.path.abspath(__file__))
        self.path_data = os.path.join(self.path_here, "data")

    def test_saving_objects(self):
        packet = Saveable("test_Saveable", path=self.path_data)
        data = [self.data_array, self.data_obj]

        packet.save(data=data)

        file_path = os.path.join(self.path_data, "test_Saveable.pkl")
        self.assertTrue(os.path.exists(file_path))

    def check_saved_data(self):
        packet = Saveable("test_Saveable", path=self.path_data)
        data = [self.data_array, self.data_obj]

        data_loaded = packet.load()

        self.assertEqual(data, data_loaded)


class TestLoadSave(unittest.TestCase):
    def setUp(self):
        self.path_here = os.path.dirname(os.path.abspath(__file__))
        self.path_data = os.path.join(self.path_here, "data")

    def test_saving(self):
        file_path = os.path.join(self.path_data, "test_loadSave.pkl")
        if os.path.exists(file_path):
            os.remove(file_path)
        loadSave(
            test_fun, "test_loadSave", force_save=False, args=(5,), path=self.path_data
        )

        self.assertTrue(os.path.exists(file_path))

    def test_loading(self):
        data = test_fun(5)
        data_loaded = loadSave(
            test_fun, "test_loadSave", force_save=False, args=(5,), path=self.path_data
        )

        self.assertEqual(data, data_loaded)
