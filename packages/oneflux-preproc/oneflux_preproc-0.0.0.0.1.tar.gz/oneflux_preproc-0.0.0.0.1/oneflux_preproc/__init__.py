import pandas as pd
import xarray as xr
from . import version, _core, io, process, corrections,  qaqc, external, compatibility
# ignore gapfilling, partitioning, footprint,
from ._core import utils
from .process import process_time_series_in_windows, process_time_series, preprocess_eddy_covariance_data
# from . import version, handler, _core, corrections, gapfilling, partitioning, footprint
# from ._core.eddycov import universal_wt as wavelet_transform
# from .handler import run_from_eddypro
# from ._core.pipeline import process, main

