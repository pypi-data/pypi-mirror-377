from . import PyFluxPro, EddyPro, OneFlux
from configobj import ConfigObj


def convert_to_setup(setup, save_to=None):
    setup = ConfigObj(setup)
    setup["level"] = "L0"
    setup.filename = save_to
    if save_to:
        setup.write()
    return setup
