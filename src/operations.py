# -*- coding: utf-8 -*-
"""All new operations needed for simulations in plain structure."""

import numpy as np
from math import factorial
import matplotlib.pyplot as plt

from .core import parallel


def N(v):
    """Normalization constant fro eigenvectors of LHO."""
    return 1.0 / np.sqrt(np.sqrt(np.pi) * 2 ** v * factorial(v))


def get_E(v):
    return v + 0.5


def make_Hr(VMAX):
    """Return a list of np.poly1d objects representing Hermite polynomials."""

    # Define the Hermite polynomials up to order VMAX by recursion:
    Hr = [None] * (VMAX + 1)
    Hr[0] = np.poly1d([1.0,])
    Hr[1] = np.poly1d([2.0, 0.0])
    for v in range(2, VMAX + 1):
        Hr[v] = Hr[1] * Hr[v - 1] - 2 * (v - 1) * Hr[v - 2]
    return Hr


def get_psi_part(v, q):
    """Return the harmonic oscillator wavefunction for level v on grid q."""
    Hr = make_Hr(v + 1)
    return N(v) * Hr[v](q) * np.exp(-q * q / 2.0)


def get_psi(q, C):
    """Return the harmonic oscillator wavefunction for level v on grid q."""
    Hr_l = make_Hr(len(C))
    amp = 0
    for n, C_n in enumerate(C):
        amp += C_n * 1.0 / np.sqrt(np.sqrt(np.pi) * 2 ** n * factorial(n)) * Hr_l[n](q)
    amp *= np.exp(-q * q / 2.0)
    return amp


def get_turning_points(v):
    """Return the classical turning points for state v."""
    qmax = np.sqrt(2.0 * get_E(v + 0.5))
    return -qmax, qmax


def get_potential(q):
    """Return potential energy on scaled oscillator displacement grid q."""
    return q ** 2 / 2


def schrodinger_propagate(
    psi_0=None, H=None, t0=None, t1=None, N=None, w=None, v=None, v_i=None
):
    """Propagate state of system with hamiltonian in time."""
    if psi_0 is None:
        raise Exception("Please state initial wavefunction.")

    if H is None:
        raise Exception("Please state hamiltonian.")

    if t0 is None:
        raise Exception("Please state t0.")

    if t1 is None:
        raise Exception("Please state t1.")

    if N is None:
        raise Exception("Please state N.")

    if w is None or v is None or v_i is None:
        w, v = np.linalg.eig(H)
        v_i = np.linalg.inv(v)

    t_lin = np.linspace(t0, t1, num=N, endpoint=False)

    for t_i in range(N):
        H_t = np.dot(v, np.dot(np.diag(np.exp(-1j * w * t_lin[t_i])), v_i))
        yield np.dot(H_t, psi_0)


def create_trace_B_except(agg, vib_pos):
    """First example of trace over vibraions."""
    heap = []
    positions = []
    for ist in range(agg.Ntot):
        state = agg.vibsigs[ist]
        new_state = [state[0], state[1][vib_pos]]
        if new_state not in heap:
            heap.append(new_state)
            positions.append(ist)

    return positions, heap


def trace_B_except(agg, psi, vib_pos, trace_ind, new_states):
    """First example of trace over vibraions."""
    new_psi = np.zeros((len(trace_ind)), dtype="complex128")
    for ist in range(agg.Ntot):
        state = agg.vibsigs[ist]
        ist_new = new_states.index([state[0], state[1][vib_pos]])
        new_psi[ist_new] += psi[ist]

    return new_psi


def create_trace_E_except(agg, el_pos):
    """First example of trace over electronic states."""
    heap = []
    positions = []
    for ist in range(agg.Ntot):
        state = agg.vibsigs[ist]
        new_state = [state[0][el_pos], state[1]]
        if new_state not in heap:
            heap.append(new_state)
            positions.append(ist)

    return positions, heap


def trace_E_except(agg, psi, el, trace_ind, new_states):
    """First example of trace over electronic states."""
    new_psi = np.zeros((len(trace_ind)), dtype="complex128")
    for ist in range(agg.Ntot):
        state = agg.vibsigs[ist]
        ist_new = new_states.index([state[0][el_pos], state[1]])
        new_psi[ist_new] += psi[ist]

    return new_psi


