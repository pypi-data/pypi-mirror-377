"""
Simply read data from a file and return a pandas DataFrame.
This module provides a function to read data from a file and return it as a pandas DataFrame.

It supports various file formats including CSV, Excel, and NetCDF.
"""
import xarray as xr
import re
import pandas as pd
import numpy as np
import datetime
from pandas.api.types import is_numeric_dtype, is_object_dtype
from ..._core.units import resolve_unit

# Read eddypro
# Data to netcdf4 with a format that allows :
# import xarray as xr
# import numpy as np

# # Create example data
# avgtime = pd.date_range('2023-01-01', periods=10)
# rawtime = pd.date_range('2023-01-01', periods=10)
# lat = np.arange(10)
# lon = np.arange(10)
# temperature = np.random.rand(len(time), len(lat), len(lon))
# humidity = np.random.rand(len(time), len(lat), len(lon))

# # Create an xarray Dataset
# ds = xr.Dataset(
#     {
#         'temperature': (('avgtime', 'lat', 'lon'), temperature),
#         'humidity': (('rawtime', 'lat', 'lon'), humidity),
#     },
#     coords={
#         'time': time,
#         'lat': lat,
#         'lon': lon,
#     }
# )

# # Access variables like columns
# temperature_data = ds['temperature']
# humidity_data = ds['humidity']

# # Perform operations on the data
# mean_temperature = temperature_data.mean(dim='time')


def d0_d1_from_time_range(trange):
    if trange is None:
        return None, None
    d0 = pd.to_datetime(trange.split(
        '-', 1)[0]) if trange.split('-', 1)[0] else None
    d1 = pd.to_datetime(trange.split(
        '-', 1)[1]) if trange.split('-', 1)[1] else None
    return d0, d1


def generate_time_windows(tmin, tmax, fastfreq, slowfreq, include='both'):
    tmin = pd.to_datetime(tmin)
    tmax = pd.to_datetime(tmax)
    slow_range = pd.date_range(tmin, tmax, freq=slowfreq).floor(slowfreq)
    slow_delta = pd.Timedelta(slowfreq)

    result = []
    for p in slow_range:
        start = max(p, tmin)
        end = min(p + slow_delta, tmax)
        times = pd.date_range(start, end, freq=fastfreq)

        if include == 'left':
            times = times[:-1]
        elif include == 'right':
            times = times[1:]
        elif include != 'both':
            continue  # or raise ValueError("Invalid 'include' value")

        result.append(times)

    return result

def resolve_timestamp(data, timestamp_name='timestamp'):
    # Create a lowercase mapping of column names to original column names
    col_map = {col.lower(): col for col in data.columns}

    def has_cols(*cols):
        return all(col.lower() in col_map for col in cols)

    if timestamp_name.lower() in col_map:
        try:
            data[timestamp_name] = pd.to_datetime(
                data[col_map['timestamp']].astype(
                    str), format='%Y%m%d%H%M%S.%f'
            )
        except ValueError:
            data[timestamp_name] = pd.to_datetime(
                data[col_map['timestamp']], errors='coerce'
            )
    elif 'timestamp_end' in col_map:
        data[timestamp_name] = pd.to_datetime(
            data[col_map['timestamp_end']], format='%Y%m%d%H%M'
        )
    elif has_cols('date', 'time'):
        data[timestamp_name] = pd.to_datetime(
            data[col_map['date']] + " " + data[col_map['time']]
        )
    elif has_cols('seconds', 'nanoseconds'):
        data[timestamp_name] = pd.to_datetime(
            data[col_map['seconds']] + data[col_map['nanoseconds']] * 10**-9, unit='s'
        )
    elif has_cols('year', 'month', 'day', 'hour', 'minute'):
        data[timestamp_name] = pd.to_datetime(
            data[col_map['year']].astype(str).str.zfill(4) + '-' +
            data[col_map['month']].astype(str).str.zfill(2) + '-' +
            data[col_map['day']].astype(str).str.zfill(2) + 'T' +
            data[col_map['hour']].astype(str).str.zfill(2) +
            data[col_map['minute']].astype(str).str.zfill(2)
        )

    return data



def extract_timestamp(df, tname, datestr, dt, date_format, datefomatfrom, datefomatto):
    """
    Extract timestamp
    """
    if tname not in df.columns or datefomatfrom == 'drop':
        if "date" in df.columns and "time" in df.columns:
            df[tname] = pd.to_datetime(
                df.date + " " + df.time, format='%Y-%m-%d %H:%M')
        else:
            df[tname] = pd.to_datetime(
                datestr, format=date_format) - datetime.timedelta(seconds=dt) * (len(df)-1 + -1*df.index)
            # td, format=date_format) + datetime.timedelta(seconds=dt) * (df_td.index)
            df[tname] = df[tname].dt.strftime(
                datefomatto)
    else:
        try:
            if is_numeric_dtype(df[tname]):
                df.loc[:, tname] = df.loc[:, tname].apply(lambda e: pd.to_datetime(
                    '%.2f' % e, format=datefomatfrom).strftime(datefomatto))
            elif is_object_dtype(df[tname]):
                df.loc[:, tname] = df.loc[:, tname].apply(
                    lambda e: pd.to_datetime(e).strftime(datefomatto))
            else:
                df.loc[:, tname] = pd.to_datetime(
                    df[tname], format=datefomatfrom).strftime(datefomatto)
        except:
            # warnings.warn(f'error when converting {tname} from {datefomatfrom} to {datefomatto}.')
            pass
    return df


