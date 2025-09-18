import numpy as np
from .units import convert_unit, ureg
from . import constants

# Constants
Ru = ureg('8.314 J/mol/K')          # universal gas constant J/[mol K]
M_d = ureg('0.02897 kg/mol')       # kg/mol (dry air)
M_h2o = ureg('0.01802 kg/mol')     # kg/mol (water vapor)
R_h2o = Ru / M_h2o     # J/(kg·K)
R_d = Ru / M_d        # J/(kg·K)
e_base = np.e       # base of natural log


def add_micrometeorological_variables_to_data(data):
    # # Example conditions
    # Ta = 298.15   # ambient temperature in K
    # Pa = 101325   # ambient pressure in Pa
    # chi = 0.01    # mol fraction H₂O
    # Tsonic = 299  # sonic temperature if used

    # Ta = data.t_ga.copy()
    # Ta.data = (data.t_ga.values + 273.15) * ureg('kelvin')  # Ambient temperature in Celsius
    Ta = data.ta
    Pa = data.press_cell # * 1e3
    chi = data.h2o * 1e-3
    Tsonic = data.t_sonic

    data = data.assign(Pa=Pa,)

    # T = data.t_sonic - 273.15  # Convert to Celsius if needed
    # if (Stats % Mean(te) > 220d0 . and . Stats % Mean(te) < 340d0) Stats % T = Stats % Mean(te)
    # if (biomet % val(bTa) > 220d0 . and . biomet % val(bTa) < 340d0) Stats % T = biomet % val(bTa)
    # Stats % Pr = Metadata % bar_press
    # if (Stats % Mean(pe) > 40000 . and . Stats % Mean(pe) < 110000) Stats % Pr = Stats % Mean(pe)
    # if (biomet % val(bPa) > 40000 . and . biomet % val(bPa) < 110000) Stats % Pr = biomet % val(bPa)

    # Ambient air molar volume[m+3 mol-1] and air mass density[kg m-3]
    # if (Stats % Pr > 0d0 . and . Stats % T /= error) then
    Va = constants.R * Tsonic / Pa
    data = data.assign(Va=Va,)
    
    data = data.assign(
        Ma=molecular_weight_wet_air(chi),)
    data = data.assign(
        rho_h2ov=rho_h2o(chi, Pa, Va),)
    data = data.assign(
        e=water_vapor_partial_pressure(data.rho_h2ov, data.t_sonic),)

    data = data.assign(
        air_temperature=air_temperature_derived_from_sonic_temperature(data.t_sonic, data.e, data.Pa),)

    data = data.assign(
        es=saturation_vapor_pressure(data.air_temperature),)

    data = data.assign(
        RH=relative_humidity(data.e, data.es),)
    data = data.assign(
        VPD=vapor_pressure_deficit(data.e, data.es),)
    data = data.assign(
        Td=dew_point_temperature(data.e),)  # e in kPa
    data = data.assign(
        Pd=dry_air_partial_pressure(data.Pa, data.e),)
    data = data.assign(
        air_molar_volume=dry_air_molar_volume(data.Pd, data.air_temperature),)
    data = data.assign(
        sealevel_moist_air_molar_volume=sealevel_moist_air_molar_volume(
            data.air_temperature, data.e),)
    data = data.assign(
        rho_d=dry_air_mass_density(data.Pd, Ta),)
    data = data.assign(
        rho_m=moist_air_density(data.rho_d, data.rho_h2ov),)
    data = data.assign(
        cpd=cp_d(Ta),)
    data = data.assign(
        cph2o=cp_h2o(data.RH, Ta),)
    data = data.assign(
        q=specific_humidity(data.e, Pa),)
    data = data.assign(
        Ta_refined=refine_Ta_sonic(data.q, Ta),)
    data = data.assign(
        cp_m=moist_air_cp(data.q, data.cpd, data.cph2o),)
    data = data.assign(
        lambda_v=latent_heat_vaporization(Ta),)
    data = data.assign(
        sigma=density_ratio_sigma(data.rho_h2ov, data.rho_d),)

    return data


def air_temperature_derived_from_sonic_temperature(Ts, e, Pa):
    return Ts * (1+0.32*e/Pa)**-1   # - 273.15


def molecular_weight_wet_air(chi_h2o):
    return constants.Mv * chi_h2o + constants.Md * (1 - chi_h2o)


def rho_h2o(chi_h2o, P, Va):
    # Using ideal gas: ρ = (P * χ) / (R_specific * T)
    # return chi_h2o * P / Va
    return chi_h2o / Va * constants.Mv


