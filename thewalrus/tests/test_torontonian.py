# Copyright 2019 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the Torontonian"""
# pylint: disable=no-self-use,redefined-outer-name
import pytest

import numpy as np
from scipy.special import poch, factorial
from thewalrus import tor, threshold_detection_prob
from thewalrus.symplectic import two_mode_squeezing

def gen_omats(l, nbar):
    r"""Generates the matrix O that enters inside the Torontonian for an l mode system
    in which the first mode is prepared in a thermal state with mean photon number nbar
    and the rest in vacuum and are later sent into a Fourier interferometer, i.e. one described
    by a DFT unitary matrix

    Args:
        l (int): number of modes
        nbar (float): mean photon number of the first mode (the only one not prepared in vacuum)

    Returns:
        array: An O matrix whose Torontonian can be calculated analytically.
    """
    A = (nbar / (l * (1.0 + nbar))) * np.ones([l, l])
    O = np.block([[A, 0 * A], [0 * A, A]])
    return O


def torontonian_analytical(l, nbar):
    r"""Return the value of the Torontonian of the O matrices generated by gen_omats

    Args:
        l (int): number of modes
        nbar (float): mean photon number of the first mode (the only one not prepared in vacuum)

    Returns:
        float: Value of the torontonian of gen_omats(l,nbar)
    """
    if np.allclose(l, nbar, atol=1e-14, rtol=0.0):
        return 1.0
    beta = -(nbar / (l * (1 + nbar)))
    pref = factorial(l) / beta
    p1 = pref * l / poch(1 / beta, l + 2)
    p2 = pref * beta / poch(2 + 1 / beta, l)
    return (p1 + p2) * (-1) ** l


def test_torontonian_tmsv():
    """Calculates the torontonian of a two-mode squeezed vacuum
    state squeezed with mean photon number 1.0"""

    mean_n = 1.0
    r = np.arcsinh(np.sqrt(mean_n))
    Omat = np.tanh(r) * np.array([[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]])

    tor_val = tor(Omat)
    assert np.allclose(tor_val.real, 1.0)


def test_torontonian_tmsv_complex_zero_imag_part():
    """Calculates the torontonian of a two-mode squeezed vacuum
    state squeezed with mean photon number 1.0"""

    mean_n = 1.0
    r = np.arcsinh(np.sqrt(mean_n))
    Omat = np.tanh(r) * np.array([[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]])
    Omat = np.complex128(Omat)
    tor_val = tor(Omat)
    assert np.allclose(tor_val.real, 1.0)


def test_torontonian_tmsv_complex():
    """Calculates the torontonian of a two-mode squeezed vacuum
    state squeezed with mean photon number 1.0"""

    mean_n = 1.0
    r = np.arcsinh(np.sqrt(mean_n))
    phase = np.exp(1j * 0.3)
    phasec = np.conj(phase)
    Omat = np.tanh(r) * np.array(
        [[0, 0, 0, phase], [0, 0, phase, 0], [0, phasec, 0, 0], [phasec, 0, 0, 0]]
    )
    tor_val = tor(Omat)
    assert np.allclose(tor_val.real, 1.0)


def test_torontonian_vacuum():
    """Calculates the torontonian of a vacuum in n modes
    """
    n_modes = 5
    Omat = np.zeros([2 * n_modes, 2 * n_modes])
    tor_val = tor(Omat)
    assert np.allclose(tor_val.real, 0.0)


@pytest.mark.parametrize("l", [1, 2, 3, 4, 5])
@pytest.mark.parametrize("nbar", np.arange(0.25, 3, 0.25))
def test_torontononian_analytical_mats(l, nbar):
    """Checks the correct value of the torontonian for the analytical family described by gen_omats"""
    assert np.allclose(torontonian_analytical(l, nbar), tor(gen_omats(l, nbar)))


@pytest.mark.parametrize("r", [0.5, 0.5, -0.8, 1, 0])
@pytest.mark.parametrize("alpha", [0.5, 2, -0.5, 0., -0.5])
def test_disp_torontonian(r, alpha):
    """calculates displaced two mode squeezed state"""

    p00a = np.exp(-2*(abs(alpha)**2 - abs(alpha)**2 * np.tanh(r)))/(np.cosh(r)**2)

    fact_0 = np.exp(-(abs(alpha)**2)/(np.cosh(r)**2))
    p01a = fact_0/(np.cosh(r)**2) - p00a

    fact_0 = np.cosh(r)**2
    fact_1 = -2*np.exp(-(abs(alpha)**2)/(np.cosh(r)**2))
    fact_2 = np.exp(-2*(abs(alpha)**2 - abs(alpha)**2. * np.tanh(r)))
    p11a = (fact_0 + fact_1 + fact_2)/(np.cosh(r)**2)

    cov = two_mode_squeezing(abs(2*r), np.angle(2*r))
    mu = 2 * np.array([alpha.real, alpha.real, alpha.imag, alpha.imag])

    p00n = threshold_detection_prob(mu, cov, (0,0))
    p01n = threshold_detection_prob(mu, cov, (0,1))
    p11n = threshold_detection_prob(mu, cov, (1,1))

    assert np.isclose(p00a, p00n)
    assert np.isclose(p01a, p01n)
    assert np.isclose(p11a, p11n)