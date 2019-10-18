"""Perform a docking maneuver."""

from numpy import sign


def xPosControl(vessel, xTarg, xPos, xVlc, vcu):
    """Manage the x position of the vessel.

    Args:
    -vessel : active vessel
    -xTarg : target for the x position
    -xPos : x position
    -xVlc : x velocity
    -vcu : vessel.control.up value

    """
    if xPos < (xTarg - 0.1):
        if xVlc < 1.0:
            vessel.control.up = 0.1
        elif vcu != 0.0:
            vessel.control.up = 0.0
    elif xPos > (xTarg + 0.1):
        if xVlc > -1.0:
            vessel.control.up = -0.1
        elif vcu != 0.0:
            vessel.control.up = 0.0
    else:
        if xVlc > 0.05:
            vessel.control.up = -0.2
        elif xVlc < -0.05:
            vessel.control.up = 0.2
        elif vcu != 0.0:
            vessel.control.up = 0.0


def yPosControl(vessel, yTarg, yPos, yVlc, vcf):
    """Manage the y position of the vessel.

    Args:
    -vessel : active vessel
    -yTarg : target for the y position
    -yPos : y position
    -yVlc : y velocity
    -vcf : vessel.control.forward value

    """
    if yPos < (yTarg - 0.1):
        if yVlc < 1.0:
            vessel.control.forward = -0.1
        elif vcf != 0.0:
            vessel.control.forward = 0.0
    elif yPos > (yTarg + 0.1):
        if yVlc > -1.0:
            vessel.control.forward = 0.1
        elif vcf != 0.0:
            vessel.control.forward = 0.0
    else:
        if yVlc > 0.05:
            vessel.control.forward = 0.2
        elif yVlc < -0.05:
            vessel.control.forward = -0.2
        elif vcf != 0.0:
            vessel.control.forward = 0.0


def zPosControl(vessel, zTarg, zPos, zVlc, vcr):
    """Manage the z position of the vessel.

    Args:
    -vessel : active vessel
    -zTarg : target for the z position
    -zPos : z position
    -zVlc : z velocity
    -vcr : vessel.control.right value

    """
    if zPos < (zTarg - 0.1):
        if zVlc < 1.0:
            vessel.control.right = -0.1
        elif vcr != 0.0:
            vessel.control.right = 0.0
    elif zPos > (zTarg + 0.1):
        if zVlc > -1.0:
            vessel.control.right = 0.1
        elif vcr() != 0.0:
            vessel.control.right = 0.0
    else:
        if zVlc > 0.05:
            vessel.control.right = 0.2
        elif zVlc < -0.05:
            vessel.control.right = -0.2
        elif vcr != 0.0:
            vessel.control.right = 0.0


def lockedPos(lockingPosition, vPos):
    """Incidcate if the vessel is locked in the correct position.

    Args:
    -lockingPosition : vector containing coordinates of locking point
    -vPos : position vector of the vessel

    """
    if abs(vPos[0] - lockingPosition[0]) < 0.15:
        xLocked = True
    else:
        xLocked = False

    if abs(vPos[1] - lockingPosition[1]) < 0.15:
        yLocked = True
    else:
        yLocked = False

    if abs(vPos[2] - lockingPosition[2]) < 0.15:
        zLocked = True
    else:
        zLocked = False

    return (xLocked, yLocked, zLocked)


def dockVesselWithTarget(conn, vessel, target, vesselDP, targetDP):
    """Dock the given vessel to a target vessel.

    Args:
    -conn : return value of the initial krpc.connect()
    -vessel : active vessel
    -target : vessel objet you want to dock to
    -vesselDP : docking port of the active vessel
    -targetDP : docking port of the target vessel

    """
    sc = conn.space_center

    sc.target_docking_port = targetDP

    targetObtRefFrame = target.orbital_reference_frame
    refFrame = sc.ReferenceFrame.create_hybrid(
        targetObtRefFrame, targetDP.reference_frame,
        targetObtRefFrame, targetDP.reference_frame)

    ut = conn.add_stream(getattr, sc, 'ut')
    vcu = conn.add_stream(getattr, vessel.control, 'up')
    vcr = conn.add_stream(getattr, vessel.control, 'right')
    vcf = conn.add_stream(getattr, vessel.control, 'forward')
    vPos = conn.add_stream(vessel.position, refFrame)
    vVlc = conn.add_stream(getattr, vessel.flight(refFrame), 'velocity')
    DPState = conn.add_stream(getattr, vesselDP, "state")

    vesselAP = vessel.auto_pilot
    # vesselAP.time_to_peak = (2.0, 2.0, 2.0)
    # vesselAP.deceleration_time = (60.0, 60.0, 60.0)
    # vesselAP.attenuation_angle = (3.0, 3.0, 3.0)
    # vesselAP.reference_frame = refFrame
    vesselAP.target_direction = (0, -1, 0)
    vesselAP.target_roll = 0
    vesselAP.engage()

    ut0 = ut()
    while ut() < (ut0 + 10.0):
        pass
    vessel.control.rcs = True

    # Station avoidace system
    if vPos()[1] < 0:
        var = {abs(vPos()[0]): 'x', abs(vPos()[2]): 'z'}
        maxPos = var.get(max(var))
        if maxPos == 'x':
            xTarg = 40.0 * sign(vPos()[0])
            zTarg = 0.0
        else:
            xTarg = 0.0
            zTarg = 40.0 * sign(vPos()[2])
        yTarg = 0.0

    xLocked = False
    yLocked = False
    zLocked = False
    while (xLocked is False) or (yLocked is False) and (zLocked is False):
        xPosControl(vessel, xTarg, vPos()[0], vVlc()[0], vcu())
        yPosControl(vessel, yTarg, vPos()[1], vVlc()[1], vcf())
        zPosControl(vessel, zTarg, vPos()[2], vVlc()[2], vcr())
        (xLocked, yLocked, zLocked) = lockedPos((xTarg, yTarg, zTarg), vPos())

    # Positionning in front of target DP
    timer = ut()
    xTarg = 0.0
    yTarg = 40.0
    zTarg = 0.0
    while timer > (ut() - 5):
        xPosControl(vessel, xTarg, vPos()[0], vVlc()[0], vcu())
        yPosControl(vessel, yTarg, vPos()[1], vVlc()[1], vcf())
        zPosControl(vessel, zTarg, vPos()[2], vVlc()[2], vcr())
        (xLocked, yLocked, zLocked) = lockedPos((xTarg, yTarg, zTarg), vPos())

        if (xLocked is False) or (yLocked is False) or (zLocked is False):
            timer = ut()

    while DPState() != sc.DockingPortState.docking:
        xPosControl(xTarg)
        zPosControl(zTarg)

        if vVlc()[1] > -0.8:
            vessel.control.forward = 0.2
        elif vcf() != 0.0:
            vessel.control.forward = 0.0
