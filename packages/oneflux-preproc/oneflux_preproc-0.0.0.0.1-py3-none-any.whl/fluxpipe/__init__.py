import pandas as pd
import xarray as xr
from . import version, _core, process, corrections, gapfilling, partitioning, footprint, qaqc, external, compatibility
# from . import version, handler, _core, corrections, gapfilling, partitioning, footprint
# from ._core.eddycov import universal_wt as wavelet_transform
# from .handler import run_from_eddypro
# from ._core.pipeline import process, main


def apply_eddycov(data):
    data = _core.micrometeorology.add_micrometeorological_variables_to_data(
        data)
    
    data = data.assign(
        wind_dir=_core.micrometeorology.wind_direction(
            data.u.mean(), data.v.mean(), float(data.attrs.get('anemometer_north_offset', 0))),)

    # data = external.load_era5.retrieve_era5(
    #     data)
    
    data = corrections.despiking.apply_despiking(data, ['u', 'v', 'w', 'co2'])
    data = corrections.time_lag.apply_time_lag(data)
    data = corrections.axis_rotation.apply_axis_rotation(data)

    data_sta = data[["u", "v", "w", "co2", "h2o"]].std()
    data_sta = data_sta.rename(
        {k: f'std_{k}' for k in list(data_sta.variables.keys())})
    data = xr.merge([data, data_sta])

    for x1, x2 in [('w', 'co2'), ('w', 'h2o'), ('w', 't_sonic'), ('u', 'v'), ('u', 'w')]:
        # data = process.conventional_covariance.covariance(data, x1=x1, x2=x2)
        data = data.assign(
            **{f'cov_{x1}_{x2}': xr.cov(data[x1], data[x2])}
        )

    data = data.assign(ustar=(data.cov_u_w.pipe(abs) ** 0.5))

    data = qaqc.sta(data)

    # Convert timestamp to datetime and set as index
    # data = data.assign_coords(date=data['timestamp_end'], time=data['time_ns'])
    # data = data.set_index(timestamp=["date", "time"]).unstack("timestamp")
    return data