def format_column_names(data):
    data.columns = [re.sub(r'\s+', '_', str(c).strip().lower()) for c in data.columns]

    # Variable mapping
    rename_map = {
        # 'h2o': 'h2o_c', 'h2o_dry': 'h2o',
        'co2': 'co2_c', 'co2_dry': 'co2',
        't_cell_out': 'ta',
    }

    # Filter only the variables available in the dataset
    rename_map_filtered = {k: v for k,
                           v in rename_map.items() if k in data.columns}

    # Rename variables to standard names
    data = data.rename(columns=rename_map_filtered)

    return data


def init_data(time_coord='timestamp', **attrs):
    data = pd.DataFrame()

    # Create an xarray Dataset
    global_attrs = attrs.copy()
    global_attrs.update(global_attrs.pop('Global', {}))

    vars_attrs = {k: global_attrs.pop(k)
                  for k, v in attrs.items() if k in data.columns}
    vars_attrs.update(global_attrs.pop('Variables', {}))

    data.insert(0, 'timestamp_end', pd.NaT)
    data.insert(0, 'timestamp_start', pd.NaT)

    data.insert(0, 'date', pd.NaT)
    data.insert(0, 'time', pd.NA)
    data.insert(0, 'latitude', data['latitude']
                if 'latitude' in data else attrs.get('latitude', None))
    data.insert(0, 'longitude', data['longitude']
                if 'longitude' in data else attrs.get('longitude', None))

    ds = (data
          .dropna(subset=['date', 'time', 'latitude', 'longitude'], how='any')
          .set_index(['date', 'time', 'latitude', 'longitude'])
          .to_xarray())

    ds = ds.assign_attrs(**global_attrs)
    ds = ds.assign_attrs(Variables=vars_attrs)

    return ds


def format_data(data, time_coord='timestamp', avg='30Min', **attrs):
    # Create an xarray Dataset
    global_attrs = attrs.copy()
    global_attrs.update(global_attrs.pop('Global', {}))

    vars_attrs = {k: global_attrs.pop(k)
                  for k, v in attrs.items() if k in data.columns}
    vars_attrs.update(global_attrs.pop('Variables', {}))

    timestamp_end = data[time_coord].dt.ceil(avg)
    timestamp_start = timestamp_end - pd.Timedelta(avg)

    data.insert(0, 'date', timestamp_end)
    data.insert(0, 'time', (data[time_coord] -
                            timestamp_start) / pd.Timedelta('1s'))
    data.insert(0, 'latitude', data['latitude']
                if 'latitude' in data else attrs.get('latitude', None))
    data.insert(0, 'longitude', data['longitude']
                if 'longitude' in data else attrs.get('longitude', None))
    
    # Drop rows with missing values in the index columns
    data = data.dropna(subset=['date', 'time', 'latitude', 'longitude'], how='any')

    # Set the multi-index
    data = data.set_index(['date', 'time', 'latitude', 'longitude'])

    # Convert to xarray Dataset
    ds = data.to_xarray()

    ds['date'].attrs.update(**{'value': 'timestamp_end', 'delta': pd.Timedelta(avg)})

    # ds = (data
    #       .dropna(subset=['date', 'time', 'latitude', 'longitude'], how='any')
    #       .set_index(['date', 'time', 'latitude', 'longitude'])
    #       .to_xarray())

    # ds = data.set_index([time_coord]).to_xarray()
    # ds = ds.assign_coords(date=ds['date'], time=ds['time'])
    # ds = ds.set_index(timestamp=["date", "time"]).unstack("timestamp")

    ds = ds.assign_attrs(**global_attrs)

    for k, v in vars_attrs.items():
        if k in ds:
            ds[k] = ds[k].assign_attrs(**v)

        elif v.get('csv', None):
            if v['csv'].get('name', None) in ds:
                ds[k] = ds[k].assign_attrs(**v['csv'].get('Attr', {}))
            elif v['csv'].get('column', None):
                var_col_nb = int(float(v['csv']['column'])) - 1
                # var_col_nb += 2
                var_col = data.columns[var_col_nb]
                ds[var_col] = ds[var_col].assign_attrs(
                    **v.get('Attr', {}))

    # Make unit aware
    for var in ds.data_vars:
        units = ds[var].attrs.get(
            'units', ds[var].attrs.get('unit_in', 'dimensionless'))
        try:
            # keep_attrs = ds[var].attrs.copy()
            resolved_unit = resolve_unit(units)
            ds[var].data = ds[var] * resolved_unit
            ds[var].attrs.update({'units': resolved_unit})
            # keep_attrs.update({'units': resolved_unit})
            # ds[var].attrs = keep_attrs
        except Exception as e:
            ds[var].attrs.update({'units': 'dimensionless'})
            # logger.debug(f"Error for variable `{var}`: {e}")
            pass
    return ds
