import xarray as xr
from . import mauder_et_al_2013

available_corrections = {
    'vickers_et_al_1997':
    type('var_', (object,), {'run': mauder_et_al_2013.mauder2013,
         'name': 'MAD (Mauder, et al., 2013)'}),
    'mauder_et_al_2013':
    type('var_', (object,), {'run': mauder_et_al_2013.mauder2013,
         'name': 'MAD (Mauder, et al., 2013)'}),
}


def apply_despiking(data, select=[], **kwargs):
    assert all([v in data for v in select]
               ), 'Not all selected variables for despiking are in data.'

    correction = available_corrections.get(
        data.attrs.get('Corrections', {}).get('despiking', {}).get('method', None), None)
    
    if correction:
        for s in select:
            data = data.assign(**{f'{s}_bfr_dpk': data[s]})

            dr = correction.run(data[s], **kwargs)

            data[s].data = dr.x

            data[s] = data[s].assign_attrs(despiking_method=correction.name)
            # other_params = {k: v for k, v in vars(
            #     dr).items() if not k.startswith('__') and k not in ['x']}
            
            # if other_params:
            #     data[k] = data[k].assign_attrs(
            #         despiking_params=other_params)
               
            for k, v in vars(dr).items():
                if k.startswith('__') or (k in ['x', 'meta']):
                        continue
                else:
                    try:
                        var_name = f'despiking_{k}_{s}'
                        data = data.assign(**{var_name: v})
                        data[var_name] = data[var_name].assign_attrs(
                            despiking_method=correction.name)
                    except:
                         pass
                    
            if 'meta' in vars(dr).keys() and dr.meta:
                data[s] = data[s].assign_attrs(despiking_meta=dr.meta)

            # data[k] = data[k].assign_attrs(
            #     **dict(despiking_method=correction.name,
            #            despiking_params={k: v for k, v in vars(dr).items() if not k.startswith('__') and k not in ['x']}))

        data.attrs['corrections_applied'] += f'despiking w/ {correction.name}; '
    return data
