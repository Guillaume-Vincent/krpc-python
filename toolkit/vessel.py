"""Regroup all the functions related to a vessel and its parts."""
from toolkit.calculations import getKerbinLocalGravity


def deployAntennas(vessel):
    """Deploy each deployable antenna on the vessel."""
    for antenna in vessel.parts.antennas:
        if antenna.deployable is True:
            antenna.deployed = True


def deploySolarPanels(vessel):
    """Deploy each deployable solar panel on the vessel."""
    for panel in vessel.parts.solar_panels:
        if panel.deployable is True:
            panel.deployed = True


def deployRadiators(vessel):
    """Deploy and/or activate each radiator on the vessel."""
    for rad in vessel.parts.radiators:
        if rad.deployable is True:
            rad.deployed = True
        else:
            rad.part.modules[0].trigger_event('Activate Radiator')


def deployFairing(vessel):
    """Deploy the fairing of the vessel."""
    for f in vessel.parts.fairings:
        f.jettison()


def getPartsByName(vessel, partName):
    """Return a list of all the parts named 'partName' of the vessel."""
    partList = []
    for part in vessel.parts.all:
        if part.title == partName:  # case sensitive
            partList.append(part)
    return partList


def getPartsByTag(vessel, partTag):
    """Return a list of all the parts tagged 'partTag' of the vessel."""
    partList = []
    for part in vessel.parts.all:
        if part.tag == partTag:  # case sensitive
            partList.append(part)
    return partList


def vesselChangeType(vessel, vesselType):
    """Change the type of the vessel."""
    vessel.type = vesselType


def vesselChangeName(vessel, vesselName):
    """Change the name of the vessel."""
    vessel.name = vesselName


def twrRegulation(vessel, meanAltitude, thrust, vesselMass, throttle, twrMax):
    """Adjust the throttle of the vessel to match the desired max twr.

    Args:
    -vessel : the vessel that is beeing controlled
    -meanAltitude : stream of the mean altitude of the vessel
    -thrust : stream of the thrust of the vessel
    -vesselMass : stream of the mass of the vessel
    -throttle : stream of the throttle of the vessel
    -twrMax : desired maximum twr

    """
    localGravity = getKerbinLocalGravity(meanAltitude())
    twr = thrust() / (vesselMass() * localGravity)

    if twrMax == 0.0:
        vessel.control.throttle = 0.0
    else:
        if (twr - 0.01) > twrMax:
            vessel.control.throttle -= abs(twr - twrMax) / 10

        if ((twr + 0.01) < twrMax) and (throttle() < 1.0):
            vessel.control.throttle += abs(twr - twrMax) / 10


def vesselDeorbit(conn, vessel):
    """Deorbit the vessel and change its type to debris."""
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    thrust = conn.add_stream(getattr, vessel, 'thrust')
    periapsisAlt = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
    vessel.control.speed_mode = conn.space_center.SpeedMode.orbit
    vessel.control.rcs = True
    vessel.control.sas = True

    ut0 = ut()
    vessel.control.forward = -1.0
    while ut() < (ut0 + 10.0):
        pass
    vessel.control.rcs = False

    ut0 = ut()
    vessel.control.sas_mode = conn.space_center.SASMode.retrograde
    while ut() < (ut0 + 10.0):
        pass
    vessel.control.throttle = 1.0

    while thrust() == 0.0:
        pass
    while (periapsisAlt() > -25000.0) and (thrust() != 0.0):
        pass
    vessel.control.throttle = 0.0

    vesselChangeType(vessel, conn.space_center.VesselType.debris)
    vesselChangeName(vessel, vessel.name+"-debris")

    ut.remove()
    thrust.remove()
    periapsisAlt.remove()
