# -*- coding: utf-8 -*-

import os
import unittest

import numpy as np

from src.building import diagonalize, calculate_FcProd
from aggregate_setup import build_testing_aggregate
from src.data_manipulation import Saveable


class TestBuilding(unittest.TestCase):
    def setUp(self):
        self.path_here = os.path.dirname(os.path.abspath(__file__))
        self.path_data = os.path.join(self.path_here, "data")
        packet = Saveable("aggregate", path=self.path_data)
        self.agg = packet.load()

    def test_diagonalize(self):
        data_array = np.array(
            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]], dtype="float64"
        )
        w, v, v_i = diagonalize(data_array)

        w_true = np.array(
            [1.61168440e01, -1.11684397e00, -1.30367773e-15], dtype="float64"
        )
        v_true = np.array(
            [
                [-0.23197069, -0.78583024, 0.40824829],
                [-0.52532209, -0.08675134, -0.81649658],
                [-0.8186735, 0.61232756, 0.40824829],
            ],
            dtype="float64",
        )
        v_i_true = np.array(
            [
                [-0.48295226, -0.59340999, -0.70386772],
                [-0.91788599, -0.24901003, 0.41986593],
                [0.40824829, -0.81649658, 0.40824829],
            ],
            dtype="float64",
        )

        self.assertTrue(np.allclose(w_true, w))
        self.assertTrue(np.allclose(v_true, v))
        self.assertTrue(np.allclose(v_i_true, v_i))

    def test_aggregate_setup(self):
        agg = build_testing_aggregate()
        H = agg.get_Hamiltonian()
        HH = H.data

        H_loaded = self.agg.get_Hamiltonian()
        HH_loaded = H_loaded.data

        self.assertTrue(np.allclose(HH_loaded, HH))

    def test_FcProd(self):
        FcProd = calculate_FcProd(self.agg)

        packet = Saveable("FcProd", path=self.path_data)
        packet.save(data=FcProd)
        FcProd_loaded = packet.load()

        self.assertTrue(np.allclose(FcProd_loaded, FcProd))
