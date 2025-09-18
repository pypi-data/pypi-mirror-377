import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

def fft_over_time(da):
    # Interpolate missing data along time
    da_interp = da.interpolate_na(dim='time', fill_value="extrapolate")

    # Apply FFT using apply_ufunc to preserve xarray metadata
    return xr.apply_ufunc(
        np.fft.fft,
        da_interp,
        input_core_dims=[["time"]],
        output_core_dims=[["frequency"]],
        dask="parallelized",
        output_dtypes=[np.complex128]
    )


def cospectrum(*args):
    return xr.apply_ufunc(
        lambda a, b: np.real(a * np.conj(b)),
        *args,
        input_core_dims=[["frequency"], ["frequency"]],
        output_core_dims=[["frequency"]],
        dask="parallelized", output_dtypes=[np.float64]
    )


def get_spectra(ds, variables=['u', 'v', 'w', 'co2', 'h2o', 't_sonic']):
    # Frequency axis
    freq = np.fft.fftfreq(len(ds.time))

    ds = ds.assign_coords(frequency=freq)

    for v in variables:
        if v in ds:
            ds[f'spectrum_{v}'] = ds.groupby(['date', 'latitude', 'longitude']).apply(
                lambda ds: fft_over_time(ds[v]))
    
    return ds


def get_cospectra(ds, variables=[['u', 'v'], ['w', 'co2'], ['w', 'h2o'], ['w', 't_sonic']]):
    # Frequency axis
    freq = np.fft.fftfreq(len(ds.time))

    ds = ds.assign_coords(frequency=freq)

    for x1, x2 in variables:
        if f'spectrum_{x1}' in ds and f'spectrum_{x2}' in ds:
            ds[f'cospectrum_{x1}_{x2}'] = ds.groupby(['date', 'latitude', 'longitude']).apply(
                lambda ds: cospectrum(ds[f'spectrum_{x1}'], ds[f'spectrum_{x2}']))
    return ds

# data['cospectrum_wts'] = data.groupby(['date', 'latitude', 'longitude']).apply(
#     lambda ds: cospectrum(ds.spectrum_w, ds.spectrum_ts))

def plot(ds):
    # Plot only the positive half (since it's symmetric)
    half = len(ds.frequency) // 2
    freq = ds.frequency

    power = (ds['cospectrum_wts'] / ds['cov_w_t_sonic']).pipe(abs).mean(
        dim=['date', 'latitude', 'longitude'])
    plt.plot(freq[:half], power[:half], c='r')

    power = (ds['cospectrum_wco2'] / ds['cov_w_co2']).pipe(abs).mean(
        dim=['date', 'latitude', 'longitude'])
    plt.plot(freq[:half], power[:half], c='k')

    plt.title("Power Spectrum")
    plt.xlabel("Frequency")
    plt.ylabel("Power (|FFT|²)")
    plt.grid(True)
    plt.yscale('log')
    plt.xscale('log')
    plt.show()
