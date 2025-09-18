import logging
import pandas as pd
import xarray as xr
from . import version, _core, io, process, corrections, qaqc, external, compatibility
from ._core.units import convert_to_prefered_units
from concurrent.futures import ProcessPoolExecutor

logger = logging.getLogger()


