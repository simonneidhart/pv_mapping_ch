"""This module is concerned with predicting the irradiance based on the instantaneous power output
of some PV plants with power meters."""
import math


def ghi(power: float, installed_capacity: float, slope: float) -> float:
    """Calculate the global horizontal irradiance.

    Parameters
    ----------
    power
        The instantaneous power [W].
    installed_capacity
        Nominal power under standard test conditions [W/m2].
    slope
        The slope [deg].

    Returns
    -------
    float
        The global horizontal irradiance [W/m2].

    """
    if power < 0:
        power = -power

    return power * 1e6 / installed_capacity / math.cos(math.radians(slope))
