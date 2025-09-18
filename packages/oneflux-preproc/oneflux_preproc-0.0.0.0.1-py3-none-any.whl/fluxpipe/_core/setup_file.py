# -*- coding: utf-8 -*-
""" Create, read, and save setup configuration files.
This module provides functions to read and write setup configuration files in a format similar to INI files.
"""

# built-in modules
import re
import os
import warnings
import logging
from functools import reduce

# 3rd party modules
import numpy as np
import pandas as pd

# project modules

logger = logging.getLogger('ep._core.setup_file')


def read_setup_file(filename):
    """Read a setup configuration file and return a dictionary.
    The file should be in a format similar to INI files, with sections and key-value pairs.
    Args:
        filename (str): The name of the file to read.
    Returns:
        dict: A dictionary containing the setup configuration.
    """
    setup = {}
    with open(filename, 'r') as file:
        section = None
        for line in file:
            line = line.strip()
            if line.startswith(';') or not line:
                continue  # Skip comments and empty lines
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]  # Extract section name
                setup[section] = {}
            else:
                key, value = line.split('=', 1)
                setup[section][key.strip()] = value.strip()
    return setup


def save_setup_file(setup, filename):
    """Save the setup configuration to a file in a format similar to INI files.
    The setup dictionary should have sections as keys and dictionaries of key-value pairs as values.
    Args:
        setup (dict): The setup configuration to save.
        filename (str): The name of the file to save the setup to.
    """
    with open(filename, 'w') as file:
        for section, values in setup.items():
            file.write(f'[{section}]\n')
            for key, value in values.items():
                file.write(f'{key} = {value}\n')
            file.write('\n')  # Add a newline after each section
    return