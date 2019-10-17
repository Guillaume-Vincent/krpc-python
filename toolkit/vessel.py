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
    twr = thrust() / (vessel_mass() * localGravity)

    if (twr - 0.01) > twrMax:
        vessel.control.throttle -= abs(twr - twrMax) / 10

    if ((twr + 0.01) < twrMax) and (throttle() < 1.0):
        vessel.control.throttle += abs(twr - twrMax) / 10
