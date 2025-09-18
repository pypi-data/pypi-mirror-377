
import numpy as np
import pandas as pd
from typing import Optional, Tuple, List, Dict, Any


def calculate_gapstats(lLUT):
  var_mean = np.nanmean(lLUT)
  var_len = len(lLUT)
  var_sd = np.std(lLUT)
  return var_mean, var_len, var_sd


def calculate_gapstats_reichstein05(l_lut_v: pd.Series) -> Tuple[float, int, float]:
    """
    Calculate gap statistics using the Reichstein05 method.
    """
    l_var_mean = l_lut_v.mean()
    l_var_fnum = len(l_lut_v)
    l_var_fsd = l_lut_v.std()
    return l_var_mean, l_var_fnum, l_var_fsd


def calculate_gapstats_vekuri23(
    l_lut_v: pd.Series,
    is_lower: pd.Series,
    is_nighttime: bool,
    n_min: int = 1
) -> Tuple[float, int, float]:
    """
    Calculate gap statistics using the Vekuri23 method.
    """
    if is_nighttime:
        return calculate_gapstats_reichstein05(l_lut_v)

    vals_lower = l_lut_v[is_lower]
    vals_higher = l_lut_v[~is_lower]

    if len(vals_lower) < n_min or len(vals_higher) < n_min:
        return calculate_gapstats_reichstein05(l_lut_v)

    mean_lower = vals_lower.mean()
    mean_higher = vals_higher.mean()
    l_var_mean = (mean_lower + mean_higher) / 2
    l_var_fnum = len(l_lut_v)
    l_var_fsd = l_lut_v.std()

    return l_var_mean, l_var_fnum, l_var_fsd


def initialize_gap_filling(
    data: pd.DataFrame,
    var_name: str,
    qf_var_name: str = 'none',
    qf_value: float = np.nan,
    fill_all: bool = True
) -> pd.DataFrame:
    """
    Initializes a data frame for newly generated gap-filled data and qualifiers.

    Parameters:
    - data: DataFrame containing the data to be processed.
    - var_name: Name of the variable to be filled.
    - qf_var_name: Name of the quality flag variable.
    - qf_value: Value of the quality flag for good (original) data.
    - fill_all: Boolean indicating whether to fill all values to estimate uncertainties.

    Returns:
    - DataFrame with initialized gap-filled data and qualifiers.
    """
    # Check if the variable and quality flag columns exist in the data
    if var_name not in data.columns:
        raise ValueError(f"Variable '{var_name}' not found in data.")
    if qf_var_name != 'none' and qf_var_name not in data.columns:
        raise ValueError(
            f"Quality flag variable '{qf_var_name}' not found in data.")

    # Create a copy of the original data to avoid modifying it directly
    temp_data = data.copy()

    # Set quality flag for the variable to be filled
    if qf_var_name != 'none':
        var_values = temp_data[var_name].where(
            temp_data[qf_var_name] == qf_value, np.nan)
    else:
        var_values = temp_data[var_name].copy()

    # Abort if the variable to be filled contains no data
    if var_values.isna().all():
        raise ValueError(
            f"Variable to be filled ('{var_name}') contains no data at all.")

    # Initialize new columns for gap-filled data and qualifiers
    temp_data[f'{var_name}_orig'] = var_values
    temp_data[f'{var_name}_f'] = var_values
    temp_data[f'{var_name}_fqc'] = np.where(var_values.isna(), 1, 0)
    temp_data[f'{var_name}_fall'] = np.where(
        var_values.isna(), np.nan, var_values)
    temp_data[f'{var_name}_fall_qc'] = np.where(var_values.isna(), 1, 0)
    temp_data[f'{var_name}_fnum'] = np.nan
    temp_data[f'{var_name}_fsd'] = np.nan
    temp_data[f'{var_name}_fmeth'] = np.nan
    temp_data[f'{var_name}_fwin'] = np.nan

    # Set fqc to zero for original values
    temp_data[f'{var_name}_f'] = temp_data[f'{var_name}_orig']
    temp_data[f'{var_name}_fqc'] = np.where(
        ~temp_data[f'{var_name}_orig'].isna(), 0, np.nan)

    # Set filling of only gaps
    if not fill_all:
        temp_data[f'{var_name}_fall'] = temp_data[f'{var_name}_orig']

    return temp_data


