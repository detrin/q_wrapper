# -*- coding: utf-8 -*-

import numpy as np
import sys
from tqdm import tqdm
import pickle
from scipy.integrate import odeint
import scipy.integrate as integrate
import scipy

import quantarhei as qr

# from quantarhei import printlog as print
# from quantarhei.utils.vectors import X

from quantarhei import Molecule
from quantarhei import Mode
from quantarhei import Aggregate

from matplotlib import rc
from math import factorial
import matplotlib.pyplot as plt
from celluloid import Camera

from toolkit import Timer
from operations import *
from data_process import *
from plotting import *
from building import calculate_FcProd, diagonalize


def make_video_wrapper(args):
    """Video wrapper in case we want to run small parts of video maker."""
    agg_name, settings, t0, t1, N, building_fun, video_name, vid_num = args
    t_lin = np.linspace(t0, t1, N + 1, endpoint=True)
    t0, t1 = t_lin[vid_num], t_lin[vid_num + 1]

    make_video(
        agg_name, settings, t0, t1, N, building_fun, video_name + "_" + str(vid_num)
    )


def make_video(args):
    """Make video from defined settings. """
    # Load main vars
    agg_name, settings, t0, t1, N, building_fun, video_name = args
    Nmol = settings["Nmol"]
    Nvib_0 = settings["Nvib_0"]
    Nvib_1 = settings["Nvib_1"]
    print("loading aggregate ...")
    agg = load_save(agg_name, building_fun, args=(settings,))
    print("loading eigenvecs and eigenvalues ...")
    H = agg.get_Hamiltonian()
    HH = H.data
    w, v, v_i = load_save(agg_name + "_diag", diagonalize, args=(HH,))

    # Set initial condition
    print("setting initial condition ...")
    Amp = 1
    psi_0 = np.zeros((HH.shape[0]), dtype="complex128")
    wave_gauss = lambda q: gaussian(q, -2.0, 0.5, Amp)
    for n in range(Nvib_0):
        result = integrate.quad(lambda q: get_psi_part(n, q) * wave_gauss(q), -100, 100)
        psi_t_i = agg.vibsigs.index(((0, 0, 0), (n, 0, 0)))
        psi_0[psi_t_i] = result[0]
    wave_gauss = lambda q: gaussian(q, 2.0, 0.5, Amp)
    for n in range(Nvib_1):
        result = integrate.quad(lambda q: get_psi_part(n, q) * wave_gauss(q), -100, 100)
        psi_t_i = agg.vibsigs.index(((0, 1, 0), (0, n, 0)))
        # psi_0[psi_t_i] = result[0]

    # Set options for fig capture
    q_min, q_max, q_num = -5, 5, 100
    q_lin = np.linspace(q_min, q_max, q_num)
    fig, axs = plt.subplots(2, Nmol)
    fig.set_size_inches((4 * Nmol, 6))
    camera = Camera(fig)

    # Propagate Schrodinger with eigenvalues
    for psi_t in tqdm(
        schrodinger_propagate(psi_0=psi_0, H=HH, t0=t0, t1=t1, N=N, w=w, v=v, v_i=v_i),
        total=N,
    ):
        st_prob = get_vibrational_positions(agg, psi_t, Nmol, Nvib_0, Nvib_1)
        q_prob = get_q_from_st_prob(st_prob, q_min, q_max, q_num)

        for mol_i in range(Nmol):
            for st in [0, 1]:
                plot_func(
                    axs[st, mol_i],
                    q_lin,
                    q_prob[mol_i, st],
                    yoffset=0,
                    xoffset=0,
                    y_lim=1.5,
                    color=st,
                )
        camera.snap()

    # Make video
    animation = camera.animate(interval=100)
    animation.save("video/" + video_name + ".mp4")

    return True


def propagate_red_dens_mat(args):
    """Evaluate only reduced density matrix."""
    agg_name, settings, t0, t1, N, building_fun = args

    # Load main vars
    Nmol = settings["Nmol"]
    Nvib_0 = settings["Nvib_0"]
    Nvib_1 = settings["Nvib_1"]
    print("loading aggregate ...")
    agg = load_save(agg_name, building_fun, args=(settings,))
    print("loading FcProd ...")
    FcProd = load_save(agg_name + "_FcProd", calculate_FcProd, args=(agg,))
    print("loading eigenvecs and eigenvalues ...")
    H = agg.get_Hamiltonian()
    HH = H.data
    w, v, v_i = load_save(agg_name + "_diag", diagonalize, args=(HH,))

    print("setting initial condition ...")
    Amp = 1
    psi_0 = np.zeros((HH.shape[0]), dtype="complex128")
    wave_gauss = lambda q: gaussian(q, -2.0, 0.5, Amp)
    for n in range(Nvib_0):
        result = integrate.quad(lambda q: get_psi_part(n, q) * wave_gauss(q), -100, 100)
        psi_t_i = agg.vibsigs.index(((1, 0, 0), (n, 0, 0)))
        psi_0[psi_t_i] = result[0]
    wave_gauss = lambda q: gaussian(q, 2.0, 0.5, Amp)
    for n in range(Nvib_1):
        result = integrate.quad(lambda q: get_psi_part(n, q) * wave_gauss(q), -100, 100)
        psi_t_i = agg.vibsigs.index(((1, 0, 0), (0, n, 0)))
        # psi_0[psi_t_i] = result[0]

    selected_el_st = []
    for n in range(agg.Nel):
        for i_n in agg.vibindices[n]:
            state = agg.vibsigs[i_n]
            if sum(state[0]) == 1 and n not in selected_el_st:
                selected_el_st.append(n)

    print("runnning simulation ...")
    red_density_mat_l = []
    for psi_t in tqdm(
        schrodinger_propagate(psi_0=psi_0, H=HH, t0=t0, t1=t1, N=N, w=w, v=v, v_i=v_i),
        total=N,
    ):
        red_density_mat, FcProd = trace_over_vibrations(
            agg, psi_t, FcProd=FcProd, selected_el_st=selected_el_st
        )
        red_density_mat_l.append(red_density_mat)

    return red_density_mat_l
