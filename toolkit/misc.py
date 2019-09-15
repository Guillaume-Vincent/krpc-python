import krpc

def countdown(conn,t):
    """Create a t-seconds countdown.

    """
    ut = conn.add_stream(getattr,conn.space_center,'ut')
    T = ut() + 1

    for i in range(t,0,-1):
        conn.ui.message("%d" % i)
        while ut() < T:
            pass
        T += 1
    ut.remove()
