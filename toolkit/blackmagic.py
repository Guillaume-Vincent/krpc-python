"""Contains a black magic function.

I wrote it but I don't know what is means;
It works, but I don't know why.

"""


def vesselOnTargetPlane(sc, vessel, target):
    """Wit for vessel and target to be on the same plane.

    Also return the direction "north"/"south" you must go in order to reach
    the target.

    """
    vrf = vessel.reference_frame
    torf = target.orbital_reference_frame

    # This is where the black magic happens
    RF = sc.ReferenceFrame.create_hybrid(vrf, torf, torf, torf)

    # (transdir[1] == 0) --> plane match
    #   (transdir[0] >= 0) --> need to go south
    #   (transdir[0] <= 0) --> need to go north
    while True:
        transdir = sc.transform_direction((0, 0, 1), RF, vrf)
        if abs(transdir[1]) > 0.2:
            sc.rails_warp_factor = 5
        elif abs(transdir[1]) > 0.01:
            sc.rails_warp_factor = 4
        elif abs(transdir[1]) > 0.005:
            sc.rails_warp_factor = 3
        else:
            sc.rails_warp_factor = 0
            break

    if transdir[0] > 0:
        return "south"
    else:
        return "north"
