
import numpy as np
import pandas as pd
from typing import Optional, Tuple, List, Dict, Any

def calculate_gapstats(lLUT):
  var_mean = np.nanmean(lLUT)
  var_len = len(lLUT)
  var_sd = np.std(lLUT)
  return var_mean, var_len, var_sd
