"""Despiking functions based on Mauder et al. 2013
"""

# built-in modules
import re
import os
import warnings
import logging
from functools import reduce

# 3rd party modules
import numpy as np
from itertools import islice
from numpy import roll

# project modules
# from ..despiking import window


logger = logging.getLogger('ep.corrections.despiking.mauder_et_al_2013')

def despike(self, cols=['u', 'v', 'w', 'co2', 'h2o'], script='Py', fup2=.1, output_index=None, **kwargs):
    
    plausibility_range = {'u': 3.5, 'v': 3.5, 'w': 5, 'co2': 3.5, 'h2o': 3.5}

    if not callable(script):
        if script=='RFlux':
            script = tcom.LazyCallable(os.path.join(
                cfp.parent, "RFlux-scripts/despiking.R"), "despiking").__get__().fc
            output_index = 0
            kwargs_ = {'mfreq': 20, 'variant': "v3", 'wsignal': 7, 'wscale': 20*60*30/6, 'zth': plausibility_range[c]}
            kwargs_.update(kwargs)
        
        elif script == 'OCE':
            script = tcom.LazyCallable(os.path.join(
                cfp.parent, "corrections/oce_despike.R"), "despike").__get__().fc
            kwargs_ = {'n': plausibility_range[c]}
            kwargs_.update(kwargs)
        
        else:
            script = mauder2013
            kwargs.pop("fill", None)

    for c in cols:
        ogap = np.isnan(self[c])

        # take off absurdity numbers
        p1 = np.nanquantile(self[c], 0.01)
        p99 = np.nanquantile(self[c], 0.99)
        absurdity_bounds_min = 10**(-3 if p1 > 0 else 3) * p1
        absurdity_bounds_max = 10**(3 if p99 > 0 else -3) * p99

        #self.loc[self[c] < absurdity_bounds_min, c] = np.nan
        #self.loc[self[c] > absurdity_bounds_max, c] = np.nan
        print(p1, p99)
        print("np.nanmedian(x)", np.nanmedian(self[c]), np.median(self[c]))
        self[c].mask(self[c] < absurdity_bounds_min, np.nan, inplace=True)
        self[c].mask(self[c] > absurdity_bounds_max, np.nan, inplace=True)
        
        print("np.nanmedian(x)", np.nanmedian(self[c]), np.median(self[c]))

        if output_index:
            self.loc[:, c] = script(self[c], **kwargs)[output_index]
        else:
            self.loc[:, c] = script(self[c], **kwargs)
        
        ngap = np.isnan(self[c])
        N = len(self)
        print(sum(ngap), N, sum(ogap))
        #signan = np.isnan(np.array(self[c]))
        self.loc[:, c] = np.interp(np.linspace(0, 1, N),
                            np.linspace(0, 1, N)[ngap == False],
                            self[c][ngap == False])
        self[c].mask(ogap, np.nan, inplace=True)
        
        #if (np.sum(np.isnan(self[c])) / len(self)) <= fup2:
        #    self.loc[:, c] = self.set_index('TIMESTAMP').loc[:, c].ffill().loc[:, c]

    return self


def mauder2013_(x, n=7, **kwargs):
    for x_i in window(x):
        despiked = x.roll(mauder2013, 7)
    return despiked


def window(seq, n=3):
    """Returns a sliding window (of width n) over data from the iterable
        s = [s(i), s(i+1), ..., s(i+n-1)]
    """
    it = iter(roll(seq, int(n/2)))
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def mauder2013(x, q=7, n=7):
    for i, x_ in enumerate(window(
        np.array(x),
        n=n
    )):
        x_ = np.array(x_)
        x_med = float(np.median(x_))
        mad = float(np.median(np.abs(x_ - x_med)))
        bounds = (float(x_med - (q * mad) / 0.6745), 
                float(x_med + (q * mad) / 0.6745))
        # print("median", x_med, "mad", mad, "bounds", bounds)
        if x_[int(n/2)] < min(bounds):
            x[i] = np.nan
        if x_[int(n/2)] > max(bounds):
            x[i] = np.nan

    #if fill is not None:
    #    x = fill(pd.Series(x) if fill in (pd.Series.ffill, pd.Series.interpolate) else x)
    return type('var_', (object,), 
                {"x": x, 
                #  "median": x_med, 
                #  "mad": mad, 
                #  "bounds": bounds,
                 "meta": {}})
