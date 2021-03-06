"""Execute the COMSAT mission.

KSP version 1.7.3

Mods used :
-B9PartSwitch
-MainSailorTextures-Complete/Essentials + Freedom Tex
-MechJeb 2
-MechJeb for all
-Mk2Expansion
-NearFutureConstruction / Props / Solar / Solar-Core
-ProceduralParts
-SCANSat
-StationPartsExpansionRedux

Craft file >>> "Orlando-COMSAT.craft"

"""
import krpc
from time import sleep
from toolkit.calculations import findClosestVessel
from toolkit.maneuvers import manApoapsis, manCircularize, manInclination
from toolkit.misc import countdown, wait
from toolkit.vessel import deployAntennas, deployFairing, deploySolarPanels,\
    getPartsByTag, toggleLights, twrRegulation, vesselDeorbit


def launch():
    """Launch the vessel carrying all the satellites."""
    countdown(conn, 5)
    
    vessel.control.throttle = 1.0
    vessel.control.activate_next_stage()


def ascentGuidance():
    """Control the ascent guidance."""
    ap.target_pitch_and_heading(90.0, 90.0-targetInclination)
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

    mainTank = getPartsByTag(vessel, "MAIN_TANK")[0]
    liquidFuel = conn.add_stream(mainTank.resources.amount, 'LiquidFuel')
    firstStageSeparated = False
    fairingDeployed = False
    reached95 = False
    mainEngine = getPartsByTag(vessel, 'MAIN_ENGINE')[0]
    secEngine = getPartsByTag(vessel, 'SEC_ENGINE')[0]
    activeEngine = mainEngine

    tgtObt = targetPeriapsis
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
                vessel.control.throttle = 0.0
                vessel.control.activate_next_stage()
                firstStageSeparated = True
                activeEngine = secEngine

        if (meanAltitude() > 60000.0) and (fairingDeployed is False):
            deployFairing(vessel)
            toggleLights(vessel)
            fairingDeployed = True

        if reached95 is False:
            if apoapsisAlt() > (0.95 * tgtObt):
                activeEngine.engine.thrust_limit = 0.05
                reached95 = True

    if fairingDeployed is False:
        deployFairing(vessel)
        toggleLights(vessel)
        fairingDeployed = True

    thrust.remove()
    throttle.remove()
    vesselMass.remove()
    apoapsisAlt.remove()
    meanAltitude.remove()

    if firstStageSeparated is False:
        vessel.control.activate_next_stage()
        firstStageSeparated = True

    vessel.control.throttle = 0.0
    sleep(1.0)
    activeEngine.engine.thrust_limit = 1.0
    vessel.control.toggle_action_group(1)  # Deploy second stage solar panels


def reachResonantOrbit():
    """Reach the desired resonant orbit."""
    manApoapsis(conn, newApoapsis=targetApoapsis, atApsis='apoapsis')
    manInclination(conn, newInclination=targetInclination)


def deploySatellites():
    """Deploy the satellites at periapsis, one per orbit."""
    timeToPeri = conn.add_stream(getattr, vessel.orbit, 'time_to_periapsis')
    leadTime = 75.0
    vessel.control.sas = True

    for N in range(0, satNumber):
        sc.warp_to(sc.ut + timeToPeri() - leadTime)
        vessel.control.sas_mode = sc.SASMode.retrograde
        wait(conn, waitTime=12.0)

        getPartsByTag(vessel, 'SDP'+str(N+1))[0].docking_port.undock()
        sat = findClosestVessel(conn)
        sc.active_vessel = sat

        satID = str(N+1)
        sat.name = "COMSAT-" + sat.orbit.body.name[:3].upper() + "-" + satID
        sat.type = sc.VesselType.relay
        
        sat.control.toggle_action_group(2)  # Activate engine
        manCircularize(conn, atApsis='periapsis')
        
        deploySolarPanels(sat)
        deployAntennas(sat)
        conn.ui.message("Satellite successfully deployed !", duration=10.0)

        wait(conn, waitTime=10.0)
        sc.active_vessel = vessel
        while timeToPeri() < leadTime:
            sleep(1)
        
# Resonant orbit for 9 satellite injections
satNumber = 9
targetApoapsis = 3367359.8
targetPeriapsis = 2863334
targetInclination = 0.0

# Connection
conn = krpc.connect(name="COMSAT")
sc = conn.space_center
vessel = sc.active_vessel
ap = vessel.auto_pilot
ap.disengage()

# Streams & Variables
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

# Mission Execution
launch()
ascentGuidance()
reachResonantOrbit()
deploySatellites()
vesselDeorbit(conn, vessel, rcs=False)

conn.close()
