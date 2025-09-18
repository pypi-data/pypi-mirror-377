import xarray as xr
from . import stationarity, turbulence
from .stationarity import stationarity_test as sta
from .turbulence import integral_turbulence_characteristics as itc

available_corrections = {
    'sta':
    type('var_', (object,), {'run': stationarity.stationarity_test,
         'name': 'STA ()'}),
    'itc':
    type('var_', (object,), {'run': turbulence.integral_turbulence_characteristics,
         'name': 'ITC ()'}),
}


def apply_qaqc(data, method=None, **kwargs):
    method = data.attrs.get('qaqc_method', method)
    correction = available_corrections.get(method, None)

    if correction:
        dr = correction.run(data, **kwargs)

        data = data.assign(**{f'qaqc_{method}_flag': dr.flag, 
                              f'qaqc_{method}': dr.test})
        data[f'qaqc_{method}_flag'] = data[f'qaqc_{method}_flag'].assign_attrs(
            method=correction.name)
        data[f'qaqc_{method}'] = data[f'qaqc_{method}'].assign_attrs(
            method=correction.name)

        # if dr.get('meta', None):
        #     data[k] = data[k].assign_attrs(
        #         time_lag_params=dr.get('meta', ''))
            
        # other_params = {k: v for k, v in vars(
        #     dr).items() if not k.startswith('__') and k not in ['x']}
        # if other_params:
        #     data[k] = data[k].assign_attrs(
        #         despiking_params=other_params)
            
        if 'meta' in vars(dr).keys() and dr.meta:
            data[f'qaqc_{method}_flag'] = data[f'qaqc_{method}_flag'].assign_attrs(
                meta=dr.meta)
            data[f'qaqc_{method}'] = data[f'qaqc_{method}'].assign_attrs(
                meta=dr.meta)
    return data
