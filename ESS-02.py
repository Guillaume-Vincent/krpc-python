"""Execute the ESS-02 mission.

KSP version 1.5.1

Mods used :
-kRPC
-StationPartsExpansionRedux
-MechJeb 2
-MechJeb and Engineer for all!
-Kerbal Joint Reinforcement Continued

Craft file >>> "ESS-02.craft"

"""

import krpc
from time import sleep
from toolkit.blackmagic import vesselOnTargetPlane
from toolkit.calculations import angle, getOrbitalPeriod, relativeError
from toolkit.docking import dockVesselWithTarget, moveXFromTarget
from toolkit.maneuvers import executeNextNode, manApoapsis, manKillRelVel,\
    manPeriapsis, manPlane
from toolkit.misc import findVessel
from toolkit.vessel import deployFairing, getPartsByName, getPartsByTag,\
    twrRegulation, vesselChangeName, vesselChangeType, vesselDeorbit


###############################################################################


def ascent_guidance(heading):
    """Control the ascent guidance."""
    ap.target_pitch_and_heading(90.0, heading)
    ap.target_roll = 90.0
    ap.engage()

    while srfSpeed() < 75.0:
        twrRegulation(vessel, meanAltitude, thrust,
                      vesselMass, throttle, twrMax=2.5)
    srfSpeed.remove()
    ap.target_pitch = 75.0
    sleep(0.5)
    
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

    while apoapsisAlt() < tgtObt:

        if (meanAltitude() < 70000.0) and (apoapsisAlt() < 0.95 * tgtObt):
            twrMax = 2.5
        elif (meanAltitude() > 70000.0) and (apoapsisAlt() < 0.95 * tgtObt):
            twrMax = 1.5
        elif apoapsisAlt() < tgtObt:
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
            if apoapsisAlt() > (0.95 * tgtObt):
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


def reachOrbit():
    """Control the vessel to reach the correct orbit."""
    manPeriapsis(conn, tgtObt, atApsis='apoapsis', tolerance=0.001)
    manPlane(conn, tolerance=0.001)

    obt = vessel.orbit
    apoapsisAlt = conn.add_stream(getattr, obt, 'apoapsis_altitude')
    periapsisAlt = conn.add_stream(getattr, obt, 'periapsis_altitude')
    eccentricity = conn.add_stream(getattr, obt, 'eccentricity')

    while eccentricity() > 0.0001:
        # Trying to get a perfectly circular orbit
        apoErr = abs(relativeError(apoapsisAlt(), tgtObt))
        periErr = abs(relativeError(periapsisAlt(), tgtObt))

        if max(apoErr, periErr) == apoErr:
            if periapsisAlt() > tgtObt:
                manPeriapsis(conn, tgtObt, 'periapsis', tolerance=0.001)
            else:
                manApoapsis(conn, tgtObt, 'periapsis', tolerance=0.001)
        else:
            if apoapsisAlt() > tgtObt:
                manPeriapsis(conn, tgtObt, 'apoapsis', tolerance=0.001)
            else:
                manApoapsis(conn, tgtObt, 'apoapsis', tolerance=0.001)


def transferOrbit():
    """Plan and execute a transfer maneuver to the space station.

    NB : the more circular the orbits, the closer the approach.

    """
    mu = kerbin.gravitational_parameter
    sma = (vessel.orbit.semi_major_axis + ess.orbit.semi_major_axis) / 2
    transferTime = getOrbitalPeriod(sma, mu) / 2
    transferAngle = 180.0 - (transferTime / ess.orbit.period) * 360.0

    vesselAnglePerSec = 360.0 / vessel.orbit.period
    essAnglePerSec = 360.0 / ess.orbit.period
    angleVslEss1 = angle(vesselPos(), essPos())
    while (angleVslEss1 < 1.0) or (angleVslEss1 > 189.0):
        angleVslEss1 = angle(vesselPos(), essPos())
        sleep(1)
    sleep(1)
    angleVslEss2 = angle(vesselPos(), essPos())
    if angleVslEss1 < angleVslEss2:
        angleVslEss = 360.0 - angle(vesselPos(), essPos())
    else:
        angleVslEss = angle(vesselPos(), essPos())

    angleVariationPerSec = vesselAnglePerSec - essAnglePerSec

    deltaAngle = angleVslEss - transferAngle
    if deltaAngle < 0.0:
        deltaAngle += 360.0
    deltaTime = (deltaAngle / angleVariationPerSec)
    transferNodeUt = ut() + deltaTime

    mj = conn.mech_jeb
    planner = mj.maneuver_planner
    mj_apo = planner.operation_apoapsis
    mj_apo.new_apoapsis = ess.orbit.apoapsis_altitude
    node = mj_apo.make_node()
    node.ut = transferNodeUt

    if node.ut > ut() + 180:
        sc.warp_to(node.ut - 120.0)
        node.remove()
        transferOrbit()
    else:
        executeNextNode(conn, tolerance=0.001, leadTime=5)
        manKillRelVel(conn, tolerance=0.01, leadTime=5)


def releasePayload():
    """Release the payload and deorbit second stage."""
    for D in vessel.parts.docking_ports:
        if D.state is sc.DockingPortState.docked:
            D.undock()

    vesselDeorbit(conn, vessel)


def launch():
    """Execute the mission, from launch to orbit."""
    global vessel
    dir = vesselOnTargetPlane(conn, vessel, ess)
    if dir == "north":
        heading = 30
    elif dir == "south":
        heading = 150
    sleep(2)

    vessel.control.throttle = 1.0
    vessel.control.activate_next_stage()
    sleep(1.0)
    ascent_guidance(heading)
    reachOrbit()
    transferOrbit()
    moveXFromTarget(conn, vessel, ess, tgtDistance=200.0)
    releasePayload()

    vessel = findVessel(conn, "ESS-02 Station")
    if vessel is not None:
        vesselChangeName(vessel, "ESS-02")
        vesselChangeType(vessel, sc.VesselType.station)

    vesselDP = getPartsByTag(vessel, "DP-up")[0].docking_port
    essDP = getPartsByTag(ess, "DP-up")[0].docking_port
    dockVesselWithTarget(conn, vessel, ess, vesselDP, essDP)


###############################################################################


conn = krpc.connect(name="ESS-02")
sc = conn.space_center
vessel = sc.active_vessel
ap = vessel.auto_pilot
ap.disengage()

kerbin = vessel.orbit.body
g = 9.81
R = kerbin.equatorial_radius
K_rf = kerbin.reference_frame
K_nrrf = kerbin.non_rotating_reference_frame
srf_rf = conn.space_center.ReferenceFrame.create_hybrid(
    position=vessel.orbit.body.reference_frame,
    rotation=vessel.surface_reference_frame)

ess = findVessel(conn, "ESS")
sc.target_vessel = ess

ut = conn.add_stream(getattr, sc, 'ut')
ssa = conn.add_stream(getattr, vessel.flight(K_rf), 'sideslip_angle')
thrust = conn.add_stream(getattr, vessel, 'thrust')
throttle = conn.add_stream(getattr, vessel.control, 'throttle')
srfSpeed = conn.add_stream(getattr, vessel.flight(srf_rf), 'speed')
vesselMass = conn.add_stream(getattr, vessel, 'mass')
apoapsisAlt = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
meanAltitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')

vesselPos = conn.add_stream(vessel.position, K_nrrf)
essPos = conn.add_stream(ess.position, K_nrrf)

tgtObt = 250000.0

launch()