def water_vapor_partial_pressure(rho_h2o, Ta):
    # Using ideal gas law: e = ρ * R_specific * T
    # where R_specific for water vapor is R_h2o = Ru / M_h2
    # Ta in Kelvin
    # The same as chi_h2o / Ru * Pa * constants.Mv * R_h2o
    return rho_h2o * constants.Rv * Ta


def saturation_vapor_pressure(Ta):
    # # Campbell & Norman (1998): es = 0.6108 * exp(17.27 * (T - 273.15)/(T - 35.85))
    # Tc = Ta - 273.15
    # return 610.78 * np.exp((17.269 * Tc) / (Tc + 237.3))
    es = Ta.copy()
    Tc = Ta.data.to('delta_degC').magnitude
    es.data = Tc**-8.2 * np.exp(77.345+0.0057*Tc-7235*Tc**-1)
    es.data = es * ureg('Pa')
    return es


def relative_humidity(e, es):
    return 100 * e / es


def vapor_pressure_deficit(e, es):
    return e - es


def dew_point_temperature(e):
    # # Campbell & Norman: Tdew = (243.5 * ln(e/0.6108)) / (17.27 - ln(e/0.6108)) + 273.15
    # return (243.5 * np.log(e_kPa / 0.6108) /
    #         (17.27 - np.log(e_kPa / 0.6108))) + 273.15
    Td = e.copy()
    e_kPa = convert_unit(e, 'kPa').values
    Td.data = 240.97 * np.log(e_kPa / 0.611) / (17.502 - np.log(e_kPa / 0.611))
    Td.data = Td * ureg('kelvin')
    return Td


def dry_air_partial_pressure(Pa, e):
    return Pa - e


def dry_air_molar_volume(Pd, Ta):
    # Ru is the universal gas constant in J/(mol·K)
    # Pd is the dry air partial pressure
    # Ta is the ambient temperature in Celsius
    # Ambient%Vd = (Stats%Pr * Ambient%Va) / Ambient%p_d
    # Va = Ru * Ta / Pa

    # Ta + 273.15
    Vd = constants.R * Ta / Pd
    return Vd


def sealevel_moist_air_molar_volume(Ta, e):
    Vsea = constants.R * Ta / (ureg("99767.5 pascal") - e)
    return Vsea

def dry_air_mass_density(Pd, Ta):
    return Pd / (constants.Rd * Ta)


def moist_air_density(rho_d, rho_h2o):
    return rho_d + rho_h2o


def cp_d(Tk):
    """
    Calculate the specific heat capacity of dry air at constant pressure (cp_d).

    Uses a temperature-dependent empirical formula to compute the specific heat
    capacity of dry air as a function of temperature.
    """
    cpd = Tk.copy()
    # Ta is in celsius
    Ta = Tk.data.to('delta_degC') / ureg('delta_degC')
    cpd.data = (constants.Cpd.to("J/kg/K") +
                ((Ta + 23.12)**2 / 3364) * ureg("J/kg/K"))
    return cpd


def cp_h2o(RH, Tk):
    cpv = Tk.copy()
    # Ta is in celsius
    Ta = Tk.data.to('delta_degC').magnitude
    cpv.data = (1859 + 0.13 * RH + (0.193 + 5.6 * 1e-3 * RH)
                             * Ta + (1e-3 + 5 * 1e-5 * RH) * Ta**2) * ureg("J/kg/K")
    return cpv


def specific_humidity(rho_h2o, rho_a):
    return rho_h2o / rho_a


def refine_Ta_sonic(q, Ta):
    return Ta / (1 + 0.51 * q)


def moist_air_cp(q, cp_d, cp_h2o):
    return (1 - q) * cp_d + q * cp_h2o


def latent_heat_vaporization(Tk):
    # Ta is in celsius
    lambdav = Tk.copy()
    Ta = Tk.data.to('delta_degC')
    lambdav.data = 1e3 * (ureg('3147.5 J/g') -
                          ureg('2.37 J/g/delta_degC') * Ta)
    return lambdav


def density_ratio_sigma(rho_h2o, rho_d):
    return rho_h2o / rho_d


def wind_direction(u, v, offset=0):
    """
    Calculate wind direction from u and v wind components.
    
    Parameters:
        u (float or np.ndarray): zonal wind component (positive eastward)
        v (float or np.ndarray): meridional wind component (positive northward)

    Returns:
        float or np.ndarray: wind direction in degrees, where 0° = North, 90° = East, etc.
    """
    direction = (180 - np.degrees(np.arctan2(v, u))) % 360
    direction = (direction + offset) % 360
    return direction
