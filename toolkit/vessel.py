"""Regroup all the functions related to a vessel and its parts."""


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
