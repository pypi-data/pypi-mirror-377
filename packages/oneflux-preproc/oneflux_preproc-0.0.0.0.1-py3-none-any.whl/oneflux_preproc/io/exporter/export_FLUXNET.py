import pandas as pd
import xarray as xr


def export_as_FLUXNET(ds: xr.Dataset, output_file='fluxnet_output.csv'):
    """
    Export an xarray.Dataset to a FLUXNET-style CSV file, with variable renaming,
    timestamp formatting, and unit verification/conversion.

    Parameters:
    - ds: xarray.Dataset
    - output_file: str
    """

    # 1. Variable mapping
    rename_map = {
        # GASES
        'co2': 'CO2',
        'h2o': 'H2O',
        'ch4': 'CH4',
        'no': 'NO',
        'no2': 'NO2',
        'n2o': 'N2O',
        'o3': 'O3',
        'co2_flux': 'FC',
        'ch4_flux': 'FCH4',
        'no_flux': 'FNO',
        'no2_flux': 'FNO2',
        'n2o_flux': 'FN2O',
        'fo3_flux': 'FO3',
        'sc': 'SC',
        'sch4': 'SCH4',
        'sno': 'SNO',
        'sno2': 'SNO2',
        'sn2o': 'SN2O',
        'so3': 'SO3',

        # FOOTPRINT
        'fetch_max': 'FETCH_MAX',
        'fetch_90': 'FETCH_90',
        'fetch_55': 'FETCH_55',
        'fetch_40': 'FETCH_40',
        'fetch_filter': 'FETCH_FILTER',

        # HEAT
        'g': 'G',
        'h': 'H',
        'le': 'LE',
        'netrad': 'NETRAD',

        # MET
        'air_temperature': 'TA',
        'rh': 'RH',
        'Pa': 'PA',
        'vpd': 'VPD',
        't_sonic': 'TS',
        'swc': 'SWC',
        'p': 'P',
        'p_rain': 'P_RAIN',

        # RADIATION
        'sw_in': 'SW_IN',
        'sw_out': 'SW_OUT',
        'lw_in': 'LW_IN',
        'lw_out': 'LW_OUT',
        'ppfd_in': 'PPFD_IN',
        'ppfd_out': 'PPFD_OUT',
        'apar': 'APAR',

        # PRODUCTS
        'nee': 'NEE',
        'reco': 'RECO',
        'gpp': 'GPP',

        # WIND
        'u': 'WS',
        'wind_dir': 'WD',
        'ustar': 'USTAR',
    }

    # Filter only the variables available in the dataset
    rename_map_filtered = {k: v for k,
                           v in rename_map.items() if k in ds.data_vars}

    # Rename variables to FLUXNET standard names
    ds = ds.rename(rename_map_filtered)

    # 2. Convert dataset to DataFrame
    df = ds.to_dataframe().reset_index()

    # 3. Time formatting
    if 'time' in df.columns:
        df['TIMESTAMP'] = df['time'].dt.strftime(
            '%Y%m%d%H%M%S')  # FLUXNET wants full timestamp
        df = df.drop(columns=['time'])
        df = df[['TIMESTAMP'] + [col for col in df.columns if col != 'TIMESTAMP']]

    # 4. Unit conversion placeholder — implement actual checks per variable if needed
    # Example: if your temperature is in Kelvin, convert to deg C
    if 'TA' in df.columns and df['TA'].max() > 100:  # crude check for Kelvin
        df['TA'] = df['TA'] - 273.15

    # Add other unit conversions here if your data needs it
    # For example, if RH is in [0–1], multiply by 100
    if 'RH' in df.columns and df['RH'].max() <= 1:
        df['RH'] = df['RH'] * 100

    # 5. Export CSV
    df.to_csv(output_file, index=False)
    print(f"FLUXNET-compatible CSV exported: {output_file}")

    return
