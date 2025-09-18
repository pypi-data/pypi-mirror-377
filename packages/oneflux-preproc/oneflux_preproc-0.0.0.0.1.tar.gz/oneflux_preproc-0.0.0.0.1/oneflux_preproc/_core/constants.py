from .units import ureg

beta = 5       # "beta" value in adiabatic correction to wind profile
Cd = ureg('840.0 J/kg/K')      # heat capacity of mineral component of soil, J/kg/K
Co = ureg('1920.0 J/kg/K')     # heat capacity of organic component of soil, J/kg/K
Cp = ureg('1004.67 J/kg/K')    # specific heat of dry air at constant pressure, J/kg-K
Cpd = ureg('1004.67 J/kg/K')   # specific heat of dry air at constant pressure, J/kg-K
Cw = ureg('4180.0 J/kg/K')    # heat capacity of water, J/kg/K
D0 = 10.       # specific humidity deficit threshold for Lasslop et al (2010) NEE expression
E0_long = 100  # long term activation energy, default value
eps = 0.0000001 # a small number for comparing floats
g = 9.81       # gravitation constant
gamma = 28     # "gamma" value in adiabatic correction to wind profile
g2kg = 1E-3    # convert grams to kilograms
k = 0.4        # von Karmans constant
Lv = ureg('2453600 J/kg')   # latent heat of vapourisation, J/kg
Mc = ureg('0.0120107 kg/mol')  # molecular weight of carbon, kg/mol
Mco2 = ureg('0.04401 kg/mol')  # molecular weight of carbon dioxide, kg/mol
Md = ureg('0.02897 kg/mol')   # molecular weight of dry air, kg/mol
missing_value = -9999         # missing data value
large_value = 1E35            # large value
small_value = -1E35           # small value
Mv = ureg('0.01802 kg/mol') # 0.01802   # molecular weight of water vapour, kg/mol
mu = Md/Mv     # ratio of dry air molecular weight to water vapour molecular weight
rho_water = ureg('1000.0 kg/m^3') # density of water, kg/m^3
R = ureg('8.314 J/mol/K')      # universal gas constant, J/mol.K
Rd = ureg('287.04 J/kg/K')    # gas constant for dry air, J/kg/K
Rv = ureg('461.5 J/kg/K')     # gas constant for water vapour, J/kg/K
Pi = 3.14159   # Pi
sb = ureg('5.6704E-8 W/m^2/K^4')  # Stefan-Boltzman constant, W/m^2/K^4
Tref = ureg('15.0 delta_degC')    # reference temperature in the Lloyd-Taylor respiration equation, degC
T0   = ureg('-46.02 delta_degC')  # zero temp[erature in the Lloyd-Taylor respiration equation, degC
P0a = ureg('10**5 Pa')  # reference pressure for potential temperature, Pa
Tb = 1800      # 30-min period, seconds
C2K = 273.15   # convert degrees celsius to kelvin
# dictionary of instrument characteristics
# used in pfp_ts.MassmanStandard(), pfp_compliance.l1_check_sonic_type() and
# pfp_compliance.l1_check_irga_type()
# 'no_sonic' is for IRGAs used in profile measurements
instruments = {"sonics": {"CSAT3": {"lwVert": 0.115, "lwHor": 0.058, "lTv": 0.115},
                          "CSAT3A": {"lwVert": 0.115, "lwHor": 0.058, "lTv": 0.115},
                          "CSAT3B": {"lwVert": 0.115, "lwHor": 0.058, "lTv": 0.115},
                          "WindMaster-Pro": {"lwVert": 0.106, "lwHor": 0.107, "lTv": 0.106}},
               "irgas": {"open_path": {"Li-7500": {"dIRGA": 0.0095, "lIRGA": 0.127},
                                       "Li-7500A": {"dIRGA": 0.0095, "lIRGA": 0.127},
                                       "Li-7500RS": {"dIRGA": 0.0095, "lIRGA": 0.127},
                                       "Li-7500DS": {"dIRGA": 0.0095, "lIRGA": 0.127},
                                       "EC150": {"dIRGA": 0.01, "lIRGA": 0.154},
                                       "IRGASON": {"dIRGA": 0.01, "lIRGA": 0.154}},
                         "closed_path": {"Li-7200": {"dIRGA": 0.0064, "lIRGA": 0.125},
                                         "Li-7200RS": {"dIRGA": 0.0064, "lIRGA": 0.125},
                                         "Li-7200DS": {"dIRGA": 0.0064, "lIRGA": 0.125},
                                         "EC155": {"dIRGA": 0.008, "lIRGA": 0.120},
                                         "Li-830": {"dIRGA": None, "lIRGA": None},
                                         "Li-840": {"dIRGA": None, "lIRGA": None},
                                         "Li-850": {"dIRGA": None, "lIRGA": None},
                                         "None": {"dIRGA": None, "lIRGA": None}}}}
# dictionary of site names and time zones
tz_dict = {"adelaideriver":"Australia/Darwin",
           "alicespringsmulga":"Australia/Darwin",
           "arcturus":"Australia/Brisbane",
           "calperum":"Australia/Adelaide",
           "capetribulation":"Australia/Brisbane",
           "cowbay":"Australia/Brisbane",
           "cumberlandplains":"Australia/Sydney",
           "cup_ec":"Australia/Sydney",
           "daintree":"Australia/Brisbane",
           "dalypasture":"Australia/Darwin",
           "dalyregrowth":"Australia/Darwin",
           "dalyuncleared":"Australia/Darwin",
           "dargo":"Australia/Melbourne",
           "dryriver":"Australia/Darwin",
           "foggdam":"Australia/Darwin",
           "gingin":"Australia/Perth",
           "greatwestern":"Australia/Perth",
           "gww":"Australia/Perth",
           "howardsprings":"Australia/Darwin",
           "litchfield":"Australia/Darwin",
           "nimmo":"Australia/Sydney",
           "reddirt":"Australia/Darwin",
           "riggs":"Australia/Melbourne",
           "robson":"Australia/Brisbane",
           "samford":"Australia/Brisbane",
           "sturtplains":"Australia/Darwin",
           "titreeeast":"Australia/Darwin",
           "tumbarumba":"Australia/Canberra",
           "wallaby":"Australia/Melbourne",
           "warra":"Australia/Hobart",
           "whroo":"Australia/Melbourne",
           "wombat":"Australia/Melbourne",
           "yanco_jaxa":"Australia/Sydney"}
units_synonyms = {"Fsd":["W/m^2","W+1m-2"],
                  "Fsu":["W/m^2","W+1m-2"],
                  "Fld":["W/m^2","W+1m-2"],
                  "Flu":["W/m^2","W+1m-2"],
                  "Fn":["W/m^2","W+1m-2"],
                  "Fg":["W/m^2","W+1m-2"],
                  "Precip":["mm"],
                  "ps":["kPa"],
                  "RH":["%","percent"],
                  "Sws":["frac","m^3/m^3","m+3m-3"],
                  "Ta":["C","degC"],
                  "Ts":["C","degC"],
                  "Wd":["degT","deg","degrees"],
                  "Ws":["m/s","m+1s-1"]}