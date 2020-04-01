# -*- coding: utf-8 -*-
"""Aggregate building using quantarhei package."""

import numpy as np
import sys
from tqdm import tqdm
import pickle
from scipy.integrate import odeint
import scipy.integrate as integrate
import scipy

import quantarhei as qr

from quantarhei import Molecule
from quantarhei import Mode
from quantarhei import Aggregate

from matplotlib import rc
from math import factorial
import matplotlib.pyplot as plt
from celluloid import Camera


def build_aggregate_1(settings):
    """Example function for building aggregate no. 1"""
    mol_l = []
    mod_l = []

    with qr.energy_units("1/cm"):
        for ind in range(settings["Nmol"]):
            mol = Molecule([0.0, settings["E1"]])
            # mol1.set_dipole(0,1,[1.0, 0.0, 0.0])
            # mol1.set_transition_width((0,1), width)

            mod = Mode(settings["omega"])
            mol.add_Mode(mod)
            mod.set_nmax(0, settings["Nvib_0"])
            mod.set_nmax(1, settings["Nvib_1"])
            mod.set_HR(1, settings["HR"])
            mol_l.append(mol)
            mod_l.append(mod)

    agg = Aggregate(molecules=mol_l)
    for ind in range(settings["Nmol"] - 1):
        agg.set_resonance_coupling(ind, ind + 1, settings["JJ"])
    agg.set_resonance_coupling(settings["Nmol"] - 1, 0, settings["JJ"])

    agg.build(mult=1)

    return agg


def build_aggregate_2(settings):
    """Example function for building aggregate no. 2"""
    mol_l = []
    mod_l = []

    with qr.energy_units("1/cm"):
        for ind in range(settings["Nmol"]):
            mol = Molecule([0.0, settings["E1"]])
            # mol1.set_dipole(0,1,[1.0, 0.0, 0.0])
            # mol1.set_transition_width((0,1), width)

            mod = Mode(settings["omega"])
            mol.add_Mode(mod)
            mod.set_nmax(0, settings["Nvib_0"])
            mod.set_nmax(1, settings["Nvib_1"])
            mod.set_HR(1, settings["HR"])
            mol_l.append(mol)
            mod_l.append(mod)

    agg = Aggregate(molecules=mol_l)
    for ind in range(settings["Nmol"] - 1):
        agg.set_resonance_coupling(ind, ind + 1, settings["JJ"])
    # agg.set_resonance_coupling(settings["Nmol"]-1, 0, settings["JJ"])

    agg.build(mult=1)

    return agg


def calculate_FcProd(agg):
    """Calculate product of all Frack-Condon factors for tracing over vibration."""
    FcProd = np.zeros_like(agg.FCf)
    for i in range(FcProd.shape[0]):
        for j in range(FcProd.shape[1]):
            for i_g in range(agg.Nb[0]):
                FcProd[i, j] += agg.FCf[i_g, i] * agg.FCf[j, i_g]

    return FcProd


def diagonalize(A):
    """Shortcut for digitalization call."""
    w, v = np.linalg.eig(A)
    v_i = np.linalg.inv(v)
    return w, v, v_i
