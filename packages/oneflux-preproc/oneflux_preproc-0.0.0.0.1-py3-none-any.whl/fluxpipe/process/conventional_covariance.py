import xarray as xr


def covariance(data, x1="w", x2="co2"):
    ds = data.copy()
    # content.
    ds = ds.assign(
        **{f'cov_{x1}_{x2}': xr.cov(data[x1], data[x2], dim='time')}
    )
    return ds
