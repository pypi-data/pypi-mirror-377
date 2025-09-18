import numpy as np


def time_lag(length=711, diameter=5.3, pump=15, dt=20):
    # default time lag in number of data points
    return int(np.round((length * (np.pi * (diameter/2)**2) * (10**-6) / pump) * 60 * dt))