def fill_lut_generic(
    data: pd.DataFrame,
    win_days: int,
    verbose: bool = True,
    calculate_gapstats=calculate_gapstats_reichstein05,
    **kwargs
) -> pd.DataFrame:
    """
    Performs Look-Up Table (LUT) gap-filling algorithm.

    Parameters:
    - data: DataFrame containing the data to be processed.
    - win_days: Window size for filling in days.
    - verbose: Boolean indicating whether to print status information.
    - calculate_gapstats: Function to compute gap statistics.
    - **kwargs: Arbitrary keyword arguments for condition variables and their tolerances.

    Returns:
    - DataFrame with gap-filled data.
    """
    gap_fill_results = pd.DataFrame(
        columns=['index', 'mean', 'fnum', 'fsd', 'fmeth', 'fwin', 'fqc'])

    # Check if necessary columns are present in the data
    required_columns = ['VAR_f', 'VAR_orig', 'VAR_fall']
    if not all(column in data.columns for column in required_columns):
        raise ValueError(
            'Data frame has not been initialized with required columns!')

    # Determine positions where gaps need to be filled
    gaps_to_fill = data[data['VAR_fall'].isna()].index

    if len(gaps_to_fill) > 0:
        # Separate condition variables and their tolerances
        condition_vars = {k: v for k, v in kwargs.items() if k.startswith('v')}
        tolerance_vals = {k: v for k, v in kwargs.items() if k.startswith('t')}

        for idx, gap_position in enumerate(gaps_to_fill):
            if verbose and idx == 0:
                active_vars = [
                    var for var in condition_vars.values() if var != 'none']
                print(
                    f'Look up table with window size of {win_days} days with {" ".join(active_vars)}')

            start_idx = max(0, gap_position - win_days * 48)
            end_idx = min(len(data), gap_position + win_days * 48)

            # Special handling for Rg variable
            is_v1_rg = 'Rg' in condition_vars.get('v1', '')
            adjusted_t1 = tolerance_vals.get('t1', np.nan)
            if is_v1_rg:
                adjusted_t1 = max(
                    min(adjusted_t1, data.loc[gap_position, condition_vars['v1']]), 20)

            # Determine valid rows for filling
            valid_rows = pd.Series(True, index=range(start_idx, end_idx + 1))
            valid_rows &= ~data.loc[start_idx:end_idx, 'VAR_orig'].isna()

            for var_key, var in condition_vars.items():
                tol_key = var_key.replace('v', 't')
                if var != 'none' and tol_key in tolerance_vals:
                    var_values = data.loc[start_idx:end_idx, var]
                    adjusted_tol = adjusted_t1 if var_key == 'v1' else tolerance_vals[tol_key]
                    valid_rows &= (abs(
                        var_values - var_values.loc[gap_position - start_idx]) < adjusted_tol) & ~var_values.isna()

            lut_values = data.loc[start_idx:end_idx, 'VAR_orig'][valid_rows]

            if len(lut_values) > 1:
                var_values = data.loc[start_idx:end_idx, condition_vars['v1']]
                is_v1_below_t1 = var_values[valid_rows] <= var_values.loc[gap_position - start_idx]
                is_nighttime = is_v1_rg and data.loc[gap_position,
                                                     condition_vars['v1']] < 10

                gap_stats = calculate_gapstats(
                    lut_values, is_v1_below_t1, is_nighttime)
                mean_val, num_val, sd_val = gap_stats

                window_size = 2 * win_days
                method = np.nan
                quality_flag = np.nan

                # Determine method and quality flag
                if all(var != 'none' for var in condition_vars.values()):
                    method = 1
                    if window_size <= 14:
                        quality_flag = 1
                    elif window_size <= 56:
                        quality_flag = 2
                    else:
                        quality_flag = 3
                elif condition_vars['v1'] != 'none' and all(var == 'none' for var in condition_vars.values() if var != 'v1'):
                    method = 2
                    if window_size <= 14:
                        quality_flag = 1
                    elif window_size <= 28:
                        quality_flag = 2
                    else:
                        quality_flag = 3

                new_row = pd.DataFrame([[gap_position, mean_val, num_val, sd_val, method, window_size, quality_flag]],
                                       columns=gap_fill_results.columns)
                gap_fill_results = pd.concat(
                    [gap_fill_results, new_row], ignore_index=True)

            if verbose and idx % 100 == 0:
                print('.', end='')
            if verbose and idx % 6000 == 0:
                print('\n.', end='')

        if verbose:
            print(f'\n{gap_fill_results.shape[0]}')

    if not gap_fill_results.empty:
        data.loc[gap_fill_results['index'], ['VAR_fall', 'VAR_fnum', 'VAR_fsd', 'VAR_fmeth', 'VAR_fwin', 'VAR_fall_qc']] = \
            gap_fill_results[['mean', 'fnum', 'fsd',
                              'fmeth', 'fwin', 'fqc']].values

        gaps = data.loc[gap_fill_results['index'], 'VAR_f'].isna()
        data.loc[gap_fill_results['index'], ['VAR_f', 'VAR_fqc']
                 ] = gap_fill_results[['mean', 'fqc']].values

    return data[['VAR_orig', 'VAR_f', 'VAR_fall', 'VAR_fnum', 'VAR_fsd', 'VAR_fwin']]


