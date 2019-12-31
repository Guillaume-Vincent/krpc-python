"""Send a satellite to kerbin orbit and recover the first stage.

Payload :
15t max for Low Kerbin Orbit

"""

import krpc
from time import sleep
from toolkit.vessel import getVesselPitch
from toolkit.impact import GetImpactInfos


def maintainVerticalSpeed(maxSpeed=None, minSpeed=None):
    """Control throttle to maintain the current vert. speed of the rocket.

    It can avoid going faster than maxSpeed(default=None),
    and slower than minSpeed(default=None).

    """
    t0 = (vesselMass() / vesselMaxThrust()) * g0 * (R / (R+vesselAlt()))**2

    if minSpeed is not None:
        if vSpeed() < minSpeed:
            t0 += 0.1
    if maxSpeed is not None:
        if vSpeed() > maxSpeed:
            t0 -= 0.1

    control = min(max(t0, 0.0), 1.0)  # min: 0.0 ; max: 1.0
    if control != throttle():
        vessel.control.throttle = control


def boostback():
    """Execute the boostback burn to land at a precise location."""
    vessel.control.sas = True
    vessel.control.rcs = True
    sleep(0.1)
    vessel.control.speed_mode = sc.SpeedMode.orbit
    vessel.control.sas_mode = sc.SASMode.radial
    sleep(15)

    vessel.control.throttle = 0.2
    landingLongitude = -74.5
    while GetImpactInfos(sc, obt).impactLongitude > landingLongitude:
        sleep(0.01)
    vessel.control.throttle = 0.0
    vessel.control.sas = False
    vessel.control.rcs = False


def liftOff():
    """Lift-Off."""
    vessel.control.sas = True
    vessel.control.throttle = 1.0
    vessel.control.activate_next_stage()
    sleep(1.0)

    while srfSpeed() < 90.0:
        sleep(0.1)

    vessel.control.sas = False
    while getVesselPitch(vesselDirection) > 85.0:
        vessel.control.yaw = -0.1 + (getVesselPitch(vesselDirection) - 85) / 25
        sleep(0.01)

    vessel.control.yaw = 0.0
    vessel.control.sas = True

    while ssa() < 0.1:
        sleep(0.01)

    sleep(0.1)
    vessel.control.sas_mode = sc.SASMode.prograde

    while apoapsisAlt() < 100000.0:
        sleep(0.05)
    vessel.control.throttle = 0.0

    sleep(0.5)
    vessel.control.activate_next_stage()


def propulsiveLanding():
    """Land the rocket softly."""
    # Control configuration
    vessel.control.sas = True
    vessel.control.rcs = True
    vessel.control.speed_mode = sc.SpeedMode.surface
    sleep(0.01)  # making sure SAS is on before targeting retrograde
    vessel.control.sas_mode = sc.SASMode.retrograde
    finsDeployed = False
    legsDeployed = False
    sasDisengaged = False

    # Waiting to enter dense atmosphere
    while vesselAlt() > 30000.0:
        sleep(0.1)

    # Reducing vertical speed
    while vSpeed() < -10.0:
        # Deploying grid fins at 15km
        if (vesselAlt() < 15000.0) and (finsDeployed is False):
            vessel.control.brakes = True
            finsDeployed = True

        # Deploying landing legs when vertical speed < 100m/s
        if (vSpeed() > -100.0) and (legsDeployed is False):
            vessel.control.gear = True
            legsDeployed = False

        accGravity = g0 * (R / (R+vesselAlt()))**2
        accEngine = vesselMaxThrust() / vesselMass()
        acc = accEngine - accGravity
        dist = vSpeed()**2/(2 * acc) + \
            GetImpactInfos(sc, obt).impactAltitude + 30.0

        if (dist > vesselAlt()) and (throttle() != 1.0):
            vessel.control.throttle = 1.0
        elif (dist < vesselAlt()) and (throttle() != 0.0):
            vessel.control.throttle = 0.0
        sleep(0.01)

    # Landing softly
    while vSpeed() < -0.1:
        maintainVerticalSpeed(maxSpeed=-4)

        if (vesselPitch() > 89.9) and (sasDisengaged is False):
            # Trying to land vertically
            vessel.control.sas_mode = sc.SASMode.stability_assist
            sasDisengaged = True

        sleep(0.05)

    # Turning main engine off
    vessel.control.throttle = 0.0


# Establishing connection
conn = krpc.connect(name="PropulsiveLanding")
sc = conn.space_center
vessel = sc.active_vessel
ap = vessel.auto_pilot
obt = vessel.orbit
kerbin = obt.body
krf = kerbin.reference_frame
vrf = vessel.orbit.body.reference_frame
vsrf = vessel.surface_reference_frame

# Setting up streams and constants
R = 600000.0
g0 = 9.81

ut = conn.add_stream(getattr, sc, 'ut')
ssa = conn.add_stream(getattr, vessel.flight(krf), 'sideslip_angle')
vSpeed = conn.add_stream(getattr, vessel.flight(vrf), 'vertical_speed')
throttle = conn.add_stream(getattr, vessel.control, 'throttle')
srfSpeed = conn.add_stream(getattr, vessel.flight(vrf), 'speed')
vesselAlt = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
vesselMass = conn.add_stream(getattr, vessel, 'mass')
vesselPitch = conn.add_stream(getattr, vessel.flight(), 'pitch')
apoapsisAlt = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
vesselDirection = conn.add_stream(vessel.direction, vsrf)
vesselMaxThrust = conn.add_stream(getattr, vessel, 'available_thrust')

###############################################################################

liftOff()
boostback()
while (vesselAlt() > 70000.0) or (vSpeed() > 0.0):
    sleep(1)
propulsiveLanding()
