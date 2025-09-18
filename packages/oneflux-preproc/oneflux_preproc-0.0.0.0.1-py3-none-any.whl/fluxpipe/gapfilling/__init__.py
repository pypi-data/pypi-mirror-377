from . import pyfluxpro, xr_interpolation

available_corrections = {
    'mds':
    type('var_', (object,), {'run': pyfluxpro,
         'name': 'Conventional covariance.'}),
    'default':
    type('var_', (object,), {'run': xr_interpolation.apply_interpolation,
         'name': 'xarray built-in interpolation'}),
}


def apply_interpolation(data, meth='default', **kwargs):
    method = data.attrs.get('gapfill_method', meth)
    correction = available_corrections.get(method, None)
    
    if correction:
        dr = correction.run(data, **kwargs)

        for k, v in vars(dr).items():
            if k.startswith('__') or (k in ['x', 'meta']):
                continue
            else:
                data = data.assign(**{f'{k}_fill': v})
    return data
