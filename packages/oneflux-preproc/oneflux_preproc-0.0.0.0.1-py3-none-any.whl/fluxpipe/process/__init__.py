import xarray as xr
from . import conventional_covariance

available_corrections = {
    'ec':
    type('var_', (object,), {'run': conventional_covariance.covariance,
         'name': 'Conventional covariance.'}),
    'wv':
    type('var_', (object,), {'run': conventional_covariance.covariance,
         'name': 'Wavelet-based covariance (Coimbra et al., 2025)'}),
}


def apply_process(data, method=None, **kwargs):
    method = data.attrs.get('process_method', method)
    correction = available_corrections.get(method, 'ec')

    data = data.mean(dim='time', keep_attrs=True)

    if correction:
        x1 = 'w'
        x2 = 'co2'
        # data = correction.run(data, x1, x2, **kwargs)

        data = data.assign(
            **{f'{x2}_flux': data[f'cov_{x1}_{x2}'] * data['air_molar_volume']**-1}
        )
    return data