def create_trace_total(agg, el_pos, vib_pos):
    "Example of total trace."
    heap = []
    positions = []
    for ist in range(agg.Ntot):
        state = agg.vibsigs[ist]
        new_state = [state[0][el_pos], state[1][vib_pos]]
        if new_state not in heap:
            heap.append(new_state)
            positions.append(ist)

    return positions, heap


def trace_total(agg, psi, el_pos, vib_pos, trace_ind, new_states):
    "Example of total trace."
    new_psi = np.zeros((len(trace_ind)), dtype="complex128")
    for ist in range(agg.Ntot):
        state = agg.vibsigs[ist]
        ist_new = new_states.index([state[0][el_pos], state[1][vib_pos]])
        new_psi[ist_new] += psi[ist]

    return new_psi


def gaussian(x, mu, sig, A):
    "Analytical function of gaussian wavepocket."
    return (
        A
        * 1.0
        / (np.sqrt(2.0 * np.pi) * sig)
        * np.exp(-np.power((x - mu) / sig, 2.0) / 2)
    )


def get_vibrational_positions(agg, psi, settings):
    "Get probability of vibrational positions of monomers."
    Nmol, Nvib_0 = settings["Nmol"], settings["Nvib_0"]
    st_prob = np.zeros((Nmol, 2, Nvib_0), dtype="complex128")
    for ist in range(agg.Ntot):
        el_st, vib_st = agg.vibsigs[ist]
        el_st, vib_st = list(el_st), list(vib_st)
        for mol_i in range(Nmol):
            st_prob[mol_i, el_st[mol_i], vib_st[mol_i]] += psi[ist]
    return st_prob


def get_q_from_st_prob(st_prob, q_min, q_max, q_num, absolute=True):
    "Get the coordinate of vibrational positions of monomers."
    q_lin = np.linspace(q_min, q_max, q_num)
    Nmol = st_prob.shape[0]
    q_prob = np.zeros((Nmol, 2, q_num), dtype="float64")

    for mol_i in range(Nmol):
        for st in [0, 1]:
            for q_i in range(q_num):
                if absolute:
                    q_prob[mol_i, st, q_i] = np.absolute(
                        get_psi(q_lin[q_i], st_prob[mol_i, st])
                    )
                else:
                    q_prob[mol_i, st, q_i] = np.real(
                        get_psi(q_lin[q_i], st_prob[mol_i, st])
                    )

    return q_prob


def trace_over_vibrations_core(args):
    "Core function for parallel computations of trace over vibrations."
    agg, psi, FcProd, selected_el_st, n, m = args
    red_density_mat = np.zeros((el_st_len, el_st_len), dtype="complex128")
    for i_n in agg.vibindices[n]:
        for i_m in agg.vibindices[m]:
            red_density_mat[n, m] += np.conj(psi[i_n]) * psi[i_n] * FcProd[i_n, i_m]
    return red_density_mat


def trace_over_vibrations(agg, psi, FcProd=None, selected_el_st=None, n_jobs=1):
    """Trace over vibrations from Schrodinger equation."""
    if FcProd is None:
        FcProd = np.zeros_like(agg.FCf)
        for i in range(FcProd.shape[0]):
            for j in range(FcProd.shape[1]):
                for i_g in range(agg.Nb[0]):
                    FcProd[i, j] += agg.FCf[i_g, i] * agg.FCf[j, i_g]

    if selected_el_st is None:
        el_states = [n for n in range(agg.Nel)]
    else:
        el_states = selected_el_st
    el_st_len = len(el_states)

    red_density_mat = np.zeros((el_st_len, el_st_len), dtype="complex128")
    if n_jobs == 1:
        for n_i in range(el_st_len):
            n = el_states[n_i]
            for i_n in agg.vibindices[n]:
                for m_i in range(el_st_len):
                    m = el_states[m_i]
                    for i_m in agg.vibindices[m]:
                        red_density_mat[n_i, m_i] += (
                            np.conj(psi[i_n]) * psi[i_n] * FcProd[i_n, i_m]
                        )
    else:
        args = []
        for n in el_states:
            for m in el_states:
                # args_part = copy.deepcopy([agg, psi, FcProd, selected_el_st])
                args_part = [agg, psi, FcProd, selected_el_st, n, m]
                args.append(args_part)
        results = parallel(trace_over_vibrations_core, args, n_jobs=n_jobs)
        for parcel in results:
            red_density_mat += parcel

    return red_density_mat, FcProd
