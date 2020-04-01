# -*- coding: utf-8 -*-
"""Simple plotting functions."""

import sys
import numpy as np

from matplotlib import rc
import matplotlib.pyplot as plt


def show_hamiltonian(H):
    """Plot picture from hamiltonian in order to inspect it visually."""
    data = np.log((H.data + 1))
    plt.imshow(data, interpolation="nearest")
    plt.colorbar()
    plt.show()


def print_matrix(A, precision=2, linewidth=100, threshold=None):
    """Output np matrix with set precision."""
    if threshold is None:
        threshold = sys.maxsize
    with np.printoptions(
        precision=precision,
        suppress=True,
        threshold=sys.maxsize,
        formatter={"float": "{:0.2f}".format},
        linewidth=linewidth,
    ):
        print(A)


def plot_wavepocket_of_monomers_simple(
    ax, q, f, scaling=1, yoffset=0, xoffset=0, y_lim=1, color=0
):
    """Plot f*scaling with offset yoffset.

    The curve above the offset is filled with COLOUR1; the curve below is
    filled with COLOUR2.

    """
    rc("font", **{"family": "serif", "serif": ["Computer Modern"], "size": 14})
    rc("text", usetex=True)

    # Colours of the positive and negative parts of the wavefunction
    if color == 0:
        # ground state
        COLOUR1 = (0.329, 0.2, 0.921, 1.0)
        COLOUR2 = (0.286, 0.227, 0.552, 1.0)
    elif color == 1:
        # exited state
        COLOUR1 = (0.886, 0.156, 0.2391, 1.0)
        COLOUR2 = (0.568, 0.152, 0.2, 1.0)

    ax.plot(q, f * scaling + yoffset, color=COLOUR1)
    ax.fill_between(
        q + xoffset, f * scaling + yoffset, yoffset, f > 0.0, color=COLOUR1, alpha=0.5
    )
    ax.fill_between(
        q + xoffset, f * scaling + yoffset, yoffset, f < 0.0, color=COLOUR2, alpha=0.5
    )
    ax.set_ylim(-y_lim, y_lim)
