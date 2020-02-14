"""Regroup all the functions related to calculations."""

import math
from time import sleep


def dotproduct(u, v):
    """Return the dot product of two vectors."""
    dp = u[0]*v[0] + u[1]*v[1] + u[2]*v[2]
    return dp


def length(u):
    """Return the length of a vector."""
    len = math.sqrt(dotproduct(u, u))
    return len


def angle(u, v):
    """Return the angle between two vectors."""
    rad_angle = math.acos(dotproduct(u, v) / (length(u) * length(v)))
    return rad_angle * 180.0 / math.pi


def distance(a, b):
    """Return the distance between two points."""
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2)


def relativeError(realValue, targetValue):
    """Return the relative error between real and the theoretical value."""
    relErr = (realValue - targetValue) / abs(targetValue)
    return relErr


def getUtSlice(ut, factor):
    """Divide the rotational period of Kerbin into a number of slices.
    
    Return the number of slices elapsed since T0.
    """
    kerbinRotationalPeriod = 21549.42578125

    slice = ut // (kerbinRotationalPeriod / factor)
    return slice


def getOrbitalPeriod(sma, mu):
    """Return the orbital period of a vessel, using the semi major axis."""
    period = 2 * math.pi * math.sqrt(sma**3 / mu)
    return period


def getKerbinLocalGravity(meanAltitude):
    """Return the local gravity seen by a vessel arround Kerbin."""
    g = 9.81
    R = 600000.0
    localGravity = g * (R / (R + meanAltitude))**2
    return localGravity


def getSemiMajorAxis(period, mu):
    """Return the semi major axis of an orbit, using the orbital period."""
    sma = ((mu * period**2) / (4 * math.pi**2)) ** (1 / 3)
    return sma


def getTimeOfAscendingNode(conn):
    """Return the ut of the next ascending node."""
    mj = conn.mech_jeb
    planner = mj.maneuver_planner
    mjInc = planner.operation_inclination

    mjInc.time_selector.time_reference = mj.TimeReference.eq_ascending
    anNode = mjInc.make_node()
    anUT = anNode.ut
    sleep(0.1)
    anNode.remove()
    return anUT


def findClosestVessel(conn, vessel=None, sphere=10000):
    """Return the closest vessel to the vessel in a sphere arroud it.

    If no origin vessel is given, the active vessel will be taken by default.
    Sphere radius in meters (default : 10000).
    If no vessel is found in the sphere, returns None.
    """
    if vessel is None:
        vessel = conn.space_center.active_vessel

    vesselList = conn.add_stream(getattr, conn.space_center, 'vessels')
    refFrame = vessel.reference_frame
    minDist = sphere + 1000
    closestVessel = None

    for V in vesselList():
        dist = length(V.position(refFrame))
        if dist < sphere:
            if V != vessel and dist < minDist:
                closestVessel = V
                minDist = dist

    return closestVessel
