import xarray as xr
from . import theoretical, fixed, maximisation

available_corrections = {
    'constant':
    type('var_', (object,), {'run': fixed.fix_time_lag,
                             'name': 'constant time lag'}),
    'maxcov&default':
    type('var_', (object,), {'run': maximisation.time_lag_w_default,
                             'name': 'maximization covariance with default'}),
    'maxcov':
    type('var_', (object,), {'run': maximisation.time_lag,
         'name': 'maximization covariance'}),
    # 'tlag_opt':
    # type('var_', (object,), {'run': mauder_et_al_2013.mauder2013,
    #      'name': 'MAD (Mauder, et al., 2013)'}),
}


def apply_time_lag(data, x1='w', x2='co2', **kwargs):
    assert all([v in data for v in [x1, x2]]
               ), 'Not all variables for time lag optimization are in data.'

    correction = available_corrections.get(
        data.attrs.get('Corrections', {}).get('time_lag', {}).get('method', None), None)
    # if correction is a function, then type('var_', (object,), {'run': correction, 'name': ?})

    if correction:
        data = data.assign(**{f'{x2}_bfr_timelag': data[x2]})

        # Translate time lag in sec. to data points
        if 'tlag' not in kwargs:
            kwargs['tlag'] = - int(float(data[x2].attrs.get(
                'nom_timelag', 0)) * float(data.attrs.get('acquisition_frequency', 0)))
            kwargs['tlag_min'] = - int(float(data[x2].attrs.get(
                'min_timelag', 0)) * float(data.attrs.get('acquisition_frequency', 0)))
            kwargs['tlag_max'] = - int(float(data[x2].attrs.get(
                'max_timelag', 0)) * float(data.attrs.get('acquisition_frequency', 0)))

        dr = correction.run(data[x1], data[x2], **kwargs)

        data[x2].data = dr.x

        data[x2] = data[x2].assign_attrs(time_lag_method=correction.name)
        for k, v in vars(dr).items():
            if k.startswith('__') or (k in ['x', 'meta']):
                continue
            else:
                try:
                    if k in ['tlag']:
                        try:
                            v = abs(v * \
                                float(data.attrs.get('acquisition_frequency', 0)) ** -1)
                        except:
                            pass
                    var_name = f'time_lag_params_{k}_{x2}'
                    
                    # logger.debug(f'Assigning {var_name} with value {v} to data.')
                    data = data.assign(**{var_name: v})
                    data[var_name] = data[var_name].assign_attrs(
                        time_lag_method=correction.name)
                except:
                    pass

        if 'meta' in vars(dr).keys() and dr.meta:
            data[x2] = data[x2].assign_attrs(time_lag_meta=dr.meta)

        data.attrs['corrections_applied'] += f'time lag optimization w/ {correction.name}; '
    return data
