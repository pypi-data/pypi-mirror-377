# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Module that implements a single calculation API for the Pandeia Engine
"""

from .etc3D import calculate_exposure_time, calculate_sn
from . import debug_utils

def perform_calculation(calc_input, dict_report=True, webapp=True, validate=False):
    """
    Function to perform a single ETC calculation

    Parameters
    ----------
    calc_input: dict
        Dictionary containing the information required to perform the calculation.
    dict_report: Boolean (default: True)
        If True, return a dict in engine output API format. Otherwise return
        a report.Report instance.
    webapp: Boolean (default: True)
        Toggle strict API checking for webapp
    validate: Boolean (default: False)
        Toggle whether additional intermediate products are saved internally
    """

    if True:   # you can change it to False
        if 'fake_exception' in calc_input:
            perform_fake_exceptions(calc_input)

    debug_utils.init(calc_input)

    # run the calculation....
    snr = calc_input['configuration']['detector'].get('calculate_snr', True)
    if snr:
        report = calculate_sn(calc_input, webapp=webapp, validate=validate)
    else:
        report = calculate_exposure_time(calc_input, webapp=webapp, validate=validate)

    if dict_report:
        return report.as_dict()
    else:
        return report


def perform_fake_exceptions(calc_input):
    """
    Generate fake exceptions for testing

    Parameters
    ----------
    calc_input : dict
        A heirarchical calculation input dictionary

    Raises
    ------
    custom_exceptions.PandeiaException
        Testing exception for custom Pandeia errors
    Exception
        Testing exception for generic errors
    """
    i = calc_input['fake_exception']
    if 'pandeia' in i:
        from . import custom_exceptions
        raise custom_exceptions.PandeiaException("fake pandeia exception for testing")
    if 'exception' in i:
        raise Exception("fake abnormal exception for testing")
