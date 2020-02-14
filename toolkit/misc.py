"""Regroup all miscellanous functions."""
from time import sleep


def countdown(conn, t):
    """Create a t-seconds countdown."""
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    T = ut() + 1

    for i in range(t, 0, -1):
        conn.ui.message("%d" % i)
        while ut() < T:
            pass
        T += 1
    ut.remove()


def convertTime(ut):
    """Convert a time in seconds to a Y D HH:MM:SS format (KSP game time)."""
    ut_s = int(ut)
    ut_m = int(ut_s / 60)
    ut_h = int(ut_m / 60)
    ut_d = 1 + int(ut_h / 6)
    ut_y = 1 + int(ut_d / 427)

    ut_s = ut_s % 60
    ut_m = ut_m % 60
    ut_h = ut_h % 6
    ut_d = ut_d % 427

    Y = "Y" + str(ut_y)
    D = "D" + str(ut_d)
    HH = '{:02}'.format(ut_h)
    MM = '{:02}'.format(ut_m)
    SS = '{:02}'.format(ut_s)

    return (Y + " " + D + " " + HH + ":" + MM + ":" + SS)


def targetBody(conn, body):
    """Target the desired body."""
    for n in conn.space_center.bodies:
        if n == body:
            conn.space_center.target_body = conn.space_center.bodies.get(n)
    return conn.space_center.target_body


def findVessel(conn, vesselName):
    """Return the first vessel that has the given name."""
    for V in conn.space_center.vessels:
        if V.name == vesselName:
            return V
    return None


def wait(conn, waitTime):
    """Wait for a certain in game time (in seconds)."""
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    T0 = ut()
    
    while ut() < T0 + waitTime:
        sleep(0.01)
    