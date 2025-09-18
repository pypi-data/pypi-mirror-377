import xarray as xr
from . import conventional_covariance
from .._core import constants

available_methods = {
    'ec':
    type('var_', (object,), {'run': conventional_covariance.covariance,
         'name': 'Conventional covariance.'}),
    'wv':
    type('var_', (object,), {'run': conventional_covariance.covariance,
         'name': 'Wavelet-based covariance (Coimbra et al., 2025)'}),
}

def calculate_L0(data, **kwargs):
    data['FC'] = data['cov_w_co2'] * data['air_molar_volume']**-1
    data['h2o_flux'] = data['cov_w_h2o'] * data['air_molar_volume']**-1
    data['LE'] = data['h2o_flux'] * constants.Mv * constants.Lv
    data['E0'] = data['h2o_flux'] * constants.Mv
    data['H'] = data['cov_w_t_sonic'] * data['rho_m'] * data['cpd']

    data['Tp'] = data['air_temperature'] * (constants.P0a / data['Pa'])**0.286
    data['MO_lenght'] = (data['Tp'] * data['ustar']**3) / \
        (constants.k * constants.g * data['H'] / (data['rho_m'] * data['cpd']))

    return data


def apply_process(data, method=None, **kwargs):
    method = data.attrs.get('process_method', method)
    meth_run = available_methods.get(method, 'ec')

    data = data.mean(dim='time', keep_attrs=True)

    data = calculate_L0(data)

    # for
    # if data[f'cov_{x1}_co2'].data.to_root_units().units == "meter/second":
    #     data[f'{x2}_flux'] = data[f'cov_{x1}_co2'] * \
    #         data['air_molar_volume']**-1

    # if meth_run:
    #     x1 = 'w'
    #     x2 = 'co2'

    #     # needs:
    #     #   w = 'w'
    #     #   x = 'co2', 'h2o', ...
    #     #   corr = data['air_molar_volume']**-1
    #     {'FC': {'base': f'cov_{x1}_co2',
    #             'correction': data['air_molar_volume']**-1}}

    #     # data = meth_run.run(data, x1, x2, **kwargs)

    #     data = data.assign(
    #         **{f'{x2}_flux': data[f'cov_{x1}_co2'] * data['air_molar_volume']**-1,
    #            f'LE': data[f'cov_{x1}_h2o'] * data['air_molar_volume']**-1,
    #            f'H': data[f'cov_{x1}_t_sonic'] * data['air_molar_volume']**-1, }
    #     )
    return data
