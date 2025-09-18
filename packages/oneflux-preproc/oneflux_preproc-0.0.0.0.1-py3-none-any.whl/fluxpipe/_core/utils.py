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
