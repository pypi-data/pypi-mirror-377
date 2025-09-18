"""This module implements the double, triple rotation and planar fit corrections for wind components
as described by Wilczak et al. (2001). The corrections are applied to the u, v, and w components of wind data.
It provides functions for both double and triple rotation corrections, allowing for the correction of wind data
to account for the tilt of the anemometer and the alignment of the mean wind vector.
"""

# built-in modules
import re
import os
import warnings
import logging
from functools import reduce

# 3rd party modules
import numpy as np
import pandas as pd
import scipy as sp

# project modules

logger = logging.getLogger('ep.corrections.axis_rotation.wilczak_et_al_2001')

def double_rotation(u, v, w, verbosity=0):
    """
    Perform a double rotation correction on the input wind components u, v, w.
    This function applies the first rotation to align the mean wind vector with the x-axis,
    and the second rotation to align the mean vertical wind component with the z-axis.
    Parameters:
        u (array-like): The u component of the wind.
        v (array-like): The v component of the wind.
        w (array-like): The w component of the wind.
        verbosity (int): Level of verbosity for debug output.
    Returns:
        tuple: Corrected u, v, w components and the angles of the first (theta) and second (phi) rotations.
    """
    # Ensure inputs are numpy arrays
    u = np.asarray(u)
    v = np.asarray(v)
    w = np.asarray(w)

    #first rotation
    theta = np.arctan(np.nanmean(v)/np.nanmean(u))
    u1 = u * np.cos(theta) + v * np.sin(theta)
    v1 = -u * np.sin(theta) + v * np.cos(theta)
    w1 = w

    #second rotation
    phi = np.arctan(np.nanmean(w1)/np.nanmean(u1))
    u2 = u1 * np.cos(phi) + w1 * np.sin(phi)
    v2 = v1
    w2 = -u1 * np.sin(phi) + w1 * np.cos(phi)
    
    if verbosity > 0:
        print(f"Double rotation angles: theta={theta}, phi={phi}")
    
    # Return the corrected components and angles as a named tuple-like object
    return type('var_', (object,), 
                {"u": u2, 
                 "v": v2, 
                 "w": w2, 
                 "theta": theta,
                 "phi": phi,
                 "meta": {}})


def triple_rotation(u, v, w, verbosity=0):
    """
    Perform a triple rotation correction on the input wind components u, v, w.
    This function applies the double rotation method followed by a third rotation
    to correct for the tilt of the anemometer.
    Parameters:
        u (array-like): The u component of the wind.
        v (array-like): The v component of the wind.
        w (array-like): The w component of the wind.
        verbosity (int): Level of verbosity for debug output.
    Returns:
        tuple: Corrected u, v, w components and the angle of the third rotation (psi).
    """
    #first and second rotations
    u2, v2, w2, theta, phi = double_rotation(u, v, w, verbosity)
    
    #third rotation
    psi = np.arctan((2 * np.nanmean(v2 * w2)) /
                        (np.nanmean(v2**2) - np.nanmean(w2**2)))
    u3 = u2
    v3 = v2 * np.cos(psi) + w2 * np.sin(psi)
    w3 = -v2 * np.sin(psi) + w2 * np.cos(psi)
    
    if verbosity > 0:
        print(f"First rotation angles: theta={theta}, phi={phi}, psi={psi}")
    if verbosity > 0:
        print(f"Mean w after triple rotation: {np.nanmean(w3)}")

    # Return the corrected components and angles as a named tuple-like object
    return type('var_', (object,), 
                {"u": u3, 
                 "v": v3, 
                 "w": w3, 
                 "theta": theta, 
                 "phi": phi, 
                 "psi": psi,
                 "meta": {}})


def planarfit(u, v, w, verbosity=0):
    """Perform a planar fit correction on the input wind components u, v, w.
    This function calculates the mean wind vector and applies a rotation to align it with the z-axis.
    Parameters:
        u (array-like): The u component of the wind.
        v (array-like): The v component of the wind.
        w (array-like): The w component of the wind.
        verbosity (int): Level of verbosity for debug output.
    Returns:
        tuple: Corrected u, v, w components after planar fit correction.
    """

    # Ensure inputs are numpy arrays
    u = np.asarray(u)
    v = np.asarray(v)
    w = np.asarray(w)

    meanU = np.nanmean(u)
    meanV = np.nanmean(v)
    meanW = np.nanmean(w)

    def findB(meanU, meanV, meanW):
        su = np.nansum(meanU)
        sv = np.nansum(meanV)
        sw = np.nansum(meanW)

        suv = meanU * meanV
        suw = meanU * meanW
        svw = meanV * meanW
        su2 = meanU * meanU
        sv2 = meanV * meanV

        H = np.matrix([[1, su, sv], [su, su2, suv], [sv, suv, sv2]])
        g = np.matrix([sw, suw, svw]).T
        x = sp.linalg.solve(H, g)

        b0 = x[0][0]
        b1 = x[1][0]
        b2 = x[2][0]
        return b0, b1, b2

    b0, b1, b2 = findB(meanU, meanV, meanW)

    Deno = np.sqrt(1 + b1 ** 2 + b2 ** 2)
    p31 = -b1 / Deno
    p32 = -b2 / Deno
    p33 = 1 / Deno

    cosγ = p33 / np.sqrt(p32**2+p33**2)
    sinγ = -p32 / np.sqrt(p32**2 + p33**2)
    cosβ = np.sqrt(p32**2 + p33**2)
    sinβ = p31

    R2 = np.matrix([[1, 0, 0],
                    [0, cosγ, -sinγ],
                    [0, sinγ, cosγ]])
    R3 = np.matrix([[cosβ, 0, sinβ],
                    [0, 1, 0],
                    [-sinβ, 0, cosβ]])

    A0 = R3.T * R2.T * [[meanU], [meanV], [meanW]]

    α = np.arctan2(A0[1].tolist()[0][0],
                   A0[0].tolist()[0][0])

    R1 = np.matrix([[np.cos(α), -np.sin(α), 0],
                    [np.sin(α), np.cos(α), 0],
                    [0, 0, 1]])

    A1 = R1.T * ((R3.T * R2.T) * np.matrix([u, v, w - b0]))

    U1 = np.array(A1[0])[0]
    V1 = np.array(A1[1])[0]
    W1 = np.array(A1[2])[0]

    if verbosity > 0:
        print(f"Planar fit angles: α={α}, β={np.arctan2(sinβ, cosβ)}, γ={np.arctan2(sinγ, cosγ)}")
        print(f"Mean w after planar fit: {np.nanmean(W1)}")

    if type(u) == pd.Series:
        U1 = pd.Series(U1)
    if type(v) == pd.Series:
        V1 = pd.Series(V1)
    if type(w) == pd.Series:
        W1 = pd.Series(W1)

    # Return the corrected components as a named tuple-like object
    return type('var_', (object,), 
                {"u": U1, 
                 "v": V1, 
                 "w": W1,
                 "meta": {}})
