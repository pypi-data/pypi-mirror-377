import xarray as xr
from . import wilczak_et_al_2001

available_corrections = {
    'double_rotation':
    type('var_', (object,), {'run': wilczak_et_al_2001.double_rotation,
         'name': 'double rotation (Wilczak, et al., 2001)'}),
    'triple_rotation': 
    type('var_', (object,), {'run': wilczak_et_al_2001.triple_rotation,
         'name': 'triple rotation (Wilczak, et al., 2001)'}),
    'planarfit': 
    type('var_', (object,), {'run': wilczak_et_al_2001.planarfit,
         'name': 'planar fit (Wilczak, et al., 2001)'}),
}

def apply_axis_rotation(data):
     assert all([v in data for v in ['u', 'v', 'w']]), 'Missing required variables in axis rotation.' 

     correction = available_corrections.get(
         data.attrs.get('Corrections', {}).get('axis_rotation', {}).get('method', None), None)

     data = data.assign(u_unrot=data.u, v_unrot=data.v, w_unrot=data.w)

     if correction:
          dr = correction.run(data.u, data.v, data.w)
          dr = vars(dr)

          for k in ['u', 'v', 'w']:
               data[k].data = dr[k]
               
               data[k] = data[k].assign_attrs(axis_rotation_method=correction.name)

               if dr.get('meta', None):
                   data[k] = data[k].assign_attrs(
                       time_lag_params=dr.get('meta', ''))
               
          for k, v in dr.items():
               if k.startswith('__') or (k in ['u', 'v', 'w', 'meta']):
                    continue
               else:
                   var_name = f'axis_rotation_params_{k}'
                   data = data.assign(**{var_name: v})
                   data[var_name] = data[var_name].assign_attrs(
                         time_lag_method=correction.name)
          # if isinstance(
          #      dr.u.data, xr.DataArray) else dr.u
          # data['v'].data = dr.v if isinstance(
          #      dr.v.data, xr.DataArray) else dr.v
          # data['w'].data = dr.w if isinstance(
          #      dr.w.data, xr.DataArray) else dr.w

          # data['u'] = data['u'].assign_attrs(
          #      **dict(axis_rotation_method=correction.name,
          #                axis_rotation_params={k: v for k, v in dr.items() if not k.startswith('__') and k not in ['u', 'v', 'w']}))

          data.attrs['corrections_applied'] += f'axis rotation w/ {correction.name}; '
     return data
