"""Regroup all the functions related to the impact pos of the vessel."""

from math import cos, sin


class ImpactInfos:
    """Contains all the infos of the impact point."""

    def __init__(self, time, latitude, longitude, altitude):
        """Initialize the class with the given parameters."""
        self.impactTime = time
        self.impactLatitude = latitude
        self.impactLongitude = longitude
        self.impactAltitude = altitude


def GetImpactInfos(sc, obt):
    """Get and return impact infos.

    Return a class with the time, latitude, longitude, and altitude of impact
    Args:
    -sc : space_center object
    -obt : orbit object of the vessel

    """
    kerbin = obt.body
    krf = kerbin.reference_frame
    t0 = sc.ut
    tA = t0  # Start time
    tB = t0 + 30.0  # End time
    while kerbin.altitude_at_position(obt.position_at(tB, krf), krf) > 0.0:
        tB += 30.0  # Making sure we're below 0 meters at t=tB
    dt = tB - tA  # Time difference between tA and tB

    while dt > 0.0001:  # For sufficient precision
        tM = (tA + tB) / 2  # Mean time between tA and tB
        pos = obt.position_at(tM, krf)  # position vector at t=tM
        T = tM-t0  # time to impact

        # Revised pos vector (taking Kerbin rotation into account)
        theta = T * kerbin.rotational_speed
        pos = (pos[0]*cos(theta) + pos[2]*sin(theta),
               pos[1],
               -pos[0]*sin(theta) + pos[2]*cos(theta))

        # Finding vessel altitude at t=tM
        r = kerbin.altitude_at_position(pos, krf)

        # Dichotomy principle
        if r < 0.0:
            tB = tM
        else:
            tA = tM

        # New time difference between tA and tB
        dt = tB-tA

    impactTime = tM
    impactLatitude = kerbin.latitude_at_position(pos, krf)
    impactLongitude = kerbin.longitude_at_position(pos, krf)
    impactAltitude = kerbin.surface_height(impactLatitude, impactLongitude)

    # Return a class containing time/lat/long/alt of impact
    return ImpactInfos(impactTime, impactLatitude,
                       impactLongitude, impactAltitude)
