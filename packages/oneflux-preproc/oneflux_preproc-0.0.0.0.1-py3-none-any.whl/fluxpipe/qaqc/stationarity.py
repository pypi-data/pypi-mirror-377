import xarray as xr
import numpy as np
import pandas as pd


def stationarity_test(ds, x1="w", x2="co2", n=6):
    '''
    Add stationarity flag to dataset.
    
    Parameters
    ----------
    flagdata: pandas DataFrame with stationarity flags
    data2: pandas DataFrame with complementary data for comparison

    flagdata: data to include stationarity flag
    data2: complementary data at a faster pace for comparison
    cov_name: variable used for comparison
    one_dta_per: input how many data2 observations are accounted per flagdata observation
    '''
    
    # assert len(list(ds.dims)) == 1, 'Data must be a single time series.'

    # Check if x1 and x2 are in the dataset
    if x1 not in ds or x2 not in ds:
        raise ValueError(f"Variables '{x1}' and '{x2}' must be present in the dataset.")
    
    dim = list(ds.dims)[0]

    sum_ = []
    chunk_size = ds.sizes[dim] // n
    for i in range(n):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < n - 1 else ds.sizes[dim]
        ds_ = ds.isel({dim: slice(start, end)})
        sum_ += [xr.cov(ds_[x1], ds_[x2])]
    sum_ = np.nanmean(sum_)

    cov_ = xr.cov(ds[x1], ds[x2])

    stat = np.floor(
        np.abs((sum_ - cov_) / cov_) * 100.)
    if (sum_ <= -9000.) or (cov_ <= -9000.) or (cov_ > 99999):
        stat = 99999

    flag = 2
    if stat <= 100:
        flag = 1
    if stat <= 30:
        flag = 0

    ds = ds.assign({f'qaqc_stationarity_{x1}_{x2}': stat,
                    f'qaqc_stationarity_flag_{x1}_{x2}': flag})

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

"""
ADD FLAGS
"""


def fITC(flagdata, latitude, **kwargs):
    n = {k: k for k in ['zL', 'zm', 'z0', 'ol', 'ustar', 'sigmaw']}
    n.update(**{k: v for k, v in kwargs.items() if k in n.keys()})

    if n['zL'] not in flagdata.columns:
        flagdata[n['zL']] = (flagdata[n['zm']]-flagdata[n['z0']]) / flagdata.ol

    flagdata['sTp_Tpstar_mo'] = 2 * np.abs(flagdata[n['zL']])**(1/8)

    flagdata.loc[(np.abs(flagdata[n['zL']]) < 0.032), 'sTp_Tpstar_mo'] = 1.3

    # f: Coriolis parameter
    f = 2. * 2.*np.pi/(24.*60.*60.) * np.sin(np.deg2rad(latitude))

    cond_ = (np.abs(flagdata[n['zL']]) > -0.2) * \
        (np.abs(flagdata[n['zL']]) < 0.4)
    flagdata.loc[cond_, 'sTp_Tpstar_mo'] = (
        0.21 * np.log(1. * f / flagdata[n['ustar']]) + 3.1)[cond_]

    flagdata['sw_ustar'] = flagdata[n['sigmaw']] / flagdata[n['ustar']]
    flagdata['itc_co2'] = np.floor(np.abs((flagdata.sTp_Tpstar_mo -
                                           flagdata.sw_ustar) / flagdata.sTp_Tpstar_mo) * 100)

    flagdata.loc[flagdata.sTp_Tpstar_mo < 10**-6, 'itc_co2'] = 0

    flagdata['fITC'] = 2
    flagdata.loc[flagdata.itc_co2 <= 100, 'fITC'] = 1
    flagdata.loc[flagdata.itc_co2 <= 30, 'fITC'] = 0

    return flagdata


def fSTA(flagdata, data2, cov_name='cov_wco2', bydate=False, one_dta_per=None):
    '''
    Add stationarity flag to dataset.

    flagdata: data to include stationarity flag
    data2: complementary data at a faster pace for comparison
    cov_name: variable used for comparison
    one_dta_per: input how many data2 observations are accounted per flagdata observation
    '''

    if bydate:
        """
        breaks = np.unique(data2[bydate].dt.ceil(
            '30min'), return_index=True)[1]
        breaks.sort()
        #breaks = breaks[1:] if breaks[0] == 0 else breaks
        
        flagdata['sum_wco2'] = np.array([np.nanmean(p) for p in np.split(
            data2[cov_name], breaks, axis=0)]).ravel()
        """
        data2[bydate] = data2[bydate].dt.ceil('30min')
        data2 = data2.groupby(bydate)[cov_name].apply(np.nanmean)
        data2 = data2.reset_index()
        data2.columns = [bydate, 'sum_wco2']
        flagdata = pd.merge(flagdata, data2, 'left', bydate)
        # flagdata['sum_wco2'] = np.array(data2.groupby("_group_")[cov_name].apply(np.nanmean)).ravel()

    else:
        if one_dta_per:
            flagdata['sum_wco2'] = np.nanmean(np.array(
                data2[cov_name]).reshape(-1, int(one_dta_per)), axis=1).ravel()[:len(flagdata)]
        else:
            flagdata['sum_wco2'] = np.nanmean(np.array(
                data2[cov_name]).reshape(-1, int(round(len(data2)/len(flagdata)))), axis=1).ravel()

    flagdata['stat_wco2'] = np.floor(
        np.abs((flagdata.sum_wco2 - flagdata[cov_name]) / flagdata[cov_name]) * 100.)

    flagdata.loc[flagdata['sum_wco2'] <= -9000., ['stat_wco2']] = 99999
    flagdata.loc[flagdata[cov_name] <= -9000., ['stat_wco2']] = 99999
    flagdata.loc[flagdata[cov_name]
                 > 99999, ['stat_wco2']] = 99999

    flagdata['fSTA'] = 2
    flagdata.loc[flagdata.stat_wco2 <= 100, 'fSTA'] = 1
    flagdata.loc[flagdata.stat_wco2 <= 30, 'fSTA'] = 0
    return flagdata
