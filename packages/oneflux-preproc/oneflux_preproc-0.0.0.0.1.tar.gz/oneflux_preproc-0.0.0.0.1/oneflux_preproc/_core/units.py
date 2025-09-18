import pint
from pint.errors import UndefinedUnitError
import pint_xarray

ureg = pint.UnitRegistry(force_ndarray_like=True)
# Define ppm as a dimensionless unit if not already defined
ureg.define('ppm = 1e-6 = parts_per_million')
ureg.define('ppt = 1e-3 = parts_per_thousand')
ureg.define('µmol = 1e-6 mole = micromol')
ureg.define('celsius = delta_degC = celsius')

# Register your registry globally for pint-pandas
pint_xarray.setup_registry(ureg)
pint.set_application_registry(ureg)

# Define aliases (case-insensitive mapping)
UNIT_ALIASES = {
    'ppt': '1e-3',
    'ppm': '1e-6',
    'ppb': '1e-9',
    'kpa': 'kilopascal',
    'μmol': 'micromole',
    'umol': 'micromole',
    'ug': 'microgram',
    'lit/m': 'L/min',
    'celsius': 'delta_degC',
    'kelvin': 'Kelvin',
}


def resolve_unit(unit_str: str):
    """
    Attempts to resolve a unit string using Pint.
    Falls back to alias lookup if the unit is not found.
    """
    unit_str = unit_str.replace('_', '/')

    if not unit_str:
        return ureg('dimensionless')  # Treat empty as dimensionless

    try:
        return ureg(unit_str)
    except UndefinedUnitError:
        # Try alias map (case-insensitive)
        unit_str_lower = unit_str.lower()
        alias = UNIT_ALIASES.get(unit_str_lower)
        if alias:
            return ureg(alias)
        else:
            raise UndefinedUnitError(
                f"Unit '{unit_str}' not found and no alias matched.")


def convert_unit(da, to_units):
    """
    Convert an xarray.DataArray containing Pint Quantities in .values to new units.

    Parameters:
        da: xarray.DataArray with pint.Quantity values
        to_units: string or Pint Unit to convert to, e.g. 'degC', 'meter'

    Returns:
        xarray.DataArray with converted magnitude and updated units attribute.
    """
    q = da.data  # should be a Pint Quantity
    converted_q = q.to(to_units)

    # Rebuild DataArray with converted magnitude and original coords/dims
    da_converted = da.copy()
    da_converted.data = converted_q  # .magnitude
    da_converted.attrs = da.attrs.copy()
    da_converted.attrs['unit_in'] = str(converted_q.units)
    return da_converted


def convert_to_prefered_units(ds, units=["μmol/m²/s", "m/s", "W/m²", "g/m²/s"]):
    for var in ds.data_vars:
        for target_unit in units:
            try:
                # Try to convert
                ds[var].data = ds[var].data.to(target_unit)
                break  # Stop at the first successful conversion
            except Exception as e:
                continue  # Try next unit
    return ds

def DEPRECATED_compute_equation(data, y: str, *args: str, formula, unit_formula=None):
    """
    Compute a new variable `y` using the given formula and attach unit metadata.

    Parameters:
        data: xarray.Dataset or pandas.DataFrame-like (must support .assign and .attrs)
        y (str): Name of the new variable to be created
        *args (str): Names of existing variables used in the formula
        formula (function): A function that takes data[args[0]], data[args[1]], ..., and returns a computed value

    Returns:
        data with new variable y and computed unit metadata
    """
    if not unit_formula:
        unit_formula = formula

    # Evaluate the formula using the columns passed in
    variables = [data[var] for var in args]
    result = formula(*variables)

    # Assign result to new variable y
    data = data.assign(**{y: result})

    # Attempt to compute units
    data[y].attrs = getattr(data[y], 'attrs', {})
    data[y].attrs['unit_in'] = ""

    try:
        # Get unit strings from input variables
        units = [data[arg].attrs['unit_in'] for arg in args]

        # Build Pint quantities for each variable
        pint_quantities = [resolve_unit(u) for u in units]
        # pint_quantities = [ureg(unit if unit else 'dimensionless')
        #                    for unit in units]

        # Simulate formula on Pint quantities to get output unit
        unit_result = unit_formula(*pint_quantities).to_base_units()

        # Store result unit
        data[y].attrs['unit_in'] = str(unit_result)

    except Exception as e:
        data[y].attrs['unit_in'] = f"Error computing units: {e}"

    return data
