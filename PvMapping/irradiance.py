"""This module is concerned with predicting the irradiance based on the instantaneous power output
of some PV plants with power meters."""
import math

from pvlib.irradiance import erbs
from pvlib.location import Location


def get_ghi(power: float, installed_capacity: float, slope: float) -> float:
    """Calculate the global horizontal irradiance.

    Parameters
    ----------
    power
        The instantaneous power [W].
    installed_capacity
        Nominal power under standard test conditions [W].
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


def get_dni_dhi(lat, lon, timestamp, ghi) -> tuple[float, float]:
    """Calculate DNI and DHI from the GHI using the Erbs model.

    Parameters
    ----------
    lat
        The latitude in decimal degrees.
    lon
        The longitude in decimal degrees.
    timestamp
        The time at which the GHI was measured.
    ghi
        Global horizontal irradiance [W/m^2]

    Returns
    -------
    tuple
        The DNI and DHI in W/m^2
    """
    loc = Location(lat, lon)
    sol_pos = loc.get_solarposition(timestamp)
    zenith = sol_pos["zenith"]
    irradiance = erbs(ghi, zenith, timestamp)
    return float(irradiance["dni"]), float(irradiance["dhi"])
