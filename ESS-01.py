"""Execute the ESS-01 mission.

KSP version 1.5.1

Mods used :
-kRPC
-StationPartsExpansionRedux
-MechJeb 2
-MechJeb and Engineer for all!
-Kerbal Joint Reinforcement Continued

Craft file >>> "ESS-01.craft"

"""

import krpc
from time import sleep
from toolkit.misc import findVessel
from toolkit.vessel import twrRegulation, getPartsByName, getPartsByTag,\
    deployFairing, vesselDeorbit, vesselChangeName, vesselChangeType
from toolkit.maneuvers import manPeriapsis, manInclination


def ascent_guidance():
    """Control the ascent guidance."""
    ap.target_pitch_and_heading(90.0, 30.0)
    ap.target_roll = 90.0
    ap.engage()

    while srfSpeed() < 75.0:
        twrRegulation(vessel, meanAltitude, thrust,
                      vesselMass, throttle, twrMax=2.5)
    srfSpeed.remove()
    ap.target_pitch = 75.0

    while ssa() < 0.1:
        twrRegulation(vessel, meanAltitude, thrust,
                      vesselMass, throttle, twrMax=2.5)
    ssa.remove()
    ap.disengage()
    vessel.control.sas = True
    sleep(0.1)
    vessel.control.sas_mode = sc.SASMode.prograde

    mainTank = getPartsByName(vessel, "Kerbodyne S3-3600 Tank")[0]
    liquidFuel = conn.add_stream(mainTank.resources.amount, 'LiquidFuel')
    firstStageSeparated = False
    fairingDeployed = False
    reached95 = False
    mainEngine = getPartsByTag(vessel, 'Main Engine')[0]
    secEngine = getPartsByTag(vessel, 'Second Engine')[0]
    activeEngine = mainEngine

    while apoapsisAlt() < tgtApo:

        if (meanAltitude() < 70000.0) and (apoapsisAlt() < 0.95 * tgtApo):
            twrMax = 2.5
        elif (meanAltitude() > 70000.0) and (apoapsisAlt() < 0.95 * tgtApo):
            twrMax = 1.5
        elif apoapsisAlt() < tgtApo:
            twrMax = 0.2
        elif meanAltitude() < 70000.0:
            twrMax = 0.0
        else:
            vessel.control.throttle = 0.0
            break

        twrRegulation(vessel, meanAltitude, thrust,
                      vesselMass, throttle, twrMax)

        if firstStageSeparated is False:
            if liquidFuel() < 0.1:
                liquidFuel.remove()
                vessel.control.activate_next_stage()
                firstStageSeparated = True
                activeEngine = secEngine

        if (meanAltitude() > 60000.0) and (fairingDeployed is False):
            deployFairing(vessel)
            fairingDeployed = True

        if reached95 is False:
            if apoapsisAlt() > (0.95 * tgtApo):
                activeEngine.engine.thrust_limit = 0.05
                reached95 = True

    thrust.remove()
    throttle.remove()
    vesselMass.remove()
    apoapsisAlt.remove()
    meanAltitude.remove()

    if firstStageSeparated is False:
        vessel.control.activate_next_stage()
        firstStageSeparated = True

    sleep(1.0)
    activeEngine.engine.thrust_limit = 1.0


def reach_orbit():
    """Control the vessel to reach the correct orbit."""
    manPeriapsis(conn, newPeriapsis=tgtPeri, atApsis='apoapsis')
    manInclination(conn, newInclination=60.0, tolerance=0.001)
    sleep(1.0)


def release_payload():
    """Release the payload and deorbit second stage."""
    for D in vessel.parts.docking_ports:
        if D.state is sc.DockingPortState.docked:
            D.undock()

    vesselDeorbit(conn, vessel)


def launch():
    """Execute the mission, from launch to orbit."""
    vessel.control.throttle = 1.0
    vessel.control.activate_next_stage()
    sleep(1.0)
    ascent_guidance()
    reach_orbit()
    release_payload()

    ESS = findVessel(conn, "ESS-01 Station")
    if ESS is not None:
        vesselChangeName(ESS, "ESS")
        vesselChangeType(ESS, sc.VesselType.station)

###############################################################################


conn = krpc.connect(name="ESS-01")
sc = conn.space_center
vessel = sc.active_vessel
ap = vessel.auto_pilot
ap.disengage()

kerbin = vessel.orbit.body
K_rf = kerbin.reference_frame
srf_rf = conn.space_center.ReferenceFrame.create_hybrid(
    position=vessel.orbit.body.reference_frame,
    rotation=vessel.surface_reference_frame)

ssa = conn.add_stream(getattr, vessel.flight(K_rf), 'sideslip_angle')
thrust = conn.add_stream(getattr, vessel, 'thrust')
throttle = conn.add_stream(getattr, vessel.control, 'throttle')
srfSpeed = conn.add_stream(getattr, vessel.flight(srf_rf), 'speed')
vesselMass = conn.add_stream(getattr, vessel, 'mass')
apoapsisAlt = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
meanAltitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')

tgtApo = 500000.0
tgtPeri = 500000.0

launch()
