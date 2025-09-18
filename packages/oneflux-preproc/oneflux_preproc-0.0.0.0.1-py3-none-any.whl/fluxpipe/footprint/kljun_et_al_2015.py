import fluxprint
import pandas as pd
import xarray as xr


def retrieve_footprint(ds, lat=48.88514, lon=2.42222):
    crs = fluxprint.rasterio.crs.CRS.from_string('EPSG:3035')

    fp = fluxprint.wrapper(
        data=pd.DataFrame(
            {'TIMESTAMP': list(ds.date.values),
            # Measurement height (m)
             'zm': [ds.attrs.get('zm', 2)] * len(ds.date),
            # Roughness length (m)
             'z0': [ds.attrs.get('z0', 2)+0.1] * len(ds.date),
             'ws': list(ds.u.values),         # Wind speed (m/s)
             'ustar': list(ds.u.values/10),      # Friction velocity (m/s)
            # Planetary boundary layer height (m)
             'pblh': list(ds['blh_era5'].interpolate_na(dim='date', fill_value='extrapolate').values),
             'mo_length': [-100] * len(ds.date),  # Monin-Obukhov length (m)
            # Standard deviation of lateral velocity (m/s)
             'v_sigma': list(ds.std_v.values),
            # Wind direction (degrees)
             'wind_dir': list(ds.wind_dir.values)
            }),
        footprint_model='kljun_et_al_2015',
        out_as='nc', precision=10,
        meta=dict(
            Tower_Location_Latitude=lat,
            Tower_Location_Longitude=lon,
            Tower_Location_CRS="EPSG:4326",
            timestep={'timezone': 'UTC'},
            Coordinate_Reference_System=crs.to_string(),
            crs_projection4=crs.to_proj4(),
            crs_wkt=crs.to_wkt()),
        by='TIMESTAMP',
        domain=[-100, 100, -100, 100], dx=10, dy=10)

    fp = fp.rename_dims(timestep='date').rename_vars(timestep='date')
    
    return xr.merge([ds, fp])