def fill_lut(
    data: pd.DataFrame,
    win_days: int,
    v1: str = 'none',
    t1: float = np.nan,
    v2: str = 'none',
    t2: float = np.nan,
    v3: str = 'none',
    t3: float = np.nan,
    v4: str = 'none',
    t4: float = np.nan,
    v5: str = 'none',
    t5: float = np.nan,
    verbose: bool = True,
    calculate_gapstats=calculate_gapstats_reichstein05
) -> pd.DataFrame:
    """
    Performs Look-Up Table (LUT) gap-filling algorithm.

    Parameters:
    - data: DataFrame containing the data to be processed.
    - win_days: Window size for filling in days.
    - v1 to v5: Condition variables.
    - t1 to t5: Tolerance intervals for condition variables.
    - verbose: Boolean indicating whether to print status information.
    - calculate_gapstats: Function to compute gap statistics.

    Returns:
    - DataFrame with gap-filled data.
    """
    l_gf = pd.DataFrame(
        columns=['index', 'mean', 'fnum', 'fsd', 'fmeth', 'fwin', 'fqc'])

    # Check if sTEMP has been initialized with new VAR_ columns
    required_columns = ['VAR_f', 'VAR_orig', 'VAR_fall']
    if not all(col in data.columns for col in required_columns):
        raise ValueError(
            'Temporal data frame sTEMP for processing results has not been initialized with sFillInit!')

    # Determine gap positions
    to_be_filled = data[data['VAR_fall'].isna()].index
    if len(to_be_filled) > 0:
        for pos_idx, pos in enumerate(to_be_filled):
            if verbose and pos_idx == 0:
                none_cols = [v for v in [v1, v2, v3, v4, v5] if v != 'none']
                print(f'Look up table with window size of {win_days} days with {" ".join(none_cols)}')

            gap_idx = pos
            start_idx = max(0, gap_idx - win_days * 48)
            end_idx = min(len(data), gap_idx + win_days * 48)

            # Special treatment of Rg to be congruent with MR PV-Wave
            is_v1_rg = 'Rg' in v1
            t1_red = t1
            if is_v1_rg:
                t1_red = max(min(t1, data.loc[gap_idx, v1]), 20)

            # Set LUT fill condition
            rows_b = ~data.loc[start_idx:end_idx, 'VAR_orig'].isna()
            if v1 != 'none':
                v1_v = data.loc[start_idx:end_idx, v1]
                rows_b = rows_b & (
                    abs(v1_v - v1_v.loc[gap_idx - start_idx]) < t1_red) & ~v1_v.isna()
            if v2 != 'none':
                v2_v = data.loc[start_idx:end_idx, v2]
                rows_b = rows_b & (
                    abs(v2_v - v2_v.loc[gap_idx - start_idx]) < t2) & ~v2_v.isna()
            if v3 != 'none':
                v3_v = data.loc[start_idx:end_idx, v3]
                rows_b = rows_b & (
                    abs(v3_v - v3_v.loc[gap_idx - start_idx]) < t3) & ~v3_v.isna()
            if v4 != 'none':
                v4_v = data.loc[start_idx:end_idx, v4]
                rows_b = rows_b & (
                    abs(v4_v - v4_v.loc[gap_idx - start_idx]) < t4) & ~v4_v.isna()
            if v5 != 'none':
                v5_v = data.loc[start_idx:end_idx, v5]
                rows_b = rows_b & (
                    abs(v5_v - v5_v.loc[gap_idx - start_idx]) < t5) & ~v5_v.isna()

            l_lut_v = data.loc[start_idx:end_idx, 'VAR_orig'][rows_b]

            is_v1_below_t1 = v1_v[rows_b] <= v1_v.loc[gap_idx - start_idx]
            is_nighttime = is_v1_rg and data.loc[gap_idx, v1] < 10

            if len(l_lut_v) > 1:
                gap_stats = calculate_gapstats(
                    l_lut_v, is_v1_below_t1, is_nighttime)
                l_var_mean, l_var_fnum, l_var_fsd = gap_stats

                l_var_fwin = 2 * win_days
                l_var_fmeth = np.nan
                l_var_fqc = np.nan

                if v1 != 'none' and v2 != 'none' and v3 != 'none':
                    l_var_fmeth = 1
                    if l_var_fwin <= 14:
                        l_var_fqc = 1
                    elif l_var_fwin > 14 and l_var_fwin <= 56:
                        l_var_fqc = 2
                    elif l_var_fwin > 56:
                        l_var_fqc = 3

                if v1 != 'none' and v2 == 'none' and v3 == 'none':
                    l_var_fmeth = 2
                    if l_var_fwin <= 14:
                        l_var_fqc = 1
                    elif l_var_fwin > 14 and l_var_fwin <= 28:
                        l_var_fqc = 2
                    elif l_var_fwin > 28:
                        l_var_fqc = 3

                new_row = pd.DataFrame([[gap_idx, l_var_mean, l_var_fnum, l_var_fsd, l_var_fmeth, l_var_fwin, l_var_fqc]],
                                       columns=l_gf.columns)
                l_gf = pd.concat([l_gf, new_row], ignore_index=True)

            if verbose and pos_idx % 100 == 0:
                print('.', end='')
            if verbose and pos_idx % 6000 == 0:
                print('.', end='')

        if verbose:
            print(f'{l_gf.shape[0]}')

    if not l_gf.empty:
        data.loc[l_gf['index'], ['VAR_fall', 'VAR_fnum', 'VAR_fsd', 'VAR_fmeth', 'VAR_fwin',
                                 'VAR_fall_qc']] = l_gf[['mean', 'fnum', 'fsd', 'fmeth', 'fwin', 'fqc']].values

        gaps_b = data.loc[l_gf['index'], 'VAR_f'].isna()
        data.loc[l_gf['index'], ['VAR_f', 'VAR_fqc']
                 ] = l_gf[['mean', 'fqc']].values

    return data[['VAR_orig', 'VAR_f', 'VAR_fall', 'VAR_fnum', 'VAR_fsd', 'VAR_fwin']]


