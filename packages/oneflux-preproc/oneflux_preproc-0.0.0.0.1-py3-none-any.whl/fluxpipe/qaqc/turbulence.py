import xarray as xr
import numpy as np
import pandas as pd

def e(ds):
    if 'zm' in ds:
        zm = ds['zm']
    else:
        zm = ds.attrs.get('zm', None)

    if 'z0' in ds:
        z0 = ds['z0']
    else:
        z0 = ds.attrs.get('z0', None)

    if 'zL' in ds:
        zL = ds['zL']
    else:
        zL = (zm-z0) / ds['ol']

def integral_turbulence_characteristics(ds, x1="w", x2="co2", 
                                        zL=1, latitude=None, **kwargs):
    '''
    Add turbulence flag to dataset.
    '''
    if not latitude:
        latitude = ds.attrs.get('latitude', None)
        
    # n = {k: k for k in ['zL', 'zm', 'z0', 'ol', 'ustar', 'sigmaw']}
    # n.update(**{k: v for k, v in kwargs.items() if k in n.keys()})

    assert len(list(ds.dims)) == 1, 'Data must be a single time series.'

    sTp_Tpstar_mo = 2 * np.abs(zL)**(1/8)

    if (np.abs(zL) < 0.032):
                 sTp_Tpstar_mo = 1.3
    if (np.abs(zL) > -0.2) and (np.abs(zL) < 0.4):
        # f: Coriolis parameter
        f = 2. * 2.*np.pi/(24.*60.*60.) * np.sin(np.deg2rad(latitude))
        sTp_Tpstar_mo = 0.21 * np.log(1. * f / ds['ustar']) + 3.1
    
    sw_ustar = ds['std_w'] / ds['ustar']

    stat = np.floor(
        np.abs((sTp_Tpstar_mo - sw_ustar) / sTp_Tpstar_mo) * 100.)
    if (sTp_Tpstar_mo <= 10**-6):
        stat = 0

    flag = 2
    if stat <= 100:
        flag = 1
    if stat <= 30:
        flag = 0

    ds = ds.assign({f'qaqc_itc_{x1}_{x2}': stat,
                    f'qaqc_itc_flag_{x1}_{x2}': flag})

    # for each group calculate the cov
    # calculate the mean of the cov for all groups
    # compare the mean with the cov
    # return % and flag (0,1,2)

    return ds

    return type(
        'var_', (object,),
        {"test": stat,
         "flag": flag,
         "meta": {}}
    )