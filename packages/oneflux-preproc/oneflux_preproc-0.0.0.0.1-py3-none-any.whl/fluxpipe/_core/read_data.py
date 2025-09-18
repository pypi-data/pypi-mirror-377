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


def extract_timestamp(df, tname, datestr, dt, date_format, datefomatfrom, datefomatto):
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

    data.insert(0, 'timestamp_end', data[time_coord].dt.ceil(
        avg))
    data.insert(0, 'timestamp_start',
                data['timestamp_end'] - pd.Timedelta(avg))

    data.insert(0, 'date', data['timestamp_end'])
    data.insert(0, 'time', (data[time_coord] -
                            data['timestamp_start']) / pd.Timedelta('1s'))
    data.insert(0, 'latitude', data['latitude']
                if 'latitude' in data else attrs.get('latitude', None))
    data.insert(0, 'longitude', data['longitude']
                if 'longitude' in data else attrs.get('longitude', None))
    
    ds = (data
          .dropna(subset=['date', 'time', 'latitude', 'longitude'], how='any')
          .set_index(['date', 'time', 'latitude', 'longitude'])
          .to_xarray())

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
                var_col_nb = int(float(v['csv']['column']))
                var_col_nb += 5
                var_col = data.columns[var_col_nb]
                ds[var_col] = ds[var_col].assign_attrs(
                    **v.get('Attr', {}))

    return ds
