# the following line needed for unicode character in convert_anglestring
# -*- coding: latin-1 -*-
# standard modules
import copy
import datetime
import logging
import numbers
import os
import platform
import sys
import time
# third party modules
import dateutil
import numpy
import pytz
import xlrd
# Local modules

logger = logging.basicConfig()

def get_base_path():
    """
    Purpose:
     Return the base path dependng on whether we are running as a script
     or a Pyinstaller application.
    Author: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    """
    # check if we running as a PyInstaller application
    if getattr(sys, 'frozen', False):
        # running as a PyInstaller application
        base_path = sys._MEIPASS
    else:
        # running as a script
        base_path = os.path.abspath(".")
    return base_path


def file_exists(filename, mode="quiet"):
    """
    Purpose:
     Return True or False if file exists
    Author: OzFlux
    """
    if not os.path.exists(filename):
        if mode != "quiet":
            logger.error(" File " + filename + " not found")
        return False
    else:
        return True


def update_nested_dict(d, u):
    """
    Recursively updates a nested dictionary `d` with values from another dictionary `u`.
    If a key in `u` maps to a dictionary and the corresponding key in `d` also maps to a dictionary,
    the function updates the nested dictionary in `d`. Otherwise, it overwrites the value in `d`.

    Args:
        d (dict): The dictionary to update.
        u (dict): The dictionary containing updates.

    Returns:
        dict: The updated dictionary.
    """
    # Iterate over each key-value pair in the update dictionary `u`
    for k, v in u.items():
        # Check if the current value is a dictionary
        if isinstance(v, dict):
            # If the corresponding value in `d` is also a dictionary, recursively update it
            # Use `d.get(k, {})` to handle cases where the key `k` is not already in `d`
            d[k] = update_nested_dict(d.get(k, {}), v)
        else:
            # If the value is not a dictionary, directly update/overwrite the key in `d`
            d[k] = v
    # Return the updated dictionary
    return d


def update_nested_dicts(*ds, fstr=None):
    r = {}
    for d in ds:
        if isinstance(d, str) and fstr:
            try:
                d = fstr(d)
            except Exception as e:
                continue
        r = update_nested_dict(r, d)
    return r
