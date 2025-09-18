import os
import numpy as np
# from scripts import common as tcom
import pathlib
import warnings
from scipy import optimize
import xarray as xr
# current file path
# cfp = pathlib.Path(__file__).parent.resolve()

def default_lag(length=711, diameter=5.3, pump=15, dt=20):
    # default time lag in number of data points
    return int(np.round((length * (np.pi * (diameter/2)**2) * (10**-6) / pump) * 60 * dt))


def cost_function(fix, move, shift):
    shift = int(np.round(shift))
    return -np.abs(xr.cov(fix, move.shift(time=shift)))


def cost_function_w_bounds(fix, move, shift, shift_min, shift_max):
    shift = int(np.round(shift))
    if (shift_min and shift < shift_min) or (shift_max and shift > shift_max):
        return 9999
    return -np.abs(xr.cov(fix, move.shift(time=shift)))


def time_lag(fix, move, tlag, **kwargs):
    opt = optimize.minimize(
        lambda t: cost_function(fix, move, t), [tlag])
    moved = move.shift(time=int(np.round(opt.x)))

    return type(
        'var_', (object,),
        {"x": moved,
         "tlag": int(opt.x),
         "meta": {}}
    )


def time_lag_w_default(fix, move, tlag, tlag_min=0, tlag_max=100, **kwargs):
    opt = optimize.brute(
        lambda t: cost_function(fix, move, t), [(tlag_min, tlag_max)], Ns=(tlag_max - tlag_min + 1),)
    
    opt_use = int(np.round(opt))
    if (tlag_min and np.abs(opt_use) < np.abs(tlag_min)):
        opt_use = -tlag_min
    elif (tlag_max and np.abs(opt_use) > np.abs(tlag_max)):
        opt_use = -tlag_max

    moved = move.shift(time=opt_use)

    return type(
        'var_', (object,),
        {"x": moved,
         "tlag_opt": float(opt),
         "tlag": opt_use,
         "meta": {}}
    )


def time_lag_w_default_opt(fix, move, tlag, tlag_min=None, tlag_max=None, **kwargs):
    opt = optimize.basinhopping(
        lambda t: cost_function_w_bounds(fix, move, t, tlag_min, tlag_max), [tlag], stepsize=1)
    moved = move.shift(time=int(opt.x))

    return type(
        'var_', (object,),
        {"x": moved,
         "tlag": int(opt.x),
         "meta": {}}
    )
