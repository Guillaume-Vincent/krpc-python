"""Regroup all the function related to maneuvers."""


def executeNextNode(conn, tolerance, leadTime):
    """Execute the next node."""
    executor = conn.mech_jeb.node_executor
    vsl = conn.space_center.active_vessel
    executorStatus = conn.add_stream(getattr, executor, 'enabled')
    nodeList = conn.add_stream(getattr, vsl.control, 'nodes')

    executor.tolerance = tolerance
    executor.lead_time = leadTime
    executor.execute_one_node()
    
    while (executorStatus() is True) or (nodeList() != []):
        pass

    executorStatus.remove()
    nodeList.remove()

def manPeriapsis(conn, newPeriapsis, atApsis, tolerance=0.01, leadTime=5):
    """Change the periapsis of the orbit.

    Args:
    -newPeriapsis : the new desired periapsis of the orbit
    -atApsis : location of the burn ('apoapsis','periapsis')
    -tolerance : tolerance of the mechjeb node executor
    -leadTime : lead time of warp before burn time

    """
    mj = conn.mech_jeb
    planner = mj.maneuver_planner
    mjPeri = planner.operation_periapsis

    if atApsis == 'apoapsis':
        mjPeri.time_selector.time_reference = mj.TimeReference.apoapsis
    elif atApsis == 'periapsis':
        mjPeri.time_selector.time_reference = mj.TimeReference.periapsis
    mjPeri.new_periapsis = newPeriapsis
    mjPeri.make_node()
    executeNextNode(conn, tolerance, leadTime)


def manApoapsis(conn, newApoapsis, atApsis, tolerance=0.01, leadTime=5):
    """Change the apoapsis of the orbit.

    Args:
    -newApoapsis : the new desired apoapsis of the orbit
    -atApsis : location of the burn ('apoapsis','periapsis')
    -tolerance : tolerance of the mechjeb node executor (default : 0.01)
    -leadTime : lead time of warp before burn time (default : 5)

    """
    mj = conn.mech_jeb
    planner = mj.maneuver_planner
    mjApo = planner.operation_apoapsis

    if atApsis == 'apoapsis':
        mjApo.time_selector.time_reference = mj.TimeReference.apoapsis
    elif atApsis == 'periapsis':
        mjApo.time_selector.time_reference = mj.TimeReference.periapsis
    mjApo.new_apoapsis = newApoapsis
    mjApo.make_node()
    executeNextNode(conn, tolerance, leadTime)


def manSemiMajorAxis(conn, newSMA, atApsis, tolerance=0.01, leadTime=5):
    """Change the semi major axis of the orbit.

    Args:
    -newSMA : the new desired semi major axis of the orbit
    -atApsis : location of the burn ('apoapsis','periapsis')
    -tolerance : tolerance of the mechjeb node executor (default : 0.01)
    -leadTime : lead time of warp before burn time (default : 5)

    """
    mj = conn.mech_jeb
    planner = mj.maneuver_planner
    mjSMA = planner.operation_semi_major

    if atApsis == 'apoapsis':
        mjSMA.time_selector.time_reference = mj.TimeReference.apoapsis
    elif atApsis == 'periapsis':
        mjSMA.time_selector.time_reference = mj.TimeReference.periapsis
    mjSMA.new_semi_major_axis = newSMA
    mjSMA.make_node()
    executeNextNode(conn, tolerance, leadTime)


def manCircularize(conn, atApsis, tolerance=0.01, leadTime=5):
    """Circularize the orbit at the desired apsis.

    Args:
    -atApsis : location of the burn ('apoapsis','periapsis')
    -tolerance : tolerance of the mechjeb node executor (default : 0.01)
    -leadTime : lead time of warp before burn time (default : 5)

    """
    mj = conn.mech_jeb
    planner = mj.maneuver_planner
    mjCirc = planner.operation_circularize

    if atApsis == 'apoapsis':
        mjCirc.time_selector.time_reference = mj.TimeReference.apoapsis
    elif atApsis == 'periapsis':
        mjCirc.time_selector.time_reference = mj.TimeReference.periapsis
    mjCirc.make_node()
    executeNextNode(conn, tolerance, leadTime)


def manInclination(conn, newInclination=0.0, tolerance=0.01, leadTime=5):
    """Change the inclination of the orbit.

    Args:
    -newInclination : the new desiredinclination of the orbit (default : 0.0)
    -tolerance : tolerance of the mechjeb node executor (default : 0.01)
    -leadTime : lead time of warp before burn time (default : 5)

    """
    mj = conn.mech_jeb
    planner = mj.maneuver_planner
    mjInc = planner.operation_inclination

    mjInc.time_selector.time_reference = mj.TimeReference.eq_nearest_ad
    mjInc.new_inclination = newInclination
    mjInc.make_node()
    executeNextNode(conn, tolerance, leadTime)
