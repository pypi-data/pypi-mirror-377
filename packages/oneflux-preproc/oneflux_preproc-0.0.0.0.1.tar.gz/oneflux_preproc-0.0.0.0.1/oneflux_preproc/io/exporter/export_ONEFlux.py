import pandas as pd
import xarray as xr
import os


def export_as_ONEFlux(ds: xr.Dataset, output_file='fluxnet_output.csv'):
    header = []
    header += [f"site,{ds.attrs['site_name']}"]
    # header += [f"year,{ds.attrs['latitude']}"]
    header += [f"lat,{ds.attrs['latitude']}"]
    header += [f"lon,{ds.attrs['longitude']}"]
    header += [f"timezone,?"]
    header += [f"htower,?"]
    header += [f"htower,?"]
    header += [f"timeres,halfhourly"]
    header += [f"sc_negl,1"]
    header += [f"notes,{pd.Timestamp.now().strftime('%Y%m%d%H%M')} qc visual comparison SY"]
    header += [f"notes,dataset retrieved on {pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"]

    # 1. Variable mapping
    rename_map = {
        # GASES
        'co2': 'CO2',
        'h2o': 'H2O',
        'ch4': 'CH4',
        'no': 'NO',
        'no2': 'NO2',
        'n2o': 'N2O'
        }
    
    expected_columns = ['CO2','FC','G','H','H2O',
                        'LE','NEE_pi','NETRAD','P','PA','PPFD_IN','RH','SWC_1',
                        'SW_IN','TA','TS_1','USTAR','VPD','WD','WS']

    ds = ds.rename({k: k.upper() for k in ds.data_vars})

    csv_data = pd.DataFrame({
        'TIMESTAMP_START': ds['date'] - ds.date.attrs['delta'],
        'TIMESTAMP_END': ds['date'],
    })

    for col in expected_columns:
        csv_data[col] = ds[col].data.magnitude.ravel() if col in ds else pd.NA

    # Write .csv
    csv_header = "\n".join(header)

    # Guarantee folders exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write to file
    with open(output_file, 'w', newline='') as f:
        # First write the pre-data lines
        f.write(csv_header + '\n')
        csv_data.to_csv(f, index=False)
    return