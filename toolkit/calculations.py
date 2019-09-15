import krpc
import math

def getOrbitalPeriod(sma,mu):
    """Return the orbital period of a vessel, using the semi major axis.

    """
    period = 2 * math.pi * math.sqrt(sma**3 / mu)
    return period

def getSemiMajorAxis(period,mu):
    """Return the semi major axis of an orbit, using the orbital period.

    """
    sma = ((mu * period**2) / (4 * math.pi**2)) ** (1 / 3)
    return sma
