import krpc
import math
from time import sleep

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

def getTimeOfAscendingNode(conn):
    """Return the ut of the next ascending node.

    """
    mj = conn.mech_jeb
    planner = mj.maneuver_planner
    mjInc = planner.operation_inclination

    mjInc.time_selector.time_reference = mj.TimeReference.eq_ascending
    anNode = mj_inc.make_node()
    anUT = anNode.ut
    sleep(0.1)
    anNode.remove()
    return anUT
