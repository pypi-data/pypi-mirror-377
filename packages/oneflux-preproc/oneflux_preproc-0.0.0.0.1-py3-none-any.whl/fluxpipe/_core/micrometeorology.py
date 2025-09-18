import numpy as np

# Constants
Ru = 8.314          # universal gas constant J/[mol K]
M_d = 0.02897       # kg/mol (dry air)
M_h2o = 0.01802     # kg/mol (water vapor)
R_h2o = Ru / M_h2o     # J/(kg·K)
R_d = Ru / M_d        # J/(kg·K)
e_base = np.e       # base of natural log


def add_micrometeorological_variables_to_data(data):
    # # Example conditions
    # Ta = 298.15   # ambient temperature in K
    # Pa = 101325   # ambient pressure in Pa
    # chi = 0.01    # mol fraction H₂O
    # Tsonic = 299  # sonic temperature if used

    Ta = data.t_ga  # Ambient temperature in Celsius
    Pa = data.press_cell * 1e3
    chi = data.h2o * 1e-3
    Tsonic = data.t_sonic

    # T = data.t_sonic - 273.15  # Convert to Celsius if needed
    # if (Stats % Mean(te) > 220d0 . and . Stats % Mean(te) < 340d0) Stats % T = Stats % Mean(te)
    # if (biomet % val(bTa) > 220d0 . and . biomet % val(bTa) < 340d0) Stats % T = biomet % val(bTa)
    # Stats % Pr = Metadata % bar_press
    # if (Stats % Mean(pe) > 40000 . and . Stats % Mean(pe) < 110000) Stats % Pr = Stats % Mean(pe)
    # if (biomet % val(bPa) > 40000 . and . biomet % val(bPa) < 110000) Stats % Pr = biomet % val(bPa)

    # Ambient air molar volume[m+3 mol-1] and air mass density[kg m-3]
    # if (Stats % Pr > 0d0 . and . Stats % T /= error) then
    Va = Ru * Tsonic / Pa
    data = data.assign(Va=Va,)
    
    data = data.assign(
        Ma=molecular_weight_wet_air(chi),)
    data = data.assign(
        rho_h2ov = rho_h2o(chi, Pa, Va),)
    data = data.assign(
        e=water_vapor_partial_pressure(data.rho_h2ov, Tsonic),)
    data = data.assign(
        es=saturation_vapor_pressure(Ta),)

    data = data.assign(
        air_temperature=air_temperature_derived_from_sonic_temperature(Tsonic, data.e, Pa),)
    
    data = data.assign(
        RH=relative_humidity(data.e, data.es),)
    data = data.assign(
        VPD=vapor_pressure_deficit(data.e, data.es),)
    data = data.assign(
        Td=dew_point_temperature(data.e / 1000),)  # e in kPa
    data = data.assign(
        Pd=dry_air_partial_pressure(Pa, data.e),)
    data = data.assign(
        air_molar_volume=dry_air_molar_volume(data.Pd, data.air_temperature),)
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
    return Ts * (1+0.32*e/Pa)**-1 - 273.15


def molecular_weight_wet_air(chi_h2o):
    return M_h2o * chi_h2o + M_d * (1 - chi_h2o)


def rho_h2o(chi_h2o, P, Va):
    # Using ideal gas: ρ = (P * χ) / (R_specific * T)
    # return chi_h2o * P / Va
    return chi_h2o / Va * M_h2o


def water_vapor_partial_pressure(rho_h2o, Ta):
    # Using ideal gas law: e = ρ * R_specific * T
    # where R_specific for water vapor is R_h2o = Ru / M_h2
    # Ta in Kelvin
    # The same as chi_h2o / Ru * Pa * M_h2o * R_h2o
    return rho_h2o * R_h2o * Ta


def saturation_vapor_pressure(Ta):
    # # Campbell & Norman (1998): es = 0.6108 * exp(17.27 * (T - 273.15)/(T - 35.85))
    # Tc = Ta - 273.15
    # return 610.78 * np.exp((17.269 * Tc) / (Tc + 237.3))
    return Ta**-8.2 * np.exp(77.345+0.0057*Ta-7235*Ta**-1)


def relative_humidity(e, es):
    return 100 * e / es


def vapor_pressure_deficit(e, es):
    return e - es


def dew_point_temperature(e_kPa):
    # # Campbell & Norman: Tdew = (243.5 * ln(e/0.6108)) / (17.27 - ln(e/0.6108)) + 273.15
    # return (243.5 * np.log(e_kPa / 0.6108) /
    #         (17.27 - np.log(e_kPa / 0.6108))) + 273.15
    return (240.97 * np.log(e_kPa / 0.611) /
            (17.502 - np.log(e_kPa / 0.611))) + 273.15


def dry_air_partial_pressure(Pa, e):
    return Pa - e


def dry_air_molar_volume(Pd, Ta):
    # Ru is the universal gas constant in J/(mol·K)
    # Pd is the dry air partial pressure
    # Ta is the ambient temperature in Celsius
    # Ambient%Vd = (Stats%Pr * Ambient%Va) / Ambient%p_d
    # Va = Ru * Ta / Pa

    Vd = Ru * (Ta + 273.15) / Pd
    return Vd


def dry_air_mass_density(Pd, Ta):
    return Pd / (R_d * Ta)


def moist_air_density(rho_d, rho_h2o):
    return rho_d + rho_h2o


def cp_d(Ta):
    # Ta is in celsius
    return 1005 + (Ta+23.12)**2 / 3364


def cp_h2o(RH, Ta):
    # Ta is in celsius
    return 1859 + 0.13 * RH +(0.193 + 5.6 * 1e-3 * RH) * Ta + (1e-3 + 5 * 1e-5 * RH) * Ta**2


def specific_humidity(rho_h2o, rho_a):
    return rho_h2o / rho_a


def refine_Ta_sonic(q, Ta):
    return Ta / (1 + 0.51 * q)


def moist_air_cp(q, cp_d, cp_h2o):
    return (1 - q) * cp_d + q * cp_h2o


def latent_heat_vaporization(Ta):
    # Ta is in celsius
    return 1e3 * (3147.5 - 2.37 * Ta)


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
