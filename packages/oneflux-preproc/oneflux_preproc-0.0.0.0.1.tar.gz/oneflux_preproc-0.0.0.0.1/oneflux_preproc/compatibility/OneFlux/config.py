
# built-in modules
from configobj import ConfigObj
import re
import os
import warnings
import logging
from functools import reduce

# 3rd party modules
import numpy as np
import pandas as pd

# project modules

logger = logging.getLogger('wvlt.oneflux_compatibility')


def write_files_as_01_qc_visual(config, dst, overwrite=True):
    template = [
        f"site, {config.get('site_name', '')}",
        f"year, 2005",
        f"lat, {config.get('latitude', '')}",
        f"lon, {config.get('longitude', '')}",
        f"timezone, -6",
        f"htower, 200501010030, 4.05",
        f"timeres, halfhourly",
        f"sc_negl, 1"]
    # TIMESTAMP_START, TIMESTAMP_END, CO2, FC, G, H, H2O, LE, NEE_pi, NETRAD, P, PA, PPFD_IN, RH, SWC_1, SW_IN, TA, TS_1, USTAR, VPD, WD, WS
    
    if os.path.exists(dst) and not overwrite:
        logger.info(f"File `{dst}` already exists, to overwrite state `overwrite=True`.")
        return
    
    with open(dst, 'w+') as wf:
        wf.write("\n".join(template))
    return
