import xarray as xr
# from .._core.commons import compute_equation


def covariance(data, x1="w", x2="co2"):
    ds = data.copy()

    # ds = compute_equation(
    #     ds, f'cov_{x1}_{x2}', x1, x2, formula=lambda a, b: xr.cov(a, b), unit_formula=lambda a, b: a * b)
    # content.
    # name_cov_var = f'cov_{x1}_{x2}'
    ds = ds.assign(
        **{f'cov_{x1}_{x2}': xr.cov(data[x1], data[x2], dim='time')}
    )

    # data[name_cov_var].attrs['unit_in'] = ""
    # if 'unit_in' in data[x1].attrs and 'unit_in' in data[x2].attrs:
    #     data[name_cov_var].attrs['unit_in'] = (
    #         ureg(data[x1].attrs['unit_in']) *
    #         ureg(data[x2].attrs['unit_in'])
    #     ).to_root_units()
    return ds
