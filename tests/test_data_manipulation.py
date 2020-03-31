# -*- coding: utf-8 -*-

import os
import unittest

import numpy as np

from src.data_manipulation import Saveable

class TestObject:
    def __init__(self):
        self.data = [0]
    
    def run(self):
        self.data += [0]

class TestSaveable(unittest.TestCase):
        
    def setUp(self,verbose=False):
        np.random.seed(1701) # NCC-1701-D
        self.data_array = np.random.uniform(0, 1, size=2**5)
        self.data_obj = TestObject()
        self.path_here = os.path.dirname(os.path.abspath(__file__))
    
    def test_saving_objects(self):
        path = os.path.join(self.path_here, "data")
        packet = Saveable("test_Saveable", path=path)
        data = [self.data_array, self.data_obj]

        packet.save(data=data)

        file_path = os.path.join(self.path_here, "data", "test_Saveable.pkl")
        self.assertTrue(os.path.exists(file_path))

    def check_saved_data(self):
        path = os.path.join(self.path_here, "data")
        packet = Saveable("test_Saveable", path=path)
        data = [self.data_array, self.data_obj]

        data_loaded = packet.load()

        self.assertEqual(data, data_loaded)
