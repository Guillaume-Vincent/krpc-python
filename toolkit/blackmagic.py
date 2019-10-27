"""Contains a black magic function.

I wrote it but I don't know what is means;
It works, but I don't know why.

"""


def vesselOnTargetPlane(conn, vessel, target):
    """Wit for vessel and target to be on the same plane.

    Also return the direction "north"/"south" you must go in order to reach
    the target.

    """
    sc = conn.space_center

    vrf = vessel.reference_frame
    torf = target.orbital_reference_frame

    # This is where the black magic happens
    RF = sc.ReferenceFrame.create_hybrid(vrf, torf, torf, torf)

    # (transdir[1] == 0) --> plane match
    #   (transdir[0] >= 0) --> need to go south
    #   (transdir[0] <= 0) --> need to go north
    rwf = conn.add_stream(getattr, sc, 'rails_warp_factor')
    transdir = conn.add_stream(sc.transform_direction, (0, 0, 1), RF, vrf)
    while True:
        if abs(transdir()[1]) > 0.2:
            if rwf() != 5:
                sc.rails_warp_factor = 5
        elif abs(transdir()[1]) > 0.01:
            if rwf() != 4:
                sc.rails_warp_factor = 4
        elif abs(transdir()[1]) > 0.005:
            if rwf() != 3:
                sc.rails_warp_factor = 3
        else:
            sc.rails_warp_factor = 0
            sc.physics_warp_factor = 0
            break

    if transdir()[0] > 0:
        return "south"
    else:
        return "north"
