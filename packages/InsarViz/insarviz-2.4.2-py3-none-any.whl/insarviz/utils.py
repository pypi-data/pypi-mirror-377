#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" utils

This module contains miscellaneous utils methods:
* normalize_path - transform a path string into a pathlib.Path
* get_nearest - get index and value of closest value in array to target
value
* openUrl - open webpage of documentation
"""

# imports ###################################################################

from typing import Union

import pathlib

import numpy as np

from PySide6.QtWidgets import QMessageBox

from PySide6.QtCore import QUrl

from PySide6.QtGui import QDesktopServices

# utils #####################################################################


def normalize_path(path: str, project_path: str = "") -> pathlib.Path:
    """
    Transform a path string into a pathlib.Path.

    Parameters
    ----------
    path : str

    Returns
    -------
    pathlib.Path
    """
    # test if path is a correct absolute path to a file
    normalized_path = pathlib.Path(path)
    if normalized_path.exists():
        return normalized_path
    # test if path is a correct relative path to a file
    normalized_path = pathlib.Path(project_path).parent / pathlib.Path(path)
    if normalized_path.exists():
        return normalized_path
    # test if path is a correct absolute path to a file in Windows format
    normalized_path = pathlib.Path(pathlib.PureWindowsPath(path).as_posix())
    if normalized_path.exists():
        return normalized_path
    # test if path is a correct relative path to a file in Windows format
    normalized_path = pathlib.Path(pathlib.PureWindowsPath(
        project_path).parent.as_posix()) / pathlib.Path(pathlib.PureWindowsPath(path).as_posix())
    if normalized_path.exists():
        return normalized_path
    # else path may be an url
    return pathlib.Path(path)


def get_nearest(array, value):
    """
    Look into an array to find the nearest value to input value.
    Nearest is defined as minimal absolute difference between tested values.
    Returns array value and index of the nearest array value.

    Examples:
    ---------
    a = numpy.array((1, 5, 13, 7))
    get_nearest(a, 8)
    (7, 3)
    get_nearest(a, 1.23)
    (1, 0)

    Parameters
    ----------
    array : array
        Array where to look for the nearest value.
    value : int or float
        Value whose nearest value we want to find in the array.

    Returns
    -------
    array[idx], idx : tuple
        Nearest value found in array, index of nearest value found in array.

    """
    array = np.asarray(array)
    idx = (np.abs(array-value)).argmin()
    return array[idx], idx


def openUrl(self):
    """
    open url of documentation

    Returns
    -------
    None.

    """
    url = QUrl('https://deformvis.gricad-pages.univ-grenoble-alpes.fr/insarviz/index.html')  # noqa
    if not QDesktopServices.openUrl(url):
        QMessageBox.warning(self, 'Open Url', 'Could not open url')
