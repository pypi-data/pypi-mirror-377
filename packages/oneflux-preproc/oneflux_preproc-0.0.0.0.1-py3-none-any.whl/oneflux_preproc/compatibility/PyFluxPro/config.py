
# built-in modules
from configobj import ConfigObj
import re
import os
import warnings
import logging
from functools import reduce

# 3rd party modules
import numpy as np
import pandas as pd

# project modules

logger = logging.getLogger('wvlt.pyfluxpro_compatibility')

def copy_values_from(source, target, overwrite=True):
    result = {}
    for key, val in source.items():
        if isinstance(val, dict):
            # Recurse into nested dict
            result[key] = copy_values_from(val, target.get(key, {}))
        else:
            if overwrite:
                # Copy value from target if exists, else keep original
                result[key] = target.get(key, val)
            else:
                result[key] = val or target.get(key, val)
    return result

def find_info_to_fill(path):
    return set(re.findall('<.*?>', str(ConfigObj(path))))

def L1_cfg(config,
           dst='eddypy/compatibility/PyFluxPro/L1.txt',
           template='eddypy/compatibility/PyFluxPro/templates/L1/L1_eddypro_csv.txt',
           **options):
    with open(dst, 'w+') as wf:
        with open(template, 'r') as rf:
            for line in rf.readlines():
                for k, v in options.items():
                    line = line.replace(f'<{k}>', v)
                wf.write(line)

    setup = ConfigObj(dst)
    setup['Files'] = config['Files']
    setup.write()
    return


def L2_cfg(config, 
           dst='eddypy/compatibility/PyFluxPro/L2.txt', 
           template='eddypy/compatibility/PyFluxPro/templates/L2/L2_eddypro.txt'):
    with open(dst, 'w+') as wf:
        with open(template, 'r') as rf:
            for line in rf.readlines():
                # for k, v in config['Options'].items():
                #     line = line.replace(f'<{k}>', v)
                wf.write(line)

    setup = ConfigObj(dst)
    setup['Files'] = config['Files']
    setup['Options'] = config['Options']
    setup.write()
    return

    
def L3_cfg(config, 
           dst='eddypy/compatibility/PyFluxPro/L3.txt', 
           template='eddypy/compatibility/PyFluxPro/templates/L3/L3_eddypro.txt'):
    with open(dst, 'w+') as wf:
        with open(template, 'r') as rf:
            for line in rf.readlines():
                for k, v in config['Options'].items():
                    line = line.replace(f'<{k}>', v)
                wf.write(line)

    setup = ConfigObj(dst)
    setup['Files'] = config['Files']
    setup['Options'] = config['Options']
    setup.write()
    return


def L4_cfg(config,
           dst='eddypy/compatibility/PyFluxPro/L4.txt',
           template='eddypy/compatibility/PyFluxPro/templates/L4/L4_fluxnet.txt'):
    with open(dst, 'w+') as wf:
        with open(template, 'r') as rf:
            for line in rf.readlines():
                for k, v in config['Options'].items():
                    line = line.replace(f'<{k}>', v)
                wf.write(line)

    setup = ConfigObj(dst)
    setup['Files'] = config['Files']
    setup['Options'] = config['Options']
    setup.write()
    return


def L5_cfg(config,
           dst='eddypy/compatibility/PyFluxPro/L5.txt',
           template='eddypy/compatibility/PyFluxPro/templates/L5/L5_MDS.txt'):
    with open(dst, 'w+') as wf:
        with open(template, 'r') as rf:
            for line in rf.readlines():
                for k, v in config['Options'].items():
                    line = line.replace(f'<{k}>', v)
                wf.write(line)

    setup = ConfigObj(dst)
    setup['Files'] = config['Files']
    setup['Options'] = config['Options']
    setup.write()
    return
