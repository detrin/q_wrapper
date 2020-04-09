# -*- coding: utf-8 -*-

import scipy.integrate as integrate

import quantarhei as qr

from quantarhei import Molecule
from quantarhei import Mode
from quantarhei import Aggregate


def build_testing_aggregate():
    """Testing aggregate for unit tests."""
    # Number of molecules
    Nmol = 2
    # energy of molecule one
    E1 = 12500.0
    # energy gap to molecule two
    Edelta = 100.0
    # coupling between the two molecules
    JJ = 30.0
    # frequency of the vibrational mode
    omega = 110.0
    # Huan-Rhys factor
    HR = 0.01
    # transition width
    width = 80
    # max nvib states
    Nvib_0 = 3
    Nvib_1 = 3

    mol_l = []
    mod_l = []

    with qr.energy_units("1/cm"):
        for ind in range(Nmol):
            mol = Molecule([0.0, E1])
            mol.set_dipole(0, 1, [1.0, 0.0, 0.0])
            mol.set_transition_width((0, 1), width)

            mod = Mode(omega)
            mol.add_Mode(mod)
            mod.set_nmax(0, Nvib_0)
            mod.set_nmax(1, Nvib_1)
            mod.set_HR(1, HR)
            mol_l.append(mol)
            mod_l.append(mod)

    agg = Aggregate(molecules=mol_l)
    for ind in range(Nmol - 1):
        agg.set_resonance_coupling(ind, ind + 1, JJ)
    agg.set_resonance_coupling(Nmol - 1, 0, JJ)

    agg.build(mult=1)

    return agg
