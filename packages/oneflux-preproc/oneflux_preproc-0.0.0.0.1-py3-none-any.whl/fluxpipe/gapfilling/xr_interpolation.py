def apply_interpolation(data, dim='date', selected_vars=['co2', 'h2o', 'u', 'v', 'w'], **kwargs):
    """
    Apply gap filling and interpolation to the data.
    
    Parameters:
    data (xarray.Dataset): The input dataset with gaps.
    
    Returns:
    xarray.Dataset: The dataset with gaps filled or interpolated.
    """
    default = dict(
        fill_value='extrapolate')
    default.update(kwargs)
    kwargs = default
    
    filled = {var: data[var].interpolate_na(
        dim=dim, **kwargs) for var in selected_vars if var in data}

    return type(
        'var_', (object,),
        filled
    )
