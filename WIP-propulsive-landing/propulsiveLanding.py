"""Make a propulsive landing."""

import krpc
from time import sleep
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def maintainVerticalSpeed():
    """Control throttle to maintain the current vert. speed of the rocket."""
    t0 = (vesselMass() / vesselMaxThrust()) * g0 * (R / (R+vesselAlt()))**2
    control = min(max(t0, 0.0), 1.0)  # min: 0.0 ; max: 1.0
    if control != throttle():
        vessel.control.throttle = control


# Establishing connection
conn = krpc.connect(name="PropulsiveLanding")
sc = conn.space_center
vessel = sc.active_vessel
ap = vessel.auto_pilot

# Setting up streams and constants
R = 600000.0
g0 = 9.81
RF = vessel.orbit.body.reference_frame
ut = conn.add_stream(getattr, sc, 'ut')
vSpeed = conn.add_stream(getattr, vessel.flight(RF), 'vertical_speed')
throttle = conn.add_stream(getattr, vessel.control, 'throttle')
vesselAlt = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
vesselMass = conn.add_stream(getattr, vessel, 'mass')
vesselPitch = conn.add_stream(getattr, vessel.flight(), 'pitch')
vesselMaxThrust = conn.add_stream(getattr, vessel, 'available_thrust')

# Setting up telemetry
X = []  # will store time
Y = []  # will store altitude
T = []  # will store throttle
telemetryStarted = False

# Vessel configuration
vessel.control.sas = True
vessel.control.rcs = True
vessel.control.speed_mode = sc.SpeedMode.surface
sleep(0.01)  # making sure SAS is on before targeting retrograde
vessel.control.sas_mode = sc.SASMode.retrograde
finsDeployed = False
legsDeployed = False
sasDisengaged = False

# Waiting to enter denser atmosphere
while vesselAlt() > 35000.0:
    pass

# Reducing vertical speed
while vSpeed() < -10.0:
    if vesselAlt() < 25000.0:
        if telemetryStarted is False:
            TIME = ut()
            telemetryStarted = True
        X.append(ut()-TIME)
        Y.append(vesselAlt())
        T.append(throttle())

    # Deploying grid fins at 15km
    if (vesselAlt() < 15000.0) and (finsDeployed is False):
        vessel.control.brakes = True
        finsDeployed = True

    # Deploying landing legs when vertical speed < 50m/s
    if (vSpeed() > -50.0) and (legsDeployed is False):
        vessel.control.gear = True
        legsDeployed = False

    accGravity = g0 * (R / (R+vesselAlt()))**2
    try:
        accEngine = vesselMaxThrust() / vesselMass()
    except ZeroDivisionError:  # vesselMass() might be 0 if vessel is destroyed
        break
    else:
        acc = accEngine - accGravity
        dist = 30.0 + vSpeed()**2/(2 * acc)  # sea landing
        # dist = 65.0 + 30.0 + vSpeed()**2/(2 * acc)  # ksc landing

    if (dist > vesselAlt()) and (throttle() != 1.0):
        vessel.control.throttle = 1.0
    elif (dist < vesselAlt()) and (throttle() != 0.0):
        vessel.control.throttle = 0.0

    sleep(0.05)

# Landing
while vSpeed() < -0.1:
    maintainVerticalSpeed()

    if (vesselPitch() > 89.9) and (sasDisengaged is False):
        # Trying to land vertically
        vessel.control.sas_mode = sc.SASMode.stability_assist
        sasDisengaged = True

    X.append(ut()-TIME)
    Y.append(vesselAlt())
    T.append(throttle())

    sleep(0.05)
vessel.control.throttle = 0.0

# Plotly
# May take some time to process
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=X, y=Y, name="altitude data"), secondary_y=False)
fig.add_trace(go.Scatter(x=X, y=T, name="throttle data"), secondary_y=True)
fig.update_layout(title_text="Propulsive Landing")
fig.update_xaxes(title_text="Time (s)")
fig.update_yaxes(title_text="Altitude (m)", secondary_y=False)
fig.update_yaxes(title_text="Throttle", secondary_y=True)
fig.show()
