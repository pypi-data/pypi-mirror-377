import tempfile
import xarray as xr
import numpy as np
# pip install cdsapi

def initialize():
    import cdsapi
    c = cdsapi.Client()
    return c


def retrieve_era5(data):
    c = initialize()

    years = list(np.unique(data.date.dt.year).astype(str))
    months = list(np.unique(data.date.dt.month).astype(str))
    days = list(np.unique(data.date.dt.day).astype(str))
    hours = list(np.unique(data.date.dt.hour).astype(str))

    with tempfile.NamedTemporaryFile(suffix='.nc', delete=True) as tmpfile:
        # tmpfile.close()
        # era5_file = tmpfile.name
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': 'boundary_layer_height',
                'year': years,
                'month': months,
                'day': days,
                'time': [f'{str(i).zfill(2)}:00' for i in hours],
                'format': 'netcdf',
                # North, West, South, East
                'area': [data.attrs.get('latitude', 0),
                         data.attrs.get('longitude', 0),
                         data.attrs.get('latitude', 0),
                         data.attrs.get('longitude', 0)],
            },
            tmpfile.name
        )

        ds = xr.open_dataset(tmpfile.name)

        ds = ds.rename_dims(valid_time="date").mean(['latitude', 'longitude'])
        ds = xr.DataArray(
            ds['blh'], {'date': ds['valid_time'].rename('date')})

        data = data.assign(blh_era5=ds)

        return data
