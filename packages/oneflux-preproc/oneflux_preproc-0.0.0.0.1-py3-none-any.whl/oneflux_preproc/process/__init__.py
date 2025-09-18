import logging
import xarray as xr
from . import conventional_covariance, L0_fluxes
from .._core import constants
from .. import version, _core, io, process, corrections, qaqc, external, compatibility
from .._core.units import convert_to_prefered_units
# from concurrent.futures import ProcessPoolExecutor

logger = logging.getLogger()


def preprocess_eddy_covariance_data(data):
    data = _core.micrometeorology.add_micrometeorological_variables_to_data(
        data)

    data = data.assign(
        wind_dir=_core.micrometeorology.wind_direction(
            data.u.mean(), data.v.mean(), float(data.attrs.get('anemometer_north_offset', 0))),)

    logger.debug('Micrometeorology added to data. Starting corrections.')

    data = data.pint.dequantify()
    data = corrections.despiking.apply_despiking(data, ['u', 'v', 'w', 'co2'])
    data = corrections.time_lag.apply_time_lag(data)
    data = corrections.axis_rotation.apply_axis_rotation(data)
    data = data.pint.quantify()

    logger.debug(
        'High frequency corrections done. Starting covariance calculations.')

    data_sta = data[["u", "v", "w", "co2", "h2o"]].std()
    data_sta = data_sta.rename(
        {k: f'std_{k}' for k in list(data_sta.variables.keys())})
    data = xr.merge([data, data_sta])

    for x1, x2 in [('w', 'co2'), ('w', 'h2o'), ('w', 't_sonic'), ('u', 'v'), ('u', 'w')]:
        data = data.assign(
            **{f'cov_{x1}_{x2}': xr.cov(data[x1], data[x2])}
        )

    data = data.assign(ustar=(data.cov_u_w.pipe(abs) ** 0.5))

    logger.debug('Covariances calculated. Calculating quality control.')

    data = data.pint.dequantify()
    data = qaqc.sta(data)
    data = data.pint.quantify()

    logger.debug('All pre processing done.')

    data = convert_to_prefered_units(data)

    # Convert timestamp to datetime and set as index
    # data = data.assign_coords(date=data['timestamp_end'], time=data['time_ns'])
    # data = data.set_index(timestamp=["date", "time"]).unstack("timestamp")
    return data


def process_time_series(setup, datetimes, keep_raw=False):
    raw_data = io.importer.import_data(
        setup, datetimes, io.importer.import_ascii.import_ascii)

    data = io.importer.read_data.format_data(
        raw_data, corrections_applied='', **setup.copy())

    data = data.groupby(['date', 'latitude', 'longitude']
                        ).apply(preprocess_eddy_covariance_data)

    processed_data = data.mean(dim='time', keep_attrs=True)

    if keep_raw:
        # Only keep variables that have the 'time' dimension
        data_with_time = data[[
            var for var in data.data_vars if 'time' in data[var].dims]]

        # Concatenate along the 'date' dimension
        processed_data = xr.concat(
            [processed_data, data_with_time], dim='date')
    # if keep_raw = True:
    #   data = only the data which has 'time' in dims
    #   xr.concat([processed_data, data], dim='date')

    processed_data = process.L0_fluxes.calculate_L0(processed_data)

    processed_data = _core.units.convert_to_prefered_units(processed_data)

    return processed_data


def process_time_series_in_windows(setup, parallel=False, **kwargs):
    time_range = setup['datetimerange']
    file_freq = f"{setup['Files']['fileduration']}Min"
    process_freq = f"3h"

    start_time, end_time = io.importer.read_data.d0_d1_from_time_range(
        time_range)
    time_windows = io.importer.read_data.generate_time_windows(
        start_time, end_time, file_freq, process_freq)

    processed_chunks = []

    # # Parallel execution
    # if parallel:
    #     # Build args list
    #     arg_list = [(setup, w) for w in time_windows]
    #     with ProcessPoolExecutor() as executor:
    #         processed_chunks = list(executor.map(
    #             process_time_series, arg_list))
    # else:
    for window in time_windows:
        processed_data = process_time_series(setup, window, **kwargs)

        processed_chunks.append(processed_data)

    final_dataset = xr.concat(processed_chunks, dim='date')
    return final_dataset
